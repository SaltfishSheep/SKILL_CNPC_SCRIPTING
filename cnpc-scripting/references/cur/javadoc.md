# JavaDoc Class Reference — 1.8+ (Cur)

Quick reference for fetching API documentation. Verified against 1.12.2 JavaDoc.
**Also applies to Goodbird (1.19.2+)** — same API structure, different package paths for some classes.

## Core Objects

| Class | Purpose |
|---|---|
| `noppes.npcs.api.entity.ICustomNpc` | NPC object — use `npc.getXxx()` sub-objects |
| `noppes.npcs.api.entity.IPlayer` | Player object |
| `noppes.npcs.api.IWorld` | World object |
| `noppes.npcs.api.entity.IEntity` | Base entity interface |
| `noppes.npcs.api.entity.IEntityLivingBase` | Living entity (health, effects) |
| `noppes.npcs.api.entity.IEntityLiving` | Living entity (navigation) |
| `noppes.npcs.api.item.IItemStack` | Item stack |
| `noppes.npcs.api.NpcAPI` | Global API singleton |

## NPC Sub-Objects

| Class | Purpose |
|---|---|
| `noppes.npcs.api.entity.data.INPCStats` | Health, melee/ranged strength, resistances |
| `noppes.npcs.api.entity.data.INPCAi` | Movement, standing, retaliation |
| `noppes.npcs.api.entity.data.INPCDisplay` | Name, skin, model, size |
| `noppes.npcs.api.entity.data.INPCInventory` | Weapons, armor, drops |
| `noppes.npcs.api.entity.data.INPCAdvanced` | Advanced settings |
| `noppes.npcs.api.entity.data.INPCRole` | Role (Trader, Follower, etc.) |
| `noppes.npcs.api.entity.data.INPCJob` | Job (Guard, Healer, etc.) |
| `noppes.npcs.api.entity.data.INPCMelee` | Melee combat settings |
| `noppes.npcs.api.entity.data.INPCRanged` | Ranged combat settings |
| `noppes.npcs.api.ITimers` | Timer scheduling |
| `noppes.npcs.api.entity.data.ILine` | In-world dialog text display |

## Events

| Package | Key Classes |
|---|---|
| `noppes.npcs.api.event.NpcEvent` | InitEvent, InteractEvent, DamagedEvent, DiedEvent, KilledEntityEvent, MeleeAttackEvent, RangedLaunchedEvent, TargetEvent, TargetLostEvent, CollideEvent, TimerEvent, UpdateEvent |
| `noppes.npcs.api.event.PlayerEvent` | InitEvent, InteractEvent, AttackEvent, BreakEvent, DamagedEvent, DamagedEntityEvent, DiedEvent, KilledEntityEvent, ChatEvent, KeyPressedEvent, LoginEvent, LogoutEvent, UpdateEvent, TimerEvent |
| `noppes.npcs.api.event.BlockEvent` | InitEvent, InteractEvent, BreakEvent, ClickedEvent, CollidedEvent, TimerEvent, UpdateEvent, RedstoneEvent, HarvestedEvent, NeighborChangedEvent, DoorToggleEvent, ExplodedEvent, RainFillEvent |
| `noppes.npcs.api.event.ItemEvent` | InitEvent, InteractEvent, AttackEvent, UpdateEvent, TossedEvent, PickedUpEvent, SpawnEvent |
| `noppes.npcs.api.event.DialogEvent` | OpenEvent, OptionEvent, CloseEvent |
| `noppes.npcs.api.event.QuestEvent` | QuestStartEvent, QuestCompletedEvent, QuestTurnedInEvent |
| `noppes.npcs.api.event.RoleEvent` | TraderEvent, TradeFailedEvent, FollowerHireEvent, FollowerFinishedEvent, BankUpgradedEvent, BankUnlockedEvent, TransporterUseEvent, TransporterUnlockedEvent, MailmanEvent |
| `noppes.npcs.api.event.CustomGuiEvent` | ButtonEvent, CloseEvent, ScrollEvent, SlotClickEvent, SlotEvent |
| `noppes.npcs.api.event.CustomContainerEvent` | CloseEvent, SlotClickedEvent |
| `noppes.npcs.api.event.ProjectileEvent` | ImpactEvent, UpdateEvent |
| `noppes.npcs.api.event.WorldEvent` | ScriptCommandEvent |
| `noppes.npcs.api.event.ForgeEvent` | InitEvent, EntityEvent, WorldEvent |
| `noppes.npcs.api.event.HandlerEvent` | FactionsLoadedEvent, RecipesLoadedEvent |

