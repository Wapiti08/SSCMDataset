# parsing
from parsing.syslog import parse_syslog_csv
from parsing.auditd import parse_audit_log
from parsing.auth import parse_auth_log
from parsing.zeek import parse_conn_log, parse_dns_log, parse_http_log, parse_files_log, parse_ssh_log, parse_ssl_log
from parsing.suricata import parse_suricata_log
# labeling
from labeling.tagger import tag_steps

from analysis.ambig import ambiguity
from analysis.coverage import step_coverage
from analysis.failure_taxonomy import failure_taxonomy
from analysis.metrics import compute_metrics

from recons.chain_builder import reconstruct_chain
from recons.event_graph import build_event_graph

from ..utils.io import safe_parse
import pandas as pd

def main():
    frames = []

    # ------- host telemetry --------
    frames.append(parse_syslog_csv("syslog.csv"))
    frames.append(parse_auth_log("auth.log"))


    events = pd.concat([
        parse_syslog_csv("syslog.csv"),
        parse_audit_log("audit.log"),
    ])

    tagged = tag_steps(events)

    print("Coverage:", step_coverage(tagged))
    print("Failures:", failure_taxonomy(tagged))

    g = build_event_graph(tagged)
    chain = reconstruct_chain(g, tagged.dropna(subset=["step"]))
    print("Chain:", chain)

if __name__ == "__main__":
    main()