import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# DATABASE
# ============================================================

# Database location:
# agent_pre_deployer/modules/capability_ontology.db

DB_PATH = Path(__file__).parent.parent / "modules" / "capability_ontology.db"

TABLE_NAME = "attack_patterns"

CIA_COLUMNS = [
    "confidentiality_impact",
    "integrity_impact",
    "availability_impact",
]

# These columns are controlled by the application rather than
# directly edited by the user.
IDENTITY_COLUMN = "pattern_id"
DERIVED_COLUMN = "cia_total"


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


def get_database_columns():
    """Return the actual columns in the attack_patterns table."""

    with get_connection() as conn:

        rows = conn.execute(
            f"PRAGMA table_info({TABLE_NAME})"
        ).fetchall()

    return [row[1] for row in rows]


def normalise_cia_value(value):
    """
    Convert a CIA impact value to an integer between 0 and 5.
    """

    value = pd.to_numeric(
        value,
        errors="coerce",
    )

    if pd.isna(value):
        return 0

    return max(
        0,
        min(5, int(value)),
    )


def calculate_cia_total(row):
    """Calculate CIA total from the three CIA components."""

    return (
        normalise_cia_value(row["confidentiality_impact"])
        +
        normalise_cia_value(row["integrity_impact"])
        +
        normalise_cia_value(row["availability_impact"])
    )


def save_patterns(table, deleted_pattern_ids):
    """
    Save all editable database fields and delete selected rows.

    pattern_id:
        Used as the stable row identifier and is not edited.

    cia_total:
        Derived automatically from the three CIA components.

    deleted_pattern_ids:
        Rows selected using the Delete checkbox.
    """

    database_columns = get_database_columns()

    if IDENTITY_COLUMN not in database_columns:
        raise ValueError(
            f"Required identity column '{IDENTITY_COLUMN}' "
            "does not exist in the database."
        )

    # --------------------------------------------------------
    # Determine which columns may actually be updated.
    # --------------------------------------------------------

    editable_columns = [
        column
        for column in database_columns
        if column not in {
            IDENTITY_COLUMN,
            DERIVED_COLUMN,
        }
    ]

    # --------------------------------------------------------
    # Validate the incoming dataframe.
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in database_columns
        if column not in table.columns
    ]

    if missing_columns:
        raise ValueError(
            "The editor is missing database columns: "
            + ", ".join(missing_columns)
        )

    with get_connection() as conn:

        # ====================================================
        # DELETE SELECTED ROWS
        # ====================================================

        for pattern_id in deleted_pattern_ids:

            conn.execute(
                f"""
                DELETE FROM {TABLE_NAME}
                WHERE {IDENTITY_COLUMN} = ?
                """,
                (pattern_id,),
            )

        # ====================================================
        # UPDATE REMAINING ROWS
        # ====================================================

        for _, row in table.iterrows():

            pattern_id = row[IDENTITY_COLUMN]

            # Skip rows that were selected for deletion.
            if pattern_id in deleted_pattern_ids:
                continue

            values = []

            for column in editable_columns:

                value = row[column]

                # ------------------------------------------------
                # CIA fields
                # ------------------------------------------------

                if column in CIA_COLUMNS:

                    value = normalise_cia_value(value)

                # ------------------------------------------------
                # Pandas NaN -> SQLite NULL
                # ------------------------------------------------

                elif pd.isna(value):

                    value = None

                # ------------------------------------------------
                # Pandas/numpy scalar -> normal Python scalar
                # ------------------------------------------------

                elif hasattr(value, "item"):

                    try:
                        value = value.item()
                    except Exception:
                        pass

                values.append(value)

            # ----------------------------------------------------
            # Recalculate CIA total.
            # ----------------------------------------------------

            cia_total = calculate_cia_total(row)

            # ----------------------------------------------------
            # Build UPDATE statement dynamically.
            #
            # Column names come directly from PRAGMA table_info,
            # not user input, so they are trusted database names.
            # Values remain parameterised.
            # ----------------------------------------------------

            set_clause = ", ".join(
                f"{column} = ?"
                for column in editable_columns
            )

            update_values = values + [
                cia_total,
                pattern_id,
            ]

            # cia_total is updated separately because it is derived.
            update_sql = f"""
                UPDATE {TABLE_NAME}
                SET
                    {set_clause},
                    {DERIVED_COLUMN} = ?
                WHERE {IDENTITY_COLUMN} = ?
            """

            conn.execute(
                update_sql,
                update_values,
            )

        # ====================================================
        # COMMIT EVERYTHING AT ONCE
        # ====================================================

        conn.commit()


# ============================================================
# COLUMN CONFIGURATION
# ============================================================

