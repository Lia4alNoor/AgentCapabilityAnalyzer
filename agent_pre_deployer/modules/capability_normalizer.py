"""
capability_normalizer — canonical normalization vocabulary (canon_normalizer)

Normalizes raw tool expressions (name + description) into the canonical
C1-C6 capability concepts, following the Capability Ontology Mapper design:

1. RULES lexicon: each rule is one signal — a regex pattern searched in the
   tool's assumed_capability (name + description), pointing to a capability
   with a reason and a base confidence (High / Medium / Low).
2. Multi-label matching: every rule is checked independently; one tool can
   collect several capabilities. If several rules hit the same capability,
   only the strongest (highest-confidence) hit is kept.
3. Hint cross-checks (supporting evidence, never ground truth):
   - readOnlyHint = true contradicts write-side capabilities (C3-C6)
     -> confidence lowered one step, note recorded.
   - openWorldHint = true supports external-facing capabilities (C1, C3)
     -> confidence raised one step.
   - destructiveHint = true confirms C4 -> confidence forced to High.
4. Hint-only fallbacks (Low confidence, manual-review queue):
   - openWorldHint = true with no C1/C3 match -> tag C1 (Low).
   - readOnlyHint = false plus a mutating verb -> tag C4 (Low).
5. UNMAPPED: nothing matched -> primary_capability = None.

Exports (used by module_3_capability_normalization):
    normalize_tool(tool) -> dict
    get_normalization_matches(tool) -> list
"""

import re

# ---------------------------------------------------------------------------
# Canonical C1-C6 concepts (must stay in sync with Module 4's ontology)
# ---------------------------------------------------------------------------

CANONICAL_CONCEPTS = {
    "C1": "External Data Ingestion",
    "C2": "Sensitive Data Access",
    "C3": "External Communication",
    "C4": "State Modification",
    "C5": "System Execution",
    "C6": "Physical Actuation",
}

# Confidence levels and one-step raise/lower
CONFIDENCE_SCORES = {"High": 1.0, "Medium": 0.7, "Low": 0.4}
_LEVELS = ["Low", "Medium", "High"]


def _raise_level(level):
    idx = _LEVELS.index(level)
    return _LEVELS[min(idx + 1, len(_LEVELS) - 1)]


def _lower_level(level):
    idx = _LEVELS.index(level)
    return _LEVELS[max(idx - 1, 0)]


# ---------------------------------------------------------------------------
# RULES lexicon (the codebook — extend as new patterns are found)
# Each rule: (capability_id, regex pattern, reason, base confidence)
# ---------------------------------------------------------------------------

