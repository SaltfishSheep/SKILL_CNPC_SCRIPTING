# JavaDoc Class Reference — 1.7.x (Old)

Quick reference for fetching API documentation. Package: `noppes.npcs.scripted`

## Core Objects

| Class | Purpose |
|---|---|
| `noppes.npcs.scripted.ScriptNpc` | NPC object — all methods directly on npc |
| `noppes.npcs.scripted.ScriptPlayer` | Player object |
| `noppes.npcs.scripted.ScriptWorld` | World object |
| `noppes.npcs.scripted.ScriptEntity` | Base entity (position, movement) |
| `noppes.npcs.scripted.ScriptLivingBase` | Living entity (health, effects) |
| `noppes.npcs.scripted.ScriptLiving` | Living entity (navigation) |
| `noppes.npcs.scripted.ScriptItemStack` | Item stack |
| `noppes.npcs.scripted.ScriptFaction` | Faction data |
| `noppes.npcs.scripted.ScriptRoleInterface` | Role interface (Trader, Follower, etc.) |
| `noppes.npcs.scripted.ScriptJobInterface` | Job interface (Guard, Healer, etc.) |
| `noppes.npcs.scripted.ScriptScoreboard` | Scoreboard access |

## Events

| Class | Purpose |
|---|---|
| `noppes.npcs.scripted.ScriptEvent` | Base event (setCancelled, isCancelled) |
| `noppes.npcs.scripted.ScriptEventDamaged` | NPC damaged (getDamage, getSource, getType) |
| `noppes.npcs.scripted.ScriptEventKilled` | NPC killed (getSource, getType) |
| `noppes.npcs.scripted.ScriptEventAttack` | NPC attacks (getTarget, getDamage, isRanged) |
| `noppes.npcs.scripted.ScriptEventTarget` | NPC target (getTarget, setTarget) |
| `noppes.npcs.scripted.ScriptEventDialog` | Dialog events (isClosing) |

## Class Hierarchy

```
ScriptEntity
├── ScriptLivingBase
│   ├── ScriptLiving (adds navigation)
│   │   └── ScriptNpc
│   └── ScriptPlayer (no navigation)
└── ScriptAnimal, ScriptMonster, ScriptPixelmon
```

## Important Notes

- **No `NpcAPI` class** in 1.7.x — world access is via injected `world` variable
- **NPC has no sub-objects** — methods like `getStats()`, `getAi()`, `getDisplay()` do not exist; all NPC methods are directly on the `npc` object
- **Eval-based** — code runs top-to-bottom in sub-slots, no function definitions
- **Package:** `noppes.npcs.scripted` (not `noppes.npcs.api`)
