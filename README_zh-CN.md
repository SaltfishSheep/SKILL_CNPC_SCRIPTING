[English](README.md) | [中文](README_zh-CN.md)

# CNPC Scripting Skill

一个面向 AI 编程助手（OpenCode、Claude Code、Cursor、Codex、Windsurf 等）的 Skill，为其提供编写和调试 [CustomNPCs](https://www.kodevelopment.nl/customnpcs/)（CNPC）Minecraft 模组 JavaScript 脚本所需的全部知识。

## 功能概述

CNPC 的 API 因 Minecraft 版本而异，无法从通用 JavaScript 知识推断。本 Skill 为你的助手提供：

- **版本路由** — 自动加载 1.7.x 至 1.21.x 对应版本的 API 文档
- **ES5 强制检查** — 所有 CNPC 脚本运行在 Nashorn（Java 的 JS 引擎）上，仅支持 ES5。Skill 会强制执行此约束，防止常见的 ES6+ 语法错误。
- **多分支支持** — 标准版 CustomNPCs、CustomNPC+（1.7.10 分支）、BetaZavr（1.12.2 非官方分支）、Goodbird（1.19.2+ 社区移植版）
- **Minecraft 映射查询** — 用于解析各版本混淆后的 Minecraft 类名 / 方法名 / 字段名的工具

## 项目结构

```
SKILL_CNPC_SCRIPTING/
├── cnpc-scripting/
│   ├── SKILL.md                    # Main skill definition (load this in your agent)
│   └── references/
│       ├── common/                 # Version-neutral documentation
│       │   └── advanced.md         # Nashorn Java interop & native MC access
│       ├── old/                    # 1.7.x (standard) reference docs
│       │   ├── scripting.md
│       │   ├── events.md
│       │   ├── storage.md
│       │   ├── constants.md
│       │   ├── examples.md
│       │   └── examples-storage.md
│       └── cur/                    # 1.8+ / Goodbird reference docs
│           ├── scripting.md
│           ├── events.md
│           ├── storage.md
│           ├── constants.md
│           ├── examples.md
│           └── examples-storage.md
├── LICENSE                         # MIT License
└── .gitignore
```

## 安装

### 前置要求

- **Git 2.19+**
- **Node.js ≥ 18**

### 第一步：安装 MCP 服务器

本 Skill 需要两个 MCP 服务器才能正常工作。

**1. Native MC Mapping MCP** — Minecraft 混淆名称映射查询

```bash
git clone https://github.com/SaltfishSheep/AI-MCP-NativeMinecraftAccess.git
cd AI-MCP-NativeMinecraftAccess
npm install
npm run build
```

**2. CNPC JavaDoc MCP** — CustomNPCs API 方法/字段查询

```bash
git clone https://github.com/SaltfishSheep/AI-MCP-CNPCAPIAccess.git
cd AI-MCP-CNPCAPIAccess
npm install
npm run build
```

**添加到 MCP 客户端配置：**

```json
{
  "mcpServers": {
    "native-mc-access": {
      "command": "node",
      "args": ["/absolute/path/to/AI-MCP-NativeMinecraftAccess/dist/index.js"]
    },
    "cnpc-javadoc": {
      "command": "node",
      "args": ["/absolute/path/to/AI-MCP-CNPCAPIAccess/dist/index.js"]
    }
  }
}
```

> 将 `/absolute/path/to/` 替换为你实际克隆仓库的路径。

### 第二步：安装 Skill

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/SaltfishSheep/SKILL_CNPC_SCRIPTING.git .cnpc_skill_tmp
git -C .cnpc_skill_tmp sparse-checkout set cnpc-scripting
mkdir -p ~/.agents/skills
rm -rf ~/.agents/skills/cnpc-scripting
mv .cnpc_skill_tmp/cnpc-scripting ~/.agents/skills/cnpc-scripting
rm -rf .cnpc_skill_tmp
```

<details>
<summary>特定工具专属路径</summary>

**OpenCode:**
```bash
mkdir -p ~/.config/opencode/skills
mv .cnpc_skill_tmp/cnpc-scripting ~/.config/opencode/skills/cnpc-scripting
```

**Claude Code:**
```bash
mkdir -p ~/.claude/skills
mv .cnpc_skill_tmp/cnpc-scripting ~/.claude/skills/cnpc-scripting
```

**Codex:**
```bash
mkdir -p ~/.agents/skills
mv .cnpc_skill_tmp/cnpc-scripting ~/.agents/skills/cnpc-scripting
```

</details>

## 版本路由

Skill 根据确认的 Minecraft 版本路由到不同的参考文件：

| 版本 | 参考文件集 | 说明 |
|------|-----------|------|
| 1.7.x（标准版） | `old/` | 子槽位中直接执行 eval 代码 |
| 1.7.10（CustomNPC+） | `cur/` | 使用 1.8+ 的约定 |
| 1.8+ | `cur/` | 命名函数处理器 |
| 1.12.2（BetaZavr） | `cur/` | 新增 `dump()`、客户端脚本 |
| 1.19.2+（Goodbird） | `cur/` | 基本继承自 1.8+，有少量新增 |

## 关键约束

- **仅限 ES5** — `let`、`const`、箭头函数、模板字符串、class、解构赋值、`for...of`、`Promise`、`async`/`await`、`Map`/`Set` 均被禁止
- **Nashorn 引擎** — 脚本运行在 Java 的 Nashorn 中，而非浏览器。`console.log()` 不存在。
- **每个 NPC 单线程** — 避免阻塞操作
- **脚本粘贴到游戏 UI 中** — 它们不是磁盘上的文件

## 许可证

MIT 许可证 — 详见 [LICENSE](LICENSE)。

## Skill 版本历史

- **0.4.0** — 当前版本。更短提示词，继承MCP工具用于搜索。
- **0.3.1** — 少量修复。
- **0.3.0** — 多版本支持、映射工具、完善的参考文档。
