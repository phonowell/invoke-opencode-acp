# invoke-opencode-acp

Claude Code skill · 委托复杂任务至 OpenCode 子代理 · 节省 50-90% token

## 元原则

**精简冗余**：机器可读 > 人类可读 · 符号/缩写/列表 · 删助词
**冲突信代码**：代码为真 · 文档描述与实现冲突时信代码
**客观诚实**：不主观评价 · 不因用户情绪转移立场 · 不编造事实 · 立刻暴露不确定信息

## Skill 使用

调用后**必须等待完成**再执行其他操作 · 避免立即自行实现

## 核心机制

**Token 节省原理**：委托至 OpenCode → 使用免费替代模型（GLM-4.7/Qwen） → 仅摘要进入主对话
**Tradeoff**：Token 节省（99%）vs 能力下降（替代模型 < Claude）

## 何时使用

**触发条件**：≥2 文件修改 · 重构 · 批量操作 · 代码审查 · 多步推理 · git 操作
**避免**：单文件快速编辑 · 递归调用 OpenCode

## 工作流

### 交互式模式（>30分钟任务）

```bash
# 后台启动
python3 ~/.claude/skills/invoke-opencode-acp/acp_client.py "$PWD" "任务描述" -o /tmp/output.txt
```

**检查循环**（每 5 分钟）：
1. `Bash(..., run_in_background=True)` → 获取 task_id
2. `TaskOutput(task_id, block=True, timeout=300000)` → 等待 5 分钟
3. 状态判断：
   - `completed` → Read 输出文件 → 返回结果
   - `running` → `AskUserQuestion` 是否继续
     - 继续 → 重复步骤 2
     - 终止 → `KillShell(task_id)` 自动清理

### 一次性模式（<30分钟任务）

```bash
python3 ~/.claude/skills/invoke-opencode-acp/acp_client.py "$PWD" "任务描述" -o /tmp/output.txt -t 300
```

**参数**：
- `-o FILE`（必需）：输出文件 · 避免污染主对话
- `-t SECONDS`：超时秒数（默认 1800）
- `-v`：详细模式 · 协议消息至 stderr

## 技术细节

**ACP 协议流程**：
1. `opencode acp` → stdin/stdout 通信
2. `initialize`（protocolVersion: 1 数值型）
3. `session/new`（cwd, mcpServers: [] 数组）
4. `session/prompt`（prompt: [] 数组格式，非 content）
5. 监听 `session/update` → 过滤 `<thinking>` 标签

**错误码**：-32001 未找到 · -32002 拒绝 · -32003 状态 · -32601 方法 · -32602 参数

**输出优化**：自动注入约束（摘要优先 · 过滤 thinking · 仅关键结果）

## 项目结构

```
skills/invoke-opencode-acp/
  SKILL.md           # Skill 定义
  acp_client.py      # ACP 客户端（直接调用）
tests/
  test_acp_client.py # 单元测试
```

## 依赖

- Claude Code CLI（已安装）
- OpenCode CLI：`npm install -g opencode`
- Python 3.7+

## TodoWrite 约束

≥3 步骤任务必须建 todo · 实时更新状态 · 完成立即标记

## 输出约束

禁预告文字 · 状态用符号 ✓/✗/→ · 一次性批量 Edit · 数据优先 · 直达结论 · 工具间隔零输出 · 错误格式 ✗ {位置}:{类型} · 代码块零注释 · ≥2 条用列表 · 路径缩写（. 项目根 · ~ 主目录）· 禁总结性重复 · 进度 {当前}/{总数} · 提问直入

## 子任务模型

Task 工具可用 `model: "haiku"` 节省成本（简单任务）
