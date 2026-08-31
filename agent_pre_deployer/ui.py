import streamlit as st

from ui.header import render_header
from ui.sidebar import render_sidebar
from ui.overview import render_overview
from ui.tools_capabilities import render_tools_capabilities
from ui.composition_analysis import render_composition_analysis
from ui.risk_mitigations import render_risk_mitigations
from ui.interpretation_limits import render_interpretation_limits
from ui.final_report import render_final_report

st.set_page_config(
    page_title="AgentPreDeployer",
    layout="wide",
)

render_header()

uploaded_file = render_sidebar()

# Run pipeline here...

if analysis_result is not None:
    render_overview(analysis_result)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Tools & Capabilities",
        "Composition Analysis",
        "CIA Risk & Mitigations",
        "Interpretation Limits",
        "Final Report",
    ])

    with tab1:
        render_tools_capabilities(analysis_result)

    with tab2:
        render_composition_analysis(analysis_result)

    with tab3:
        render_risk_mitigations(analysis_result)

    with tab4:
        render_interpretation_limits(analysis_result)

    with tab5:
        render_final_report(analysis_result)