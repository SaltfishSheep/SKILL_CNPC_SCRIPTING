# Data Storage — 1.7.x (Old)

This file covers the 1.7.x data storage mechanisms. For 1.8+ (cur), see
`references/cur/storage.md` instead.

## tempdata — Short-lived, any type

```
// 运行 (Init) sub-slot:
npc.setTempData("counter", 0);
npc.setTempData("playerList", []);      // Can store arrays
npc.setTempData("config", {greeting: "Hello"});  // Can store objects

// 对话 1 (Interact) sub-slot:
var counter = npc.getTempData("counter");
npc.setTempData("counter", counter + 1);
```

- **Type support:** Any Object (strings, numbers, arrays, maps, etc.)
- **Scope:** Per-entity for NPCs/Players; shared across all worlds for ScriptWorld
- **Persistence:** NOT persistent — cleared on entity unload OR server restart
- **API:** `getTempData(key)`, `setTempData(key, value)`, `hasTempData(key)`, `removeTempData(key)`, `clearTempData()`

**World-level tempdata** (shared across all NPCs):
```
// 运行 (Init) sub-slot:
world.setTempData("globalCounter", 0);
// All worlds share the same tempdata
```

## storeddata — Long-lived, strings and numbers only

```
// 运行 (Init) sub-slot:
npc.setStoredData("visitCount", 0);        // Number — OK
npc.setStoredData("lastVisitor", "Steve"); // String — OK
npc.setStoredData("enabled", true);        // BOOLEAN — WILL NOT BE STORED!

// 对话 1 (Interact) sub-slot:
var count = npc.getStoredData("visitCount");
npc.setStoredData("visitCount", count + 1);
npc.setStoredData("lastVisitor", player.getName());

// Booleans workaround: use 0/1
npc.setStoredData("enabled", 1); // Store as number instead
```

- **Type support:** Strings and numbers ONLY — other types are NOT stored
- **Scope:** Per-entity for NPCs/Players; global for ScriptWorld
- **Persistence:** Persists through world restart
- **API:** `getStoredData(key)`, `setStoredData(key, value)`, `hasStoredData(key)`, `removeStoredData(key)`, `clearStoredData()`

### ⚠️ storeddata is unreliable on standard 1.7.10

Known data loss issues have been reported by the community. Data may be lost in
various situations. For long-term persistence on standard 1.7.10, consider using
file I/O as an alternative. CustomNPC+ has fixed storeddata reliability.

**World-level storeddata** (global persistent storage):
```
// 运行 (Init) sub-slot:
world.setStoredData("globalQuestComplete", 0);
```

## NBT Access

**NOT available on standard 1.7.10.**

The `getNbt()` / `getXXNbt()` methods that provide live read/write or snapshot
read-only NBT access are a 1.8+ feature. They do NOT exist in the standard 1.7.10 API.

On CustomNPC+ (1.7.10d+), some NBT access may be available through Java interop,
but this is not part of the standard scripting API.

## Storage Decision Guide (1.7.x)

| Need | Best choice |
|---|---|
| Temporary scratch data during one session | `tempdata` |
| Persist a number or string across restarts | `storeddata` (⚠️ unreliable on standard 1.7.10) |
| Persist a complex value | `tempdata` (will be lost on restart) |
| Boolean flags | Store as `0`/`1` in `storeddata` |
| Long-term persistence on standard 1.7.10 | Consider file I/O as alternative |
| Tag an item permanently | ❌ Not available (NBT is 1.8+ only) |
| Read entity/item NBT state | ❌ Not available (NBT is 1.8+ only) |

