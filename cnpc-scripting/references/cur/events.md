# CNPC 1.8+ Event System Reference

This file is the **complete, authoritative reference** for 1.8+ events: function-name
mapping, event fields, container rules, and cancellation. For 1.7.x, see
`references/old/events.md` instead.

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
| `setCanceled(cancel)` | `void` | Cancel/uncancel |
| `setPhase(phase)` | `void` | Set the event phase |
| `setResult(result)` | `void` | Set the event result |

**Cancelling events:** Do NOT `return false` — return values from event functions are
ignored by CNPC. Use `e.setCanceled(true)`.

**1.8+ note:** Check `e.isCancelable()` first — some events cannot be cancelled.

```javascript
// 1.8+ cancellation:
function damaged(e) {
    if (e.isCancelable()) {
        e.setCanceled(true);  // cancel the damage
    }
}
```

## Event → Function Name Mapping

In 1.8+, the Java layer passes events to JavaScript functions with **specific names**.
The function name is derived from the event class name by stripping the "Event" suffix
and converting to lowerCamelCase. This mapping is consistent across all 1.8+ versions.

**Important:** old API docs (kodevelopment.nl) may contain mapping errors.
Always use the mapping below, never infer function names from doc page text.

| Event Class | Function Name | Script Container |
|---|---|---|
| **BlockEvent** | | Block |
| BlockEvent.BreakEvent | `broken` | Block |
| BlockEvent.ClickedEvent | `clicked` | Block |
| BlockEvent.CollidedEvent | `collide` | Block |
| BlockEvent.DoorToggleEvent | `doorToggle` | Block |
| BlockEvent.ExplodedEvent | `exploded` | Block |
| BlockEvent.FallenUponEvent | `fallenUpon` | Block |
| BlockEvent.HarvestedEvent | `harvested` | Block |
| BlockEvent.InitEvent | `init` | Block |
| BlockEvent.InteractEvent | `interact` | Block |
| BlockEvent.NeighborChangedEvent | `neighborChanged` | Block |
| BlockEvent.RainFillEvent | `rainFilled` | Block |
| BlockEvent.RedstoneEvent | `redstone` | Block |
| BlockEvent.TimerEvent | `timer` | Block |
| BlockEvent.TickEvent | `tick` | Block |
| **CustomGuiEvent** | | *No dedicated container (see below)* |
| CustomGuiEvent.ButtonEvent | `customGuiButton` | Parent container |
| CustomGuiEvent.CloseEvent | `customGuiClosed` | Parent container |
| CustomGuiEvent.ScrollEvent | `customGuiScroll` | Parent container |
| CustomGuiEvent.SlotClickedEvent | `customGuiSlotClicked` | Parent container |
| CustomGuiEvent.SlotEvent | `customGuiSlot` | Parent container |
| **DialogEvent** (Player scripts only) | | Player |
| DialogEvent.CloseEvent | `dialogClose` | Player |
| DialogEvent.DialogEvent | `dialog` | Player |
| DialogEvent.OptionEvent | `dialogOption` | Player |
| **ForgeEvent** | | Forge |
| ForgeEvent.WorldEvent | *(varies)* | Forge |
| **WorldEvent** | | World |
| WorldEvent.ScriptCommandEvent (1.12.2) | `scriptCommand` | World |
| WorldEvent.ScriptTriggerEvent (1.18+) | `trigger` | World |
| **ItemEvent** | | Item |
| ItemEvent.AttackEvent | `attack` | Item |
| ItemEvent.InitEvent | `init` | Item |
| ItemEvent.InteractEvent | `interact` | Item |
| ItemEvent.PickedUpEvent | `pickedUp` | Item |
| ItemEvent.SpawnEvent | `spawn` | Item |
| ItemEvent.TossedEvent | `toss` | Item |
| ItemEvent.TickEvent | `tick` | Item |

