# Tableau Viz Gallery Curation

Tableau Viz Gallery 수집은 `tools/collect_tableau_gallery.py`를 사용한다.

## 수집 방식

Tableau 공식 갤러리 HTML이나 Tableau Public URL 규칙만으로 embed code를 만들지 않는다. 실제 브라우저에서 각 상세 페이지를 열고 Share 버튼을 클릭한 뒤, viz iframe 내부의 Share 패널에서 Embed Code input 값을 읽는다.

핵심 흐름:

1. `https://www.tableau.com/viz-gallery`에서 Tableau Public 상세 링크 목록을 수집한다.
2. 각 상세 페이지를 열고 지정한 시간만큼 대기한다.
3. OneTrust 쿠키 배너가 있으면 `onetrust-accept-btn-handler`를 클릭한다.
4. 바깥 Tableau Public 페이지의 Share 버튼을 클릭한다.
5. `public.tableau.com/views/...` iframe으로 전환한다.
6. iframe 내부 Share 패널의 Embed Code input과 Link input을 읽는다.
7. Embed Code 안의 `static_image` param에서 썸네일 URL을 읽는다.
8. 항목별 결과를 즉시 CSV에 저장한다.

## 명령 예시

3번부터 끝까지 수집:

```powershell
python tools/collect_tableau_gallery.py --start-index 3
```

스킵 항목만 10초 대기로 재시도:

```powershell
python tools/collect_tableau_gallery.py --only-index 1 --only-index 7 --only-index 8 --only-index 12 --only-index 17 --only-index 18 --only-index 22 --only-index 27 --wait-seconds 10 --force
```

수집 후 Supabase에 등록:

```powershell
python tools/collect_tableau_gallery.py --start-index 3 --skip-index 1 --skip-index 2 --register
```

`--register`는 `.env`의 `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `FOLIO_ADMIN_PASSWORD`를 사용한다. 기본 관리자 이메일은 `admin@folio.com`이며, 필요하면 `--admin-email`로 바꾼다.

## 2026-08-11 수집 결과

Tableau Viz Gallery 27개 중 23개를 등록했다.

성공 항목은 모두 실제 Share 패널에서 embed URL과 썸네일을 확인했다. `docs/curation/tableau_gallery/all.csv`는 등록된 Tableau 프로젝트를 기존 Streamlit 수집 CSV와 호환되는 형태로 보관한다.

최종 스킵:

- `#1` Finding Oases In Food Deserts: 10초 대기 후에도 embed code와 link를 읽지 못함
- `#7` Total Annual Loss of Bee Colonies in the US: link는 읽혔지만 embed code가 비어 있음
- `#8` Boeing Market Outlook: Tableau Public 상세 페이지가 404
- `#22` VFSG Feb: link는 읽혔지만 embed code가 비어 있음

## 주의사항

- Headless Chrome은 Tableau 쪽에서 차단될 수 있다. 기본은 visible Chrome이다.
- 공유 버튼은 바깥 페이지에 있지만, Embed Code input은 첫 번째 Tableau viz iframe 내부에 있다.
- `body.text`만 보면 Share 패널이 열린 사실을 놓칠 수 있다.
- Tableau UI 언어가 영어가 아닐 수 있으므로 Share 버튼 탐색은 `Share`와 `공유`를 모두 허용한다.
- 제목은 본문 첫 줄보다 브라우저 title에서 `| Tableau Public`을 제거한 값을 우선한다. 본문 첫 줄은 로케일에 따라 `등록`, `만들기` 같은 메뉴 텍스트로 잘못 잡힐 수 있다.
- 긴 작업은 전체가 끝난 뒤 판단하지 말고, 항목 하나가 끝날 때마다 `collected`, `skipped_*`, `error_*`를 기록하고 CSV를 즉시 저장한다.
