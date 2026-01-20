"""Labeling rules for coarse attack steps.

Design goals:
- Schema-tolerant: rules reference canonical fields; tagger resolves to real columns via FIELD_ALIASES.
- Conservative defaults: prefer structured hints when available to reduce keyword-only noise.
- Extendable: TECHNIQUE_TO_STEP enables expected-step scoring from ATT&CK layers.

Coarse steps (current): AUTH, DOWNLOAD, OUTBOUND_CONN
"""

# ---- source groups ----
AZURE_SOURCES = ["azure_conn", "azure_process", "azure_security", "azure_events", "azure_port"]
AZURE_NET_SOURCES = ["azure_conn", "azure_port"]
AZURE_AUTH_SOURCES = ["azure_security", "azure_events"]

# ---- schema aliases ----
# Canonical field -> list of possible column names across telemetry sources.
# The tagger prefers exact matches, then case-insensitive matches.
FIELD_ALIASES = {
    "raw": [
        "raw", "_raw", "message", "Message", "msg", "log", "Log", "Details",
        "RenderedDescription", "Description", "EventData", "SyslogMessage",
    ],
    "message": [
        "message", "Message", "RenderedDescription", "Description", "Details", "EventMessage", "SyslogMessage",
    ],
    "cmdline": [
        "cmdline", "CmdLine", "CommandLine", "commandLine", "process_command_line",
        "ProcessCommandLine", "Command", "SyslogMessage",
    ],
    "process": [
        "process", "process_name", "ProcessName", "Image", "NewProcessName", "ParentProcessName",
    ],
    "exe": [
        "exe", "Executable", "Image", "process_path", "NewProcessName", "ProcessName",
    ],
    "event": [
        "event", "EventID", "EventId", "event_id", "EventName", "OperationName", "ActivityDisplayName",
    ],
    "action": [
        "action", "Action", "OperationName", "Activity", "ResultType", "EventAction",
        "Facility", "SeverityLevel",
    ],
    "event_type": [
        "event_type", "EventType", "Type", "ZeekEventType", "SuricataEventType",
    ],
    "proto": [
        "proto", "Protocol", "networkProtocol", "TransportProtocol", "ipProtocol",
    ],
    "service": [
        "service", "Service", "app_proto", "AppProtocol",
    ],
    "dst": [
        "dst", "dst_ip", "dest_ip", "DestinationIP", "DestinationIp", "DestIp",
        "RemoteIP", "RemoteIp", "DstAddr", "id.resp_h", "daddr", "dstaddr",
    ],
    "dst_port": [
        "dst_port", "DestinationPort", "DestPort", "RemotePort", "id.resp_p", "dport", "dstport",
    ],
    "src": [
        "src", "src_ip", "SourceIP", "SourceIp", "SrcIp", "ClientIP", "HostIP", "id.orig_h",
    ],
    "user": [
        "user", "User", "Account", "AccountName", "SubjectUserName", "TargetUserName", "acct", "username",
    ],
    "timestamp": [
        "timestamp", "TimeGenerated [UTC]", "EventTime [UTC]", "time", "TimeCreated", "TimeStamp",
    ],
}

# ---- ATT&CK technique to coarse step mapping (for expected-step scoring) ----
# Extend this as you add more coarse steps.
TECHNIQUE_TO_STEP = {
    # Credential access / valid accounts / brute force -> AUTH
    "T1078": "AUTH",   # Valid Accounts
    "T1110": "AUTH",   # Brute Force

    # Ingress tool transfer / obtain capabilities -> DOWNLOAD
    "T1105": "DOWNLOAD",  # Ingress Tool Transfer
    "T1588": "DOWNLOAD",  # Obtain Capabilities
    "T1588.001": "DOWNLOAD",
    "T1588.002": "DOWNLOAD",
    "T1588.003": "DOWNLOAD",
    "T1588.004": "DOWNLOAD",
    "T1608": "DOWNLOAD",  # Stage Capabilities
    "T1608.001": "DOWNLOAD",
    "T1608.002": "DOWNLOAD",
    "T1608.003": "DOWNLOAD",
    "T1608.004": "DOWNLOAD",

    # Proxy / encoding / encrypted channel / exfil over c2 channel -> OUTBOUND_CONN
    "T1090": "OUTBOUND_CONN",  # Proxy
    "T1132": "OUTBOUND_CONN",  # Data Encoding
    "T1572": "OUTBOUND_CONN",  # Protocol Tunneling
    "T1041": "OUTBOUND_CONN",  # Exfiltration Over C2 Channel
    "T1020": "OUTBOUND_CONN",  # Automated Exfiltration
    "T1030": "OUTBOUND_CONN",  # Data Transfer Size Limits (network transfer patterns)
}


