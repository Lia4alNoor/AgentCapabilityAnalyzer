"""
======================================================================
SOURCE CODE READER
======================================================================

Purpose
-------
Read the source code associated with an MCP tool.

The source JSON determines which source directory is used.

Source mapping
--------------
everything_tools.json
    -> src_server_code/everything/

filesystem_tools.json
    -> src_server_code/filesystem/

git_tools.json
    -> src_server_code/git/

memory_tools.json
    -> src_server_code/memory/


Special handling
----------------
The "everything" server has one source file per tool.

Therefore:

    echo
        -> everything/echo.ts

For the other servers, the implementation may be distributed across
multiple source files. Their complete source directory is therefore
read as one combined source corpus.


Usage
-----
python source_code_reader.py echo everything_tools.json

python source_code_reader.py write_file filesystem_tools.json

python source_code_reader.py git_status git_tools.json

python source_code_reader.py
    -> asks for both values interactively
"""

import sys
from pathlib import Path


# ======================================================================
# CONFIGURATION
# ======================================================================

SCRIPT_DIR = Path(__file__).resolve().parent

SRC_SERVER_CODE_DIR = (
    SCRIPT_DIR / "src_server_code"
)

SOURCE_EXTENSIONS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
}


# ======================================================================
# SOURCE DIRECTORY MAPPING
# ======================================================================

SOURCE_DIRECTORY_MAP = {
    "everything_tools.json": "everything",
    "filesystem_tools.json": "filesystem",
    "git_tools.json": "git",
    "memory_tools.json": "memory",
}


# ======================================================================
# FIND SOURCE DIRECTORY
# ======================================================================

def get_source_directory(source_json):
    """
    Determine which src_server_code directory corresponds to the
    supplied JSON source file.
    """

    source_json = Path(
        source_json
    ).name

    directory_name = SOURCE_DIRECTORY_MAP.get(
        source_json
    )

    if directory_name is None:

        raise ValueError(
            f"Unknown source JSON file: {source_json}\n\n"
            f"Supported files:\n"
            f"  {', '.join(SOURCE_DIRECTORY_MAP.keys())}"
        )

    source_directory = (
        SRC_SERVER_CODE_DIR / directory_name
    )

    if not source_directory.exists():

        raise FileNotFoundError(
            f"Source directory does not exist:\n"
            f"  {source_directory}"
        )

    return source_directory


# ======================================================================
# FIND SOURCE FILES
# ======================================================================

def find_source_files(source_directory):
    """
    Recursively find supported source files inside a server directory.
    """

    files = []

    for filepath in source_directory.rglob("*"):

        if not filepath.is_file():
            continue

        if filepath.suffix.lower() not in SOURCE_EXTENSIONS:
            continue

        files.append(filepath)

    return sorted(files)


# ======================================================================
# EVERYTHING SERVER
# ======================================================================

def find_everything_tool_file(
    tool_name,
    source_directory
):
    """
    Find the individual source file for a tool belonging to the
    "everything" server.

    Example:

        echo
            -> everything/echo.ts
    """

    expected_filename = (
        f"{tool_name}.ts"
    )

    matches = []

    for filepath in source_directory.rglob(
        expected_filename
    ):

        if filepath.is_file():
            matches.append(filepath)

    if not matches:
        return None

    if len(matches) > 1:

        print(
            "\nWARNING: Multiple files matched the tool:"
        )

        for filepath in matches:
            print(
                f"  {filepath}"
            )

        print(
            "\nUsing the first match."
        )

    return matches[0]


# ======================================================================
# READ SOURCE FILE
# ======================================================================

def read_source_file(filepath):
    """
    Read a source file using UTF-8.
    """

    try:

        return filepath.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        return filepath.read_text(
            encoding="utf-8-sig"
        )


# ======================================================================
# READ EVERYTHING TOOL
# ======================================================================

def read_everything_tool(
    tool_name,
    source_directory
):
    """
    Read the specific tool file for the everything server.
    """

    filepath = find_everything_tool_file(
        tool_name,
        source_directory
    )

    if filepath is None:
        return []

    return [
        {
            "source_file": filepath,
            "source": read_source_file(filepath)
        }
    ]


# ======================================================================
# READ COMPLETE SERVER CORPUS
# ======================================================================

