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
  relative to this SKILL.md: `versions.md`, `events.md`, `event-fields.md`, `advanced.md`,
  `storage.md`, `npc-objects.md`, `scripting-1.7.md`, `scripting-1.8.md`)
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

**Full details:** `references/advanced.md` — covers:
- `Java.type()` / `Java.extend()` / `Java.super()` / `Java.to()` / `Java.from()`
- SAM auto-conversion and JavaBean property access
- Native MC access via `getMC*()` methods (with confirmation workflow)
- Obfuscated name rules and version-specific mappings
- Java reflection for private fields/methods

Only suggest advanced features when the standard API is insufficient.

## Debugging & Output in CNPC

> **No browser console.** `console.log()` does not exist.

| Method | Version | Purpose |
|---|---|---|
| `print("msg")` | All | Script console dialog (silent, manual check) |
| `npc.say("msg")` | All | Chat bubble above NPC |
| Player messaging | Version-specific | See references: `scripting-1.7.md` (1.7.x) or `npc-objects.md` (1.8+) |
| Broadcast | 1.8+ only | `npc.world.broadcast("msg")` |

### Debugging Java exceptions

Nashorn does **not** wrap Java exceptions — they are thrown as-is into JavaScript.
A `try-catch` block will receive the raw Java exception object:

```javascript
try {
    npc.executeCommand("badcommand");
} catch (err) {
    print("Java exception: " + err.getClass().getName() + " - " + err.getMessage());
}
```

This is useful for diagnosing runtime errors. The exception's Java class name and
message provide direct clues about what went wrong.

### dump() — BetaZavr fork only

The BetaZavr unofficial 1.12.2 fork provides a built-in `dump(object)` method that
prints the full structure of any object: constructors, subclasses, all fields and
methods (including private ones). This is invaluable for exploring unfamiliar APIs:

```javascript
function interact(e) {
    dump(npc);  // prints full NPC object structure
    dump(e);    // prints event object structure
}
```

This method is **only available in the BetaZavr fork.** Do not suggest it for
standard CNPC or Goodbird 1.20.1+ builds.

## NPC Object Model

ICustomNpc exposes its functionality through chainable sub-objects (`npc.getStats()`,
`npc.getAi()`, `npc.getDisplay()`, etc.). Common pattern: `npc.getStats().setMaxHealth(200)`.

Key sub-objects: Stats, Ai, Display, Inventory, Timers, Advanced, Faction, Role, Job.
Role and Job types are identified via `getType()` combined with version-specific constants
from `EnumRoleType` / `EnumJobType`.

**Full details:** `references/npc-objects.md` — covers sub-object tables, Role/Job identification,
Player object methods (quest/faction/teleport), and `updateClient()` / `reset()`.

## Data Storage

Three mechanisms, each with different trade-offs:
- **tempdata** — HashMap-backed, any type, unstable (lost on reload/death).
  Per-entity: each NPC has its own independent tempdata store.
- **storeddata** — persistent, strings and numbers only. Booleans are NOT supported —
  you must **manually convert** them to `"1"`/`"0"` or `"true"`/`"false"` strings.
  Per-entity: each NPC/player has its own store, keys don't need player name prefixes.
  Survives entity death, world reload, and server restart.
  **1.7.10 warning:** storeddata is unreliable on standard 1.7.10 (CustomNPC+ fixes
  this). For long-term storage on standard 1.7.10, consider using file I/O.
- **NBT** — `getNbt()` (live, read/write, item=permanent, entity=semi-persistent) vs
  `getXXNbt()` (snapshot, read-only). **Not available on standard 1.7.x.**

**Full details:** `references/storage.md` — covers API usage, lifetime, type restrictions,
and the storage decision guide.

## NpcAPI — Global API Access

Beyond per-NPC scripting, `NpcAPI.Instance()` (and `event.API` in handlers) provides
world-level operations: spawn NPCs, create custom GUIs, access other dimensions, etc.

**Full details:** `references/npc-objects.md` — covers access methods, key API table,
and `spawnNPC` / `createNPC` examples.

## Event System

CNPC has two fundamentally different event architectures: **1.7** and **1.8+**.
Always determine the user's version first, then **lock to one version**. Once locked,
only read reference files for that version. **If the user asks for both versions,
refuse until they choose one. If they insist, explain why it's problematic and ask why
they need both. Only proceed with both after their second confirmation, and declare
that quality is not guaranteed.** Do not pre-load files for another version.

**Quick dispatch (pick ONE, ignore the rest):**
- **1.7.x (standard)** → `references/scripting-1.7.md`. Do not read 1.8+ scripting files.
  `references/advanced.md` (Java interop, native MC) is version-neutral — available to 1.7.
- **1.8+ / Goodbird 1.20.1+** → use the files listed in the §1.8+ section below.
  Do not read `scripting-1.7.md`.
