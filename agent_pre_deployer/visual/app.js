/* =========================================================
   AgentPreDeployer
   Interactive Mermaid Capability Mapping

   NODE DETAILS
   ========================================================= */


/* =========================================================
   NODE DETAILS
   ========================================================= */

const NODE_DETAILS = {

    A: {
        title: "MCP Tool JSON",
        category: "Input",
        badges: ["Input", "MCP", "Tool Metadata"],

        description:
            "The starting point of the pipeline. The system receives an MCP tool definition containing the tool name, description, and available hints.",

        inputs: [
            ["Tool name", "Name or identifier of the MCP tool"],
            ["Description", "Natural-language description of what the tool does"],
            ["Hints", "Metadata such as readOnlyHint, openWorldHint, and destructiveHint"]
        ],

        outputs: [
            "Normalized tool representation",
            "Raw semantic information for capability extraction"
        ],

        path: [
            "MCP Tool JSON",
            "M2",
            "M3",
            "M5"
        ]
    },


    B: {
        title: "Text Normalization",
        category: "Module 2",
        badges: ["M2", "Pre-processing"],

        description:
            "Normalizes textual input before semantic capability detectors are applied.",

        rules: [
            "lowercase",
            "_ - / → spaces",
            "collapse whitespace"
        ],

        purpose:
            "The normalization step reduces superficial differences in tool descriptions so that downstream keyword and regular-expression detectors can operate consistently.",

        path: [
            "MCP Tool JSON",
            "Normalize text",
            "Capability detectors"
        ]
    },


    C: {
        title: "assumed_capability",
        category: "Module 2",
        badges: ["M2", "Intermediate Representation"],

        description:
            "Creates the assumed_capability representation from the tool name and description. Module 2 produces this representation; Module 3 is responsible for normalization and ontology mapping.",

        fields: [
            ["Source", "Tool name + description"],
            ["Role", "Intermediate semantic representation"],
            ["Used by", "Module 3 canon_normalizer"]
        ],

        purpose:
            "Provides Module 3 with the textual evidence required to identify one or more capability concepts."
    },


    D1: {
        title: "Read-only Detector",
        category: "Module 2",
        badges: ["M2", "Read-only", "Detector"],

        description:
            "Detects language suggesting that a tool primarily reads, retrieves, displays, searches, or inspects information.",

        rules: [
            "read | list | get | retrieve",
            "query | show | view | display",
            "fetch | search | find | describe | inspect",
            "AND no state-modifying keyword"
        ],

        purpose:
            "Produces behavioural evidence indicating that a tool may be read-only. This is intermediate evidence and is not itself a direct C1–C6 mapping.",

        important:
            "The detector explicitly checks for the absence of state-modifying language."
    },


    D2: {
        title: "Destructive Detector",
        category: "Module 2",
        badges: ["M2", "Destructive", "Detector"],

        description:
            "Detects language associated with destructive operations.",

        rules: [
            "delete",
            "remove",
            "drop",
            "destroy",
            "clear",
            "overwrite",
            "truncate"
        ],

        purpose:
            "Provides behavioural evidence that the tool may perform destructive state changes."
    },


    D3: {
        title: "State-modification Detector",
        category: "Module 2",
        badges: ["M2", "State Modification", "Detector"],

        description:
            "Detects operations that create, modify, update, delete, move, rename, save, or otherwise alter persistent state.",

        rules: [
            "create | write | edit | modify | update",
            "insert | remove | move | rename",
            "overwrite | alter | truncate | destroy",
            "drop | clear | append | save",
            "set | change",
            "+ state target noun"
        ],

        purpose:
            "Creates behavioural evidence that a tool changes state. Module 3 subsequently determines whether this evidence corresponds to C4 State Modification."
    },


    D4: {
        title: "External-access Detector",
        category: "Module 2",
        badges: ["M2", "External Access", "Detector"],

        description:
            "Detects descriptions indicating access to external, remote, web, HTTP, API, or other externally hosted resources.",

        rules: [
            "fetch.*(data|content|information|resource)",
            "retrieve.*(data|content|information|resource)",
            "download.*(file|content|data|resource)",
            "web search | search the web",
            "browse.*web",
            "http.*request | https.*request",
            "api.*request | request.*external",
            "access.*remote | retrieve.*remote",
            "connect.*external",
            "external.*service",
            "remote.*service | remote.*server"
        ],

        purpose:
            "Produces intermediate behavioural evidence associated with external access."
    },


    D5: {
        title: "Code-execution Detector",
        category: "Module 2",
        badges: ["M2", "Execution", "Detector"],

        description:
            "Detects descriptions indicating command, script, program, shell, process, or code execution.",

        rules: [
            "execute.*(code|command|script|program)",
            "execute.*shell",
            "run.*(command|script|code|program|shell)",
            "run.*process",
            "execute command | run command",
            "shell command",
            "shell.*execution",
            "command execution",
            "evaluate.*(code|expression|script)",
            "eval.*(code|expression)",
            "spawn.*process",
            "subprocess",
            "child process",
            "terminal command",
            "system command",
            "script execution"
        ],

        purpose:
            "Produces behavioural evidence that can support the C5 System Execution mapping."
    },


    D6: {
        title: "External-communication Detector",
        category: "Module 2",
        badges: ["M2", "Communication", "Detector"],

        description:
            "Detects descriptions suggesting that a tool communicates externally, sends information, makes requests, contacts services, or interacts with users or external APIs.",

        rules: [
            "send.*message | send.*request",
            "send.*data | send.*email",
            "send.*notification | send.*response",
            "server.*request",
            "request.*user | user.*request",
            "user elicitation | elicitation request",
            "sampling request",
            "communicate.*with",
            "communication.*with",
            "external interaction",
            "trigger.*(elicitation|sampling)",
            "call.*api | api.*call",
            "call.*service",
            "contact.*server",
            "notify.*user"
        ],

        purpose:
            "Produces behavioural evidence associated with external communication. This evidence later contributes to C3 External Communication mapping."
    },


    F: {
        title: "capability_features",
        category: "Module 2",
        badges: ["M2", "Feature Vector", "Intermediate"],

        description:
            "Aggregates the behavioural evidence generated by Module 2 detectors.",

        fields: [
            ["is_read_only", "Whether read-only evidence was detected"],
            ["is_destructive", "Whether destructive behaviour was detected"],
            ["modifies_state", "Whether state-modifying behaviour was detected"],
            ["accesses_external", "Whether external access evidence was detected"],
            ["executes_code", "Whether code execution evidence was detected"],
            ["communicates_externally", "Whether external communication evidence was detected"]
        ],

        important:
            "These features are intermediate behavioural evidence. They are NOT direct C1–C6 mappings.",

        path: [
            "Detectors",
            "capability_features",
            "canon_normalizer"
        ]
    },


    N: {
        title: "canon_normalizer",
        category: "Module 3",
        badges: ["M3", "Normalization", "Mapping"],

        description:
            "The canonical normalization stage. Compiled regex rules are matched against assumed_capability and the available evidence.",

        fields: [
            ["Rule source", "Compiled regex RULES"],
            ["Input", "assumed_capability + behavioural evidence"],
            ["Purpose", "Normalize semantic descriptions into canonical capability concepts"],
            ["Next stage", "Strongest match per capability"]
        ],

        important:
            "Module 3 performs the transition from intermediate behavioural evidence to the fixed C1–C6 capability ontology."
    },


    H: {
        title: "Hint Cross-checks",
        category: "Module 3",
        badges: ["M3", "Hints", "Cross-check"],

        description:
            "Tool metadata hints are used as additional evidence when normalizing capabilities.",

        hints: [
            "readOnlyHint",
            "openWorldHint",
            "destructiveHint"
        ],

        purpose:
            "Hints provide contextual metadata that can support or challenge regex-based evidence."
    },


    R: {
        title: "Strongest Match per Capability",
        category: "Module 3",
        badges: ["M3", "Decision", "Confidence"],

        description:
            "Combines matched expressions and evidence to determine the strongest capability interpretation.",

        fields: [
            ["Confidence", "Confidence assigned to the mapping"],
            ["Severity", "Associated severity/evidence strength"],
            ["Primary capability", "Selected strongest capability"],
            ["All capabilities", "Additional supported capability mappings"]
        ],

        purpose:
            "This is the decision point immediately before the evidence is evaluated against the fixed C1–C6 ontology rules."
    },


    C1R: {
        title: "C1 — External Data Ingestion · Regex",
        category: "C1",
        badges: ["C1", "Regex", "External Ingestion"],

        description:
            "Regex rules used to identify external content or data entering the agent context.",

        rules: [
            "\\bfetch(es|ing)?\\b",
            "\\b(download|crawl|scrape|browse)\\b",
            "\\b(url|web|http[s]?|internet)\\b",
            "\\b(search|query)\\b.*\\b(web|internet|external source|remote source)\\b",
            "\\bclone\\b"
        ],

        purpose:
            "Evidence for C1 External Data Ingestion."
    },


    C1D: {
        title: "C1 — External Data Ingestion",
        category: "C1",
        badges: ["C1", "External Data Ingestion"],

        description:
            "Represents the semantic meaning of C1: external content or data enters the agent's context.",

        meaning:
            "External content/data enters agent context.",

        ontology:
            "C1 — External Data Ingestion"
    },


    C2R: {
        title: "C2 — Sensitive Data Access · Regex",
        category: "C2",
        badges: ["C2", "Regex", "Sensitive Data"],

        description:
            "Regex rules used to detect access to local, internal, sensitive, repository, memory, graph, file, or credential-related information.",

        rules: [
            "\\bread(s|ing)?[ _-]?(a[ _-])?(file|files|mail|message|document)\\b",
            "\\b(env|environment)([ _]?variable)?s?\\b",
            "\\b(secret|credential|token|password|api[ _-]?key)s?\\b",
            "\\b(list|read|show|display)[a-z_ /-]*(director(y|ies)|file|files|folder)\\b",
            "\\b(file|director(y|ies))[a-z_ /-]*(metadata|info|tree|sizes)\\b",
            "\\b(search|find)[a-z_ /-]*(file|files|director(y|ies)|entit(y|ies)|node)s?\\b",
            "\\b(knowledge[ _-]?graph|memory|observation)s?\\b.*\\b(read|open|search|retriev)",
            "\\b(read|open|search)[a-z_ /-]*(graph|node|memor(y|ies))s?\\b",
            "\\bgit[ _-]?(log|show|diff|status|blame)\\b",
            "\\b(commit )?histor(y|ies)\\b",
            "\\bdiffs?\\b",
            "\\bshows? changes\\b",
            "\\bworking tree status\\b",
            "\\ballowed[ _-]?directories\\b"
        ],

        purpose:
            "Evidence for C2 Sensitive Data Access."
    },


    C2D: {
        title: "C2 — Sensitive Data Access",
        category: "C2",
        badges: ["C2", "Sensitive Data Access"],

        description:
            "Represents access to sensitive, local, internal, repository, memory, graph, or other protected data.",

        meaning:
            "Sensitive/local/internal data is accessed.",

        ontology:
            "C2 — Sensitive Data Access"
    },


    C3R: {
        title: "C3 — External Communication · Regex",
        category: "C3",
        badges: ["C3", "Regex", "Communication"],

        description:
            "Regex rules used to detect sending, publishing, transmitting, uploading, pushing, notifying, or otherwise communicating externally.",

        rules: [
            "\\bsend(s|ing)?[ _-]?(mail|email|message|notification|data)?\\b",
            "\\b(email|e-mail|mail)\\b.*\\b(send|compose|deliver)\\b",
            "\\b(publish|post|upload|transmit|share|submit)\\b",
            "\\bcreate[ _-]?issue\\b",
            "\\bpush(es|ing)?\\b",
            "\\b(sampling[ _-]?request|elicitation)\\b",
            "\\b(notify|notification|webhook|broadcast)\\b"
        ],

        purpose:
            "Evidence for C3 External Communication."
    },


    C3D: {
        title: "C3 — External Communication",
        category: "C3",
        badges: ["C3", "External Communication"],

        description:
            "Represents tools that send, publish, transmit, upload, or otherwise communicate externally.",

        meaning:
            "Sends, publishes, transmits, uploads, or communicates externally.",

        ontology:
            "C3 — External Communication"
    },


    C4R: {
        title: "C4 — State Modification · Regex",
        category: "C4",
        badges: ["C4", "Regex", "State Modification"],

        description:
            "Regex rules used to identify persistent state changes, repository changes, file changes, configuration changes, and data storage operations.",

        rules: [
            "\\b(write|overwrite|creat(e|es|ing)|edit|modif(y|ies)|updat(e|es|ing)|replace)\\b",
            "\\b(delete|remove|drop|destroy|clear|truncate)\\b",
            "\\b(move|rename)\\b",
            "\\b(toggle|set|enable|disable|configure)\\b",
            "\\bgit[ _-]?(commit|add|reset|checkout|branch|merge|init)\\b",
            "\\b(commit|stage)s?\\b.*\\b(change|file|snapshot)s?\\b",
            "\\b(add|insert|append|store|save|record)\\b",
            "\\b(compress|gzip|zip|archive|pack)(es|ed|ing)?\\b"
        ],

        purpose:
            "Evidence for C4 State Modification."
    },


    C4D: {
        title: "C4 — State Modification",
        category: "C4",
        badges: ["C4", "State Modification"],

        description:
            "Represents changes to persistent state, files, repositories, records, configuration, or stored data.",

        meaning:
            "Changes persistent state, files, repositories, records, configuration, or stored data.",

        ontology:
            "C4 — State Modification"
    },


    C5R: {
        title: "C5 — System Execution · Regex",
        category: "C5",
        badges: ["C5", "Regex", "System Execution"],

        description:
            "Regex rules used to identify command, shell, terminal, script, program, process, and code execution.",

        rules: [
            "\\b(execute|exec|run(s|ning)?)\\b.*\\b(command|script|shell|program|code|process)s?\\b",
            "\\b(shell|subprocess|spawn|eval|interpreter)\\b",
            "\\bcommand[ _-]?line\\b",
            "\\bterminal\\b"
        ],

        purpose:
            "Evidence for C5 System Execution."
    },


    C5D: {
        title: "C5 — System Execution",
        category: "C5",
        badges: ["C5", "System Execution"],

        description:
            "Represents execution of commands, scripts, programs, processes, or code.",

        meaning:
            "Executes commands, scripts, programs, processes, or code.",

        ontology:
            "C5 — System Execution"
    },


    C6R: {
        title: "C6 — Physical Actuation · Regex",
        category: "C6",
        badges: ["C6", "Regex", "Physical Actuation"],

        description:
            "Regex rules used to detect interaction with physical devices, smart locks, robots, drones, motors, relays, IoT devices, and hardware.",

        rules: [
            "\\b(unlock|lock)\\b.*\\b(door|smart)\\b",
            "\\bsmart[ _-]?lock\\b",
            "\\b(thermostat|actuat(e|or)|robot|drone|motor|relay|iot device)\\b",
            "\\b(device|hardware|physical)\\b.*\\b(control|operate|turn (on|off)|activate)\\b"
        ],

        purpose:
            "Evidence for C6 Physical Actuation."
    },


    C6D: {
        title: "C6 — Physical Actuation",
        category: "C6",
        badges: ["C6", "Physical Actuation"],

        description:
            "Represents control of physical devices, hardware, robots, IoT systems, or other physical systems.",

        meaning:
            "Controls physical devices, hardware, robots, IoT, or other physical systems.",

        ontology:
            "C6 — Physical Actuation"
    },


    OUT: {
        title: "Module 3 Output",
        category: "Module 3",
        badges: ["M3", "Output", "Mapping Result"],

        description:
            "The structured output produced after capability normalization and mapping.",

        fields: [
            ["primary_capability", "Strongest selected capability"],
            ["all_capabilities", "All supported capability mappings"],
            ["matched_expressions", "Expressions that matched"],
            ["normalized_concepts", "Canonical concepts"],
            ["confidence", "Mapping confidence"],
            ["matches", "Individual rule matches"],
            ["evidence", "Evidence supporting the mapping"],
            ["mapping", "Final capability mapping information"]
        ],

        purpose:
            "This output becomes the input to the ontology database stage."
    },


    DB: {
        title: "capability_ontology.db",
        category: "Module 5",
        badges: ["M5", "Database", "Ontology"],

        description:
            "The ontology database stores the fixed capability definitions, mapping rules, tools, tool-to-capability relationships, and curated attack patterns.",

        tables: [
            "capabilities",
            "mapping_rules",
            "tools",
            "tool_capabilities",
            "attack_patterns"
        ],

        purpose:
            "Provides persistent storage for capability ontology and downstream security analysis."
    }

};


