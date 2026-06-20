# 1.8+ Scripting Reference

This file contains 1.8+ specific scripting patterns, rules, and conventions.
For 1.7.x, read `references/scripting-1.7.md` instead.

## Function-Name Dispatch

The Java mod layer dispatches events to JavaScript by **function name**. When an event
fires, the mod looks for a function with the matching name and calls it with the event
object: `function eventName(e) { ... }`.

**Critically: the function name mapping in `references/events.md` is the authoritative
source.** Individual JavaDoc pages (especially older versions) may contain errors in
their descriptions. Do NOT derive the function name from the doc text — always reference
the mapping table. If a doc page says one thing and the mapping says another, trust
the mapping.

## Script Container Placement

The event's parent class determines which script container the function goes into.
This is NOT optional — functions in the wrong container will never be called.

| Parent class | Container |
|---|---|
| `NpcEvent` | NPC script |
| `PlayerEvent` | Player script |
| `BlockEvent` | Block script |
| `DialogEvent` | **Player script** |
| `ItemEvent` | Item script |
| `ForgeEvent` | Forge script |
| `WorldEvent` | World script |
| `HandlerEvent` | Handler script |
| `QuestEvent` | **Player script** |
| `RoleEvent` | **NPC script** |

When generating code, always tell the user which script container to place the
function in.

## Exceptions: No Dedicated Container

### ProjectileEvent

Call `projectile.enableEvents()` to register the current container. The projectile
maintains a list and sends events to all registered containers.

### CustomGuiEvent

On GUI creation, the current container is recorded. Events fire only to that single
container.

## Cross-Script Communication (Low Priority)

When the user needs scripts in different containers to communicate, mention these options
and let the user choose:

1. **Trigger event** — `ScriptTriggerEvent` (1.18+, function `trigger`) or
   `ScriptCommandEvent` (1.12.2, function `scriptCommand`). Fires when
   `/noppes script trigger` is run or `ICustomNpc.trigger(id, ...arguments)` is called.

2. **Minecraft scoreboard** — Use scoreboard values as a shared data channel. Scripts
   can read/write scoreboard objectives via raw MC access, creating indirect communication.

3. **storeddata** (within same NPC) — Use `npc.storeddata` as a shared key-value store
   between different event handlers in the same NPC script.

Present these as options and let the user decide based on their use case.

## QuestEvent (Player Scripts Only)

Follows a simple naming rule: drop `Event` suffix, convert to camelCase.

| Event | Function |
|---|---|
| `QuestEvent.QuestStartEvent` | `questStart` |
| `QuestEvent.QuestCompletedEvent` | `questCompleted` |
| `QuestEvent.QuestTurnedInEvent` | `questTurnIn` |

## RoleEvent (NPC Scripts Only)

All role events share the single function name **`role`**. The event type is determined
at runtime from `event` properties. Different NPC roles trigger `role(event)` with
different fields. See `references/events.md` for the full role event table.

## Output Methods

| Method | Purpose |
|---|---|
| `print("msg")` | Script console dialog |
| `npc.say("msg")` | Chat bubble above NPC |
| `player.message("msg")` | Message to interacting player (primary; `sendMessage` is a 1.7 compat alias) |
| `npc.world.broadcast("msg")` | Broadcast to all players |

## Cancelling Events

Use `e.setCanceled(true)` to cancel an event. Check `e.isCancelable()` first —
some events cannot be cancelled. `return false` does nothing.

```javascript
function damaged(e) {
    if (e.isCancelable()) {
        e.setCanceled(true);
    }
}
```

## NPC Command Execution — executeCommand()

NPCs can run server commands via `npc.executeCommand("command string")`.
The method **returns the command's output as a string**, which can be captured:

```javascript
function interact(e) {
    var result = npc.executeCommand("list");
    e.player.message("Online players: " + result);
}
```

**Server configuration requirements:**

| Setting | Location | Required value |
|---|---|---|
| `enable-command-block` | `server.properties` | `true` |
| `NpcUseOpCommands` | `CustomNPCs.cfg` | `true` (if NPC needs OP commands) |
| Command output feedback | `/gamerule commandBlockOutput` | `true` (default) or `false` to suppress |

**Security warning:** Setting `NpcUseOpCommands=true` in `CustomNPCs.cfg` allows NPCs
to run commands with operator-level permissions. This is a significant security risk on
multiplayer servers — scripts can execute any command including `/op`, `/ban`, `/stop`.
Remind the user of this when OP commands are needed.

Commands execute under the identity UUID `c9c843f8-4cb1-4c82-aa61-e264291b7bd6`
and name `[customnpcs]` for permission plugin compatibility.

## Common Patterns

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

**Cancelling events:** Do NOT `return false` — use `e.setCanceled(true)`. Check
`e.isCancelable()` first. (1.7.x: `e.setCancelled(true)` with double 'l', always cancelable.)

### Timer-based behavior (NPC/Block/Player scripts)

```javascript
function init(e) {
    // Start a repeating timer every 100 ticks (5 seconds)
    npc.getTimers().start(1, 100, true);
    // forceStart(id, ticks, repeat) overwrites existing timers with same id
}
```

Timers are managed via `npc.getTimers()`:
- `start(id, ticks, repeat)` — starts timer, errors if id already active
- `forceStart(id, ticks, repeat)` — starts/overwrites timer with same id
- `stop(id)` — stops a running timer, returns false if not found
- `reset(id)` — resets timer countdown to 0
- `has(id)` — checks if timer is active
- `clear()` — stops all timers

**Note:** The timer event fires at `ticks + 1`, not exactly at the specified tick count.
For example, `start(1, 100, true)` fires on tick 101, not 100.

```javascript
function timer(e) {
    npc.say("5 seconds have passed!");
}
```

### Tick-based behavior (NPC script)

```javascript
function tick(e) {
    // Called every 10 ticks (0.5 seconds)
    var count = (npc.tempdata.get("tickCount") || 0) + 1;
    npc.tempdata.put("tickCount", count);
    if (count % 100 === 0) {
        npc.say("5 seconds have passed!");
    }
}
```

## CustomNPC+ (1.7.10 Fork — Routes Here)

CustomNPC+ is an unofficial fork by KAMKEEL for 1.7.10. It follows 1.8+ conventions
(function dispatch, multi-page scripts) but with its own API. Fetch its docs
(see `references/versions.md`).

Key features beyond standard CNPC:
- 154+ script hooks (NPC, Player, Block, Item, Quest, Dialog, Faction, Ability,
  Animation, Auction, Effect, Recipe, and more)
- Additional script types: Global, Linked Item, Effect, Ability, Recipe, Forge Event
- Supports both JavaScript (Nashorn) and Java (Janino compiler)
- Client-side scripts, custom GUIs with overlays, Addon API
- NBT access: supported | storeddata: reliable
