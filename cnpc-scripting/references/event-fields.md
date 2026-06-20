# Event Fields Reference

Before using any event field, **always fetch the specific event's JavaDoc page** for the
user's version. This table is based on 1.12.2 JavaDoc — fields may differ slightly
across versions.

## Naming Convention

The function parameter `e` is just a convention (short for "event"). It is a **formal
parameter** — you can name it anything (some developers use `c`). The actual instance
is the event object matching the function name:

```javascript
// All equivalent:
function interact(e) { var player = e.player; }
function interact(c) { var player = c.player; }
function interact(event) { var player = event.player; }
```

## Universal Fields and Methods

### `e.API` — Available on ALL events

Every event object exposes `e.API: NpcAPI`, the global NpcAPI singleton. Use it for
world-level operations inside any handler:

```javascript
function interact(e) {
    var wolf = e.API.spawnNPC(e.npc.world, x, y, z);
}
```

This is equivalent to `NpcAPI.Instance()` but more convenient when inside a handler.

### Inherited Forge Event methods — Available on ALL events

All CNPC events extend `net.minecraftforge.fml.common.eventhandler.Event`. These
methods are always callable on `e`:

| Method | Signature | Purpose |
|---|---|---|
| `getListenerList()` | `ListenerList` | Get the event listener list |
| `getPhase()` | `EventPriority` | Get the current event phase |
| `getResult()` | `Result` | Get the event result |
| `hasResult()` | `boolean` | Whether the event has a result |
| `isCancelable()` | `boolean` | Whether the event can be cancelled (1.8+ only — 1.7 has no such method) |
| `isCanceled()` | `boolean` | Whether the event is currently cancelled |
| `setCanceled(cancel)` | `void` | Cancel/uncancel (1.8+, single 'l') |
| `setCancelled(cancel)` | `void` | Cancel/uncancel (1.7.x, double 'l') |
| `setPhase(phase)` | `void` | Set the event phase |
| `setResult(result)` | `void` | Set the event result |

**Cancelling events:** Do NOT `return false` — return values from event functions are
ignored by CNPC. Use `e.setCanceled(true)` (1.8+) or `e.setCancelled(true)` (1.7.x).

**1.7.x note:** 1.7 events are always cancelable — `isCancelable()` does not exist.
Call `setCancelled(true)` directly without checking.

**1.8+ note:** Check `e.isCancelable()` first — some events cannot be cancelled.

```javascript
// 1.8+ cancellation:
function damaged(e) {
    if (e.isCancelable()) {
        e.setCanceled(true);  // cancel the damage
    }
}

// 1.7.x cancellation:
// Events are always cancelable, no isCancelable() check needed.
function damaged(e) {
    e.setCancelled(true);  // note double 'l'
}
```

## Field Availability Rules

- **Never assume `e.player` exists** — it is only present on events that involve a player.
- All NpcEvent subclasses inherit `e.npc: ICustomNpc`. Use `e.npc.world` for world access.
- The function name determines the event class. A field on `interact` may not exist on `damaged`.
- All events expose `e.API: NpcAPI`.

## Event Field Table (verified against 1.12.2 JavaDoc)

