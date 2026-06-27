# Data Storage — old convention

This file covers the old convention data storage mechanisms. For cur convention, see
`references/cur/storage.md` instead.

See examples in `references/old/examples-storage.md`

## tempdata — Short-lived, any type

- **Type support:** Any Object (strings, numbers, arrays, maps, etc.)
- **Scope:** Per-entity for NPCs/Players; shared across all worlds for ScriptWorld
- **Persistence:** NOT persistent — cleared on entity unload OR server restart
- **API:** `getTempData(key)`, `setTempData(key, value)`, `hasTempData(key)`, `removeTempData(key)`, `clearTempData()`

**World-level tempdata** (shared across all NPCs): see examples-storage.md

## storeddata — Long-lived, strings and numbers only

- **Type support:** Strings and numbers ONLY — other types are NOT stored
- **Scope:** Per-entity for NPCs/Players; global for ScriptWorld
- **Persistence:** Persists through world restart
- **API:** `getStoredData(key)`, `setStoredData(key, value)`, `hasStoredData(key)`, `removeStoredData(key)`, `clearStoredData()`

### ⚠️ storeddata is unreliable on standard 1.7.10

Known data loss issues have been reported by the community. Data may be lost in
various situations. For long-term persistence on standard 1.7.10, consider using
file I/O as an alternative. CustomNPC+ has fixed storeddata reliability.

**World-level storeddata** (global persistent storage): see examples-storage.md

## NBT Access

**NOT available on standard 1.7.10.**

The `getNbt()` / `getXXNbt()` methods that provide live read/write or snapshot
read-only NBT access are a cur convention feature. They do NOT exist in the standard 1.7.10 API.

On CustomNPC+ (1.7.10d+), some NBT access may be available through Java interop,
but this is not part of the standard scripting API.

## Storage Decision Guide (old convention)

| Need | Best choice |
|---|---|
| Temporary scratch data during one session | `tempdata` |
| Persist a number or string across restarts | `storeddata` (⚠️ unreliable on standard 1.7.10) |
| Persist a complex value | `tempdata` (will be lost on restart) |
| Boolean flags | Store as `0`/`1` in `storeddata` |
| Long-term persistence on standard 1.7.10 | Consider file I/O as alternative |
| Tag an item permanently | ❌ Not available (NBT is cur convention only) |
| Read entity/item NBT state | ❌ Not available (NBT is cur convention only) |

