param()

$ErrorActionPreference = 'SilentlyContinue'
$hasFailure = $false

function Write-Status($name, $status, $detail) {
    Write-Output ("[{0}] {1}: {2}" -f $status, $name, $detail)
}

$chromeCandidates = @(
    (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'),
    (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe')
) | Where-Object { $_ }

$chrome = $chromeCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ($chrome) {
    $version = (Get-Item -LiteralPath $chrome).VersionInfo.ProductVersion
    Write-Status 'chrome' 'PASS' ("installed ({0})" -f $version)
} else {
    Write-Status 'chrome' 'FAIL' 'executable not found'
}

$browserRoot = Join-Path $HOME '.codex\plugins\cache\openai-bundled\browser'
$browserPackage = Get-ChildItem -LiteralPath $browserRoot -Directory -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending |
    Select-Object -First 1

if (-not $browserPackage) {
    Write-Status 'browser_plugin' 'UNKNOWN' 'local browser plugin cache not found'
    exit 2
}

$scripts = Join-Path $browserPackage.FullName 'scripts'
$extensionCheck = Join-Path $scripts 'check-extension-installed.js'
$hostCheck = Join-Path $scripts 'check-native-host-manifest.js'

if ((Test-Path -LiteralPath $extensionCheck) -and (Get-Command node -ErrorAction SilentlyContinue)) {
    $extensionOutput = (& node $extensionCheck --json 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -eq 0) {
        Write-Status 'chrome_extension' 'PASS' 'installed and enabled'
    } else {
        $hasFailure = $true
        Write-Status 'chrome_extension' 'FAIL' 'missing or disabled; run the detailed checker for profile output'
    }
} else {
    Write-Status 'chrome_extension' 'UNKNOWN' 'checker or Node.js unavailable'
}

if ((Test-Path -LiteralPath $hostCheck) -and (Get-Command node -ErrorAction SilentlyContinue)) {
    $hostOutput = (& node $hostCheck --json 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -eq 0) {
        Write-Status 'native_host' 'PASS' 'manifest and registry are present'
    } else {
        $hasFailure = $true
        Write-Status 'native_host' 'FAIL' 'manifest or registry registration is missing'
    }
} else {
    Write-Status 'native_host' 'UNKNOWN' 'checker or Node.js unavailable'
}

Write-Status 'browser_runtime' 'UNKNOWN' 'runtime discovery must be checked from the Browser integration'
Write-Output 'This diagnostic is read-only. It does not install extensions or modify Chrome profiles/registry.'

if (-not $chrome -or $hasFailure) { exit 2 }
