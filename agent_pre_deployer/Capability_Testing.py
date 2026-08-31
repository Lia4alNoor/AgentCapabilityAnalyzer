"""
======================================================================
EXPERIMENT 1 — GOLD-SET CAPABILITY MAPPING ACCURACY
======================================================================

Purpose
-------
Evaluate the accuracy of the project's capability normalization and
C1-C6 mapping pipeline against an independently created gold-standard
reference set.


The C1-C6 ontology is imported directly from:

    modules/module_3_capability_normalization.py

No second ontology is maintained in this experiment.

======================================================================
"""

import csv
import json
from pathlib import Path

from modules import module_2_capability_extraction
from modules import module_3_capability_normalization


# CONFIGURATION

SCRIPT_DIR = Path(__file__).resolve().parent

DATA_DIR = SCRIPT_DIR / "data"

OUTPUT_DIR = SCRIPT_DIR / "experiment_2_results"

NUMBER_OF_TOOLS = 30

GOLD_JSON = OUTPUT_DIR / "gold_set.json"
COMPARISON_JSON = OUTPUT_DIR / "gold_vs_pipeline.json"
COMPARISON_CSV = OUTPUT_DIR / "gold_vs_pipeline.csv"
METRICS_JSON = OUTPUT_DIR / "metrics1.json"


CAPABILITY_ONTOLOGY = (
    module_3_capability_normalization.CAPABILITY_ONTOLOGY
)


# FILE DISCOVERY

def find_json_files():
    """
    Find JSON files directly inside the data directory.

    Files are sorted alphabetically to make selection deterministic.
    """

    if not DATA_DIR.exists():
        print()
        print("ERROR: Data directory does not exist:")
        print(DATA_DIR)
        return []

    return sorted(
        DATA_DIR.glob("*.json"),
        key=lambda path: path.name.lower()
    )


# ======================================================================
# FILE SELECTION
# ======================================================================

def select_json_files(json_files):
    """
    Display available JSON files and allow the researcher to select
    one or more files using their numbers.

    Example:
        1,3,5
    """

    print()
    print("=" * 100)
    print("AVAILABLE JSON FILES")
    print("=" * 100)

    print()
    print(f"Data directory: {DATA_DIR}")
    print()

    for number, filepath in enumerate(json_files, start=1):
        print(f"{number:>3}. {filepath.name}")

    print()
    print("Select one or more files by number.")
    print("Example: 1,3,5")

    while True:

        answer = input("\nFile numbers: ").strip()

        if not answer:
            print("Please select at least one file.")
            continue

        try:
            indices = [
                int(value.strip())
                for value in answer.split(",")
                if value.strip()
            ]
        except ValueError:
            print("Invalid input. Use numbers separated by commas.")
            continue

        # Remove duplicates while preserving order.
        indices = list(dict.fromkeys(indices))

        invalid = [
            index
            for index in indices
            if index < 1 or index > len(json_files)
        ]

        if invalid:
            print(f"Invalid file number(s): {invalid}")
            continue

        selected = [
            json_files[index - 1]
            for index in indices
        ]

        break

    print()
    print("=" * 100)
    print("SELECTED JSON FILES")
    print("=" * 100)

    for number, filepath in enumerate(selected, start=1):
        print(f"{number}. {filepath.name}")

    return selected


# ======================================================================
# JSON LOADING
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

    with open(filepath, "r", encoding="utf-8") as file:
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
# TOOL EXTRACTION
# ======================================================================

