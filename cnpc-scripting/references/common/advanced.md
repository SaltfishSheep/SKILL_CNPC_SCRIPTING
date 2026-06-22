# Advanced Features — Nashorn Java Interop & Native MC Access

CNPC scripts can reach beyond the standard API into Nashorn's Java bridge and even
raw Minecraft internals. These are power tools — use them deliberately, not by default.

## Nashorn Java Interop

Nashorn provides unique JavaScript-to-Java bridging capabilities.
These are essential for CNPC scripting because all mod APIs are Java objects.

**Nashorn availability:** Nashorn was removed from the JDK in Java 15 (JEP 372). However,
Forge includes Nashorn as a bundled dependency, so no separate installation is needed for
standard Forge-based setups. For maximum cross-version compatibility, always write ES5
JavaScript even if GraalJS or other modern engines are available — ES5 ensures scripts
work identically across all CNPC versions and Java runtimes.

### Importing Java classes — Java.type()

```javascript
var ArrayList = Java.type("java.util.ArrayList");
var list = new ArrayList();
list.add("item");
```

Use `Java.type("fully.qualified.ClassName")` to import any Java class available on the
server's classpath. This is how you access Java standard library classes and Minecraft
internal classes alike.

### Extending/implementing Java types — Java.extend()

```javascript
var MyRunnable = Java.extend(Java.type("java.lang.Runnable"), {
    run: function() {
        print("Hello from Java thread!");
    }
});
var instance = new MyRunnable();
```

### Calling super methods — Java.super()

```javascript
// When overriding a Java class via Java.extend(), call the parent implementation
Java.super(instance).someMethod();
```

### Type conversion — Java.to() and Java.from()

- `Java.to(obj, JavaType)` — converts a JS value to a specific Java type (e.g., force `int` vs `double`)
- `Java.from(javaCollection)` — converts a Java Collection/array into a native JS array

```javascript
var javaList = someMethod(); // returns java.util.List
var jsArray = Java.from(javaList);
jsArray.forEach(function(item) { print(item); });
```

### SAM (Single Abstract Method) auto-conversion

Nashorn automatically converts JavaScript functions to Java SAM interface instances.
No manual wrapping needed:

```javascript
var ArrayList = Java.type("java.util.ArrayList");
var list = new ArrayList();
list.add("a");
list.add("b");
// JS function auto-converted to java.util.function.Consumer
list.forEach(function(item) {
    print(item);
});
```

This works for any Java interface with a single abstract method: `Runnable`, `Consumer`,
`Predicate`, `Comparator`, etc. It does NOT work for classes with multiple abstract methods —
use `Java.extend()` for those.

### JavaBean property access

Java objects' getter/setter methods can be accessed as properties directly:

```javascript
// Instead of:   player.setHealth(player.getHealth() + 10);
// You can write: player.health = player.health + 10;
```

This works for any pair `getXxx()` / `setXxx(y)` → transparent `.xxx` property.
Boolean `isXxx()` also works as `.xxx`. Use this idiom to keep scripts concise.

### When to use which

| Scenario | Tool |
|---|---|
| Use a Java class directly | `Java.type()` |
| Implement an interface or extend a class | `Java.extend()` |
| Handle a single-method callback | Just pass a JS function (SAM auto-convert) |
| Convert Java collection to JS array | `Java.from()` |
| Force a specific Java type | `Java.to()` |
| Read/write Java object properties | Transparent getter/setter access |

## Native Minecraft Access via getMC*() — Use with Caution

> **Available in all versions (1.7.x, 1.8+, 1.18+)** but the specific methods and
> returned types differ.

CNPC API objects (INpc, IPlayer, IWorld, IEntity, IItemStack, etc.) are wrappers around
native Minecraft classes. Many of them expose **getMC*()** methods — any method whose name
starts with `getMC` — that strip the CNPC wrapper and return the raw Minecraft object
underneath. Common examples:

