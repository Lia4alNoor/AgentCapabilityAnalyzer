import os
import sqlite3
import tempfile
from pathlib import Path

import streamlit as st

from modules import (
    module_1_server_selection,
    module_2_capability_extraction,
    module_3_capability_normalization,
    module_5_ontology_database,
    module_6_composition_analysis,
    module_7_attack_pattern_analysis,
    module_8_risk_assessment,
    module_9_report_generation,
)

CAPABILITY_SEED = module_5_ontology_database.CAPABILITY_SEED

CAPABILITY_INFO = {
    cap_id: {"name": name, "definition": definition, "example_risk": example_risk}
    for cap_id, name, definition, example_risk in CAPABILITY_SEED
}


def describe_capability(cap_id):
    """Format capability ID with name. E.g., 'C4 (State Modification)'."""
    info = CAPABILITY_INFO.get(cap_id)
    return f"{cap_id} ({info['name']})" if info else str(cap_id)


def describe_sequence(cap_sequence):
    """Format capability sequence with arrows. E.g., 'C1 → C2 → C3'."""
    if not isinstance(cap_sequence, list):
        return str(cap_sequence)
    return " → ".join(describe_capability(step) for step in cap_sequence)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AgentPreDeployer",
    page_icon="🛡️",
    layout="wide",
)


# =========================================================
# LOAD CSS
# =========================================================

def load_css():
    css_path = Path(__file__).parent / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True,
            )


load_css()

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🛡️ AgentPreDeployer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Pre-deployment security assessment for agent tool permissions</div>',
    unsafe_allow_html=True,
)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.header("Analysis")

    uploaded_file = st.file_uploader(
        "Upload MCP tool metadata",
        type=["json"],
    )

    st.divider()
    st.caption("Pipeline")
    for i, step in enumerate([
        "Tool Discovery",
        "Capability Extraction",
        "Capability Normalization",
        "Ontology Database",
        "Composition Analysis",
        "Attack Pattern Analysis",
        "Risk Assessment",
        "Report Generation",
    ], 1):
        st.caption(f"{i}. {step}")

# =========================================================
# NO FILE UPLOADED
# =========================================================

if uploaded_file is None:
    st.info("Upload a JSON tool metadata file from the sidebar to begin.")

    st.markdown("### What this tool checks")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🔍 Capabilities")
        st.write("Maps tools to the C1–C6 capability ontology.")

    with col2:
        st.markdown("#### 🔗 Composition")
        st.write("Checks for literature-backed capability compositions.")

    with col3:
        st.markdown("#### ⚠️ Risk")
        st.write("Assesses CIA impact and mitigation coverage.")

    st.stop()

# =========================================================
# SESSION STATE
# =========================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "report_text" not in st.session_state:
    st.session_state.report_text = None

# =========================================================
# RUN PIPELINE
# =========================================================

if st.button("Run Security Analysis", type="primary", use_container_width=True):
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, uploaded_file.name)

        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            with st.status("Running AgentPreDeployer...", expanded=True) as status:

                st.write("Module 1 — Server discovery")
                result_1 = module_1_server_selection.run(input_path)

                st.write("Module 2 — Capability extraction")
                result_2 = module_2_capability_extraction.run(result_1)

                st.write("Module 3 — Capability normalization")
                result_3 = module_3_capability_normalization.run(result_2)

                st.write("Module 5 — Ontology database")
                result_5 = module_5_ontology_database.run(result_3)

                st.write("Module 6 — Composition analysis")
                result_6 = module_6_composition_analysis.run(result_5)

                st.write("Module 7 — Attack pattern analysis")
                result_7 = module_7_attack_pattern_analysis.run(result_6)

                st.write("Module 8 — Risk assessment")
                result_8 = module_8_risk_assessment.run(result_7)

                st.write("Module 9 — Report generation")
                result_9 = module_9_report_generation.run(result_8)

                status.update(label="Analysis complete", state="complete")

            st.session_state.analysis_result = result_9

            generated_report_path = result_9.get("final_report_path")
            if generated_report_path:
                report_path = Path(generated_report_path)
                if report_path.exists():
                    st.session_state.report_text = report_path.read_text(encoding="utf-8")

            st.success("Security assessment completed successfully.")

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.exception(e)

