[English](README.md) | [中文](README.zh.md)

# invoke-opencode-acp

**A skill for [Claude Code CLI](https://claude.ai/code)** that saves thousands of tokens by delegating complex tasks to OpenCode subagent.

> **Note**: This is a skill for the Claude Code CLI tool, not a standalone application. You must have Claude Code installed to use it.
> 
> **Requirements**: This skill requires **OpenCode** (via ACP protocol) and **Python 3.7+** to function.

## What This Skill Does

**Delegates complex tasks to a separate AI agent** (OpenCode) through the ACP protocol, saving your main Claude conversation from consuming excessive tokens.

Think of it as hiring a specialized contractor: you provide the objective, they do the work independently, and you get the results without all the back-and-forth that would fill your conversation history.

## Benefits

### Massive Token Savings

- **Without this skill**: Main Claude reads every file → analyzes → edits → repeats. Each iteration consumes thousands of tokens.
- **With this skill**: Send objective to subagent → subagent works independently → get final results. Only the summary enters your conversation.

**Typical savings**: 50-90% fewer tokens for complex tasks.

### Important Trade-off

**How it achieves savings**: OpenCode subagent uses free tokens to call alternative models (e.g., GLM-4.7, Qwen) instead of your paid Claude tokens.

**What this means**:
- ✅ **Token savings**: You pay nothing for the subagent's work
- ⚠️ **Capability trade-off**: Alternative models have lower reasoning ability compared to Claude
- ⚠️ **Quality variance**: Results may be less nuanced or require review

**Best use cases**:
- Code refactoring and formatting (straightforward)
- Documentation updates and generation
- Test code generation
- Bug fixes with clear requirements
- Batch file operations

**Consider alternatives for**:
- Complex architecture decisions
- Nuanced code reviews
- Sensitive logic changes
- Tasks requiring deep domain expertise

### Faster Task Completion

- Main Claude stays responsive for other tasks
- Subagent works in parallel
- No context window limitations for the subtask

### Better for Complex Workflows

Perfect for:
- **Multi-file refactoring**: "Add type hints to all Python files"
- **Batch operations**: "Update all documentation files"
- **Code reviews**: "Review the entire codebase for security issues"
- **Git workflows**: "Create a pull request with these changes"

## How It Works

1. **You describe the task** (one sentence is enough)
2. **OpenCode subagent receives your objective** and works independently
3. **Results are saved** to a file (not your conversation)
4. **You get a concise summary** in your main conversation

The subagent can read files, make edits, run tests, and more—just like a full developer—without consuming your main conversation's context.

## Installation

### Prerequisites

You need three things installed:

1. **Claude Code CLI** (already installed if you're using this)
2. **OpenCode CLI** (`npm install -g opencode`)
3. **Python 3.7+** (comes with most systems)

### Quick Install

```bash
# 1. Install OpenCode (if not already)
npm install -g opencode

# 2. Copy the skill to Claude
cp -r skills/invoke-opencode-acp ~/.claude/skills/

# 3. Verify it works (optional)
python3 -m unittest tests/test_acp_client.py
```

### Verify Installation

Check that OpenCode is installed:
```bash
opencode --version
```

Check that the skill exists:
```bash
ls ~/.claude/skills/invoke-opencode-acp/SKILL.md
```

## Usage

### For Long Tasks (Interactive Mode)

Best for tasks that take more than 30 minutes or where you want to monitor progress.

Simply tell Claude what you want done:

> "Refactor all Python files in this project to use type hints"

Claude will:
1. Launch the subagent in the background
2. Check progress every 5 minutes
3. Ask if you want to continue or stop
4. Deliver the results when done

**Example tasks for interactive mode**:
- "Refactor the entire codebase"
- "Run comprehensive security audit"
- "Generate documentation for all APIs"

### For Quick Tasks (One-shot Mode)

Best for tasks that take less than 30 minutes.

> "Update the README.md with new installation instructions"

Claude will execute and return results directly.

**Example tasks for one-shot mode**:
- "Update a single document"
- "Fix a specific bug"
- "Add a small feature"

## Real-World Examples

### Example 1: Large Refactoring

**Your request**: "Add type hints to all Python files in this project"

**Without this skill**:
- Claude reads each file (10,000 tokens)
- Claude edits each file (15,000 tokens)
- Claude verifies changes (8,000 tokens)
- **Total**: ~33,000 tokens consumed

**With this skill**:
- You send the objective (50 tokens)
- Subagent works independently (0 tokens in your conversation)
- You get a summary (200 tokens)
- **Total**: ~250 tokens consumed

**Savings**: 99% token reduction!

### Example 2: Code Review

**Your request**: "Review the entire codebase for security vulnerabilities"

**Without this skill**:
- Claude reads every source file (25,000 tokens)
- Claude analyzes and documents (12,000 tokens)
- **Total**: ~37,000 tokens

**With this skill**:
- Objective + summary (~300 tokens)
- **Total**: ~300 tokens

**Savings**: 99% token reduction!

### Example 3: Batch Documentation Updates

**Your request**: "Update all .md files to include the new license header"

**Without this skill**:
- Claude reads 20 markdown files (15,000 tokens)
- Claude edits each file (20,000 tokens)
- **Total**: ~35,000 tokens

**With this skill**:
- Objective + summary (~250 tokens)
- **Total**: ~250 tokens

**Savings**: 99% token reduction!

## When to Use

**✅ Use this skill for**:
- Tasks affecting 2+ files
- Refactoring or restructuring
- Batch operations (find and replace across many files)
- Code reviews across the entire codebase
- Multi-step tasks requiring research and analysis
- Git workflows (commit, push, pull request)

**❌ Don't use for**:
- Single file quick edits
- Simple text replacements
- Tasks requiring integration with your main conversation

## How This Is Different

### vs. Normal Claude Tasks

| Aspect | Normal Claude | With invoke-opencode-acp |
|--------|--------------|-------------------------|
| Context usage | Full file contents | Just objective |
| Token consumption | High (thousands) | Low (hundreds) |
| Your conversation | Shows all steps | Shows only results |
| Speed | Sequential | Parallel |
| Best for | Simple tasks | Complex tasks |

### vs. Other Solutions

- **Claude Projects**: Still uses main context window (limited tokens)
- **Manual delegation**: Requires copy-pasting, no automation
- **invoke-opencode-acp**: Automated delegation with minimal context usage

## Troubleshooting

**"opencode command not found"**
```bash
npm install -g opencode
```

**"Skill not enabled"**
- Check the skill is in `~/.claude/skills/invoke-opencode-acp/`
- Restart Claude Code
- Enable in Claude Code settings

**Task timeout**
- Long tasks will automatically use interactive mode
- You'll be asked to continue or stop every 5 minutes

## Technical Details (For the Curious)

This skill uses the ACP (Agent Control Protocol) to communicate with OpenCode. It:

1. Launches OpenCode in the background
2. Creates a dedicated session
3. Sends your task objective
4. Filters out internal "thinking" (no need to see the reasoning)
5. Returns only the key results

The ~6 second initialization overhead is negligible compared to the token savings for complex tasks.

## License

MIT License - See [LICENSE](LICENSE) for details.

---

中文版本：[README.zh.md](README.zh.md)
