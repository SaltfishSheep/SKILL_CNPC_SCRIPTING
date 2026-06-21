# 1.7.x Scripting Reference

> **CustomNPC+ Users:** This file does NOT apply to you. Route to `references/cur/scripting.md`.

This file is the **complete, self-contained reference** for standard 1.7.10 CNPC scripting
(output, setup, quirks, common patterns). For advanced features (Java interop via `Java.type()`,
native MC access via `getMC*()`, Java reflection), 1.7 users may also read `references/common/advanced.md`
(version-neutral).

## Event System

1.7.x uses **hardcoded sub-script slots**, not function-name dispatch. For complete event
system documentation, see `references/old/events.md`.

**Quick overview:**
- **Only NPC events** — no Player, Block, Item, or other script types
- **No function name mapping** — each event is hardcoded to a specific sub-script box
- **Full-script eval** — the entire script is `eval()`'d each time
- Variables are injected as **separate scope variables** (NOT fields of `event`)

## Local Snapshot of API

Some commonly used APIs have already been documented in the reference files. They can be used for quick reference, but whenever possible, it's best to get the results from the web. The reference files are `references/old/npc-objects.md`.

## Quick fetch API online

The full path of some classes is recorded in this reference file, and you can use it to directly access the APIs you need without repeatedly searching for their locations. The reference file is `references/old/javadoc.md`

## Storage Usage

CustomNPCs scripts have some common storage solutions; see the referenced file `references/old/storage.md` for details.

## First-Time Setup

**Always remind new 1.7.x users of these setup steps:**

1. **Enable the script:** The script editor has an "开启" (Enable) toggle — it defaults
   to "否" (No). Remind the user: *"在脚本框页面，将'开启'选项调为'是'，否则脚本不会运行。"*

2. **Nashorn.jar:** Copy `nashorn.jar` from the Java installation
   (`jre/lib/ext/nashorn.jar` or `jdk/jre/lib/ext/nashorn.jar`) into the `mods/` folder.

3. **Language setting:** In the script editor, set "语言 (Language)" to "ECMAScript".

## 1.7.10 Specific Quirks

### getHeldItem()

1.7.x uses `getHeldItem()` for the NPC's held item (1.8+ uses `getMainhandItem()`).
Always null-check:

```javascript
var item = npc.getHeldItem();
if (item) {
    // use item
}
```

### Potion Crash

Applying a potion effect to a dying entity can trigger a `ConcurrentModificationException`
crash. Guard with death checks before applying effects.

### No NBT Access

Standard 1.7.x **cannot** use `getNbt()` or `getEntityNbt()`. Only CustomNPC+
provides NBT support on 1.7.

## Simple Examples

All 1.7.x scripts are placed in sub-slots, not function definitions. **Injected variables
are standalone** (e.g., `player`, `world`, `dialog`, `entity`, `target`), not fields of `event`.

### Interaction (Interact sub-slot, 对话第一个槽位)

```javascript
npc.say("Hello, traveler!");
player.sendMessage("Welcome!");
```

### Damage handling (Damage sub-slot, 伤害)

```javascript
if (event.getDamage() > 5) {
    npc.say("That hurt! Damage: " + event.getDamage());
}
if (event.getDamage() > 100) {
    event.setCancelled(true);  // cancel the damage (double 'l')
}
```
