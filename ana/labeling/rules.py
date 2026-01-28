"""Labeling rules for coarse attack steps.

Design goals:
- Schema-tolerant: rules reference canonical fields; tagger resolves to real columns via FIELD_ALIASES.
- Conservative defaults: prefer structured hints when available to reduce keyword-only noise.
- Extendable: TECHNIQUE_TO_STEP enables expected-step scoring from ATT&CK layers.

Coarse steps (current): INSTALL, AUTH (optional), DOWNLOAD, OUTBOUND_CONN, EXFIL
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
        "AdditionalFields",
        "additionalFields",
        "Properties",
        "properties",
        "AdditionalDetails",
        "additionalDetails",
],
    "message": [
        "message", "Message", "RenderedDescription", "Description", "Details", "EventMessage", "SyslogMessage",
        "AdditionalFields",
        "additionalFields",
        "OperationName",
        "ActivityDisplayName",
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
        "DestinationIP_s",
        "DestinationIp_s",
        "RemoteIP_s",
        "RemoteIp_s",
        "DestinationIPAddress",
        "DestinationIPAddress_s",
        "DstIP_s",
        "DstIp_s",
        "dest_ip_s",
        "dstIp_s",
        "DestinationIpAddress_s",
],
    "dst_port": [
        "dst_port", "DestinationPort", "DestPort", "RemotePort", "id.resp_p", "dport", "dstport",
        "DestinationPort_d",
        "DestinationPort_s",
        "RemotePort_d",
        "RemotePort_s",
        "DstPort_d",
        "DstPort_s",
        "dest_port_d",
        "dest_port_s",
        "dstPort_d",
        "dstPort_s",
        "DestinationPortNumber",
        "DestinationPortNumber_d",
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

# Network volume / direction (used by heuristics for Azure connection logs)
"bytes_in": [
    "bytes_in", "BytesIn", "bytesIn",
    "bytes_received", "bytesReceived", "BytesReceived", "ReceivedBytes",
    "recv_bytes", "rbytes", "id.resp_bytes", "resp_bytes",
    "BytesReceivedFromClient", "BytesReceivedFromServer",
    "TotalBytesReceived", "totalBytesReceived",
    "BytesReceived_d", "BytesReceived_s", "bytesReceived_d", "bytesReceived_s",
    "ReceivedBytes_d", "ReceivedBytes_s",
    "InBytes", "InBytes_d", "InboundBytes", "InboundBytes_d",
    "TotalBytesIn", "TotalBytesIn_d",
    "bytesIn_d",
    "bytesIn_s",
    "bytesin",
    "recvBytes",
    "recvBytes_d",
],
"bytes_out": [
    "bytes_out", "BytesOut", "bytesOut",
    "bytes_sent", "bytesSent", "BytesSent", "SentBytes",
    "send_bytes", "obytes", "id.orig_bytes", "orig_bytes",
    "BytesSentToClient", "BytesSentToServer",
    "TotalBytesSent", "totalBytesSent",
    "BytesSent_d", "BytesSent_s", "bytesSent_d", "bytesSent_s",
    "SentBytes_d", "SentBytes_s",
    "OutBytes", "OutBytes_d", "OutboundBytes", "OutboundBytes_d",
    "TotalBytesOut", "TotalBytesOut_d",
    "bytesOut_d",
    "bytesOut_s",
    "bytesout",
    "sendBytes",
    "sendBytes_d",
],
"direction": [
    "direction", "Direction", "flow_direction", "FlowDirection", "traffic_direction",
    "FlowDirection_s", "TrafficDirection", "TrafficDirection_s",
    "flowDirection",
    "trafficDirection",
],

}

# ---- ATT&CK technique to coarse step mapping (for expected-step scoring) ----
# Extend this as you add more coarse steps.
TECHNIQUE_TO_STEP = {
    # Supply-chain / distribution trigger -> INSTALL (optional, scenario dependent)
    "T1195": "INSTALL",     # Supply Chain Compromise
    "T1072": "INSTALL",     # Software Deployment Tools (sometimes matches install/deploy chains)

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
    "T1041": "EXFIL",  # Exfiltration Over C2 Channel
    "T1020": "EXFIL",  # Automated Exfiltration
    "T1030": "EXFIL",  # Data Transfer Size Limits (network transfer patterns)
    "T1567": "EXFIL",  # Exfiltration Over Web Service
    "T1567.001": "EXFIL",
    "T1567.002": "EXFIL",
    "T1567.003": "EXFIL",
    "T1567.004": "EXFIL",
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
    # --- Install ----
    {
        "id": "INSTALL_1",
        "step": "INSTALL",
        "patterns": [
            # package managers / installers (trigger point)
            r"\bpip(?:3)?\b\s+install\b",
            r"\bnpm\b\s+(?:install|i)\b",
            r"\byarn\b\s+add\b",
            r"\bpnpm\b\s+add\b",
            r"\bapt(?:-get)?\b\s+install\b",
            r"\byum\b\s+install\b",
            r"\bdnf\b\s+install\b",
            r"\bzypper\b\s+install\b",
            r"\bbrew\b\s+install\b",
            r"\bchoco(?:latey)?\b\s+install\b",
            r"\bpython(?:3(?:\.exe)?)?\b\s+setup\.py\s+install\b",

            # windows installers
            r"\bmsiexec(?:\.exe)?\b",
            r"\bsetup\.exe\b",

            # source retrieval often used as install-like
            r"\bgit\b\s+clone\b",
            r"\bgo\b\s+get\b",
        ],
        "fields": ["cmdline", "raw", "process", "exe", "message"],
        "sources": None,
        "priority": 25,   # higher than DOWNLOAD, so install cmd is INSTALL not DOWNLOAD
        "score": 1.0,
    },
    
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

    # --- EXFIL ---
    {
    "id": "EXFIL_1",
    "step": "EXFIL",
    "patterns": [
        # explicit upload / transfer verbs (prefer these to avoid confusing with downloads)
        r"\bcurl\b[^\n]*\s(?:-T|--upload-file)\b",
        r"\bcurl\b[^\n]*\s(?:-F|--form)\b",
        r"\bwget\b[^\n]*\s--post-(?:data|file)\b",
        r"\binvoke-(?:webrequest|restmethod)\b[^\n]*-method\s+(?:post|put)\b",
        r"\bscp\b|\bsftp\b|\brsync\b",
        r"\bazcopy\b\s+copy\b",
        r"\baws\b\s+s3\s+(?:cp|sync)\b",
        r"\bgsutil\b\s+cp\b",
        r"\brclone\b\s+(?:copy|sync)\b",
        r"\bftp\b[^\n]*\bput\b",
        # HTTP-level hints commonly present in network logs
        r"\bmultipart/form-data\b",
        r"\bcontent-disposition:\s*form-data\b",
        # last-resort keywords
        r"\bexfil(?:trat(?:e|ion))?\b",
        r"\bupload(?:ing)?\b",
    ],
    "fields": ["raw", "message", "cmdline", "uri", "method"],
    # If a structured method exists, require a write-like verb
    "where_any": [
        {"field": "method", "in": ["POST", "PUT"]},
    ],
    "sources": None,  # keep global (works for syslog/audit/zeek/suricata)
    "priority": 18,
    "score": 1.0,
    },

]
