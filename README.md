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

### Agent Capability Requirements

This skill requires your agent to support:
- **File reading** — to load bundled reference files (`references/` directory)
- **Web fetching** — to pull live JavaDoc pages for the user's target version (any URL fetch tool works)
- **File writing** — to output `.js` script files (optional, scripts are usually pasted into the game UI)

No specific tool names are assumed — the skill adapts to whatever your environment provides.

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