# =========================================================
# RESULTS
# =========================================================

analysis_result = st.session_state.analysis_result

if analysis_result is None:
    st.stop()

# =========================================================
# EXTRACT MODULE OUTPUTS
# =========================================================

all_tools = analysis_result.get("tools", [])
composition_analysis_data = analysis_result.get("composition_analysis", {})
mitigation_assessment_data = analysis_result.get("mitigation_assessment", {})

# =========================================================
# BUILD CAPABILITY PROFILE
# =========================================================

capability_to_tools = {}

for tool in all_tools:
    if not isinstance(tool, dict):
        continue

    tool_name = tool.get("tool", "Unknown tool")
    tool_mapping = tool.get("mapping", {})
    tool_mappings_list = tool_mapping.get("mappings", [])

    if not isinstance(tool_mappings_list, list):
        continue

    for mapping_entry in tool_mappings_list:
        if not isinstance(mapping_entry, dict):
            continue

        cap_id = mapping_entry.get("capability_id")
        if cap_id:
            capability_to_tools.setdefault(cap_id, set()).add(tool_name)

# =========================================================
# EXTRACT DETECTIONS & GAPS
# =========================================================

matched_compositions = composition_analysis_data.get("detections", [])
if not isinstance(matched_compositions, list):
    matched_compositions = []

matched_mitigations = mitigation_assessment_data.get("matched_composition_assessments", [])
if not isinstance(matched_mitigations, list):
    matched_mitigations = []

open_mitigation_gaps = mitigation_assessment_data.get("open_mitigation_gaps", [])
if not isinstance(open_mitigation_gaps, list):
    open_mitigation_gaps = []

# =========================================================
# OVERVIEW METRICS
# =========================================================

st.header("Assessment Overview")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric("Tools Analysed", len(all_tools))

with metric_col2:
    st.metric("Capabilities Found", len(capability_to_tools))

with metric_col3:
    st.metric("Matched Compositions", len(matched_compositions))

with metric_col4:
    st.metric("Open Gaps", len(open_mitigation_gaps))

# =========================================================
# TABBED INTERFACE
# =========================================================

tab_tools, tab_compositions, tab_cia, tab_limits, tab_report = st.tabs([
    "Tools & Capabilities",
    "Composition Analysis",
    "CIA Risk & Mitigations",
    "Interpretation Limits",
    "Final Report",
])

# =========================================================
# TAB 1: TOOLS & CAPABILITIES
# =========================================================

with tab_tools:
    st.header("Capability Taxonomy Reference")
    st.caption("The fixed C1–C6 ontology used throughout this analysis.")

    for cap_id, cap_name, cap_definition, cap_risk in CAPABILITY_SEED:
        with st.expander(f"{cap_id} — {cap_name}"):
            st.write(cap_definition)
            if cap_risk:
                st.caption(f"Example risk: {cap_risk}")

    st.divider()
    st.header("Capability Profile")

    all_tool_names = {
        tool.get("tool", "Unknown tool")
        for tool in all_tools
        if isinstance(tool, dict)
    }

    mapped_tool_names = (
        set().union(*capability_to_tools.values())
        if capability_to_tools else set()
    )

    unmapped_tool_names = sorted(all_tool_names - mapped_tool_names)

    if capability_to_tools:
        for cap_id, tool_set in sorted(capability_to_tools.items()):
            tool_count = len(tool_set)
            cap_label = describe_capability(cap_id)

            st.markdown(
                f'<span class="capability">{cap_label} — {tool_count} tool(s)</span>',
                unsafe_allow_html=True,
            )

            with st.expander(f"{cap_label}"):
                cap_definition = CAPABILITY_INFO.get(cap_id, {}).get("definition")
                if cap_definition:
                    st.caption(cap_definition)

                for tool_name in sorted(tool_set):
                    st.write(f"• {tool_name}")
    else:
        st.info("No capability information available.")

    if unmapped_tool_names:
        st.markdown("**Tools with no capability identified**")
        st.caption("These tools matched none of the C1–C6 capabilities. Worth a manual check.")
        for tool_name in unmapped_tool_names:
            st.write(f"• {tool_name}")