- **CustomNPC+** → same as 1.8+ (reads like 1.8+, not 1.7). **Do NOT read
  `references/scripting-1.7.md`.** Use `references/scripting-1.8.md` instead.
  **If the variant is uncertain (standard vs CustomNPC+), read no version files until confirmed.**

The complete event-to-function mapping and all container placement rules are in
`references/events.md` **(1.8+ only)**. 1.7 uses hardcoded sub-slots — see
`references/scripting-1.7.md` instead.

Event fields for each function are documented in `references/event-fields.md`
**(1.8+ only)**. 1.7 event fields are described in `references/scripting-1.7.md`.

**Naming convention (1.8+):** `e` is just a conventional formal parameter name (short for
"event"). It can be named anything — `c`, `event`, `evt` all work. The important
thing is the function name, which determines the event class received.

### 1.8+ (including 1.20.1, Goodbird): Function-name dispatch

> **Applies to:** All kodevelopment.nl versions ≥1.8.9, Goodbird 1.20.1+.
> **Key behaviors:** function-name dispatch, event fields per function, cancellable via `setCanceled(true)`.
> **Reference files for 1.8+ usage:**
> - `references/events.md` — full event→function mapping and container rules
> - `references/event-fields.md` — event field table with types
> - `references/scripting-1.8.md` — full 1.8+ scripting reference (containers, exceptions,
>   cross-script, Quest/Role events, output, cancellation, executeCommand)
> - `references/npc-objects.md` — NPC sub-objects + Player methods + NpcAPI
> - `references/advanced.md` — Java interop, native MC access, reflection
> - `references/storage.md` — tempdata, storeddata, NBT patterns
>
> For 1.7.x, read `references/scripting-1.7.md` instead.

The Java mod layer dispatches events to JavaScript by **function name**. When an event
fires, the mod looks for a function with the matching name and calls it with the event
object: `function eventName(e) { ... }`.

> **Read `references/scripting-1.8.md` for all 1.8+ event details** — container placement
> rules, exceptions (ProjectileEvent/CustomGuiEvent), cross-script communication,
> QuestEvent/RoleEvent specifics, output methods, cancellation, and executeCommand.

### 1.7: Hardcoded sub-script slots

> **Read `references/scripting-1.7.md` for all 1.7-specific details.** Only NPC events
> exist. No function dispatch — eval-based with `world`, `npc`, and `event` injected.
> Events cancelable via `event.setCancelled(true)` / `event.isCancelled()` (double 'l').
> Use `player.sendMessage()`, no `world.broadcast()`. No NBT access. storeddata unreliable.

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
  CustomNPC+ behaves like 1.8+ (function dispatch, multi-page scripts) — route to
  `references/scripting-1.8.md` for event/container rules, and get its API docs from
  `references/versions.md`. **Do NOT read `references/scripting-1.7.md`** for CustomNPC+
  — it describes 1.7 standard behavior that does not apply.

- **1.12.2:** Always ask "Are you using the standard CustomNPCs or the BetaZavr unofficial
  fork?" BetaZavr's fork adds built-in deobfuscation, `dump()` debugging, client-side
  scripts, and expanded data storage.

If the user is on a non-standard version (CustomNPC+, BetaZavr), **warn them explicitly:**
*"我对这个非正统版本的支持较弱，会尽量以正统版本的代码为准，可能无法完全兼容。"*

Standard versions: Noppes's official builds (all kodevelopment.nl versions) and
Goodbird's 1.20.1+ unofficial port. Non-standard: CustomNPC+, BetaZavr fork.

If the user doesn't know their version, ask about their modpack or Forge version as a clue.
Do NOT guess the version unless the user explicitly says it's fine.

### 2. Look up the API doc URL

Read `references/versions.md` to find the matching documentation URL.
Pick the closest match (e.g., 1.12.0 → use 1.12.2 docs).

### 3. Fetch the relevant API documentation

**Never rely on memorized API knowledge.** The CNPC API varies by version, and memorized
methods are often wrong or outdated. Always fetch the live documentation for the user's
specific version before writing any code that calls CNPC API methods.

**Before using any event field (e.g., `e.player`, `e.damage`, `e.source`), verify it
exists for that specific event.** Read `references/event-fields.md` for the field table,
and cross-check with the fetched JavaDoc. Never assume a field exists — events like
`damaged` have `e.source` but NO `e.player`.

#### Delegation: use subagents when possible

API document fetching is slow and token-intensive. **If your platform supports spawning
subagents or background workers (especially low-cost models designed for research), use
them.** Delegate each API doc fetch to a subagent — this offloads the token cost from
the main context and can fetch multiple pages in parallel. Launch the subagent(s) and
continue other work while they run.

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
then drill down. Common entry points:
- `noppes.npcs.api.INpc` — the NPC object
- `noppes.npcs.api.event.*` — event types (InteractEvent, DamagedEvent, TickEvent, etc.)
- `noppes.npcs.api.IPlayer` — the player object
- `noppes.npcs.api.IWorld` — the world object

