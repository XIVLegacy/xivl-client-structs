# Vendored evidence

Each subdirectory is a consumer-owned snapshot of promoted first-party
evidence. Its `PROVENANCE.json` records the source repository, source path,
source license and canonical license URL, evidence tier, transformation, and
sha256 for every file. The sha256 is the snapshot's identity. Vendoring does
not relicense the source material.

`tools/validate_vendor.py` is the drift gate. `tools/refresh_vendor.py` is the
only refresh path and requires an explicitly named source checkout; it has no
workspace-layout default. A missing or changed file fails validation rather
than silently falling back to another copy.
