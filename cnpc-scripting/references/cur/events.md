# CNPC cur convention Event System Reference

This file is the **complete, authoritative reference** for cur convention events: function-name
mapping, container rules, and cancellation. For old convention, see
`references/old/events.md` instead.

## Naming Convention

The function parameter `e` is just a convention (short for "event"). It is a **formal
parameter** — you can name it anything.

## Universal Fields and Methods

### `e.API` — Available on ALL events

Every event object exposes `e.API: NpcAPI`, the global NpcAPI singleton. Use it for
world-level operations inside any handler.

### Inherited Forge Event methods — Available on ALL events

All CNPC events extend `net.minecraftforge.fml.common.eventhandler.Event`. These
methods are always callable on `e`:

| Method | Signature | Purpose |
|---|---|---|
| `isCancelable()` | `boolean` | Whether the event can be cancelled (cur convention only) |
| `isCanceled()` | `boolean` | Whether the event is currently cancelled |
| `setCanceled(cancel)` | `void` | Cancel/uncancel |

**Cancelling events:** Do NOT `return false` — return values from event functions are
ignored by CNPC. Use `e.setCanceled(true)`.

**cur convention note:** Check `e.isCancelable()` first — some events cannot be cancelled.

## Event → Function Name Mapping

In cur convention, the Java layer passes events to JavaScript functions with **specific names**.
This mapping is consistent across all cur convention versions.

**Script Container:** After an event is triggered, it needs to be passed to the functions in the script container. 
   There are different types of script containers; 
   in CNPC, there are five kinds of script boxes: 'Player', 'Forge', 'NPC', 'Item', and 'Block'.
   Each script box corresponds to a type of script container. 
   For users, they only know about the 'script box' and aren’t aware of the script container.

**Important:** Always use the mapping below, never assume function names.

| Event Class | Function Name | Script Container |
|---|---|---|
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
| **WorldEvent** | | Forge |
| WorldEvent.ScriptCommandEvent (1.12.2) | `scriptCommand` | Forge |
| WorldEvent.ScriptTriggerEvent (1.18+) | `trigger` | Forge |
| **ItemEvent** | | Item |
| ItemEvent.AttackEvent | `attack` | Item |
| ItemEvent.InitEvent | `init` | Item |
| ItemEvent.InteractEvent | `interact` | Item |
| ItemEvent.PickedUpEvent | `pickedUp` | Item |
| ItemEvent.SpawnEvent | `spawn` | Item |
| ItemEvent.TossedEvent | `toss` | Item |
| ItemEvent.TickEvent | `tick` | Item |
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

**ItemEvent behavior notes:** Only special 'script items' can use them.
**BlockEvent behavior notes:** Only special 'script blocks' can use them.

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

| Role | Event Type | Trigger |
|---|---|---|
| Trader (商人) | RoleEvent.TraderEvent | Click trade slot |
| Trader (商人) | RoleEvent.TradeFailedEvent | Trade failed (insufficient) |
| Follower (雇佣随从) | RoleEvent.FollowerHireEvent | Successfully hired |
| Follower (雇佣随从) | RoleEvent.FollowerFinishedEvent | Hire expired |
| Bank (储存者) | RoleEvent.BankUpgradedEvent | Upgrade storage |
| Bank (储存者) | RoleEvent.BankUnlockedEvent | Unlock storage |
| Transporter (传送师) | RoleEvent.TransporterUseEvent | Teleport to location |
| Transporter (传送师) | RoleEvent.TransporterUnlockedEvent | Unlock location |
| Mailman (信使) | RoleEvent.MailmanEvent | Send mail |

## Script Container Rules

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

## Canceled Semantic Inconsistency

The result of some event cancellations doesn't make sense semantically. 
For example, if `toss` is canceled, it won't create a thrown item entity, 
but the item in the inventory will still be removed. When canceling events, 
we need to consider possible semantic issues.

## Field Availability Rules

- **Never assume `e.player` exists** — it is only present on events that involve a player.
- All NpcEvent subclasses inherit `e.npc: ICustomNpc`. Use `e.npc.world` for world access.
- The function name determines the event class. A field on `interact` may not exist on `damaged`.
- All events expose `e.API: NpcAPI`.

## Important Field Patterns

1. **`e.npc`** — available in NpcEvent subclasses and DialogEvent.
2. **`e.player`** — only on events involving player interaction.
3. **`e.source: IEntity`** — the **direct** damage source entity. 
   Unreliable for ranged/projectile attacks. For the root attacker, 
   trace through `e.damageSource` (IDamageSource, never `null`).
   `e.source` may be `null` for environmental damage (fire, lava, falling); 
   `e.damageSource` is always present.
4. **`e.API`** — available on ALL events, equivalent to `NpcAPI.Instance()`.

## Timer API & Handler

Timers are type of `noppes.npcs.api.ITimers`,
use `start(id, ticks, repeat)` or `forceStart(id, ticks, repreat)`,
`forceStart` will cover the old timer, while `start` will crash.
When you start a timer, `TimerEvent` will be enabled.

**Note:** The timer event fires at `ticks + 1`, not exactly at the specified tick count.
For example, `start(1, 99, true)` fires on tick 100, not 99.