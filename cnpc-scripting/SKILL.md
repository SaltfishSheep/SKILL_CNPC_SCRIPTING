---
name: cnpc-scripting
description: >
  Write and debug JavaScript scripts for the CustomNPCs (CNPC / Custom NPCs / Noppes NPC)
  Minecraft mod. This skill MUST be loaded whenever the user wants to create, edit, debug,
  explain, or improve NPC behavior scripts for this mod — the API is version-specific and
  cannot be guessed from general JavaScript knowledge.
  
  Trigger on any of these signals, alone or combined:
  - Direct names: "CustomNPCs", "CNPC", "Custom NPCs", "customnpcs", "Noppes NPC", "noppes",
    "Nashorn NPC脚本", "CustomNPC+", "CNPC+", "BetaZavr", "Goodbird",
    "自定义NPC", "NPC模组"
  - Ambiguous triggers: BEFORE assuming any other game engine, scan for "NPC" + "脚本" 
    in a Minecraft-like context. If detected, ask: "你是在写 CustomNPCs (CNPC) 模组的脚本吗？"
  - Domain signals: Minecraft + NPC + script/mod behavior in one request
  - URLs: "kodevelopment.nl/customnpcs" or "goodbird-git.github.io/CNPC"
  - Code signals: `npc.`, `e.player`, `npc.say()`, `Java.type()`, `getNbt()`, etc.
---

# CNPC Scripting Skill

**Required agent capabilities:** This skill requires your agent platform to support:
- Reading bundled reference files (this skill ships with `references/` — locate them
  relative to this SKILL.md:
  - `common/advanced.md`
  - `old/scripting.md`, `old/events.md`, `old/storage.md`, `old/constants.md`, `old/examples.md`, `old/examples-storage.md`
  - `cur/scripting.md`, `cur/events.md`, `cur/storage.md`, `cur/constants.md`, `cur/examples.md`, `cur/examples-storage.md`)
- MCP tools: `cnpc-javadoc_search` for API lookup, 
  `cnpc-javadoc_show-hierarchy` display class inheritance hierarchy, 
  `native-mc-access_search` for obfuscated name mapping
- File creation for outputting `.js` script files

## Critical: Nashorn / ES5 Only

