import argparse
import json
import os
import sys
import subprocess

from pathlib import Path
 
DEFAULT_IGNORE = {"__pycache__", ".git", ".DS_Store", "node_modules", ".venv", ".mypy_cache"}
 
 
def generate_tree(root, annotations=None, ignore=None, max_depth=None):
    """
    Build an ASCII tree diagram of the folder structure rooted at `root`.
 
    Args:
        root: path to the root directory to traverse.
        annotations: optional dict mapping relative paths (posix-style,
            relative to root, e.g. "scripts/cronjobs.sh") to a trailing
            comment, e.g. "only if cronjobs: true".
        ignore: optional set of file/dir names to skip entirely.
        max_depth: optional int limiting recursion depth (1 = root's
            direct children only).
 
    Returns:
        The tree as a single string, ready to print or write to a file.
    """
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"{root_path} is not a directory")
 
    ignore = set(ignore) if ignore is not None else DEFAULT_IGNORE
    annotations = annotations or {}
 
    lines = [f"{root_path.name}/"]
 
    def _walk(dir_path, prefix, rel_path, depth):
        if max_depth is not None and depth > max_depth:
            return
 
        try:
            entries = [e for e in dir_path.iterdir() if e.name not in ignore]
        except PermissionError:
            return
 
        # directories first, then files, alphabetically within each group
        entries.sort(key=lambda e: (e.is_file(), e.name.lower()))
 
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            entry_rel = f"{rel_path}/{entry.name}" if rel_path else entry.name
            display_name = entry.name + ("/" if entry.is_dir() else "")
 
            line = f"{prefix}{connector}{display_name}"
            comment = annotations.get(entry_rel)
            if comment:
                pad = max(1, 40 - len(prefix) - len(connector) - len(display_name))
                line += " " * pad + f"# {comment}"
            lines.append(line)
 
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                _walk(entry, prefix + extension, entry_rel, depth + 1)
 
    _walk(root_path, "", "", 1)
    return "\n".join(lines)
 

def has_django():
    # sys.executable ensures we use the pip tied to whatever Python
    # is running this script (venv or system), no activation needed.
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True
    )
    packages = result.stdout.lower()
    return any("django" in line for line in packages.splitlines())

def is_django_project(path: str):
    
    filepaths = os.listdir(path)
    requirement = ""
    venv = ""

    for file in filepaths:
        
        if "requirement" in file and not requirement:
            requirement = os.path.join(path, file)
        
        if "venv" in file:
            venv = os.path.join(path, file)
    
    check_venv = False
    if requirement is None:
        print("Warning: No requirement file found, check for venv")
        check_venv = True
    
    is_django_project = False
    if os.path.isfile(requirement):
        
        with open(requirement, "r", encoding="utf-8") as f:
            for line in f.readlines():
                if "django" in line.lower():
                    is_django_project = True
                    break

    if check_venv and not is_django_project:
        if os.path.isdir(venv):
            is_django_project = has_django()

    return is_django_project


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="", help="working directory")
    parser.add_argument("--output", default="", help="structure output")
    args = parser.parse_args()

    wd = args.path 
    output = args.output
    
    if wd is None or (not os.path.isdir(wd)):
        print(f"Not a valid path: {wd}")
        sys.exit(0)

    if not is_django_project(wd):
        print(f"{wd} is not a Django project")
        sys.exit(0)
    
    with open(output, "r", encoding="utf-8") as f:
        structure = generate_tree(wd)
        f.write(structure)

    