def read_server_corpus(
    source_directory
):
    """
    Read all source files belonging to a server.

    The files are kept separate in the returned structure so the
    output can identify where each piece of code came from.
    """

    source_files = find_source_files(
        source_directory
    )

    results = []

    for filepath in source_files:

        try:

            source = read_source_file(
                filepath
            )

        except Exception as error:

            print(
                f"\nWARNING: Could not read:"
                f"\n  {filepath}"
                f"\nReason: {error}"
            )

            continue

        results.append({
            "source_file": filepath,
            "source": source
        })

    return results


# ======================================================================
# DISPLAY SOURCE
# ======================================================================

def display_results(
    tool_name,
    source_json,
    source_directory,
    source_results
):
    """
    Display the source code associated with the tool.
    """

    relative_directory = (
        source_directory.relative_to(
            SRC_SERVER_CODE_DIR
        )
    )

    print("\n" + "=" * 110)

    print(
        "MCP TOOL SOURCE CODE READER"
    )

    print("=" * 110)

    print(
        f"\nTool:"
        f"\n  {tool_name}"
    )

    print(
        f"\nSource JSON:"
        f"\n  {source_json}"
    )

    print(
        f"\nSource directory:"
        f"\n  {relative_directory}"
    )

    print(
        f"\nSource files read:"
        f"\n  {len(source_results)}"
    )

    if not source_results:

        print(
            "\nNo source code was found."
        )

        return

    # --------------------------------------------------------------
    # Explain what is being shown
    # --------------------------------------------------------------

    if source_json == "everything_tools.json":

        print(
            "\nReading mode:"
            "\n  Individual tool source file"
        )

    else:

        print(
            "\nReading mode:"
            "\n  Complete server source corpus"
        )

    # --------------------------------------------------------------
    # Display source
    # --------------------------------------------------------------

    for number, result in enumerate(
        source_results,
        start=1
    ):

        relative_path = (
            result["source_file"].relative_to(
                SRC_SERVER_CODE_DIR
            )
        )

        print("\n" + "-" * 110)

        print(
            f"SOURCE FILE {number}"
        )

        print(
            f"Path:"
            f"\n  {relative_path}"
        )

        print("-" * 110)

        print(
            result["source"]
        )

    print("\n" + "=" * 110)

    print(
        "END OF SOURCE CODE"
    )

    print("=" * 110)


# ======================================================================
# MAIN
# ======================================================================

def main():

    print("\n" + "=" * 110)

    print(
        "MCP TOOL SOURCE CODE READER"
    )

    print("=" * 110)

    # --------------------------------------------------------------
    # Get tool name
    # --------------------------------------------------------------

    if len(sys.argv) >= 2:

        tool_name = sys.argv[1].strip()

    else:

        tool_name = input(
            "\nEnter MCP tool name: "
        ).strip()

    if not tool_name:

        print(
            "\nERROR: Tool name cannot be empty."
        )

        return

    # --------------------------------------------------------------
    # Get source JSON
    # --------------------------------------------------------------

    if len(sys.argv) >= 3:

        source_json = sys.argv[2].strip()

    else:

        source_json = input(
            "\nEnter source JSON filename "
            "(e.g. everything_tools.json): "
        ).strip()

    if not source_json:

        print(
            "\nERROR: Source JSON filename "
            "cannot be empty."
        )

        return

    # --------------------------------------------------------------
    # Determine source directory
    # --------------------------------------------------------------

    try:

        source_directory = get_source_directory(
            source_json
        )

    except (
        ValueError,
        FileNotFoundError
    ) as error:

        print(
            f"\nERROR:\n{error}"
        )

        return

    # --------------------------------------------------------------
    # Read source
    # --------------------------------------------------------------

    if source_json == "everything_tools.json":

        source_results = read_everything_tool(
            tool_name,
            source_directory
        )

        if not source_results:

            print(
                f"\nERROR: Could not find the source file for:"
                f"\n  {tool_name}"
            )

            print(
                f"\nExpected:"
                f"\n  {source_directory / (tool_name + '.ts')}"
            )

            return

    else:

        source_results = read_server_corpus(
            source_directory
        )

    # --------------------------------------------------------------
    # Display
    # --------------------------------------------------------------

    display_results(
        tool_name,
        source_json,
        source_directory,
        source_results
    )


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()