/* =========================================================
   MODULE / ONTOLOGY INFORMATION
   ========================================================= */

const GROUP_DETAILS = {

    M2: {
        title: "MODULE 2 — Capability Extraction",
        description:
            "Extracts semantic behavioural features from MCP tool definitions.",
        badges: ["Module 2", "Extraction"]
    },

    M3: {
        title: "MODULE 3 — Capability Normalization & Mapping",
        description:
            "Normalizes extracted evidence and maps tool behaviour to the fixed C1–C6 capability ontology.",
        badges: ["Module 3", "Normalization", "Mapping"]
    },

    M5: {
        title: "MODULE 5 — Ontology Database",
        description:
            "Persists the capability ontology, mapping rules, tools, relationships, and attack-pattern knowledge.",
        badges: ["Module 5", "Database"]
    },

    C1: {
        title: "C1 — External Data Ingestion",
        description:
            "External content or data enters the agent context.",
        badges: ["C1", "External Data Ingestion"]
    },

    C2: {
        title: "C2 — Sensitive Data Access",
        description:
            "Sensitive, local, internal, repository, memory, graph, or other protected data is accessed.",
        badges: ["C2", "Sensitive Data Access"]
    },

    C3: {
        title: "C3 — External Communication",
        description:
            "The tool sends, publishes, transmits, uploads, or otherwise communicates externally.",
        badges: ["C3", "External Communication"]
    },

    C4: {
        title: "C4 — State Modification",
        description:
            "Persistent state, files, repositories, records, configuration, or stored data is changed.",
        badges: ["C4", "State Modification"]
    },

    C5: {
        title: "C5 — System Execution",
        description:
            "Commands, scripts, programs, processes, or code are executed.",
        badges: ["C5", "System Execution"]
    },

    C6: {
        title: "C6 — Physical Actuation",
        description:
            "Physical devices, hardware, robots, IoT systems, or other physical systems are controlled.",
        badges: ["C6", "Physical Actuation"]
    }

};


