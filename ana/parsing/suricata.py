'''
 # @ Create Time: 2025-12-21 19:30:19
 # @ Modified time: 2025-12-23 16:30:21
 # @ Description: as network semantic enrichment & corroboration source
 '''

import json
from pathlib import Path
from typing import Iterable, Optional
import pandas as pd
from .utils import _to_ts, _safe_str, _subset_raw


def _mk_tuple(e: dict) -> dict:
    src_ip = _safe_str(e.get("src_ip"))
    src_port = _safe_str(e.get("src_port"))
    dst_ip = _safe_str(e.get("dest_ip"))
    dst_port = _safe_str(e.get("dest_port"))
    proto = _safe_str(e.get("proto"))
    return dict(
        src_ip=src_ip, src_port=src_port,
        dst_ip=dst_ip, dst_port=dst_port,
        proto=proto,
        subject=f"{src_ip}:{src_port}" if src_ip or src_port else "",
        object=f"{dst_ip}:{dst_port}" if dst_ip or dst_port else "",
    )

# ---------------------------------
# main parsing functions
# ---------------------------------

def parse_suricata_eve(path: str | Path) -> pd.DataFrame:
    '''
    Parse Suricata eve.json (JSON-lines).
    Keep minimal but joinable fields for cross-correlation:
        - flow_id (stable)
        - tx_id (http transaction)
        - 5-tuple (src/dst/proto)
        - event_type specific pivots:
          http: hostname/url/method/status/user_agent
          fileinfo: filename/size/state
          dns: rrname/rrtype/rcode/answers
          tls: sni/ja3/fingerprint-ish fields if present
          alert: signature/category/severity
          flow: flow_state/bytes/packets
    
    '''
    rows = []
    path = Path(path)

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            
            ts = _to_ts(e.get("timestamp"))
            if pd.isna(ts):
                continue

            etype = e.get("event_type", "unknown")
            tup = _mk_tuple(e)

            base = {
                "ts": ts,
                "host": "network_sensor",
                "source": "suricata",
                "event_type": etype,  # keep native type
                "action": etype,
                "subject": tup["subject"],
                "object": tup["object"],
                "src_ip": tup["src_ip"],
                "src_port": tup["src_port"],
                "dst_ip": tup["dst_ip"],
                "dst_port": tup["dst_port"],
                "proto": tup["proto"],
                "flow_id": _safe_str(e.get("flow_id", "")),
                "tx_id": _safe_str(e.get("tx_id", "")),
            }

            # --------- event-specific extraction ---------
            raw_small = _subset_raw(e, [
                "timestamp", "event_type", "flow_id", "tx_id",
                "src_ip", "src_port", "dest_ip", "dest_port", "proto", "app_proto",
                "in_iface", "pkt_src"
            ])

            if etype == "http":
                h = e.get("http", {}) or {}
                base["event_type"] = "http"
                base["action"] = _safe_str(h.get("http_method", "http"))
                base["http_host"] = _safe_str(h.get("hostname", ""))
                base["http_url"] = _safe_str(h.get("url", ""))
                base["http_status"] = _safe_str(h.get("status", ""))
                base["user_agent"] = _safe_str(h.get("http_user_agent", ""))
                # object as host+url for pivots
                if base["http_host"] or base["http_url"]:
                    base["object"] = base["http_host"] + base["http_url"]

                raw_small["http"] = _subset_raw(h, [
                  "hostname", "url", "http_method", "status", "length",
                    "http_user_agent", "protocol", "http_content_type"
                ])
            
            elif etype == "fileinfo":
                fi = e.get("fileinfo", {}) or {}
                base["event_type"] = "file"
                base["action"] = "fileinfo"
                base["filename"] = _safe_str(fi.get("filename", ""))
                base["file_size"] = _safe_str(fi.get("size", ""))
                base["file_state"] = _safe_str(fi.get("state", ""))
                if base["filename"]:
                    base["object"] = base["filename"]

                raw_small["fileinfo"] = _subset_raw(fi, [
                    "filename", "size", "state", "stored", "gaps", "sha256", "md5"
                ])

            elif etype == "dns":
                d = e.get("dns", {}) or {}
                base["event_type"] = "dns"
                base["action"] = _safe_str(d.get("type", "dns"))
                base["dns_rrname"] = _safe_str(d.get("rrname", ""))
                base["dns_rrtype"] = _safe_str(d.get("rrtype", ""))
                base["dns_rcode"] = _safe_str(d.get("rcode", ""))
                # pivot object to domain
                if base["dns_rrname"]:
                    base["object"] = base["dns_rrname"]

                raw_small["dns"] = _subset_raw(d, ["type", "rrname", "rrtype", "rcode", "rdata", "ttl"])

            elif etype == "tls":
                t = e.get("tls", {}) or {}
                base["event_type"] = "tls"
                base["action"] = "handshake"
                base["tls_sni"] = _safe_str(t.get("sni", ""))
                base["tls_version"] = _safe_str(t.get("version", ""))
                base["tls_ja3"] = _safe_str(t.get("ja3", ""))
                if base["tls_sni"]:
                    base["object"] = base["tls_sni"]

                raw_small["tls"] = _subset_raw(t, ["sni", "version", "subject", "issuerdn", "ja3", "ja3s", "fingerprint"])

            elif etype == "flow":
                fl = e.get("flow", {}) or {}
                base["event_type"] = "flow"
                base["action"] = _safe_str(fl.get("state", "flow"))
                base["flow_state"] = _safe_str(fl.get("state", ""))
                base["bytes_toserver"] = _safe_str(fl.get("bytes_toserver", ""))
                base["bytes_toclient"] = _safe_str(fl.get("bytes_toclient", ""))
                base["pkts_toserver"] = _safe_str(fl.get("pkts_toserver", ""))
                base["pkts_toclient"] = _safe_str(fl.get("pkts_toclient", ""))

                raw_small["flow"] = _subset_raw(fl, [
                    "state", "bytes_toserver", "bytes_toclient", "pkts_toserver", "pkts_toclient"
                ])

            elif etype == "alert":
                al = e.get("alert", {}) or {}
                base["event_type"] = "alert"
                base["action"] = "alert"
                base["signature"] = _safe_str(al.get("signature", ""))
                base["category"] = _safe_str(al.get("category", ""))
                base["severity"] = _safe_str(al.get("severity", ""))
                if base["signature"]:
                    base["object"] = base["signature"]

                raw_small["alert"] = _subset_raw(al, ["signature", "category", "severity", "gid", "signature_id", "rev"])

            else:
                # keep other types (icmp, anomaly, stats...) as generic
                base["event_type"] = etype if etype else "suricata"
                base["action"] = etype if etype else "record"

            # store small raw only (avoid full e -> huge)
            base["raw"] = json.dumps(raw_small, ensure_ascii=False)

            rows.append(base)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    # for quick testing
    # python3 -m parsing.suricata
    data_path = Path.cwd().parent.joinpath("data", "sc4")
    
    # test suricata eve.json
    eve_df = parse_suricata_eve(data_path.joinpath("eve.json"))
    print(eve_df.head())
    print(eve_df.columns)
