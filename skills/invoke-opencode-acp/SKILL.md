---
name: invoke-opencode-acp
description: Delegate complex tasks to OpenCode subagent (saves main agent tokens)
allowed-tools: Bash
---

# invoke-opencode-acp

## When to Use

**Aggressive delegation**: ≥2 file modifications or complex tasks · saves main agent tokens (~6s overhead acceptable)

**Applicable scenarios**: Refactoring · batch operations · code review · multi-file changes · independent subtasks · multi-step reasoning · git operations (commit/push/PR)

**Not applicable**: Single-file quick edits · avoid recursive calls within OpenCode

**Key principle**: Provide minimal context (objectives only) · let subagent autonomously analyze (paths/formats/details)

## Efficiency Priority

`acp_client.py` (this directory) > manual protocol · `opencode acp` > run/serve (avoid HTTP)

## Protocol Essentials

**Flow**: Launch `opencode acp` → initialize (protocolVersion: 1 numeric) → session/new (mcpServers: [] array) → session/prompt (prompt: [] array, not content) → listen for session/update

**Error codes**: -32001 not found · -32002 rejected · -32003 state · -32004 unsupported · -32601 method · -32602 params

**Constraints**: Continuous streaming · select/non-blocking IO · independent sessionId for concurrency · terminate/kill for cleanup

## Usage

### Interactive Mode (Recommended, supports timeout decisions)

**Launch task in background**:
```bash
python3 ~/.claude/skills/invoke-opencode-acp/acp_client.py "$PWD" "task description" -o /tmp/opencode_output.txt
```

**Main agent check loop** (every 5 minutes):
1. Use `Bash(..., run_in_background=True)` to start task, get task_id
2. Use `TaskOutput(task_id, block=True, timeout=300000)` to wait 5 min
3. Check status:
   - If `status == "completed"`: Read output file, return result
   - If `status == "running"`: AskUserQuestion whether to continue
     - User chooses continue: repeat step 2
     - User chooses terminate: `KillShell(task_id)` auto-cleanup

**Advantages**:
- Maintains OpenCode session without interruption
- User can decide at each checkpoint
- Main agent can auto-kill and cleanup processes

### One-shot Mode (for quick tasks)

```bash
python3 ~/.claude/skills/invoke-opencode-acp/acp_client.py "$PWD" "task" -o /tmp/output.txt -t 300
```

**Parameters**:
- `-o FILE` (required): Output file path, **avoids polluting main agent context**
- `-t SECONDS`: Timeout in seconds (default: 1800s = 30 min)
- `-v`: Verbose mode, protocol messages to stderr (for debugging)

**Token optimization**: Subagent output auto-injected with constraints (summary-first · filter thinking · key results only)

## Output

**Interactive mode**:
- Task running: Ask every 5 min whether to continue
- User confirms continue: Extend wait time
- User chooses terminate: Auto-kill process
- Task completed: ✓ Subagent task completed

**One-shot mode**:
- ✓ Subagent task completed
- ✗ Timeout/Error: {reason}
