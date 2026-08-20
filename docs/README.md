# XIVLegacy Client Structs documentation

These pages explain the consumer contract and contribution policy for the
evidence-backed FFXIV 1.23b client-structure catalog. Machine-readable
inventories and their regeneration rules live under `manifests/`.

## Policy

- [AI-assisted contributions](ai_agents/README.md) - contribution and
  documentation policy.
- [Evidence and claims](ai_agents/evidence-and-claims.md) -
  evidence classes, confidence, citations, and claim boundaries.
- [Comments and prose](ai_agents/comments-and-prose.md) -
  deletion default and comment doctrine.
- [Verification](ai_agents/verification.md) - external-evidence checks and
  limits on what CI proves.
- [Retail-input validation](ai_agents/retail-input-validation.md) - bounded
  private-input workflow, credential boundary, and sanitized attestation.

## Consumer guides

- [Client architecture](client-architecture.md) - curated catalog of
  stable model-level findings about the 1.23b client (wire dispatch,
  Lua-bridge, LGE/LuaControl class substrate, Sqwt UI).
- [Client-structure IR](ir-schema.md) - reads the generated client-structure IR
  and the schemas that validate it.
- [Naming](naming.md) - naming rules for known/unknown structs and
  fields, the address convention, and the Receiver-vs-Packet naming pairing.
- [Lua Game Engine (LGE) class system](lua-class-system.md) - full unpack of the
  LGE class system (5 Lua metatables, registration pipeline, write chokepoint).

## Related contracts

- [Manifest contract](../manifests/README.md) - manifest families,
  generated products, and regeneration entry points.
- [Tooling](../tools/README.md) - local validation and research
  commands.
