# CNPC 1.7.x Event System Reference

This file is the **complete, authoritative reference** for 1.7.x events: sub-script slots,
event fields, and cancellation. For 1.8+, see `references/cur/events.md` instead.

## Event Architecture

1.7.x uses **hardcoded sub-script slots**, not function-name dispatch:

- **Only NPC events** — no Player, Block, Item, or other script types
- **No function name mapping** — each event is hardcoded to a specific sub-script box
- **Full-script eval** — the entire script is `eval()`'d each time. The following
  variables are injected as **separate scope variables** (NOT fields of `event`):
  `world` (ScriptWorld), `npc` (ScriptNpc), `event` (event-specific type), and
  event-dependent extras like `player`, `dialog`, `target`, `entity`.
  Access them directly: `player.sendMessage(...)`, not `event.player.sendMessage(...)`.
- No function definitions — code runs top-to-bottom

## Sub-slot → 1.8+ Equivalent

| 1.7 Slot | 1.8+ equivalent | Fires every | Injected Fields |
|---|---|---|---|
| 运行 (Run) | `init` | Once on load | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc` |
| 更新 (Update) | `tick` | 10 ticks (0.5s) | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc` |
| 对话 1 (Interact) | `interact` | Right-click NPC | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc`, `player: ScriptPlayer` |
| 对话 2 (Dialog) | `dialog` | Dialog GUI opens | `event: ScriptEventDialog`, `world: ScriptWorld`, `npc: ScriptNpc`, `player: ScriptPlayer`, `dialog: int` |
| 伤害 (Damage) | `damaged` | NPC takes damage | `event: ScriptEventDamaged`, `world: ScriptWorld`, `npc: ScriptNpc` |
| Killed | `died` | NPC dies | `event: ScriptEventKilled`, `world: ScriptWorld`, `npc: ScriptNpc` |
| Attack | `meleeAttack` + `rangedAttack` | NPC attacks | `event: ScriptEventAttack`, `world: ScriptWorld`, `npc: ScriptNpc` |
| Target | `target` | NPC acquires target | `event: ScriptEventTarget`, `world: ScriptWorld`, `npc: ScriptNpc` |
| Collide | `collide` | Entity collision | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc`, `entity: ScriptEntity` |
| Kills | `kill` | NPC kills entity | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc`, `target: ScriptLivingBase` |
| Dialog Closed | `dialogClose` | Option selected or dialog closes | `event: ScriptEventDialog`, `world: ScriptWorld`, `npc: ScriptNpc`, `player: ScriptPlayer`, `dialog: int`, `option: int` |

## Event-Specific Methods

All event types extend `ScriptEvent`. The base class provides:

| Method | Purpose |
|---|---|
| `isCancelled()` | Returns `boolean` — whether the event is cancelled |
| `setCancelled(boolean bo)` | Cancels or uncancels the event |

Subclasses inherit these and add their own methods:

| Event Type | Additional Methods |
|---|---|
| `ScriptEventDamaged` (Damage) | `getDamage()`/`setDamage(float)`, `getSource()` → ScriptLivingBase, `getType()` → String, `getClearTarget()`/`setClearTarget(boolean)` |
| `ScriptEventKilled` (Killed) | `getSource()` → ScriptLivingBase, `getType()` → String |
| `ScriptEventAttack` (Attack) | `getTarget()` → ScriptLivingBase, `getDamage()`/`setDamage(float)`, `isRanged()` → boolean |
| `ScriptEventTarget` (Target/TargetLost) | `getTarget()`/`setTarget(ScriptLivingBase)` |
| `ScriptEventDialog` (Dialog/DialogClosed) | `isClosing()` → boolean |
| `ScriptEvent` (Parent type) | *(no additional event methods)* |

## Cancelling Events

- Events are **always cancelable** — use `event.isCancelled()` to check, `event.setCancelled(true)` to cancel (note double 'l'). `isCancelable()` does not exist in 1.7.
- Use `e.setCancelled(true)` — note the **double 'l'** (not `setCanceled`)
- `return false` does NOT cancel events — return values from scripts are ignored

```javascript
// 1.7.x damage cancellation
event.setCancelled(true);  // note double 'l'
```

## Dialog Gotcha

The "Dialog Closed" slot fires when a player **selects a dialog option** AND when
the dialog is **closed**. These two cases share the same sub-slot — use `event` fields
to distinguish between them.

## 1.7.x Note

> For 1.8+, see `references/cur/events.md`. This file covers 1.7.x only.