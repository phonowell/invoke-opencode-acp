---
name: invoke-opencode-acp
description: Delegate complex tasks to OpenCode subagent, use when ≥2 file modifications or batch operations
allowed-tools: Bash
---

# invoke-opencode-acp

## When to Use

**Triggers**: ≥2 file modifications · refactoring · batch operations · code review · multi-step reasoning · git operations
**Avoid**: Single-file quick edits · recursive OpenCode calls

**Core intent**: Token savings (50-90%) · main agent focuses on high-level decisions · subagent handles execution details

## Efficiency Priority

`acp_client.cjs` (this directory) > manual protocol · `opencode acp` > run/serve (avoid HTTP)

## Protocol Flow

1. `opencode acp` → stdin/stdout communication
2. `initialize` (protocolVersion: 1 numeric)
3. `session/new` (cwd, mcpServers: [] array)
4. `session/prompt` (prompt: [] array format, not content)
5. Listen for `session/update` → filter `<thinking>` tags
6. Wait for `result.stopReason === 'end_turn'`

**Error codes**: -32001 not found · -32002 rejected · -32003 state · -32601 method · -32602 params

## Usage

```bash
node ~/.claude/skills/invoke-opencode-acp/acp_client.cjs "$PWD" "task description" -o /tmp/output.txt -t 300
```

**Parameters**:
- `-o FILE` (required): Output file · avoids polluting main conversation
- `-t SECONDS`: Timeout in seconds (default: 1800 = 30min)
- `-v`: Verbose mode · protocol messages to stderr

**Timeout guidelines** (OpenCode is slow):
- Simple tasks (math, short answers): 180s (3min) minimum
- Medium tasks (single file, ~100 lines): 600s (10min) minimum
- Complex tasks (multi-file, refactoring): 1800s (30min) minimum

**Output**:
- ✓ Subagent task completed
- ✗ Timeout: {reason}
- ✗ Error: {reason}

## Dependencies

- Node.js
- OpenCode CLI: `npm install -g opencode`
