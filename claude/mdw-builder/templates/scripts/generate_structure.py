#!/usr/bin/env python3
"""
generate_structure.py
Generates the full mdw project directory structure based on middleware.config.json.
Creates folders and placeholder files only — no logic is written.

Usage:
    python templates/scripts/generate_structure.py --config middleware.config.json
"""

import argparse
import json
import os
import sys


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        print(f"[ERROR] Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def validate_config(config: dict):
    required = ["project_name", "services", "mdw_features", "core_domains", "django_version", "python_version"]
    missing = [k for k in required if k not in config]
    if missing:
        print(f"[ERROR] Missing required config keys: {missing}")
        sys.exit(1)


def make_dir(path: str):
    os.makedirs(path, exist_ok=True)
    print(f"  [dir]  {path}")


def make_file(path: str, content: str = ""):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(content)
        print(f"  [file] {path}")
    else:
        print(f"  [skip] {path} already exists")


def make_init(path: str):
    make_file(os.path.join(path, "__init__.py"))


def make_placeholder(path: str, classname: str = "", note: str = ""):
    lines = ["# Auto-generated placeholder — add logic here\n"]
    if note:
        lines.append(f"# {note}\n")
    if classname:
        lines.append(f"\nclass {classname}:\n    pass\n")
    make_file(path, "".join(lines))


def generate(config: dict):
    project = config["project_name"]
    services = config.get("services", [])
    core_domains = config.get("core_domains", [])
    cronjobs = config.get("cronjobs", False)
    admin_config = config.get("admin", {})

    print(f"\n[generate_structure] Scaffolding project: {project}\n")

    # --- scripts/ ---
    scripts_dir = "scripts"
    make_dir(scripts_dir)
    make_file(os.path.join(scripts_dir, "entrypoint.sh"), "#!/bin/bash\n# Populated from templates/scripts/entrypoint.sh\n")
    if cronjobs:
        make_file(os.path.join(scripts_dir, "cronjobs.sh"), "#!/bin/bash\n# Define cron schedules here using supercronic syntax\n")

    # --- mdw/ ---
    mdw = "mdw"
    make_dir(mdw)
    make_init(mdw)
    make_placeholder(os.path.join(mdw, "utils.py"), note="Auth helpers, sanitizers, shared utilities")
    make_placeholder(os.path.join(mdw, "processors.py"), note="Top-level input/output processors")

    # mdw/models/base/
    models_base = os.path.join(mdw, "models", "base")
    make_dir(models_base)
    make_init(os.path.join(mdw, "models"))
    make_init(models_base)
    make_placeholder(os.path.join(models_base, "base_model.py"), classname="MdwBaseModel", note="AbstractBaseModel — id, created_at, updated_at, is_active, meta")
    make_placeholder(os.path.join(models_base, "request_log.py"), classname="MdwRequestLog", note="Logs inbound/outbound API requests")
    if cronjobs or any(f in config.get("mdw_features", []) for f in ["logging"]):
        make_placeholder(os.path.join(models_base, "job_log.py"), classname="MdwJobLog", note="Logs background jobs and cron executions")

    # mdw/models/<domain>/
    for domain in core_domains:
        domain_dir = os.path.join(mdw, "models", domain)
        make_dir(domain_dir)
        make_init(domain_dir)
        make_placeholder(os.path.join(domain_dir, f"{domain}.py"), classname=f"Mdw{domain.capitalize()}", note=f"{domain.capitalize()} domain model")

    # mdw/services/
    services_dir = os.path.join(mdw, "services")
    make_dir(services_dir)
    make_init(services_dir)
    service_class_map = {
        "elasticsearch": "MdwElasticsearch",
        "sftp": "MdwSftp",
        "callcenter": "MdwCallcenter",
    }
    for svc in services:
        classname = service_class_map.get(svc, f"Mdw{svc.capitalize()}")
        make_placeholder(os.path.join(services_dir, f"{svc}.py"), classname=classname, note=f"Populated from templates/services/{svc}.py")

    # mdw/core/
    core_dir = os.path.join(mdw, "core")
    make_dir(core_dir)
    make_init(core_dir)
    core_roles = ["handlers", "processors", "pipelines", "resolvers"]
    role_suffix = {"handlers": "Handler", "processors": "Processor", "pipelines": "Pipeline", "resolvers": "Resolver"}
    for role in core_roles:
        role_dir = os.path.join(core_dir, role)
        make_dir(role_dir)
        make_init(role_dir)
        for domain in core_domains:
            classname = f"Mdw{domain.capitalize()}{role_suffix[role]}"
            make_placeholder(os.path.join(role_dir, f"{domain}_{role[:-1]}.py"), classname=classname)

    # mdw/views/external/ and mdw/views/webhooks/
    views_dir = os.path.join(mdw, "views")
    make_dir(views_dir)
    make_init(views_dir)
    for sub in ["external", "webhooks"]:
        sub_dir = os.path.join(views_dir, sub)
        make_dir(sub_dir)
        make_init(sub_dir)

    # mdw/admin/base/filters/ and mdw/admin/base/actions/
    admin_dir = os.path.join(mdw, "admin")
    admin_base = os.path.join(admin_dir, "base")
    filters_dir = os.path.join(admin_base, "filters")
    actions_dir = os.path.join(admin_base, "actions")
    for d in [admin_dir, admin_base, filters_dir, actions_dir]:
        make_dir(d)
        make_init(d)
    make_placeholder(os.path.join(admin_base, "base_admin.py"), classname="MdwBaseAdmin", note="Base admin — readonly fields, ordering, list_per_page")
    if admin_config.get("date_range_filter"):
        make_placeholder(os.path.join(filters_dir, "daterange_filter.py"), classname="DateRangeFilter")
    if admin_config.get("exact_date_filter"):
        make_placeholder(os.path.join(filters_dir, "exactdate_filter.py"), classname="ExactDateFilter")
    if admin_config.get("dedupe_action"):
        make_placeholder(os.path.join(actions_dir, "dedupe_action.py"), classname="RemoveDuplicatesAction")
    for domain in core_domains:
        domain_admin_dir = os.path.join(admin_dir, domain)
        make_dir(domain_admin_dir)
        make_init(domain_admin_dir)
        make_placeholder(os.path.join(domain_admin_dir, f"{domain}_admin.py"), classname=f"Mdw{domain.capitalize()}Admin")

    # --- k8s/ ---
    k8s_base = os.path.join("k8s", "base")
    make_dir(k8s_base)
    for f in ["deployment.yaml", "service.yaml", "configmap.yaml", "secret.yaml"]:
        make_file(os.path.join(k8s_base, f), f"# Populated from templates/k8s/{f}\n")
    if cronjobs:
        make_file(os.path.join(k8s_base, "cronjob.yaml"), "# Populated from templates/k8s/cronjob.yaml\n")
    for env in ["dev", "staging", "prod"]:
        overlay_dir = os.path.join("k8s", "overlays", env)
        make_dir(overlay_dir)
        make_file(os.path.join(overlay_dir, "kustomization.yaml"), f"# Kustomize overlay for {env}\nresources:\n  - ../../base\n")

    # --- root placeholders ---
    make_file(".env.sample", "# Generated by generate_compose.py\n")
    make_file("requirements.txt", "# Generated after dependency resolution\n")
    make_file("settings.py", "# Populated from templates/config/base_settings.py\n")
    make_file(".gitlab-ci.yml", "# Populated from templates/gitlab/.gitlab-ci.yml\n")

    print(f"\n[generate_structure] Done. Structure created for: {project}\n")
    print("Next steps:")
    print("  python templates/scripts/generate_dockerfile.py --config middleware.config.json")
    print("  python templates/scripts/generate_compose.py --config middleware.config.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate mdw project directory structure")
    parser.add_argument("--config", default="middleware.config.json", help="Path to middleware.config.json")
    args = parser.parse_args()

    config = load_config(args.config)
    validate_config(config)
    generate(config)
