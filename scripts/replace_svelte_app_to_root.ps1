# PowerShell: replace_svelte_app_to_root.ps1
# 목적: docs 디렉터리 내 모든 파일에서 svelte_app 및 src 경로 표기를 루트 기준으로 치환합니다.
# 사용법: PowerShell에서 실행. 변경 전 커밋 권장.

Param(
    [string]$TargetDir = "docs",
    [switch]$WhatIf
)

Write-Host "대상 디렉터리: $TargetDir"

$files = Get-ChildItem -Path $TargetDir -Recurse -File -Include *.md,*.mdx,*.txt,*.yaml,*.yml,*.json -ErrorAction SilentlyContinue

foreach ($file in $files) {
    $text = Get-Content -Raw -LiteralPath $file.FullName -ErrorAction SilentlyContinue
    if ($null -eq $text) { continue }
    $newText = $text

    # 명시적 매핑
    $newText = $newText -replace 'svelte_app/src/routes/', 'routes/'
    $newText = $newText -replace 'svelte_app/src/lib/', 'lib/'
    $newText = $newText -replace 'svelte_app/src/styles/', 'styles/'
    $newText = $newText -replace 'svelte_app/src/app.css', 'app.css'
    $newText = $newText -replace 'svelte_app/src/app.html', 'app.html'

    # 일반 매핑: svelte_app/ -> (루트)
    $newText = $newText -replace 'svelte_app/', ''

    # src/에서 시작하는 패스는 루트로 매핑 (docs 내에서만)
    $newText = $newText -replace 'src/routes/', 'routes/'
    $newText = $newText -replace 'src/lib/', 'lib/'
    $newText = $newText -replace 'src/styles/', 'styles/'
    $newText = $newText -replace 'src/app.css', 'app.css'
    $newText = $newText -replace 'src/app.html', 'app.html'

    if ($newText -ne $text) {
        Write-Host "Updating: $($file.FullName)"
        if (-not $WhatIf) {
            Copy-Item -LiteralPath $file.FullName -Destination "$($file.FullName).bak" -Force
            Set-Content -LiteralPath $file.FullName -Value $newText -Force
        }
    }
}

Write-Host "치환 완료. 변경된 파일은 .bak 백업을 확인하세요."