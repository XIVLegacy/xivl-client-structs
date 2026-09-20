# Retail repair contract

The canonical machine-readable record is
[`../manifests/repair_contract.json`](../manifests/repair_contract.json). It
joins the pinned 1.23b client scripts and native event transport to the retained
retail repair capture without treating emulator behavior as evidence.

## Bahamut decision

The client proves the NPC dialog and self-repair entry shape, while the retail
capture proves six accepted NPC repairs quoted at one gil. It does not prove a
numeric NPC result condition. Bahamut can implement the confirmation flow,
client-compatible item metadata checks, generic event cleanup, and a clearly
bounded one-gil tariff choice. NPC durability mutation must remain gated until
another authoritative source establishes the result.

Self-repair resolves package/slot to an item and enters ordinary CraftCommand
22013 through the generic ready-command path. The first-party manual says a
successful self-repair restores 100 percent condition and consumes the proper
dark matter, but no retained execution proves the runtime payload, consumption,
failure, or result transaction. Those server-side effects remain provisional.

Do not reuse `getRepairAmount` as the NPC price. Its 100 through 500 level bands
belong to player-to-player repair commission UI and conflict with the six
captured one-gil NPC prompts.

## Exact remaining observation

Closing the runtime gate requires an authoritative trace that attributes target
item condition before and after an accepted NPC repair. Self-repair additionally
requires a command/event trace linking item identity, material decrement, result
condition, rejection behavior, and cleanup. The retained 1.23b corpus contains
neither observation.
