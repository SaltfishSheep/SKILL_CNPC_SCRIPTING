# cur convention Scripting Reference

## Reference Files

| File | Purpose | When to read |
|---|---|---|
| `events.md` | Event→function name mapping, script container rules, field availability, cancellation | When handling events or debugging event dispatch |
| `storage.md` | Data persistence (tempdata, storeddata, NBT read/write) | When scripts need to save/load data |
| `constants.md` | AnimationType, EntitiesType, JobType, RoleType, PotionEffectType, etc. | When checking types or setting numeric constants |
| `examples.md` | Code snippets for NPC object model, role checks, spawnNPC | When writing new scripts or learning cur convention patterns |
| `examples-storage.md` | Code snippets for tempdata, storeddata, NBT operations | When implementing data persistence |

## Script Container Placement, Event Fields, and Cancellation

**Full details in `references/cur/events.md`** — event→function mapping, container rules,
field table, cancellation, QuestEvent/RoleEvent specifics.

## Cross-Script Communication

When the user needs scripts in different containers to communicate, mention these options
and let the user choose:

1. **Trigger event** — `ScriptTriggerEvent` (1.18+, function `trigger`) or
   `ScriptCommandEvent` (1.12.2, function `scriptCommand`). Fires when
   `/noppes script trigger` is run or `ICustomNpc.trigger(id, ...arguments)` is called.

2. **Minecraft scoreboard** — Use scoreboard values as a shared data channel. Scripts
   can read/write scoreboard objectives via raw MC access, creating indirect communication.

Present these as options and let the user decide based on their use case.

## NPC Object Model

ICustomNpc has several chainable sub-objects. Understanding this hierarchy is essential
for discovering methods — the JavaDoc organizes methods by sub-interface, not flat on the
NPC object. The most common chain pattern is `npc.getXxx().doYyy()`.

### Updating NPCs after runtime changes

Changes made via the sub-objects (display, stats, ai) are normally synced to clients
every 10 ticks. To sync immediately, call `npc.updateClient()`. To fully reset and
re-trigger `init`, call `npc.reset()`.

## NpcAPI — Global API Access

Beyond the `npc` and `e.player` objects, CNPC provides a global singleton API for
world-level operations that don't belong to a specific NPC.

### Accessing NpcAPI

- **From event context:** `event.API` — available in any event handler that receives `e`
- **From anywhere:** `NpcAPI.Instance()` — the static singleton accessor

Both return the same NpcAPI object. `event.API` is more convenient when inside a
handler; `NpcAPI.Instance()` works from any scope (including utility scripts).

**Important:** NpcAPI should only be used server-side. The `createNPC(world)` method
creates the NPC but does not spawn it — you must call additional methods to place it
in the world. `spawnNPC(...)` handles both creation and spawning.

## Storage Usage

CustomNPCs scripts have some common storage solutions; see the referenced file `references/cur/storage.md` for details.

## Examples

See `references/cur/examples.md` for code examples.