def get_column_config(database_columns):
    """
    Make all database columns editable except:

        pattern_id -> stable row identifier
        cia_total  -> automatically calculated

    A temporary Delete column is added separately.
    """

    config = {}

    for column in database_columns:

        # ----------------------------------------------------
        # Pattern ID
        # ----------------------------------------------------

        if column == IDENTITY_COLUMN:

            config[column] = st.column_config.TextColumn(
                "Pattern ID",
                disabled=True,
                help=(
                    "Stable database identifier. "
                    "It cannot be edited because it is used "
                    "to identify the database row."
                ),
            )

        # ----------------------------------------------------
        # CIA fields
        # ----------------------------------------------------

        elif column in CIA_COLUMNS:

            pretty_name = {
                "confidentiality_impact": "Confidentiality",
                "integrity_impact": "Integrity",
                "availability_impact": "Availability",
            }[column]

            config[column] = st.column_config.NumberColumn(
                pretty_name,
                min_value=0,
                max_value=5,
                step=1,
            )

        # ----------------------------------------------------
        # CIA Total
        # ----------------------------------------------------

        elif column == DERIVED_COLUMN:

            config[column] = st.column_config.NumberColumn(
                "CIA Total",
                disabled=True,
                help=(
                    "Automatically calculated as "
                    "Confidentiality + Integrity + Availability."
                ),
            )

        # ----------------------------------------------------
        # All other columns
        # ----------------------------------------------------

        else:

            config[column] = st.column_config.TextColumn(
                column.replace("_", " ").title(),
            )

    # --------------------------------------------------------
    # Temporary UI-only Delete column
    # --------------------------------------------------------

    config["_delete"] = st.column_config.CheckboxColumn(
        "Delete",
        default=False,
        help=(
            "Tick this row if you want to delete it "
            "when Save Changes is clicked."
        ),
    )

    return config


# ============================================================
# UI
# ============================================================

def render():

    st.header("Edit Database")

    st.caption(
        "Edit attack-pattern records directly. "
        "Changes are written to the SQLite database when "
        "you click Save Changes."
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
    # GET DATABASE COLUMNS
    # --------------------------------------------------------

    database_columns = list(table.columns)

    # --------------------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # --------------------------------------------------------

    required_columns = [
        IDENTITY_COLUMN,
        *CIA_COLUMNS,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in database_columns
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

    # --------------------------------------------------------
    # ALWAYS RECALCULATE CIA TOTAL
    # --------------------------------------------------------

    table[DERIVED_COLUMN] = (
        table["confidentiality_impact"]
        +
        table["integrity_impact"]
        +
        table["availability_impact"]
    )

    # --------------------------------------------------------
    # ADD TEMPORARY DELETE COLUMN
    # --------------------------------------------------------

    table["_delete"] = False

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.subheader(
        f"Attack Patterns ({len(table)})"
    )

    st.caption(
        "All database fields are editable except Pattern ID "
        "and CIA Total. Tick Delete for rows you want removed, "
        "then click Save Changes."
    )

    # --------------------------------------------------------
    # DATA EDITOR
    # --------------------------------------------------------

    edited_table = st.data_editor(
        table,
        column_config=get_column_config(database_columns),
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key="patterns_table_editor",
    )

    # --------------------------------------------------------
    # MAKE COPY
    # --------------------------------------------------------

    edited_table = edited_table.copy()

    # --------------------------------------------------------
    # DETERMINE DELETIONS
    # --------------------------------------------------------

    deleted_pattern_ids = set()

    if "_delete" in edited_table.columns:

        delete_mask = (
            edited_table["_delete"]
            .fillna(False)
            .astype(bool)
        )

        deleted_pattern_ids = set(
            edited_table.loc[
                delete_mask,
                IDENTITY_COLUMN,
            ].tolist()
        )

    # --------------------------------------------------------
    # RECALCULATE CIA TOTAL
    # --------------------------------------------------------

    edited_table[DERIVED_COLUMN] = (
        edited_table["confidentiality_impact"]
        .apply(normalise_cia_value)
        +
        edited_table["integrity_impact"]
        .apply(normalise_cia_value)
        +
        edited_table["availability_impact"]
        .apply(normalise_cia_value)
    )

    # --------------------------------------------------------
    # SHOW DELETE WARNING
    # --------------------------------------------------------

    if deleted_pattern_ids:

        st.warning(
            f"{len(deleted_pattern_ids)} row(s) marked for deletion. "
            "They will be permanently removed from the database "
            "when you save."
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

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    if save_clicked:

        try:

            save_patterns(
                edited_table,
                deleted_pattern_ids,
            )

            # Clear the editor so the next render loads
            # the database fresh.
            if "patterns_table_editor" in st.session_state:
                del st.session_state["patterns_table_editor"]

            if deleted_pattern_ids:

                st.success(
                    f"Changes saved successfully. "
                    f"{len(deleted_pattern_ids)} row(s) deleted."
                )

            else:

                st.success(
                    "Changes saved successfully. "
                    "The database has been updated."
                )

            st.rerun()

        except Exception as error:

            st.error(
                f"Could not save changes: {error}"
            )