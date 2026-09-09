import streamlit as st

from modules import (
    module_5_ontology_database,
    module_10,
)


def render():
    st.header("Threat Curation Chain")

    st.caption(
        "Review and curate threat-chain candidates before they are "
        "added to the attack-pattern knowledge base."
    )

    module_10.render(
        module_5_ontology_database.DB_PATH
    )