<div align="center">

# Anchor Stack

<img src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"/>
<img src="https://img.shields.io/badge/MCP-1.25+-green?style=for-the-badge&logo=anthropic&logoColor=white" alt="MCP 1.25+"/>
<img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="MIT License"/>
<img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge" alt="PRs Welcome"/>

**AI 友好的工程化基础设施**

*稳定的版本 · 统一的日志 · 可插拔的能力包*

[English](./README.md) | [中文](./README_CN.md)

---

</div>

## 为什么需要 Anchor Stack？

你是否有过这样的经历？

> *"AI 帮我写了代码，但调试花的时间比自己写还长..."*

问题不在 AI，而在于 **你的项目没有为 AI 协作而设计**。

Anchor Stack 通过以下方式解决这个问题：

| 问题 | 解决方案 |
|------|----------|
| 日志不统一 | 标准化的 `logger` 模块 - AI 知道如何添加日志 |
| 环境变量混乱 | 类型安全的 `config` 模块 - 告别散落的 `process.env` |
| 版本冲突 | 精选的依赖版本 - 经过测试，稳定可靠 |
| AI 不理解项目 | Rules 文件教会 AI 你的项目规范 |

## 核心特性

- **稳定的技术栈** - 精选的技术组合，版本锁定，避免兼容性问题
- **统一的日志框架** - 标准化的日志模块，AI 可以正确添加日志
- **AI Rules 文件** - 自动生成 Claude、Cursor、Windsurf 等工具的规则文件
- **可插拔的能力包** - 按需添加数据库、AI、认证等能力
- **MCP 原生支持** - 与所有 MCP 兼容的 AI 工具无缝集成

## 快速开始

### 安装

```bash
# 使用 pip
pip install anchor-stack

# 使用 uv（推荐）
uv pip install anchor-stack
```

### 配置 AI 工具

<details>
<summary><b>Claude Desktop</b></summary>

编辑配置文件：
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "anchor-stack": {
      "command": "anchor-stack",
      "args": ["serve"]
    }
  }
}
```

</details>

<details>
<summary><b>Cursor</b></summary>

编辑 `~/.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "anchor-stack": {
      "command": "anchor-stack",
      "args": ["serve"]
    }
  }
}
```

</details>

<details>
<summary><b>VS Code (Copilot)</b></summary>

编辑 `.vscode/settings.json`：

```json
{
  "mcp": {
    "servers": {
      "anchor-stack": {
        "command": "anchor-stack",
        "args": ["serve"]
      }
    }
  }
}
```

</details>

### 创建你的第一个项目

只需告诉你的 AI 助手：

```
使用 Anchor Stack 创建一个名为 "my-app" 的 Next.js 项目
```

AI 会调用 `scaffold_project` 工具创建：

```
my-app/
├── src/
│   ├── app/              # Next.js App Router
│   ├── components/       # React 组件
│   ├── lib/
│   │   ├── core/         # Logger & Config（请勿修改）
│   │   └── utils/        # 工具函数
│   └── services/         # 业务逻辑
├── CLAUDE.md             # Claude 规则文件
├── .cursor/rules/        # Cursor 规则文件
├── .windsurfrules        # Windsurf 规则文件
└── anchor.config.json    # 项目元数据
```

## 可用工具

### `scaffold_project`

从 Stack 模板创建新项目。

```typescript
scaffold_project({
  stack_name: "nextjs",        // 技术栈类型
  project_name: "my-app",      // 项目名称
  target_dir: "/path/to/dir"   // 目标目录
})
```

### `add_pack`

向现有项目添加能力包。

```typescript
add_pack({
  project_dir: "/path/to/project",
  pack_name: "database-postgres"
})
```

### `doctor`

检查项目健康状态和配置。

```typescript
doctor({
  project_dir: "/path/to/project"
})
```

## 可用的技术栈

| Stack | 版本 | 描述 |
|-------|------|------|
| `nextjs` | 2026.1 | Next.js 16 + React 19 + TypeScript 5.9 + Tailwind CSS |
| `fastapi` | 2026.1 | FastAPI 0.128 + SQLAlchemy 2.0 + Pydantic v2 |

## 可用的能力包

| Pack | 描述 |
|------|------|
| `database-postgres` | PostgreSQL，配合 Drizzle ORM (JS) 或 SQLAlchemy (Python) |
| `ai-langgraph` | LangChain + LangGraph，用于 AI 应用开发 |

## 工作原理

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│    AI 助手      │────▶│   Anchor Stack   │────▶│    你的项目     │
│ (Claude, etc.)  │     │   (MCP Server)   │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              ┌──────────┐         ┌──────────┐
              │  Stacks  │         │  Packs   │
              │ (技术栈)  │         │ (能力包) │
              └──────────┘         └──────────┘
```

1. **你提问** - 让 AI 创建项目
2. **AI 调用** - Anchor Stack 的 MCP 工具
3. **Anchor Stack 生成** - 规范的项目结构
4. **AI Rules** - 帮助后续 AI 交互理解你的项目

## CLI 命令

```bash
# 启动 MCP 服务器
anchor-stack serve

# 列出可用的技术栈
anchor-stack list-stacks

# 列出可用的能力包
anchor-stack list-packs

# 显示配置信息
anchor-stack info
```

## 配置选项

| 环境变量 | 默认值 | 描述 |
|----------|--------|------|
| `ANCHOR_STACK_LOG_LEVEL` | `INFO` | 日志级别 (DEBUG, INFO, WARNING, ERROR) |
| `ANCHOR_STACK_LOG_JSON` | `false` | 以 JSON 格式输出日志 |
| `ANCHOR_STACK_STACKS_DIR` | `stacks` | 自定义技术栈目录 |
| `ANCHOR_STACK_PACKS_DIR` | `packs` | 自定义能力包目录 |

## 开发指南

```bash
# 克隆仓库
git clone https://github.com/anthropics/anchor-stack.git
cd anchor-stack

# 安装依赖
uv sync

# 运行测试
uv run pytest tests/ -v

# 运行代码检查
uv run ruff check src/

# 启动开发服务器
uv run anchor-stack serve
```

## 路线图

- [x] 核心 MCP Server 实现
- [x] Next.js 技术栈模板
- [x] FastAPI 技术栈模板
- [ ] 数据库能力包 (PostgreSQL)
- [ ] AI 能力包 (LangGraph)
- [ ] 认证能力包 (NextAuth/OAuth)
- [ ] 模板管理 Web UI

## 参与贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解贡献指南。

## 开源协议

MIT License - 详见 [LICENSE](./LICENSE) 文件。

---

<div align="center">

**使用 Anchor Stack 构建 - 让 AI 辅助开发更可靠**

[报告问题](https://github.com/anthropics/anchor-stack/issues) · [功能建议](https://github.com/anthropics/anchor-stack/issues)

</div>