RULES = [
    # --- C1 External Data Ingestion -------------------------------------
    ("C1", r"\bfetch(es|ing)?\b", "Fetches content from an external source into the agent context.", "High"),
    ("C1", r"\b(download|crawl|scrape|browse)\b", "Retrieves external/web content into the agent context.", "High"),
    ("C1", r"\b(url|web|http[s]?|internet)\b", "References external web/URL content that can enter the agent.", "Medium"),
    ("C1", r"\b(research|web)[ _-]?quer(y|ies)\b", "Performs an external query whose results enter the agent context.", "Medium"),
    ("C1", r"\b(sampling[ _-]?request|elicitation)\b", "Solicits externally influenced content into the agent context.", "Low"),
    ("C1", r"\bclone\b", "Clones a remote repository, ingesting external content.", "Medium"),

    # --- C2 Sensitive Data Access ----------------------------------------
    ("C2", r"\bread(s|ing)?[ _-]?(a[ _-])?(file|files|mail|message|document)\b", "Reads file/mail contents that may be private or sensitive.", "Medium"),
    ("C2", r"\b(env|environment)([ _-]?variable)?s?\b", "Exposes environment/configuration values that may contain secrets.", "Medium"),
    ("C2", r"\b(secret|credential|token|password|api[ _-]?key)s?\b", "Directly references secrets or credentials.", "High"),
    ("C2", r"\b(list|read|show|display)[a-z_ /-]*(director(y|ies)|file|files|folder)", "Enumerates or reads local files/directories (user-specific data).", "Medium"),
    ("C2", r"\b(file|director(y|ies))[a-z_ /-]*(metadata|info|tree|sizes)\b", "Retrieves local file/directory structure and metadata.", "Medium"),
    ("C2", r"\b(search|find)[a-z_ /-]*(file|files|director(y|ies)|entit(y|ies)|node)s?\b", "Searches local data stores for user-specific content.", "Medium"),
    ("C2", r"\b(knowledge[ _-]?graph|memory|observation)s?\b.*\b(read|open|search|retriev)", "Reads stored user memory/knowledge-graph data.", "Medium"),
    ("C2", r"\b(read|open|search)[a-z_ /-]*(graph|node|memor(y|ies))s?\b", "Reads stored user memory/knowledge-graph data.", "Medium"),
    ("C2", r"\bgit[ _-]?(log|show|diff|status|blame)", "Reads repository history/contents which may contain sensitive data.", "Low"),
    ("C2", r"\b(commit )?histor(y|ies)\b|\bdiffs?\b|\bshows? changes\b|\bworking tree status\b", "Reads repository history/contents which may contain sensitive data.", "Low"),
    ("C2", r"\ballowed[ _-]?directories\b", "Reveals which local directories are accessible.", "Low"),

    # --- C3 External Communication ---------------------------------------
    ("C3", r"\bsend(s|ing)?[ _-]?(mail|email|message|notification|data)?\b", "Sends/transmits data to an external recipient or endpoint.", "High"),
    ("C3", r"\b(email|e-mail|mail)\b.*\b(send|compose|deliver)\b", "Sends email to external recipients.", "High"),
    ("C3", r"\b(publish|post|upload|transmit|share|submit)\b", "Publishes/uploads data to an external service.", "High"),
    ("C3", r"\bcreate[ _-]?issue\b", "Creates an issue on an external tracker (data leaves the system).", "High"),
    ("C3", r"\bpush(es|ing)?\b", "Pushes data/commits to a remote endpoint.", "High"),
    ("C3", r"\b(notify|notification|webhook|broadcast)\b", "Emits notifications to external listeners.", "Medium"),

    # --- C4 State Modification --------------------------------------------
    ("C4", r"\b(write|overwrite|creat(e|es|ing)|edit|modif(y|ies)|updat(e|es|ing)|replace)\b", "Creates or modifies persistent state (files, records, settings).", "High"),
    ("C4", r"\b(delete|remove|drop|destroy|clear|truncate)\b", "Deletes or destroys persistent state.", "High"),
    ("C4", r"\b(move|rename)\b", "Relocates/renames persistent objects (state change).", "Medium"),
    ("C4", r"\b(toggle|set|enable|disable|configure)\b", "Changes server-side settings or persistent flags.", "Medium"),
    ("C4", r"\bgit[ _-]?(commit|add|reset|checkout|branch|merge|init)\b|\b(commit|stage)s?\b.*\b(change|file|snapshot)s?\b", "Modifies repository state persistently.", "Medium"),
    ("C4", r"\b(add|insert|append|store|save|record)\b", "Adds new persistent records/content.", "Medium"),
    ("C4", r"\b(compress|gzip|zip|archive|pack)(es|ed|ing)?\b", "Produces new file artifacts (compressed/archived output is persistent state).", "Medium"),

    # --- C5 System Execution ----------------------------------------------
    ("C5", r"\b(execute|exec|run(s|ning)?)\b.*\b(command|script|shell|program|code|process)s?\b", "Executes commands/scripts/code on the underlying system.", "High"),
    ("C5", r"\b(shell|subprocess|spawn|eval|interpreter)\b", "Provides command/code execution on the system.", "High"),
    ("C5", r"\bcommand[ _-]?line\b|\bterminal\b", "Interacts with the system command line.", "Medium"),

    # --- C6 Physical Actuation ---------------------------------------------
    ("C6", r"\b(unlock|lock)\b.*\b(door|smart)\b|\bsmart[ _-]?lock\b", "Controls a physical lock (real-world actuation).", "High"),
    ("C6", r"\b(thermostat|actuat(e|or)|robot|drone|motor|relay|iot device)\b", "Controls hardware/IoT devices causing real-world changes.", "High"),
    ("C6", r"\b(device|hardware|physical)\b.*\b(control|operate|turn (on|off)|activate)\b", "Operates physical devices.", "Medium"),
]

_COMPILED_RULES = [
    (cap, re.compile(pattern, re.IGNORECASE), reason, confidence)
    for cap, pattern, reason, confidence in RULES
]

# Mutating verbs used by the readOnlyHint=false fallback
_MUTATING_VERBS = re.compile(
    r"\b(toggle|trigger|start|stop|restart|reset|switch|activate|deactivate)\b",
    re.IGNORECASE,
)