def load_tools_from_files(selected_files):
    """
    Load all tools from the selected JSON files.

    Every tool receives internal metadata:

        _source_file
        _source_index

    These fields are used only by the experiment and are removed before
    Module 2 is executed.
    """

    all_tools = []

    print()
    print("=" * 100)
    print("EXTRACTING TOOLS")
    print("=" * 100)

    for filepath in selected_files:

        print()
        print(f"Reading: {filepath.name}")

        try:
            tools = load_json_file(filepath)
        except Exception as error:
            print(f"ERROR reading {filepath.name}: {error}")
            continue

        valid_count = 0

        for index, tool in enumerate(tools):

            if not isinstance(tool, dict):
                continue

            tool_copy = dict(tool)

            tool_copy["_source_file"] = filepath.name
            tool_copy["_source_index"] = index

            all_tools.append(tool_copy)

            valid_count += 1

        print(f"  Tools found: {valid_count}")

    print()
    print(f"TOTAL VALID TOOLS FOUND: {len(all_tools)}")

    return all_tools


# SELECT FIRST 15 TOOLS

def select_first_15_tools(all_tools):
    """
    Automatically select the first 15 tools.

    This makes the sampling procedure deterministic:

        selected JSON files
              ↓
        file order
              ↓
        tool order within files
              ↓
        first 15 tools
    """

    if len(all_tools) < NUMBER_OF_TOOLS:

        print()
        print(
            f"ERROR: Only {len(all_tools)} valid tools were found."
        )
        print(
            f"At least {NUMBER_OF_TOOLS} tools are required."
        )

        return []

    selected_tools = all_tools[:NUMBER_OF_TOOLS]

    print()
    print("=" * 100)
    print(
        f"AUTOMATICALLY SELECTED FIRST {NUMBER_OF_TOOLS} TOOLS"
    )
    print("=" * 100)

    for number, tool in enumerate(selected_tools, start=1):

        print(
            f"{number:>2}. "
            f"{tool.get('tool', 'UNKNOWN')}"
        )

        print(
            f"    Source: "
            f"{tool.get('_source_file', 'UNKNOWN')}"
        )

    return selected_tools


# ======================================================================
# ONTOLOGY DISPLAY
# ======================================================================

def display_ontology():
    """
    Display the actual C1-C6 ontology imported from Module 3.
    """

    print()
    print("-" * 100)
    print("FIXED C1-C6 ONTOLOGY")
    print("-" * 100)

    #for capability_id, information in CAPABILITY_ONTOLOGY.items():
#
 #       print(
  #          f"{capability_id} — "
   #         f"{information['canonical']}"
    #    )

     #   print(
      #      f"    {information['definition']}"
       # )

        #print()

    #print(
       # "NONE — No C1-C6 capability applies."
    #)


# ======================================================================
# MANUAL ANNOTATION DISPLAY
# ======================================================================

def display_tool_for_annotation(tool, number, total):
    """
    Display only information available before the pipeline runs.

    Pipeline-derived information is deliberately hidden.

    NOT displayed:

        assumed_capability
        capability_features
        normalized
        mapping
    """

    print()
    print()
    print("=" * 110)

    print(
        f"TOOL {number} OF {total}"
    )

    print("=" * 110)

    print()
    print(
        f"Source file: {tool.get('_source_file', 'UNKNOWN')}"
    )

    print()
    print(
        f"Tool name: {tool.get('tool', 'UNKNOWN')}"
    )

    print()
    print("Description:")
    print("-" * 110)

    description = tool.get(
        "description",
        "NO DESCRIPTION PROVIDED"
    )

    print(description)

    print()
    print("Tool metadata:")

    print(
        f"readOnlyHint:    "
        f"{tool.get('readOnlyHint', 'Not provided')}"
    )

    print(
        f"destructiveHint: "
        f"{tool.get('destructiveHint', 'Not provided')}"
    )

    print(
        f"idempotentHint:  "
        f"{tool.get('idempotentHint', 'Not provided')}"
    )

    print(
        f"openWorldHint:   "
        f"{tool.get('openWorldHint', 'Not provided')}"
    )

    display_ontology()


# ======================================================================
# GOLD LABEL INPUT
# ======================================================================

