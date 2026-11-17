#!/usr/bin/env python3
"""Repo wrapper: same as `ora build_md` from the installed ora-tools package (see ora_tools/build_md.py)."""
import pathlib, runpy, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
runpy.run_module("ora_tools.build_md", run_name="__main__", alter_sys=True)