# Severity order used only to break confidence ties for primary capability
_SEVERITY_ORDER = ["C5", "C6", "C3", "C2", "C4", "C1"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_normalization_matches(tool):
    """
    Run the canon_normalizer lexicon over one tool.

    Args:
        tool (dict): Tool with at least 'tool' and 'description'
                     (and optionally 'assumed_capability' and MCP hints).

    Returns:
        list[dict]: One match per capability, strongest hit kept:
            {
                "capability_id": "C4",
                "canonical": "State Modification",
                "matched_expression": "write",
                "confidence": 1.0,
                "confidence_level": "High",
                "reason": "...",
                "hint_adjustments": ["..."]
            }
    """
    text = tool.get("assumed_capability") or "{} {}".format(
        tool.get("tool", ""), tool.get("description", "")
    )
    text = text.strip()

    # 1-2. Rule matching, multi-label, strongest hit per capability
    best = {}  # capability_id -> match dict
    for cap_id, regex, reason, base_level in _COMPILED_RULES:
        m = regex.search(text)
        if not m:
            continue
        candidate = {
            "capability_id": cap_id,
            "canonical": CANONICAL_CONCEPTS[cap_id],
            "matched_expression": m.group(0).strip().lower(),
            "confidence_level": base_level,
            "reason": reason,
            "hint_adjustments": [],
        }
        current = best.get(cap_id)
        if current is None or (
            CONFIDENCE_SCORES[base_level]
            > CONFIDENCE_SCORES[current["confidence_level"]]
        ):
            best[cap_id] = candidate

    # 3. Hint cross-checks (supporting evidence, never ground truth)
    read_only = tool.get("readOnlyHint")
    open_world = tool.get("openWorldHint")
    destructive = tool.get("destructiveHint")

    for cap_id, match in best.items():
        if read_only is True and cap_id in ("C3", "C4", "C5", "C6"):
            match["confidence_level"] = _lower_level(match["confidence_level"])
            match["hint_adjustments"].append(
                "readOnlyHint=true contradicts write-side capability -> lowered one step"
            )
        if open_world is True and cap_id in ("C1", "C3"):
            match["confidence_level"] = _raise_level(match["confidence_level"])
            match["hint_adjustments"].append(
                "openWorldHint=true supports external-facing capability -> raised one step"
            )
        if destructive is True and cap_id == "C4":
            match["confidence_level"] = "High"
            match["hint_adjustments"].append(
                "destructiveHint=true confirms C4 -> confidence forced to High"
            )

    # 4. Hint-only fallbacks (Low confidence, manual-review queue)
    if open_world is True and "C1" not in best and "C3" not in best:
        best["C1"] = {
            "capability_id": "C1",
            "canonical": CANONICAL_CONCEPTS["C1"],
            "matched_expression": "openWorldHint",
            "confidence_level": "Low",
            "reason": (
                "Hint-only fallback: openWorldHint=true with no C1/C3 keyword match — "
                "tool talks to something external but direction is unclear; needs manual review."
            ),
            "hint_adjustments": [],
        }
    if read_only is False and "C4" not in best and _MUTATING_VERBS.search(text):
        verb = _MUTATING_VERBS.search(text).group(0).lower()
        best["C4"] = {
            "capability_id": "C4",
            "canonical": CANONICAL_CONCEPTS["C4"],
            "matched_expression": verb,
            "confidence_level": "Low",
            "reason": (
                "Hint-only fallback: readOnlyHint=false plus mutating verb "
                "'{}' — possible state change; needs manual review.".format(verb)
            ),
            "hint_adjustments": [],
        }

    # Finalize numeric confidence
    matches = []
    for cap_id in sorted(best.keys()):
        match = best[cap_id]
        match["confidence"] = CONFIDENCE_SCORES[match["confidence_level"]]
        matches.append(match)

    return matches


def normalize_tool(tool):
    """
    Normalize a single tool into canonical C1-C6 concepts.

    Args:
        tool (dict): Tool from Module 2 with 'assumed_capability',
                     MCP hints, and 'capability_features'.

    Returns:
        dict: {
            "primary_capability": "C4" or None (UNMAPPED),
            "all_capabilities": ["C4", ...],
            "normalized_matches": [ ...match dicts... ],
            "confidence_score": 1.0,
            "evidence": "..."
        }
    """
    matches = get_normalization_matches(tool)

    if not matches:
        # 5. UNMAPPED — pure computation like echo / get-sum
        return {
            "primary_capability": None,
            "all_capabilities": [],
            "normalized_matches": [],
            "confidence_score": 1.0,
            "evidence": "UNMAPPED: no canonical capability expression matched (pure computation/demo tool).",
        }

    # Primary = highest confidence; ties broken by severity order
    def sort_key(m):
        return (
            -m["confidence"],
            _SEVERITY_ORDER.index(m["capability_id"]),
        )

    ordered = sorted(matches, key=sort_key)
    primary = ordered[0]

    evidence_parts = []
    for m in ordered:
        part = "{} {} via '{}' ({})".format(
            m["capability_id"], m["canonical"], m["matched_expression"], m["confidence_level"]
        )
        if m["hint_adjustments"]:
            part += " [{}]".format("; ".join(m["hint_adjustments"]))
        evidence_parts.append(part)

    return {
        "primary_capability": primary["capability_id"],
        "all_capabilities": [m["capability_id"] for m in ordered],
        "normalized_matches": ordered,
        "confidence_score": primary["confidence"],
        "evidence": "; ".join(evidence_parts),
    }
