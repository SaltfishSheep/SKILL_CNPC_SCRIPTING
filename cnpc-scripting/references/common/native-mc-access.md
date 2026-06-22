# Minecraft Native MC Access — Mapping Lookup

> **⚠️ This file is for advanced use only.** Most scripts should use the CNPC wrapper API
> (INpc, IPlayer, IWorld, IEntity, etc.) and never need obfuscated names.
>
> **Only read this file when:**
> 1. You have confirmed the CNPC API is truly insufficient
> 2. The user has explicitly agreed to use native MC access
> 3. You actually need to look up an obfuscated name for a specific version
>
> This file is large and the lookup process is complex. Do not read it preemptively.

When scripts use `getMC*()` or Java reflection to access Minecraft internals, you need
to convert between human-readable names and obfuscated runtime names.

**Do NOT embed mapping data in scripts or this skill.** Use the provided tools to search
mappings at runtime.

---

## Workflow

### Step 1: Search mapping cache

Use `mapping_search.py` to look up obfuscated names:

```bash
python mapping_search.py <mc_version> <expression> [page]
```

**Arguments:**
- `mc_version` — Minecraft version (e.g., `1.12.2`, `1.20.1`)
- `expression` — Boolean search expression (see syntax below)
- `page` — Page number starting from 1 (default: 1, 10 results per page)

**Search expression syntax:**
- `term` — Single word, case-insensitive substring match
- `a&b` — AND: both a and b must match
- `a|b` — OR: either a or b must match
- `(expr)` — Grouping
- `&` has higher precedence than `|`

**Examples:**
```bash
python mapping_search.py 1.12.2 Entity
python mapping_search.py 1.12.2 "Entity&moveEntity"
python mapping_search.py 1.20.1 "Entity|Player"
python mapping_search.py 1.12.2 "func_70091_d"
```

### Step 2: Handle missing cache

If `mapping_search.py` returns:
```
Mapping cache does not exist or invalid.
```

Then build the cache using `mapping_builder.py` with `--force`:

```bash
python mapping_builder.py --force <mc_version>
```

After the cache is built, retry the search from Step 1.

---

## Obfuscated name prefixes

| Prefix | System | Example | Versions |
|---|---|---|---|
| `func_` | SRG method | `func_70091_d_` | 1.7.10 – 1.16.5 |
| `field_` | SRG field | `field_70159_w_` | 1.7.10 – 1.16.5 |
| `p_` / `p_i` | SRG parameter | `p_70091_1_` | 1.7.10 – 1.16.5 |
| `m_` | SRG method (TSRGv2) | `m_91087_` | 1.17+ |
| `f_` | SRG field (TSRGv2) | `f_12345_` | 1.17+ |
| `p_` | SRG parameter (TSRGv2) | `p_12345_0_` | 1.17+ |
| No prefix, short | Notch/ProGuard | `a`, `b`, `aqk` | All versions |

---

## Access modifier note

No mapping file provides access modifiers (public/protected/private/default).
The authoritative source is the compiled bytecode, which is not practical to pre-extract.

**Scripts should attempt direct invocation first; if an `IllegalAccessError` is thrown,
fall back to reflection** (`setAccessible(true)`).

---

## License

### Mojang mappings

Mojang's mapping files are provided under a custom license:
> "You may copy and use the mappings for development purposes, but you may not
> redistribute the mappings complete and unmodified."

**This skill does NOT redistribute mapping data.** It only provides tools to fetch
and search mappings at runtime.

Full license: https://account.mojang.com/documents/minecraft_eula

### MCP mappings

MCP mappings are maintained by the community (Mod Coder Pack project).
They are distributed via Forge's Maven repository and the MCP-Archive GitHub repository.
