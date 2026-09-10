import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# DATABASE
# ============================================================

# Database location:
# agent_pre_deployer/modules/capability_ontology.db
#
# Path(__file__).parent makes this independent of the directory
# from which Streamlit is launched.

DB_PATH = Path(__file__).parent.parent / "modules" / "capability_ontology.db"
TABLE_NAME = "attack_patterns"

CIA_COLUMNS = [
    "confidentiality_impact",
    "integrity_impact",
    "availability_impact",
]


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_connection():
    """Open the AgentPreDeployer ontology database."""

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    return sqlite3.connect(str(DB_PATH))


def load_patterns():
    """Load all attack patterns from the ontology database."""

    with get_connection() as conn:
        return pd.read_sql_query(
            f"SELECT * FROM {TABLE_NAME}",
            conn,
        )


def save_patterns(table):
    """
    Save only the editable CIA impact fields.

    cia_total is recalculated from:
        confidentiality + integrity + availability

    All other attack-pattern fields remain unchanged.
    """

    required_columns = [
        "pattern_id",
        *CIA_COLUMNS,
    ]

    missing = [
        column
        for column in required_columns
        if column not in table.columns
    ]

    if missing:
        raise ValueError(
            "Required database columns are missing: "
            + ", ".join(missing)
        )

    with get_connection() as conn:

        for _, row in table.iterrows():

            # Safely convert CIA values to integers.
            confidentiality = pd.to_numeric(
                row["confidentiality_impact"],
                errors="coerce",
            )

            integrity = pd.to_numeric(
                row["integrity_impact"],
                errors="coerce",
            )

            availability = pd.to_numeric(
                row["availability_impact"],
                errors="coerce",
            )

            # Treat empty values as zero.
            confidentiality = (
                0 if pd.isna(confidentiality)
                else int(confidentiality)
            )

            integrity = (
                0 if pd.isna(integrity)
                else int(integrity)
            )

            availability = (
                0 if pd.isna(availability)
                else int(availability)
            )

            # Enforce the allowed CIA range.
            confidentiality = max(
                0,
                min(5, confidentiality),
            )

            integrity = max(
                0,
                min(5, integrity),
            )

            availability = max(
                0,
                min(5, availability),
            )

            # cia_total is derived, never manually trusted.
            cia_total = (
                confidentiality
                + integrity
                + availability
            )

            conn.execute(
                f"""
                UPDATE {TABLE_NAME}
                SET
                    confidentiality_impact = ?,
                    integrity_impact = ?,
                    availability_impact = ?,
                    cia_total = ?
                WHERE pattern_id = ?
                """,
                (
                    confidentiality,
                    integrity,
                    availability,
                    cia_total,
                    row["pattern_id"],
                ),
            )

        conn.commit()


# ============================================================
# COLUMN CONFIGURATION
# ============================================================

def get_column_config():
    """
    Configure the attack-pattern editor.

    Only the three CIA impact fields are editable.
    All other fields are view-only.
    """

    return {

        # ----------------------------------------------------
        # IDENTIFICATION
        # ----------------------------------------------------

        "pattern_id": st.column_config.TextColumn(
            "Pattern ID",
            disabled=True,
        ),

        "pattern_name": st.column_config.TextColumn(
            "Pattern Name",
            disabled=True,
        ),

        "capability_sequence": st.column_config.TextColumn(
            "Capability Sequence",
            disabled=True,
        ),

        "attack_goal": st.column_config.TextColumn(
            "Attack Goal",
            disabled=True,
        ),

        "supporting_papers": st.column_config.TextColumn(
            "Supporting Papers",
            disabled=True,
        ),

        # ----------------------------------------------------
        # EVIDENCE / CLASSIFICATION
        # ----------------------------------------------------

        "evidence_type": st.column_config.TextColumn(
            "Evidence Type",
            disabled=True,
        ),

        "confidence": st.column_config.TextColumn(
            "Confidence",
            disabled=True,
        ),

        "evidence_summary": st.column_config.TextColumn(
            "Evidence Summary",
            disabled=True,
        ),

        "module_6_eligibility": st.column_config.TextColumn(
            "Module 6 Eligibility",
            disabled=True,
        ),

        "severity": st.column_config.TextColumn(
            "Severity",
            disabled=True,
        ),

        # ----------------------------------------------------
        # EDITABLE CIA IMPACTS
        # ----------------------------------------------------

        "confidentiality_impact": st.column_config.NumberColumn(
            "Confidentiality",
            min_value=0,
            max_value=5,
            step=1,
            help="Confidentiality impact score from 0 to 5.",
        ),

        "integrity_impact": st.column_config.NumberColumn(
            "Integrity",
            min_value=0,
            max_value=5,
            step=1,
            help="Integrity impact score from 0 to 5.",
        ),

        "availability_impact": st.column_config.NumberColumn(
            "Availability",
            min_value=0,
            max_value=5,
            step=1,
            help="Availability impact score from 0 to 5.",
        ),

        # ----------------------------------------------------
        # DERIVED CIA SCORE
        # ----------------------------------------------------

        "cia_total": st.column_config.NumberColumn(
            "CIA Total",
            disabled=True,
            help=(
                "Automatically calculated as "
                "Confidentiality + Integrity + Availability."
            ),
        ),

        # ----------------------------------------------------
        # CIA EVIDENCE
        # ----------------------------------------------------

        "cia_evidence_type": st.column_config.TextColumn(
            "CIA Evidence Type",
            disabled=True,
        ),

        "cia_rationale": st.column_config.TextColumn(
            "CIA Rationale",
            disabled=True,
        ),
    }