**For 1.20.1+**: the docs are on GitHub Pages (Goodbird's unofficial docs).
They use a different structure. Navigate via the sidebar topics, not JavaDoc package paths.

### 4. Write the script and guide placement

Once the API context is loaded, write the script. For new users, cover setup first.

#### First-time setup

**Always remind new users of these three things:**

1. **Enable the script:** The script editor has an "开启" (Enable) toggle — it defaults
   to "否" (No). Remind the user: *"在脚本框页面，将'开启'选项调为'是'，否则脚本不会运行。"*
   This is the #1 reason scripts don't work for new users.

2. **Nashorn.jar (1.7.x only):** For 1.7.x, the user must copy `nashorn.jar` from their
   Java installation (`jre/lib/ext/nashorn.jar` or `jdk/jre/lib/ext/nashorn.jar`) into
   the `mods/` folder. 1.8+ versions auto-detect Nashorn or get it from Forge — no
   manual install needed.

3. **Language setting (1.7.x only):** In the script editor, set "语言 (Language)" to
    "ECMAScript". 1.8+ versions default to ECMAScript automatically.

#### Script deployment — CRITICAL

**Scripts are NOT files on disk. Do NOT tell users to place `.js` files in folders or
"link" scripts.** CNPC scripts are pasted directly into the game's UI editor:

- **1.8+:** Open the script container (NPC/Player/Block/Item etc.) → select or create a
  script page → paste code into the text area.
- **1.7:** Open the NPC script editor → click into the matching sub-slot tab → paste
  code into the text area.

Never reference file paths, directories, or "linking" when giving deployment instructions.
The user pastes the code directly into the in-game text editor.

#### Script writing conventions

> **1.8+:** read `references/scripting-1.8.md` for full conventions.
> **1.7.x:** read `references/scripting-1.7.md` — eval-based, sub-slots, no function definitions.

- Use `var` for variables to maintain state across function calls.
- Event handler signatures: `function interact(e)`, `function tick(e)`, `function damaged(e)`, etc.
- The global `npc` variable gives access to the NPC running the script.
- Event fields vary by event type — **always check `references/event-fields.md`** before
  using `e.player`, `e.source`, `e.damage`, etc. Not all events have the same fields.

#### NPC command execution — executeCommand()

NPCs can run server commands via `npc.executeCommand("command string")`.
Returns the command's output as a string. **Full details, config requirements,
and security warnings:** `references/scripting-1.8.md`.

Always explain what the script does and reference the specific API methods being used,
so the user understands the code, not just copies it.

## Common Patterns

> **1.8+:** See `references/scripting-1.8.md` for interact, damaged, timer, tick examples.
> **1.7.x:** See `references/scripting-1.7.md` for sub-slot based interaction, damage, tick examples.

### Quick reference: cancellation

Do NOT `return false` — use `e.setCanceled(true)` (1.8+) or `e.setCancelled(true)` (1.7.x, double 'l').
1.8+: check `e.isCancelable()` first. 1.7.x: events always cancelable.

## Important Notes

- **Nashorn / ES5**: all versions use Nashorn. See the Critical section above for syntax restrictions.
- CNPC scripting is single-threaded per NPC. Avoid blocking operations (infinite loops, synchronous waits).
- 1.20.1+ uses a completely rewritten scripting system with different package names.
- API methods return Java objects — use them as-is, don't try to JSON-stringify or deep-clone them.
- `npc.executeCommand("cmd")` runs server commands and returns output. Requires
  `enable-command-block=true` in `server.properties`. For OP commands, also set
  `NpcUseOpCommands=true` in `CustomNPCs.cfg` (security risk — warn the user).
- Messages to players: 1.8+ uses `player.message()` (primary). 1.7.x specifics are in
  `references/scripting-1.7.md`.
- Test scripts in a local single-player world before deploying to a server.
- **Script deployment:** Code is pasted into the in-game UI editor, NOT placed as files
  on disk. Never tell users to put scripts in folders or "link" them.

### Non-Standard Version Support

CustomNPC+ (1.7.10) and BetaZavr (1.12.2) are unofficial forks with extended APIs.
When the user is on one of these versions:
1. Warn that support is limited: *"我对这个非正统版本的支持较弱，会尽量以正统版本的代码为准"*
2. Try to match standard CNPC API patterns where possible
3. Prefer the fork's own documentation over standard CNPC JavaDocs
Goodbird's 1.20.1+ port is **not** considered non-standard — it is the official
continuation for modern Minecraft versions.
