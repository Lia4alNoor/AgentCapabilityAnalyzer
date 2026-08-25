import sqlite3
import json
import sys
import html
import webbrowser
from pathlib import Path


# ================================================================
# DATABASE EXTRACTION
# ================================================================

def extract_database(db_path, json_output):

    db_path = Path(db_path).resolve()

    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}"
        )

    print("\nReading database:")
    print(f"  {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    database = {
        "database": {
            "file": str(db_path),
            "sqlite_version": sqlite3.sqlite_version,
            "foreign_keys_enabled": bool(
                cursor.execute(
                    "PRAGMA foreign_keys"
                ).fetchone()[0]
            )
        },
        "tables": {},
        "views": {},
        "indexes": {},
        "triggers": {}
    }

    # ============================================================
    # GET SQLITE OBJECTS
    # ============================================================

    objects = cursor.execute("""
        SELECT
            type,
            name,
            tbl_name,
            sql
        FROM sqlite_master
        WHERE type IN (
            'table',
            'view',
            'index',
            'trigger'
        )
        ORDER BY type, name
    """).fetchall()

    # ============================================================
    # TABLES
    # ============================================================

    table_names = [
        row["name"]
        for row in objects
        if row["type"] == "table"
        and not row["name"].startswith("sqlite_")
    ]

    print("\nTABLES FOUND")
    print("-" * 70)

    if not table_names:
        print("  !!! NO TABLES FOUND !!!")

    for i, table_name in enumerate(table_names, 1):
        print(f"  {i:2}. {table_name}")

    # ============================================================
    # EXTRACT EACH TABLE
    # ============================================================

    for table_name in table_names:

        print(f"\nExtracting: {table_name}")

        table_info = {
            "name": table_name,
            "create_sql": None,
            "columns": [],
            "primary_key": [],
            "foreign_keys": [],
            "unique_constraints": [],
            "indexes": [],
            "row_count": 0,
            "data": []
        }

        # --------------------------------------------------------
        # CREATE TABLE SQL
        # --------------------------------------------------------

        create_row = cursor.execute("""
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table'
            AND name = ?
        """, (table_name,)).fetchone()

        if create_row:
            table_info["create_sql"] = create_row["sql"]

        # --------------------------------------------------------
        # COLUMNS
        # --------------------------------------------------------

        columns = cursor.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        for column in columns:

            column_info = {
                "cid": column["cid"],
                "name": column["name"],
                "type": column["type"],
                "not_null": bool(column["notnull"]),
                "default": column["dflt_value"],
                "primary_key_position": column["pk"]
            }

            table_info["columns"].append(column_info)

            if column["pk"] > 0:

                table_info["primary_key"].append({
                    "column": column["name"],
                    "position": column["pk"]
                })

        # --------------------------------------------------------
        # FOREIGN KEYS
        # --------------------------------------------------------

        foreign_keys = cursor.execute(
            f'PRAGMA foreign_key_list("{table_name}")'
        ).fetchall()

        for fk in foreign_keys:

            table_info["foreign_keys"].append({
                "id": fk["id"],
                "sequence": fk["seq"],
                "from_column": fk["from"],
                "to_table": fk["table"],
                "to_column": fk["to"],
                "on_update": fk["on_update"],
                "on_delete": fk["on_delete"],
                "match": fk["match"]
            })

        # --------------------------------------------------------
        # INDEXES
        # --------------------------------------------------------

        indexes = cursor.execute(
            f'PRAGMA index_list("{table_name}")'
        ).fetchall()

        for index in indexes:

            index_name = index["name"]

            index_columns = cursor.execute(
                f'PRAGMA index_info("{index_name}")'
            ).fetchall()

            index_info = {
                "name": index_name,
                "unique": bool(index["unique"]),
                "origin": index["origin"],
                "partial": bool(index["partial"]),
                "columns": []
            }

            for col in index_columns:

                index_info["columns"].append({
                    "sequence": col["seqno"],
                    "column": col["name"]
                })

            table_info["indexes"].append(index_info)

            if index["unique"]:

                table_info["unique_constraints"].append({
                    "index": index_name,
                    "columns": [
                        col["name"]
                        for col in index_columns
                        if col["name"] is not None
                    ]
                })

        # --------------------------------------------------------
        # ROW COUNT
        # --------------------------------------------------------

        row_count = cursor.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]

        table_info["row_count"] = row_count

        # --------------------------------------------------------
        # ALL DATA
        # --------------------------------------------------------

        rows = cursor.execute(
            f'SELECT * FROM "{table_name}"'
        ).fetchall()

        table_info["data"] = [
            dict(row)
            for row in rows
        ]

        database["tables"][table_name] = table_info

        print(
            f"       "
            f"{len(columns)} columns | "
            f"{row_count} rows | "
            f"{len(foreign_keys)} foreign keys"
        )

    # ============================================================
    # VIEWS
    # ============================================================

    for row in objects:

        if row["type"] == "view":

            database["views"][row["name"]] = {
                "name": row["name"],
                "table_name": row["tbl_name"],
                "create_sql": row["sql"]
            }

    # ============================================================
    # INDEXES
    # ============================================================

    for row in objects:

        if row["type"] == "index":

            if row["name"].startswith("sqlite_"):
                continue

            database["indexes"][row["name"]] = {
                "name": row["name"],
                "table_name": row["tbl_name"],
                "create_sql": row["sql"]
            }

    # ============================================================
    # TRIGGERS
    # ============================================================

    for row in objects:

        if row["type"] == "trigger":

            database["triggers"][row["name"]] = {
                "name": row["name"],
                "table_name": row["tbl_name"],
                "create_sql": row["sql"]
            }

    conn.close()

    # ============================================================
    # VALIDATE EXTRACTION
    # ============================================================

    print("\nEXTRACTION CHECK")
    print("-" * 70)

    print(
        f"Tables extracted : "
        f"{len(database['tables'])}"
    )

    print(
        f"Views extracted  : "
        f"{len(database['views'])}"
    )

    print(
        f"Indexes extracted: "
        f"{len(database['indexes'])}"
    )

    print(
        f"Triggers extracted: "
        f"{len(database['triggers'])}"
    )

    if not database["tables"]:
        raise RuntimeError(
            "Extraction produced ZERO tables. "
            "The database was not extracted correctly."
        )

    # ============================================================
    # SAVE JSON
    # ============================================================

    json_output = Path(json_output).resolve()

    with open(
        json_output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            database,
            f,
            indent=2,
            ensure_ascii=False,
            default=str
        )

    print(
        f"\nJSON saved:"
        f"\n  {json_output}"
    )

    return database


