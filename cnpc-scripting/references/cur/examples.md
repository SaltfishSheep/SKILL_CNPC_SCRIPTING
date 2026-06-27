**Use npc-object:**

```javascript
function init(e) {
    var stats = npc.getStats();
    stats.setMaxHealth(200);
    stats.setMeleeStrength(15);
    npc.getAi().setMovingType(1);  // 1 = wandering
    npc.getDisplay().setName("Elite Guard");
}
```

**Test role type example:**

```javascript
function interact(e) {
    var roleType = npc.getRole().getType();
    // Compare against version-specific constants from EnumRoleType
    if (roleType === 4) {  // 4 = Transporter on some versions
        e.player.message("This NPC is a transporter!");
    }
}
```

**spawnNPC example:**

```javascript
function interact(e) {
    if (e.player.getStoreddata().get("hasPet")) {
        return;  // already has a pet
    }
    var wolf = NpcAPI.Instance().spawnNPC(e.player.getWorld(), 
        e.player.getX(), e.player.getY(), e.player.getZ());
    wolf.getDisplay().setName(e.player.getName() + "'s Wolf");
    wolf.getDisplay().setModel("minecraft:wolf");
    wolf.getAi().setMovingType(3);  // following
    e.player.getStoreddata().put("hasPet", 1);
}
```