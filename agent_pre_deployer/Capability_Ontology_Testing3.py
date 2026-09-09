"""======================================================================
EXPERIMENT 3 — SYNTHETIC BALANCED GOLD-SET CAPABILITY MAPPING ACCURACY
======================================================================

Purpose
-------
Evaluate the accuracy of the project's capability normalization and
C1-C6 mapping pipeline (Module 2 -> Module 3) against a SYNTHETIC,
CAPABILITY-BALANCED gold set supplied as an existing input file:

    data/created_toolsc1_c6.json

The tool set is NOT created in this experiment.
It was generated separately (AI-authored, labels assigned by
construction) and is consumed here exactly as provided, mirroring
Experiment 2's methodology. No user input is required at any point.

Key methodological property
---------------------------
Gold labels in the input file were assigned BY CONSTRUCTION:
each tool description was authored to exhibit exactly one target
capability (or one target capability pair), and that target IS the
gold label. The authoring model never assigned or saw label fields.
This experiment treats the labels as read-only reference data.

Balance guarantee
-----------------
Every capability C1-C6 appears in the gold set the SAME number of
times (5 single-capability tools per capability, plus each
capability appearing in exactly 2 of the 6 rotating pairs
C1+C2, C2+C3, C3+C4, C4+C5, C5+C6, C6+C1 — 7 occurrences each
across 36 tools). The balance is asserted programmatically before
the pipeline runs; the experiment aborts if the input is unbalanced.

Process
-------
Load data/created_toolsc1_c6.json
      |
      v
Assert C1-C6 capability balance
      |
      v
Module 2 — Capability Extraction
      |
      v
Module 3 — Capability Normalization + C1-C6 Mapping
      |
      v
Compare predictions against supplied gold labels
      |
      v
Calculate metrics (same definitions as Experiment 2)
      |
      v
Save EXP3 results

The C1-C6 ontology is imported directly from:
    modules/module_3_capability_normalization.py
No second ontology is maintained in this experiment.
======================================================================"""

import csv
import json
from pathlib import Path

from modules import module_2_capability_extraction
from modules import module_3_capability_normalization

# ======================================================================
# CONFIGURATION
# ======================================================================

SCRIPT_DIR = Path(__file__).resolve().parent

# Shared data directory (same one Experiment 2 reads from).
DATA_DIR = SCRIPT_DIR / "data"

# Input: standalone AI-generated balanced tool set, supplied
# externally. This experiment never creates or modifies it.
CREATED_TOOLS_JSON = DATA_DIR / "created_toolsc1_c6.json"

# Experiment 3 output directory
OUTPUT_DIR = SCRIPT_DIR / "EXP3"

# Experiment 3 output files
RESULT_JSON = OUTPUT_DIR / "exp3_results.json"
COMPARISON_CSV = OUTPUT_DIR / "exp3_results.csv"
METRICS_JSON = OUTPUT_DIR / "exp3_metrics.json"

# Use the exact ontology from Module 3.
CAPABILITY_ONTOLOGY = (
    module_3_capability_normalization.CAPABILITY_ONTOLOGY
)

CAPABILITY_IDS = sorted(
    CAPABILITY_ONTOLOGY,
    key=lambda value: int(value[1:])
)


# ======================================================================
# LOAD CREATED TOOL SET
# ======================================================================


def load_created_tools():
    """
    Load the existing created_toolsc1_c6.json supplied as input.

    The file must contain:

        {
            "experiment": "...",
            "ontology_source": "...",
            "sampling_method": "...",
            "tool_count": 36,
            "capability_counts": {...},
            "tools": [...],
            "gold_labels": [
                {
                    "annotation_id": ...,
                    "tool": ...,
                    "description": ...,
                    "source_file": ...,
                    "source_index": ...,
                    "gold_capabilities": [...]
                }
            ]
        }
    """
    if not CREATED_TOOLS_JSON.exists():
        raise FileNotFoundError(
            "Created tool set input file does not exist:\n"
            f"{CREATED_TOOLS_JSON}\n"
            "Place created_toolsc1_c6.json in the data/ directory."
        )

    with open(
        CREATED_TOOLS_JSON,
        "r",
        encoding="utf-8"
    ) as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError(
            f"{CREATED_TOOLS_JSON.name} must contain a JSON object."
        )

    gold_labels = payload.get("gold_labels")

    if not isinstance(gold_labels, list):
        raise ValueError(
            f"{CREATED_TOOLS_JSON.name} does not contain a valid "
            "'gold_labels' list."
        )

    if not gold_labels:
        raise ValueError(
            f"{CREATED_TOOLS_JSON.name} contains no gold labels."
        )

    for record in gold_labels:
        if not isinstance(record, dict):
            raise ValueError("Gold label entry is not an object.")
        for key in (
            "annotation_id",
            "tool",
            "description",
            "gold_capabilities",
        ):
            if key not in record:
                raise ValueError(
                    f"Gold label missing required key '{key}': "
                    f"{record.get('tool', '?')}"
                )
        for cid in record["gold_capabilities"]:
            if cid not in CAPABILITY_ONTOLOGY:
                raise ValueError(
                    f"Unknown capability '{cid}' in gold label "
                    f"for tool '{record['tool']}'."
                )

    return gold_labels, payload