def get_gold_label():
    """
    Ask the researcher to assign one or more independent gold labels.

    Examples:

        C1
        C2
        C2,C4
        C1,C3
        C1,C2,C3
        NONE
    """

    print()
    print("ENTER GOLD CAPABILITY LABEL")
    print("=" * 100)

    print()
    print("Use NONE if no C1-C6 capability applies.")

    print()
    print(
        "Enter one or more capabilities separated by commas."
    )


    while True:

        answer = input(
            "\nGold capability(s): "
        ).strip().upper()

        if not answer:
            print("Please enter C1-C6 or NONE.")
            continue

        if answer == "NONE":
            return []

        capabilities = [
            value.strip()
            for value in answer.split(",")
            if value.strip()
        ]

        # Remove duplicates.
        capabilities = list(
            dict.fromkeys(capabilities)
        )

        invalid = [
            capability
            for capability in capabilities
            if capability not in CAPABILITY_ONTOLOGY
        ]

        if invalid:

            print()
            print(
                f"Invalid capability(s): {invalid}"
            )

            print(
                "Valid options: "
                "C1, C2, C3, C4, C5, C6, NONE"
            )

            continue

        # Keep consistent C1 -> C6 order.
        capabilities.sort(
            key=lambda value: int(value[1:])
        )

        return capabilities


# ======================================================================
# MANUAL GOLD SET CREATION
# ======================================================================

def manually_label_tools(selected_tools):
    """
    Create the independent gold-standard reference set.

    IMPORTANT:

    No Module 2 or Module 3 processing has occurred yet.
    """

    print()
    print()
    print("=" * 110)
    print("MANUAL GOLD-SET ANNOTATION")
    print("=" * 110)

    print()
    print(
        "You are now creating the GOLD STANDARD."
    )

    print()
    print(
        "Judge each tool using the information displayed above."
    )

    print(
        "Do NOT use automated pipeline predictions."
    )

    print()
    print(
        "The gold set must be created independently "
        "before the pipeline is executed."
    )

    input(
        "\nPress ENTER to begin..."
    )

    gold_labels = []

    for number, tool in enumerate(
        selected_tools,
        start=1
    ):

        display_tool_for_annotation(
            tool,
            number,
            len(selected_tools)
        )

        gold_capabilities = get_gold_label()

        record = {
            "annotation_id": number,
            "tool": tool.get("tool", ""),
            "description": tool.get("description", ""),
            "source_file": tool.get("_source_file", ""),
            "source_index": tool.get("_source_index"),
            "gold_capabilities": gold_capabilities
        }

        gold_labels.append(record)

        print()
        print(
            "Gold label saved:",
            gold_capabilities if gold_capabilities else "NONE"
        )

        if number < len(selected_tools):
            input(
                "\nPress ENTER for the next tool..."
            )

    return gold_labels


# ======================================================================
# SAVE GOLD SET
# ======================================================================

