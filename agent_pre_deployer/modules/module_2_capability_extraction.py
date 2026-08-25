"""
Module 2: Capability Extraction

Extracts semantic capability features from tools.
Creates assumed_capability (tool name + description) for normalization.

Does NOT normalize - that's Module 3's job.
Does NOT map to C1-C6 - that's Module 4's job.
"""


def run(input_data):
    """
    Main entry point for Module 2: Capability Extraction

    Args:
        input_data (dict): Output from Module 1
                          {
                              'tools': [...],
                              'tool_count': 10,
                              'source_file': 'data/...'
                          }

    Returns:
        dict: Tools with extracted capability features
    """
    print("=" * 70)
    print("Module 2: Capability Extraction")
    print("=" * 70)

    result = process(input_data)
    return result


def process(data):
    """
    Extract capability features from tools.

    For each tool, extracts semantic features that describe
    what the tool can do:
    - is_read_only
    - is_destructive
    - modifies_state
    - accesses_external
    - executes_code

    Also creates assumed_capability (tool name + description)
    for normalization in Module 3.

    Args:
        data (dict): Tools data from Module 1

    Returns:
        dict: Enhanced tools with extracted features
    """
    if not data:
        return None

    tools = data.get('tools', [])

    print(f"\nExtracting capabilities from {len(tools)} tools...\n")

    extracted_tools = []
    for tool in tools:
        extracted = extract_tool_capabilities(tool)
        extracted_tools.append(extracted)
        print(f"  [+] {tool['tool']}: extracted features")

    result = {
        'tools': extracted_tools,
        'tool_count': len(extracted_tools),
        'source_file': data.get('source_file'),
        'extraction_complete': True
    }

    print(f"\n✓ Extraction complete: {len(extracted_tools)} tools processed")

    return result


def extract_tool_capabilities(tool):
    """
    Extract capability features from a single tool.

    Args:
        tool (dict): Single tool object
                    {
                        "tool": "write_file",
                        "description": "Create/overwrite a file",
                        "readOnlyHint": false,
                        "destructiveHint": true,
                        ...
                    }

    Returns:
        dict: Tool with extracted capabilities
              {
                  "tool": "write_file",
                  "description": "Create/overwrite a file",
                  ... (original fields) ...,
                  "assumed_capability": "write_file Create/overwrite a file",
                  "capability_features": {
                      "is_read_only": false,
                      "is_destructive": true,
                      "modifies_state": true,
                      "accesses_external": false,
                      "executes_code": false
                  }
              }
    """
    # Start with original tool data
    result = dict(tool)

    # Extract semantic features from hints and description
    tool_name = tool.get('tool', '').lower()
    description = tool.get('description', '').lower()
    combined_text = f"{tool_name} {description}"

    # Create assumed_capability (for Module 3)
    result['assumed_capability'] = f"{tool.get('tool', '')} {tool.get('description', '')}".strip()

    # Extract capability features
    capability_features = {
        'is_read_only': extract_is_readonly(tool, combined_text),
        'is_destructive': extract_is_destructive(tool, combined_text),
        'modifies_state': extract_modifies_state(tool, combined_text),
        'accesses_external': extract_accesses_external(tool, combined_text),
        'executes_code': extract_executes_code(tool, combined_text)
    }

    result['capability_features'] = capability_features

    return result


def extract_is_readonly(tool, combined_text):
    """
    Determine if tool is read-only.

    Read operations: read, list, get, retrieve, query, show, view, display
    """
    if tool.get('readOnlyHint') is True:
        return True

    readonly_keywords = [
        'read', 'list', 'get', 'retrieve', 'query', 'show',
        'view', 'display', 'fetch', 'search', 'find', 'describe'
    ]

    for keyword in readonly_keywords:
        if f" {keyword}" in f" {combined_text}" or combined_text.startswith(keyword):
            # Confirmed read-only if no write/modify keywords
            if not any(word in combined_text for word in ['write', 'create', 'delete', 'edit', 'modify', 'move']):
                return True

    return False


def extract_is_destructive(tool, combined_text):
    """
    Determine if tool can destroy or modify data.

    Destructive operations: write, create, delete, edit, modify, move, remove
    """
    if tool.get('destructiveHint') is True:
        return True

    destructive_keywords = [
        'write', 'create', 'delete', 'edit', 'modify',
        'move', 'remove', 'drop', 'destroy', 'clear',
        'overwrite', 'replace', 'update', 'insert', 'truncate'
    ]

    for keyword in destructive_keywords:
        if f" {keyword}" in f" {combined_text}" or combined_text.startswith(keyword):
            return True

    return False


def extract_modifies_state(tool, combined_text):
    """
    Determine if tool modifies persistent application/system state.

    State modification: create, write, edit, delete, update, move
    """
    if tool.get('destructiveHint') is True:
        return True

    state_keywords = [
        'create', 'write', 'edit', 'delete', 'update', 'move',
        'modify', 'insert', 'remove', 'change', 'alter',
        'directory', 'file', 'database', 'config', 'state'
    ]

    has_state_action = False
    has_state_target = False

    for keyword in state_keywords:
        if f" {keyword}" in f" {combined_text}":
            if keyword in ['create', 'write', 'edit', 'delete', 'update', 'move', 'modify']:
                has_state_action = True
            if keyword in ['directory', 'file', 'database', 'config', 'state']:
                has_state_target = True

    return has_state_action and has_state_target


def extract_accesses_external(tool, combined_text):
    """
    Determine if tool accesses external/open-world data sources.

    External access: fetch, http, url, web, api, external, internet, remote
    """
    if tool.get('openWorldHint') is True:
        return True

    external_keywords = [
        'fetch', 'http', 'url', 'web', 'api', 'external',
        'internet', 'remote', 'download', 'request', 'service',
        'endpoint', 'network', 'cloud'
    ]

    for keyword in external_keywords:
        if f" {keyword}" in f" {combined_text}" or combined_text.startswith(keyword):
            return True

    return False


def extract_executes_code(tool, combined_text):
    """
    Determine if tool executes code/commands on the system.

    Execution: execute, run, exec, command, shell, script, eval, spawn
    """
    execution_keywords = [
        'execute', 'run', 'exec', 'command', 'shell',
        'script', 'eval', 'spawn', 'process', 'system',
        'subprocess', 'fork'
    ]

    for keyword in execution_keywords:
        if f" {keyword}" in f" {combined_text}" or combined_text.startswith(keyword):
            return True

    return False