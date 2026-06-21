# Data Storage in CNPC Scripts

CNPC scripts have several mechanisms to store data. Choose the right one based on
persistence needs and data type.

## tempdata — Short-lived, any type

```javascript
npc.tempdata.put("key", anyValue);
var val = npc.tempdata.get("key");
npc.tempdata.remove("key");
```

- **Backed by:** Java HashMap — stores any JavaScript type (objects, arrays, functions, etc.)
- **Lifetime:** **Unstable.** Lost on chunk unload, world reload, server restart, or entity death.
- **Use for:** Caching, intermediate computation results, one-off flags during a single interaction.
- **Do NOT use for:** Anything that must survive a reload or death.
- **Available on:** NPCs, players, entities (IEntity), items (IItemStack), worlds (IWorld).
  World tempdata is shared across dimensions.

## storeddata — Long-lived, strings and numbers only

```javascript
npc.storeddata.put("key", "string_value");
npc.storeddata.put("count", 42);
var name = npc.storeddata.get("key");
```

- **Backed by:** Persistent key-value store that survives saves and reloads.
- **Type restriction:** **Strings and numbers only.** Booleans, objects, arrays, and `null`
  are not supported. You must **manually convert** booleans — store them explicitly as
  `"true"` / `"false"` (strings) or `1` / `0` (numbers). This is not automatic.
- **Lifetime:** Persists across world reloads, server restarts, and entity death.
  Storeddata is stable on all entity types.

- **Use for:** Quest progress, persistent flags, counters, player-specific settings.

## NBT — Two distinct access patterns

### getNbt() — Semi-persistent NBT Tag (read/write)

In version 1.18.2+, the setter named put. In version 1.16.5-, it named set.
Here's sample.

```javascript
// or: item.getNbt()
var nbt = npc.getNbt();

// In 1.18+
nbt.putString("customKey", "value");
nbt.putInteger("score", 100);
// In 1.16-
nbt.setString("customKey", "value");
nbt.setInteger("score", 100);

var val = nbt.getString("customKey");
```

- Returns the **live NBT tag compound** attached to the entity/item.
- **For items:** fully persistent, survives everything — this is the standard way to tag items.
- **For entities:** storeddata is the safer choice — always persistent. Entity NBT can
  be lost on death in some edge cases.
- **Write-capable** — changes persist back to the object.

### getXXNbt() — Temporary serialized snapshot (read-only)

```javascript
var snapshot = npc.getEntityNbt();
var snapshot = item.getItemNbt();
```

- Returns a **one-time serialized copy** of the object's full NBT data.
- **Read-only** — modifying the snapshot does nothing to the actual entity/item.
- **Transient** — the snapshot is not linked to the live object.
- **Use for:** inspecting current state, debugging, one-time data extraction.

## Storage decision guide

| Need | Best choice |
|---|---|
| Temporary scratch data during one session | `tempdata` |
| Persist a number or string across reloads | `storeddata` |
| Persist a complex value or boolean | Serialize to string → `storeddata` |
| Tag an item permanently | `item.getNbt()` |
| Persist entity data (non-item) | `storeddata` (safer than entity NBT) |
| Read entity/item state for inspection | `getEntityNbt()` / `getItemNbt()` |
| Boolean flags | Store as `"1"` / `"0"` in `storeddata` |
