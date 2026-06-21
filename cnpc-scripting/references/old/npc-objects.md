# NPC Object Model & World Access — 1.7.x (Old)

This file covers the 1.7.x NPC/Player/World object model. For 1.8+ (cur), see
`references/cur/npc-objects.md` instead.

## Key Differences from 1.8+

| Feature | 1.7.x (old) | 1.8+ (cur) |
|---|---|---|
| Class names | ScriptNpc, ScriptPlayer, ScriptWorld | ICustomNpc, IPlayer, IWorld |
| Package | `noppes.npcs.scripted` | `noppes.npcs.api` |
| Sub-objects | ❌ None — all methods directly on npc | ✅ getStats(), getAi(), getDisplay(), etc. |
| API access | Injected scope variables: `event`, `world`, `npc` (no function wrapper) | `e.API`, `NpcAPI.Instance()` |
| Hook signature | Eval-based: bare code in sub-slot (no function definition) | `function init(e)` with `e.npc`, `e.world` |
| Inventory | Direct: `npc.getRightItem()`, `npc.getArmor(slot)` | `npc.getInventory().getXXX()` |
| Stats | Direct: `npc.getMeleeStrength()`, `npc.setMaxHealth()` | `npc.getStats().getXXX()` |
| Display | Direct: `npc.getName()`, `npc.setTexture()` | `npc.getDisplay().getXXX()` |
| Navigation | Inherited: `npc.navigateTo(x,y,z,speed)` | `npc.getAi().setMovingType()` |
| updateClient() | ❌ Not available | ✅ `npc.updateClient()` |

## ScriptNpc — Direct Methods (No Sub-Objects)

In 1.7.x, **all methods are called directly on the `npc` object**. There are no
sub-objects like `getStats()`, `getAi()`, `getDisplay()`.

### Identity & Display

| Method | Returns | Description |
|---|---|---|
| `getName()` / `setName(String)` | String / void | NPC name |
| `getTitle()` / `setTitle(String)` | String / void | NPC title |
| `getTexture()` / `setTexture(String)` | String / void | NPC texture |
| `getSize()` / `setSize(int)` | int / void | Size (1-30, default 5) |
| `getVisibleType()` / `setVisibleType(int)` | int / void | 0=visible, 1=invisible, 2=semi-visible |
| `getShowName()` / `setShowName(int)` | int / void | 0=visible, 1=invisible, 2=when-attacking |
| `getShowBossBar()` / `setShowBossBar(int)` | int / void | 0=invisible, 1=visible, 2=when-attacking |
| `setAnimation(int)` | void | Animation (see AnimationType constants) |
| `setRotation(float)` | void | Rotation (0-360) |

### Scale

| Method | Description |
|---|---|
| `setHeadScale(float x, float y, float z)` | Head scale |
| `setBodyScale(float x, float y, float z)` | Body scale |
| `setArmsScale(float x, float y, float z)` | Arms scale |
| `setLegsScale(float x, float y, float z)` | Legs scale |

### Home Position

| Method | Returns | Description |
|---|---|---|
| `getHomeX()` / `getHomeY()` / `getHomeZ()` | int | Home position |
| `setHomeX(int)` / `setHomeY(int)` / `setHomeZ(int)` | void | Set home position |
| `setHome(int x, int y, int z)` | void | Set home position |
| `getReturnToHome()` / `setReturnToHome(boolean)` | boolean / void | Return-to-home behavior |

### Combat — Melee

| Method | Returns | Description |
|---|---|---|
| `getMeleeStrength()` / `setMeleeStrength(int)` | int / void | Melee attack strength |
| `getMeleeSpeed()` / `setMeleeSpeed(int)` | int / void | Melee attack speed |
| `getMeleeResistance()` / `setMeleeResistance(float)` | float / void | Melee resistance (0-2, default 1) |

### Combat — Ranged

| Method | Returns | Description |
|---|---|---|
| `getRangedStrength()` / `setRangedStrength(int)` | int / void | Ranged attack strength |
| `getRangedSpeed()` / `setRangedSpeed(int)` | int / void | Ranged attack speed |
| `getRangedBurst()` / `setRangedBurst(int)` | int / void | Ranged burst count |
| `getArrowResistance()` / `setArrowResistance(float)` | float / void | Arrow resistance (0-2, default 1) |

### Combat — Resistances & Regen

| Method | Returns | Description |
|---|---|---|
| `getExplosionResistance()` / `setExplosionResistance(float)` | float / void | Explosion resistance (0-2) |
| `getKnockbackResistance()` / `setKnockbackResistance(float)` | float / void | Knockback resistance (0-2, default 1) |
| `setRetaliateType(int)` | void | 0=normal, 1=panic, 2=retreat, 3=nothing |
| `getCombatRegen()` / `setCombatRegen(int)` | int / void | Combat health regen per second |
| `getHealthRegen()` / `setHealthRegen(int)` | int / void | Non-combat health regen per second |
| `setMaxHealth(int)` | void | Set max health |

