# GitHub LLM 可发现性报告

- 项目: invoke-opencode-acp
- Repo: https://github.com/phonowell/invoke-opencode-acp
- 范围: ./README.md, ./README.zh.md, ./README.ja.md, ./skills/invoke-opencode-acp/SKILL.md, ./skills/invoke-opencode-acp/acp_client.cjs, ./tests/test_acp_client.js, ./LICENSE
- 元数据: description=Save 50-90% tokens in Claude Code by delegating complex tasks to OpenCode subagent. Uses free alternative models with slightly lower reasoning capability for significant cost savings. | homepage=none | topics=agent-delegation, claude-code, claude-skills, cost-saving, opencode, token-optimization

## 诊断(按严重度)

- ✗ 高: 缺 `./llms.txt`、`./llms.md`
- → 中: `./README.md` 缺 LLM 友好摘要/关键词/快速入口小节
- → 中: topics 缺 `acp-protocol`/`json-rpc`/`nodejs`/`cli`/`llm-tool`
- → 低: `./docs` 为空，文档集中在 `./README.md`
- ✓ 低: `./LICENSE`=MIT；多语 README 完整

## 模板草案

`./llms.txt`
```
Project: invoke-opencode-acp
Repository: https://github.com/phonowell/invoke-opencode-acp
Homepage: none

Summary (EN): Claude Code CLI skill that delegates complex tasks to an OpenCode subagent via ACP protocol to save tokens.
摘要 (ZH): Claude Code CLI 技能，通过 ACP 协议把复杂任务委托给 OpenCode 子代理以节省 token。

Primary use cases (EN):
- Multi-file refactors and batch operations
- Code reviews or long-running tasks via subagent
主要用途 (ZH):
- 多文件重构与批量操作
- 子代理执行代码审查或耗时任务

Keywords (EN): claude-code, opencode, acp-protocol
关键词 (ZH): Claude Code, OpenCode, ACP 协议

Install (EN): npm install -g opencode; cp -r skills/invoke-opencode-acp ~/.claude/skills/
安装 (ZH): npm install -g opencode；cp -r skills/invoke-opencode-acp ~/.claude/skills/

Quick usage (EN):
- node ~/.claude/skills/invoke-opencode-acp/acp_client.cjs "$PWD" "task description" -o /tmp/output.txt -t 300
快速使用 (ZH):
- node ~/.claude/skills/invoke-opencode-acp/acp_client.cjs "$PWD" "任务描述" -o /tmp/output.txt -t 300

API/Docs: ./README.md
Examples: ./README.md
License: MIT
Citation: none
Contact: https://github.com/phonowell/invoke-opencode-acp/issues
```

`./llms.md`
```markdown
# LLM Quick Card

## Project
- Name: invoke-opencode-acp
- Repo: https://github.com/phonowell/invoke-opencode-acp
- Homepage: none

## Summary
- EN: Claude Code CLI skill that delegates complex tasks to an OpenCode subagent via ACP protocol to save tokens.
- ZH: Claude Code CLI 技能，通过 ACP 协议把复杂任务委托给 OpenCode 子代理以节省 token。

## What it does / 主要用途
- EN: delegate multi-file refactors, batch operations, and code reviews
- ZH: 委托多文件重构、批量操作与代码审查

## Keywords / 关键词
- EN: claude-code, opencode, acp-protocol
- ZH: Claude Code, OpenCode, ACP 协议

## Install / 安装
- EN: npm install -g opencode; cp -r skills/invoke-opencode-acp ~/.claude/skills/
- ZH: npm install -g opencode；cp -r skills/invoke-opencode-acp ~/.claude/skills/

## Quickstart / 快速开始
```bash
node ~/.claude/skills/invoke-opencode-acp/acp_client.cjs "$PWD" "task description" -o /tmp/output.txt -t 300
```

## Docs & API
- Docs: ./README.md
- API: none

## Examples
- ./README.md

## License / Citation / Contact
- License: MIT
- Citation: none
- Contact: https://github.com/phonowell/invoke-opencode-acp/issues
```

`./README.md` 章节
```markdown
## LLM Friendly Summary / LLM 友好摘要

**EN:** Claude Code CLI skill that delegates complex tasks to an OpenCode subagent via ACP protocol to save tokens.
**ZH:** Claude Code CLI 技能，通过 ACP 协议把复杂任务委托给 OpenCode 子代理以节省 token。

### Quickstart / 快速开始
```bash
npm install -g opencode
cp -r skills/invoke-opencode-acp ~/.claude/skills/
node ~/.claude/skills/invoke-opencode-acp/acp_client.cjs "$PWD" "任务描述" -o /tmp/output.txt -t 300
```

### Key Capabilities / 核心能力
- EN: delegate complex tasks to an OpenCode subagent; reduce token usage; output results to file
- ZH: 将复杂任务委托给 OpenCode 子代理；节省 token；结果输出到文件

### Typical Use Cases / 典型场景
- EN: multi-file refactors, batch operations, code reviews
- ZH: 多文件重构、批量操作、代码审查

### Keywords / 关键词
- EN: claude-code, opencode, acp-protocol
- ZH: Claude Code, OpenCode, ACP 协议

### Docs & API / 文档与 API
- Docs: ./README.md
- API: none
- Examples: ./README.md
```

## 元数据建议

- → description: Claude Code CLI skill that delegates complex tasks to an OpenCode subagent via ACP protocol, saving 50-90% tokens.
- → topics: claude-code, claude-skills, opencode, acp-protocol, json-rpc, nodejs, cli, agent-delegation, token-optimization, llm-tool

## 待确认修改清单

- → 新增 `./llms.txt`
- → 新增 `./llms.md`
- → 更新 `./README.md` 加入 LLM 章节
- → `gh repo edit` 更新 description/topics
