# Advanced Features — Nashorn Java Interop & Native MC Access

CNPC scripts can reach beyond the standard API into Nashorn's Java bridge and even
raw Minecraft internals. These are power tools — use them deliberately, not by default.

## Nashorn Java Interop

Nashorn provides unique JavaScript-to-Java bridging capabilities.
These are essential for CNPC scripting because all mod APIs are Java objects.

### Java Interop Methods

| Method | Purpose |
|---|---|
| `Java.type("fully.qualified.ClassName")` | Import any Java class available on the server's classpath |
| `Java.extend(JavaType, {method: function})` | Extend/implement a Java class or interface |
| `Java.super(instance)` | Call parent implementation when overriding a Java class |
| `Java.to(obj, JavaType)` | Convert JS value to specific Java type (e.g., force `int` vs `double`) |
| `Java.from(javaCollection)` | Convert Java Collection/array into native JS array |

### SAM (Single Abstract Method) auto-conversion

Nashorn automatically converts JavaScript functions to Java functional interface, 
like: `Runnable`, `Consumer`, `Predicate`, `Comparator`, etc. It does NOT work for classes with
multiple abstract methods — use `Java.extend()` for those.

```javascript
// Example
var thread = new java.lang.Thread(function(){print("test")});
```

### JavaBean property access

Java objects' getter/setter methods can be accessed as properties directly:
`player.setHealth(x)` → `player.health = x`, `player.getHealth()` → `player.health`.
Boolean `isXxx()` also works as `.xxx`. Use this idiom to keep scripts concise.

## Native Minecraft Access via getMC*() — Use with Caution

> **Available in all versions (old convention, cur convention, 1.18+)** but the specific methods and
> returned types differ.

CNPC API objects (INpc, IPlayer, IWorld, IEntity, IItemStack, etc.) are wrappers around
native Minecraft classes. Many of them expose **getMC*()** methods — any method whose name
starts with `getMC` — that strip the CNPC wrapper and return the raw Minecraft object
underneath. Common examples:

| CNPC wrapper (cur convention) | CNPC wrapper (old convention) | old convention / 1.12-1.16 | 1.18+ |
|---|---|---|---|
| `IEntity` | `ScriptEntity` | `getMCEntity()` | `getMCEntity()` |
| `IWorld` | `ScriptWorld` | `getMCWorld()` | `getMCLevel()` |
| `IItemStack` | `ScriptItemStack` | `getMCItemStack()` | `getMCItemStack()` |

**Note:** `IPlayer` does NOT have a separate `getMCPlayer()` method — players are entities
and use `getMCEntity()` like any other entity. IWorld's method changed between 1.16 and 1.18
due to Minecraft's internal refactoring (World → Level). Class paths also changed in 1.17+.

### Required: warn and confirm

Before writing any script that uses `getMC*()` or reobfuscated MC names:

1. **Verify the CNPC API is truly insufficient** — in order to maintain the cross-version compatibility, 
    exhaust standard API options first.
2. Only proceed after explicit user confirmation. If the user hesitates, suggest
    alternative approaches (CNPC API workarounds, community scripts, simpler solutions).

### Reobfuscated names — use native-mc-access_search MCP tool

In a production Minecraft environment, all native minecraft class methods and fields use
**reobfuscated names** (e.g., `func_70032_d`, `m_77764_`), which also called **SRG name**, 
not the human-readable deobfuscated name (e.g., `onUpdate`), which also called MCP name. 
Code from other Minecraft mods or tutorials uses MCP names will **not work** as-is,
it can only serve as reference for logic and structure.

Reobfuscated names vary across versions — a name that works on 1.12.2 will likely
**not** work on 1.16.5 or 1.20.1.

**Use the `native-mc-access_search` MCP tool to look up reobfuscated names.** The CNPC
wrapper API covers most use cases. Native MC access via `getMC*()` has poor version
compatibility and should be a last resort.

## Java Reflection for Private Fields and Methods

When native MC objects are needed but the target field or method is **private**, use
Java reflection via Nashorn's Java interop. For private members, you **must** call
`setAccessible(true)` before accessing them.

This is a last-resort technique. Prefer CNPC API methods first, then `getMC*()` for
public members, then reflection only when neither suffices.