def assert_balanced(gold_labels):
    """Assert every capability appears equally often. Print the table."""
    counts = {cid: 0 for cid in CAPABILITY_IDS}
    for record in gold_labels:
        for cid in record["gold_capabilities"]:
            counts[cid] += 1

    print()
    print("=" * 110)
    print("GOLD-SET CAPABILITY BALANCE")
    print("=" * 110)
    for cid in CAPABILITY_IDS:
        print(
            f"  {cid}  "
            f"{CAPABILITY_ONTOLOGY[cid]['canonical']:<30} "
            f"{counts[cid]:>3} occurrences"
        )

    distinct = set(counts.values())
    if len(distinct) != 1:
        raise RuntimeError(
            f"Gold set is NOT balanced: {counts}"
        )
    print(
        f"\n  BALANCED: every capability appears exactly "
        f"{distinct.pop()} times across {len(gold_labels)} tools."
    )
    return counts


# ======================================================================
# PREPARE MODULE 2 INPUT
# ======================================================================


def prepare_module_input(gold_labels):
    """Convert the supplied tools into the structure expected by
    Module 2. Gold labels are NOT passed to the pipeline."""
    clean_tools = [
        {
            "tool": record["tool"],
            "description": record["description"],
        }
        for record in gold_labels
    ]
    return {
        "tools": clean_tools,
        "tool_count": len(clean_tools),
        "source_file": "EXP3_SYNTHETIC_GOLD_SET",
    }


# ======================================================================
# RUN MODULE 2 + MODULE 3
# ======================================================================


def run_actual_pipeline(gold_labels):
    module_input = prepare_module_input(gold_labels)

    print()
    print("=" * 100)
    print("RUNNING MODULE 2 — CAPABILITY EXTRACTION")
    print("=" * 100)
    result_2 = module_2_capability_extraction.run(module_input)

    print()
    print("=" * 100)
    print("RUNNING MODULE 3 — CAPABILITY NORMALIZATION + MAPPING")
    print("=" * 100)
    result_3 = module_3_capability_normalization.run(result_2)

    return result_3


# ======================================================================
# PIPELINE PREDICTION
# ======================================================================


def get_pipeline_prediction(pipeline_tool):
    """Extract the final C1-C6 prediction from Module 3."""
    mapping = pipeline_tool.get("mapping", {})
    predicted = mapping.get("all_capabilities", [])
    if not predicted:
        return []
    predicted = [
        capability
        for capability in predicted
        if capability in CAPABILITY_ONTOLOGY
    ]
    predicted.sort(key=lambda value: int(value[1:]))
    return predicted


def find_pipeline_tool(pipeline_tools, gold_record):
    """Match the pipeline result to the gold record by tool name.
    Names are unique in the supplied tool set, so this is
    deterministic."""
    tool_name = gold_record["tool"]
    for tool in pipeline_tools:
        if tool.get("tool") == tool_name:
            return tool
    return None


# ======================================================================
# COMPARE GOLD VS PIPELINE
# ======================================================================