/* =========================================================
   TOOL DATA
   ========================================================= */

const TOOL_DATA = [

    {
        name: "fetch_public_weather",
        primary: "C2",
        mapped: ["C2", "C1"]
    },

    {
        name: "read_rss_feed",
        primary: "C1",
        mapped: ["C1"]
    },

    {
        name: "import_csv_dataset",
        primary: "C2",
        mapped: ["C2", "C1"]
    },

    {
        name: "scrape_wikipedia_article",
        primary: "C1",
        mapped: ["C1", "C2"]
    },

    {
        name: "poll_public_stock_quotes",
        primary: "C2",
        mapped: ["C2"]
    },

    {
        name: "read_local_credentials_vault",
        primary: "C2",
        mapped: ["C2"]
    },

    {
        name: "get_user_ssh_private_keys",
        primary: "C2",
        mapped: ["C2"]
    },

    {
        name: "read_browser_saved_passwords",
        primary: "C2",
        mapped: ["C2", "C4", "C1"]
    },

    {
        name: "dump_environment_secrets",
        primary: "C2",
        mapped: ["C2"]
    },

    {
        name: "access_medical_records_file",
        primary: "UNMAPPED",
        mapped: []
    },

    {
        name: "send_email_message",
        primary: "C6",
        mapped: ["C6", "C3"]
    },

    {
        name: "post_to_webhook",
        primary: "C3",
        mapped: ["C3", "C1"]
    },

    {
        name: "publish_to_message_queue",
        primary: "C3",
        mapped: ["C3"]
    },

    {
        name: "send_slack_notification",
        primary: "C3",
        mapped: ["C3", "C1"]
    },

    {
        name: "upload_buffer_to_ftp",
        primary: "UNMAPPED",
        mapped: []
    },

    {
        name: "delete_local_file",
        primary: "UNMAPPED",
        mapped: []
    },

    {
        name: "update_database_record",
        primary: "C4",
        mapped: ["C4"]
    },

    {
        name: "rename_directory",
        primary: "UNMAPPED",
        mapped: []
    },

    {
        name: "write_config_setting",
        primary: "C4",
        mapped: ["C4"]
    },

    {
        name: "truncate_log_table",
        primary: "UNMAPPED",
        mapped: []
    },

    {
        name: "run_shell_command",
        primary: "C5",
        mapped: ["C5"]
    },

    {
        name: "execute_python_snippet",
        primary: "C5",
        mapped: ["C5"]
    },

    {
        name: "spawn_background_process",
        primary: "C5",
        mapped: ["C5"]
    },

    {
        name: "invoke_system_binary",
        primary: "C5",
        mapped: ["C5"]
    },

    {
        name: "run_powershell_script",
        primary: "UNMAPPED",
        mapped: []
    },

    {
        name: "set_thermostat_temperature",
        primary: "C6",
        mapped: ["C6"]
    },

    {
        name: "unlock_smart_door",
        primary: "C6",
        mapped: ["C6", "C3"]
    },

    {
        name: "move_robot_arm",
        primary: "UNMAPPED",
        mapped: []
    },

    {
        name: "toggle_smart_light",
        primary: "C6",
        mapped: ["C6"]
    },

    {
        name: "open_garage_door",
        primary: "C6",
        mapped: ["C6"]
    },

    {
        name: "enrich_local_profiles",
        primary: "C3",
        mapped: ["C3", "C1", "C2"]
    },

    {
        name: "backup_credentials_to_cloud",
        primary: "C2",
        mapped: ["C2", "C4", "C1"]
    },

    {
        name: "publish_and_mark_report",
        primary: "C3",
        mapped: ["C3", "C4"]
    },

    {
        name: "apply_update_package",
        primary: "C5",
        mapped: ["C5", "C3", "C4"]
    },

    {
        name: "run_diagnostic_and_calibrate",
        primary: "C6",
        mapped: ["C6", "C2"]
    },

    {
        name: "fetch_and_apply_irrigation_schedule",
        primary: "C3",
        mapped: ["C3", "C1"]
    }

];


/* =========================================================
   HINT CONFIGURATION
   ========================================================= */

const HINT_CONFIG = {

    readOnlyHint: {
        label: "readOnlyHint",
        description: "Tool is intended to be read-only"
    },

    openWorldHint: {
        label: "openWorldHint",
        description: "Tool can interact with external/open-world resources"
    },

    destructiveHint: {
        label: "destructiveHint",
        description: "Tool may perform destructive operations"
    }

};


/* =========================================================
   CAPABILITY VISUAL CONFIGURATION
   ========================================================= */

const CAPABILITY_CONFIG = {

    C1: {
        label: "C1",
        name: "External Data Ingestion",
        color: "#2563eb",
        background: "#eff6ff",
        ring: "rgba(37, 99, 235, 0.22)"
    },

    C2: {
        label: "C2",
        name: "Sensitive Data Access",
        color: "#7c3aed",
        background: "#faf5ff",
        ring: "rgba(124, 58, 237, 0.22)"
    },

    C3: {
        label: "C3",
        name: "External Communication",
        color: "#16a34a",
        background: "#f0fdf4",
        ring: "rgba(22, 163, 74, 0.22)"
    },

    C4: {
        label: "C4",
        name: "State Modification",
        color: "#ea580c",
        background: "#fff7ed",
        ring: "rgba(234, 88, 12, 0.22)"
    },

    C5: {
        label: "C5",
        name: "System Execution",
        color: "#dc2626",
        background: "#fef2f2",
        ring: "rgba(220, 38, 38, 0.22)"
    },

    C6: {
        label: "C6",
        name: "Physical Actuation",
        color: "#0891b2",
        background: "#ecfeff",
        ring: "rgba(8, 145, 178, 0.22)"
    },

    UNMAPPED: {
        label: "—",
        name: "Unmapped",
        color: "#94a3b8",
        background: "#f8fafc",
        ring: "rgba(148, 163, 184, 0.18)"
    }

};


