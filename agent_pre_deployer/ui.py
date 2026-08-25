import os
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
    '<div class="subtitle">'
    "Pre-deployment security assessment for agent tool permissions"
    "</div>",
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
    st.caption("1. Tool Discovery")
    st.caption("2. Capability Extraction")
    st.caption("3. Capability Normalization")
    st.caption("4. Ontology Database")
    st.caption("5. Composition Analysis")
    st.caption("6. Attack Pattern Analysis")
    st.caption("7. Risk Assessment")
    st.caption("8. Report Generation")


# =========================================================
# NO FILE UPLOADED
# =========================================================

if uploaded_file is None:

    st.info(
        "Upload a JSON tool metadata file from the sidebar to begin."
    )

    st.markdown("### What this tool checks")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🔍 Capabilities")
        st.write(
            "Maps tools to the fixed C1–C6 capability ontology."
        )

    with col2:
        st.markdown("#### 🔗 Composition")
        st.write(
            "Checks whether the server contains literature-backed "
            "capability compositions."
        )

    with col3:
        st.markdown("#### ⚠️ Risk")
        st.write(
            "Assesses CIA impact, attack-pattern findings, and "
            "mitigation coverage."
        )

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

if st.button(
    "Run Security Analysis",
    type="primary",
    use_container_width=True,
):

    with tempfile.TemporaryDirectory() as temp_dir:

        input_path = os.path.join(
            temp_dir,
            uploaded_file.name,
        )

        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:

            with st.status(
                "Running AgentPreDeployer...",
                expanded=True,
            ) as status:

                # -------------------------------------------------
                # MODULE 1
                # -------------------------------------------------

                st.write("Module 1 — Server discovery")

                result_1 = module_1_server_selection.run(
                    input_path
                )

                # -------------------------------------------------
                # MODULE 2
                # -------------------------------------------------

                st.write("Module 2 — Capability extraction")

                result_2 = module_2_capability_extraction.run(
                    result_1
                )

                # -------------------------------------------------
                # MODULE 3
                # -------------------------------------------------

                st.write("Module 3 — Capability normalization")

                result_3 = module_3_capability_normalization.run(
                    result_2
                )

                # -------------------------------------------------
                # MODULE 5
                # -------------------------------------------------

                st.write("Module 5 — Ontology database")

                result_5 = module_5_ontology_database.run(
                    result_3
                )

                # -------------------------------------------------
                # MODULE 6
                # -------------------------------------------------

                st.write("Module 6 — Composition analysis")

                result_6 = module_6_composition_analysis.run(
                    result_5
                )

                # -------------------------------------------------
                # MODULE 7
                # -------------------------------------------------

                st.write("Module 7 — Attack pattern analysis")

                result_7 = module_7_attack_pattern_analysis.run(
                    result_6
                )

                # -------------------------------------------------
                # MODULE 8
                # -------------------------------------------------

                st.write("Module 8 — Risk assessment")

                result_8 = module_8_risk_assessment.run(
                    result_7
                )

                # -------------------------------------------------
                # MODULE 9
                # -------------------------------------------------

                st.write("Module 9 — Report generation")

                result_9 = module_9_report_generation.run(
                    result_8
                )

                status.update(
                    label="Analysis complete",
                    state="complete",
                )

            # -----------------------------------------------------
            # IMPORTANT:
            # Module 9 returns the final pipeline dictionary.
            # Store result_9, NOT result_8.
            # -----------------------------------------------------

            st.session_state.analysis_result = result_9

            # -----------------------------------------------------
            # Load the exact report generated by Module 9
            # -----------------------------------------------------

            generated_report_path = result_9.get(
                "final_report_path"
            )

            if generated_report_path:

                report_path = Path(
                    generated_report_path
                )

                if report_path.exists():

                    st.session_state.report_text = (
                        report_path.read_text(
                            encoding="utf-8"
                        )
                    )

                else:

                    st.session_state.report_text = None

            else:

                st.session_state.report_text = None

            st.success(
                "Security assessment completed successfully."
            )

        except Exception as e:

            st.error(
                f"Analysis failed: {e}"
            )

            st.exception(e)


# =========================================================
# RESULTS
# =========================================================

result = st.session_state.analysis_result

if result is None:
    st.stop()


# =========================================================
# EXTRACT MODULE OUTPUTS
# =========================================================

tools = result.get(
    "tools",
    [],
)

composition_analysis = result.get(
    "composition_analysis",
    {},
)

mitigation_assessment = result.get(
    "mitigation_assessment",
    {},
)

attack_pattern_analysis = result.get(
    "attack_pattern_analysis",
    {},
)


