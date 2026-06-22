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
  - Ambiguous triggers (CAUGHT-EARLY RULE): BEFORE assuming any other game engine or
    framework, scan the request for "NPC" + "脚本" appearing together in a Minecraft-like
    context. If detected, immediately ask: "你是在写 CustomNPCs (CNPC) 模组的脚本吗？"
    Load this skill on confirmation. This rule takes priority over generic scripting
    responses — a user asking about "NPC 脚本" without specifying a game is most likely
    CNPC. Do not ask about Unity, Unreal, or other engines first.
  - Domain signals: the user mentions Minecraft + NPC + script/mod behavior in one request
  - Multiple versions: user asks about scripts for multiple MC versions in one conversation
    (e.g., "1.7 and 1.12") — warn about context pollution, suggest one version per session
  - URLs: any link containing "kodevelopment.nl/customnpcs" or "goodbird-git.github.io/CNPC"
  - API references: mention of "INpc", "IPlayer", "IWorld", "noppes.npcs.api", "NpcAPI",
    "Java.type", "Java.extend", "Java.to", "Java.from", "Java.super",
    "getMCEntity", "getMCWorld", "getMCLevel", "getMCItemStack", "getMC"
  - Code signals: pasted JS code using `npc.`, `e.player`, `e.world`, `npc.say()`,
    `npc.executeCommand()`, `Java.type()`, `Java.extend()`, `Java.from()`,
    `Java.to()`, `Java.super()`, `getNbt()`, `getEntityNbt()`, `getItemNbt()`,
    `tempdata`, `storeddata`, or functions named `interact`, `tick`, `damaged`,
    `init`, `died`, `target`, `collide`, `killed`, `meleeAttack`, `rangedLaunched`
  
  Even if the user just says "帮我写一个NPC脚本" without naming the mod, assume CNPC
  and ask to confirm. Do not treat this as ordinary JavaScript — the CNPC mod has its
  own Java-backed API that differs across Minecraft versions and cannot be inferred.
  CRITICAL: ALL CNPC scripts run on Nashorn (Java's JS engine). The language standard is
  ES5 ONLY. `let`, `const`, arrow functions, template literals, classes, destructuring,
  `for...of`, and any ES6+ syntax will cause runtime errors.
  LANGUAGE SUPPORT: This skill only supports ECMAScript (JavaScript). If the user mentions
  Python, Lua, Ruby, or any other CNPC scripting language, refuse politely and state you
  can only write ECMAScript. If they insist, warn that you cannot guarantee correctness.
---

# CNPC Scripting Skill

Help the user write JavaScript scripts for the CustomNPCs (CNPC) Minecraft mod.
The mod provides a scripting engine that runs JS inside Minecraft, with a version-specific
API for interacting with NPCs, players, worlds, and items.

**Required agent capabilities:** This skill requires your agent platform to support:
- Reading bundled reference files (this skill ships with `references/` — locate them
  relative to this SKILL.md:
  - `common/versions.md`, `common/advanced.md`
  - `old/scripting.md`, `old/events.md`, `old/npc-objects.md`, `old/storage.md`, `old/javadoc.md`
  - `cur/scripting.md`, `cur/events.md`, `cur/npc-objects.md`, `cur/storage.md`, `cur/javadoc.md`)
- Web/URL fetching to pull live JavaDoc pages for the user's target version
- File creation for outputting `.js` script files

No specific tool names are assumed — adapt to whatever your environment provides.

## Critical: Nashorn / ES5 Only

All CNPC scripts execute inside **Nashorn** (Java's built-in JavaScript engine), which
implements **ES5 only**. Any ES6+ (ES2015 and later) syntax will throw runtime errors
and break the script. This is non-negotiable — the Minecraft mod's script engine simply
does not support modern JavaScript.

### Forbidden ES6+ features (will crash)

| Forbidden | ES5 Replacement |
|---|---|
| `let x = 1` | `var x = 1` |
| `const x = 1` | `var x = 1` (use naming conventions for constants) |
| `() => { ... }` | `function() { ... }` |
| `` `Hello ${name}` `` | `"Hello " + name` |
| `class Foo { }` | Prototype-based objects |
| `var { x, y } = obj` | `var x = obj.x; var y = obj.y` |
| `for (var x of arr)` | `for (var i = 0; i < arr.length; i++)` |
| `[...arr]` / `f(...args)` | `.slice()` / `.apply()` |
| `function f(x = 1)` | `function f(x) { x = x || 1; }` |
| `Promise`, `async`, `await` | Callbacks only |
| `Map`, `Set`, `WeakMap` | Plain objects `{}` and arrays `[]` |

### Always verify before output

Before returning any script to the user, scan it for:
1. `let` or `const` → replace with `var`
2. Arrow functions `=>` → replace with `function`
3. Template literals with `${}` → replace with string concatenation
4. Any other ES6+ syntax

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

CNPC has two fundamentally different event architectures: **1.7** and **1.8+**.
Always determine the user's version first, then **lock to one version**. Once locked,
only read reference files for that version. See [Workflow §1](#1-confirm-the-minecraft--mod-version)
for the full version-locking policy and how to handle multi-version requests.

**Quick dispatch (pick ONE, ignore the rest):**
- **1.7.x (standard)** → `old/scripting.md` + `old/events.md` + `old/npc-objects.md` + `old/storage.md` + `old/javadoc.md`
- **1.8+ / Goodbird 1.19.2+** → `cur/scripting.md` + `cur/events.md` + `cur/npc-objects.md` + `cur/storage.md` + `cur/javadoc.md`
- **CustomNPC+** → uses **cur conventions** (same as 1.8+). See [Workflow §1](#1-confirm-the-minecraft--mod-version) for full routing.
- `common/advanced.md` is version-neutral — available to all versions.
- If the variant is uncertain, read no version files until confirmed.

## Language Policy

CNPC supports multiple scripting languages (ECMAScript, Python/Jython, Lua, Ruby).
**This skill only handles ECMAScript (JavaScript).** If the user mentions or requests
any other language:

1. Refuse politely: *"我只能编写 ECMAScript (JavaScript) 脚本，无法处理 Python/Lua/Ruby。"*
2. If the user insists, state clearly: *"我无法保证非 ECMAScript 代码的效果和正确性。"*
3. Then proceed, but only with best-effort advice — do not claim correctness.

## Workflow

When a user asks for CNPC scripting help, follow this order:

### 1. Confirm the Minecraft / Mod version

Ask the user which Minecraft version their server/client is running (e.g., 1.12.2, 1.16.5, 1.20.1).
This determines which API documentation to use — the API changes between versions,
especially between ≤1.18.2 and ≥1.20.1.

**Version-specific confirmation required:**

- **Single version per conversation:** 1.7.x (standard) and 1.8+ use fundamentally
  different scripting models. Mixing both in one conversation causes context pollution
  and degrades output quality. If the user requests scripts for both versions:
  1. **Do NOT load any version-specific reference files yet.**
  2. Warn: *"同时编写 1.7 和 1.8+ 的脚本会导致多版本提示词相互干扰，请选择一个版本，或开新对话处理另一个版本。"*
  3. **Wait for the user to choose a single version before loading references.**

  If the user **insists on both versions**, do not accept immediately:
  1. Explain why mixing versions causes problems (conflicting event models, output methods,
     cancellation rules, deployment instructions)
  2. Ask *"能否告诉我为什么需要同时编写两个版本的脚本？"*
  3. **Only after the user explicitly confirms again** — and you have stated: *"同时编写
     两个版本将不保证脚本质量和准确性"* — may you proceed to load both sets of files.

- **1.7.10:** Always ask "Are you using standard CustomNPCs or CustomNPC+?" **If the
  version is uncertain, do NOT read any version-specific files yet — wait for confirmation.**
  CustomNPC+ uses **cur conventions** (function dispatch, multi-page scripts) — route to
  `references/cur/scripting.md` for event/container rules, and get its API docs from
  `references/common/versions.md`. **Do NOT read `references/old/scripting.md`** for CustomNPC+
  — it describes old-convention behavior that does not apply.

- **1.12.2:** Always ask "Are you using the standard CustomNPCs or the BetaZavr unofficial
  fork?" BetaZavr's fork adds built-in deobfuscation, `dump()` debugging, client-side
  scripts, and expanded data storage. BetaZavr also has an experimental 1.20.1 version.

If the user is on a non-standard version (CustomNPC+, BetaZavr), **warn them explicitly:**
*"我对这个非正统版本的支持较弱，会尽量以正统版本的代码为准，可能无法完全兼容。"*

Standard versions: Noppes's official builds (all kodevelopment.nl versions) and
Goodbird's 1.19.2+ unofficial port. Non-standard: CustomNPC+, BetaZavr fork.

If the user doesn't know their version, ask about their modpack or Forge version as a clue.
Do NOT guess the version unless the user explicitly says it's fine.

### 2. Load the version-specific scripting reference — CRITICAL, FULL FIDELITY REQUIRED

**Immediately after version confirmation, you MUST obtain the corresponding `scripting.md`
file in full, before proceeding to any other step.**

| Confirmed version | File to load |
|---|---|
| 1.7.x (standard) | `references/old/scripting.md` |
| 1.8+ / Goodbird 1.19.2+ | `references/cur/scripting.md` |
| CustomNPC+ (1.7.10 fork) | `references/cur/scripting.md` |

**This file must be loaded with full fidelity — verbatim content, not summarized or
paraphrased.** Delegation is allowed **only if** the sub-agent returns the complete
file content verbatim (e.g., a file-reading tool that passes through raw text). Do NOT
delegate to agents that summarize, compress, or paraphrase content (e.g., a research
agent asked to "explain what this file says").

**Why full fidelity is required:**
- `scripting.md` defines the **event system paradigm** for the version — the difference
  between bare eval code in sub-slots (1.7.x) and named function handlers (1.8+). A
  summary cannot preserve this distinction with enough fidelity.
- It contains **cross-references** to events.md, npc-objects.md, storage.md, and javadoc.md
  that the main agent needs to follow in subsequent steps.
- It includes **version-specific quirks** (e.g., 1.7.x's `setCancelled` with double 'l',
  `getHeldItem()` vs `getMainhandItem()`) that a sub-agent summary may omit.

**After loading scripting.md**, follow its internal pointers to load additional reference
files (events.md, npc-objects.md, etc.) as needed — these may be loaded by the main agent
or delegated, since scripting.md provides the authoritative routing context.

### 3. Look up the API doc URL

Read `references/common/versions.md` to find the matching documentation URL.
Pick the closest match (e.g., 1.12.0 → use 1.12.2 docs).

### 4. Fetch the relevant API documentation

**Never rely on memorized API knowledge.** The CNPC API varies by version, and memorized
methods are often wrong or outdated. Always fetch the live documentation for the user's
specific version before writing any code that calls CNPC API methods.

**Before using any event field, verify it exists for that specific event and version.**
Read the version-specific event reference and cross-check with the fetched JavaDoc.
Never assume a field exists.

#### Delegation: use parallel processing when possible

API document fetching is slow and token-intensive. **If your platform supports parallel
processing or delegation features, use them to fetch documentation concurrently.**
This offloads token cost from the main conversation and allows fetching multiple pages
at once. Continue other work while fetches run in parallel.

#### If the API fetch fails (timeout / unreachable)

**Do not silently skip documentation.** Handle the failure based on version:

| Version | Fallback strategy |
|---|---|
| 1.7.x (standard) | Inform the user: network issue, ask them to provide an accessible network environment |
| 1.8+ (standard, kodevelopment.nl) | Try fetching a nearby version's API (e.g., 1.16.5 fails → try 1.12.2 or 1.18.2) |
| Non-standard (CustomNPC+, BetaZavr) | Use 1.12.2 API as the primary fallback; 1.20.1 API as secondary. Prefer 1.12.2. |

If multiple fallback versions are available and none work, tell the user the docs are
unreachable and ask how they'd like to proceed.

#### What to fetch

The docs are JavaDoc pages (HTML). Use your platform's web fetch or URL retrieval
capability to pull the relevant class/method pages. This skill does not assume any
specific tool name (e.g., `webfetch`, `web_fetch`, `fetch_url` are all equivalent) —
use whatever your environment provides.
Don't fetch the entire JavaDoc site — only the classes/methods relevant to the task.

**How to know which classes to fetch:**
- For NPC behavior: look for `npc` object methods, event objects
- For dialogue/quests: look for player interaction, quest APIs
- For world manipulation: look for world, block, entity APIs
- For inventory/items: look for item stack APIs

When the user's task is vague, fetch the main package index first to identify relevant classes,
then drill down. See the **JavaDoc Class Reference** section in the version-specific
scripting reference for a complete list of common classes and their package paths.

**For 1.19.2+ (Goodbird)**: the docs are on GitHub Pages (Goodbird's unofficial docs).
They use a different structure. Navigate via the sidebar topics, not JavaDoc package paths.

### 5. Write the script and guide placement

Once the API context is loaded, write the script. For new users, cover setup first.

#### First-time setup

**Always remind new users:**

1. **Enable the script:** The script editor has an "开启" (Enable) toggle — it defaults
   to "否" (No). Remind the user: *"在脚本框页面，将'开启'选项调为'是'，否则脚本不会运行。"*
   This is the #1 reason scripts don't work for new users.

2. **Version-specific setup:** 1.7.x requires manual Nashorn.jar installation and language
   setting. 1.8+ handles this automatically. See the version-specific scripting reference
   for details.

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
- CNPC scripting is single-threaded per NPC. Avoid blocking operations (infinite loops, synchronous waits).
- 1.19.2+ (Goodbird) uses a completely rewritten scripting system with different package names.
- API methods return Java objects — use them as-is, don't try to JSON-stringify or deep-clone them.
- Test scripts in a local single-player world before deploying to a server.
- **`executeCommand()`:** Requires `enable-command-block=true` in `server.properties`.
  For OP commands, also set `NpcUseOpCommands=true` in `CustomNPCs.cfg` (security risk).
  1.8+ returns output as string; 1.7.x returns void. See version-specific scripting reference.

### Non-Standard Version Support

CustomNPC+ and BetaZavr are unofficial forks — see [Workflow §1](#1-confirm-the-minecraft--mod-version)
for confirmation steps and warning policy. Goodbird's 1.19.2+ port is **not** non-standard.

## Version Routing
| Version | Reference Files |
|---|---|
| 1.7.x (standard) | `old/scripting.md`, `old/events.md`, `old/npc-objects.md`, `old/storage.md`, `old/javadoc.md` |
| 1.8+ / Goodbird 1.19.2+ | `cur/scripting.md`, `cur/events.md`, `cur/npc-objects.md`, `cur/storage.md`, `cur/javadoc.md` |
| CustomNPC+ (1.7.10 fork) | Use **cur** files (same as 1.8+) |
| Advanced features | `common/advanced.md` (version-neutral) |
| Java Doc fetching | Always fetch live docs for the user's specific version; use `common/versions.md` to find URLs |

## Common Output Methods
| Method | 1.7.x | 1.8+ | description |
|---|---|---|---|
| `print("msg")` | ✅ | ✅ | Prints a message to the console, which is silent, only visible in in-game script gui |
| `npc.say("msg")` | ✅ | ✅ | Makes the NPC say a message |
| `player.sendMessage("msg")` | ✅ | ❌ | Sends a message to the player (1.7.x only) |
| `player.message("msg")` | ❌ | ✅ | Sends a message to the player (1.8+ only) |
| `npc.world.broadcast("msg")` | ❌ | ✅ | Broadcasts a message to the entire world (1.8+ only) |

## Configuration for Sub-Users

For some variables and configurations that sub-users can modify, you can put them in the global variables section at the very beginning of the script and use comments to mark them as configurable.

## Delegated Reference Loading

After loading `scripting.md` in the main agent (mandatory, see Workflow §2), the remaining
reference files should be loaded via **sub-agent delegation** to save main-agent context
tokens. The sub-agent reads the full file and returns only the content relevant to the
user's task.

### Delegatable files (after version is confirmed)

| Reference file | Delegate prompt template |
|---|---|
| `{ver}/events.md` | "Read `references/{ver}/events.md` in full. The user's task is: {task_summary}. Return: (1) the event→function mapping for events relevant to this task, (2) the field table rows for those events only, (3) any cancellation rules. Omit events and fields unrelated to the task." |
| `{ver}/npc-objects.md` | "Read `references/{ver}/npc-objects.md` in full. The user needs to work with: {object_types}. Return: the method tables for those objects only, plus any critical gotchas. Omit unrelated object types." |
| `{ver}/storage.md` | "Read `references/{ver}/storage.md` in full. The user needs: {storage_need}. Return: the relevant storage mechanism's API, type restrictions, and persistence behavior. Include the decision guide row matching their need." |
| `{ver}/javadoc.md` | "Read `references/{ver}/javadoc.md` in full. The user's task involves: {api_area}. Return: the class paths for the relevant classes/packages only. Omit unrelated entries." |

Where `{ver}` is `old` or `cur` based on the confirmed version.

### Rules

1. **`scripting.md` must NOT be delegated** — it defines the event paradigm and must be in
   the main agent's context with full fidelity.
2. Sub-agents must **read the file verbatim** and extract relevant portions — never summarize
   or paraphrase API signatures, field names, or version-specific quirks.
3. When the task is broad (e.g., "write a full NPC with combat + dialogue + storage"),
   delegate multiple files in parallel and reconcile the results before writing code.
4. When the task is narrow (e.g., "how do I use timers"), only delegate the single relevant
   file — skip the rest entirely.
5. If delegation is not available (e.g., platform limitation), fall back to main-agent
   loading — but prefer delegation when possible to preserve context budget for code
   generation and JavaDoc fetching.