#!/usr/bin/env python3
"""Repo wrapper: same as `ora ora_mcp` from the installed ora-tools package (see ora_tools/ora_mcp.py)."""
import pathlib, runpy, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
runpy.run_module("ora_tools.ora_mcp", run_name="__main__", alter_sys=True)