# =========================================================
# CAPABILITY PROFILE
#
# Same logic used by Module 9.
# Do NOT rely on ontology["capabilities"] here because the
# actual pipeline capability information is stored in the
# individual tool mappings.
# =========================================================

capability_tools = {}

for tool in tools:

    if not isinstance(tool, dict):
        continue

    tool_name = tool.get(
        "tool",
        "Unknown tool",
    )

    mapping = tool.get(
        "mapping",
        {},
    )

    mappings = mapping.get(
        "mappings",
        [],
    )

    if not isinstance(mappings, list):
        continue

    for mapping_entry in mappings:

        if not isinstance(mapping_entry, dict):
            continue

        capability_id = mapping_entry.get(
            "capability_id"
        )

        if capability_id:

            capability_tools.setdefault(
                capability_id,
                set(),
            ).add(tool_name)


# =========================================================
# MODULE 6 DETECTIONS
#
# Module 9 uses composition_analysis["detections"].
# These are literature-backed composition matches.
# They are NOT confirmed attacks.
# =========================================================

detections = composition_analysis.get(
    "detections",
    [],
)

if not isinstance(detections, list):
    detections = []


# =========================================================
# MODULE 8 MITIGATION ASSESSMENTS
# =========================================================

matched_mitigations = mitigation_assessment.get(
    "matched_composition_assessments",
    [],
)

if not isinstance(matched_mitigations, list):
    matched_mitigations = []


# =========================================================
# OPEN MITIGATION GAPS
# =========================================================

open_gaps = mitigation_assessment.get(
    "open_mitigation_gaps",
    [],
)

if not isinstance(open_gaps, list):
    open_gaps = []


# =========================================================
# OVERVIEW
# =========================================================

st.header("Assessment Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Tools Analysed",
        len(tools),
    )

with col2:

    st.metric(
        "Capabilities",
        len(capability_tools),
    )

with col3:

    st.metric(
        "Matched Compositions",
        len(detections),
    )

with col4:

    st.metric(
        "Open Mitigation Gaps",
        len(open_gaps),
    )


# =========================================================
# CAPABILITY PROFILE
# =========================================================

st.header("Capability Profile")