def save_gold_set(gold_labels):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    data = {
        "experiment": (
            "Experiment 1 — Gold-set capability mapping accuracy"
        ),
        "ontology_source": (
            "modules.module_3_capability_normalization."
            "CAPABILITY_ONTOLOGY"
        ),
        "sampling_method": (
            "First 15 tools from researcher-selected JSON files"
        ),
        "tool_count": len(gold_labels),
        "gold_labels": gold_labels
    }

    with open(
        GOLD_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("Gold set saved:")
    print(f"  {GOLD_JSON}")


# ======================================================================
# PREPARE MODULE 2 INPUT
# ======================================================================

def prepare_module_input(selected_tools):
    """
    Convert selected tools into the structure expected by Module 2.

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
        "source_file": "Experiment_1_Gold_Set"
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
    Find the exact pipeline tool corresponding to the gold record.

    Matching uses:

        1. source position where possible
        2. tool name

    Since Module 2 receives exactly the selected tools in the same
    order, annotation_id is also preserved as a useful fallback.
    """

    tool_name = gold_record["tool"]
    source_index = gold_record.get("source_index")

    # First try exact name.
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
    Compare independent gold labels against Module 3 predictions.
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

        gold = gold_record[
            "gold_capabilities"
        ]

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
# ERROR ANALYSIS
# ======================================================================

def collect_error_analysis(comparison):
    """
    For every incorrect prediction, allow the researcher to record
    a brief explanation of why the pipeline differed from the gold
    label.

    This does NOT change the prediction or the gold label.
    """

    errors = [
        result
        for result in comparison
        if not result["exact_match"]
    ]

    if not errors:
        return

    print()
    print()
    print("=" * 110)
    print("ERROR ANALYSIS")
    print("=" * 110)

    print()
    print(
        "For each mismatch, record why the pipeline prediction "
        "differs from the gold label."
    )

    print(
        "This explanation is stored as qualitative error evidence."
    )

    for number, result in enumerate(
        errors,
        start=1
    ):

        gold = (
            ", ".join(result["gold_capabilities"])
            if result["gold_capabilities"]
            else "NONE"
        )

        predicted = (
            ", ".join(result["predicted_capabilities"])
            if result["predicted_capabilities"]
            else "NONE"
        )

        print()
        print("-" * 110)

        print(
            f"ERROR {number}/{len(errors)}"
        )

        print(
            f"Tool:       {result['tool']}"
        )

        print(
            f"GOLD:       {gold}"
        )

        print(
            f"PREDICTED:  {predicted}"
        )

        print()
        print(
            "Pipeline evidence:"
        )

        print(
            f"  Normalized concepts: "
            f"{result['normalized_concepts']}"
        )

        print(
            f"  Matched expressions: "
            f"{result['matched_expressions']}"
        )

        print(
            f"  Confidence: "
            f"{result['normalization_confidence']}"
        )

        print(
            f"  Mapping reason: "
            f"{result['mapping_reason']}"
        )

        print()

        explanation = input(
            "Why is this prediction different from the gold label? "
            "\n> "
        ).strip()

        result["error_analysis"] = explanation


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
            "capability": capability,
            "canonical":
                CAPABILITY_ONTOLOGY[
                    capability
                ]["canonical"],
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1
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
        "tool_count": total,
        "exact_set_correct": exact_correct,
        "exact_set_accuracy": exact_set_accuracy,
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": micro_f1
    }

    return metrics


# ======================================================================
# PRINT COMPARISON
# ======================================================================

