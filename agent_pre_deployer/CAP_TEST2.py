"""
======================================================================
EXPERIMENT 2 — GOLD-SET CAPABILITY MAPPING ACCURACY
======================================================================

Purpose
-------
Evaluate the accuracy of the project's capability normalization and
C1-C6 mapping pipeline against the gold-standard reference set
provided as input.

The gold set is NOT created in this experiment.

Instead, Experiment 2 accepts an existing gold-set JSON containing:

    {
        "experiment": "...",
        "ontology_source": "...",
        "sampling_method": "...",
        "tool_count": 30,
        "gold_labels": [...]
    }

The C1-C6 ontology is imported directly from:

    modules/module_3_capability_normalization.py

No second ontology is maintained in this experiment.

Process
-------
Gold-set JSON
      |
      v
Load gold_labels
      |
      v
Locate exact tools using source_file + source_index
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
Calculate metrics
      |
      v
Save EXP2 results

======================================================================
"""

import csv
import json
from pathlib import Path

from modules import module_2_capability_extraction
from modules import module_3_capability_normalization


# ======================================================================
# CONFIGURATION
# ======================================================================

SCRIPT_DIR = Path(__file__).resolve().parent

DATA_DIR = SCRIPT_DIR / "data"

# Input gold-set JSON
GOLD_INPUT_JSON = SCRIPT_DIR / r"C:\Users\amal4\PycharmProjects\AgentPreDeployment_check\agent_pre_deployer\experiment_2_results\gold_set.json"

# Experiment 2 output directory
OUTPUT_DIR = SCRIPT_DIR / "EXP2"

# Experiment 2 output files
RESULT_JSON = OUTPUT_DIR / "exp2_results.json"
COMPARISON_CSV = OUTPUT_DIR / "exp2_results.csv"
METRICS_JSON = OUTPUT_DIR / "exp2_metrics.json"


# Use the exact ontology from Module 3.
CAPABILITY_ONTOLOGY = (
    module_3_capability_normalization.CAPABILITY_ONTOLOGY
)


# ======================================================================
# LOAD GOLD SET
# ======================================================================