if capability_tools:

    for capability_id, tool_set in sorted(
        capability_tools.items()
    ):

        tool_count = len(tool_set)

        st.markdown(
            f"""
            <span class="capability">
                {capability_id} — {tool_count} tool(s)
            </span>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(
            f"{capability_id} — Tools contributing this capability"
        ):

            for tool_name in sorted(tool_set):
                st.write(f"• {tool_name}")

else:

    st.info(
        "No capability information available."
    )


# =========================================================
# LITERATURE-BACKED COMPOSITIONS
# =========================================================

st.header(
    "Matched Literature-Backed Capability Compositions"
)

st.caption(
    "These are Level-1 composition matches. "
    "A match indicates that the required capabilities are "
    "present in the server; it does not establish that an "
    "attack was executed or observed."
)


if not detections:

    st.success(
        "No literature-backed capability composition matched."
    )

else:

    for detection in detections:

        if not isinstance(detection, dict):
            st.write(detection)
            continue

        pattern_id = detection.get(
            "pattern_id",
            "Unknown",
        )

        pattern_name = detection.get(
            "pattern_name",
            "Unknown pattern",
        )

        severity = detection.get(
            "severity",
            "Unknown",
        )

        finding_type = detection.get(
            "finding_type",
            "Unknown",
        )

        confidence = detection.get(
            "confidence",
            "Unknown",
        )

        sequence = detection.get(
            "capability_sequence",
            [],
        )

        if isinstance(sequence, list):

            sequence_text = " → ".join(
                str(x)
                for x in sequence
            )

        else:

            sequence_text = str(sequence)

        severity_lower = str(severity).lower()

        if severity_lower == "high":
            severity_class = "severity-high"
        elif severity_lower == "medium":
            severity_class = "severity-medium"
        else:
            severity_class = "severity-low"

        st.markdown(
            f"""<div class="composition-card">
        <div class="composition-header">
        <div>
        <div class="pattern-id">{pattern_id}</div>
        <div class="pattern-name">{pattern_name}</div>
        </div>
        <span class="status-badge {severity_class}">{severity}</span>
        </div>
        <div class="sequence-label">Literature-defined sequence</div>
        <div class="sequence">{sequence_text}</div>
        </div>""",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)

        with col_a:

            st.markdown(
                "**Literature-defined sequence**"
            )

            st.code(
                sequence_text,
                language="text",
            )

        with col_b:

            st.markdown(
                "**Finding classification**"
            )

            st.write(
                finding_type
            )

            st.markdown(
                "**Mapping confidence**"
            )

            st.write(
                f"{confidence} "
                "(literature-mapping confidence)"
            )

        # -----------------------------------------------------
        # CIA IMPACT
        # -----------------------------------------------------

        impact = detection.get(
            "impact_assessment"
        )

        if impact:

            st.markdown("#### CIA Impact")

            cia1, cia2, cia3, cia4 = st.columns(4)

            with cia1:
                st.metric(
                    "Confidentiality",
                    impact.get(
                        "confidentiality",
                        "-",
                    ),
                )

            with cia2:
                st.metric(
                    "Integrity",
                    impact.get(
                        "integrity",
                        "-",
                    ),
                )

            with cia3:
                st.metric(
                    "Availability",
                    impact.get(
                        "availability",
                        "-",
                    ),
                )

            with cia4:
                st.metric(
                    "CIA Total",
                    impact.get(
                        "total",
                        "-",
                    ),
                )

            if impact.get("rationale"):

                st.markdown(
                    "**CIA rationale:**"
                )

                st.write(
                    impact.get(
                        "rationale"
                    )
                )

            if impact.get("evidence_type"):

                st.caption(
                    "Evidence type: "
                    + str(
                        impact.get(
                            "evidence_type"
                        )
                    )
                )

        st.divider()


# =========================================================
# EXCLUDED PATTERNS
# =========================================================

excluded_patterns = composition_analysis.get(
    "excluded_patterns",
    [],
)

if excluded_patterns:

    st.header("Excluded Patterns")

    st.info(
        "The following literature patterns were excluded "
        "from composition matching because they were not "
        "eligible under the project's matching rules. "
        "They are retained as evidence only."
    )

    for pattern_id in excluded_patterns:

        st.write(
            f"• {pattern_id}"
        )


# =========================================================
# MITIGATION COVERAGE
# =========================================================

st.header(
    "Mitigation Coverage for Matched Compositions"
)


if not matched_mitigations:

    if detections:

        st.warning(
            "Matched compositions were found, but no "
            "composition-specific mitigation assessments "
            "are available."
        )

    else:

        st.info(
            "No matched compositions require mitigation coverage."
        )

else:

    for assessment in matched_mitigations:

        if not isinstance(assessment, dict):
            continue

        pattern_id = assessment.get(
            "pattern_id",
            "Unknown",
        )

        pattern_name = assessment.get(
            "pattern_name",
            "Unknown pattern",
        )

        coverage_status = assessment.get(
            "coverage_status",
            "Unknown",
        )

        st.markdown(
            f"### {pattern_id} — {pattern_name}"
        )

        st.markdown(
            f"**Coverage status:** `{coverage_status}`"
        )

        if assessment.get("note"):

            st.info(
                assessment.get("note")
            )

        # -----------------------------------------------------
        # Literature mitigations
        # -----------------------------------------------------

        literature_mitigations = assessment.get(
            "literature_mitigations",
            [],
        )

        if literature_mitigations:

            st.markdown(
                "#### Literature-backed mitigations"
            )

            for mitigation in literature_mitigations:

                mitigation_id = mitigation.get(
                    "mitigation_id",
                    "Unknown",
                )

                mitigation_name = mitigation.get(
                    "mitigation_name",
                    "Unknown mitigation",
                )

                evidence_type = mitigation.get(
                    "evidence_type",
                    "Unknown",
                )

                applicability = mitigation.get(
                    "applicability",
                    "Unknown",
                )

                with st.expander(
                    f"{mitigation_id} — {mitigation_name}"
                ):

                    st.write(
                        "**Evidence type:** "
                        + str(evidence_type)
                    )

                    st.write(
                        "**Applicability:** "
                        + str(applicability)
                    )

                    if mitigation.get(
                        "supporting_papers"
                    ):

                        st.write(
                            "**Supporting papers:** "
                            + str(
                                mitigation.get(
                                    "supporting_papers"
                                )
                            )
                        )

                    if mitigation.get("timing"):

                        st.write(
                            "**Timing:** "
                            + str(
                                mitigation.get(
                                    "timing"
                                )
                            )
                        )

                    if mitigation.get(
                        "effectiveness_evidence"
                    ):

                        st.write(
                            "**Effectiveness evidence:** "
                            + str(
                                mitigation.get(
                                    "effectiveness_evidence"
                                )
                            )
                        )

                    if mitigation.get(
                        "limitations"
                    ):

                        st.write(
                            "**Limitations:** "
                            + str(
                                mitigation.get(
                                    "limitations"
                                )
                            )
                        )

        else:

            st.write(
                "Literature mitigations: none"
            )

        # -----------------------------------------------------
        # Project-derived mitigations
        # -----------------------------------------------------

        project_mitigations = assessment.get(
            "project_mitigations",
            [],
        )

        if project_mitigations:

            st.markdown(
                "#### Project-derived mitigations"
            )

            for mitigation in project_mitigations:

                mitigation_id = mitigation.get(
                    "mitigation_id",
                    "Unknown",
                )

                mitigation_name = mitigation.get(
                    "mitigation_name",
                    "Unknown mitigation",
                )

                control_type = mitigation.get(
                    "control_type",
                    "Unknown",
                )

                timing = mitigation.get(
                    "timing",
                    "Unknown",
                )

                with st.expander(
                    f"{mitigation_id} — {mitigation_name}"
                ):

                    st.write(
                        f"**Control type:** {control_type}"
                    )

                    st.write(
                        f"**Timing:** {timing}"
                    )

                    st.write(
                        "**Evidence status:** "
                        + str(
                            mitigation.get(
                                "evidence_status",
                                "Unknown",
                            )
                        )
                    )

                    st.write(
                        "**Rationale:** "
                        + str(
                            mitigation.get(
                                "project_rationale",
                                "",
                            )
                        )
                    )

        else:

            st.write(
                "Project-derived mitigations: none"
            )

        if assessment.get("warning"):

            st.warning(
                assessment.get("warning")
            )

        st.divider()


# =========================================================
# OPEN MITIGATION GAPS
# =========================================================

st.header("Open Mitigation Gaps")

if not open_gaps:

    st.success(
        "No open mitigation gaps among matched compositions."
    )

else:

    for gap in open_gaps:

        if not isinstance(gap, dict):
            continue

        pattern_id = gap.get(
            "pattern_id",
            "Unknown",
        )

        gap_text = gap.get(
            "gap",
            "No gap description provided.",
        )

        proposals = gap.get(
            "project_proposals",
            [],
        )

        st.markdown(
            f"""
            <div class="finding risk-high">
                <strong>{pattern_id}</strong><br>
                {gap_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if proposals:

            st.markdown(
                "**Project proposal(s):**"
            )

            for proposal in proposals:

                st.write(
                    f"• {proposal}"
                )

        else:

            st.write(
                "**Project proposal(s):** none"
            )

        if gap.get("warning"):

            st.warning(
                gap.get("warning")
            )


# =========================================================
# PATTERN COVERAGE REFERENCE
# =========================================================

pattern_coverage = mitigation_assessment.get(
    "pattern_coverage_reference",
    [],
)

if pattern_coverage:

    st.header(
        "Pattern Coverage Reference (P1–P9)"
    )

    for coverage in pattern_coverage:

        if not isinstance(coverage, dict):
            continue

        pattern_id = coverage.get(
            "pattern_id",
            "Unknown",
        )

        coverage_status = coverage.get(
            "coverage_status",
            "Unknown",
        )

        literature_ids = [
            m.get("mitigation_id", "Unknown")
            for m in coverage.get(
                "literature_mitigations",
                [],
            )
            if isinstance(m, dict)
        ]

        project_ids = [
            m.get("mitigation_id", "Unknown")
            for m in coverage.get(
                "project_mitigations",
                [],
            )
            if isinstance(m, dict)
        ]

        literature_text = (
            ", ".join(literature_ids)
            if literature_ids
            else "-"
        )

        project_text = (
            ", ".join(project_ids)
            if project_ids
            else "-"
        )

        st.markdown(
            f"**{pattern_id}:** `{coverage_status}`"
        )

        st.caption(
            f"Literature: {literature_text} | "
            f"Project: {project_text}"
        )

        if coverage.get("note"):

            st.write(
                coverage.get("note")
            )


# =========================================================
# INTERPRETATION LIMITS
# =========================================================

st.header(
    "Interpretation Limits and Disclaimers"
)

limitation = composition_analysis.get(
    "limitation"
)

interpretation = composition_analysis.get(
    "interpretation",
    {},
)

impact_interpretation = interpretation.get(
    "impact_assessment"
)

mitigation_semantics = mitigation_assessment.get(
    "semantics"
)

applicability_rule = mitigation_assessment.get(
    "applicability_rule"
)

if limitation:
    st.warning(limitation)

if impact_interpretation:
    st.info(impact_interpretation)

if mitigation_semantics:
    st.info(mitigation_semantics)

if applicability_rule:
    st.info(applicability_rule)

st.caption(
    "CIA totals are CIA impact totals only. "
    "They are not converted into a risk score at this stage."
)


# =========================================================
# FINAL REPORT
# =========================================================

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

    with st.expander(
        "View full report",
        expanded=False,
    ):

        st.text(
            report_text
        )

else:

    st.warning(
        "The analysis completed, but Module 9's generated "
        "report could not be loaded into the UI."
    )

    final_report_path = result.get(
        "final_report_path"
    )

    if final_report_path:

        st.caption(
            "Expected report path:"
        )

        st.code(
            str(final_report_path)
        )