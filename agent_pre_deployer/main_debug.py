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

from config import INPUT_FILE, OUTPUT_FILE

import json


# ================================================================
# DEBUG DISPLAY
# ================================================================

def print_result(module_name, result):

    print("\n")
    print("=" * 80)
    print(f"RESULT FROM {module_name}")
    print("=" * 80)

    if result is None:
        print("None")
        return

    # Dictionaries / lists
    if isinstance(result, (dict, list, tuple)):

        try:
            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                    default=str
                )
            )

        except Exception:
            print(result)

    else:
        print(result)

    print("=" * 80)


# ================================================================
# MAIN PIPELINE
# ================================================================

def main():

    print("=" * 60)
    print("        AgentPreDeployer - Tool Metadata Extractor")
    print("=" * 60)

    try:

        # ========================================================
        # MODULE 1
        # ========================================================

        result_1 = module_1_server_selection.run(INPUT_FILE)

        # ========================================================
        # MODULE 2
        # ========================================================

        result_2 = module_2_capability_extraction.run(result_1)

        # ========================================================
        # MODULE 3
        # ========================================================

        result_3 = module_3_capability_normalization.run(result_2)

        # ========================================================
        # MODULE 4
        # ========================================================

        # IMPORTANT:
        # Your original code has Module 4 commented out.
        #
        # result_4 = module_4_capability_mapping.run(result_3)

        # Since Module 5 currently expects result_3,
        # we preserve your existing pipeline.

        # ========================================================
        # MODULE 5
        # ========================================================

        result_5 = module_5_ontology_database.run(result_3)

        # ========================================================
        # MODULE 6
        # ========================================================

        result_6 = module_6_composition_analysis.run(result_5)

        # ========================================================
        # MODULE 7
        # ========================================================

        result_7 = module_7_attack_pattern_analysis.run(result_6)

        # ========================================================
        # MODULE 8
        # ========================================================

        result_8 = module_8_risk_assessment.run(result_7)

        # ========================================================
        # MODULE 9
        # ========================================================

        result_9 = module_9_report_generation.run(result_8)

        # ========================================================
        # FINAL MESSAGE
        # ========================================================

        print("\n" + "=" * 60)
        print(f"Report saved to: {OUTPUT_FILE}")
        print("=" * 60)

        # ========================================================
        # PRINT EVERY MODULE RESULT
        # ========================================================

        print("\n\n")
        print("#" * 80)
        print("#                    PIPELINE RESULTS")
        print("#" * 80)

        print_result(
            "MODULE 1 - SERVER SELECTION",
            result_1
        )

        print_result(
            "MODULE 2 - CAPABILITY EXTRACTION",
            result_2
        )

        print_result(
            "MODULE 3 - CAPABILITY NORMALIZATION",
            result_3
        )

        print_result(
            "MODULE 5 - ONTOLOGY DATABASE",
            result_5
        )

        print_result(
            "MODULE 6 - COMPOSITION ANALYSIS",
            result_6
        )

        print_result(
            "MODULE 7 - ATTACK PATTERN ANALYSIS",
            result_7
        )

        print_result(
            "MODULE 8 - RISK ASSESSMENT",
            result_8
        )

        print_result(
            "MODULE 9 - REPORT GENERATION",
            result_9
        )

        print("\n")
        print("#" * 80)
        print("#                 END OF PIPELINE RESULTS")
        print("#" * 80)

    except Exception as error:

        print("\nERROR:")
        print(error)

        raise



# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":
    main()