# =========================================================
# TAB 2: COMPOSITION ANALYSIS
# =========================================================

with tab_compositions:
    st.header("Matched Literature-Backed Capability Compositions")
    st.caption(
        "Level-1 composition matches indicate required capabilities are present. "
        "A match does not establish that an attack was executed."
    )

    if not matched_compositions:
        st.success("✓ No literature-backed capability compositions matched.")
    else:
        for detection in matched_compositions:
            if not isinstance(detection, dict):
                st.write(detection)
                continue

            pattern_id = detection.get("pattern_id", "Unknown")
            pattern_name = detection.get("pattern_name", "Unknown pattern")
            severity = detection.get("severity", "Unknown")
            finding_type = detection.get("finding_type", "Unknown")
            confidence = detection.get("confidence", "Unknown")
            cap_sequence = detection.get("capability_sequence", [])
            sequence_text = describe_sequence(cap_sequence)

            severity_class = {
                "high": "severity-high",
                "medium": "severity-medium",
            }.get(str(severity).lower(), "severity-low")

            st.markdown(
                f'''<div class="composition-card">
                <div class="composition-header">
                <div>
                <div class="pattern-id">{pattern_id}</div>
                <div class="pattern-name">{pattern_name}</div>
                </div>
                <span class="status-badge {severity_class}">{severity}</span>
                </div>
                <div class="sequence">{sequence_text}</div>
                </div>''',
                unsafe_allow_html=True,
            )

            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("**Sequence**")
                st.code(sequence_text, language="text")

            with col_right:
                st.markdown("**Finding**")
                st.write(finding_type)
                st.markdown("**Confidence**")
                st.write(f"{confidence} (literature-mapping)")

            # CIA Impact
            impact_data = detection.get("impact_assessment")
            if impact_data:
                st.markdown("#### CIA Impact")
                cia_col1, cia_col2, cia_col3, cia_col4 = st.columns(4)

                with cia_col1:
                    st.metric("Confidentiality", impact_data.get("confidentiality", "-"))
                with cia_col2:
                    st.metric("Integrity", impact_data.get("integrity", "-"))
                with cia_col3:
                    st.metric("Availability", impact_data.get("availability", "-"))
                with cia_col4:
                    st.metric("Total", impact_data.get("total", "-"))

                if impact_data.get("rationale"):
                    st.markdown("**Rationale**")
                    st.write(impact_data.get("rationale"))

            st.divider()

    # Excluded patterns
    excluded_patterns = composition_analysis_data.get("excluded_patterns", [])
    if excluded_patterns:
        st.header("Excluded Patterns")
        st.info("Literature patterns excluded from matching (retained as evidence).")
        for pattern_id in excluded_patterns:
            st.write(f"• {pattern_id}")

# =========================================================
# TAB 3: CIA RISK & MITIGATIONS
# =========================================================

