# Looker Studio Gallery Curation

Looker Studio Gallery 수집은 `tools/collect_looker_studio_gallery.py`를 사용한다.

## 수집 방식

Google Data Studio Gallery는 현재 `https://datastudio.google.com/gallery`에서 접근된다. 카드 DOM에 제목, 작성자, 설명, `open/...` URL, 썸네일 URL이 노출된다.

핵심 흐름:

1. Gallery의 `a.reportImageUrl` 카드 목록을 읽는다.
2. 카드의 `open/...` URL을 실제 브라우저에서 연다.
3. 브라우저가 이동한 `reporting/{report_id}/page/{page_id}` URL을 source URL로 사용한다.
4. `reporting/`을 `embed/reporting/`으로 바꾼 URL을 iframe용 embed URL로 사용한다.
5. embed URL을 실제로 열어 본문이 렌더되는지 확인한다.
6. 카드 이미지의 `thumbnail?sz=w320-h240-p-k-nu` URL을 썸네일로 사용한다.
7. 항목별 결과를 즉시 CSV에 저장한다.

Tableau와 달리 Share 패널을 열 필요가 없었다. 공개 Gallery 항목은 `open` URL이 실제 report URL로 리다이렉트되고, `embed/reporting` URL이 바로 렌더된다.

## 명령 예시

전체 수집:

```powershell
python tools/collect_looker_studio_gallery.py
```

나머지 카테고리 수집:

```powershell
python tools/collect_looker_studio_gallery.py --category "Marketing Templates" --category Community --category "Community Visualizations" --register
```

알려진 모든 카테고리 수집:

```powershell
python tools/collect_looker_studio_gallery.py --all-categories --register
```

수집 후 Supabase 등록:

```powershell
python tools/collect_looker_studio_gallery.py --register
```

일부 항목만 재시도:

```powershell
python tools/collect_looker_studio_gallery.py --only-index 3 --force
```

`--register`는 `.env`의 `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `FOLIO_ADMIN_PASSWORD`를 사용한다.

## 2026-08-11 수집 결과

Featured Gallery 11개를 1차 등록한 뒤 iframe 접근성을 재검증했다. 이후 Marketing Templates, Community, Community Visualizations 카테고리까지 추가 수집했다. 보고서 소유자가 외부 사이트 보기를 막았거나 Looker Studio 시스템 오류가 반복되는 항목은 skip 처리했다.

검증 결과:

- valid CSV rows: 80
- skipped CSV rows: 81
- missing embed: 0
- missing thumbnail: 0
- Supabase public Looker Studio projects: 80
- Supabase hidden Looker Studio projects: 6

Featured 1차 skip 처리:

- How much do countries invest in Research & Development?: `보고서에 액세스할 수 없음`
- Machine Learning with TensorFlow.js: `보고서에 액세스할 수 없음`
- Overview of Google Analytics (Blue World report): `보고서에 액세스할 수 없음`
- MLS Players on Both Sides of Fouls in 2018: `보고서에 액세스할 수 없음`
- Website & Marketing Performance Report: Looker Studio 시스템 오류 반복
- Nonprofit Web Data Template: `보고서에 액세스할 수 없음`

위 6개는 Supabase에서 삭제하지 않고 `is_public=false`로 전환했다.

나머지 카테고리 수집 결과:

- Marketing Templates: 3개 모두 외부 embed 차단으로 skip
- Community: 정상 64개
- Community Visualizations: 정상 11개

Skip 로그는 `docs/curation/looker_studio_gallery/skipped.csv`에 보존한다.

## 주의사항

- `datastudio.google.com`은 여전히 Data Studio 도메인을 쓰지만 제품명은 Looker Studio로 표기한다.
- source URL은 Gallery 카드의 `open/...` URL이 아니라, 실제로 이동한 `reporting/.../page/...` URL을 저장한다.
- embed URL은 실제 렌더 확인 후 `embed/reporting/.../page/...` URL을 저장한다.
- 본문이 비어 있지 않아도 `보고서에 액세스할 수 없음`, 외부 사이트 보기 사용 중지, 시스템 오류 문구가 있으면 사용자에게 정상 보고서가 아니므로 skip한다.
- Gallery 카드 description은 짧은 소개로 쓸 수 있다.
- 제목은 Gallery 카드 제목을 우선 사용하고, 필요하면 보고서 title에서 `› ...` 뒤를 제거한 값을 fallback으로 사용한다.