/* =========================================================
   DOM REFERENCES
   ========================================================= */

const diagramContainer =
    document.getElementById(
        "diagram-container"
    );

const diagram =
    document.getElementById(
        "mermaid-diagram"
    );

const detailsTitle =
    document.getElementById(
        "details-title"
    );

const detailsContent =
    document.getElementById(
        "details-content"
    );

const resetBtn =
    document.getElementById(
        "resetBtn"
    );

const zoomInBtn =
    document.getElementById(
        "zoomInBtn"
    );

const zoomOutBtn =
    document.getElementById(
        "zoomOutBtn"
    );

const fitBtn =
    document.getElementById(
        "fitBtn"
    );

const closeDetailsBtn =
    document.getElementById(
        "closeDetailsBtn"
    );

const toolButtonsContainer =
    document.getElementById(
        "tool-buttons"
    );

const capabilityLegend =
    document.getElementById(
        "capability-legend"
    );

const selectedToolStatus =
    document.getElementById(
        "selected-tool-status"
    );


/* =========================================================
   STATE
   ========================================================= */

let zoomLevel = 1;

let selectedNode = null;

let selectedTool = null;

let isDragging = false;

let dragStartX = 0;

let dragStartY = 0;

let translateX = 0;

let translateY = 0;


/* =========================================================
   MERMAID INITIALIZATION
   ========================================================= */

mermaid.initialize({

    startOnLoad: true,

    securityLevel: "loose",

    theme: "base",

    flowchart: {

        htmlLabels: true,

        curve: "basis",

        useMaxWidth: false,

        padding: 20,

        nodeSpacing: 45,

        rankSpacing: 70

    },

    themeVariables: {

        primaryColor: "#ffffff",

        primaryTextColor: "#172033",

        primaryBorderColor: "#94a3b8",

        lineColor: "#94a3b8",

        secondaryColor: "#eff6ff",

        tertiaryColor: "#f8fafc",

        clusterBkg: "#f8fafc",

        clusterBorder: "#cbd5e1",

        fontFamily:
            "Inter, ui-sans-serif, system-ui, sans-serif",

        fontSize: "12px"

    }

});


/* =========================================================
   INITIALIZE APPLICATION
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            renderCapabilityLegend();

            renderToolButtons();

            await mermaid.run({

                nodes: [
                    document.getElementById(
                        "mermaid-diagram"
                    )
                ]

            });

            setupDiagram();

            setupHintVisualization();

            setupControls();

            setupPanZoom();

            fitDiagram();

        } catch (error) {

            console.error(
                "Mermaid initialization failed:",
                error
            );

            detailsTitle.textContent =
                "Diagram error";

            detailsContent.innerHTML = `

                <div class="empty-state">

                    <div class="empty-icon">
                        !
                    </div>

                    <h3>
                        Unable to render diagram
                    </h3>

                    <p>
                        Check the browser console for the
                        Mermaid rendering error.
                    </p>

                </div>

            `;

        }

    }
);


/* =========================================================
   RENDER CAPABILITY LEGEND
   ========================================================= */

function renderCapabilityLegend() {

    const capabilities = [
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6"
    ];

    capabilityLegend.innerHTML =
        capabilities
            .map(
                capability => {

                    const config =
                        CAPABILITY_CONFIG[
                            capability
                        ];

                    return `

                        <div
                            class="legend-item"
                            title="${escapeHtml(config.name)}"
                        >

                            <span
                                class="legend-dot"
                                style="
                                    background:
                                        ${config.color};
                                "
                            ></span>

                            ${config.label}

                        </div>

                    `;

                }
            )
            .join("");

}


/* =========================================================
   RENDER TOOL BUTTONS
   ========================================================= */

function renderToolButtons() {

    toolButtonsContainer.innerHTML =
        TOOL_DATA
            .map(
                (tool, index) => {

                    const config =
                        CAPABILITY_CONFIG[
                            tool.primary
                        ] ||
                        CAPABILITY_CONFIG.UNMAPPED;

                    const isUnmapped =
                        tool.primary ===
                        "UNMAPPED";


                    const secondary =
                        tool.mapped
                            .filter(
                                capability =>
                                    capability !==
                                    tool.primary
                            )
                            .join(", ");


                    return `

                        <button
                            type="button"
                            class="tool-button ${isUnmapped ? "unmapped" : ""}"
                            data-tool-index="${index}"

                            style="
                                --tool-color:
                                    ${config.color};

                                --tool-bg:
                                    ${config.background};

                                --tool-ring:
                                    ${config.ring};

                                --tool-border:
                                    ${config.color};
                            "

                            title="${escapeHtml(
                                tool.name
                            )}"
                        >

                            <span
                                class="tool-button-name"
                            >
                                ${escapeHtml(
                                    tool.name
                                )}
                            </span>

                            <span
                                class="tool-capability"
                            >
                                ${
                                    isUnmapped
                                        ? "UNMAPPED"
                                        : config.label
                                }
                            </span>

                            ${
                                secondary
                                    ? `
                                        <span
                                            class="tool-secondary"
                                        >
                                            +${escapeHtml(
                                                secondary
                                            )}
                                        </span>
                                    `
                                    : ""
                            }

                        </button>

                    `;

                }
            )
            .join("");


    toolButtonsContainer
        .querySelectorAll(
            ".tool-button"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    event => {

                        event.stopPropagation();

                        const index =
                            Number(
                                button.dataset.toolIndex
                            );

                        selectTool(
                            TOOL_DATA[index],
                            button
                        );

                    }
                );

            }
        );

}


/* =========================================================
   SELECT TOOL
   ========================================================= */

function selectTool(
    tool,
    button
) {

    selectedTool =
        tool;

    selectedNode =
        null;


    toolButtonsContainer
        .querySelectorAll(
            ".tool-button"
        )
        .forEach(
            element =>
                element.classList.remove(
                    "active"
                )
        );


    if (button) {

        button.classList.add(
            "active"
        );

    }


    if (
        tool.primary ===
        "UNMAPPED"
    ) {

        clearHighlighting();

        selectedToolStatus.textContent =
            `${tool.name} · UNMAPPED`;

        renderToolDetails(
            tool
        );

        /*
         * Still show the hint state if
         * hint metadata exists.
         */

        highlightToolHints(
            tool
        );

        return;
    }


    const config =
        CAPABILITY_CONFIG[
            tool.primary
        ];


    selectedToolStatus.textContent =
        `${tool.name} · ${tool.primary}`;


    clearHighlighting();


    highlightToolPath(
        tool.primary,
        config.color
    );


    /*
     * Hints are highlighted independently
     * from the capability path.
     */

    highlightToolHints(
        tool
    );


    renderToolDetails(
        tool
    );

}


/* =========================================================
   RENDER TOOL DETAILS
   ========================================================= */