def load_gold_set():
    """
    Load the existing gold-set JSON supplied as input.

    The gold set must contain:

        {
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

    if not GOLD_INPUT_JSON.exists():
        raise FileNotFoundError(
            f"Gold-set input file does not exist:\n"
            f"{GOLD_INPUT_JSON}"
        )

    with open(
        GOLD_INPUT_JSON,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Gold-set JSON must contain a JSON object."
        )

    gold_labels = data.get("gold_labels")

    if not isinstance(gold_labels, list):
        raise ValueError(
            "Gold-set JSON does not contain a valid "
            "'gold_labels' list."
        )

    if not gold_labels:
        raise ValueError(
            "Gold-set contains no gold labels."
        )

    return data


# ======================================================================
# LOAD TOOLS FROM SOURCE FILES
# ======================================================================

def load_json_file(filepath):
    """
    Load tools from common JSON structures.

    Supported:

        [
            {...},
            {...}
        ]

    or:

        {
            "tools": [...]
        }

    or:

        {
            "data": {
                "tools": [...]
            }
        }
    """

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        tools = data.get("tools")

        if isinstance(tools, list):
            return tools

        nested_data = data.get("data")

        if isinstance(nested_data, dict):

            tools = nested_data.get("tools")

            if isinstance(tools, list):
                return tools

    raise ValueError(
        f"Could not find a tools list in {filepath.name}"
    )


# ======================================================================
# RECONSTRUCT TOOLS FROM GOLD SET
# ======================================================================

def reconstruct_tools(gold_labels):
    """
    Reconstruct exactly the tools referenced by the gold set.

    Each gold record contains:

        source_file
        source_index

    Therefore the experiment does NOT perform:

        - file selection
        - tool selection
        - random sampling
        - manual annotation

    The gold set itself determines exactly which tools are evaluated.
    """

    tools = []

    print()
    print("=" * 110)
    print("RECONSTRUCTING TOOLS FROM GOLD SET")
    print("=" * 110)

    # Cache loaded JSON files so that each file is read only once.
    file_cache = {}

    for gold_record in gold_labels:

        source_file = gold_record.get("source_file")
        source_index = gold_record.get("source_index")

        tool_name = gold_record.get(
            "tool",
            "UNKNOWN"
        )

        if not source_file:
            raise ValueError(
                f"Missing source_file for tool: {tool_name}"
            )

        if source_index is None:
            raise ValueError(
                f"Missing source_index for tool: {tool_name}"
            )

        filepath = DATA_DIR / source_file

        if not filepath.exists():
            raise FileNotFoundError(
                f"Source file for tool '{tool_name}' "
                f"does not exist:\n{filepath}"
            )

        # Load file once.
        if source_file not in file_cache:
            file_cache[source_file] = load_json_file(
                filepath
            )

        source_tools = file_cache[source_file]

        if source_index < 0 or source_index >= len(source_tools):
            raise IndexError(
                f"source_index {source_index} is invalid "
                f"for {source_file}"
            )

        original_tool = source_tools[source_index]

        if not isinstance(original_tool, dict):
            raise ValueError(
                f"Tool at {source_file}[{source_index}] "
                f"is not a JSON object."
            )

        actual_tool_name = original_tool.get(
            "tool",
            ""
        )

        # Verify that the source position actually corresponds
        # to the tool recorded in the gold set.
        if actual_tool_name != tool_name:

            raise ValueError(
                "\nGold-set/source mismatch detected.\n"
                f"  Gold tool:   {tool_name}\n"
                f"  Source file: {source_file}\n"
                f"  Source index:{source_index}\n"
                f"  Actual tool: {actual_tool_name}\n"
            )

        tool_copy = dict(original_tool)

        # Experiment-only metadata.
        tool_copy["_source_file"] = source_file
        tool_copy["_source_index"] = source_index

        tools.append(tool_copy)

        print(
            f"{gold_record.get('annotation_id', '?'):>3}. "
            f"{tool_name:<45} "
            f"{source_file}[{source_index}]"
        )

    print()
    print(
        f"TOTAL TOOLS RECONSTRUCTED: {len(tools)}"
    )

    return tools


# ======================================================================
# PREPARE MODULE 2 INPUT
# ======================================================================

def prepare_module_input(selected_tools):
    """
    Convert reconstructed tools into the structure expected by Module 2.

    Experiment-only metadata beginning with '_' is removed.
    """

    clean_tools = []

    for tool in selected_tools:

        clean_tool = {
            key: value
            for key, value in tool.items()
            if not key.startswith("_")
        }

        clean_tools.append(clean_tool)

    return {
        "tools": clean_tools,
        "tool_count": len(clean_tools),
        "source_file": "EXP2_GOLD_SET"
    }


# ======================================================================
# RUN MODULE 2 + MODULE 3
# ======================================================================

def run_actual_pipeline(selected_tools):

    module_input = prepare_module_input(
        selected_tools
    )

    # ------------------------------------------------------------------
    # MODULE 2
    # ------------------------------------------------------------------

    print()
    print("=" * 100)
    print("RUNNING MODULE 2 — CAPABILITY EXTRACTION")
    print("=" * 100)

    result_2 = (
        module_2_capability_extraction.run(
            module_input
        )
    )

    # ------------------------------------------------------------------
    # MODULE 3
    # ------------------------------------------------------------------

    print()
    print("=" * 100)
    print(
        "RUNNING MODULE 3 — "
        "CAPABILITY NORMALIZATION + MAPPING"
    )
    print("=" * 100)

    result_3 = (
        module_3_capability_normalization.run(
            result_2
        )
    )

    return result_3


# ======================================================================
# PIPELINE PREDICTION
# ======================================================================

def get_pipeline_prediction(pipeline_tool):
    """
    Extract the final C1-C6 prediction from Module 3.
    """

    mapping = pipeline_tool.get(
        "mapping",
        {}
    )

    predicted = mapping.get(
        "all_capabilities",
        []
    )

    if not predicted:
        return []

    predicted = [
        capability
        for capability in predicted
        if capability in CAPABILITY_ONTOLOGY
    ]

    predicted.sort(
        key=lambda value: int(value[1:])
    )

    return predicted


# ======================================================================
# MATCH PIPELINE TOOL
# ======================================================================

def find_pipeline_tool(
    pipeline_tools,
    gold_record
):
    """
    Match the pipeline result to the gold record.

    Matching is performed using:

        1. tool name

    The pipeline receives the exact tools reconstructed from the gold
    set and in the same order, so this is deterministic.
    """

    tool_name = gold_record["tool"]

    for tool in pipeline_tools:

        if tool.get("tool") == tool_name:
            return tool

    return None


# ======================================================================
# COMPARE GOLD VS PIPELINE
# ======================================================================

def compare_results(
    gold_labels,
    pipeline_output
):
    """
    Compare supplied gold labels against Module 3 predictions.

    IMPORTANT:

    The gold labels are read-only reference data.

    This function does not modify them.
    """

    pipeline_tools = pipeline_output.get(
        "tools",
        []
    )

    comparison = []

    for gold_record in gold_labels:

        pipeline_tool = find_pipeline_tool(
            pipeline_tools,
            gold_record
        )

        gold = gold_record.get(
            "gold_capabilities",
            []
        )

        # --------------------------------------------------------------
        # Pipeline tool not found
        # --------------------------------------------------------------

        if pipeline_tool is None:

            comparison.append({

                "annotation_id":
                    gold_record["annotation_id"],

                "tool":
                    gold_record["tool"],

                "source_file":
                    gold_record["source_file"],

                "source_index":
                    gold_record["source_index"],

                "description":
                    gold_record["description"],

                "gold_capabilities":
                    gold,

                "predicted_capabilities":
                    [],

                "exact_match":
                    False,

                "status":
                    "NOT_FOUND_IN_PIPELINE",

                "primary_prediction":
                    None,

                "normalized_concepts":
                    [],

                "matched_expressions":
                    [],

                "normalization_confidence":
                    0.0,

                "mapping_reason":
                    "",

                "is_ambiguous":
                    False,

                "error_analysis":
                    "Pipeline tool not found."
            })

            continue

        # --------------------------------------------------------------
        # Pipeline prediction
        # --------------------------------------------------------------

        predicted = get_pipeline_prediction(
            pipeline_tool
        )

        normalized = pipeline_tool.get(
            "normalized",
            {}
        )

        mapping = pipeline_tool.get(
            "mapping",
            {}
        )

        exact_match = (
            set(gold)
            ==
            set(predicted)
        )

        comparison.append({

            "annotation_id":
                gold_record["annotation_id"],

            "tool":
                gold_record["tool"],

            "source_file":
                gold_record["source_file"],

            "source_index":
                gold_record["source_index"],

            "description":
                gold_record["description"],

            "gold_capabilities":
                gold,

            "predicted_capabilities":
                predicted,

            "exact_match":
                exact_match,

            "status":
                "CORRECT"
                if exact_match
                else "MISCLASSIFIED",

            "primary_prediction":
                mapping.get(
                    "primary_capability"
                ),

            "normalized_concepts":
                normalized.get(
                    "normalized_concepts",
                    []
                ),

            "matched_expressions":
                normalized.get(
                    "matched_expressions",
                    []
                ),

            "normalization_confidence":
                normalized.get(
                    "confidence",
                    0.0
                ),

            "mapping_reason":
                mapping.get(
                    "mapping_reason",
                    ""
                ),

            "is_ambiguous":
                mapping.get(
                    "is_ambiguous",
                    False
                ),

            "error_analysis":
                ""
        })

    return comparison


# ======================================================================
# CALCULATE METRICS
# ======================================================================

def calculate_metrics(comparison):
    """
    Calculate one-vs-rest metrics for each C1-C6 capability.

        TP = capability in GOLD and PREDICTED
        FP = capability not in GOLD but PREDICTED
        FN = capability in GOLD but not PREDICTED
    """

    metrics = {}

    for capability in CAPABILITY_ONTOLOGY:

        tp = 0
        fp = 0
        fn = 0

        for result in comparison:

            gold = set(
                result["gold_capabilities"]
            )

            predicted = set(
                result["predicted_capabilities"]
            )

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
            if precision_denominator
            else 0.0
        )

        recall = (
            tp / recall_denominator
            if recall_denominator
            else 0.0
        )

        f1 = (
            2 * precision * recall /
            (precision + recall)
            if precision + recall
            else 0.0
        )

        metrics[capability] = {

            "capability":
                capability,

            "canonical":
                CAPABILITY_ONTOLOGY[
                    capability
                ]["canonical"],

            "true_positive":
                tp,

            "false_positive":
                fp,

            "false_negative":
                fn,

            "precision":
                precision,

            "recall":
                recall,

            "f1":
                f1
        }

    # ------------------------------------------------------------------
    # Exact-set accuracy
    # ------------------------------------------------------------------

    total = len(comparison)

    exact_correct = sum(
        result["exact_match"]
        for result in comparison
    )

    exact_set_accuracy = (
        exact_correct / total
        if total
        else 0.0
    )

    # ------------------------------------------------------------------
    # Overall micro counts
    # ------------------------------------------------------------------

    total_tp = sum(
        metrics[capability]["true_positive"]
        for capability in CAPABILITY_ONTOLOGY
    )

    total_fp = sum(
        metrics[capability]["false_positive"]
        for capability in CAPABILITY_ONTOLOGY
    )

    total_fn = sum(
        metrics[capability]["false_negative"]
        for capability in CAPABILITY_ONTOLOGY
    )

    micro_precision = (
        total_tp / (total_tp + total_fp)
        if total_tp + total_fp
        else 0.0
    )

    micro_recall = (
        total_tp / (total_tp + total_fn)
        if total_tp + total_fn
        else 0.0
    )

    micro_f1 = (
        2 * micro_precision * micro_recall /
        (micro_precision + micro_recall)
        if micro_precision + micro_recall
        else 0.0
    )

    metrics["_overall"] = {

        "tool_count":
            total,

        "exact_set_correct":
            exact_correct,

        "exact_set_accuracy":
            exact_set_accuracy,

        "micro_precision":
            micro_precision,

        "micro_recall":
            micro_recall,

        "micro_f1":
            micro_f1
    }

    return metrics


# ======================================================================
# PRINT COMPARISON
# ======================================================================

def print_comparison(comparison):

    print()
    print("=" * 115)
    print("GOLD SET VS PIPELINE PREDICTION")
    print("=" * 115)

    for result in comparison:

        gold = (
            ", ".join(
                result["gold_capabilities"]
            )
            if result["gold_capabilities"]
            else "NONE"
        )

        predicted = (
            ", ".join(
                result["predicted_capabilities"]
            )
            if result["predicted_capabilities"]
            else "NONE"
        )

        symbol = (
            "✓"
            if result["exact_match"]
            else "✗"
        )

        print()
        print("-" * 115)

        print(
            f"{symbol} {result['tool']}"
        )

        print(
            f"    Source:       "
            f"{result['source_file']}"
            f"[{result['source_index']}]"
        )

        print(
            f"    GOLD:         "
            f"{gold}"
        )

        print(
            f"    PREDICTED:    "
            f"{predicted}"
        )

        print(
            f"    Exact match:  "
            f"{result['exact_match']}"
        )

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

        print(
            f"      Ambiguous: "
            f"{result['is_ambiguous']}"
        )

        print(
            f"      Mapping reason: "
            f"{result['mapping_reason']}"
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

    print(
        f"Micro precision: "
        f"{overall['micro_precision']:.3f}"
    )

    print(
        f"Micro recall:    "
        f"{overall['micro_recall']:.3f}"
    )

    print(
        f"Micro F1:        "
        f"{overall['micro_f1']:.3f}"
    )

    print("=" * 105)


# ======================================================================
# SAVE EXP2 RESULTS
# ======================================================================

def save_results(
    gold_input,
    comparison,
    metrics
):
    """
    Save the complete Experiment 2 result.

    The original gold labels are preserved exactly as supplied.

    The output contains:

        - experiment metadata
        - input gold-set metadata
        - gold_labels
        - pipeline comparison
        - metrics
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    result = {

        "experiment":
            "Experiment 2 — Gold-set capability mapping accuracy",

        "input_gold_set":
            GOLD_INPUT_JSON.name,

        "ontology_source":
            (
                "modules.module_3_capability_normalization."
                "CAPABILITY_ONTOLOGY"
            ),

        "sampling_method":
            gold_input.get(
                "sampling_method",
                "Provided externally"
            ),

        "tool_count":
            len(comparison),

        "gold_labels":
            gold_input["gold_labels"],

        "results":
            comparison,

        "metrics":
            metrics
    }

    with open(
        RESULT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("Experiment 2 JSON saved:")
    print(f"  {RESULT_JSON}")


# ======================================================================
# SAVE CSV
# ======================================================================

def save_comparison_csv(comparison):

    fieldnames = [

        "annotation_id",
        "tool",
        "source_file",
        "source_index",
        "gold_capabilities",
        "predicted_capabilities",
        "exact_match",
        "status",
        "primary_prediction",
        "normalized_concepts",
        "matched_expressions",
        "normalization_confidence",
        "mapping_reason",
        "is_ambiguous",
        "error_analysis"
    ]

    with open(
        COMPARISON_CSV,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for result in comparison:

            writer.writerow({

                "annotation_id":
                    result["annotation_id"],

                "tool":
                    result["tool"],

                "source_file":
                    result["source_file"],

                "source_index":
                    result["source_index"],

                "gold_capabilities":
                    ",".join(
                        result["gold_capabilities"]
                    ),

                "predicted_capabilities":
                    ",".join(
                        result["predicted_capabilities"]
                    ),

                "exact_match":
                    result["exact_match"],

                "status":
                    result["status"],

                "primary_prediction":
                    result["primary_prediction"],

                "normalized_concepts":
                    ",".join(
                        result["normalized_concepts"]
                    ),

                "matched_expressions":
                    ",".join(
                        result["matched_expressions"]
                    ),

                "normalization_confidence":
                    result["normalization_confidence"],

                "mapping_reason":
                    result["mapping_reason"],

                "is_ambiguous":
                    result["is_ambiguous"],

                "error_analysis":
                    result["error_analysis"]
            })

    print()
    print("Experiment 2 CSV saved:")
    print(f"  {COMPARISON_CSV}")


# ======================================================================
# SAVE METRICS
# ======================================================================

def save_metrics(metrics):

    with open(
        METRICS_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("Experiment 2 metrics saved:")
    print(f"  {METRICS_JSON}")


# ======================================================================
# MAIN
# ======================================================================

def main():

    print()
    print("=" * 110)
    print(
        "EXPERIMENT 2 — GOLD-SET CAPABILITY MAPPING ACCURACY"
    )
    print("=" * 110)

    print()
    print("Input:")
    print(
        f"  {GOLD_INPUT_JSON}"
    )

    print()
    print("Ontology source:")
    print(
        "  modules.module_3_capability_normalization."
        "CAPABILITY_ONTOLOGY"
    )

    print()
    print(
        "The gold set is supplied externally."
    )

    print(
        "No file selection or manual annotation is performed."
    )

    # ==================================================================
    # STEP 1 — LOAD EXISTING GOLD SET
    # ==================================================================

    gold_input = load_gold_set()

    gold_labels = gold_input["gold_labels"]

    print()
    print(
        f"Gold labels loaded: {len(gold_labels)}"
    )

    # ==================================================================
    # STEP 2 — RECONSTRUCT EXACT TOOLS
    # ==================================================================

    selected_tools = reconstruct_tools(
        gold_labels
    )

    # ==================================================================
    # STEP 3 — RUN MODULE 2 + MODULE 3
    # ==================================================================

    pipeline_output = run_actual_pipeline(
        selected_tools
    )

    # ==================================================================
    # STEP 4 — COMPARE GOLD VS PIPELINE
    # ==================================================================

    comparison = compare_results(
        gold_labels,
        pipeline_output
    )

    # ==================================================================
    # STEP 5 — DISPLAY COMPARISON
    # ==================================================================

    print_comparison(
        comparison
    )

    # ==================================================================
    # STEP 6 — CALCULATE METRICS
    # ==================================================================

    metrics = calculate_metrics(
        comparison
    )

    # ==================================================================
    # STEP 7 — DISPLAY METRICS
    # ==================================================================

    print_metrics(
        metrics
    )

    # ==================================================================
    # STEP 8 — SAVE RESULTS
    # ==================================================================

    save_results(
        gold_input,
        comparison,
        metrics
    )

    save_comparison_csv(
        comparison
    )

    save_metrics(
        metrics
    )

    # ==================================================================
    # COMPLETE
    # ==================================================================

    print()
    print()
    print("=" * 110)
    print("EXPERIMENT 2 COMPLETE")
    print("=" * 110)

    print()
    print("Results directory:")
    print(
        f"  {OUTPUT_DIR}"
    )

    print()
    print("Files created:")

    print(
        f"  1. {RESULT_JSON.name}"
    )

    print(
        f"  2. {COMPARISON_CSV.name}"
    )

    print(
        f"  3. {METRICS_JSON.name}"
    )

    print()
    print("Methodological property:")

    print(
        "The gold labels were supplied as an existing "
        "independent reference set."
    )

    print(
        "Experiment 2 does not create, modify, or select "
        "the gold labels."
    )

    print(
        "The pipeline is evaluated against the supplied "
        "gold standard exactly as provided."
    )

    print()
    print("=" * 110)


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()