# ============================================================
# UI
# ============================================================

def render():

    st.header("Edit Database")

    st.caption(
        "View literature-backed attack patterns and update "
        "their CIA impact scores."
    )

    # --------------------------------------------------------
    # LOAD DATABASE
    # --------------------------------------------------------

    try:
        table = load_patterns()

    except Exception as error:

        st.error(
            f"Could not load the {TABLE_NAME} table."
        )

        st.code(str(error))

        st.info(
            f"Database expected at:\n{DB_PATH}"
        )

        return

    # --------------------------------------------------------
    # EMPTY DATABASE
    # --------------------------------------------------------

    if table.empty:

        st.info(
            "No attack patterns found in the database."
        )

        return

    # --------------------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # --------------------------------------------------------

    required_columns = [
        "pattern_id",
        *CIA_COLUMNS,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in table.columns
    ]

    if missing_columns:

        st.error(
            "The attack_patterns table is missing required "
            f"columns: {', '.join(missing_columns)}"
        )

        return

    # --------------------------------------------------------
    # NORMALISE CIA VALUES
    # --------------------------------------------------------

    for column in CIA_COLUMNS:

        table[column] = (
            pd.to_numeric(
                table[column],
                errors="coerce",
            )
            .fillna(0)
            .astype(int)
            .clip(0, 5)
        )

    # Always derive CIA total from the three components.
    table["cia_total"] = (
        table["confidentiality_impact"]
        + table["integrity_impact"]
        + table["availability_impact"]
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.subheader(
        f"Attack Patterns ({len(table)})"
    )

    st.caption(
        "Only Confidentiality, Integrity, and Availability "
        "are editable. CIA Total is derived automatically."
    )

    # --------------------------------------------------------
    # DATA EDITOR
    # --------------------------------------------------------

    edited_table = st.data_editor(
        table,
        column_config=get_column_config(),
        hide_index=True,
        use_container_width=True,
        key="patterns_table_editor",
    )

    # --------------------------------------------------------
    # RECALCULATE CIA TOTAL FROM CURRENT EDITS
    # --------------------------------------------------------

    edited_table = edited_table.copy()

    edited_table["cia_total"] = (
        pd.to_numeric(
            edited_table["confidentiality_impact"],
            errors="coerce",
        )
        .fillna(0)
        +
        pd.to_numeric(
            edited_table["integrity_impact"],
            errors="coerce",
        )
        .fillna(0)
        +
        pd.to_numeric(
            edited_table["availability_impact"],
            errors="coerce",
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # SAVE BUTTON
    # --------------------------------------------------------

    st.divider()

    left_column, right_column = st.columns([1, 5])

    with left_column:

        save_clicked = st.button(
            "💾 Save Changes",
            type="primary",
            use_container_width=True,
        )

    if save_clicked:

        try:

            save_patterns(edited_table)

            st.success(
                "Saved successfully. CIA scores have been updated."
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Could not save changes: {error}"
            )
