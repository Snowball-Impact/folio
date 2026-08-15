# Power BI Desktop Change Log Curation

Power BI Desktop QFE 변경 로그에서 버그 수정과 개선 항목을 수집한다.

## 수집 대상

- 원문: Power BI Desktop change log
- 기본 URL: `https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-change-log`
- 저장 위치: `docs/curation/powerbi_changelog/all.csv`

## 실행

정기 운영에서는 통합 명령을 사용한다.

```powershell
python tools\collect_powerbi_all.py
```

개별 갱신이 필요할 때는 아래 명령을 사용한다.

```powershell
python tools\collect_powerbi_changelog.py
```

기본값은 2025년 이후 QFE 릴리스 섹션을 모두 수집한다. 시작 연도를 바꾸려면:

```powershell
python tools\collect_powerbi_changelog.py --since-year 2024
```

디버깅을 위해 개수를 제한할 수도 있다.

```powershell
python tools\collect_powerbi_changelog.py --max-releases 5
```

## CSV 필드

- `source_url`: 원문 링크
- `release_label`: QFE 릴리스 이름
- `version`, `released_at`: 버전과 릴리스일
- `fix_en`: 원문 변경/수정 항목
- `summary_ko`: FOLIO 표시용 한국어 요약 초안
- `tags`: 영향 영역 태그 후보
- `publication_status`: 기본값 `review`

## 활용 아이디어

- "이번 Power BI Desktop 업데이트에서 주의할 버그 수정"
- DirectQuery, Snowflake, Copilot, 모델링, 시각화 등 주제별 변경 로그 큐레이션
- PBIX 웹 게시 전 권장 버전/주의사항 콘텐츠
