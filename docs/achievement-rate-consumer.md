# Achievement rate consumer

Clientbound `0x019f` stores its second and third dwords in an achievement
cache, then reports a numerator and denominator to Lua. The third wire dword
is not passed to Lua as progress flags. The
[native contract](../manifests/achievement_rate_consumer.json) records the
authenticated instruction and script evidence.

The receiver copies application `+0`, `+4` and `+8`. The native update uses
the first as the achievement key, caches the other two, and looks up a client
maximum. `_onReceiveAchievementRate` receives the key, the progress count
clamped to that maximum using a signed comparison, and the maximum itself.
The list widget calculates `floor(numerator*100/denominator)` and formats
the progress text. The detail widget stores the same numerator and denominator.

Completion queries use separate client state. This route establishes no
completed, new or in-progress bits in application `+8`. The closing dword
at `+0x0c` is not copied by the inspected receiver route and supplies no Lua
argument. Its server purpose, and the semantic meaning of the cached third
dword, remain unresolved.
