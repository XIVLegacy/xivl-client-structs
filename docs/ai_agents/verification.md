# Verification

`.github/workflows/checks.yml` is the authoritative list of CI-covered checks,
and CI runs them on every pull request and push to `main`.

## External-evidence checks

CI cannot inspect a contributor's retail client, capture corpus, or Ghidra
project. For a direct RTTI pass against the client executable, run:

```powershell
python -m tools.extractors.client_pe --exe C:\path\to\ffxivgame.exe --rtti
```

The expected result is `ffxiv_1.0_rtti.txt`. Addresses, slot counts, and type
descriptors are research leads that must be confirmed against the retained
Ghidra evidence before promotion.

For a capture-backed bridge change, run:

```powershell
python tools\validate_pcap_bridge.py --captures-dir C:\path\to\captures
```

Exit 0 validates the bridge against that explicit corpus without rewriting the
tracked sidecar. Record the exact client, capture, or Ghidra artifact for every
external-evidence result.

## Claim limits

A green CI run demonstrates repository consistency. It does not prove behavior
against a live client, capture session, or an unprovided Ghidra project. Do not
claim external validation unless that track ran and its artifact and result are
recorded.
