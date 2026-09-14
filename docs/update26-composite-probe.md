# 0.26 Composite currency test — separate laboratory package

This is a standalone optional test package over0.26 Sandbox. Enable it alone in a fresh test game, **not alongside0.26**. It contains no adaptive plating, containment study or production chain, and is not the friends-playtest package.

The official [March2025 update](https://www.sinsofasolarempire2.com/article/535214/march-2025-total-subjugation-update) documents dynamically sized UI support for up to eight custom exotic types. The earlier concern about a fixed five-resource UI is therefore superseded by documented support. Actual integration still needs the following engine checks; none has been observed by the agent.

1. Open Military → Engineering and research **LAB TEST: receive one Composite** (one credit, one second). Confirm a distinct **ProtoTech Composite** balance of1 without changing any ordinary exotic balance.
2. Save, reload, and confirm1 remains. Research is one-time; it must not award another unit on reload.
3. On a capital or titan with an empty defense slot, purchase **LAB TEST: spend one Composite**. It costs one credit and one Composite and has no combat benefit. Check balance0.
4. On a second eligible ship with an empty slot, attempt the same purchase. It must fail for insufficient Composite. Record the fitting/shop time separately from the one-second base item time.
5. Check item cancellation/refund and dismantling behavior. In a controlled two-player test, compare each owner's balances and simultaneous purchases; save/reload during a purchase.

Source definitions use the native exotic registry, research windfall and item exotic price. No existing resource is renamed, no custom script grants stock, and no refinery/survey/NPC/start-mode route produces it. Existing weapon, hull and shieldless definitions are unchanged.

Passing this currency test is only the first Stage5 acceptance gate. Interruptible paid study, facility ownership/loss, one study per player, item-bound shield permissions, out-of-combat regeneration and equip/refill prevention still need separate implementation and runtime tests before a production plating item can join the regular package.
