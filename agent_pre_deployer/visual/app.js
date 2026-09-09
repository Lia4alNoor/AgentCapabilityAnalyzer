
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

        rules: [
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
   DOM REFERENCES
   ========================================================= */

const diagramContainer =
    document.getElementById("diagram-container");

const diagram =
    document.getElementById("mermaid-diagram");

const detailsTitle =
    document.getElementById("details-title");

const detailsContent =
    document.getElementById("details-content");

const resetBtn =
    document.getElementById("resetBtn");

const zoomInBtn =
    document.getElementById("zoomInBtn");

const zoomOutBtn =
    document.getElementById("zoomOutBtn");

const fitBtn =
    document.getElementById("fitBtn");

const closeDetailsBtn =
    document.getElementById("closeDetailsBtn");


/* =========================================================
   STATE
   ========================================================= */

let zoomLevel = 1;

let selectedNode = null;

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

            await mermaid.run({
                nodes: [
                    document.getElementById(
                        "mermaid-diagram"
                    )
                ]
            });

            setupDiagram();

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
                    <div class="empty-icon">!</div>
                    <h3>Unable to render diagram</h3>
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
   SETUP DIAGRAM
   ========================================================= */

function setupDiagram() {

    const svg =
        diagram.querySelector("svg");

    if (!svg) {

        console.warn(
            "Mermaid SVG not found."
        );

        return;
    }


    /*
     * Mermaid gives nodes IDs such as:
     *
     * flowchart-A-...
     *
     * We extract the logical node ID.
     */

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


    /*
     * Typical Mermaid generated IDs:
     *
     * flowchart-A-0
     * flowchart-D1-1
     */

    const match =
        mermaidId.match(
            /flowchart-([A-Za-z0-9_]+)-/
        );


    if (match) {

        return match[1];

    }


    /*
     * Fallback for other Mermaid versions.
     */

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


    /*
     * Mermaid cluster IDs can vary by version.
     * Search for known identifiers.
     */

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
                <h3>No detail definition</h3>
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
                                    ${escapeHtml(badge)}
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
                                            ${escapeHtml(field[0])}
                                        </div>

                                        <div class="value">
                                            ${escapeHtml(field[1])}
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
     * Rules
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

                <div class="code-block">
${data.rules.map(escapeHtml).join("\n")}
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
                                            ${escapeHtml(table)}
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


    clearHighlighting();


    detailsTitle.textContent =
        data.title;


    const badgeHtml =
        data.badges
            .map(
                badge =>
                    `<span class="badge blue">
                        ${escapeHtml(badge)}
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
        node =>
            node.classList.add(
                "node-selected"
            )
    );

}


/* =========================================================
   CONNECTED PATH HIGHLIGHTING
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


    /*
     * Mermaid edges have different generated IDs
     * between versions. Instead of relying entirely
     * on generated IDs, inspect edge labels and
     * nearby graph structure.
     */

    const node =
        findNodeElement(
            nodeId
        );


    if (!node) {
        return;
    }


    /*
     * Highlight adjacent edges using the SVG
     * geometry relationships where possible.
     */

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
            element =>
                element.classList.remove(
                    "node-selected"
                )
        );


    svg
        .querySelectorAll(
            ".node-dimmed"
        )
        .forEach(
            element =>
                element.classList.remove(
                    "node-dimmed"
                )
        );


    svg
        .querySelectorAll(
            ".edge-highlight"
        )
        .forEach(
            element =>
                element.classList.remove(
                    "edge-highlight"
                )
        );


    svg
        .querySelectorAll(
            ".edge-dimmed"
        )
        .forEach(
            element =>
                element.classList.remove(
                    "edge-dimmed"
                )
        );

}


/* =========================================================
   RESET
   ========================================================= */

function resetView() {

    selectedNode =
        null;

    clearHighlighting();

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
                Click a node in the diagram to inspect
                its purpose, detection logic, inputs,
                outputs, and evidence.
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
                        Click a node in the diagram to inspect
                        its purpose, detection logic, inputs,
                        outputs, and evidence.
                    </p>

                </div>

            `;

            selectedNode =
                null;

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

            /*
             * Don't start panning when clicking a node.
             */

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


    /*
     * Reset first.
     */

    zoomLevel =
        1;

    translateX =
        0;

    translateY =
        0;


    /*
     * Get actual diagram dimensions.
     */

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