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

## Installation

### Prerequisites

- **Git 2.19+**
- **Node.js ≥ 18**

### Step 1: Install MCP Servers

This skill requires two MCP servers to be installed and configured in your AI agent.

**1. Native MC Mapping MCP** — Minecraft obfuscated name mapping lookups

```bash
git clone https://github.com/SaltfishSheep/AI-MCP-NativeMinecraftAccess.git
cd AI-MCP-NativeMinecraftAccess
npm install
npm run build
```

**2. CNPC JavaDoc MCP** — CustomNPCs API method/field lookups

```bash
git clone https://github.com/SaltfishSheep/AI-MCP-CNPCAPIAccess.git
cd AI-MCP-CNPCAPIAccess
npm install
npm run build
```

**Add to your MCP client configuration:**

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

> Replace `/absolute/path/to/` with the actual paths where you cloned the repos.

### Step 2: Install the Skill

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/SaltfishSheep/SKILL_CNPC_SCRIPTING.git .cnpc_skill_tmp
git -C .cnpc_skill_tmp sparse-checkout set cnpc-scripting
mkdir -p ~/.agents/skills
rm -rf ~/.agents/skills/cnpc-scripting
mv .cnpc_skill_tmp/cnpc-scripting ~/.agents/skills/cnpc-scripting
rm -rf .cnpc_skill_tmp
```

<details>
<summary>Agent-specific paths</summary>

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

- **0.4.0** — Current version. Shorter prompts. MCP tool integrated with search API.
- **0.3.0** — A few fix.
- **0.3.1** — Multi-version support, mapping tools, comprehensive reference docs.
