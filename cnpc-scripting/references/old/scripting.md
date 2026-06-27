# old convention Scripting Reference

## Reference Files

| File | Purpose | When to read |
|---|---|---|
| `events.md` | Event→sub-slot mapping, injected fields, cancellation rules | When handling NPC events or debugging event-related issues |
| `storage.md` | Data persistence mechanisms (tempdata, storeddata, NBT limitations) | When scripts need to save/load data |
| `constants.md` | RoleType, JobType, EntityType, AnimationType constant values | When checking role/job/entity types or setting animations |
| `examples.md` | Code snippets for common scripting patterns | When writing new scripts or learning old convention syntax |
| `examples-storage.md` | Code snippets for storage operations | When implementing data persistence |

## Sub-slot mapping, Event System

**Full details in `references/old/events.md`** — event→sub-slot mapping, injected field table, cancellation.

## Global API Access (old convention)

In standard old convention, there is **no `NpcAPI` class** and **no `event.API` property**.
The package is `noppes.npcs.scripted`, not `noppes.npcs.api`.

Code is placed in **sub-script slots** and runs top-to-bottom via `eval()`.
Variables `event`, `world`, `npc`, and event-dependent extras (`player`, `dialog`,
`target`, `entity`) are **injected directly into scope** — NOT accessed via function
parameters.

**Do NOT wrap code in function definitions.** There are no `function init(e) {}` or
`function interact(event, world, npc, player) {}` — just bare code in each sub-slot.

## 1.7.10 Specific Quirks

### getHeldItem()

old convention uses `getHeldItem()` for the NPC's held item (cur convention uses `getMainhandItem()`).
Always null-check. See examples in `references/old/examples.md`.

### Potion Crash

Applying a potion effect to a dying entity can trigger a `ConcurrentModificationException`
crash. Guard with death checks before applying effects.

## Constants

See `references/old/constants.md` for RoleType, JobType, EntityType, and AnimationType constants.

## Critical Gotchas

1. **Eval-based, not function-based** — Code runs top-to-bottom in each sub-slot, NOT inside function definitions
2. **No updateClient()** — Changes may require `reset()` or happen automatically
3. **No world.broadcast()** — Use commands or iterate players for broadcasts

## Storage Usage

CustomNPCs scripts have some common storage solutions; see the referenced file `references/old/storage.md` for details.

## Examples

See `references/old/examples.md` for code examples.