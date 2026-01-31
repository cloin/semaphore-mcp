# Pull request: add delete_access_key MCP tool

We wanted to be able to delete access keys from the key store via MCP.

**Changes:**
- Expose `delete_access_key(project_id, key_id)` as an MCP tool. The API client already had the method; this wires it through and registers it.
- Add unit tests and E2E test for delete.
- Document Access keys in README Available Tools.

**Open the PR manually:** https://github.com/cloin/semaphore-mcp/compare/main...SpaceTerran:feature/delete-access-key

Or from the fork: https://github.com/SpaceTerran/semaphore-mcp/pull/new/feature/delete-access-key (then change base repo to `cloin/semaphore-mcp` and base branch to `main`).

**Title:** `feat: add delete_access_key MCP tool`

**Body:** (use the text above under "We wanted to be able to delete...")