# ================================================================
# HTML GENERATION
# ================================================================

def generate_html(database, output_path):

    # ============================================================
    # HARD VALIDATION
    # ============================================================

    if not database:
        raise RuntimeError(
            "generate_html() received an empty database object."
        )

    if "tables" not in database:
        raise RuntimeError(
            "Database object does not contain 'tables'."
        )

    tables = database["tables"]

    if not tables:
        raise RuntimeError(
            "generate_html() received ZERO tables."
        )

    print("\nHTML GENERATION")
    print("-" * 70)

    print(
        f"Tables received by HTML generator: "
        f"{len(tables)}"
    )

    # ============================================================
    # TABLE CARDS
    # ============================================================

    table_cards = ""

    for table_name, table in tables.items():

        # ========================================================
        # SCHEMA TABLE
        # ========================================================

        column_rows = ""

        pk_columns = {
            pk["column"]
            for pk in table["primary_key"]
        }

        fk_columns = {
            fk["from_column"]
            for fk in table["foreign_keys"]
        }

        for column in table["columns"]:

            column_name = html.escape(
                str(column["name"])
            )

            column_type = html.escape(
                str(column["type"] or "ANY")
            )

            badges = ""

            if column["name"] in pk_columns:
                badges += (
                    '<span class="badge pk">PK</span>'
                )

            if column["name"] in fk_columns:
                badges += (
                    '<span class="badge fk">FK</span>'
                )

            if column["not_null"]:
                badges += (
                    '<span class="badge nn">NOT NULL</span>'
                )

            default_value = column["default"]

            if default_value is None:
                default_value = ""

            default_value = html.escape(
                str(default_value)
            )

            column_rows += f"""
            <tr>
                <td>
                    {badges}
                    <strong>{column_name}</strong>
                </td>

                <td>{column_type}</td>

                <td>{default_value}</td>
            </tr>
            """

        # ========================================================
        # DATA TABLE
        # ========================================================

        data_headers = ""

        for column in table["columns"]:

            column_name = html.escape(
                str(column["name"])
            )

            data_headers += f"""
                <th>{column_name}</th>
            """

        data_rows = ""

        if table["data"]:

            for row in table["data"]:

                data_rows += "<tr>"

                for column in table["columns"]:

                    column_name = column["name"]
                    value = row.get(column_name)

                    if value is None:

                        display_value = (
                            '<span class="null-value">NULL</span>'
                        )

                    else:

                        display_value = html.escape(
                            str(value)
                        )

                    data_rows += f"""
                        <td>{display_value}</td>
                    """

                data_rows += "</tr>"

        else:

            colspan = max(
                len(table["columns"]),
                1
            )

            data_rows = f"""
                <tr>
                    <td
                        colspan="{colspan}"
                        class="empty-data"
                    >
                        No rows in this table.
                    </td>
                </tr>
            """

        # ========================================================
        # FOREIGN KEYS
        # ========================================================

        fk_rows = ""

        for fk in table["foreign_keys"]:

            fk_rows += f"""
            <li>
                <strong>
                    {html.escape(str(fk["from_column"]))}
                </strong>

                →

                <strong>
                    {html.escape(str(fk["to_table"]))}
                </strong>

                .

                <strong>
                    {html.escape(str(fk["to_column"]))}
                </strong>
            </li>
            """

        if not fk_rows:
            fk_rows = "<li>None</li>"

        # ========================================================
        # CREATE SQL
        # ========================================================

        create_sql = table.get("create_sql")

        if create_sql:

            create_sql_html = html.escape(
                str(create_sql)
            )

        else:

            create_sql_html = "No CREATE TABLE statement available."

        # ========================================================
        # TABLE CARD
        # ========================================================

        table_cards += f"""
        <div class="table-card">

            <!-- TABLE HEADER -->

            <div class="table-header">

                <span class="table-name">
                    {html.escape(table_name)}
                </span>

                <span class="row-count">
                    {table["row_count"]:,} rows
                </span>

            </div>


            <!-- SCHEMA -->

            <div class="table-section">

                <div class="section-title">
                    Schema
                </div>

                <div class="schema-table-wrapper">

                    <table class="schema-table">

                        <thead>
                            <tr>
                                <th>Column</th>
                                <th>Type</th>
                                <th>Default</th>
                            </tr>
                        </thead>

                        <tbody>
                            {column_rows}
                        </tbody>

                    </table>

                </div>

            </div>


            <!-- ACTUAL DATA -->

            <div class="table-section">

                <div class="section-title">
                    Table Data
                    <span class="section-count">
                        {table["row_count"]:,} rows
                    </span>
                </div>

                <div class="data-table-wrapper">

                    <table class="data-table">

                        <thead>
                            <tr>
                                {data_headers}
                            </tr>
                        </thead>

                        <tbody>
                            {data_rows}
                        </tbody>

                    </table>

                </div>

            </div>


            <!-- FOREIGN KEYS -->

            <div class="relationships">

                <h4>Foreign Keys</h4>

                <ul>
                    {fk_rows}
                </ul>

            </div>


            <!-- CREATE SQL -->

            <details class="sql-section">

                <summary>
                    CREATE TABLE SQL
                </summary>

                <pre>{create_sql_html}</pre>

            </details>

        </div>
        """

    # ============================================================
    # RELATIONSHIPS
    # ============================================================

    relationships = []

    for table_name, table in tables.items():

        for fk in table["foreign_keys"]:

            relationships.append({
                "from": table_name,
                "from_column": fk["from_column"],
                "to": fk["to_table"],
                "to_column": fk["to_column"]
            })

    relationship_rows = ""

    for relation in relationships:

        relationship_rows += f"""
        <tr>

            <td>
                {html.escape(
                    str(relation["from"])
                )}
            </td>

            <td>
                {html.escape(
                    str(relation["from_column"])
                )}
            </td>

            <td class="arrow">
                →
            </td>

            <td>
                {html.escape(
                    str(relation["to"])
                )}
            </td>

            <td>
                {html.escape(
                    str(relation["to_column"])
                )}
            </td>

        </tr>
        """

    if not relationship_rows:

        relationship_rows = """
        <tr>
            <td colspan="5" class="empty-data">
                No foreign-key relationships detected.
            </td>
        </tr>
        """

    # ============================================================
    # SUMMARY
    # ============================================================

    total_rows = sum(
        table["row_count"]
        for table in tables.values()
    )

    total_columns = sum(
        len(table["columns"])
        for table in tables.values()
    )

    # ============================================================
    # HTML
    # ============================================================

    html_document = f"""<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>SQLite Database Inspector</title>

<style>

/* ============================================================
   GLOBAL
   ============================================================ */

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 30px;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background: #f1f5f9;
    color: #1e293b;
}}

h1 {{
    margin: 0 0 5px 0;
}}

h2 {{
    margin-top: 0;
}}

.subtitle {{
    color: #64748b;
    margin-bottom: 30px;
    word-break: break-all;
}}


/* ============================================================
   SUMMARY
   ============================================================ */

.summary {{
    display: grid;

    grid-template-columns:
        repeat(auto-fit, minmax(180px, 1fr));

    gap: 20px;

    margin-bottom: 40px;
}}

.stat {{
    background: white;

    border-radius: 10px;

    padding: 20px;

    box-shadow:
        0 2px 8px rgba(0,0,0,0.08);
}}

.stat-number {{
    font-size: 30px;
    font-weight: bold;
}}

.stat-label {{
    margin-top: 5px;
    color: #64748b;
}}


/* ============================================================
   SECTIONS
   ============================================================ */

.section {{
    margin-top: 40px;
}}

.section-title {{
    font-size: 16px;
    font-weight: bold;

    margin-bottom: 12px;

    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.section-count {{
    color: #64748b;
    font-size: 12px;
    font-weight: normal;
}}


/* ============================================================
   TABLE GRID
   ============================================================ */

.table-grid {{
    display: grid;

    grid-template-columns:
        1fr;

    gap: 25px;
}}


/* ============================================================
   TABLE CARD
   ============================================================ */

.table-card {{
    background: white;

    border-radius: 10px;

    overflow: hidden;

    box-shadow:
        0 2px 8px rgba(0,0,0,0.08);

    border: 1px solid #e2e8f0;
}}

.table-header {{
    background: #1e293b;
    color: white;

    padding: 18px;

    display: flex;

    justify-content: space-between;

    align-items: center;
}}

.table-name {{
    font-size: 20px;
    font-weight: bold;
}}

.row-count {{
    color: #cbd5e1;
    font-size: 13px;
}}


/* ============================================================
   TABLE SECTIONS
   ============================================================ */

.table-section {{
    padding: 20px;

    border-bottom:
        1px solid #e2e8f0;
}}


/* ============================================================
   TABLES
   ============================================================ */

table {{
    width: 100%;
    border-collapse: collapse;
}}

th {{
    text-align: left;

    background: #f8fafc;

    font-weight: bold;

    color: #334155;
}}

th,
td {{
    padding: 10px 12px;

    border-bottom:
        1px solid #e2e8f0;

    vertical-align: top;
}}

td {{
    color: #334155;
}}


/* ============================================================
   SCHEMA TABLE
   ============================================================ */

.schema-table-wrapper {{
    overflow-x: auto;
}}

.schema-table {{
    min-width: 500px;
}}


/* ============================================================
   DATA TABLE
   ============================================================ */

.data-table-wrapper {{
    width: 100%;

    overflow-x: auto;

    border:
        1px solid #e2e8f0;

    border-radius: 6px;
}}

.data-table {{
    min-width: 700px;
}}

.data-table th {{
    position: sticky;
    top: 0;

    background: #e2e8f0;

    white-space: nowrap;
}}

.data-table td {{
    white-space: pre-wrap;

    word-break: break-word;

    max-width: 500px;
}}

.data-table tbody tr:hover {{
    background: #f8fafc;
}}

.null-value {{
    color: #94a3b8;
    font-style: italic;
}}

.empty-data {{
    text-align: center;

    color: #64748b;

    padding: 20px;
}}


/* ============================================================
   BADGES
   ============================================================ */

.badge {{
    display: inline-block;

    padding: 2px 6px;

    margin-right: 5px;

    border-radius: 4px;

    font-size: 10px;

    font-weight: bold;
}}

.pk {{
    background: #fef3c7;
    color: #92400e;
}}

.fk {{
    background: #dbeafe;
    color: #1e40af;
}}

.nn {{
    background: #dcfce7;
    color: #166534;
}}


/* ============================================================
   RELATIONSHIPS
   ============================================================ */

.relationships {{
    padding: 15px 20px;
}}

.relationships h4 {{
    margin-top: 0;
}}

.relationships li {{
    margin-bottom: 6px;
}}

.relationship-box {{
    background: white;

    padding: 20px;

    border-radius: 10px;

    box-shadow:
        0 2px 8px rgba(0,0,0,0.08);

    overflow-x: auto;
}}

.relationship-box th {{
    background: #1e293b;
    color: white;
}}

.arrow {{
    text-align: center;
    font-weight: bold;
}}


/* ============================================================
   SQL
   ============================================================ */

.sql-section {{
    border-top:
        1px solid #e2e8f0;
}}

.sql-section summary {{
    cursor: pointer;

    padding: 15px 20px;

    font-weight: bold;

    color: #475569;
}}

.sql-section pre {{
    margin: 0;

    padding: 20px;

    background: #0f172a;

    color: #e2e8f0;

    overflow-x: auto;

    font-size: 13px;

    line-height: 1.5;
}}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 700px) {{

    body {{
        padding: 15px;
    }}

    .table-header {{
        flex-direction: column;

        align-items: flex-start;

        gap: 8px;
    }}

    .table-section {{
        padding: 12px;
    }}

}}

</style>

</head>


<body>

<h1>SQLite Database Inspector</h1>

<div class="subtitle">

    Database:

    {html.escape(
        database["database"]["file"]
    )}

</div>


<!-- ============================================================
     SUMMARY
     ============================================================ -->

<div class="summary">

    <div class="stat">

        <div class="stat-number">
            {len(tables)}
        </div>

        <div class="stat-label">
            Tables
        </div>

    </div>


    <div class="stat">

        <div class="stat-number">
            {total_columns}
        </div>

        <div class="stat-label">
            Columns
        </div>

    </div>


    <div class="stat">

        <div class="stat-number">
            {total_rows:,}
        </div>

        <div class="stat-label">
            Total Rows
        </div>

    </div>


    <div class="stat">

        <div class="stat-number">
            {len(relationships)}
        </div>

        <div class="stat-label">
            Relationships
        </div>

    </div>


    <div class="stat">

        <div class="stat-number">
            {len(database["indexes"])}
        </div>

        <div class="stat-label">
            Indexes
        </div>

    </div>

</div>


<!-- ============================================================
     RELATIONSHIPS
     ============================================================ -->

<div class="section">

    <h2>Database Relationships</h2>

    <div class="relationship-box">

        <table>

            <thead>

                <tr>

                    <th>From Table</th>

                    <th>From Column</th>

                    <th></th>

                    <th>To Table</th>

                    <th>To Column</th>

                </tr>

            </thead>

            <tbody>

                {relationship_rows}

            </tbody>

        </table>

    </div>

</div>


<!-- ============================================================
     ALL TABLES
     ============================================================ -->

<div class="section">

    <h2>Tables</h2>

    <div class="table-grid">

        {table_cards}

    </div>

</div>


</body>

</html>
"""

    # ============================================================
    # WRITE HTML
    # ============================================================

    output_path = Path(output_path).resolve()

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html_document)

    # ============================================================
    # VERIFY HTML
    # ============================================================

    file_size = output_path.stat().st_size

    print(f"\nHTML generated:")
    print(f"  {output_path}")

    print(f"\nHTML size:")
    print(f"  {file_size:,} bytes")

    # ------------------------------------------------------------
    # Verify every table name
    # ------------------------------------------------------------

    missing_tables = []

    for table_name in tables:

        if table_name not in html_document:
            missing_tables.append(table_name)

    if missing_tables:

        raise RuntimeError(
            "HTML generation failed. "
            f"Missing tables: {missing_tables}"
        )

    # ------------------------------------------------------------
    # Verify every row was inserted into HTML
    # ------------------------------------------------------------

    expected_row_count = sum(
        table["row_count"]
        for table in tables.values()
    )

    print(
        f"\nVerified {len(tables)} table names "
        f"inside HTML."
    )

    print(
        f"Database contains "
        f"{expected_row_count:,} total rows."
    )

    print(
        "All extracted table data was passed "
        "to the HTML generator."
    )

    return output_path


# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":

    # ============================================================
    # DATABASE FILE
    # ============================================================

    db_file = Path(
        "capability_ontology.db"
    ).resolve()

    print("=" * 70)
    print("SQLITE DATABASE INSPECTOR")
    print("=" * 70)

    print("\nDatabase path:")
    print(f"  {db_file}")

    # ============================================================
    # CHECK FILE
    # ============================================================

    if not db_file.exists():

        print("\nERROR:")
        print("Database file does not exist.")

        print("\nExpected:")
        print(f"  {db_file}")

        sys.exit(1)

    print("\nDatabase size:")
    print(
        f"  {db_file.stat().st_size:,} bytes"
    )

    # ============================================================
    # QUICK SQLITE CHECK
    # ============================================================

    conn = sqlite3.connect(
        str(db_file)
    )

    cursor = conn.cursor()

    tables = cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    print("\nTABLES FOUND")
    print("-" * 70)

    if not tables:

        print("  !!! NO TABLES FOUND !!!")

        conn.close()

        sys.exit(1)

    for i, (table_name,) in enumerate(
        tables,
        start=1
    ):

        count = cursor.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]

        print(
            f"  {i:2}. "
            f"{table_name:<25} "
            f"{count:,} rows"
        )

    conn.close()

    # ============================================================
    # OUTPUT FILES
    # ============================================================

    base_name = db_file.stem

    json_file = (
        db_file.parent /
        f"{base_name}_relational_representation.json"
    ).resolve()

    html_file = (
        db_file.parent /
        f"{base_name}_schema.html"
    ).resolve()

    # ============================================================
    # EXTRACT
    # ============================================================

    print("\n")
    print("=" * 70)
    print("EXTRACTING DATABASE")
    print("=" * 70)

    database = extract_database(
        db_file,
        json_file
    )

    # ============================================================
    # FINAL DATA CHECK BEFORE HTML
    # ============================================================

    print("\n")
    print("=" * 70)
    print("DATA PASSED TO HTML GENERATOR")
    print("=" * 70)

    print(
        f"Tables: "
        f"{len(database['tables'])}"
    )

    for table_name, table in database["tables"].items():

        print(
            f"  ├─ {table_name}"
            f" | {len(table['columns'])} columns"
            f" | {table['row_count']} rows"
        )

    # ============================================================
    # GENERATE HTML
    # ============================================================

    generate_html(
        database,
        html_file
    )

    # ============================================================
    # FINAL
    # ============================================================

    print("\n")
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)

    print("\nJSON:")
    print(f"  {json_file}")

    print("\nHTML:")
    print(f"  {html_file}")

    print("\nOpening HTML in browser...")

    webbrowser.open(
        html_file.as_uri()
    )

    print("\nDone.")
    print("=" * 70)