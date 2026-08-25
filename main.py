# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import json
from pathlib import Path


# ============================================================
# TABLE 2 — Filesystem: Declared Tool Capabilities
# ============================================================

filesystem_tools = [
    {
        "tool": "write_file",
        "description": "Create/overwrite a file",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "index.ts"
    },
    {
        "tool": "edit_file",
        "description": "Replace exact text in a file",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
        "source": "index.ts"
    },
    {
        "tool": "create_directory",
        "description": "Create a directory",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "index.ts"
    },
    {
        "tool": "list_directory",
        "description": "List directory contents",
        "readOnlyHint": True,
        "destructiveHint": None,
        "idempotentHint": None,
        "openWorldHint": False,
        "source": "index.ts"
    },
    {
        "tool": "list_directory_with_sizes",
        "description": "List contents and sizes",
        "readOnlyHint": True,
        "destructiveHint": None,
        "idempotentHint": None,
        "openWorldHint": False,
        "source": "index.ts"
    },
    {
        "tool": "directory_tree",
        "description": "Recursively show directory tree",
        "readOnlyHint": True,
        "destructiveHint": None,
        "idempotentHint": None,
        "openWorldHint": False,
        "source": "index.ts"
    },
    {
        "tool": "move_file",
        "description": "Move/rename files or directories",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
        "source": "index.ts"
    },
    {
        "tool": "search_files",
        "description": "Search files/directories by pattern",
        "readOnlyHint": True,
        "destructiveHint": None,
        "idempotentHint": None,
        "openWorldHint": False,
        "source": "index.ts"
    },
    {
        "tool": "get_file_info",
        "description": "Retrieve file/directory metadata",
        "readOnlyHint": True,
        "destructiveHint": None,
        "idempotentHint": None,
        "openWorldHint": False,
        "source": "index.ts"
    },
    {
        "tool": "list_allowed_directories",
        "description": "List accessible directories",
        "readOnlyHint": True,
        "destructiveHint": None,
        "idempotentHint": None,
        "openWorldHint": False,
        "source": "index.ts"
    }
]


# ============================================================
# TABLE 3 — Git: Declared Tool Capabilities
# ============================================================

git_tools = [
    {
        "tool": "git_status",
        "description": "Shows the working tree status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_diff_unstaged",
        "description": "Shows changes in the working directory that are not yet staged",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_diff_staged",
        "description": "Shows changes that are staged for commit",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_diff",
        "description": "Shows differences between branches or commits",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_commit",
        "description": "Records changes to the repository",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_add",
        "description": "Adds file contents to the staging area",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_reset",
        "description": "Unstages all staged changes",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_log",
        "description": "Shows the commit logs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_create_branch",
        "description": "Creates a new branch from an optional base branch",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_checkout",
        "description": "Switches branches",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_show",
        "description": "Shows the contents of a commit",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "list_tools()"
    },
    {
        "tool": "git_branch",
        "description": "List Git branches",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "list_tools()"
    }
]


# ============================================================
# TABLE 4 — Memory: Declared Tool Capabilities
# ============================================================

memory_tools = [
    {
        "tool": "create_entities",
        "description": "Create multiple new entities in the knowledge graph",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
        "source": "registerTool()"
    },
    {
        "tool": "create_relations",
        "description": "Create multiple new relations between entities in the knowledge graph. Relations should be in active voice",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
        "source": "registerTool()"
    },
    {
        "tool": "add_observations",
        "description": "Add new observations to existing entities in the knowledge graph",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
        "source": "registerTool()"
    },
    {
        "tool": "delete_entities",
        "description": "Delete multiple entities and their associated relations from the knowledge graph",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "registerTool()"
    },
    {
        "tool": "delete_observations",
        "description": "Delete specific observations from entities in the knowledge graph",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "registerTool()"
    },
    {
        "tool": "delete_relations",
        "description": "Delete multiple relations from the knowledge graph",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "registerTool()"
    },
    {
        "tool": "read_graph",
        "description": "Read the entire knowledge graph",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "registerTool()"
    },
    {
        "tool": "search_nodes",
        "description": "Search for nodes in the knowledge graph based on a query",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "registerTool()"
    },
    {
        "tool": "open_nodes",
        "description": "Open specific nodes in the knowledge graph by their names",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "source": "registerTool()"
    }
]


# ============================================================
# TABLE 5 — Everything: Declared Tool Capabilities
# ============================================================

