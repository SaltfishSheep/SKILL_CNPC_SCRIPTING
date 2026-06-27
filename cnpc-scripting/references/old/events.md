# CNPC old convention Event System Reference

This file is the **complete, authoritative reference** for old convention events: sub-script slots,
event fields, and cancellation. For cur convention, see `references/cur/events.md` instead.

## Event Architecture

old convention uses **hardcoded sub-script slots**, not function-name dispatch:

- **Only NPC events** — no Player, Block, Item, or other script types
- **No function name mapping** — each event is hardcoded to a specific sub-script box
- **Full-script eval** — the entire script is `eval()`'d each time. The following
  variables are injected as **separate scope variables** (NOT fields of `event`):
  `world` (ScriptWorld), `npc` (ScriptNpc), `event` (event-specific type), and
  event-dependent extras like `player`, `dialog`, `target`, `entity`.
  Access them directly: `player.sendMessage(...)`, not `event.player.sendMessage(...)`.
- No function definitions — code runs top-to-bottom

## Sub-slot → cur convention Equivalent

| old convention Slot | Fires every | Injected Fields |
|---|---|---|
| 运行 (Run) | Once on load | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc` |
| 更新 (Update) | 10 ticks (0.5s) | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc` |
| 对话 1 (Interact) | Right-click NPC | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc`, `player: ScriptPlayer` |
| 对话 2 (Dialog) | Dialog GUI opens | `event: ScriptEventDialog`, `world: ScriptWorld`, `npc: ScriptNpc`, `player: ScriptPlayer`, `dialog: int` |
| 伤害 (Damage) | NPC takes damage | `event: ScriptEventDamaged`, `world: ScriptWorld`, `npc: ScriptNpc` |
| Killed | NPC dies | `event: ScriptEventKilled`, `world: ScriptWorld`, `npc: ScriptNpc` |
| Attack | NPC melee or ranged attacks | `event: ScriptEventAttack`, `world: ScriptWorld`, `npc: ScriptNpc` |
| Target | NPC acquires target | `event: ScriptEventTarget`, `world: ScriptWorld`, `npc: ScriptNpc` |
| Collide | Entity collision | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc`, `entity: ScriptEntity` |
| Kills | NPC kills entity | `event: ScriptEvent`, `world: ScriptWorld`, `npc: ScriptNpc`, `target: ScriptLivingBase` |
| Dialog Closed | Option selected or dialog closes | `event: ScriptEventDialog`, `world: ScriptWorld`, `npc: ScriptNpc`, `player: ScriptPlayer`, `dialog: int`, `option: int` |

## Cancelling Events

- Events are **always cancelable** — use `event.isCancelled()` to check, `event.setCancelled(true)` to cancel (note double 'l'). `isCancelable()` does not exist in 1.7.
- Use `e.setCancelled(true)` — note the **double 'l'** (not `setCanceled`)
- `return false` does NOT cancel events — return values from scripts are ignored

```javascript
// old convention damage cancellation
event.setCancelled(true);  // note double 'l'
```

## Dialog Gotcha

The "Dialog Closed" slot fires when a player **selects a dialog option** AND when
the dialog is **closed**. These two cases share the same sub-slot — use `event` fields
to distinguish between them.