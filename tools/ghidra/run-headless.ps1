<#
.SYNOPSIS
    Runs a Ghidra headless post-script against the analyzed client project.

.DESCRIPTION
    Required environment:
      BCS_GHIDRA_HOME      Ghidra install root (contains support\analyzeHeadless.bat)
      BCS_GHIDRA_PROJECTS  Ghidra project directory
      BCS_GHIDRA_PROJECT   project name
      BCS_JAVA_HOME        JDK root
    Optional:
      BCS_GHIDRA_PROGRAM   program name within the project (default ffxivgame.exe)

    Read scripts should pass -ReadOnly so an unexpected write cannot be saved.
    The project lock is exclusive; a held GUI lock causes headless execution to fail.

.EXAMPLE
    tools\ghidra\run-headless.ps1 -Script DumpVAs.java -ReadOnly `
        -Out logs\c140.txt -ScriptEnv @{ XIVL_TARGET_VAS = '0x00891F00' }

.EXAMPLE
    tools\ghidra\run-headless.ps1 -Script ApplyProgramEdits.java `
        -ScriptEnv @{ BCS_EDITS = 'edits.tsv'; BCS_EDITS_REPORT = 'report.txt' }
#>
[CmdletBinding()]
param(
    # Post-script file name, resolved against -ScriptPath.
    [Parameter(Mandatory = $true)][string]$Script,

    # Directories searched for the post-script. Defaults to this script's folder.
    [string[]]$ScriptPath,

    # Environment variables handed to the post-script.
    [hashtable]$ScriptEnv = @{},

    # Convenience for the XIVL_DUMP_PATH convention most dump scripts use.
    [string]$Out,

    # Forbid saving program changes. Use for every read-only script.
    [switch]$ReadOnly,

    [switch]$Analyze,

    [string]$GhidraHome = $env:BCS_GHIDRA_HOME,
    [string]$ProjectDir = $env:BCS_GHIDRA_PROJECTS,
    [string]$ProjectName = $env:BCS_GHIDRA_PROJECT,
    [string]$Program = $env:BCS_GHIDRA_PROGRAM,
    [string]$JavaHome = $env:BCS_JAVA_HOME,
    [string]$MaxMem = '8G',

    # Headless log destination. Defaults to a temp file.
    [string]$LogPath
)

$ErrorActionPreference = 'Stop'

function Require-Value {
    param([string]$Value, [string]$EnvName, [string]$What)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "$What not set. Set `$env:$EnvName or pass the matching parameter."
    }
    return $Value
}

$GhidraHome  = Require-Value $GhidraHome  'BCS_GHIDRA_HOME'     'Ghidra install root'
$ProjectDir  = Require-Value $ProjectDir  'BCS_GHIDRA_PROJECTS' 'Ghidra project directory'
$ProjectName = Require-Value $ProjectName 'BCS_GHIDRA_PROJECT'  'Ghidra project name'
$JavaHome    = Require-Value $JavaHome    'BCS_JAVA_HOME'       'JDK root'
if ([string]::IsNullOrWhiteSpace($Program)) { $Program = 'ffxivgame.exe' }

$headless = Join-Path $GhidraHome 'support\analyzeHeadless.bat'
if (-not (Test-Path $headless)) { throw "analyzeHeadless.bat not found under $GhidraHome" }
if (-not (Test-Path $JavaHome))  { throw "JDK not found at $JavaHome" }
if (-not (Test-Path $ProjectDir)) { throw "project directory not found: $ProjectDir" }

if (-not $ScriptPath) { $ScriptPath = @($PSScriptRoot) }
$resolved = $null
foreach ($dir in $ScriptPath) {
    $candidate = Join-Path $dir $Script
    if (Test-Path $candidate) { $resolved = $candidate; break }
}
if (-not $resolved) { throw "post-script '$Script' not found in: $($ScriptPath -join '; ')" }

# Ghidra uses an exclusive project lock. Warn before headless reports the failure.
$lockFile = Join-Path $ProjectDir "$ProjectName.lock"
if ((Test-Path $lockFile) -and ((Get-Process javaw, java -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0)) {
    Write-Warning "$ProjectName appears locked by a running Ghidra instance. Close it if this run aborts."
}

if (-not $LogPath) { $LogPath = Join-Path ([System.IO.Path]::GetTempPath()) "bcs-headless-$PID.log" }
if ($Out) { $ScriptEnv['XIVL_DUMP_PATH'] = $Out }

$saved = @{}
$applied = @{
    'JAVA_HOME'              = $JavaHome
    'PATH'                   = (Join-Path $JavaHome 'bin') + ';' + $env:PATH
    'GHIDRA_HEADLESS_MAXMEM' = $MaxMem
    'GHIDRA_JAVA_OPTIONS'    = '-Dlog4j.skipJansi=true'
}
foreach ($k in $ScriptEnv.Keys) { $applied[$k] = [string]$ScriptEnv[$k] }

$headlessArgs = @($ProjectDir, $ProjectName, '-process', $Program)
if (-not $Analyze) { $headlessArgs += '-noanalysis' }
if ($ReadOnly)     { $headlessArgs += '-readOnly' }
$headlessArgs += @('-scriptPath', ($ScriptPath -join ';'), '-postScript', $Script)

try {
    foreach ($k in $applied.Keys) {
        $saved[$k] = [System.Environment]::GetEnvironmentVariable($k)
        Set-Item -Path "env:$k" -Value $applied[$k]
    }
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    & $headless @headlessArgs *> $LogPath
    $headlessExit = $LASTEXITCODE
    $timer.Stop()
    $elapsed = $timer.Elapsed
}
finally {
    foreach ($k in $saved.Keys) {
        if ($null -eq $saved[$k]) { Remove-Item -Path "env:$k" -ErrorAction SilentlyContinue }
        else { Set-Item -Path "env:$k" -Value $saved[$k] }
    }
}

$log = Get-Content $LogPath -Raw -ErrorAction SilentlyContinue
if ($null -eq $log) { $log = '' }

$status = 'OK'
if ($log -match 'LockException: Unable to lock project') {
    $status = 'LOCKED'
    Write-Error "Project '$ProjectName' is locked by another Ghidra instance. Close the GUI and retry."
}
elseif ($log -match 'SCRIPT ERROR|Abort due to Headless analyzer error') {
    $status = 'SCRIPT_ERROR'
}
elseif ($headlessExit -ne 0) {
    $status = 'HEADLESS_ERROR'
}

# Save succeeded does not prove edits landed. Use the post-script report status.
[pscustomobject]@{
    Script       = $Script
    Status       = $status
    Seconds      = [math]::Round($elapsed.TotalSeconds, 1)
    HeadlessSaved = ($log -match 'Save succeeded')
    ReadOnly     = [bool]$ReadOnly
    Output       = $Out
    Log          = $LogPath
} | Format-List

if ($status -ne 'OK') {
    Write-Host '--- headless errors ---'
    Select-String -Path $LogPath -Pattern 'ERROR|Exception' |
        Select-Object -First 8 |
        ForEach-Object { $_.Line.Trim() }
    exit 1
}