def expected_steps_from_techniques(technique_ids):
    """Map ATT&CK technique IDs to the expected set of coarse steps."""
    if not technique_ids:
        return []
    out = set()
    for t in technique_ids:
        if t is None:
            continue
        key = str(t).strip()
        step = TECHNIQUE_TO_STEP.get(key)
        if step:
            out.add(step)
    return sorted(out)


# ---- coarse step detection rules ----
STEP_RULES = [
    # --- AUTH ---
    {
        "id": "AUTH_1",
        "step": "AUTH",
        "patterns": [
            # linux/syslog/auth
            r"\bsshd\b",
            r"Failed password",
            r"Accepted password",
            r"Accepted publickey",
            r"invalid user",
            r"pam_unix\(sshd:auth\)",

            # auditd
            r"\bUSER_LOGIN\b",
            r"\bUSER_AUTH\b",
            r"\bUSER_ACCT\b",
            r"PAM:authentication",
            r"op=login",
            r"res=(?:failed|success)",

            # windows/azure (lightweight)
            r"\blogon\b",
            r"\blogin\b",
            r"\bauthentication\b",
            r"\b4624\b",
            r"\b4625\b",
            r"\brdp\b",
        ],
        "fields": ["raw", "message", "event", "action", "user"],
        # include syslog because sshd/pam auth frequently lives there
        "sources": ["auth", "auditd", "syslog"] + AZURE_AUTH_SOURCES,
        "priority": 10,
        "score": 1.0,
    },

    # --- DOWNLOAD ---
    {
        "id": "DL_1",
        "step": "DOWNLOAD",
        "patterns": [
            # fetch tooling
            r"\bcurl\b.+https?://",
            r"\bwget\b.+https?://",
            r"\bcurl\b.*\s-(?:o|O)\s",
            r"\bwget\b.*\s-(?:O|o)\s",

            # package managers / repo pulls
            r"\bapt(?:-get)?\b\s+install\b",
            r"\byum\b\s+install\b",
            r"\bdnf\b\s+install\b",
            r"\bpip(?:3)?\b\s+install\b",
            r"\bnpm\b\s+install\b",
            r"\bgo\b\s+get\b",
            r"\bgit\b\s+clone\b",

            # windows/powershell/bits/certutil
            r"\binvoke-webrequest\b",
            r"\binvoke-restmethod\b",
            r"\bstart-bitstransfer\b",
            r"\bbitsadmin\b",
            r"\bcertutil\b.+\b-urlcache\b",
            r"https?://\S+\.(?:exe|dll|ps1|zip|msi|jar)\b",
            r"\bdownload(?:file)?\b.+https?://",
        ],
        "fields": ["raw", "cmdline", "process", "exe", "message"],
        "sources": None,  # keep global
        "priority": 20,
        "score": 1.0,
    },

    # --- OUTBOUND_CONN ---
    {
        "id": "NET_1",
        "step": "OUTBOUND_CONN",
        "patterns": [
            # keyword fallback (keep small)
            r"\bdns\b",
            r"\bhttp\b",
            r"\bssl\b",
            r"\bconnect\b",
            r"\boutbound\b",
        ],
        # If event_type/service exists, use it to reduce false positives
        "where_any": [
            {"field": "event_type", "in": ["conn", "dns", "http", "ssl", "tls", "flow", "netconn"]},
            {"field": "service", "in": ["dns", "http", "ssl", "tls"]},
        ],
        "fields": ["raw", "event_type", "proto", "service", "message", "action", "dst", "dst_port"],
        "sources": ["zeek", "suricata"] + AZURE_NET_SOURCES,
        "priority": 15,
        "score": 1.0,
    },
]
