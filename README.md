[English](README.md) | [中文](README_zh-CN.md)

# CNPC Scripting Skill

A skill for AI coding agents (OpenCode, Claude Code, Cursor, Codex, Windsurf, etc.) that provides the knowledge needed to write and debug JavaScript scripts for the [CustomNPCs](https://www.kodevelopment.nl/customnpcs/) (CNPC) Minecraft mod.

## What It Does

CNPC has a version-specific Java-backed API that cannot be guessed from general JavaScript knowledge. This skill gives your agent:

- **Version-specific API routing** — automatically loads the right documentation for 1.7.x through 1.21.x
- **ES5 enforcement** — all CNPC scripts run on Nashorn (Java's JS engine), which only supports ES5. The skill enforces this constraint and prevents common ES6+ mistakes.
- **Multi-variant support** — standard CustomNPCs, CustomNPC+ (1.7.10 fork), BetaZavr (1.12.2 unofficial fork), and Goodbird (1.19.2+ community port)
- **Minecraft mapping lookups** — tools for resolving obfuscated Minecraft class/method/field names across versions

## Project Structure

```
SKILL_CNPC_SCRIPTING/
├── cnpc-scripting/
│   ├── SKILL.md                    # Main skill definition (load this in your agent)
│   ├── info.json                   # Version metadata
│   ├── mapping_builder.py          # Builds mapping caches from MCP/Mojang data
│   ├── mapping_search.py           # Searches mapping caches with boolean expressions
│   ├── references/
│   │   ├── common/                 # Version-neutral documentation
│   │   │   ├── versions.md         # API doc URLs for all MC versions
│   │   │   ├── advanced.md         # Nashorn Java interop & native MC access
│   │   │   └── native-mc-access.md         # Deobfuscation name resolution workflow
│   │   ├── old/                    # 1.7.x (standard) reference docs
│   │   │   ├── scripting.md
│   │   │   ├── events.md
│   │   │   ├── npc-objects.md
│   │   │   ├── storage.md
│   │   │   └── javadoc.md
│   │   └── cur/                    # 1.8+ / Goodbird reference docs
│   │       ├── scripting.md
│   │       ├── events.md
│   │       ├── npc-objects.md
│   │       ├── storage.md
│   │       └── javadoc.md
│   └── .mapping-caches/            # Generated mapping CSV files (gitignored)
│       ├── mapping-info.json
│       └── 1.12.2.csv
├── LICENSE                         # MIT License
└── .gitignore
```

## Installation

Requires **Git 2.19+**.

### Universal (shared across agents)

`~/.agents/skills/` is the cross-agent standard supported by OpenCode and Codex natively. Claude Code does not support it yet (see [feature request](https://github.com/anthropics/claude-code/issues/31005)).

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/SaltfishSheep/SKILL_CNPC_SCRIPTING.git .cnpc_skill_tmp
git -C .cnpc_skill_tmp sparse-checkout set cnpc-scripting
mkdir -p ~/.agents/skills
rm -rf ~/.agents/skills/cnpc-scripting
mv .cnpc_skill_tmp/cnpc-scripting ~/.agents/skills/cnpc-scripting
rm -rf .cnpc_skill_tmp
```

### Agent-specific

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

> **For AI agents:** When helping the user install this skill, ask whether they want to install to the universal ~/.agents/skills/ directory (shared across OpenCode and Codex) or to a specific agent's directory (e.g. ~/.claude/skills/ for Claude Code, ~/.config/opencode/skills/ for OpenCode, ~/.agents/skills/ for Codex). If the user only uses one agent, suggest the agent-specific path. If they use multiple agents, suggest the universal path.

If your agent does not support directory-based skills, you can paste the contents of `SKILL.md` directly into your agent's custom instructions or system prompt. The agent will read the `references/` files on demand.

### Agent Capability Requirements

This skill requires your agent to support:
- **File reading** — to load bundled reference files (`references/` directory)
- **Web fetching** — to pull live JavaDoc pages for the user's target version (any URL fetch tool works)
- **File writing** — to output `.js` script files (optional, scripts are usually pasted into the game UI)

No specific tool names are assumed — the skill adapts to whatever your environment provides.

## Mapping Tools

The skill includes Python tools for working with Minecraft's obfuscated code mappings. These are needed when scripts access Minecraft internals via `getMC*()` methods or Java reflection.

### Building a Mapping Cache

Generate a mapping cache for a specific Minecraft version:

```bash
cd cnpc-scripting
python mapping_builder.py 1.12.2
python mapping_builder.py 1.20.1
```

This downloads MCP/Mojang mapping data and produces a unified CSV at `.mapping-caches/<version>.csv`.

**Supported versions:** 1.7.10, 1.8–1.11.2, 1.12.2–1.15.2, 1.16.1–1.16.5, 1.17–1.20.1

### Searching a Mapping Cache

Search for obfuscated names using boolean expressions:

```bash
cd cnpc-scripting

# Simple search
python mapping_search.py 1.12.2 "KeyBinding"

# AND search
python mapping_search.py 1.12.2 "Entity&Player"

# OR search
python mapping_search.py 1.12.2 "Entity|Player"

# Complex expressions
python mapping_search.py 1.12.2 "(Entity|Player)&client"

# Paginated results (page 2)
python mapping_search.py 1.12.2 "Block" 2
```

**Expression syntax:**
| Operator | Meaning | Example |
|----------|---------|---------|
| `term` | Case-insensitive substring match | `KeyBinding` |
| `&` | AND (both must match) | `Entity&Living` |
| `\|` | OR (either must match) | `Entity\|Player` |
| `()` | Grouping | `(a\|b)&c` |

## Version Routing

The skill routes to different reference files based on the confirmed Minecraft version:

| Version | Reference Set | Notes |
|---------|---------------|-------|
| 1.7.x (standard) | `old/` | Bare eval code in sub-slots |
| 1.7.10 (CustomNPC+) | `cur/` | Uses 1.8+ conventions |
| 1.8+ | `cur/` | Named function handlers |
| 1.12.2 (BetaZavr) | `cur/` | Adds `dump()`, client scripts |
| 1.19.2+ (Goodbird) | `cur/` | Largely inherited from 1.8+, with minor additions |

## Key Constraints

- **ES5 only** — `let`, `const`, arrow functions, template literals, classes, destructuring, `for...of`, `Promise`, `async`/`await`, `Map`/`Set` are all forbidden
- **Nashorn engine** — scripts run inside Java's Nashorn, not a browser. `console.log()` does not exist.
- **Single-threaded per NPC** — avoid blocking operations
- **Scripts are pasted into the game UI** — they are not files on disk

## License

MIT License — see [LICENSE](LICENSE).

## Skill Version History

- **0.3.1** — Current version. Multi-version support, mapping tools, comprehensive reference docs.
