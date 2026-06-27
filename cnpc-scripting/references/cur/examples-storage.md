**Use tempdata or storeddata:**

```javascript
function init(e) {
    var npc = e.npc;

    npc.tempdata.put("key", anyValue);
    var val = npc.tempdata.get("key");
    npc.tempdata.remove("key");

    npc.storeddata.put("key", "string_value");
    npc.storeddata.put("count", 42);
    var name = npc.storeddata.get("key");
}
```

**Use NBT in 1.16-:**

```javascript
function interact(e) {
    var nbt = e.player.mainhandItem.nbt;
    nbt.setString("customKey", "value");
    nbt.setInteger("score", 100);
    var val = nbt.getString("customKey");
}
```

**Use NBT in 1.18+:**

```javascript
function interact(e) {
    var nbt = e.player.mainhandItem.nbt;
    nbt.putString("customKey", "value");
    nbt.putInteger("score", 100);
    var val = nbt.getString("customKey");
}
```

**Get Serialized NBT:**

```javascript
var snapshot = npc.getEntityNbt();
var snapshot = item.getItemNbt();
```