def print_comparison(comparison):

    print()
    print()
    print("=" * 115)
    print("GOLD SET VS PIPELINE PREDICTION")
    print("=" * 115)

    for result in comparison:

        gold = (
            ", ".join(result["gold_capabilities"])
            if result["gold_capabilities"]
            else "NONE"
        )

        predicted = (
            ", ".join(result["predicted_capabilities"])
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

        if result["error_analysis"]:

            print()

            print(
                f"    Error analysis: "
                f"{result['error_analysis']}"
            )


# ======================================================================
# PRINT METRICS
# ======================================================================

def print_metrics(metrics):

    print()
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
# SAVE COMPARISON JSON
# ======================================================================

def save_comparison_json(comparison):

    data = {
        "experiment":
            "Experiment 1 — Gold-set capability mapping accuracy",

        "ontology_source":
            (
                "modules.module_3_capability_normalization."
                "CAPABILITY_ONTOLOGY"
            ),

        "tool_count":
            len(comparison),

        "results":
            comparison
    }

    with open(
        COMPARISON_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("Comparison JSON saved:")
    print(f"  {COMPARISON_JSON}")


# ======================================================================
# SAVE COMPARISON CSV
# ======================================================================

def save_comparison_csv(comparison):

    fieldnames = [
        "annotation_id",
        "tool",
        "source_file",
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
    print("Comparison CSV saved:")
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
    print("Metrics saved:")
    print(f"  {METRICS_JSON}")


# ======================================================================
# MAIN
# ======================================================================

def main():

    print()
    print("=" * 110)
    print(
        "EXPERIMENT 1 — GOLD-SET CAPABILITY MAPPING ACCURACY"
    )
    print("=" * 110)

    print()
    print(
        "Objective:"
    )

    print(
        "Evaluate whether the project's automated capability "
        "mapping correctly assigns C1-C6 capabilities to tools."
    )

    print()
    print(
        "Ontology source:"
    )

    print(
        "modules.module_3_capability_normalization."
        "CAPABILITY_ONTOLOGY"
    )

    print()
    print(
        "Sampling:"
    )

    print(
        f"First {NUMBER_OF_TOOLS} tools from the selected JSON files."
    )

    # ==================================================================
    # STEP 1 — FIND JSON FILES
    # ==================================================================

    json_files = find_json_files()

    if not json_files:

        print()
        print("No JSON files found.")
        return

    # ==================================================================
    # STEP 2 — SELECT JSON FILES
    # ==================================================================

    selected_files = select_json_files(
        json_files
    )

    # ==================================================================
    # STEP 3 — LOAD TOOLS
    # ==================================================================

    all_tools = load_tools_from_files(
        selected_files
    )

    if len(all_tools) < NUMBER_OF_TOOLS:

        print()
        print(
            f"ERROR: Need at least {NUMBER_OF_TOOLS} tools."
        )

        return

    # ==================================================================
    # STEP 4 — AUTOMATICALLY SELECT FIRST 15
    # ==================================================================

    selected_tools = select_first_15_tools(
        all_tools
    )

    if not selected_tools:
        return

    # ==================================================================
    # STEP 5 — MANUAL GOLD LABELING
    # ==================================================================

    gold_labels = manually_label_tools(
        selected_tools
    )

    # ==================================================================
    # STEP 6 — SAVE GOLD BEFORE RUNNING PIPELINE
    # ==================================================================

    save_gold_set(
        gold_labels
    )

    print()
    print("=" * 100)
    print("GOLD SET LOCKED")
    print("=" * 100)

    print()
    print(
        "The independent gold reference has now been saved."
    )

    print(
        "The automated pipeline will now be executed."
    )

    input(
        "\nPress ENTER to run Module 2 and Module 3..."
    )

    # ==================================================================
    # STEP 7 — RUN MODULE 2 + MODULE 3
    # ==================================================================

    pipeline_output = run_actual_pipeline(
        selected_tools
    )

    # ==================================================================
    # STEP 8 — COMPARE RESULTS
    # ==================================================================

    comparison = compare_results(
        gold_labels,
        pipeline_output
    )

    # ==================================================================
    # STEP 9 — DISPLAY COMPARISON
    # ==================================================================

    print_comparison(
        comparison
    )

    # ==================================================================
    # STEP 10 — COLLECT ERROR ANALYSIS
    # ==================================================================

    collect_error_analysis(
        comparison
    )

    # ==================================================================
    # STEP 11 — CALCULATE METRICS
    # ==================================================================

    metrics = calculate_metrics(
        comparison
    )

    # ==================================================================
    # STEP 12 — DISPLAY METRICS
    # ==================================================================

    print_metrics(
        metrics
    )

    # ==================================================================
    # STEP 13 — SAVE RESULTS
    # ==================================================================

    save_comparison_json(
        comparison
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
    print("EXPERIMENT 1 COMPLETE")
    print("=" * 110)

    print()
    print(
        f"Results directory:"
    )

    print(
        f"  {OUTPUT_DIR}"
    )

    print()
    print(
        "Files created:"
    )

    print(
        f"  1. {GOLD_JSON.name}"
    )

    print(
        f"  2. {COMPARISON_JSON.name}"
    )

    print(
        f"  3. {COMPARISON_CSV.name}"
    )

    print(
        f"  4. {METRICS_JSON.name}"
    )

    print()
    print(
        "Methodological property:"
    )

    print(
        "The gold labels were created and saved BEFORE "
        "Module 2 and Module 3 were executed."
    )

    print(
        "Therefore, the automated predictions could not "
        "influence the gold annotations."
    )

    print()
    print("=" * 110)


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()