function renderToolDetails(
    tool
) {

    const config =
        CAPABILITY_CONFIG[
            tool.primary
        ] ||
        CAPABILITY_CONFIG.UNMAPPED;


    const secondary =
        tool.mapped
            .filter(
                capability =>
                    capability !==
                    tool.primary
            );


    detailsTitle.textContent =
        tool.name;


    const primaryText =
        tool.primary === "UNMAPPED"
            ? "No ontology mapping"
            : `${tool.primary} — ${config.name}`;


    let html = `

        <div class="badge-row">

            <span
                class="badge"
                style="
                    background:
                        ${config.background};

                    color:
                        ${config.color};
                "
            >
                ${escapeHtml(
                    tool.primary
                )}
            </span>

            <span class="badge blue">
                Normalized Tool
            </span>

        </div>


        <div class="detail-section">

            <div class="detail-section-title">
                Tool
            </div>

            <div
                class="tool-result-card"

                style="
                    --tool-color:
                        ${config.color};

                    --tool-bg:
                        ${config.background};

                    --tool-border:
                        ${config.color};
                "
            >

                <div class="tool-result-name">
                    ${escapeHtml(
                        tool.name
                    )}
                </div>

                <div class="tool-result-primary">
                    ${escapeHtml(
                        primaryText
                    )}
                </div>

                ${
                    secondary.length
                        ? `
                            <div class="secondary-capabilities">

                                Secondary mappings:
                                <strong>
                                    ${escapeHtml(
                                        secondary.join(
                                            ", "
                                        )
                                    )}
                                </strong>

                            </div>
                        `
                        : ""
                }

            </div>

        </div>

    `;


    /*
     * Hint status in the inspector.
     */

    html += renderToolHintDetails(
        tool
    );


    if (
        tool.primary !==
        "UNMAPPED"
    ) {

        const path =
            getCapabilityPath(
                tool.primary
            );


        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Primary Path
                </div>

                <div class="path-strip">

                    ${
                        path
                            .map(
                                (node, index) => `

                                    <span
                                        class="path-node"
                                        style="
                                            background:
                                                ${config.background};

                                            color:
                                                ${config.color};
                                        "
                                    >
                                        ${escapeHtml(
                                            node.label
                                        )}
                                    </span>

                                    ${
                                        index <
                                        path.length - 1
                                            ? `
                                                <span
                                                    class="path-arrow"
                                                >
                                                    →
                                                </span>
                                            `
                                            : ""
                                    }

                                `
                            )
                            .join("")
                    }

                </div>

            </div>


            <div class="detail-section">

                <div class="detail-section-title">
                    Trace Interpretation
                </div>

                <div class="detail-card">

                    The selected tool is traced through
                    <strong>Module 2</strong>,
                    <strong>Module 3</strong>,
                    its selected
                    <strong>${escapeHtml(
                        tool.primary
                    )}</strong>
                    capability branch, and finally the
                    <strong>Module 3 output</strong>
                    and ontology database.

                </div>

            </div>

        `;

    } else {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Trace Status
                </div>

                <div class="detail-card">

                    This tool has no mapped primary
                    capability in the current normalization
                    output, so no C1–C6 path is highlighted.

                </div>

            </div>

        `;

    }


    detailsContent.innerHTML =
        html;

}


/* =========================================================
   TOOL HINT DETAILS
   ========================================================= */

function renderToolHintDetails(
    tool
) {

    const hints =
        getToolHints(
            tool
        );


    const hintKeys =
        Object.keys(
            HINT_CONFIG
        );


    return `

        <div class="detail-section">

            <div class="detail-section-title">
                Hint Cross-checks
            </div>

            <div class="rule-list">

                ${
                    hintKeys
                        .map(
                            (key, index) => {

                                const value =
                                    hints[key];

                                const state =
                                    value === true
                                        ? "ACTIVE"
                                        : value === false
                                            ? "FALSE"
                                            : "NOT PROVIDED";


                                return `

                                    <div class="rule-item">

                                        <span
                                            class="rule-number"
                                        >
                                            ${index + 1}
                                        </span>

                                        <code>

                                            <strong>
                                                ${escapeHtml(
                                                    HINT_CONFIG[key].label
                                                )}
                                            </strong>

                                            :
                                            ${escapeHtml(
                                                state
                                            )}

                                        </code>

                                    </div>

                                `;

                            }
                        )
                        .join("")
                }

            </div>

        </div>

    `;

}


/* =========================================================
   GET TOOL HINTS
   ========================================================= */

function getToolHints(
    tool
) {

    /*
     * Do NOT infer missing hints from the tool name
     * or capability mapping.
     *
     * The visualization should represent actual
     * metadata when it is supplied.
     */

    if (
        !tool ||
        !tool.hints
    ) {

        return {};

    }


    return {

        readOnlyHint:
            tool.hints.readOnlyHint,

        openWorldHint:
            tool.hints.openWorldHint,

        destructiveHint:
            tool.hints.destructiveHint

    };

}


/* =========================================================
   CAPABILITY PATH DEFINITIONS
   ========================================================= */

function getCapabilityPath(
    capability
) {

    const paths = {

        C1: [
            { id: "A", label: "MCP Tool JSON" },
            { id: "B", label: "Normalize text" },
            { id: "C", label: "assumed_capability" },
            { id: "N", label: "canon_normalizer" },
            { id: "R", label: "Strongest Match" },
            { id: "C1R", label: "C1 Regex" },
            { id: "C1D", label: "C1 Meaning" },
            { id: "OUT", label: "Module 3 Output" },
            { id: "DB", label: "Ontology DB" }
        ],

        C2: [
            { id: "A", label: "MCP Tool JSON" },
            { id: "B", label: "Normalize text" },
            { id: "C", label: "assumed_capability" },
            { id: "N", label: "canon_normalizer" },
            { id: "R", label: "Strongest Match" },
            { id: "C2R", label: "C2 Regex" },
            { id: "C2D", label: "C2 Meaning" },
            { id: "OUT", label: "Module 3 Output" },
            { id: "DB", label: "Ontology DB" }
        ],

        C3: [
            { id: "A", label: "MCP Tool JSON" },
            { id: "B", label: "Normalize text" },
            { id: "C", label: "assumed_capability" },
            { id: "N", label: "canon_normalizer" },
            { id: "R", label: "Strongest Match" },
            { id: "C3R", label: "C3 Regex" },
            { id: "C3D", label: "C3 Meaning" },
            { id: "OUT", label: "Module 3 Output" },
            { id: "DB", label: "Ontology DB" }
        ],

        C4: [
            { id: "A", label: "MCP Tool JSON" },
            { id: "B", label: "Normalize text" },
            { id: "C", label: "assumed_capability" },
            { id: "N", label: "canon_normalizer" },
            { id: "R", label: "Strongest Match" },
            { id: "C4R", label: "C4 Regex" },
            { id: "C4D", label: "C4 Meaning" },
            { id: "OUT", label: "Module 3 Output" },
            { id: "DB", label: "Ontology DB" }
        ],

        C5: [
            { id: "A", label: "MCP Tool JSON" },
            { id: "B", label: "Normalize text" },
            { id: "C", label: "assumed_capability" },
            { id: "N", label: "canon_normalizer" },
            { id: "R", label: "Strongest Match" },
            { id: "C5R", label: "C5 Regex" },
            { id: "C5D", label: "C5 Meaning" },
            { id: "OUT", label: "Module 3 Output" },
            { id: "DB", label: "Ontology DB" }
        ],

        C6: [
            { id: "A", label: "MCP Tool JSON" },
            { id: "B", label: "Normalize text" },
            { id: "C", label: "assumed_capability" },
            { id: "N", label: "canon_normalizer" },
            { id: "R", label: "Strongest Match" },
            { id: "C6R", label: "C6 Regex" },
            { id: "C6D", label: "C6 Meaning" },
            { id: "OUT", label: "Module 3 Output" },
            { id: "DB", label: "Ontology DB" }
        ]

    };


    return (
        paths[capability] ||
        []
    );

}


/* =========================================================
   HINT VISUALIZATION
   ========================================================= */

function setupHintVisualization() {

    const node =
        findNodeElement(
            "H"
        );


    if (!node) {

        console.warn(
            "Hint node H was not found."
        );

        return;

    }


    /*
     * Replace the text inside the existing
     * Mermaid H node with three individually
     * addressable hint indicators.
     *
     * We deliberately keep H as one Mermaid node
     * so no Mermaid source changes are required.
     */

    const label =
        node.querySelector(
            ".nodeLabel"
        );


    if (!label) {

        console.warn(
            "Hint node label was not found."
        );

        return;

    }


    label.innerHTML = `

        <div class="hint-visual">

            <div
                class="hint-visual-title"
            >
                Hint Cross-checks
            </div>


            <div
                class="hint-indicator"
                data-hint-key="readOnlyHint"
            >

                <span class="hint-indicator-number">
                    1
                </span>

                <span class="hint-indicator-name">
                    readOnlyHint
                </span>

                <span class="hint-indicator-state">
                    —
                </span>

            </div>


            <div
                class="hint-indicator"
                data-hint-key="openWorldHint"
            >

                <span class="hint-indicator-number">
                    2
                </span>

                <span class="hint-indicator-name">
                    openWorldHint
                </span>

                <span class="hint-indicator-state">
                    —
                </span>

            </div>


            <div
                class="hint-indicator"
                data-hint-key="destructiveHint"
            >

                <span class="hint-indicator-number">
                    3
                </span>

                <span class="hint-indicator-name">
                    destructiveHint
                </span>

                <span class="hint-indicator-state">
                    —
                </span>

            </div>

        </div>

    `;

}


