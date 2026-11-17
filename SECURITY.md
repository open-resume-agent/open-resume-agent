# Security Policy

ORA handles personal career data, so privacy bugs count as security bugs.

## In scope
- Anything that discloses an item above the requester's audience: validator, `filter_doc`, public builds (M7), renderers (O1) or the MCP server (X1/X2)
- `never` items appearing in any output (D1, M6)
- Ways to bypass the M8 prompt-injection rule in the compiled Agent Instructions
- Digest or signature checks (M3, I2) that can be bypassed
- Code execution through crafted ORA documents or agent files

## Reporting
Please **don't open a public issue**. Use GitHub's private vulnerability reporting (*Security → Report a vulnerability*). We'll acknowledge within 5 working days and agree a fix and disclosure date with you.

## Supported versions
Only the latest minor version of the spec and tools gets fixes.

## Data in this repo
All example people are fictional. Never commit a real person's private build (`*.private.md` is git-ignored).
