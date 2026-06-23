#!/usr/bin/env python3
"""
generate_dockerfile.py
Generates a Dockerfile based on middleware.config.json.

Usage:
    python templates/scripts/generate_dockerfile.py --config middleware.config.json
"""

import argparse
import json
import os
import sys

DEP_MAPPING = {
    "default": {
        "Django": "",
        "djangorestframework": "",
        "python-dotenv": "",
        "httpx": ""
    },
    "elasticsearch": {
        "elasticsearch": "7.17.0",
        "requests": ""
    },
    "sftp": {
        "paramiko": ""
    },
    "callcenter": {},
    "msteams": {},
    "report": {
        "openpyxl": ""
    },
    "db": {
        "mysqlclient": ""
    }
}

def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        print(f"[ERROR] Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def validate_config(config: dict):
    required = ["project_name", "services", "python_version"]
    missing = [k for k in required if k not in config]
    if missing:
        print(f"[ERROR] Missing required config keys: {missing}")
        sys.exit(1)


def generate(config: dict, output = ""):
    
    services = config.get("services", [])
    default_lib = DEP_MAPPING.get("default", {})
    
    with open(output, "r", encoding="utf-8") as f:

        def write_to_file(conf: dict):
            for lib, version in conf.items():
                if version == "":
                    f.write(f"{lib}\n")
                else:
                    f.write(f"{lib}=={version}\n")

        write_to_file(default_lib)
        for service in services:
            if service not in DEP_MAPPING:
                continue

            deps = DEP_MAPPING.get(service, {})
            write_to_file(deps)
       
        if config.get("db", False):
            write_to_file(DEP_MAPPING.get("db", {}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate docker-compose files from middleware.config.json")
    parser.add_argument("--config", default="middleware.config.json", help="Path to middleware.config.json")
    parser.add_argument("--base-output", default="requirements.txt", help="Output path for docker-compose.yml")

    args = parser.parse_args()

    config = load_config(args.config)
    validate_config(config)
    generate(config, args.base_output)
