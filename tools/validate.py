#!/usr/bin/env python3
"""Repo wrapper: same as `ora validate` from the installed open-resume-agent package (see ora_tools/validate.py)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from ora_tools.validate import main
sys.exit(main(sys.argv[1:]))
