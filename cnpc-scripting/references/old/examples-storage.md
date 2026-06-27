**Use tempdata:**

```javascript
// 运行 (Init) sub-slot:
npc.setTempData("counter", 0);
npc.setTempData("playerList", []);      // Can store arrays
npc.setTempData("config", {greeting: "Hello"});  // Can store objects

// 对话 1 (Interact) sub-slot:
var counter = npc.getTempData("counter");
npc.setTempData("counter", counter + 1);
```

**World-level tempdata (shared across all NPCs):**

```javascript
// 运行 (Init) sub-slot:
world.setTempData("globalCounter", 0);
// All worlds share the same tempdata
```

**Use storeddata:**

```javascript
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

**World-level storeddata (global persistent storage):**

```javascript
// 运行 (Init) sub-slot:
world.setStoredData("globalQuestComplete", 0);
```