### Inventory (Direct on ScriptNpc)

| Method | Returns | Description |
|---|---|---|
| `getRightItem()` / `setRightItem(ScriptItemStack)` | ScriptItemStack / void | Right hand item |
| `getLefttItem()` / `setLeftItem(ScriptItemStack)` | ScriptItemStack / void | Left hand item (note: typo in API) |
| `getProjectileItem()` / `setProjectileItem(ScriptItemStack)` | ScriptItemStack / void | Projectile item |
| `getArmor(int slot)` / `setArmor(int slot, ScriptItemStack)` | ScriptItemStack / void | Armor (0=head, 1=body, 2=legs, 3=boots) |

### Faction & Role/Job

| Method | Returns | Description |
|---|---|---|
| `getFaction()` / `setFaction(int id)` | ScriptFaction / void | NPC faction |
| `getRole()` | ScriptRoleInterface | NPC role |
| `getJob()` | ScriptJobInterface | NPC job |

### Actions

| Method | Returns | Description |
|---|---|---|
| `say(String)` | void | NPC says message to all |
| `say(ScriptPlayer, String)` | void | NPC says message to specific player |
| `kill()` | void | Kill NPC (doesn't despawn) |
| `reset()` | void | Reset NPC (triggers Init script) |
| `executeCommand(String)` | void | Execute server command |
| `giveItem(ScriptPlayer, ScriptItemStack)` | void | Give item to player |
| `shootItem(ScriptLivingBase, ScriptItemStack, int accuracy)` | void | Shoot item at target |

### Inherited from ScriptEntity (all entities)

| Method | Returns | Description |
|---|---|---|
| `getX()` / `getY()` / `getZ()` | double | Position |
| `setPosition(double, double, double)` | void | Set position |
| `getBlockX()` / `getBlockY()` / `getBlockZ()` | int | Block position |
| `isAlive()` | boolean | Is entity alive |
| `despawn()` | void | Remove entity permanently |
| `getRotation()` | float | Current rotation |
| `getRider()` / `setRider(ScriptEntity)` | ScriptEntity / void | Rider management |
| `getMount()` / `setMount(ScriptEntity)` | ScriptEntity / void | Mount management |
| `dropItem(ScriptItemStack)` | void | Drop item |
| `inWater()` / `inLava()` / `inFire()` | boolean | Environment checks |
| `isBurning()` / `setBurning(int)` / `extinguish()` | — | Fire management |
| `knockback(int power, float direction)` | void | Apply knockback |
| `isSneaking()` / `isSprinting()` | boolean | Movement state |
| `getMCEntity()` | Entity | Raw MC entity (expert only) |

### Inherited from ScriptLivingBase

| Method | Returns | Description |
|---|---|---|
| `getHealth()` / `setHealth(float)` | float / void | Health management |
| `getMaxHealth()` | float | Max health |
| `getHeldItem()` / `setHeldItem(ScriptItemStack)` | ScriptItemStack / void | Held item |
| `addPotionEffect(int, int, int, boolean)` | void | Add potion effect |
| `clearPotionEffects()` | void | Clear all effects |
| `swingHand()` | void | Swing hand animation |
| `canSeeEntity(ScriptEntity)` | boolean | Line of sight check |
| `getAttackTarget()` / `setAttackTarget(ScriptLivingBase)` | ScriptLivingBase / void | Attack target |
| `isAttacking()` | boolean | Is currently attacking |

### Inherited from ScriptLiving (Navigation)

| Method | Returns | Description |
|---|---|---|
| `navigateTo(double x, double y, double z, double speed)` | void | Pathfind to location (0.7 = default speed) |
| `clearNavigation()` | void | Stop navigating |
| `isNavigating()` | boolean | Is currently navigating |

## ScriptPlayer Methods (1.7.x)

Class hierarchy: `ScriptEntity → ScriptLivingBase → ScriptPlayer`
(Note: ScriptPlayer does NOT extend ScriptLiving — no navigation methods.)

### Player Identity

| Method | Returns | Description |
|---|---|---|
| `getName()` | String | Player name |
| `getDisplayName()` | String | Display name (may include formatting) |

### Quest Management

| Method | Returns | Description |
|---|---|---|
| `hasFinishedQuest(int id)` | boolean | Quest completed? |
| `hasActiveQuest(int id)` | boolean | Quest active? |
| `hasReadDialog(int id)` | boolean | Dialog read? |
| `startQuest(int id)` | void | Add quest to active list |
| `finishQuest(int id)` | void | Add quest to finished list |
| `stopQuest(int id)` | void | Remove from active list |
| `removeQuest(int id)` | void | Remove from active and finished |

### Faction

| Method | Returns | Description |
|---|---|---|
| `addFactionPoints(int faction, int points)` | void | Add/remove faction points (negative to decrease) |
| `getFactionPoints(int faction)` | int | Get faction points |

### Inventory

| Method | Returns | Description |
|---|---|---|
| `getInventory()` | ScriptItemStack[] | Get inventory (size 36) |
| `inventoryItemCount(ScriptItemStack)` | int | Count specific items |
| `giveItem(ScriptItemStack, int amount)` | boolean | Give item |
| `giveItem(String id, int damage, int amount)` | boolean | Give item by name |
| `removeItem(ScriptItemStack, int amount)` | boolean | Remove items |
| `removeItem(String id, int damage, int amount)` | boolean | Remove items by name |
| `removeAllItems(ScriptItemStack)` | void | Remove all of specific item |

### Game Mode & Experience

| Method | Returns | Description |
|---|---|---|
| `getMode()` / `setMode(int)` | int / void | 0=Survival, 1=Creative, 2=Adventure |
| `getExpLevel()` / `setExpLevel(int)` | int / void | Experience level |

### Spawn & Communication

| Method | Description |
|---|---|
| `setSpawnpoint(int x, int y, int z)` | Set spawn point |
| `resetSpawnpoint()` | Reset spawn to default |
| `sendMessage(String)` | Send chat message |

### Permissions

| Method | Returns | Description |
|---|---|---|
| `hasAchievement(String)` | boolean | Check achievement |
| `hasBukkitPermission(String)` | boolean | Check Bukkit/Cauldron permission |

### Inherited from ScriptEntity (on ScriptPlayer)

| Method | Returns | Description |
|---|---|---|
| `getX()` / `getY()` / `getZ()` | double | Position |
| `setPosition(double, double, double)` | void | Teleport player |
| `getBlockX()` / `getBlockY()` / `getBlockZ()` | int | Block position |
| `isAlive()` | boolean | Is entity alive |
| `getRotation()` | float | Current rotation |
| `getTempData(key)` / `setTempData(key, value)` | Object / void | Temp data |
| `hasTempData(key)` / `removeTempData(key)` | boolean / void | Temp data management |
| `clearTempData()` | void | Clear all temp data |
| `getStoredData(key)` / `setStoredData(key, value)` | Object / void | Stored data |
| `hasStoredData(key)` / `removeStoredData(key)` | boolean / void | Stored data management |
| `clearStoredData()` | void | Clear all stored data |
| `inWater()` / `inLava()` / `inFire()` | boolean | Environment checks |
| `isBurning()` / `setBurning(int)` / `extinguish()` | — | Fire management |

### Inherited from ScriptLivingBase (on ScriptPlayer)

| Method | Returns | Description |
|---|---|---|
| `getHealth()` / `setHealth(float)` | float / void | Health management |
| `getMaxHealth()` | float | Max health |
| `getHeldItem()` / `setHeldItem(ScriptItemStack)` | ScriptItemStack / void | Held item |
| `addPotionEffect(int, int, int, boolean)` | void | Add potion effect |
| `clearPotionEffects()` | void | Clear all effects |
| `swingHand()` | void | Swing hand animation |
| `canSeeEntity(ScriptEntity)` | boolean | Line of sight check |

## ScriptWorld Methods (1.7.x)

| Method | Returns | Description |
|---|---|---|
| `getPlayer(String name)` | ScriptPlayer | Get online player by name |
| `getAllServerPlayers()` | ScriptPlayer[] | Get all online players |
| `createItem(String id, int damage, int amount)` | ScriptItemStack | Create item |
| `getBlock(int x, int y, int z)` | ScriptItemStack | Get block at position |
| `setBlock(int x, int y, int z, ScriptItemStack)` | void | Set block |
| `removeBlock(int x, int y, int z)` | void | Remove block |
| `getSignText(int x, int y, int z)` | String | Read sign text |
| `getTime()` / `setTime(long)` | long / void | World time |
| `getTotalTime()` | long | Total world time |
| `isDay()` | boolean | Is daytime |
| `isRaining()` / `setRaining(boolean)` | boolean / void | Rain control |
| `thunderStrike(double x, double y, double z)` | void | Lightning strike |
| `explode(double x, double y, double z, float range, boolean fire, boolean grief)` | void | Create explosion |
| `spawnParticle(...)` | void | Spawn particles |
| `spawnClone(int x, int y, int z, int tab, String name)` | ScriptEntity | Spawn cloned entity |
| `getScoreboard()` | ScriptScoreboard | Get scoreboard |
| `getBiomeName(int x, int z)` | String | Get biome name |
| `getMCWorld()` | World | Raw MC world (expert only) |

## Role/Job Type Identification (1.7.x)

### RoleType Constants

| Constant | Value | Description |
|---|---|---|
| `RoleType.UNKNOWN` | 0 | No role |
| `RoleType.MAILMAN` | 1 | Mailman |
| `RoleType.TRADER` | 2 | Trader |
| `RoleType.FOLLOWER` | 3 | Follower |
| `RoleType.BANK` | 4 | Bank |
| `RoleType.TRANSPORTER` | 5 | Transporter |

### JobType Constants

| Constant | Value | Description |
|---|---|---|
| `JobType.UNKNOWN` | 0 | No job |
| `JobType.BARD` | 1 | Bard |
| `JobType.HEALER` | 2 | Healer |
| `JobType.GUARD` | 3 | Guard |
| `JobType.FOLLOWER` | 4 | Follower (job) |
| `JobType.ITEMGIVER` | 5 | Item Giver |
| `JobType.SPAWNER` | 6 | Spawner |
| `JobType.CONVERSATION` | 7 | Conversation |
| `JobType.PUPPET` | 8 | Puppet |

### Role Implementations

| Class | Key Methods |
|---|---|
| `ScriptRoleFollower` | `setOwner(ScriptPlayer)`, `getOwner()`, `hasOwner()`, `getDaysLeft()`, `addDaysLeft(int)`, `getInfiniteDays()`, `setInfiniteDays(boolean)` |
| `ScriptRoleTrader` | `setSellOption(slot, currency, sold)`, `removeSellOption(slot)`, `setMarket(name)`, `getMarket()` |
| `ScriptRoleMailman` | *(no additional scripting methods)* |
| `ScriptRoleBank` | *(no additional scripting methods)* |
| `ScriptRoleTransporter` | *(no additional scripting methods)* |

### EntityType Constants

| Constant | Value | Description |
|---|---|---|
| `EntityType.UNKNOWN` | 0 | Unknown |
| `EntityType.PLAYER` | 1 | Player |
| `EntityType.NPC` | 2 | Custom NPC |
| `EntityType.MONSTER` | 3 | Monster |
| `EntityType.ANIMAL` | 4 | Animal |
| `EntityType.LIVING` | 5 | Living entity |

### AnimationType Constants

| Constant | Value |
|---|---|
| `AnimationType.NORMAL` | 0 |
| `AnimationType.SITTING` | 1 |
| `AnimationType.LYING` | 2 |
| `AnimationType.HUGGING` | 3 |
| `AnimationType.SNEAKING` | 4 |
| `AnimationType.DANCING` | 5 |

## Global API Access (1.7.x)

In standard 1.7.x, there is **no `NpcAPI` class** and **no `event.API` property**.
The package is `noppes.npcs.scripted`, not `noppes.npcs.api`.

Code is placed in **sub-script slots** and runs top-to-bottom via `eval()`.
Variables `event`, `world`, `npc`, and event-dependent extras (`player`, `dialog`,
`target`, `entity`) are **injected directly into scope** — NOT accessed via function
parameters.

```
// 运行 (Init) sub-slot:
npc.say("Hello world! I am " + npc.getName());
var player = world.getPlayer("Steve");
if (player != null) {
    npc.say("Steve is online!");
}

// 对话 1 (Interact) sub-slot:
npc.say("Hello " + player.getName() + "!");
if (world.isDay()) {
    npc.say("It's daytime!");
}
```

**Do NOT wrap code in function definitions.** There are no `function init(e) {}` or
`function interact(event, world, npc, player) {}` — just bare code in each sub-slot.

## Critical Gotchas

1. **No sub-objects** — `npc.getMeleeStrength()`, NOT `npc.getStats().getMeleeStrength()`
2. **Eval-based, not function-based** — Code runs top-to-bottom in each sub-slot, NOT inside function definitions
3. **Booleans don't store** — Use `0`/`1` instead of `true`/`false`
4. **No NBT access** — Cannot read/write raw NBT on standard 1.7.10
5. **No updateClient()** — Changes may require `reset()` or happen automatically
6. **No world.broadcast()** — Use commands or iterate players for broadcasts
7. **ScriptWorld.getBlock() returns ScriptItemStack** — different from 1.8+ which returns ScriptBlockState

---

**Note:** This document does not guarantee that all available methods are listed.
For a complete and up-to-date reference, always fetch the JavaDoc for the user's
specific version. Some methods may be missing, deprecated, or version-specific.
