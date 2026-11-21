# Releasing

Publishing a GitHub release does the rest: `.github/workflows/publish.yml` checks the versions,
runs the tests, uploads to PyPI with trusted publishing, then lists the server in the MCP Registry.
No tokens are stored anywhere.

## 1. Prepare (pull request)
```bash
make check                  # stale-file check, validation, all tests
ruff check ora_tools tools tests
# bump: pyproject.toml version, ora_tools/__init__.py, server.json (both versions), CITATION.cff (version, date-released)
# CHANGELOG.md: rename "Unreleased" to "X.Y.Z — YYYY-MM-DD"
```
Open a pull request, wait for CI, and merge it.

## 2. Publish
Create the GitHub release `vX.Y.Z` on the merge commit and paste the CHANGELOG section as notes.
The release tag must equal the version in `pyproject.toml`, `ora_tools/__init__.py` and `server.json`, or the workflow stops before uploading.
The workflow then:
- uploads the wheel and sdist to PyPI (trusted publishing, environment `pypi`)
- signs in to the MCP Registry with GitHub OIDC and publishes `server.json`. The registry checks that the PyPI
  package exists and that its README contains `mcp-name: io.github.open-resume-agent/ora-mcp` (it does), and
  that the `server.json` description is 100 characters or fewer.

Zenodo archives every published release automatically and mints a version DOI. The README and `CITATION.cff`
use the all-versions DOI, so they never need updating.

## 3. Announce
Post in Discussions → Announcements.

## Manual fallback
If the workflow cannot run, publish from a checkout:
```bash
make package && twine upload dist/*                 # PyPI token in ~/.pypirc
mcp-publisher login github --token <classic PAT with read:org only> && mcp-publisher publish
```
The interactive `mcp-publisher login github` cannot publish under the organization namespace.