def compare_results(gold_labels, pipeline_output):
    """Compare supplied gold labels against Module 3 predictions.

    IMPORTANT:
    The gold labels are read-only reference data.
    This function does not modify them.
    """
    pipeline_tools = pipeline_output.get("tools", [])
    comparison = []

    for gold_record in gold_labels:
        pipeline_tool = find_pipeline_tool(
            pipeline_tools, gold_record
        )
        gold = gold_record.get("gold_capabilities", [])

        if pipeline_tool is None:
            comparison.append({
                "annotation_id": gold_record["annotation_id"],
                "tool": gold_record["tool"],
                "source_file": gold_record.get(
                    "source_file", CREATED_TOOLS_JSON.name
                ),
                "source_index": gold_record.get(
                    "source_index"
                ),
                "description": gold_record["description"],
                "gold_capabilities": gold,
                "predicted_capabilities": [],
                "exact_match": False,
                "status": "NOT_FOUND_IN_PIPELINE",
                "primary_prediction": None,
                "normalized_concepts": [],
                "matched_expressions": [],
                "normalization_confidence": 0.0,
                "mapping_reason": "",
                "is_ambiguous": False,
                "error_analysis": "Pipeline tool not found.",
            })
            continue

        predicted = get_pipeline_prediction(pipeline_tool)
        normalized = pipeline_tool.get("normalized", {})
        mapping = pipeline_tool.get("mapping", {})
        exact_match = set(gold) == set(predicted)

        comparison.append({
            "annotation_id": gold_record["annotation_id"],
            "tool": gold_record["tool"],
            "source_file": gold_record.get(
                "source_file", CREATED_TOOLS_JSON.name
            ),
            "source_index": gold_record.get("source_index"),
            "description": gold_record["description"],
            "gold_capabilities": gold,
            "predicted_capabilities": predicted,
            "exact_match": exact_match,
            "status": (
                "CORRECT" if exact_match else "MISCLASSIFIED"
            ),
            "primary_prediction": mapping.get(
                "primary_capability"
            ),
            "normalized_concepts": normalized.get(
                "normalized_concepts", []
            ),
            "matched_expressions": normalized.get(
                "matched_expressions", []
            ),
            "normalization_confidence": normalized.get(
                "confidence", 0.0
            ),
            "mapping_reason": mapping.get("mapping_reason", ""),
            "is_ambiguous": mapping.get("is_ambiguous", False),
            "error_analysis": "",
        })

    return comparison


# ======================================================================
# CALCULATE METRICS (same definitions as Experiment 2)
# ======================================================================