| Function | Event Class | Fields |
|---|---|---|
| **NpcEvent** | | *(all inherit `e.npc: ICustomNpc`)* |
| `init` | NpcEvent.InitEvent | `e.npc` |
| `tick` | NpcEvent.UpdateEvent | `e.npc` |
| `interact` | NpcEvent.InteractEvent | `e.npc`, `e.player: IPlayer` |
| `damaged` | NpcEvent.DamagedEvent | `e.npc`, `e.source: IEntity` (direct source; use `e.damageSource` for root attacker), `e.damage: float`, `e.damageSource: IDamageSource`, `e.clearTarget: boolean` |
| `died` | NpcEvent.DiedEvent | `e.npc`, `e.source: IEntity` (direct source; use `e.damageSource` for root attacker), `e.type: String`, `e.damageSource: IDamageSource`, `e.droppedItems: IItemStack[]`, `e.expDropped: int`, `e.line: ILine` |
| `kill` | NpcEvent.KilledEntityEvent | `e.npc`, `e.killed: IEntityLivingBase` |
| `meleeAttack` | NpcEvent.MeleeAttackEvent | `e.npc`, `e.target: IEntityLivingBase`, `e.damage: float` |
| `rangedAttack` | NpcEvent.RangedLaunchedEvent | `e.npc`, `e.target: IEntityLivingBase` |
| `target` | NpcEvent.TargetEvent | `e.npc`, `e.target: IEntityLivingBase` |
| `targetLost` | NpcEvent.TargetLostEvent | `e.npc`, `e.oldTarget: IEntityLivingBase` |
| `collide` | NpcEvent.CollideEvent | `e.npc`, `e.source: IEntity` |
| `timer` | NpcEvent.TimerEvent | `e.npc`, `e.id: int` |
| `role` | RoleEvent | `e.npc`, `e.player: IPlayer`, role-specific fields (see role.txt) |
| **PlayerEvent** | | *(all inherit `e.player: IPlayer`)* |
| `interact` | PlayerEvent.InteractEvent | `e.player` |
| `attack` | PlayerEvent.AttackEvent | `e.player`, `e.type: int` |
| `broken` | PlayerEvent.BreakEvent | `e.player`, `e.block: IBlock` |
| `damaged` | PlayerEvent.DamagedEvent | `e.player`, `e.source: IEntity`, `e.damage: float` |
| `damagedEntity` | PlayerEvent.DamagedEntityEvent | `e.player`, `e.target: IEntity`, `e.damage: float`, `e.damageSource: IDamageSource` |
| `died` | PlayerEvent.DiedEvent | `e.player`, `e.source: IEntity` |
| `kill` | PlayerEvent.KilledEntityEvent | `e.player`, `e.killed: IEntityLivingBase` |
| `tick` | PlayerEvent.TickEvent | `e.player` |
| `chat` | PlayerEvent.ChatEvent | `e.player`, `e.message: String` |
| `keyPressed` | PlayerEvent.KeyPressedEvent | `e.player`, `e.key: int`, `e.isCtrl: boolean`, `e.isShift: boolean`, `e.isAlt: boolean` |
| `timer` | PlayerEvent.TimerEvent | `e.player`, `e.id: int` |
| `login` | PlayerEvent.LoginEvent | `e.player` |
| `logout` | PlayerEvent.LogoutEvent | `e.player` |
| `containerOpen` | PlayerEvent.ContainerOpen | `e.player`, `e.container: IContainer` |
| `containerClosed` | PlayerEvent.CloseContainer | `e.player`, `e.container: IContainer` |
| `pickedUp` | PlayerEvent.PickUpEvent | `e.player`, `e.item: IItemStack` |
| `toss` | PlayerEvent.TossEvent | `e.player`, `e.item: IItemStack` |
| `rangedLaunched` | PlayerEvent.RangedLaunchedEvent | `e.player`, `e.projectile: IProjectile` |
| `factionUpdate` | PlayerEvent.FactionUpdateEvent | `e.player`, `e.faction: IFaction`, `e.points: int`, `e.init: boolean` |
| `levelUp` | PlayerEvent.LevelUpEvent | `e.player`, `e.level: int` |
| **BlockEvent** | | *(all inherit `e.block: IBlock`)* |
| `interact` | BlockEvent.InteractEvent | `e.block`, `e.player: IPlayer` |
| `broken` | BlockEvent.BreakEvent | `e.block` |
| `clicked` | BlockEvent.ClickedEvent | `e.block`, `e.player: IPlayer` |
| `collide` | BlockEvent.CollidedEvent | `e.block`, `e.source: IEntity` |
| `timer` | BlockEvent.TimerEvent | `e.block`, `e.id: int` |
| `tick` | BlockEvent.TickEvent | `e.block` |
| `redstone` | BlockEvent.RedstoneEvent | `e.block`, `e.power: int` |
| `doorToggle` | BlockEvent.DoorToggleEvent | `e.block` |
| `exploded` | BlockEvent.ExplodedEvent | `e.block` |
| `harvested` | BlockEvent.HarvestedEvent | `e.block`, `e.player: IPlayer` |
| `neighborChanged` | BlockEvent.NeighborChangedEvent | `e.block` |
| **DialogEvent** (Player scripts) | | |
| `dialog` | DialogEvent.OpenEvent | `e.player: IPlayer`, `e.dialog: IDialog`, `e.npc: ICustomNpc` |
| `dialogOption` | DialogEvent.OptionEvent | `e.player: IPlayer`, `e.dialog: IDialog`, `e.npc: ICustomNpc`, `e.option: IDialogOption` |
| `dialogClose` | DialogEvent.CloseEvent | `e.player: IPlayer`, `e.dialog: IDialog`, `e.npc: ICustomNpc` |
| **ItemEvent** | | *(all inherit `e.item: IItemStack`)* |
| `init` | ItemEvent.InitEvent | `e.item` |
| `tick` | ItemEvent.UpdateEvent | `e.item`, `e.player: IPlayer` (only when in inventory) |
| `interact` | ItemEvent.InteractEvent | `e.item`, `e.player: IPlayer` |
| `attack` | ItemEvent.AttackEvent | `e.item`, `e.player: IPlayer`, `e.type: int` |
| `toss` | ItemEvent.TossEvent | `e.item`, `e.player: IPlayer` |
| `pickedUp` | ItemEvent.PickedUpEvent | `e.item`, `e.player: IPlayer` |
| `spawn` | ItemEvent.SpawnEvent | `e.item` |
| **CustomGuiEvent** | | *(all inherit `e.player: IPlayer`, `e.gui: ICustomGui`)* |
| `customGuiButton` | CustomGuiEvent.ButtonEvent | `e.player`, `e.gui`, `e.buttonId: int`, `e.button: IButton` |
| `customGuiClosed` | CustomGuiEvent.CloseEvent | `e.player`, `e.gui` |
| `customGuiScroll` | CustomGuiEvent.ScrollEvent | `e.player`, `e.gui` |
| `customGuiSlotClicked` | CustomGuiEvent.SlotClickEvent | `e.player`, `e.gui`, `e.slot: IItemSlot`, `e.dragType: int`, `e.clickType: String` |
| `customGuiSlot` | CustomGuiEvent.SlotEvent | `e.player`, `e.gui`, `e.slot: IItemSlot` |
| **QuestEvent** (Player scripts) | | |
| `questStart` | QuestEvent.QuestStartEvent | `e.player: IPlayer`, `e.quest: IQuest` |
| `questCompleted` | QuestEvent.QuestCompletedEvent | `e.player: IPlayer`, `e.quest: IQuest` |
| `questTurnIn` | QuestEvent.QuestTurnedInEvent | `e.player: IPlayer`, `e.quest: IQuest` |
| **ProjectileEvent** | | |
| `projectileImpact` | ProjectileEvent.ImpactEvent | `e.projectile: IProjectile`, `e.target: IEntity` |
| `projectileTick` | ProjectileEvent.TickEvent | `e.projectile: IProjectile` |
| **WorldEvent** | | |
| `scriptCommand` (1.12.2) / `trigger` (1.18+) | WorldEvent.ScriptCommandEvent (1.12.2) / ScriptTriggerEvent (1.18+) | `e.world: IWorld`, `e.id: int`, `e.entity: IEntity` (nullable), `e.pos: IPos`, `e.arguments: Object[]`. Runs in Player, NPC, Script Block, or Forge scripts depending on how the command was invoked. |

## Important Field Patterns

1. **`e.npc`** — available in NpcEvent subclasses and DialogEvent. Use `e.npc.world` for world access.
2. **`e.player`** — only on events involving player interaction (see table above). Not present
   on `damaged`, `died`, `tick`, `init`, `kill`, `meleeAttack`, `rangedAttack`, `target`,
   `targetLost`, `collide`, `timer` (NpcEvent), `timer` (BlockEvent), `spawn` (ItemEvent),
   or `projectileTick`. Never assume — always check.
3. **`e.source: IEntity`** — the **direct** damage source entity. Unreliable for ranged/projectile
   attacks: the source may be the projectile, not the shooter. For the root attacker,
   trace through `e.damageSource` (IDamageSource, never `null`).
   `e.source` may be `null` for environmental damage (fire, lava, falling); `e.damageSource` is always present.
4. **`e.target`** — on attack events: the attack target.
5. **`e.damage`** — on damage/attack events (NpcEvent + PlayerEvent): a `float`, not `int`.
6. **`e.API`** — available on ALL events, equivalent to `NpcAPI.Instance()`.

## 1.7.x Note

> For 1.7.x event fields, see `references/scripting-1.7.md`. This file covers 1.8+ only.
