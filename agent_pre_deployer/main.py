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

def main():
    print("=" * 60)
    print("        AgentPreDeployer - Tool Metadata Extractor")
    print("=" * 60)

    try:
        # Module 1: Server Selection / Discovery
        result_1 = module_1_server_selection.run(INPUT_FILE)

        # Module 2: Capability Extraction
        result_2 = module_2_capability_extraction.run(result_1)

        # Module 3: Capability Normalization and mapping
        result_3 = module_3_capability_normalization.run(result_2)

        # Module 4: Capability Mapping result_4 = module_4_capability_mapping.run(result_3)

        # Module 5: Ontology Database
        result_5 = module_5_ontology_database.run(result_3)

        # Module 6: Composition Analysis
        result_6 = module_6_composition_analysis.run(result_5)

        # Module 7: Attack Pattern Analysis
        result_7 = module_7_attack_pattern_analysis.run(result_6)

        # Module 8: Risk Assessment
        result_8 = module_8_risk_assessment.run(result_7)

        # Module 9: Report Generation
        result_9 = module_9_report_generation.run(result_8)

        print("\n" + "=" * 60)
        print(f"Report saved to: {OUTPUT_FILE}")
        print("=" * 60)

    except Exception as error:
        print(f"\nERROR: {error}")
        raise

if __name__ == "__main__":
    main()
