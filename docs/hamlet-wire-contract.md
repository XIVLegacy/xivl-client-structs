# Hamlet ranking and score payloads

Clientbound `0x01a6` replaces the area master's ranking collection, while
`0x01a8` replaces a player's score cache. The widgets retrieve those caches
through native getters. The receive handlers do not directly open widgets.
The [native manifest](../manifests/hamlet_wire_contract.json) owns field
offsets, source identities, instruction locators and Lua joins.

The ranking constructor copies 1520 bytes: twenty 76-byte records. Records
whose first dword is zero are skipped. The inspected getters and widget join
the remaining fields to points, player name, Grand Company icon selector,
optional linkshell name and icon input. The widget displays its row index as
rank; this does not establish a server tie-breaking rule.

The score constructor copies 264 bytes. Its first dword supplies an additive
value, followed by a correction byte, 128 category selectors and 128 factors.
The first zero selector ends iteration. Native lookup tables map each
selector to a category and signed base points; a positive factor multiplies
those points. The totals getter applies the signed correction byte and adds
the first wire dword. The UI labels that additive value as clear-time points,
without establishing a time unit or server scoring rule.

`_getHamletDefenseScoreAll` returns five totals and then destroys the score
cache. Consumers must account for this read consuming state. Neither opcode
is observed in the retained capture corpus, so the copy extents are native
requirements rather than captured packet lengths. Server ranking, bonus,
reward and valid-input policies remain unresolved.
