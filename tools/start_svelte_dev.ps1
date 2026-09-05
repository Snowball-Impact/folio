[CmdletBinding()]
param([int]$Port = 5174)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$appRoot = Join-Path $repoRoot "svelte_app"
$runtimeRoot = Join-Path $repoRoot ".runtime"
$xdgConfig = Join-Path $runtimeRoot "xdg-config"
$miniflareRegistry = Join-Path $runtimeRoot "miniflare-registry"

New-Item -ItemType Directory -Force -Path $xdgConfig, $miniflareRegistry | Out-Null
$env:XDG_CONFIG_HOME = $xdgConfig
$env:MINIFLARE_REGISTRY_PATH = $miniflareRegistry

$repoEnv = Join-Path $repoRoot ".env"
if (Test-Path $repoEnv) {
    Get-Content $repoEnv | ForEach-Object {
        if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
            $name = $Matches[1]
            if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
                $value = $Matches[2].Trim()
                if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }
}

Push-Location $appRoot
try {
    & npm.cmd run dev -- --host 127.0.0.1 --port $Port
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}