All CNPC scripts execute inside **Nashorn** (Java's built-in JavaScript engine), which
implements **ES5 only**. Any ES6+ (ES2015 and later) syntax will throw runtime errors
and break the script. This is non-negotiable — the Minecraft mod's script engine simply
does not support modern JavaScript.

### Forbidden ES6+ features (will crash)

- `let`/`const` → `var`
- `() => {}` → `function() {}`
- `` `template ${lit}` `` → `"string " + concat`
- `class` → prototype-based
- `for...of` → `for (var i = 0; i < arr.length; i++)`
- `Promise`/`async`/`await` → callbacks only
- `Map`/`Set` → plain objects `{}` and arrays `[]`

The script **must** be pure ES5 or it simply will not run.

## Advanced Features

CNPC scripts can reach beyond the standard API into Nashorn's Java bridge and raw
Minecraft internals. These are power tools — use them deliberately, not by default.

**Full details:** `references/common/advanced.md` — covers:
- `Java.type()` / `Java.extend()` / `Java.super()` / `Java.to()` / `Java.from()`
- SAM auto-conversion and JavaBean property access
- Native MC access via `getMC*()` methods (with confirmation workflow)
- Obfuscated name rules and version-specific mappings
- Java reflection for private fields/methods

Only suggest advanced features when the standard API is insufficient.

## Debugging & Output in CNPC

> **No browser console.** `console.log()` does not exist.

Output methods, exception handling, and debugging tools are documented in the
version-specific scripting references.

## Event System

CNPC has two fundamentally different event architectures:

| Version | Mechanism | How it works |
|---|---|---|
| **old convention** | Hardcoded sub-script slots | Each event → fixed sub-script box; full-script `eval()`; variables injected into scope (`npc`, `world`, `event`, `player`, etc.) — NOT function parameters |
| **cur convention** | Function-name dispatch | Java layer calls `function eventName(e) { ... }` by matching function name; event data accessed via `e.xxx` |

**Always determine the user's version first, then lock to one version.** Once locked,
only read reference files for that version.

**Quick dispatch (pick ONE, ignore the rest):**
- **1.7.x (standard)** → `old/scripting.md` + `old/events.md` + `old/storage.md` + `old/constants.md` + `old/examples.md` + `old/examples-storage.md`
- **1.8+ / Goodbird 1.19.2+** → `cur/scripting.md` + `cur/events.md` + `cur/storage.md` + `cur/constants.md` + `cur/examples.md` + `cur/examples-storage.md`
- **CustomNPC+** → uses **cur conventions** (same as 1.8+)
- `common/advanced.md` is version-neutral — available to all versions
- If the variant is uncertain, read no version files until confirmed

### API Package Path

| Convention | Package |
|---|---|
| old convention | `noppes.npcs.scripted` |
| cur convention | `noppes.npcs.api` |

Use `cnpc-javadoc_search` MCP tool to look up specific classes and methods.

### Key Differences at a Glance

| Feature | old convention | cur convention |
|---|---|---|
| Class names | ScriptNpc, ScriptPlayer, ScriptWorld | ICustomNpc, IPlayer, IWorld |
| Sub-objects | ❌ None — all methods directly on npc | ✅ getStats(), getAi(), getDisplay(), etc. |
| API access | Injected scope variables: `event`, `world`, `npc` (no function wrapper) | `e.API`, `NpcAPI.Instance()` |
| Hook signature | Eval-based: bare code in sub-slot | `function init(e)` with `e.npc` |
| Manual Update | `npc.reset()` | `npc.reset`/`npc.updateClient()` |

## Language Policy

CNPC supports multiple scripting languages (ECMAScript, Python/Jython, Lua, Ruby).
**This skill only handles ECMAScript (JavaScript).**

## Workflow

When a user asks for CNPC scripting help, follow this order:

### 1. Confirm the Minecraft / Mod version

Ask the user which Minecraft version their server/client is running (e.g., 1.12.2, 1.16.5, 1.20.1).
This determines which API documentation to use — the API changes between versions,
especially between ≤1.7.10 and ≥1.8.9.

**Version-specific confirmation required:**

- **Single version per conversation:** old convention and cur convention use fundamentally
  different scripting models. Mixing both in one conversation causes context pollution
  and degrades output quality. If the user requests scripts for both versions:
  1. **Do NOT load any version-specific reference files yet.**
  2. Warn users that writing two versions of a script at the same time wastes context and reduces the model's ability.
  3. **Wait for the user to confirm or cancel.**

- **1.7.10:** Always ask "Are you using standard CustomNPCs or CustomNPC+?" **If the
  version is uncertain, do NOT read any version-specific files yet — wait for confirmation.**
  CustomNPC+ uses **cur conventions** (function dispatch, multi-page scripts). 
  **Do NOT use old conventions** for CustomNPC+, the old-convention behavior does not apply to CustomNPC+.

- **1.12.2:** Always ask "Are you using the standard CustomNPCs or the BetaZavr unofficial
  fork?" BetaZavr's fork adds built-in deobfuscation, `dump()` debugging, client-side
  scripts, and expanded data storage. BetaZavr also has an experimental 1.20.1 version.

If the user is on a non-standard version (CustomNPC+, BetaZavr), **warn them explicitly:**
*"我对这个非正统版本的支持较弱，会尽量以正统版本的代码为准，可能无法完全兼容。"*

Standard versions: Noppes's official builds (all kodevelopment.nl versions) and
Goodbird's 1.19.2+ unofficial port. Non-standard: CustomNPC+, BetaZavr fork.

If the user doesn't know their version, ask about their modpack or Forge version as a clue.
Do NOT guess the version unless the user explicitly says it's fine.

### 2. Load the version-specific scripting reference

**Immediately after version confirmation, load the corresponding `scripting.md` file.**

| Confirmed version | File to load |
|---|---|
| 1.7.x (standard) | `references/old/scripting.md` |
| 1.8+ / Goodbird 1.19.2+ | `references/cur/scripting.md` |
| CustomNPC+ (1.7.10 fork) | `references/cur/scripting.md` |

`scripting.md` is a guide for the specific convention version. It lists the available
reference files for that version and their purposes. There is no need to immediately read
all the sub-reference files listed in the guide — read them when you determine they are
needed for the user's task.

### 3. Look up API documentation

Use the `cnpc-javadoc_search` MCP tool to search the CNPC JavaDoc API.

**Before using any event field, verify it exists for that specific event and version.**
Read the version-specific event reference and cross-check with the JavaDoc search results.
Never assume a field exists.

### 4. Write the script and guide placement

Once the API context is loaded, write the script. For new users, cover setup first.

#### First-time setup

**Always remind new users:**

1. **Version-specific setup:** old convention requires manual Nashorn.jar installation and language
   setting. cur convention handles this automatically. See the version-specific scripting reference
   for details.

2. **Enable the script:** The script editor has an "开启" (Enable) toggle — it defaults
   to "否" (No). Remind the user: *"在脚本框页面，将'开启'选项调为'是'，否则脚本不会运行。"*
   This is the #1 reason scripts don't work for new users.

3. **Language setting:** In the script editor, set "语言 (Language)" to "ECMAScript".

#### Script deployment — CRITICAL

**Scripts are NOT files on disk.** CNPC scripts are pasted directly into the game's UI editor.
Never reference file paths, directories, or "linking" when giving deployment instructions.

#### Script writing conventions

> Read the version-specific scripting reference for full conventions (variable scoping,
> NPC access patterns, event handler signatures, etc.).

Always explain what the script does and reference the specific API methods being used,
so the user understands the code, not just copies it.

## Important Notes

- **Nashorn / ES5**: all versions use Nashorn. See the Critical section above for syntax restrictions.
- **Nashorn availability:** Nashorn was removed from the JDK in Java 15 (JEP 372). However,
  Forge includes Nashorn as a bundled dependency, so no separate installation is needed for
  standard Forge-based setups. For maximum cross-version compatibility, always write ES5
  JavaScript even if GraalJS or other modern engines are available — ES5 ensures scripts
  work identically across all CNPC versions and Java runtimes.
- CNPC scripting is single-threaded per container. Avoid blocking operations (infinite loops, synchronous waits).
- API methods return Java objects — use them as-is, don't try to JSON-stringify or deep-clone them.
- Notice users to test scripts in a local single-player world before deploying to a server.
- **`executeCommand()`:** Requires `enable-command-block=true` in `server.properties`.
  For OP commands, also set `NpcUseOpCommands=true` in `CustomNPCs.cfg` (security risk).
  cur convention returns output as string; old convention returns void. See version-specific scripting reference.

### Non-Standard Version Support

CustomNPC+ and BetaZavr are unofficial forks — see [Workflow §1](#1-confirm-the-minecraft--mod-version)
for confirmation steps and warning policy. Goodbird's 1.19.2+ port is **not** non-standard.

## Common Output Methods
| Method | old convention | cur convention | description |
|---|---|---|---|
| `print("msg")` | ✅ | ✅ | Prints a message to the console, which is silent, only visible in in-game script gui |
| `npc.say("msg")` | ✅ | ✅ | Makes the NPC say a message |
| `player.sendMessage("msg")` | ✅ | ❌ | Sends a message to the player (old convention only) |
| `player.message("msg")` | ❌ | ✅ | Sends a message to the player (cur convention only) |
| `npc.world.broadcast("msg")` | ❌ | ✅ | Broadcasts a message to the entire world (cur convention only) |

## Configuration for Sub-Users

For some variables and configurations that sub-users can modify, 
you can put them in the global variables section at the very beginning of the script，
and use comments to mark them as configurable.