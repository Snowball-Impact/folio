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
$envFile = Join-Path $repoRoot ".env"

New-Item -ItemType Directory -Force -Path $xdgConfig, $miniflareRegistry | Out-Null
$env:XDG_CONFIG_HOME = $xdgConfig
$env:MINIFLARE_REGISTRY_PATH = $miniflareRegistry
$env:CLOUDFLARE_INCLUDE_PROCESS_ENV = "true"

if (Test-Path -LiteralPath $envFile) {
    Get-Content -LiteralPath $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }

        $match = [regex]::Match($line, "^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
        if (-not $match.Success) {
            return
        }

        $key = $match.Groups[1].Value
        $value = $match.Groups[2].Value.Trim()
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

Push-Location $appRoot
try {
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    & npx.cmd wrangler pages dev .svelte-kit/cloudflare --ip=$Ip --port=$Port --env-file=$envFile
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}
