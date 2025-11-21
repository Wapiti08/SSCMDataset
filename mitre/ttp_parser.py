'''
 # @ Create Time: 2025-11-21 09:08:25
 # @ Modified time: 2025-11-21 09:08:27
 # @ Description: 

This module provides an LLM-assisted pipeline to parse arbitrary source code or
log snippets and extract MITRE ATT&CK TTPs, then convert them into the ATT&CK
Navigator layer JSON format required by the user.


The core workflow:
1. `extract_ttps_from_code(source_text, llm_client)`
- Sends code/snippet text to an LLM with a crafted prompt to identify
MITRE ATT&CK techniques (IDs + tactics).


2. `build_navigator_layer(techniques)`
- Accepts a list of dicts: [{"techniqueID": ..., "tactic": ...}, ...].
- Produces a full Navigator-compatible layer JSON.


3. `parse_code_to_layer(source_text, llm_client)`
- Convenience wrapper combining extraction and JSON building.

 '''
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.as_posix()))
import json
import re
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import argparse


Prompt_Template = """
    You are a cybersecurity analyst. Given the following source code or logs,
    extract all MITRE ATT&CK techniques referenced, implied, or likely used.

    Return JSON with fields:
    [
    {"techniqueID": "Txxxx" or "Txxxx.yyy", "tactic": "<tactic-name>"},
    ...
    ]

    Source:

"""

# ---------------------------------------------------------------------
# EXTRACT TTPs
# ---------------------------------------------------------------------

def extract_ttps_from_code(source_code: str, client: OpenAI) -> List[Dict[str, str]]:
    prompt = Prompt_Template + "\n" + source_code + "\n"

    response = client.responses.create(
        model="gpt-5.1",
        input=prompt
    )

    # extract output
    raw_output = response.output_text

    # match context in [], allow for newlines
    match = re.search(r"(\[.*?\])", raw_output, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON array found in LLM response.")

    # parse JSON from output
    try:
        techniques = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise ValueError("Could not decode JSON from LLM output.")
    
    cleaned = []
    for t in techniques:
        # match key words
        if "techniqueID" in t and "tactic" in t:
            cleaned.append({
                "techniqueID": t["techniqueID"],
                "tactic": t["tactic"]
            })

    return cleaned


# ---------------------------------------------------------------------
# BUILD ATT&CK NAVIGATOR LAYER
# ---------------------------------------------------------------------
def build_navigator_layer(techniques: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "name": "layer",
        "versions": {
            "attack": "10",
            "navigator": "4.5.5",
            "layer": "4.3",
        },
        "domain": "enterprise-attack",
        "description": "",
        "filters": {
            "platforms": [
                "Linux","macOS","Windows","Azure AD","Office 365","SaaS",
                "IaaS","Google Workspace","PRE","Network","Containers"
            ]
        },
        "sorting": 0,
        "layout": {
            "layout": "side",
            "aggregateFunction": "average",
            "showID": False,
            "showName": True,
            "showAggregateScores": False,
            "countUnscored": False,
        },
        "hideDisabled": False,
        "techniques": techniques,
    }

# ---------------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------------

def parse_code_to_layer(source_code: str, client: OpenAI) -> Dict[str, Any]:
    techs = extract_ttps_from_code(source_code, client)
    layer = build_navigator_layer(techs)
    return layer

if __name__ == "__main__":
    dotenv_path = Path.cwd().parent.joinpath('.env').as_posix()
    load_dotenv(dotenv_path)
    import os
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

    parser = argparse.ArgumentParser(description="Parse source code/logs to MITRE ATT&CK Navigator layer.")
    parser.add_argument("input_file", type=str, help="Path to input source code or log file.")
    parser.add_argument("output_file", type=str, help="Path to output Navigator layer JSON file.")
    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        source_text = f.read()
    layer_json = parse_code_to_layer(source_text, client)
    with open(args.output_file, "w") as f:
        json.dump(layer_json, f, indent=4)