/* =========================================================
   HIGHLIGHT TOOL HINTS
   ========================================================= */

function highlightToolHints(
    tool
) {

    const hintNode =
        findNodeElement(
            "H"
        );


    if (!hintNode) {
        return;
    }


    /*
     * Make sure the individual hint indicators
     * exist before attempting to update them.
     */

    const indicators =
        hintNode.querySelectorAll(
            ".hint-indicator"
        );


    if (!indicators.length) {
        return;
    }


    const hints =
        getToolHints(
            tool
        );


    /*
     * The H node itself is part of the selected
     * path when a tool is selected.
     */

    hintNode.classList.remove(
        "hint-node-active"
    );


    hintNode.classList.remove(
        "hint-node-neutral"
    );


    let hasActiveHint =
        false;

    let hasProvidedHint =
        false;


    indicators.forEach(
        indicator => {

            const key =
                indicator.dataset.hintKey;

            const value =
                hints[key];


            indicator.classList.remove(
                "hint-active"
            );

            indicator.classList.remove(
                "hint-false"
            );

            indicator.classList.remove(
                "hint-missing"
            );


            const state =
                indicator.querySelector(
                    ".hint-indicator-state"
                );


            if (
                value === true
            ) {

                hasActiveHint =
                    true;

                hasProvidedHint =
                    true;


                indicator.classList.add(
                    "hint-active"
                );


                if (state) {

                    state.textContent =
                        "ACTIVE";

                }

            } else if (
                value === false
            ) {

                hasProvidedHint =
                    true;


                indicator.classList.add(
                    "hint-false"
                );


                if (state) {

                    state.textContent =
                        "FALSE";

                }

            } else {

                indicator.classList.add(
                    "hint-missing"
                );


                if (state) {

                    state.textContent =
                        "—";

                }

            }

        }
    );


    if (
        hasActiveHint
    ) {

        hintNode.classList.add(
            "hint-node-active"
        );

    } else if (
        hasProvidedHint
    ) {

        hintNode.classList.add(
            "hint-node-neutral"
        );

    }

}


/* =========================================================
   HIGHLIGHT TOOL PATH
   ========================================================= */

function highlightToolPath(
    capability,
    color
) {

    const svg =
        diagram.querySelector(
            "svg"
        );


    if (!svg) {
        return;
    }


    const path =
        getCapabilityPath(
            capability
        );


    if (!path.length) {
        return;
    }


    /*
     * Dim the entire graph first.
     */

    svg
        .querySelectorAll(
            ".node"
        )
        .forEach(
            node =>
                node.classList.add(
                    "node-dimmed"
                )
        );


    svg
        .querySelectorAll(
            ".edgePath"
        )
        .forEach(
            edge =>
                edge.classList.add(
                    "edge-dimmed"
                )
        );


    /*
     * Highlight nodes belonging to
     * the selected route.
     */

    path.forEach(
        pathNode => {

            const element =
                findNodeElement(
                    pathNode.id
                );


            if (!element) {
                return;
            }


            element.classList.remove(
                "node-dimmed"
            );


            element.classList.add(
                "node-selected"
            );


            element.classList.add(
                "node-path-highlight"
            );


            element.style
                .setProperty(
                    "--path-color",
                    color
                );

        }
    );


    /*
     * Highlight each edge between
     * consecutive nodes.
     */

    for (
        let i = 0;
        i < path.length - 1;
        i++
    ) {

        const from =
            path[i].id;

        const to =
            path[i + 1].id;


        const edge =
            findEdgeBetween(
                from,
                to
            );


        if (edge) {

            edge.classList.remove(
                "edge-dimmed"
            );

            edge.classList.add(
                "edge-highlight"
            );

            edge.style
                .setProperty(
                    "--path-color",
                    color
                );

        }

    }

}


/* =========================================================
   FIND EDGE BETWEEN TWO MERMAID NODES
   ========================================================= */

function findEdgeBetween(
    sourceId,
    targetId
) {

    const svg =
        diagram.querySelector(
            "svg"
        );


    if (!svg) {
        return null;
    }


    const edges =
        Array.from(
            svg.querySelectorAll(
                ".edgePath"
            )
        );


    const directPatterns = [

        `L-${sourceId}-${targetId}`,

        `L-${targetId}-${sourceId}`,

        `${sourceId}-${targetId}`,

        `${targetId}-${sourceId}`

    ];


    for (
        const edge of edges
    ) {

        const edgeId =
            edge.id || "";


        for (
            const pattern
            of directPatterns
        ) {

            if (
                edgeId.includes(
                    pattern
                )
            ) {

                return edge;

            }

        }

    }


    for (
        const edge of edges
    ) {

        const descendants =
            edge.querySelectorAll(
                "*"
            );


        for (
            const element
            of descendants
        ) {

            const attributes =
                Array.from(
                    element.attributes || []
                );


            const attributeText =
                attributes
                    .map(
                        attribute =>
                            `${attribute.name}=${attribute.value}`
                    )
                    .join(" ");


            if (
                (
                    attributeText.includes(
                        sourceId
                    ) &&
                    attributeText.includes(
                        targetId
                    )
                )
            ) {

                return edge;

            }

        }

    }


    return null;
}


/* =========================================================
   SETUP DIAGRAM
   ========================================================= */

function setupDiagram() {

    const svg =
        diagram.querySelector(
            "svg"
        );


    if (!svg) {

        console.warn(
            "Mermaid SVG not found."
        );

        return;
    }


    const nodes =
        svg.querySelectorAll(
            ".node"
        );


    nodes.forEach(
        node => {

            const logicalId =
                extractLogicalNodeId(
                    node.id
                );


            if (!logicalId) {
                return;
            }


            node.dataset.nodeId =
                logicalId;


            node.addEventListener(
                "click",
                event => {

                    event.stopPropagation();

                    selectNode(
                        logicalId
                    );

                }
            );

        }
    );


    /*
     * Add click behaviour to clusters.
     */

    const clusters =
        svg.querySelectorAll(
            "g.cluster"
        );


    clusters.forEach(
        cluster => {

            const clusterId =
                cluster.id || "";


            const logicalId =
                extractClusterId(
                    clusterId
                );


            if (!logicalId) {
                return;
            }


            cluster.dataset.clusterId =
                logicalId;


            cluster.style.cursor =
                "pointer";


            cluster.addEventListener(
                "click",
                event => {

                    event.stopPropagation();


                    if (
                        GROUP_DETAILS[
                            logicalId
                        ]
                    ) {

                        showGroupDetails(
                            logicalId
                        );

                    }

                }
            );

        }
    );

}


/* =========================================================
   EXTRACT NODE ID
   ========================================================= */

function extractLogicalNodeId(
    mermaidId
) {

    if (!mermaidId) {
        return null;
    }


    const match =
        mermaidId.match(
            /flowchart-([A-Za-z0-9_]+)-/
        );


    if (match) {

        return match[1];

    }


    const parts =
        mermaidId.split("-");


    if (
        parts.length >= 2 &&
        parts[0] === "flowchart"
    ) {

        return parts[1];

    }


    return null;
}


/* =========================================================
   EXTRACT CLUSTER ID
   ========================================================= */

function extractClusterId(
    clusterId
) {

    if (!clusterId) {
        return null;
    }


    const knownIds = [
        "M2",
        "M3",
        "M5",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6"
    ];


    for (
        const id of knownIds
    ) {

        if (
            clusterId.includes(id)
        ) {

            return id;

        }

    }


    return null;
}


/* =========================================================
   SELECT NODE
   ========================================================= */

function selectNode(
    nodeId
) {

    selectedNode =
        nodeId;

    selectedTool =
        null;


    toolButtonsContainer
        .querySelectorAll(
            ".tool-button"
        )
        .forEach(
            button =>
                button.classList.remove(
                    "active"
                )
        );


    clearHighlighting();


    const node =
        findNodeElement(
            nodeId
        );


    if (node) {

        node.classList.add(
            "node-selected"
        );

    }


    highlightConnectedPath(
        nodeId
    );


    if (
        NODE_DETAILS[nodeId]
    ) {

        renderNodeDetails(
            nodeId
        );

    } else {

        detailsTitle.textContent =
            nodeId;

        detailsContent.innerHTML = `

            <div class="empty-state">

                <h3>
                    No detail definition
                </h3>

                <p>
                    The node exists in the Mermaid graph,
                    but no additional inspector content
                    has been configured for it.
                </p>

            </div>

        `;

    }

}


