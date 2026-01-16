STEP_RULES = [
    # --- AUTH ---
    {
        "step": "AUTH",
        "patterns": [
            r"\bsshd\b",
            r"Failed password",
            r"Accepted password",
            r"\bUSER_LOGIN\b",
        ],
        "fields": ["raw", "message", "event", "action"],
        "sources": ["auth", "azure_wins", "auditd"],       
        "priority": 10,
        "score": 1.0,
    },

    # --- DOWNLOAD ---
    {
        "step": "DOWNLOAD",
        "patterns": [
            r"/usr/bin/curl\b",
            r"/usr/bin/wget\b",
            r"\bcurl\b.+https?://",
            r"\bwget\b.+https?://",
        ],
        "fields": ["raw", "cmdline", "process", "exe", "message"],
        "sources": None,
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
        ],
        "fields": ["raw", "event_type", "proto", "service", "message"],
        "sources": ["zeek", "suricata", "azure_wins"],
        "priority": 15,
        "score": 1.0,
    },
]