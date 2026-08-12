$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$utf8 = [System.Text.UTF8Encoding]::new($false)
$jsonPaths = @(& git -C $repoRoot ls-files --cached --others --exclude-standard -- "*.json")
if ($LASTEXITCODE -ne 0)
{
    throw "git ls-files failed while enumerating repository JSON files."
}
$jsonFiles = @($jsonPaths | ForEach-Object { Get-Item -LiteralPath (Join-Path $repoRoot $_) })

foreach ($file in $jsonFiles)
{
    $null = [System.IO.File]::ReadAllText($file.FullName, $utf8) | ConvertFrom-Json
}

function Get-ArrayCount($value)
{
    if ($null -eq $value)
    {
        return 0
    }

    return @($value).Count
}

$structsPath = Join-Path $repoRoot (Join-Path "manifests" "structs.json")
if (Test-Path $structsPath)
{
    $structsManifest = [System.IO.File]::ReadAllText($structsPath, $utf8) | ConvertFrom-Json
    $structCount = Get-ArrayCount $structsManifest.structs

    if ($structsManifest.structCount -ne $structCount)
    {
        throw "Struct manifest count $($structsManifest.structCount) does not match structs array count $structCount."
    }
}

$symbolsPath = Join-Path $repoRoot (Join-Path "manifests" "symbols.json")
if (Test-Path $symbolsPath)
{
    $symbolsManifest = [System.IO.File]::ReadAllText($symbolsPath, $utf8) | ConvertFrom-Json
    $symbolCount = Get-ArrayCount $symbolsManifest.symbols

    if ($symbolsManifest.symbolCount -ne $symbolCount)
    {
        throw "Symbol manifest count $($symbolsManifest.symbolCount) does not match symbols array count $symbolCount."
    }
}

function Get-ObjectKeyCount($value)
{
    if ($null -eq $value)
    {
        return 0
    }
    return ($value.PSObject.Properties | Measure-Object).Count
}

$luaApiPath = Join-Path $repoRoot (Join-Path "manifests" "lua_api_index.json")
if (Test-Path $luaApiPath)
{
    $luaApi = [System.IO.File]::ReadAllText($luaApiPath, $utf8) | ConvertFrom-Json
    $apiCount = Get-ObjectKeyCount $luaApi.apis
    if ($luaApi.luaApiCount -ne $apiCount)
    {
        throw "lua_api_index luaApiCount $($luaApi.luaApiCount) does not match apis key count $apiCount."
    }
}

$receiverMapPath = Join-Path $repoRoot (Join-Path "manifests" "receiver_opcode_map_inbound.json")
if (Test-Path $receiverMapPath)
{
    $rmap = [System.IO.File]::ReadAllText($receiverMapPath, $utf8) | ConvertFrom-Json
    $inboundLen = Get-ArrayCount $rmap.inboundReceivers
    $internalLen = Get-ArrayCount $rmap.clientInternalReceivers
    $strongLen = Get-ArrayCount $rmap.strongCandidates
    $candidateLen = Get-ArrayCount $rmap.candidates
    if ($rmap.inboundConfirmedCount -ne $inboundLen)
    {
        throw "receiver_opcode_map_inbound inboundConfirmedCount $($rmap.inboundConfirmedCount) does not match inboundReceivers array count $inboundLen."
    }
    if ($rmap.clientInternalCount -ne $internalLen)
    {
        throw "receiver_opcode_map_inbound clientInternalCount $($rmap.clientInternalCount) does not match clientInternalReceivers array count $internalLen."
    }
    if ($rmap.strongCount -ne $strongLen)
    {
        throw "receiver_opcode_map_inbound strongCount $($rmap.strongCount) does not match strongCandidates array count $strongLen."
    }
    if ($rmap.candidateCount -ne $candidateLen)
    {
        throw "receiver_opcode_map_inbound candidateCount $($rmap.candidateCount) does not match candidates array count $candidateLen."
    }
}

$napiMapPath = Join-Path $repoRoot (Join-Path "manifests" "control_class_napi_map.json")
if (Test-Path $napiMapPath)
{
    $napi = [System.IO.File]::ReadAllText($napiMapPath, $utf8) | ConvertFrom-Json
    $classCount = Get-ObjectKeyCount $napi.classes
    if ($napi.totals.classCount -ne $classCount)
    {
        throw "control_class_napi_map totals.classCount $($napi.totals.classCount) does not match classes key count $classCount."
    }
}

Write-Host "Validated $($jsonFiles.Count) JSON files."

# Vendored files must match the sha256 declared in their PROVENANCE.json.
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python)
{
    throw "python not found on PATH; required for vendor provenance validation (validate_vendor.py)."
}
& $python.Source (Join-Path $PSScriptRoot "validate_vendor.py")
if ($LASTEXITCODE -ne 0)
{
    throw "Vendor provenance validation failed (validate_vendor.py exit $LASTEXITCODE)."
}
