#!/usr/bin/env python3
"""Repo wrapper: same as `ora to_agent_card` from the installed open-resume-agent package (see ora_tools/to_agent_card.py)."""
import pathlib, runpy, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
runpy.run_module("ora_tools.to_agent_card", run_name="__main__", alter_sys=True)
