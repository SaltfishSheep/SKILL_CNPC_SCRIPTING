# 1.7.x Scripting Reference

> **CustomNPC+ Users — DO NOT READ THIS FILE.** If the user is on CustomNPC+, close
> this file immediately. CustomNPC+ follows 1.8+ conventions (function dispatch,
> multi-page scripts). All content below (hardcoded slots, eval-based dispatch,
> `ScriptEvent` types) does NOT apply. Route to `references/scripting-1.8.md` instead.

This file is the **complete, self-contained reference** for standard 1.7.10 CNPC scripting
(event architecture, output, cancellation, setup, quirks, common patterns). For advanced
features (Java interop via `Java.type()`, native MC access via `getMC*()`, Java reflection),
1.7 users may also read `references/advanced.md` (version-neutral).

## Event Architecture

1.7.x uses **hardcoded sub-script slots**, not function-name dispatch:

- **Only NPC events** — no Player, Block, Item, or other script types
- **No function name mapping** — each event is hardcoded to a specific sub-script box
- **Full-script eval** — the entire script is `eval()`'d each time. The following
  variables are injected into scope: `world` (IWorld), `npc` (ICustomNpc), `event`
  (event-specific type), and event-dependent extras like `player`, `dialog`, `target`.
- No function definitions — code runs top-to-bottom

### Sub-slot → 1.8+ Equivalent

| 1.7 Slot | 1.8+ equivalent | Fires every |
|---|---|---|
| 运行 (Run) | `init` | Once on load |
| 更新 (Update) | `tick` | 10 ticks (0.5s) |
| 对话 1 (Interact) | `interact` | Right-click NPC |
| 对话 2 (Dialog) | `dialog` | Dialog GUI opens (injects `player`, `dialog`) |
| 伤害 (Damage) | `damaged` | NPC takes damage. `event` is `ScriptEventDamaged` — methods: `getDamage()`/`setDamage()` (float), `getSource()` (ScriptLivingBase), `getType()` (String), `getClearTarget()`/`setClearTarget()` (boolean) |
| Killed | `died` | NPC dies |
| Attack | `meleeAttack` + `rangedAttack` | NPC attacks. `event` is `ScriptEventAttack` — methods: `getTarget()` (ScriptLivingBase), `getDamage()`/`setDamage()` (float), `isRanged()` (boolean) |
| Target | `target` | NPC acquires target. `event` is `ScriptEventTarget` — methods: `getTarget()`/`setTarget()` (ScriptLivingBase) |
| Collide | `collide` | Entity collision (injects `entity`) |
| Kills | `kill` | NPC kills entity (injects `target`) |
| Dialog Closed | `dialogClose` | Option selected or dialog closes (injects `player`, `dialog`, `option`) |

### Dialog Gotcha

The "Dialog Closed" slot fires when a player **selects a dialog option** AND when
the dialog is **closed**. These two cases share the same sub-slot — use `event` fields
to distinguish between them.

## Output Methods

1.7.x has a different set of output methods than 1.8+:

| Method | Purpose | Notes |
|---|---|---|
| `print("msg")` | Script console dialog | Debug logging |
| `npc.say("msg")` | Chat bubble above NPC | Quick visual feedback |
| `event.player.sendMessage("msg")` | Message to interacting player | Primary player messaging |
| `npc.world.broadcast("msg")` | ❌ Does NOT exist in 1.7 | Use commands or iterate players |

**1.7.x has no `world.broadcast()`** — use commands or iterate players for broadcasts.
**1.7.x has no `player.message()`** — use `player.sendMessage()` instead.

## Cancelling Events

- Events are **always cancelable** — use `event.isCancelled()` to check, `event.setCancelled(true)` to cancel (note double 'l'). `isCancelable()` does not exist in 1.7.
- Use `e.setCancelled(true)` — note the **double 'l'** (not `setCanceled`)
- `return false` does NOT cancel events — return values from scripts are ignored

```javascript
// 1.7.x damage cancellation
event.setCancelled(true);  // note double 'l'
```

## First-Time Setup

**Always remind new 1.7.x users of these setup steps:**

1. **Enable the script:** The script editor has an "开启" (Enable) toggle — it defaults
   to "否" (No). Remind the user: *"在脚本框页面，将'开启'选项调为'是'，否则脚本不会运行。"*

2. **Nashorn.jar:** Copy `nashorn.jar` from the Java installation
   (`jre/lib/ext/nashorn.jar` or `jdk/jre/lib/ext/nashorn.jar`) into the `mods/` folder.

3. **Language setting:** In the script editor, set "语言 (Language)" to "ECMAScript".

## Script Deployment

Scripts are pasted directly into the in-game UI editor:
- Open the NPC script editor → click into the matching sub-slot tab → paste code

Never reference file paths, directories, or "linking" when giving deployment instructions.

## 1.7.10 Specific Quirks

### getHeldItem()

1.7.x uses `getHeldItem()` for the NPC's held item (1.8+ uses `getMainhandItem()`).
Always null-check:

```javascript
var item = npc.getHeldItem();
if (item) {
    // use item
}
```

### Potion Crash

Applying a potion effect to a dying entity can trigger a `ConcurrentModificationException`
crash. Guard with death checks before applying effects.

### No NBT Access

Standard 1.7.x **cannot** use `getNbt()` or `getEntityNbt()`. Only CustomNPC+
provides NBT support on 1.7.

### storeddata Unreliable

On standard 1.7.10, storeddata is unreliable — data can be lost unexpectedly.
For long-term persistence, consider using **file I/O** as an alternative.
CustomNPC+ fixes storeddata reliability.

## Common Patterns

All 1.7.x scripts are placed in sub-slots, not function definitions.

### Interaction (Dialogue 1 sub-slot)

```javascript
npc.say("Hello, traveler!");
event.player.sendMessage("Welcome!");
```

### Damage handling (Damage sub-slot)

```javascript
if (event.damage > 5) {
    npc.say("That hurt! Damage: " + event.damage);
}
if (event.damage > 100) {
    event.setCancelled(true);  // cancel the damage (double 'l')
}
```

### Tick-based behavior (Update sub-slot, fires every 10 ticks / 0.5s)

```javascript
var count = (npc.tempdata.get("tickCount") || 0) + 1;
npc.tempdata.put("tickCount", count);
if (count % 100 === 0) {
    npc.say("5 seconds have passed!");
}
```
