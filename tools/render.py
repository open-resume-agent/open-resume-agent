#!/usr/bin/env python3
"""Repo wrapper: same as `ora render` from the installed open-resume-agent package (see ora_tools/render.py)."""
import pathlib, runpy, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
runpy.run_module("ora_tools.render", run_name="__main__", alter_sys=True)