| CNPC wrapper (1.8+) | CNPC wrapper (1.7.x) | 1.7.x / 1.12-1.16 | 1.18+ |
|---|---|---|---|
| `IEntity` / `ICustomNpc` | `ScriptEntity` / `ScriptNpc` | `getMCEntity()` → `net.minecraft.entity.Entity` | `getMCEntity()` → `net.minecraft.world.entity.Entity` |
| `IPlayer` | `ScriptPlayer` | `getMCEntity()` → `net.minecraft.entity.player.EntityPlayer` | `getMCEntity()` → `net.minecraft.world.entity.player.Player` |
| `IWorld` | `ScriptWorld` | `getMCWorld()` → `net.minecraft.world.World` | `getMCLevel()` → `net.minecraft.world.level.Level` |
| `IItemStack` | `ScriptItemStack` | `getMCItemStack()` → `net.minecraft.item.ItemStack` | `getMCItemStack()` → `net.minecraft.world.item.ItemStack` |

**Note:** `IPlayer` does NOT have a separate `getMCPlayer()` method — players are entities
and use `getMCEntity()` like any other entity. IWorld's method changed between 1.16 and 1.18
due to Minecraft's internal refactoring (World → Level). Class paths also changed in 1.17+
(entity classes moved to `net.minecraft.world.entity`).

**This is an escape hatch, not the default path.** Only consider it when:
- The existing CNPC API genuinely cannot achieve the goal
- The user explicitly requests low-level MC access

### Required: warn and confirm

Before writing any script that uses `getMC*()` or obfuscated MC names:

1. **Verify the CNPC API is truly insufficient** — exhaust standard API options first.
2. Explain to the user: native MC access requires obfuscated field/method names which
   vary by version and are difficult to verify. This approach is inherently fragile.
3. Ask the user to confirm they want to proceed, explicitly stating: *"使用重混淆名
   的 MC 原生方法难以保证正确性，可能需要非常多轮的调试才能正常工作。确定要尝试吗？"*
4. Only proceed after explicit user confirmation. If the user hesitates, suggest
   alternative approaches (CNPC API workarounds, community scripts, simpler solutions).

### Obfuscated names — read mappings.md only when necessary

In a production Minecraft environment, all vanilla class methods and fields use
**obfuscated names** (e.g., `func_70032_d`), not the human-readable MCP names
(e.g., `onUpdate`). Code from other Minecraft mods or tutorials uses MCP names
and will **not work** as-is — it can only serve as reference for logic and structure.

Obfuscated names vary across versions — a name that works on 1.12.2 will likely
**not** work on 1.16.5 or 1.20.1.

**⚠️ Only read [mappings.md](mappings.md) when you actually need to look up obfuscated
names.** The mapping lookup process is complex, involves multiple external data sources,
and is rarely needed — the CNPC wrapper API covers most use cases. Native MC access
via `getMC*()` has poor version compatibility and should be a last resort.

## Java Reflection for Private Fields and Methods

When native MC objects are needed but the target field or method is **private**, use
Java reflection via Nashorn's Java interop. For private members, you **must** call
`setAccessible(true)` before accessing them.

### Accessing a private field

```javascript
var entity = npc.getMCEntity();
// Get java.lang.Class via .getClass()
var clazz = entity.getClass();
var field = clazz.getDeclaredField("field_70177_z");  // obfuscated name
field.setAccessible(true);  // required for private fields
var value = field.get(entity);
```

### Calling a private method

```javascript
var method = clazz.getDeclaredMethod("func_70032_d", Java.type("int"));
method.setAccessible(true);  // required for private methods
var result = method.invoke(entity, 42);
```

### Getting Class objects without an instance

```javascript
// Import a class for static-level reflection
var EntityClass = Java.type("net.minecraft.entity.Entity");

// Access a private static field (null = static field, no instance needed)
// Replace "SOME_STATIC_FIELD" with the obfuscated name you need
var someField = EntityClass.class.getDeclaredField("SOME_STATIC_FIELD");
var value = someField.get(null);

// Also works for methods
var registerMethod = EntityClass.class.getDeclaredMethod("somePrivateStaticMethod");
registerMethod.invoke(null, arg1, arg2);
```

Pass `null` as the first argument to `get()` / `invoke()` when working with static members.

**Key points:**
- Always call `setAccessible(true)` on `Field` / `Method` objects before accessing private members.
- Use **obfuscated names** for field/method names (same rules as above).
- `getDeclaredField()` / `getDeclaredMethod()` includes private members; `getField()` /
  `getMethod()` only returns public ones.
- This is a last-resort technique. Prefer CNPC API methods first, then `getMC*()` for
  public members, then reflection only when neither suffices.