/* =========================================================
   FIND NODE
   ========================================================= */

function findNodeElement(
    nodeId
) {

    return document.querySelector(
        `[data-node-id="${nodeId}"]`
    );

}


/* =========================================================
   RENDER NODE DETAILS
   ========================================================= */

function renderNodeDetails(
    nodeId
) {

    const data =
        NODE_DETAILS[nodeId];


    if (!data) {
        return;
    }


    detailsTitle.textContent =
        data.title;


    let html = "";


    /*
     * Badges
     */

    if (
        data.badges &&
        data.badges.length
    ) {

        html += `

            <div class="badge-row">

                ${
                    data.badges
                        .map(
                            (badge, index) =>
                                `<span class="badge ${getBadgeClass(index)}">
                                    ${escapeHtml(
                                        badge
                                    )}
                                </span>`
                        )
                        .join("")
                }

            </div>

        `;

    }


    /*
     * Description
     */

    if (data.description) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Purpose
                </div>

                <div class="detail-description">

                    ${escapeHtml(
                        data.description
                    )}

                </div>

            </div>

        `;

    }


    /*
     * Fields
     */

    if (
        data.fields &&
        data.fields.length
    ) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Details
                </div>

                <div class="detail-card">

                    ${
                        data.fields
                            .map(
                                field => `

                                    <div class="key-value">

                                        <div class="key">
                                            ${escapeHtml(
                                                field[0]
                                            )}
                                        </div>

                                        <div class="value">
                                            ${escapeHtml(
                                                field[1]
                                            )}
                                        </div>

                                    </div>

                                `
                            )
                            .join("")
                    }

                </div>

            </div>

        `;

    }


    /*
     * Detection Rules
     */

    if (
        data.rules &&
        data.rules.length
    ) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Detection Rules
                </div>

                <div class="rule-list">

                    ${
                        data.rules
                            .map(
                                (rule, index) => `

                                    <div class="rule-item">

                                        <span
                                            class="rule-number"
                                        >
                                            ${index + 1}
                                        </span>

                                        <code>
                                            ${escapeHtml(
                                                rule
                                            )}
                                        </code>

                                    </div>

                                `
                            )
                            .join("")
                    }

                </div>

            </div>

        `;

    }


    /*
     * Hints
     */

    if (
        data.hints &&
        data.hints.length
    ) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Hints
                </div>

                <div class="rule-list">

                    ${
                        data.hints
                            .map(
                                (hint, index) => `

                                    <div class="rule-item">

                                        <span
                                            class="rule-number"
                                        >
                                            ${index + 1}
                                        </span>

                                        <code>
                                            ${escapeHtml(
                                                hint
                                            )}
                                        </code>

                                    </div>

                                `
                            )
                            .join("")
                    }

                </div>

            </div>

        `;

    }


    /*
     * Tables
     */

    if (
        data.tables &&
        data.tables.length
    ) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Database Tables
                </div>

                <div class="detail-card">

                    ${
                        data.tables
                            .map(
                                table => `

                                    <div class="key-value">

                                        <div class="key">
                                            Table
                                        </div>

                                        <div class="value">
                                            ${escapeHtml(
                                                table
                                            )}
                                        </div>

                                    </div>

                                `
                            )
                            .join("")
                    }

                </div>

            </div>

        `;

    }


    /*
     * Meaning
     */

    if (data.meaning) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Semantic Meaning
                </div>

                <div class="detail-card">

                    ${escapeHtml(
                        data.meaning
                    )}

                </div>

            </div>

        `;

    }


    /*
     * Ontology
     */

    if (data.ontology) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Ontology Mapping
                </div>

                <div class="detail-card">

                    <strong>
                        ${escapeHtml(
                            data.ontology
                        )}
                    </strong>

                </div>

            </div>

        `;

    }


    /*
     * Important note
     */

    if (data.important) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Important
                </div>

                <div class="detail-card">

                    ${escapeHtml(
                        data.important
                    )}

                </div>

            </div>

        `;

    }


    /*
     * Inputs
     */

    if (
        data.inputs &&
        data.inputs.length
    ) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Inputs
                </div>

                <div class="detail-card">

                    ${
                        data.inputs
                            .map(
                                field => `

                                    <div class="key-value">

                                        <div class="key">
                                            ${escapeHtml(
                                                field[0]
                                            )}
                                        </div>

                                        <div class="value">
                                            ${escapeHtml(
                                                field[1]
                                            )}
                                        </div>

                                    </div>

                                `
                            )
                            .join("")
                    }

                </div>

            </div>

        `;

    }


    /*
     * Outputs
     */

    if (
        data.outputs &&
        data.outputs.length
    ) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Outputs
                </div>

                <div class="detail-card">

                    ${
                        data.outputs
                            .map(
                                output => `

                                    <div class="key-value">

                                        <div class="key">
                                            Output
                                        </div>

                                        <div class="value">
                                            ${escapeHtml(
                                                output
                                            )}
                                        </div>

                                    </div>

                                `
                            )
                            .join("")
                    }

                </div>

            </div>

        `;

    }


    /*
     * Path
     */

    if (
        data.path &&
        data.path.length
    ) {

        html += `

            <div class="detail-section">

                <div class="detail-section-title">
                    Path
                </div>

                <div class="path-strip">

                    ${
                        data.path
                            .map(
                                (item, index) => `

                                    <span
                                        class="path-node"
                                    >
                                        ${escapeHtml(
                                            item
                                        )}
                                    </span>

                                    ${
                                        index <
                                        data.path.length - 1
                                            ? `
                                                <span
                                                    class="path-arrow"
                                                >
                                                    →
                                                </span>
                                            `
                                            : ""
                                    }

                                `
                            )
                            .join("")
                    }

                </div>

            </div>

        `;

    }


    detailsContent.innerHTML =
        html;

}


/* =========================================================
   GROUP DETAILS
   ========================================================= */

function showGroupDetails(
    groupId
) {

    const data =
        GROUP_DETAILS[groupId];


    if (!data) {
        return;
    }


    selectedNode =
        groupId;

    selectedTool =
        null;


    toolButtonsContainer
        .querySelectorAll(
            ".tool-button"
        )
        .forEach(
            button =>
                button.classList.remove(
                    "active"
                )
        );


    clearHighlighting();


    detailsTitle.textContent =
        data.title;


    const badgeHtml =
        data.badges
            .map(
                badge =>
                    `<span class="badge blue">
                        ${escapeHtml(
                            badge
                        )}
                    </span>`
            )
            .join("");


    detailsContent.innerHTML = `

        <div class="badge-row">
            ${badgeHtml}
        </div>

        <div class="detail-section">

            <div class="detail-section-title">
                Overview
            </div>

            <div class="detail-description">

                ${escapeHtml(
                    data.description
                )}

            </div>

        </div>

    `;


    highlightGroup(
        groupId
    );

}


/* =========================================================
   HIGHLIGHT GROUP
   ========================================================= */

function highlightGroup(
    groupId
) {

    const svg =
        diagram.querySelector(
            "svg"
        );


    if (!svg) {
        return;
    }


    const cluster =
        Array.from(
            svg.querySelectorAll(
                "g.cluster"
            )
        ).find(
            element =>
                (
                    element.id || ""
                ).includes(groupId)
        );


    if (!cluster) {
        return;
    }


    const nodes =
        cluster.querySelectorAll(
            ".node"
        );


    nodes.forEach(
        node => {

            node.classList.add(
                "node-selected"
            );

        }
    );

}


/* =========================================================
   ORIGINAL NODE PATH HIGHLIGHTING
   ========================================================= */

function highlightConnectedPath(
    nodeId
) {

    const svg =
        diagram.querySelector(
            "svg"
        );


    if (!svg) {
        return;
    }


    const node =
        findNodeElement(
            nodeId
        );


    if (!node) {
        return;
    }


    const edges =
        svg.querySelectorAll(
            ".edgePath"
        );


    edges.forEach(
        edge => {

            const edgeId =
                edge.id || "";


            if (
                edgeId.includes(
                    nodeId
                )
            ) {

                edge.classList.add(
                    "edge-highlight"
                );

            }

        }
    );

}