**ItemEvent behavior notes:**
- `tick` — only fires when the item is **in a player's inventory** (every 10 ticks).
- `interact` — fires on right-click with the item (air, block, or entity).
- `attack` — fires on left-click with the item (air, block, or entity).
- `toss` — fires when the player throws the item on the ground. Cancelling prevents the item from appearing in the world, but it still leaves the inventory.
- `spawn` — fires when a scripted item entity spawns into the world.
- `pickedUp` — fires when a player picks up the scripted item.

| Event Class | Function Name | Script Container |
|---|---|---|
| **NpcEvent** | | NPC |
| NpcEvent.CollideEvent | `collide` | NPC |
| NpcEvent.DamagedEvent | `damaged` | NPC |
| NpcEvent.DiedEvent | `died` | NPC |
| NpcEvent.InitEvent | `init` | NPC |
| NpcEvent.InteractEvent | `interact` | NPC |
| NpcEvent.KilledEntityEvent | `kill` | NPC |
| NpcEvent.MeleeAttackEvent | `meleeAttack` | NPC |
| NpcEvent.RangedLaunchedEvent | `rangedLaunched` (≤1.16) / `rangedAttack` (1.18+) | NPC |
| NpcEvent.TargetEvent | `target` | NPC |
| NpcEvent.TargetLostEvent | `targetLost` | NPC |
| NpcEvent.TimerEvent | `timer` | NPC |
| NpcEvent.UpdateEvent | `tick` | NPC |
| **PlayerEvent** | | Player |
| PlayerEvent.AttackEvent | `attack` | Player |
| PlayerEvent.BreakEvent | `broken` | Player |
| PlayerEvent.ChatEvent | `chat` | Player |
| PlayerEvent.CloseContainer | `containerClosed` | Player |
| PlayerEvent.ContainerOpen | `containerOpen` | Player |
| PlayerEvent.DamagedEntityEvent | `damagedEntity` | Player |
| PlayerEvent.DamagedEvent | `damaged` | Player |
| PlayerEvent.DiedEvent | `died` | Player |
| PlayerEvent.FactionUpdateEvent | `factionUpdate` | Player |
| PlayerEvent.InitEvent | `init` | Player |
| PlayerEvent.InteractEvent | `interact` | Player |
| PlayerEvent.KeyPressedEvent | `keyPressed` | Player |
| PlayerEvent.KeyReleasedEvent | `keyReleased` | Player |
| PlayerEvent.KilledEntityEvent | `kill` | Player |
| PlayerEvent.LevelUpEvent | `levelUp` | Player |
| PlayerEvent.LoginEvent | `login` | Player |
| PlayerEvent.LogoutEvent | `logout` | Player |
| PlayerEvent.PickUpEvent | `pickedUp` | Player |
| PlayerEvent.PlaySoundEvent | `playSound` | Player |
| PlayerEvent.RangedLaunchedEvent | `rangedLaunched` | Player |
| PlayerEvent.TimerEvent | `timer` | Player |
| PlayerEvent.TossEvent | `toss` | Player |
| PlayerEvent.TickEvent | `tick` | Player |
| **ProjectileEvent** | | *No dedicated container (see below)* |
| ProjectileEvent.ImpactEvent | `projectileImpact` | Registered containers |
| ProjectileEvent.TickEvent | `projectileTick` | Registered containers |
| **QuestEvent** (Player scripts only) | | Player |
| QuestEvent.QuestStartEvent | `questStart` | Player |
| QuestEvent.QuestCompletedEvent | `questCompleted` | Player |
| QuestEvent.QuestTurnedInEvent | `questTurnIn` | Player |
| **RoleEvent** (NPC scripts only) | | NPC |

### RoleEvent Details (NPC scripts only)

All RoleEvent sub-types use function name `role`. The event type is determined by the NPC's current role.

Summary of known RoleEvent sub-types:

| Role | Event Type | Trigger | Event Fields |
|---|---|---|---|
| Trader (商人) | RoleEvent.TraderEvent | Click trade slot | `event.slot`, `event.currency1`, `event.currency2` |
| Trader (商人) | RoleEvent.TradeFailedEvent | Trade failed (insufficient) | `event.slot`, `event.currency1`, `event.currency2`, `event.receiving` |
| Follower (雇佣随从) | RoleEvent.FollowerHireEvent | Successfully hired | `event.days` |
| Follower (雇佣随从) | RoleEvent.FollowerFinishedEvent | Hire expired | *(none extra)* |
| Bank (储存者) | RoleEvent.BankUpgradedEvent | Upgrade storage | `event.slot` |
| Bank (储存者) | RoleEvent.BankUnlockedEvent | Unlock storage | `event.slot` |
| Transporter (传送师) | RoleEvent.TransporterUseEvent | Teleport to location | `event.location` |
| Transporter (传送师) | RoleEvent.TransporterUnlockedEvent | Unlock location | *(none extra)* |
| Mailman (信使) | RoleEvent.MailmanEvent | Send mail | `event.mail` |

## Script Container Rules

### Standard containers
Most events are scoped to a specific script container type:
- **NpcEvent** → NPC script (the NPC's own script box)
- **PlayerEvent** → Player script (global player scripts)
- **BlockEvent** → Block script
- **ForgeEvent** → Forge script
- **ItemEvent** → Item script
- **DialogEvent** → Player script (only)
- **QuestEvent** → Player script (only)
- **RoleEvent** → NPC script (only)

### Exception: CustomGuiEvent
- No dedicated script container.
- Records the container that **instantiated** the GUI at creation time.
- When events fire, they trigger the matching function name in that single recorded container.
- Only ONE container is recorded (the creator).

### Exception: ProjectileEvent
- No dedicated script container.
- Call `IProjectile.enableEvents()` to register the **current** script container.
- Multiple containers can register (all containers that called enableEvents).
- When events fire, they trigger the matching function in ALL registered containers.

## Field Availability Rules

- **Never assume `e.player` exists** — it is only present on events that involve a player.
- All NpcEvent subclasses inherit `e.npc: ICustomNpc`. Use `e.npc.world` for world access.
- The function name determines the event class. A field on `interact` may not exist on `damaged`.
- All events expose `e.API: NpcAPI`.

## Event Field Table (verified against 1.12.2 JavaDoc, applies to all 1.8+ versions)

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
| `rangedLaunched` (≤1.16) / `rangedAttack` (1.18+) | NpcEvent.RangedLaunchedEvent | `e.npc`, `e.target: IEntityLivingBase` |
| `target` | NpcEvent.TargetEvent | `e.npc`, `e.target: IEntityLivingBase` |
| `targetLost` | NpcEvent.TargetLostEvent | `e.npc`, `e.oldTarget: IEntityLivingBase` |
| `collide` | NpcEvent.CollideEvent | `e.npc`, `e.source: IEntity` |
| `timer` | NpcEvent.TimerEvent | `e.npc`, `e.id: int` |
| `role` | RoleEvent | `e.npc`, `e.player: IPlayer`, role-specific fields (see RoleEvent Details above) |
| **PlayerEvent** | | *(all inherit `e.player: IPlayer`)* |
| `interact` | PlayerEvent.InteractEvent | `e.player`, `e.target: Object`, `e.type: int` (0=air, 1=entity, 2=block) |
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

## Timer API & Handler

Timers are managed via `npc.getTimers()`:

| Method | Purpose |
|---|---|
| `start(id, ticks, repeat)` | Start timer; errors if id already active |
| `forceStart(id, ticks, repeat)` | Start/overwrite timer with same id |
| `stop(id)` | Stop a running timer; returns false if not found |
| `reset(id)` | Reset timer countdown to 0 |
| `has(id)` | Check if timer is active |
| `clear()` | Stop all timers |

**Note:** The timer event fires at `ticks + 1`, not exactly at the specified tick count.
For example, `start(1, 99, true)` fires on tick 100, not 99.

```javascript
function init(e) {
    // Start a repeating timer every 100 ticks (5 seconds)
    e.npc.getTimers().start(1, 99, true);
}

function timer(e) {
    e.npc.say("5 seconds have passed!");
}
```

## 1.7.x Note

> For 1.7.x, see `references/old/scripting.md` + `references/old/npc-objects.md` +
> `references/old/storage.md` + `references/old/javadoc.md`. This file covers 1.8+ only.