with tab_cia:
    st.header("Mitigation Coverage for Matched Compositions")

    if not matched_mitigations:
        if matched_compositions:
            st.warning("Matched compositions found, but no mitigation assessments available.")
        else:
            st.info("No matched compositions require mitigation coverage.")
    else:
        for assessment in matched_mitigations:
            if not isinstance(assessment, dict):
                continue

            pattern_id = assessment.get("pattern_id", "Unknown")
            pattern_name = assessment.get("pattern_name", "Unknown pattern")
            coverage_status = assessment.get("coverage_status", "Unknown")

            st.markdown(f"### {pattern_id} — {pattern_name}")
            st.markdown(f"**Coverage:** `{coverage_status}`")

            if assessment.get("note"):
                st.info(assessment.get("note"))

            # Literature mitigations
            lit_mitigations = assessment.get("literature_mitigations", [])
            if lit_mitigations:
                st.markdown("#### Literature-backed Mitigations")
                for mitigation in lit_mitigations:
                    m_id = mitigation.get("mitigation_id", "Unknown")
                    m_name = mitigation.get("mitigation_name", "Unknown")

                    with st.expander(f"{m_id} — {m_name}"):
                        st.write(f"**Type:** {mitigation.get('evidence_type', '-')}")
                        st.write(f"**Applicable:** {mitigation.get('applicability', '-')}")

                        if mitigation.get("supporting_papers"):
                            st.write(f"**Papers:** {mitigation.get('supporting_papers')}")
                        if mitigation.get("timing"):
                            st.write(f"**Timing:** {mitigation.get('timing')}")
                        if mitigation.get("effectiveness_evidence"):
                            st.write(f"**Evidence:** {mitigation.get('effectiveness_evidence')}")
                        if mitigation.get("limitations"):
                            st.write(f"**Limits:** {mitigation.get('limitations')}")

            # Project mitigations
            proj_mitigations = assessment.get("project_mitigations", [])
            if proj_mitigations:
                st.markdown("#### Project-derived Mitigations")
                for mitigation in proj_mitigations:
                    m_id = mitigation.get("mitigation_id", "Unknown")
                    m_name = mitigation.get("mitigation_name", "Unknown")

                    with st.expander(f"{m_id} — {m_name}"):
                        st.write(f"**Type:** {mitigation.get('control_type', '-')}")
                        st.write(f"**Timing:** {mitigation.get('timing', '-')}")
                        st.write(f"**Status:** {mitigation.get('evidence_status', '-')}")
                        st.write(f"**Rationale:** {mitigation.get('project_rationale', '')}")

            if assessment.get("warning"):
                st.warning(assessment.get("warning"))

            st.divider()

    # Open gaps
    st.header("Open Mitigation Gaps")

    if not open_mitigation_gaps:
        st.success("✓ No open mitigation gaps.")
    else:
        for gap in open_mitigation_gaps:
            if not isinstance(gap, dict):
                continue

            pattern_id = gap.get("pattern_id", "Unknown")
            gap_text = gap.get("gap", "No description.")
            proposals = gap.get("project_proposals", [])

            st.markdown(
                f'''<div class="finding risk-high">
                <strong>{pattern_id}</strong><br>
                {gap_text}
                </div>''',
                unsafe_allow_html=True,
            )

            if proposals:
                st.markdown("**Proposals**")
                for proposal in proposals:
                    st.write(f"• {proposal}")

            if gap.get("warning"):
                st.warning(gap.get("warning"))

# =========================================================
# TAB 4: INTERPRETATION LIMITS & DISCLAIMERS
# =========================================================