/* =========================================================
   CLEAR HINT VISUALIZATION
   ========================================================= */

function clearHintVisualization() {

    const hintNode =
        findNodeElement(
            "H"
        );


    if (!hintNode) {
        return;
    }


    hintNode.classList.remove(
        "hint-node-active"
    );


    hintNode.classList.remove(
        "hint-node-neutral"
    );


    hintNode
        .querySelectorAll(
            ".hint-indicator"
        )
        .forEach(
            indicator => {

                indicator.classList.remove(
                    "hint-active"
                );

                indicator.classList.remove(
                    "hint-false"
                );

                indicator.classList.remove(
                    "hint-missing"
                );


                const state =
                    indicator.querySelector(
                        ".hint-indicator-state"
                    );


                if (state) {

                    state.textContent =
                        "—";

                }

            }
        );

}


/* =========================================================
   CLEAR HIGHLIGHTING
   ========================================================= */

function clearHighlighting() {

    const svg =
        diagram.querySelector(
            "svg"
        );


    if (!svg) {
        return;
    }


    svg
        .querySelectorAll(
            ".node-selected"
        )
        .forEach(
            element => {

                element.classList.remove(
                    "node-selected"
                );

            }
        );


    svg
        .querySelectorAll(
            ".node-path-highlight"
        )
        .forEach(
            element => {

                element.classList.remove(
                    "node-path-highlight"
                );

                element.style.removeProperty(
                    "--path-color"
                );

            }
        );


    svg
        .querySelectorAll(
            ".node-dimmed"
        )
        .forEach(
            element => {

                element.classList.remove(
                    "node-dimmed"
                );

            }
        );


    svg
        .querySelectorAll(
            ".edge-highlight"
        )
        .forEach(
            element => {

                element.classList.remove(
                    "edge-highlight"
                );

                element.style.removeProperty(
                    "--path-color"
                );

            }
        );


    svg
        .querySelectorAll(
            ".edge-dimmed"
        )
        .forEach(
            element => {

                element.classList.remove(
                    "edge-dimmed"
                );

            }
        );


    clearHintVisualization();

}


/* =========================================================
   RESET
   ========================================================= */

function resetView() {

    selectedNode =
        null;

    selectedTool =
        null;


    toolButtonsContainer
        .querySelectorAll(
            ".tool-button"
        )
        .forEach(
            button =>
                button.classList.remove(
                    "active"
                )
        );


    clearHighlighting();


    selectedToolStatus.textContent =
        "No tool selected";


    detailsTitle.textContent =
        "Select a node";


    detailsContent.innerHTML = `

        <div class="empty-state">

            <div class="empty-icon">
                ⌁
            </div>

            <h3>
                Explore the pipeline
            </h3>

            <p>
                Select a tool to trace its primary capability
                path, or click a node in the diagram to inspect
                its purpose, detection logic, inputs, outputs,
                and evidence.
            </p>

        </div>

    `;


    zoomLevel =
        1;

    translateX =
        0;

    translateY =
        0;


    applyTransform();

    fitDiagram();

}


/* =========================================================
   CONTROLS
   ========================================================= */

function setupControls() {

    resetBtn.addEventListener(
        "click",
        resetView
    );


    zoomInBtn.addEventListener(
        "click",
        () => {

            zoomLevel =
                Math.min(
                    zoomLevel + 0.15,
                    3
                );

            applyTransform();

        }
    );


    zoomOutBtn.addEventListener(
        "click",
        () => {

            zoomLevel =
                Math.max(
                    zoomLevel - 0.15,
                    0.25
                );

            applyTransform();

        }
    );


    fitBtn.addEventListener(
        "click",
        fitDiagram
    );


    closeDetailsBtn.addEventListener(
        "click",
        () => {

            detailsTitle.textContent =
                "Select a node";


            detailsContent.innerHTML = `

                <div class="empty-state">

                    <div class="empty-icon">
                        ⌁
                    </div>

                    <h3>
                        Explore the pipeline
                    </h3>

                    <p>
                        Select a tool to trace its primary
                        capability path, or click a node in
                        the diagram to inspect its logic.
                    </p>

                </div>

            `;


            selectedNode =
                null;

            selectedTool =
                null;


            toolButtonsContainer
                .querySelectorAll(
                    ".tool-button"
                )
                .forEach(
                    button =>
                        button.classList.remove(
                            "active"
                        )
                );


            selectedToolStatus.textContent =
                "No tool selected";


            clearHighlighting();

        }
    );

}


/* =========================================================
   PAN / ZOOM
   ========================================================= */

function setupPanZoom() {

    diagramContainer.addEventListener(
        "wheel",
        event => {

            event.preventDefault();


            const delta =
                event.deltaY < 0
                    ? 0.1
                    : -0.1;


            zoomLevel =
                Math.min(
                    Math.max(
                        zoomLevel + delta,
                        0.25
                    ),
                    3
                );


            applyTransform();

        },
        {
            passive: false
        }
    );


    diagramContainer.addEventListener(
        "mousedown",
        event => {

            if (
                event.target.closest(
                    ".node"
                )
            ) {
                return;
            }


            isDragging =
                true;


            dragStartX =
                event.clientX -
                translateX;


            dragStartY =
                event.clientY -
                translateY;


            diagramContainer.style.cursor =
                "grabbing";

        }
    );


    window.addEventListener(
        "mousemove",
        event => {

            if (!isDragging) {
                return;
            }


            translateX =
                event.clientX -
                dragStartX;


            translateY =
                event.clientY -
                dragStartY;


            applyTransform();

        }
    );


    window.addEventListener(
        "mouseup",
        () => {

            isDragging =
                false;

            diagramContainer.style.cursor =
                "grab";

        }
    );


    /*
     * Touch support
     */

    let touchStartX =
        0;

    let touchStartY =
        0;


    diagramContainer.addEventListener(
        "touchstart",
        event => {

            if (
                event.touches.length !== 1
            ) {
                return;
            }


            touchStartX =
                event.touches[0].clientX -
                translateX;


            touchStartY =
                event.touches[0].clientY -
                translateY;

        },
        {
            passive: true
        }
    );


    diagramContainer.addEventListener(
        "touchmove",
        event => {

            if (
                event.touches.length !== 1
            ) {
                return;
            }


            translateX =
                event.touches[0].clientX -
                touchStartX;


            translateY =
                event.touches[0].clientY -
                touchStartY;


            applyTransform();

        },
        {
            passive: true
        }
    );

}


/* =========================================================
   APPLY TRANSFORM
   ========================================================= */

function applyTransform() {

    diagram.style.transform =
        `
        translate(
            ${translateX}px,
            ${translateY}px
        )
        scale(
            ${zoomLevel}
        )
        `;

}


/* =========================================================
   FIT DIAGRAM
   ========================================================= */

function fitDiagram() {

    const svg =
        diagram.querySelector(
            "svg"
        );


    if (!svg) {
        return;
    }


    zoomLevel =
        1;

    translateX =
        0;

    translateY =
        0;


    const svgRect =
        svg.getBoundingClientRect();


    const containerRect =
        diagramContainer.getBoundingClientRect();


    if (
        !svgRect.width ||
        !svgRect.height
    ) {
        return;
    }


    const horizontalRatio =
        (
            containerRect.width -
            80
        ) /
        svgRect.width;


    const verticalRatio =
        (
            containerRect.height -
            80
        ) /
        svgRect.height;


    zoomLevel =
        Math.min(
            horizontalRatio,
            verticalRatio,
            1
        );


    zoomLevel =
        Math.max(
            zoomLevel,
            0.25
        );


    applyTransform();

}


/* =========================================================
   BADGE CLASS
   ========================================================= */

function getBadgeClass(
    index
) {

    const classes = [
        "blue",
        "green",
        "orange",
        "purple",
        "red"
    ];


    return classes[
        index %
        classes.length
    ];

}


/* =========================================================
   HTML ESCAPING
   ========================================================= */

function escapeHtml(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}