## GUI

| Class | Purpose |
|---|---|
| `noppes.npcs.api.gui.ICustomGui` | Custom GUI |
| `noppes.npcs.api.gui.IButton` | GUI button |
| `noppes.npcs.api.gui.IItemSlot` | GUI item slot |
| `noppes.npcs.api.gui.ILabel` | GUI label |
| `noppes.npcs.api.gui.IScroll` | GUI scroll list |
| `noppes.npcs.api.gui.ITextField` | GUI text field |
| `noppes.npcs.api.gui.ITexturedButton` | Textured button |
| `noppes.npcs.api.gui.ITexturedRect` | Textured rectangle |
| `noppes.npcs.api.gui.ICustomGuiComponent` | Base GUI component |

## Handler & Data

| Class | Purpose |
|---|---|
| `noppes.npcs.api.handler.data.IDialog` | Dialog data |
| `noppes.npcs.api.handler.data.IDialogOption` | Dialog option |
| `noppes.npcs.api.handler.data.IDialogCategory` | Dialog category |
| `noppes.npcs.api.handler.data.IQuest` | Quest data |
| `noppes.npcs.api.handler.data.IQuestCategory` | Quest category |
| `noppes.npcs.api.handler.data.IQuestObjective` | Quest objective |
| `noppes.npcs.api.handler.data.IFaction` | Faction data |
| `noppes.npcs.api.handler.data.IRecipe` | Recipe data |
| `noppes.npcs.api.handler.data.IAvailability` | Availability conditions |

## Block & Item

| Class | Purpose |
|---|---|
| `noppes.npcs.api.block.IBlock` | Block state |
| `noppes.npcs.api.block.IBlockScripted` | Scripted block |
| `noppes.npcs.api.block.IBlockScriptedDoor` | Scripted door |
| `noppes.npcs.api.block.IBlockFluidContainer` | Fluid container block |
| `noppes.npcs.api.block.ITextPlane` | Text plane (signs) |
| `noppes.npcs.api.item.IItemStack` | Item stack |
| `noppes.npcs.api.item.IItemScripted` | Scripted item |
| `noppes.npcs.api.item.IItemArmor` | Armor item |
| `noppes.npcs.api.item.IItemBlock` | Block item |
| `noppes.npcs.api.item.IItemBook` | Book item |

## Entities

| Class | Purpose |
|---|---|
| `noppes.npcs.api.entity.IProjectile` | Projectile entity |
| `noppes.npcs.api.entity.IAnimal` | Animal entity |
| `noppes.npcs.api.entity.IMonster` | Monster entity |

## Other

| Class | Purpose |
|---|---|
| `noppes.npcs.api.IContainer` | Container (inventory) |
| `noppes.npcs.api.IContainerCustomChest` | Custom chest container |
| `noppes.npcs.api.IDamageSource` | Damage source |
| `noppes.npcs.api.IDimension` | Dimension |
| `noppes.npcs.api.INbt` | NBT tag compound |
| `noppes.npcs.api.IPos` | Position |
| `noppes.npcs.api.IRayTrace` | Ray trace result |
| `noppes.npcs.api.IScoreboard` | Scoreboard |
| `noppes.npcs.api.IScoreboardObjective` | Scoreboard objective |
| `noppes.npcs.api.IScoreboardScore` | Scoreboard score |
| `noppes.npcs.api.IScoreboardTeam` | Scoreboard team |
| `noppes.npcs.api.CommandNoppesBase` | Custom command base |

## Goodbird (1.19.2+)

For Goodbird's port, the docs are on GitHub Pages with a different structure.
Navigate via sidebar topics, not JavaDoc package paths.
