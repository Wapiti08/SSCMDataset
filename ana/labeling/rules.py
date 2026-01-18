# ---- source groups ----
AZURE_SOURCES = ["azure_conn", "azure_process", "azure_security", "azure_events", "azure_port"]
AZURE_NET_SOURCES = ["azure_conn", "azure_port"]
AZURE_AUTH_SOURCES = ["azure_security", "azure_events"]

STEP_RULES = [
    # --- AUTH ---
    {
        "step": "AUTH",
        "patterns": [
            # linux/auth
            r"\bsshd\b",
            r"Failed password",
            r"Accepted password",
            r"\bUSER_LOGIN\b",

            # windows/azure (lightweight)
            r"\blogon\b",
            r"\blogin\b",
            r"\bauthentication\b",
            r"\b4624\b",
            r"\b4625\b",
            r"\brdp\b",
        ],
        "fields": ["raw", "message", "event", "action"],
        "sources": ["auth", "auditd"] + AZURE_AUTH_SOURCES,
        "priority": 10,
        "score": 1.0,
    },

    # --- DOWNLOAD ---
    {
        "step": "DOWNLOAD",
        "patterns": [
            # linux
            r"/usr/bin/curl\b",
            r"/usr/bin/wget\b",
            r"\bcurl\b.+https?://",
            r"\bwget\b.+https?://",

            # windows/powershell/bits/certutil
            r"\binvoke-webrequest\b",
            r"\bstart-bitstransfer\b",
            r"\bbitsadmin\b",
            r"\bcertutil\b.+\b-urlcache\b",
            r"https?://\S+\.(exe|dll|ps1|zip|msi)\b",
            r"\bdownload(file)?\b.+https?://",
        ],
        "fields": ["raw", "cmdline", "process", "exe", "message"],
        "sources": None,  # keep global
        "priority": 20,
        "score": 1.0,
    },

    # --- OUTBOUND_CONN ---
    {
        "step": "OUTBOUND_CONN",
        "patterns": [
            r"\bconnect\b",
            r"\bdns\b",
            r"\bhttp\b",
            r"\bssl\b",
            r"\boutbound\b",
        ],
        "fields": ["raw", "event_type", "proto", "service", "message", "action", "dst"],
        "sources": ["zeek", "suricata"] + AZURE_NET_SOURCES,
        "priority": 15,
        "score": 1.0,
    },
]
