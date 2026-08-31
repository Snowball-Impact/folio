[CmdletBinding()]
param(
    [int]$Port = 8788,
    [string]$Ip = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$appRoot = Join-Path $repoRoot "svelte_app"
$runtimeRoot = Join-Path $repoRoot ".runtime"
$xdgConfig = Join-Path $runtimeRoot "xdg-config"
$miniflareRegistry = Join-Path $runtimeRoot "miniflare-registry"

New-Item -ItemType Directory -Force -Path $xdgConfig, $miniflareRegistry | Out-Null
$env:XDG_CONFIG_HOME = $xdgConfig
$env:MINIFLARE_REGISTRY_PATH = $miniflareRegistry

Push-Location $appRoot
try {
    & npx.cmd wrangler pages dev .svelte-kit/cloudflare --ip=$Ip --port=$Port
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}
