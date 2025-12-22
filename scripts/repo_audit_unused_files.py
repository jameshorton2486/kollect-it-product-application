#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repo Audit Script
Finds Python files not imported by main.py
"""

from pathlib import Path
import ast
import sys
import io

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path("desktop-app")
MAIN = ROOT / "main.py"

imports = set()

def collect_imports(file_path):
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8", errors="ignore"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
    except Exception:
        pass

collect_imports(MAIN)

all_py_files = list(ROOT.rglob("*.py"))
unused = []

for f in all_py_files:
    if f.name == "main.py":
        continue
    if f.parent.name == "modules":
        continue
    if f.stem not in imports:
        unused.append(f)

print("\n📦 UNUSED / UNIMPORTED FILES:")
for f in unused:
    print(" -", f)

print(f"\nTotal unused files: {len(unused)}")
