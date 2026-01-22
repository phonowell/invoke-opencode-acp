# LLM Quick Card

## Project
- Name: invoke-opencode-acp
- Repo: https://github.com/phonowell/invoke-opencode-acp
- Homepage: none

## Summary
- EN: Claude Code CLI skill that delegates complex tasks to an OpenCode subagent via ACP protocol to save tokens.

## What it does
- Delegate multi-file refactors, batch operations, and code reviews
- Reduce token usage by offloading work to a subagent

## Keywords
- claude-code, opencode, acp-protocol, json-rpc, nodejs, cli, llm-tool

## Install
- npm install -g opencode; cp -r skills/invoke-opencode-acp ~/.claude/skills/

## Quickstart
```bash
node ~/.claude/skills/invoke-opencode-acp/acp_client.cjs "$PWD" "task description" -o /tmp/output.txt -t 300
```

## Docs & API
- Docs: README.md
- API: none

## Examples
- README.md

## License / Citation / Contact
- License: MIT
- Citation: none
- Contact: https://github.com/phonowell/invoke-opencode-acp/issues