everything_tools = [
    {
        "tool": "echo",
        "description": "Echoes back the input string",
        "outputSchema": None,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "get-annotated-message",
        "description": "Demonstrates how annotations can be used to provide metadata about content.",
        "outputSchema": None,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "get-env",
        "description": "Returns environment variables for debugging MCP server configuration",
        "outputSchema": None,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "get-resource-links",
        "description": "Returns resource links that reference different types of resources",
        "outputSchema": None,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "get-resource-reference",
        "description": "Returns a resource reference that can be used by MCP clients",
        "outputSchema": None,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "get-roots-list",
        "description": "Lists the current MCP roots provided by the client",
        "outputSchema": None,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "get-structured-content",
        "description": "Returns structured content along with an output schema",
        "outputSchema": "Declared",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "get-sum",
        "description": "Returns the sum of two numbers",
        "outputSchema": None,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "get-tiny-image",
        "description": "Returns a tiny MCP logo image",
        "outputSchema": None,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "gzip-file-as-resource",
        "description": "Compresses a file using gzip and returns a resource or resource link",
        "outputSchema": None,
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    },
    {
        "tool": "toggle-simulated-logging",
        "description": "Toggles simulated random-level logging on or off",
        "outputSchema": None,
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    },
    {
        "tool": "toggle-subscriber-updates",
        "description": "Toggles simulated resource subscription updates on or off",
        "outputSchema": None,
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    },
    {
        "tool": "trigger-long-running-operation",
        "description": "Demonstrates a long-running operation with progress updates",
        "outputSchema": None,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    {
        "tool": "trigger-elicitation-request",
        "description": "Triggers a request from the server for user elicitation",
        "outputSchema": None,
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    },
    {
        "tool": "trigger-elicitation-request-async",
        "description": "Triggers an asynchronous elicitation request",
        "outputSchema": None,
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    },
    {
        "tool": "trigger-sampling-request",
        "description": "Triggers a request from the server for LLM sampling",
        "outputSchema": None,
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    },
    {
        "tool": "trigger-sampling-request-async",
        "description": "Triggers an asynchronous sampling request",
        "outputSchema": None,
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    },
    {
        "tool": "simulate-research-query",
        "description": "Simulates a deep research operation",
        "outputSchema": None,
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    },
    {
        "tool": "trigger-url-elicitation",
        "description": "Triggers URL elicitation for a browser flow",
        "outputSchema": None,
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
]


# ============================================================
# SERVER PROVENANCE
# ============================================================

server_provenance = {
    "filesystem": {
        "server": "Filesystem",
        "server_id": "@modelcontextprotocol/server-filesystem",
        "version": "0.6.3",
        "source_commit": "fd8248e56b822cc16a74b6610a88141fdfa09bd6",
        "registration_source": "src/filesystem/index.ts"
    },
    "git": {
        "server": "Git",
        "server_id": "@modelcontextprotocol/git",
        "version": "0.6.3",
        "source_commit": "3bcfedd8e40212a1fd6e4bd3ab5abf459257f83b",
        "registration_source": "src/git/src/mcp_server_git/server.py"
    },
    "memory": {
        "server": "Memory",
        "server_id": None,
        "version": None,
        "source_commit": "7b1170d1da1e36bc9f553f51e76e64cbfd652b3e",
        "registration_source": "src/memory/index.ts"
    },
    "everything": {
        "server": "Everything",
        "server_id": None,
        "version": None,
        "source_commit": None,
        "registration_source": "src/everything/tools"
    }
}


# ============================================================
# COMPLETE DATASET
# ============================================================

mcp_dataset = {
    "server_provenance": server_provenance,

    "tools": {
        "filesystem": filesystem_tools,
        "git": git_tools,
        "memory": memory_tools,
        "everything": everything_tools
    }
}


# ============================================================
# SAVE AS JSON
# ============================================================

output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

# Individual tables
with open(output_dir / "filesystem_tools.json", "w", encoding="utf-8") as f:
    json.dump(filesystem_tools, f, indent=2, ensure_ascii=False)

with open(output_dir / "git_tools.json", "w", encoding="utf-8") as f:
    json.dump(git_tools, f, indent=2, ensure_ascii=False)

with open(output_dir / "memory_tools.json", "w", encoding="utf-8") as f:
    json.dump(memory_tools, f, indent=2, ensure_ascii=False)

with open(output_dir / "everything_tools.json", "w", encoding="utf-8") as f:
    json.dump(everything_tools, f, indent=2, ensure_ascii=False)

# Server provenance
with open(output_dir / "server_provenance.json", "w", encoding="utf-8") as f:
    json.dump(server_provenance, f, indent=2, ensure_ascii=False)

# Complete dataset
with open(output_dir / "mcp_dataset.json", "w", encoding="utf-8") as f:
    json.dump(mcp_dataset, f, indent=2, ensure_ascii=False)


# ============================================================
# VERIFICATION
# ============================================================

print("Dataset created successfully.")
print()
print(f"Filesystem tools : {len(filesystem_tools)}")
print(f"Git tools        : {len(git_tools)}")
print(f"Memory tools     : {len(memory_tools)}")
print(f"Everything tools : {len(everything_tools)}")
print(f"Total tools      : {len(filesystem_tools) + len(git_tools) + len(memory_tools) + len(everything_tools)}")

