# CNPC Event System Reference

## 1.8+ Versions: Function Name Mapping

In 1.8+, the Java layer passes events to JavaScript functions with **specific names**.
The function name is derived from the event class name by stripping the "Event" suffix
and converting to lowerCamelCase. This mapping is consistent across all 1.8+ versions.

**Important:** old API docs (kodevelopment.nl) may contain mapping errors.
Always use the mapping below, never infer function names from doc page text.

### Event → Function Name Mapping (extracted from official docs)

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
| **NpcEvent** | | NPC |
| NpcEvent.CollideEvent | `collide` | NPC |
| NpcEvent.DamagedEvent | `damaged` | NPC |
| NpcEvent.DiedEvent | `died` | NPC |
| NpcEvent.InitEvent | `init` | NPC |
| NpcEvent.InteractEvent | `interact` | NPC |
| NpcEvent.KilledEntityEvent | `kill` | NPC |
| NpcEvent.MeleeAttackEvent | `meleeAttack` | NPC |
| NpcEvent.RangedAttackEvent | `rangedAttack` | NPC |
| NpcEvent.TargetEvent | `target` | NPC |
| NpcEvent.TargetLostEvent | `targetLost` | NPC |
| NpcEvent.TimerEvent | `timer` | NPC |
| NpcEvent.TickEvent | `tick` | NPC |
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

All RoleEvent sub-types use function name `role`. The event type is determined by
the NPC's current role/profession. See `references/role.txt` for full sub-event details.

Summary of known RoleEvent sub-types:

| Role | Trigger | Event Fields |
|---|---|---|
| Trader (商人) | Click trade slot (empty) | `event.slot`, `event.currency1`, `event.currency2` |
| Trader (商人) | Trade failed (insufficient) | `event.slot`, `event.currency1`, `event.currency2`, `event.receiving` |
| Follower (雇佣随从) | Successfully hired | `event.days` |
| Follower (雇佣随从) | Hire expired | *(none extra)* |
| Bank (储存者) | Upgrade storage | `event.slot` |
| Bank (储存者) | Unlock storage | `event.slot` |
| Transporter (传送师) | Teleport to location | `event.location` (has getId, getX, getY, getZ, getName, getDimension) |
| Transporter (传送师) | Unlock location | *(none extra)* |
| Mailman (信使) | Send mail | `event.mail` (getSender, getSubject, getText, getQuest, getContainer) |

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

## 1.7.x Note

> For 1.7.x content, see `references/scripting-1.7.md` — the complete, self-contained
> 1.7 reference. This file covers 1.8+ only.
