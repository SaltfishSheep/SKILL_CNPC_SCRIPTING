# NPC Object Model & Global API Access

## NPC Object Model

ICustomNpc has several chainable sub-objects. Understanding this hierarchy is essential
for discovering methods — the JavaDoc organizes methods by sub-interface, not flat on the
NPC object. The most common chain pattern is `npc.getXxx().doYyy()`.

### Key sub-objects

| Accessor | Returns | Purpose |
|---|---|---|
| `npc.getStats()` | INPCStats | Max health, melee/ranged strength, combat regen, resistances |
| `npc.getAi()` | INPCAi | Moving type, standing type, retaliation type, return-to-home |
| `npc.getDisplay()` | INPCDisplay | Name, skin, model, size, visibility, show name tag |
| `npc.getInventory()` | INPCInventory | Weapon, offhand, armor, projectile item, drop chances |
| `npc.getTimers()` | ITimers | Schedule repeating or one-shot timer events |
| `npc.getAdvanced()` | INPCAdvanced | Advanced settings (see JavaDoc per version) |
| `npc.getFaction()` | IFaction | Read faction ID, hostility settings |
| `npc.getRole()` | INPCRole | Read role info (use `getType()` to identify which role — see below) |
| `npc.getJob()` | INPCJob | Read job info (use `getType()` to identify which job — see below) |

**Example chain:**

```javascript
function init(e) {
    var stats = npc.getStats();
    stats.setMaxHealth(200);
    stats.setMeleeStrength(15);
    npc.getAi().setMovingType(1);  // 1 = wandering
    npc.getDisplay().setName("Elite Guard");
}
```

### Role and Job type identification

`getRole()` and `getJob()` return the interface type, but you cannot directly check
which specific role/job it is from the interface alone. Use `getType()` combined with
the version-specific constants to identify the concrete type.

The constants are defined in the API as static fields (e.g., `EnumRoleType.Trader`,
`EnumJobType.Guard`). Fetch the JavaDoc for `EnumRoleType` and `EnumJobType` to get
the exact numeric values for the user's version. Common roles include:
Trader, Follower, Bank, Transporter, Mailman. Common jobs include:
Bard, Conversation, Follower, Guard, Healer, ItemGiver, Puppet, Spawner.

```javascript
function interact(e) {
    var roleType = npc.getRole().getType();
    // Compare against version-specific constants from EnumRoleType
    if (roleType === 4) {  // 4 = Transporter on some versions
        e.player.message("This NPC is a transporter!");
    }
}
```

### Player object methods

The `IPlayer` object (from `e.player`) has many methods beyond `message`:

| Method | Purpose |
|---|---|
| `hasFinishedQuest(id)` / `hasActiveQuest(id)` | Check quest status |
| `startQuest(id)` / `finishQuest(id)` / `stopQuest(id)` / `removeQuest(id)` | Manage quests |
| `hasReadDialog(id)` | Check dialog read status |
| `addFactionPoints(faction, points)` / `getFactionPoints(faction)` | Faction system |
| `getMode()` / `setMode(type)` | Gamemode (0=Survival, 1=Creative, 2=Adventure) |
| `setPosition(x, y, z)` | Teleport player |
| `setSpawnpoint(x, y, z)` / `resetSpawnpoint()` | Spawn management |
| `giveItem(item)` | Give item to player |
| `getHeldItem()` / `getMainhandItem()` | Player's held item (version-dependent) |
| `getName()` / `getUUID()` | Player identity |

Always fetch the specific IPlayer JavaDoc page for the user's version — not all methods
exist in all versions.

### Updating NPCs after runtime changes

Changes made via the sub-objects (display, stats, ai) are normally synced to clients
every 10 ticks. To sync immediately, call `npc.updateClient()`. To fully reset and
re-trigger `init`, call `npc.reset()`.

## NpcAPI — Global API Access

Beyond the `npc` and `e.player` objects, CNPC provides a global singleton API for
world-level operations that don't belong to a specific NPC.

### Accessing NpcAPI

- **From event context:** `event.API` — available in any event handler that receives `e`
- **From anywhere:** `NpcAPI.Instance()` — the static singleton accessor

Both return the same NpcAPI object. `event.API` is more convenient when inside a
handler; `NpcAPI.Instance()` works from any scope (including utility scripts).

### Key NpcAPI methods

| Method | Purpose |
|---|---|
| `spawnNPC(world, x, y, z)` | Create and spawn a new NPC at coordinates |
| `createNPC(world)` | Create an NPC instance (does NOT spawn — use sparingly) |
| `getIEntity(entity)` | Wrap a raw MC entity into IEntity |
| `getIWorld(dimensionId)` | Get an IWorld by dimension ID |
| `getIWorlds()` | Get all loaded worlds |
| `createCustomGui(id, width, height, pauseGame)` | Create a custom GUI |
| `getFactions()` | Access faction handler |
| `getDialogs()` | Access dialog handler |
| `getClones()` | Access clone (stored NPC) handler |
| `IsAvailable()` | Check if CNPC API is loaded and ready |
| `events()` | Get the Forge EventBus (advanced — for registering custom event listeners) |
| `getRawPlayerData(uuid)` | Read raw NBT player data |
| `stringToNbt(str)` | Parse a JSON/NBT string into INbt |
| `getRandomName(dictionary, gender)` | Generate random NPC names |
| `executeCommand(world, command)` | Execute command via world context |

**spawnNPC example:**

```javascript
function interact(e) {
    if (e.player.getStoreddata().get("hasPet")) {
        return;  // already has a pet
    }
    var wolf = NpcAPI.Instance().spawnNPC(e.player.getWorld(), 
        e.player.getX(), e.player.getY(), e.player.getZ());
    wolf.getDisplay().setName(e.player.getName() + "'s Wolf");
    wolf.getDisplay().setModel("minecraft:wolf");
    wolf.getAi().setMovingType(3);  // following
    e.player.getStoreddata().put("hasPet", 1);
}
```

**Important:** NpcAPI should only be used server-side. The `createNPC(world)` method
creates the NPC but does not spawn it — you must call additional methods to place it
in the world. `spawnNPC(...)` handles both creation and spawning.

---

**Note:** This document does not guarantee that all available methods are listed.
For a complete and up-to-date reference, always fetch the JavaDoc for the user's
specific version. Some methods may be missing, deprecated, or version-specific.
