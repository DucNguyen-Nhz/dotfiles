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


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        print(f"[ERROR] Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def validate_config(config: dict):
    required = ["python_version", "django_version", "services", "mdw_features"]
    missing = [k for k in required if k not in config]
    if missing:
        print(f"[ERROR] Missing required config keys: {missing}")
        sys.exit(1)


def resolve_system_deps(services: list) -> list:
    """Map services to required system-level apt packages."""
    deps = []
    if "sftp" in services:
        deps.append("openssh-client")
    if "elasticsearch" in services:
        pass  # no extra system deps needed
    return deps


def resolve_pip_deps(services: list, features: list, django_version: str) -> list:
    """Map services and features to pip packages."""
    packages = ["djangorestframework", "python-decouple", "gunicorn", "psycopg2-binary", "celery", "redis"]

    if django_version == "latest":
        packages.append("django --upgrade")
    else:
        packages.append(f"django=={django_version}")

    service_map = {
        "elasticsearch": ["elasticsearch", "django-elasticsearch-dsl"],
        "sftp": ["paramiko"],
    }
    feature_map = {
        "retry": ["tenacity"],
        "transform": ["pydantic"],
        "auth": ["djangorestframework-simplejwt"],
    }

    for svc in services:
        packages.extend(service_map.get(svc, []))
    for feat in features:
        packages.extend(feature_map.get(feat, []))

    return packages


def generate(config: dict, output_path: str = "Dockerfile"):
    python_version = config["python_version"]
    django_version = config["django_version"]
    services = config.get("services", [])
    features = config.get("mdw_features", [])
    cronjobs = config.get("cronjobs", False)

    system_deps = resolve_system_deps(services)
    pip_deps = resolve_pip_deps(services, features, django_version)

    lines = []

    # Base image
    lines.append(f"FROM python:{python_version}-slim\n")
    lines.append("")

    # Environment
    lines.append("ENV PYTHONDONTWRITEBYTECODE=1 \\")
    lines.append("    PYTHONUNBUFFERED=1 \\")
    lines.append("    PIP_NO_CACHE_DIR=1\n")

    # Working directory
    lines.append("WORKDIR /app\n")

    # System dependencies
    apt_packages = ["gcc", "libpq-dev", "curl", "bash"]
    apt_packages.extend(system_deps)
    if cronjobs:
        apt_packages.append("wget")  # needed to download supercronic
    lines.append("RUN apt-get update && apt-get install -y --no-install-recommends \\")
    for i, pkg in enumerate(apt_packages):
        suffix = " \\" if i < len(apt_packages) - 1 else ""
        lines.append(f"    {pkg}{suffix}")
    lines.append("    && apt-get clean && rm -rf /var/lib/apt/lists/*\n")

    # Supercronic (if cronjobs enabled)
    if cronjobs:
        lines.append("# Install supercronic for cron support")
        lines.append('RUN SUPERCRONIC_URL="https://github.com/aptible/supercronic/releases/latest/download/supercronic-linux-amd64" \\')
        lines.append('    && curl -fsSLO "$SUPERCRONIC_URL" \\')
        lines.append('    && chmod +x supercronic-linux-amd64 \\')
        lines.append('    && mv supercronic-linux-amd64 /usr/local/bin/supercronic\n')

    # Python dependencies
    lines.append("COPY requirements.txt .")
    lines.append("RUN pip install --upgrade pip \\")
    for i, pkg in enumerate(pip_deps):
        suffix = " \\" if i < len(pip_deps) - 1 else ""
        lines.append(f"    && pip install {pkg}{suffix}")
    lines.append("")

    # Copy project
    lines.append("COPY . .\n")

    # Scripts
    chmod_targets = "scripts/entrypoint.sh"
    if cronjobs:
        chmod_targets += " scripts/cronjobs.sh"
    lines.append(f"RUN chmod +x {chmod_targets}\n")

    # Port
    lines.append("EXPOSE 8000\n")

    # Entrypoint
    lines.append('ENTRYPOINT ["scripts/entrypoint.sh"]')

    dockerfile_content = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(dockerfile_content)

    print(f"[generate_dockerfile] Dockerfile written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Dockerfile from middleware.config.json")
    parser.add_argument("--config", default="middleware.config.json", help="Path to middleware.config.json")
    parser.add_argument("--output", default="Dockerfile", help="Output path for Dockerfile")
    args = parser.parse_args()

    config = load_config(args.config)
    validate_config(config)
    generate(config, output_path=args.output)
