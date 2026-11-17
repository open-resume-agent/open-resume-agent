"""`ora` command line: build · validate · render · card · mcp.

  ora build   resume-agent.json -o resume-agent.md [--build public|private|<audience>]
  ora validate resume-agent.md [more files] [--today YYYY-MM-DD]
  ora render  resume-agent.md --format docx|pdf|html|md|txt|json-resume [--view ID] [--audience A] [--template T]
  ora card    resume-agent.json            # A2A Agent Card to stdout
  ora mcp     resume-agent.md              # MCP server over stdio (also: ora-mcp)
"""
import runpy, sys

from . import __version__

COMMANDS = {"build": "build_md", "validate": "validate", "render": "render", "card": "to_agent_card", "mcp": "ora_mcp"}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__); return 0
    if argv[0] in ("-V", "--version"):
        print(f"ora-tools {__version__}"); return 0
    cmd, rest = argv[0], argv[1:]
    if cmd not in COMMANDS:
        print(f"unknown command '{cmd}'\n{__doc__}", file=sys.stderr); return 2
    sys.argv = [f"ora {cmd}"] + rest
    if cmd == "validate":
        from .validate import main as vmain
        return vmain(rest)
    runpy.run_module(f"ora_tools.{COMMANDS[cmd]}", run_name="__main__", alter_sys=True)
    return 0


def mcp_main():
    sys.argv = ["ora-mcp"] + sys.argv[1:]
    runpy.run_module("ora_tools.ora_mcp", run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    sys.exit(main())
