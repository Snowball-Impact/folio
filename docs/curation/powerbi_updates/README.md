# Power BI Updates Curation

Power BI 분석가 유입용 콘텐츠 후보를 Microsoft Learn 월별 업데이트 아카이브에서 수집한다.

## 수집 대상

- 원문: Power BI Desktop and Power BI service monthly update archive
- 기본 URL: `https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-latest-update-archive?tabs=powerbi-desktop`
- 저장 위치: `docs/curation/powerbi_updates/all.csv`

## 실행

```powershell
python tools\collect_powerbi_updates.py
```

기본값은 2025년 이후 월별 업데이트 섹션을 모두 수집한다. 시작 연도를 바꾸려면:

```powershell
python tools\collect_powerbi_updates.py --since-year 2024
```

디버깅을 위해 개수를 제한할 수도 있다.

```powershell
python tools\collect_powerbi_updates.py --max-releases 3
```

## CSV 필드

- `source_url`: 원문 링크
- `title_en`, `summary_en`, `feature_description_en`: 원문 기반 영문 정보
- `title_ko`, `summary_ko`, `feature_description_ko`: FOLIO 표시용 한국어 초안
- `image_urls`: 원문 섹션에서 발견한 시각자료 후보
- `tags`: FOLIO 큐레이션용 태그 후보
- `publication_status`: 기본값 `review`

## 현재 한계

한국어 번역과 요약은 아직 규칙 기반 초안이다. 공개 전 운영자가 원문을 보고 문맥, 용어, 중요도를 검수해야 한다.

후속으로 OpenAI API 또는 별도 번역/요약 파이프라인을 붙이면 `summary_ko`, `feature_description_ko` 품질을 올릴 수 있다.
