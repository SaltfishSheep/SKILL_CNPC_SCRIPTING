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
│   ├── SKILL.md                    # Skill 主定义文件（加载此文件即可）
│   ├── info.json                   # 版本元数据
│   ├── mapping_builder.py          # 从 MCP/Mojang 数据构建映射缓存
│   ├── mapping_search.py           # 使用布尔表达式搜索映射缓存
│   ├── references/
│   │   ├── common/                 # 版本无关的通用文档
│   │   │   ├── versions.md         # 各版本 API 文档 URL
│   │   │   ├── advanced.md         # Nashorn Java 互操作与原生 MC 访问
│   │   │   └── native-mc-access.md         # 反混淆名称解析工作流
│   │   ├── old/                    # 1.7.x（标准版）参考文档
│   │   │   ├── scripting.md
│   │   │   ├── events.md
│   │   │   ├── npc-objects.md
│   │   │   ├── storage.md
│   │   │   └── javadoc.md
│   │   └── cur/                    # 1.8+ / Goodbird 参考文档
│   │       ├── scripting.md
│   │       ├── events.md
│   │       ├── npc-objects.md
│   │       ├── storage.md
│   │       └── javadoc.md
│   └── .mapping-caches/            # 生成的映射缓存 CSV 文件（已 gitignore）
│       ├── mapping-info.json
│       └── 1.12.2.csv
├── LICENSE                         # MIT 许可证
└── .gitignore
```

## 安装

需要 **Git 2.19+**。

### 通用安装（多 agent 共享）

`~/.agents/skills/` 是跨 agent 标准路径，OpenCode 和 Codex 原生支持。Claude Code 暂不支持（见 [feature request](https://github.com/anthropics/claude-code/issues/31005)）。

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/SaltfishSheep/SKILL_CNPC_SCRIPTING.git .cnpc_skill_tmp
git -C .cnpc_skill_tmp sparse-checkout set cnpc-scripting
mkdir -p ~/.agents/skills
rm -rf ~/.agents/skills/cnpc-scripting
mv .cnpc_skill_tmp/cnpc-scripting ~/.agents/skills/cnpc-scripting
rm -rf .cnpc_skill_tmp
```

### 特定工具专属安装

<details>
<summary>OpenCode</summary>

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/SaltfishSheep/SKILL_CNPC_SCRIPTING.git .cnpc_skill_tmp
git -C .cnpc_skill_tmp sparse-checkout set cnpc-scripting
mkdir -p ~/.config/opencode/skills
rm -rf ~/.config/opencode/skills/cnpc-scripting
mv .cnpc_skill_tmp/cnpc-scripting ~/.config/opencode/skills/cnpc-scripting
rm -rf .cnpc_skill_tmp
```

</details>

<details>
<summary>Claude Code</summary>

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/SaltfishSheep/SKILL_CNPC_SCRIPTING.git .cnpc_skill_tmp
git -C .cnpc_skill_tmp sparse-checkout set cnpc-scripting
mkdir -p ~/.claude/skills
rm -rf ~/.claude/skills/cnpc-scripting
mv .cnpc_skill_tmp/cnpc-scripting ~/.claude/skills/cnpc-scripting
rm -rf .cnpc_skill_tmp
```

</details>

<details>
<summary>Codex</summary>

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/SaltfishSheep/SKILL_CNPC_SCRIPTING.git .cnpc_skill_tmp
git -C .cnpc_skill_tmp sparse-checkout set cnpc-scripting
mkdir -p ~/.agents/skills
rm -rf ~/.agents/skills/cnpc-scripting
mv .cnpc_skill_tmp/cnpc-scripting ~/.agents/skills/cnpc-scripting
rm -rf .cnpc_skill_tmp
```

</details>

> **致 AI 助手：** 帮助用户安装本 skill 时，请询问用户是希望安装到通用的 ~/.agents/skills/ 目录（OpenCode 和 Codex 共享），还是安装到特定工具的专属目录（如 Claude Code 的 ~/.claude/skills/、OpenCode 的 ~/.config/opencode/skills/、Codex 的 ~/.agents/skills/）。如果用户只使用一种 agent，建议使用该工具的专属路径；如果使用多种 agent，建议使用通用路径。

如果你的 agent 不支持目录级 skill，也可以只将 `SKILL.md` 的内容粘贴到 agent 的自定义指令 / system prompt 中，agent 会在需要时自行读取 `references/` 下的参考文件。

### Agent 能力要求

本 Skill 要求你的 agent 支持：
- **文件读取** — 用于加载随附的参考文件（`references/` 目录）
- **网页抓取** — 用于获取用户目标版本的实时 JavaDoc 页面（任何 URL 抓取工具均可）
- **文件写入** — 用于输出 `.js` 脚本文件（可选，脚本通常直接粘贴到游戏 UI 中）

不预设任何具体工具名称 — Skill 会适配你的环境所提供的任何工具。

## 映射工具

Skill 包含用于处理 Minecraft 混淆代码映射的 Python 工具。当脚本通过 `getMC*()` 方法或 Java 反射访问 Minecraft 内部时需要用到。

### 构建映射缓存

为指定 Minecraft 版本生成映射缓存：

```bash
cd cnpc-scripting
python mapping_builder.py 1.12.2
python mapping_builder.py 1.20.1
```

该命令会下载 MCP/Mojang 映射数据，并在 `.mapping-caches/<version>.csv` 生成统一的 CSV 文件。

**支持的版本：** 1.7.10、1.8–1.11.2、1.12.2–1.15.2、1.16.1–1.16.5、1.17–1.20.1

### 搜索映射缓存

使用布尔表达式搜索混淆名称：

```bash
cd cnpc-scripting

# 简单搜索
python mapping_search.py 1.12.2 "KeyBinding"

# AND 搜索
python mapping_search.py 1.12.2 "Entity&Player"

# OR 搜索
python mapping_search.py 1.12.2 "Entity|Player"

# 复合表达式
python mapping_search.py 1.12.2 "(Entity|Player)&client"

# 分页结果（第 2 页）
python mapping_search.py 1.12.2 "Block" 2
```

**表达式语法：**
| 运算符 | 含义 | 示例 |
|--------|------|------|
| `term` | 不区分大小写的子串匹配 | `KeyBinding` |
| `&` | AND（两者都须匹配） | `Entity&Living` |
| `\|` | OR（任一匹配即可） | `Entity\|Player` |
| `()` | 分组 | `(a\|b)&c` |

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

- **0.3.1** — 当前版本。多版本支持、映射工具、完善的参考文档。
