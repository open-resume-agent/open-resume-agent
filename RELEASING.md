# Releasing

Everything runs locally. Nothing runs on GitHub.

## 1. Prepare
```bash
make check                  # stale-file check, validation, all tests
# bump: pyproject.toml version, ora_tools/__init__.py, server.json (both versions), CHANGELOG.md
```

## 2. Publish the Python package (PyPI)
One-time: create a PyPI account, enable 2FA, and create an API token scoped to `ora-tools` (the first upload needs an account-wide token).
```bash
pip install build twine
make package                # builds dist/*.whl and dist/*.tar.gz
twine upload dist/*         # username: __token__ · password: your PyPI token
```

## 3. List the MCP server (MCP Registry)
The registry checks that the PyPI package exists and that its README contains
`mcp-name: io.github.open-resume-agent/ora-mcp` (it does).
```bash
brew install mcp-publisher  # or download the binary from the registry releases
mcp-publisher validate      # checks server.json
mcp-publisher login github  # sign in as a member of the open-resume-agent org
mcp-publisher publish
```

## 4. Tag and announce
Create the GitHub release `vX.Y.Z` (paste the CHANGELOG section) and post in Discussions → Announcements.