def calculate_metrics(comparison):
    """One-vs-rest metrics per capability.

        TP = capability in GOLD and PREDICTED
        FP = capability not in GOLD but PREDICTED
        FN = capability in GOLD but not PREDICTED
    """
    metrics = {}

    for capability in CAPABILITY_ONTOLOGY:
        tp = fp = fn = 0
        for result in comparison:
            gold = set(result["gold_capabilities"])
            predicted = set(result["predicted_capabilities"])
            in_gold = capability in gold
            in_predicted = capability in predicted
            if in_gold and in_predicted:
                tp += 1
            elif not in_gold and in_predicted:
                fp += 1
            elif in_gold and not in_predicted:
                fn += 1

        precision_denominator = tp + fp
        recall_denominator = tp + fn
        precision = (
            tp / precision_denominator
            if precision_denominator else 0.0
        )
        recall = (
            tp / recall_denominator
            if recall_denominator else 0.0
        )
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )

        metrics[capability] = {
            "capability": capability,
            "canonical": CAPABILITY_ONTOLOGY[
                capability
            ]["canonical"],
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    # ------------------------------------------------------------------
    # Exact-set accuracy
    # ------------------------------------------------------------------
    total = len(comparison)
    exact_correct = sum(
        result["exact_match"] for result in comparison
    )
    exact_set_accuracy = (
        exact_correct / total if total else 0.0
    )

    # ------------------------------------------------------------------
    # Overall micro counts
    # ------------------------------------------------------------------
    total_tp = sum(
        metrics[c]["true_positive"] for c in CAPABILITY_ONTOLOGY
    )
    total_fp = sum(
        metrics[c]["false_positive"] for c in CAPABILITY_ONTOLOGY
    )
    total_fn = sum(
        metrics[c]["false_negative"] for c in CAPABILITY_ONTOLOGY
    )

    micro_precision = (
        total_tp / (total_tp + total_fp)
        if total_tp + total_fp else 0.0
    )
    micro_recall = (
        total_tp / (total_tp + total_fn)
        if total_tp + total_fn else 0.0
    )
    micro_f1 = (
        2 * micro_precision * micro_recall
        / (micro_precision + micro_recall)
        if micro_precision + micro_recall else 0.0
    )

    # Macro F1 is meaningful here BECAUSE the set is balanced.
    macro_f1 = sum(
        metrics[c]["f1"] for c in CAPABILITY_ONTOLOGY
    ) / len(CAPABILITY_ONTOLOGY)

    metrics["_overall"] = {
        "tool_count": total,
        "exact_set_correct": exact_correct,
        "exact_set_accuracy": exact_set_accuracy,
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": micro_f1,
        "macro_f1": macro_f1,
    }

    return metrics


# ======================================================================
# PRINT COMPARISON
# ======================================================================


def print_comparison(comparison):
    print()
    print("=" * 115)
    print("SYNTHETIC GOLD SET VS PIPELINE PREDICTION")
    print("=" * 115)

    for result in comparison:
        gold = (
            ", ".join(result["gold_capabilities"])
            if result["gold_capabilities"] else "NONE"
        )
        predicted = (
            ", ".join(result["predicted_capabilities"])
            if result["predicted_capabilities"] else "NONE"
        )
        symbol = "\u2713" if result["exact_match"] else "\u2717"

        print()
        print("-" * 115)
        print(f"{symbol} {result['tool']}")
        print(f"    GOLD:         {gold}")
        print(f"    PREDICTED:    {predicted}")
        print(f"    Exact match:  {result['exact_match']}")
        print()
        print("    Pipeline evidence:")
        print(
            f"      Primary prediction: "
            f"{result['primary_prediction']}"
        )
        print(
            f"      Normalized concepts: "
            f"{result['normalized_concepts']}"
        )
        print(
            f"      Matched expressions: "
            f"{result['matched_expressions']}"
        )
        print(
            f"      Confidence: "
            f"{result['normalization_confidence']}"
        )
        print(f"      Ambiguous: {result['is_ambiguous']}")
        print(
            f"      Mapping reason: {result['mapping_reason']}"
        )


# ======================================================================
# PRINT METRICS
# ======================================================================


def print_metrics(metrics):
    print()
    print("=" * 105)
    print("PER-CAPABILITY METRICS")
    print("=" * 105)
    print()
    print(
        f"{'Capability':<12}"
        f"{'TP':>8}"
        f"{'FP':>8}"
        f"{'FN':>8}"
        f"{'Precision':>14}"
        f"{'Recall':>14}"
        f"{'F1':>14}"
    )
    print("-" * 90)

    for capability in CAPABILITY_ONTOLOGY:
        result = metrics[capability]
        print(
            f"{capability:<12}"
            f"{result['true_positive']:>8}"
            f"{result['false_positive']:>8}"
            f"{result['false_negative']:>8}"
            f"{result['precision']:>14.3f}"
            f"{result['recall']:>14.3f}"
            f"{result['f1']:>14.3f}"
        )

    overall = metrics["_overall"]
    print()
    print("=" * 105)
    print(
        f"Exact-set correct: "
        f"{overall['exact_set_correct']}/"
        f"{overall['tool_count']}"
    )
    print(
        f"Exact-set accuracy: "
        f"{overall['exact_set_accuracy'] * 100:.2f}%"
    )
    print()
    print(f"Micro precision: {overall['micro_precision']:.3f}")
    print(f"Micro recall:    {overall['micro_recall']:.3f}")
    print(f"Micro F1:        {overall['micro_f1']:.3f}")
    print(f"Macro F1:        {overall['macro_f1']:.3f}")
    print("=" * 105)


# ======================================================================
# SAVE RESULTS
# ======================================================================


def save_results(gold_payload, comparison, metrics):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = {
        "experiment": gold_payload.get(
            "experiment",
            "Experiment 3 \u2014 Synthetic balanced gold-set "
            "capability mapping accuracy",
        ),
        "input_gold_set": CREATED_TOOLS_JSON.name,
        "ontology_source": (
            "modules.module_3_capability_normalization."
            "CAPABILITY_ONTOLOGY"
        ),
        "sampling_method": gold_payload.get(
            "sampling_method", "Provided externally"
        ),
        "tool_count": len(comparison),
        "capability_counts": gold_payload.get(
            "capability_counts"
        ),
        "gold_labels": gold_payload["gold_labels"],
        "results": comparison,
        "metrics": metrics,
    }
    with open(RESULT_JSON, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    print()
    print("Experiment 3 JSON saved:")
    print(f"  {RESULT_JSON}")


def save_comparison_csv(comparison):
    fieldnames = [
        "annotation_id", "tool", "source_file", "source_index",
        "gold_capabilities", "predicted_capabilities",
        "exact_match", "status", "primary_prediction",
        "normalized_concepts", "matched_expressions",
        "normalization_confidence", "mapping_reason",
        "is_ambiguous", "error_analysis",
    ]
    with open(
        COMPARISON_CSV, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in comparison:
            writer.writerow({
                "annotation_id": result["annotation_id"],
                "tool": result["tool"],
                "source_file": result["source_file"],
                "source_index": result["source_index"],
                "gold_capabilities": ",".join(
                    result["gold_capabilities"]
                ),
                "predicted_capabilities": ",".join(
                    result["predicted_capabilities"]
                ),
                "exact_match": result["exact_match"],
                "status": result["status"],
                "primary_prediction": result[
                    "primary_prediction"
                ],
                "normalized_concepts": ",".join(
                    str(x) for x in result["normalized_concepts"]
                ),
                "matched_expressions": ",".join(
                    str(x) for x in result["matched_expressions"]
                ),
                "normalization_confidence": result[
                    "normalization_confidence"
                ],
                "mapping_reason": result["mapping_reason"],
                "is_ambiguous": result["is_ambiguous"],
                "error_analysis": result["error_analysis"],
            })
    print()
    print("Experiment 3 CSV saved:")
    print(f"  {COMPARISON_CSV}")


def save_metrics(metrics):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(METRICS_JSON, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4, ensure_ascii=False)
    print()
    print("Experiment 3 metrics saved:")
    print(f"  {METRICS_JSON}")


# ======================================================================
# MAIN
# ======================================================================


def main():
    print()
    print("=" * 110)
    print(
        "EXPERIMENT 3 \u2014 SYNTHETIC BALANCED GOLD-SET "
        "CAPABILITY MAPPING ACCURACY"
    )
    print("=" * 110)
    print()
    print("Input:")
    print(f"  {CREATED_TOOLS_JSON}")
    print()
    print("Ontology source:")
    print(
        "  modules.module_3_capability_normalization."
        "CAPABILITY_ONTOLOGY"
    )
    print()
    print(
        "The tool set is supplied externally (AI-generated, "
        "labels by construction)."
    )
    print(
        "No generation, file selection, or manual annotation "
        "is performed."
    )

    # ==================================================================
    # STEP 1 — LOAD THE SUPPLIED CREATED TOOL SET
    # ==================================================================
    gold_labels, gold_payload = load_created_tools()

    print()
    print(f"Gold labels loaded: {len(gold_labels)}")

    # ==================================================================
    # STEP 2 — ASSERT CAPABILITY BALANCE
    # ==================================================================
    assert_balanced(gold_labels)

    # ==================================================================
    # STEP 3 — RUN MODULE 2 + MODULE 3
    # ==================================================================
    pipeline_output = run_actual_pipeline(gold_labels)

    # ==================================================================
    # STEP 4 — COMPARE GOLD VS PIPELINE
    # ==================================================================
    comparison = compare_results(gold_labels, pipeline_output)

    # ==================================================================
    # STEP 5 — DISPLAY COMPARISON
    # ==================================================================
    print_comparison(comparison)

    # ==================================================================
    # STEP 6 — CALCULATE + DISPLAY METRICS
    # ==================================================================
    metrics = calculate_metrics(comparison)
    print_metrics(metrics)

    # ==================================================================
    # STEP 7 — SAVE RESULTS
    # ==================================================================
    save_results(gold_payload, comparison, metrics)
    save_comparison_csv(comparison)
    save_metrics(metrics)

    # ==================================================================
    # COMPLETE
    # ==================================================================
    print()
    print("=" * 110)
    print("EXPERIMENT 3 COMPLETE")
    print("=" * 110)
    print()
    print("Results directory:")
    print(f"  {OUTPUT_DIR}")
    print()
    print("Files created:")
    print(f"  1. {RESULT_JSON.name}")
    print(f"  2. {COMPARISON_CSV.name}")
    print(f"  3. {METRICS_JSON.name}")
    print()
    print("Methodological properties:")
    print(
        "  1. The gold labels were supplied as an existing "
        "independent reference set"
    )
    print(
        "     with labels assigned by construction; this "
        "experiment does not create,"
    )
    print("     modify, or select them.")
    print(
        "  2. Every capability C1-C6 appears an identical number "
        "of times (asserted"
    )
    print("     before the pipeline runs).")
    print(
        "  3. The pipeline is evaluated against the supplied "
        "gold standard exactly"
    )
    print("     as provided.")
    print()
    print("=" * 110)


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()
