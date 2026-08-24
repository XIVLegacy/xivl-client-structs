<#
.SYNOPSIS
    Runs and verifies the read-only named-string/address reference exporter.
#>
[CmdletBinding(DefaultParameterSetName = 'String')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Address')]
    [ValidateNotNullOrEmpty()][string[]]$Addresses,

    [Parameter(Mandatory, ParameterSetName = 'String')]
    [ValidateNotNullOrEmpty()][string[]]$Strings,

    [Parameter(ParameterSetName = 'String')]
    [ValidateSet('EXACT', 'SUBSTRING')][string]$StringMatch = 'EXACT',

    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$Out,
    [ValidateRange(1, 4096)][int]$MaxMatches = 4096,
    [ValidateRange(1, 100000)][int]$MaxReferences = 100000
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$output = [IO.Path]::GetFullPath($Out)
$parent = Split-Path $output -Parent
if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
    throw "Output parent directory does not exist: $parent"
}
if (Test-Path -LiteralPath $output) {
    throw "Output already exists: $output"
}

$scriptEnv = @{
    XIVL_REFERENCE_MAX_MATCHES = [string]$MaxMatches
    XIVL_REFERENCE_MAX_REFERENCES = [string]$MaxReferences
}
if ($PSCmdlet.ParameterSetName -eq 'Address') {
    $scriptEnv.XIVL_REFERENCE_MODE = 'ADDRESS'
    $scriptEnv.XIVL_REFERENCE_ADDRESSES = $Addresses -join ','
}
else {
    if ($Strings | Where-Object { $_ -match "`r|`n" }) {
        throw 'Each string query must be one line'
    }
    $scriptEnv.XIVL_REFERENCE_MODE = 'STRING'
    $scriptEnv.XIVL_REFERENCE_STRINGS = $Strings -join "`n"
    $scriptEnv.XIVL_STRING_MATCH = $StringMatch
}

& (Join-Path $PSScriptRoot 'run-headless.ps1') `
    -Script FindReferences.java -ReadOnly -Out $output `
    -ScriptEnv $scriptEnv -ScriptPath @((Join-Path $repoRoot 'ghidra'))
if ($LASTEXITCODE -ne 0) {
    throw "Headless reference export failed with exit $LASTEXITCODE"
}

& python (Join-Path $repoRoot 'tools\verify_reference_export.py') $output
if ($LASTEXITCODE -ne 0) {
    throw "Reference export verification failed with exit $LASTEXITCODE"
}
