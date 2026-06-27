**getHeldItem() example:**

```javascript
var item = npc.getHeldItem();
if (item) {
    // use item
}
```

**Simple damage check and cancel:**

```javascript
if (event.getDamage() > 5) {
    npc.say("That hurt! Damage: " + event.getDamage());
}
if (event.getDamage() > 100) {
    event.setCancelled(true);  // cancel the damage (double 'l')
}
```