with tab_limits:
    st.header("Interpretation Limits and Disclaimers")

    limitation = composition_analysis_data.get("limitation")
    if limitation:
        st.warning(limitation)

    interpretation_data = composition_analysis_data.get("interpretation", {})
    if interpretation_data.get("impact_assessment"):
        st.info(interpretation_data.get("impact_assessment"))

    mitigation_semantics = mitigation_assessment_data.get("semantics")
    if mitigation_semantics:
        st.info(mitigation_semantics)

    applicability_rule = mitigation_assessment_data.get("applicability_rule")
    if applicability_rule:
        st.info(applicability_rule)

    st.caption("CIA totals represent CIA impact only, not converted to risk scores at this stage.")

    # Pattern coverage reference
    pattern_coverage = mitigation_assessment_data.get("pattern_coverage_reference", [])
    if pattern_coverage:
        st.divider()
        st.header("Pattern Coverage Reference (P1–P9)")

        for coverage in pattern_coverage:
            if not isinstance(coverage, dict):
                continue

            pattern_id = coverage.get("pattern_id", "Unknown")
            coverage_status = coverage.get("coverage_status", "Unknown")

            lit_ids = [
                m.get("mitigation_id", "Unknown")
                for m in coverage.get("literature_mitigations", [])
                if isinstance(m, dict)
            ]

            proj_ids = [
                m.get("mitigation_id", "Unknown")
                for m in coverage.get("project_mitigations", [])
                if isinstance(m, dict)
            ]

            lit_text = ", ".join(lit_ids) if lit_ids else "-"
            proj_text = ", ".join(proj_ids) if proj_ids else "-"

            st.markdown(f"**{pattern_id}:** `{coverage_status}`")
            st.caption(f"Literature: {lit_text} | Project: {proj_text}")

            if coverage.get("note"):
                st.write(coverage.get("note"))

    # Manual validation reference
    st.divider()
    st.header("Manual Validation Reference")

    st.caption(
        "Fixed, human-labelled reference tools used to calibrate the C1–C6 mapper. "
        "Shared names indicate mapper calibration checks."
    )

    try:
        validation_conn = sqlite3.connect(module_5_ontology_database.DB_PATH)
        try:
            mapper_rows = validation_conn.execute(
                """
                SELECT tools.name, tool_capabilities.capability_id
                FROM tool_capabilities
                JOIN tools ON tools.tool_id = tool_capabilities.tool_id
                WHERE tool_capabilities.source = 'mapper'
                """
            ).fetchall()
        finally:
            validation_conn.close()
    except sqlite3.Error as db_error:
        mapper_rows = []
        st.warning(f"Could not read ontology database: {db_error}")

    mapper_ids_by_name = {}
    for tool_name, capability_id in mapper_rows:
        mapper_ids_by_name.setdefault(tool_name, set()).add(capability_id)

    for ref_name, ref_description, ref_labels in module_5_ontology_database.MANUAL_VALIDATION_SET:
        manual_ids = {cap_id for cap_id, _confidence, _reason in ref_labels}

        with st.expander(f"{ref_name} — {ref_description}"):
            if ref_labels:
                for cap_id, confidence, reason in ref_labels:
                    st.write(
                        f"• Manual: {describe_capability(cap_id)} ({confidence}) — {reason}"
                    )
            else:
                st.write("• Manual: intentionally unmapped")

            mapper_ids = mapper_ids_by_name.get(ref_name)

            if mapper_ids is None:
                st.caption("No mapper verdict for same-named tool in this run.")
            elif mapper_ids == manual_ids:
                st.success(
                    "Mapper agrees: "
                    + (", ".join(sorted(describe_capability(c) for c in mapper_ids)) or "none")
                )
            else:
                st.error(
                    "Mapper disagrees — mapper: "
                    + (", ".join(sorted(describe_capability(c) for c in mapper_ids)) or "none")
                    + " · manual: "
                    + (", ".join(sorted(describe_capability(c) for c in manual_ids)) or "none")
                )

# =========================================================
# TAB 5: FINAL REPORT
# =========================================================

with tab_report:
    st.header("Final Report")

    report_text = st.session_state.report_text

    if report_text:
        st.download_button(
            label="Download Full Report",
            data=report_text,
            file_name="agent_pre_deployer_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

        with st.expander("View full report", expanded=False):
            st.text(report_text)

    else:
        st.warning(
            "The analysis completed, but the generated report could not be loaded."
        )

        final_report_path = analysis_result.get("final_report_path")
        if final_report_path:
            st.caption("Expected report path:")
            st.code(str(final_report_path))