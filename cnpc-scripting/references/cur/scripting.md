# 1.8+ Scripting Reference

This file contains 1.8+ specific scripting patterns, rules, and conventions.
For 1.7.x, read `references/old/scripting.md` instead.

## Function-Name Dispatch

The Java mod layer dispatches events to JavaScript by **function name**. When an event
fires, the mod looks for a function with the matching name and calls it with the event
object: `function eventName(e) { ... }`.

**Critically: the function name mapping in `references/cur/events.md` is the authoritative
source.** Individual JavaDoc pages (especially older versions) may contain errors in
their descriptions. Do NOT derive the function name from the doc text — always reference
the mapping table. If a doc page says one thing and the mapping says another, trust
the mapping.

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

## Local Snapshot of API

Some commonly used APIs have already been documented in the reference files. They can be used for quick reference, but whenever possible, it's best to get the results from the web. The reference files are `references/cur/npc-objects.md`.

## Quick fetch API online

The full path of some classes is recorded in this reference file, and you can use it to directly access the APIs you need without repeatedly searching for their locations. The reference file is `references/cur/javadoc.md`

## Storage Usage

CustomNPCs scripts have some common storage solutions; see the referenced file `references/cur/storage.md` for details.

## Simple Examples

### Basic NPC interaction (NPC script)

```javascript
function interact(e) {
    var player = e.player;
    player.message("Hello, traveler!");
    npc.say("Welcome to my shop!");
}
```

### Health / damage handling (NPC script)

```javascript
function damaged(e) {
    var source = e.source;
    var damage = e.damage;
    if (damage > 5) {
        npc.say("That hurt!");
    }
    if (damage > 100 && e.isCancelable()) {
        e.setCanceled(true);  // cancel the damage
    }
}
```

## CustomNPC+ (1.7.10 Fork)

CustomNPC+ uses **cur conventions** (same as 1.8+). Fetch its docs from `references/common/versions.md`.
Do NOT use old-convention files. See `SKILL.md` Workflow §1 for full routing and warning policy.
