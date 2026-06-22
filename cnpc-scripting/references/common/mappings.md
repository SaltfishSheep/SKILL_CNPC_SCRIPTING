# Minecraft Mapping Lookup — Deobfuscation Name Resolution

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
to convert between human-readable names and obfuscated runtime names. This file documents
the external data sources, acquisition workflow, and lookup methods.

**Do NOT embed mapping data in scripts or this skill.** Fetch it at runtime from the
sources below. See [License](#license) for details.

---

## Version routing

| Version range | Mapping system | Primary source |
|---|---|---|
| 1.7.10 – 1.16.5 | MCP (SRG + human names) | TSRG + CSV (merged) |
| 1.17+ | SRG intermediate + Mojang official | TSRG + ProGuard (merged) |

**Critical:** A method name that works on 1.12.2 will likely **not** work on 1.16.5
or 1.20.1. Always verify the obfuscated name for the user's specific version.

---

## Unified cache schema

All version-specific workflows produce the same CSV format at
`./mapping-caches/<mc-version>.csv`. The query logic is version-agnostic.

### CSV columns (8 columns, fixed order)

```
obf_class,deobf_class,type,obf_name,deobf_name,srg_name,desc,is_static
```

| # | Column | Description | 1.7.10–1.16.5 source | 1.17+ source |
|---|---|---|---|---|
| 1 | `obf_class` | Obfuscated class name | TSRG | TSRGv2 / ProGuard |
| 2 | `deobf_class` | Deobfuscated class path | TSRG (= Mojang path) | ProGuard (= Official path) |
| 3 | `type` | `field` or `method` | Inferred (has descriptor → method) | Inferred (has `(` in descriptor → method) |
| 4 | `obf_name` | Obfuscated member name | TSRG | TSRGv2 / ProGuard |
| 5 | `deobf_name` | Deobfuscated member name | CSV (`name`) = MCP name | ProGuard = Mojang name |
| 6 | `srg_name` | SRG member name | CSV (`searge`) | TSRGv2 |
| 7 | `desc` | Java type descriptor | TSRG (methods only) | TSRGv2 / ProGuard |
| 8 | `is_static` | Static member flag | TSRG `static_methods.txt` | TSRGv2 (`static` sub-line) |

**Descriptor rules:**
- Methods: full method descriptor, e.g. `(DDD)V`, `(Ljava/lang/Object;)Z`
- Fields: field type descriptor, e.g. `Ljava/lang/String;`, `I`, `F`
- 1.7.10–1.16.5: TSRGv1 does not include field descriptors or field SRG names;
  field `desc` is left empty; field `srg_name` comes from CSV `searge` column
  (TSRGv1 field entries only provide `obf_class`, `obf_name`, `deobf_name`)

**`is_static` rules:**
- 1.7.10–1.16.5: check if SRG name (trailing `_` stripped) exists in `static_methods.txt` → `true`, else `false`
- 1.17+: TSRGv2 entries may have a `static` sub-indented line → `true`, else `false`
- ProGuard does not provide this info (but TSRGv2 does for 1.17+)

**Access modifier note:** No mapping file provides access modifiers (public/protected/
private/default). The authoritative source is the compiled bytecode, which is not
practical to pre-extract. **Scripts should attempt direct invocation first; if an
`IllegalAccessError` is thrown, fall back to reflection** (`setAccessible(true)`).

### Example rows

**CSV escaping note:** All 8 columns must be present in every row. When a column is empty
(e.g. `desc` for fields, or `is_static` when unknown), use consecutive commas to preserve
column positions. Field descriptors are unavailable in TSRGv1 (1.7.10–1.16.5).

1.12.2:
```csv
aab,net/minecraft/entity/Entity,method,a,moveEntity,func_70091_d_,(DDD)V,
aab,net/minecraft/entity/Entity,field,a,motionX,field_70159_w,,
btn,net/minecraft/client/gui/widget/button/Button,method,<init>,<init>,<init>,(IIILjava/lang/String;)V,
bms,net/minecraft/util/Timer,method,<init>,<init>,<init>,(F)V,
```

1.20.1:
```csv
box$b,net/minecraft/world/entity/Entity,field,a,health,f_19847_,I,
box$b,net/minecraft/world/entity/Entity,method,<init>,<init>,<init>,(Ljava/util/UUID;Lboy;I)V,
box$b,net/minecraft/world/entity/Entity,method,a,tick,m_26235_,()I,
box$b,net/minecraft/world/entity/Entity,method,a,method_262811,m_262811_,(Lcom/mojang/serialization/codecs/RecordCodecBuilder$Instance;)Lcom/mojang/datafixers/kinds/App;,true
```

### Query pseudocode

```
cache_file = "./mapping-caches/" + mc_version + ".csv"
if cache_file exists:
    table = read_csv(cache_file)
else:
    table = build_merged_table(mc_version)  // version-specific workflow
    write_csv(cache_file, table)

// All queries below work regardless of version:
results = table.filter(row => row.deobf_class == target_class)
results = table.filter(row => row.srg_name == target_srg)
results = table.filter(row => row.deobf_name == target_name)
results = table.filter(row => row.obf_class == target_obf_class)
```

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

## Data acquisition workflow (1.7.10 – 1.16.5)

For 1.7.10 – 1.16.5, the model must download two ZIP files, extract them, and merge
their contents into a single lookup table. This is a **mandatory three-step process**:
download → extract → merge. Do NOT search raw TSRG or CSV files separately.

### Step 1: Download ZIPs

Download both ZIP files for the target MC version:

```
# TSRG file (class context + SRG names)
https://maven.minecraftforge.net/de/oceanlabs/mcp/mcp_config/<mc_version>/mcp_config-<mc_version>.zip

# CSV file (SRG ↔ MCP human-readable names)
# First, find the latest snapshot date from the version index:
https://raw.githubusercontent.com/Aizistral-Studios/MCP-Archive/master/versions.json
# Then download:
https://maven.minecraftforge.net/de/oceanlabs/mcp/mcp_snapshot/<date>-<mc_version>/mcp_snapshot-<date>-<mc_version>.zip
```

### Step 2: Extract files

From the TSRG ZIP, extract:
```
config/joined.tsrg
config/static_methods.txt
config/constructors
```

From the CSV ZIP, extract:
```
fields.csv
methods.csv
params.csv    (optional, for parameter names)
```

### Step 3: Merge into unified lookup table

**This is the core step.** The TSRG file contains class context (which class each member
belongs to) but uses SRG names. The CSV files contain human-readable MCP names but lack
class context. Merge them to create a single lookup table with all information.

#### TSRG format

```
<obf_class> <mojang_class_path>
    <obf_field> <mojang_field_name>
    <obf_method> <descriptor> <srg_method_name>
```

Parsing rules:
- Unindented line → class mapping: `<obf> <mojang_path>`
- Indented line with `(` → method: `<obf> <descriptor> <srg_name>`
- Indented line without `(` → field: `<obf> <mojang_name>`

Example (1.12.2):
```
a net/minecraft/util/text/TextFormatting
    a BLACK
    b DARK_BLUE
    a (I)La; func_175744_a
```

Example (1.16.5):
```
a net/minecraft/util/math/vector/Matrix3f
    a field_226097_a_
    a ()V func_226110_a_
```

#### CSV format

```csv
searge,name,side,desc
field_70159_w,motionX,0,The velocity of the entity in the X axis.
func_70091_d,moveEntity,0,Moves the entity based on the given parameters.
```

Columns:
- `searge` — SRG name (stable across builds)
- `name` — Human-readable MCP name
- `side` — 0=client, 1=server, 2=both
- `desc` — Human-readable description (NOT used in unified schema)

#### static_methods.txt format

One SRG method name per line. These are the methods marked as `static` in the source.

```
func_100015_a
func_110121_a
func_110304_a
func_110311_f
func_110537_b
```

**Matching note:** TSRG names may have a trailing `_` (e.g. `func_70091_d_`) while
`static_methods.txt` may not (e.g. `func_70091_d`). Strip trailing `_` before comparing.

#### constructors format

One constructor per line. Format: `<srg_id> <class_path> <descriptor>`

```
1005 net/minecraft/client/Minecraft$3 (Lnet/minecraft/client/Minecraft;)V
1015 net/minecraft/client/gui/widget/button/Button (IIILjava/lang/String;)V
1018 net/minecraft/util/Timer (F)V
```

These are constructor methods that need to be added to the merged table as `<init>` entries.
The `class_path` can be matched against TSRG's second column to get `obf_class`.

#### Merge logic

1. Parse TSRG file into two maps:
   - Methods: `srg_name → { deobf_class, obf_class, obf_name, descriptor }`
   - Fields: `(obf_class, mojang_name) → { obf_class, obf_name }` (TSRGv1 fields have no SRG name)
2. Parse `static_methods.txt` into a set of SRG names (strip trailing `_` when matching against CSV `searge`)
3. Parse `constructors` file — each line is `<srg_id> <class_path> <descriptor>`:
   - Create a method entry: `obf_name = <init>`, `deobf_name = <init>`, `srg_name = <init>`
   - Look up `obf_class` from TSRG by `class_path`
   - `is_static = false`, `type = method`
4. For each row in CSV:
   - If row has a `searge` starting with `func_` → method: look up in method map by `srg_name`
   - If row has a `searge` starting with `field_` → field: look up in field map by `(obf_class_from_csv, name)`
     (match TSRG's mojang field name against CSV's `name` column)
5. If found, attach class context to the CSV row
6. If not found (TSRG may not cover all entries), keep the CSV row without class context
7. Map to unified columns:
   - `obf_class` ← TSRG `obf_class`
   - `deobf_class` ← TSRG `mojang_class_path`
   - `type` ← `method` if entry has descriptor, else `field`
   - `obf_name` ← TSRG `obf_name`
   - `deobf_name` ← CSV `name`
   - `srg_name` ← CSV `searge` (for methods from TSRG map; for fields directly from CSV)
   - `desc` ← TSRG descriptor (methods only; empty for TSRGv1 fields)
   - `is_static` ← `true` if `srg_name` (with trailing `_` stripped) is in `static_methods.txt` set, else `false`

**Cache the merged table to `./mapping-caches/<mc-version>.csv`.** On subsequent lookups
for the same version, read the cached CSV directly — skip the download/extract/merge steps.
Only rebuild the cache when the file does not exist or the user requests a refresh.

---

## Data acquisition workflow (1.17+)

For 1.17+, MCP CSV no longer exists (MCP was abandoned). However, **MCPConfig's
`joined.tsrg` still exists and contains SRG intermediate names** (`m_####_`, `f_####_`).
Combine TSRG (for SRG names + class context) with Mojang ProGuard (for human-readable
Mojang names) to build a complete lookup table.

### Step 1: Download files

```
# TSRG file (class context + SRG names) — same MCPConfig source as older versions
https://maven.minecraftforge.net/de/oceanlabs/mcp/mcp_config/<mc_version>/mcp_config-<mc_version>.zip

# ProGuard file (Mojang human-readable names)
# 1. GET https://piston-meta.mojang.com/mc/game/version_manifest_v2.json
#    → Find entry for target version, extract its "url" field
# 2. GET <version_url>
#    → Extract downloads.client_mappings.url
# 3. GET <client_mappings_url>
```

### Step 2: Extract files

From the TSRG ZIP, extract:
```
config/joined.tsrg
```

The ProGuard file is a plain text file (no ZIP wrapping).

### Step 3: Merge into unified lookup table

The TSRG provides SRG names + class context. ProGuard provides Mojang names.
**The bridge between them is the obfuscated class name** (first column in TSRGv2,
`-> <ObfName>` in ProGuard).

#### TSRGv2 format (1.17+)

```
<obf_class> <srg_class_path> <srg_class_id>
    <obf_member> <srg_name> <srg_id>
    <obf_member> <descriptor> <srg_name> <srg_id>
        static
        <param_index> o <param_srg_name> <param_srg_id>
```

**Critical difference from TSRGv1:** The second column is an **SRG intermediate class
path** (`net/minecraft/src/C_746_$C_749_`), NOT a Mojang class path. The common key
between TSRGv2 and ProGuard is the **obfuscated class name** (first column).

Parsing rules:
- Unindented line → class: `<obf_class> <srg_class_path> <srg_class_id>`
- Indented line without `(` → field: `<obf> <srg_name> <srg_id>`
- Indented line with `(` → method: `<obf> <descriptor> <srg_name> <srg_id>`
- `<clinit>` and `<init>` are special: their "SRG name" is the literal name, not an `m_`/`f_` prefix
- Sub-indented `static` → member is static (`is_static = true`)
- Sub-indented `<index> o <srg> <id>` → method parameter (not a field entry)

Example (1.20.1):
```
box$b net/minecraft/src/C_746_$C_749_ 749
    a f_262739_ 262739
    b f_262751_ 262751
    c f_26228_ 26228
    <init> (Ljava/util/UUID;Lboy;I)V <init> 26231
        0 o f_26228_ 26232
        1 o f_26229_ 26233
        2 o f_26230_ 26234
    a ()I m_26235_ 26235
    b ()Ljava/util/UUID; f_26228_ 262854
    equals (Ljava/lang/Object;)Z equals 262822
        0 o p_263014_ 263014
    hashCode ()I hashCode 262850
```

**Note:** In TSRGv2, some method entries have `f_` names — these are getter/setter methods
whose SRG name reuses the field's SRG name. They are still methods (have descriptors).

#### ProGuard format

```
# Class mapping
net.minecraft.world.entity.Entity -> afh:
# Method mapping (indented)
    42:42:void tick() -> a
    43:43:double getX() -> b
# Field mapping (indented)
    int health -> aB
    float speed -> aC
```

Parsing rules:
- Unindented line ending with `:` → class: `<MojangName> -> <ObfName>:`
- Indented line with `()` → method: `[line:]returnType name(params) -> obfName`
- Indented line without `()` → field: `type name -> obfName`

#### Merge logic

1. Parse TSRGv2 into entries: `{ obf_class, obf_name, descriptor, srg_name, type, is_static }`
2. Parse ProGuard into entries: `{ deobf_class (Mojang), obf_class, obf_name, deobf_name, descriptor, type }`
3. **Join on `(obf_class, obf_name, type)`** to combine SRG names from TSRGv2 with Mojang names from ProGuard
4. Use ProGuard's `deobf_class` as the canonical Mojang class path
5. If a TSRGv2 entry has no ProGuard match, keep it with empty `deobf_name` and `deobf_class`
6. Map to unified columns:
   - `obf_class` ← TSRGv2 / ProGuard (bridge key)
   - `deobf_class` ← ProGuard Mojang class path
   - `type` ← `method` or `field`
   - `obf_name` ← TSRGv2 / ProGuard (bridge key)
   - `deobf_name` ← ProGuard Mojang name
   - `srg_name` ← TSRGv2 SRG name
   - `desc` ← TSRGv2 descriptor
   - `is_static` ← `true` if TSRGv2 has `static` sub-line, else `false`

**Cache the merged table to `./mapping-caches/<mc-version>.csv`.** On subsequent lookups
for the same version, read the cached CSV directly — skip the download/extract/merge steps.
Only rebuild the cache when the file does not exist or the user requests a refresh.

---

## Search capabilities

All versions produce the same unified CSV schema. The query steps are identical regardless
of MC version — only the column values differ (SRG prefix style, human-readable name origin).

### Unified search table

| You have | Search column(s) | Return |
|---|---|---|
| Deobfuscated class path (`net/minecraft/entity/Entity`) | `deobf_class` | All members of that class |
| SRG name (`func_70091_d_` or `m_26235_`) | `srg_name` | Deobf name + class + obf name |
| Deobfuscated name (`moveEntity` or `tick`) | `deobf_name` | SRG name + class + obf name |
| Obfuscated class name (`aab` or `box$b`) | `obf_class` | Class path + all members |
| Obfuscated member name (`a`) | `obf_name` (within class) | SRG + deobf name |

---

## Quick reference: MCP version availability

MCP mappings exist for these MC versions (from MCP-Archive versions.json):

| MC version | Stable | Example snapshot |
|---|---|---|
| 1.7.10 | 8–12 | 20140925 |
| 1.8 – 1.8.9 | 15–20 | 20151128 |
| 1.9 – 1.9.4 | 24–26 | 20160516 |
| 1.10.2 | 29 | 20161117 |
| 1.11 – 1.11.2 | 31, 32 | 20170612 |
| 1.12 – 1.12.2 | 39–47 | 20180814 |
| 1.13 – 1.13.2 | 41–47 | 20190530 |
| 1.14 – 1.14.4 | 49–58 | 20200119 |
| 1.15 – 1.15.1 | 60 | 20211108 |
| 1.16.1 – 1.16.5 | 2021… | — |

**After 1.16.5, MCP is abandoned.** Forge switched to Mojang official mappings.

### MCPConfig TSRG availability (all versions)

MCPConfig `joined.tsrg` is available for **all Forge-supported versions**, including 1.17+.
Verified on NeoForged Maven (`maven.neoforged.net/releases/de/oceanlabs/mcp/mcp_config/`):

| MC version | Format | SRG prefix |
|---|---|---|
| 1.7.10 – 1.16.5 | TSRGv1 | `func_` / `field_` |
| 1.17 – 1.21.5+ | TSRGv2 | `m_` / `f_` |

---

## License

### Mojang mappings

Mojang's mapping files are provided under a custom license:
> "You may copy and use the mappings for development purposes, but you may not
> redistribute the mappings complete and unmodified."

**This skill does NOT redistribute mapping data.** It only provides URLs and format
instructions for users to fetch mappings themselves at runtime.

Full license: https://account.mojang.com/documents/minecraft_eula

### MCP mappings

MCP mappings are maintained by the community (Mod Coder Pack project).
They are distributed via Forge's Maven repository and the MCP-Archive GitHub repository.
