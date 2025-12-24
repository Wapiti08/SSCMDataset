from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Scenario:
    id: str               # e.g., "SC1"
    name: str             # short name
    description: str
    expected_sources: Dict[str, bool]  # which telemetry is expected

SCENARIOS = {
    "sc1": Scenario(
        id = "SC1",
        name="Stegano",
        description="A scenario involving steganography-based data exfiltration.",
        expected_sources={
            "azure_conn": True,
            "azure_process": True,
            "azure_security": True,
            "auditd": False,
            "auth": False,
            "suricata": False,
            "syslog": False,
            "zeek": False,
        },
    ),
    "sc2": Scenario(
        id = "SC2",
        name="Starter",
        description="A scenario involving steganography-based data exfiltration.",
        expected_sources={
            "azure_conn": True,
            "azure_process": True,
            "azure_security": True,
            "auditd": False,
            "auth": False,
            "suricata": False,
            "syslog": False,
            "zeek": False,
        },
    ),
    "sc3": Scenario(
        id = "SC1",
        name="Stegano",
        description="A scenario involving steganography-based data exfiltration.",
        expected_sources={
            "azure_conn": True,
            "azure_process": True,
            "azure_security": True,
            "auditd": False,
            "auth": False,
            "suricata": False,
            "syslog": False,
            "zeek": False,
        },
    ),
    "sc4": Scenario(
        id = "SC1",
        name="Stegano",
        description="A scenario involving steganography-based data exfiltration.",
        expected_sources={
            "azure_conn": True,
            "azure_process": True,
            "azure_security": True,
            "auditd": False,
            "auth": False,
            "suricata": False,
            "syslog": False,
            "zeek": False,
        },
    ),
    "sc5": Scenario(
        id = "SC1",
        name="Stegano",
        description="A scenario involving steganography-based data exfiltration.",
        expected_sources={
            "azure_conn": True,
            "azure_process": True,
            "azure_security": True,
            "auditd": False,
            "auth": False,
            "suricata": False,
            "syslog": False,
            "zeek": False,
        },
    ),
    "sc6": Scenario(
        id = "SC1",
        name="Stegano",
        description="A scenario involving steganography-based data exfiltration.",
        expected_sources={
            "azure_conn": True,
            "azure_process": True,
            "azure_security": True,
            "auditd": False,
            "auth": False,
            "suricata": False,
            "syslog": False,
            "zeek": False,
        },
    ),
    "sc7": Scenario(
        id = "SC1",
        name="Stegano",
        description="A scenario involving steganography-based data exfiltration.",
        expected_sources={
            "azure_conn": True,
            "azure_process": True,
            "azure_security": True,
            "auditd": False,
            "auth": False,
            "suricata": False,
            "syslog": False,
            "zeek": False,
        },
    ),

}