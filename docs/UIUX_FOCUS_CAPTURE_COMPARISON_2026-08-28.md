# FOLIO 핵심 페이지 시각 비교 2026-08-28

## 목적

마이페이지, 알림, 프로젝트 등록, 프로젝트 상세를 원본 Streamlit 캡처와 최신 인증 Svelte 캡처로 나란히 확인했다. 이 문서는 픽셀 점수보다 기능과 UIUX 차이를 찾기 위한 비교 기록이다.

비교 생성물은 [focus-compare-20260828](../artifacts/ui-parity/focus-compare-20260828/)에 저장했다.

## 비교 기준과 한계

- 원본 캡처는 데스크톱 `1424px`, 모바일 `500px`이며 Svelte 인증 캡처는 데스크톱 `1440px`, 모바일 `390px`이다.
- 비교 시 원본 폭으로 비례 조정했지만, viewport와 브라우저 상태가 완전히 같지 않으므로 `first viewport diff`는 pass/fail 점수가 아니다.
- 원본과 Svelte의 로그인 계정·프로젝트 데이터가 달라 카드 수, 제목, 통계, 댓글 수, 세로 길이는 구조 차이와 데이터 차이를 분리해서 판단해야 한다.
- 상세의 cross-origin 대시보드는 full-page 캡처에서 빈 영역처럼 보일 수 있다. iframe 표시 여부는 DOM 메트릭과 전용 `dashboard-frame.png`를 함께 본다.
- 상세 인증 테스트는 댓글 상호작용 뒤 `scrollY=0`으로 복귀한 다음 `detail-viewport.png`와 full-page 캡처를 저장한다. 이전 캡처처럼 상호작용으로 이동한 스크롤 위치에서 저장하면 sticky 헤더가 중간에 합성되어 실제 레이아웃처럼 보일 수 있다.
- `artifacts/ui-parity/same-project-detail-20260825`는 `dd1ed00c-1458-4f8e-92cb-4f31e319625d`를 사용한 과거 산출물이다. 현재 이 ID는 유효 fixture로 확인되지 않았으므로, 해당 자료를 최신 동일 fixture 근거로 사용하지 않는다.

## 캡처 수치

| 페이지 | viewport | 원본 크기 | Svelte 크기 | 높이 비율 | 첫 viewport diff |
| --- | --- | ---: | ---: | ---: | ---: |
| 마이페이지 | desktop | 1424x1039 | 1440x1184 | 1.140 | 0.181 |
| 마이페이지 | mobile | 500x2778 | 390x1457 | 0.524 | 0.264 |
| 알림 | desktop | 1424x1028 | 1440x1000 | 0.973 | 0.168 |
| 알림 | mobile | 500x2767 | 390x1072 | 0.387 | 0.252 |
| 등록 | desktop | 1424x1050 | 1440x1561 | 1.487 | 0.236 |
| 등록 | mobile | 500x2789 | 390x2374 | 0.851 | 0.311 |
| 상세 | desktop | 1424x3622 | 1440x3051 | 0.842 | 0.409 |
| 상세 | mobile | 500x7901 | 390x3389 | 0.429 | 0.357 |

수치 원본은 [report.json](../artifacts/ui-parity/focus-compare-20260828/report.json), 시각 확인용은 [metrics.md](../artifacts/ui-parity/focus-compare-20260828/metrics.md)와 페이지별 `first-viewport`/`full` sheet다.

## 페이지별 판정

## 동일 Fixture 재검증

현재 생존하는 공개 fixture `7553d519-b395-464a-bd57-3b33100e2df1`를 원본과 Svelte 양쪽에 지정해 비로그인 상태로 새로 캡처했다.

| viewport | 원본 캡처 | Svelte 캡처 | 원본 댓글 | Svelte 댓글 | 원본 대표 결과물 | Svelte 대표 결과물 | 판정 |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| desktop | `same-project-detail-20260828/streamlit-7553-desktop.png` | `routes-public-detail-fixture-renders-anonymous-state-desktop/public-detail.png` | 0 | 0 | Embed 안내 + 링크 3개 | Power BI 로딩 iframe 셸 | `partial` |
| mobile | `same-project-detail-20260828/streamlit-7553-mobile.png` | `routes-public-detail-fixture-renders-anonymous-state-mobile/public-detail.png` | 0 | 0 | Embed 안내 + 링크 3개 | Power BI 로딩 iframe 셸 | `partial` |

- 동일 fixture의 제목, 히어로 카드, 메타 정보, 리포트, 댓글 0개 상태는 양쪽에서 확인됐다.
- 원본 캡처는 비로그인 상태에서 Power BI Embed Token 안내와 대시보드/보고서/GitHub 링크를 렌더링했다. Svelte는 같은 비로그인 상태에서 Power BI embed 요청을 시작해 로딩 iframe 셸을 렌더링했다.
- 원본 코드 `folio_app/components/project_detail_content.py`는 Power BI 프로젝트에서도 `get_powerbi_embed_config()` 성공 여부에 따라 SDK viewer 또는 fallback을 선택한다. 따라서 현재 비로그인 캡처만으로 원본 iframe이 동작하지 않는다고 결론내리지 않는다.
- 원본 인증 캡처에서 `로그인 → My Page → 내 프로젝트 보기 → 상세` 내부 이동은 데스크톱·모바일 모두 `로그아웃`, 작성자 액션, 댓글 입력 상태로 확인됐다. 증거는 `same-project-detail-20260828/streamlit-7553-authenticated-internal-navigation-verified-desktop.png`와 `...mobile.png`다.
- 원본 상세를 로그인 후 직접 URL로 열었을 때 데스크톱·모바일 초기 로딩 셸에서는 인증 UI가 잠시 보이지 않았지만, 정착 후 `로그아웃`, 작성자 액션, 댓글 입력, visitor cookie, visible Power BI host가 확인됐다. 직접 URL 세션 복원은 `pass`로 판정하고, 캡처 도구가 초기 상태와 정착 상태를 별도 기록하도록 보강했다.
- 상세 비교 도구는 작은 `h3` overflow를 스크롤 대상처럼 선택하던 문제를 수정했고, `--wait-for-text`, `--settle-seconds`, `--login`, `--via-my-page`를 지원한다.

동일 fixture 비로그인 수치 산출물은 [same-project-detail-20260828](../artifacts/ui-parity/same-project-detail-20260828/)의 `same-project-metrics.md`와 `same-project-report.json`이다. 위 표의 해당 산출물 인증 상태는 `anonymous`로 기록되어 있으며, 인증 비교는 아래 별도 표를 사용한다.

### 1. 마이페이지

- 데스크톱의 히어로, 프로필 요약, 통계 칩, 프로젝트 목록, 보기/수정/삭제 액션의 정보 계층은 유사하다.
- 원본 캡처는 프로젝트 1개, Svelte 인증 캡처는 프로젝트 2개이므로 카드 수와 전체 높이는 시각 parity 근거로 사용하지 않는다.
- 모바일은 원본과 Svelte 모두 페이지 히어로 이미지를 숨기는 구조이며, 프로필 요약과 통계가 세로로 이어진다.
- 프로필 편집 버튼 우측 정렬과 카드 footer의 태그·metrics는 코드와 DOM 검증이 있다.
- 원본 `portfolio_items.py`는 태그를 모두 렌더링하고 metrics를 조회·좋아요·댓글·공개 상태 아이콘으로 표시한다. Svelte도 footer를 같은 아이콘/aria-label 구조로 맞추고 태그 전체를 렌더링했다.
- 원본 캡처의 고정 상태를 mock으로 재현해 프로필 `맹광국/스노우볼 임팩트`, 통계 `전체 1·공개 1·조회 23·좋아요 2`, 프로젝트 1건, 6개 태그, 3개 액션과 삭제 확인 모달을 desktop/mobile에서 캡처했다. 산출물은 `artifacts/playwright/test-results/authenticated-routes-authe-0b8fc-le-and-portfolio-state-auth-{desktop,mobile}/`다.

판정: `partial`

남은 확인: 실제 계정 데이터가 아닌 mock 상태이므로, 실제 데이터에서의 카드 수·읽지 않은 댓글 상태와 동일 데이터 픽셀 비교는 별도 확인한다.

### 2. 알림

- 데스크톱은 최근 알림 제목, 상태, 날짜, 프로젝트 보기 액션의 3열 정보 계층이 원본과 동일한 방향이다.
- 모바일은 원본 코드도 `grid-template-columns: 1fr`로 행을 세로화하므로, Svelte의 상태/제목/시각/프로젝트 보기 순서 자체는 원본과 일치한다.
- 읽음 처리, 모두 읽음, 프로젝트 이동, 헤더 팝오버 열기/ESC 닫기는 DOM과 요청 mock으로 별도 검증됐다.
- 원본 캡처의 알림 데이터와 Svelte 인증 데이터가 다르므로 행 수와 제목 말줄임은 기능 판정과 분리한다.
- 원본 코드상 `프로젝트 보기`는 상태·제목·시간 3열 행 다음 줄에 우측 정렬된다. Svelte도 `.notification-item`을 블록 컨테이너로 바꾸고 버튼을 별도 우측 행으로 배치했으며, 최신 데스크톱·모바일 캡처에서 동일한 구조를 확인했다.
- 원본의 고정 알림 3건을 mock으로 재현해 페이지 진입 후 모두 읽음 상태, `2026-08-02 HH:mm` 날짜, 프로젝트 보기 3개, 헤더 unread 배지 제거를 확인했다. Svelte는 알림 페이지의 자동 읽음 처리를 `folio:notifications-read` 이벤트로 공통 헤더에 동기화한다. 산출물은 `artifacts/playwright/test-results/authenticated-routes-authe-a7b9d--state-and-header-sync-auth-{desktop,mobile}/`다.

판정: `pass`

남은 확인: 실제 DB의 알림 수가 달라질 때의 행 수 차이는 데이터 차이로 분리한다. 읽음 전환·헤더 동기화·버튼의 별도 행·우측 정렬·모바일 폭은 pass다.

### 3. 프로젝트 등록

- 데스크톱은 기본 정보·산출물 링크 2열, 플랫폼/썸네일 선택, hero 미리보기라는 핵심 구조가 원본과 대응된다.
- Tiptap 툴바와 본문 미리보기는 Svelte에 추가됐고, 문단 형식은 원본 Quill의 선택형 흐름에 맞춰 `Normal/H1/H2/H3` 선택기로 노출된다. 위첨자·아래첨자·글자 색상·배경색·글꼴과 이미지 URL·이미지 파일·인라인 수식 입력도 추가했다. 이미지와 수식은 Tiptap 공식 Image/Mathematics 확장과 KaTeX 렌더링을 사용한다. 본문 이미지 파일은 편집 중 로컬 미리보기 후 프로젝트별 `project-body-assets` Storage public URL로 치환해 저장한다. 현재 캡처의 전체 세로 길이가 원본보다 크므로 본문 편집 영역과 preview 상태를 원본의 실제 입력 상태별로 나눠 확인해야 한다.
- 원본 반응형 CSS는 `max-width: 760px`에서 page hero visual을 숨긴다. 기존 Svelte는 등록 hero 미리보기를 모바일에서 다시 표시하고 있었고, 모바일 비교에서 별도 대형 preview 카드가 나타났다.
- 이 차이를 `svelte_app/src/app.css`에서 모바일 `.submit-preview-hero .hero-thumbnail-preview` 숨김으로 수정했다. 5176 기준 인증 모바일 재캡처에서 preview DOM은 화면에 노출되지 않았고, 폼·Tiptap·제출 액션은 유지됐다.
- 원본 저장 코드는 본문을 `problem/dataset/process/insights` 네 필드로 분해한다. Svelte의 비변경 수정 저장 테스트도 저장 직전 동기화된 네 필드에 `<p>` HTML이 포함되는지 데스크톱·모바일 모두 확인했다. 저장 payload 계약은 `pass`다.
- 실제 opt-in persistence 검증에서 Tiptap `h2`, `ul/li`, `blockquote`, `a[href]`, `sup`, `sub`, 글자 색상, 글꼴, 배경색, `img[src]`, inline math가 저장 후 상세와 수정 재진입에서도 유지되는 것을 데스크톱·모바일 모두 확인했다. 해당 결과는 [uiux-rich-body-persistence-20260828](../artifacts/uiux-rich-body-persistence-20260828/)에 저장했다. 위험 URL·style 라이브 주입 검증에서도 `javascript:` 링크·이미지, 위험 style, `script`가 제거되고 안전한 `https` 링크·이미지·수식과 허용된 글자 색상만 유지됐다. 결과는 [uiux-project-body-sanitizer-20260828](../artifacts/uiux-project-body-sanitizer-20260828/)에 저장했다.
- 원본 hero preview의 작성자 fallback과 조회·좋아요·댓글 icon metrics를 Svelte `ProjectCard`의 preview 전용 markup으로 맞췄고, `.submit-hero .card-summary`가 상위 `p` 색상 규칙에 덮이지 않도록 대비를 복구했다. desktop 캡처에서 원본과 같은 하단 정보 계층을 확인했으며, mobile preview 숨김 규칙은 유지한다.
- 문단 형식 선택기의 `Normal -> H2 -> H3 -> H1 -> H2` 전환, 위첨자·아래첨자·글자 색상 mark DOM, 실제 에디터 heading DOM 동기화를 데스크톱·모바일에서 각각 검증했다. 표적 테스트는 `2 passed`였고, 이후 인증 전체 suite도 `40 passed`로 통과했다.

판정: `partial`

남은 확인: Tiptap 툴바와 원본 Quill 툴바의 시각적 차이, viewport 폭 차이에 따른 전체 높이는 `partial`로 남긴다. 이미지 URL 입력과 본문 이미지 파일 업로드는 기능 기준으로 확인됐고, 파일 업로드는 `JPG/PNG/WebP`, 최대 5MB 범위로 제한된다. hero preview·입력 상태 전환·본문 persistence·모바일 숨김은 기능/UX 기준으로 확인됐다.

### 4. 프로젝트 상세

- 데스크톱은 상세 hero, 대표 결과물, 실제 dashboard iframe, 프로젝트 리포트, 댓글 영역이 모두 렌더링된다.
- 원본 반응형 CSS는 모바일에서 hero visual을 숨긴다. 기존 Svelte의 `.detail-card-preview { display: block; }` 예외 때문에 모바일에 hero 카드가 보였고, 원본 캡처와 다른 상단 정보 계층을 만들었다.
- 이 차이를 같은 모바일 media query에서 `.detail-hero.project-detail-image-hero .detail-card-preview { display: none; }`로 수정했다. 5176 기준 인증 모바일 재캡처에서 hero card는 화면에 노출되지 않았고, 대표 결과물 iframe은 `318x640`으로 렌더링됐다.
- 댓글 날짜와 답글/삭제 액션의 조밀한 footer 배치는 코드와 인증 DOM 메트릭으로 확인됐다. 답글 열기/취소와 삭제 확인/취소도 별도 상호작용 테스트가 있다.
- 원본 compact 카드의 최근 활동 `NEW` badge와 `등록일 · 작성자/소속` 하단 메타를 Svelte `ProjectCard`에 추가했다. 상세 desktop assertion에서 `NEW`, `2026-08-27`, `맹광국`을 확인하고, 등록/수정 preview에서는 원본처럼 작성자만 표시하도록 유지했다.
- 동일 제목의 인증 캡처에서 원본은 데스크톱 제목이 한 줄이고 모바일 제목이 작은 계층으로 표시된다. Svelte의 상세 전용 제목 크기를 원본의 실제 렌더링 스케일에 맞춰 조정한 뒤 데스크톱 한 줄, 모바일 축소 상태를 캡처로 확인했다. 상세 fixture 렌더링·Power BI fallback·댓글 밀도·댓글 등록 테스트는 유효 프로젝트를 명시한 재실행에서 desktop/mobile 합계 `8 passed`했다.
- 상세 hero의 compact 카드도 원본 project card와 동일하게 밝은 요약 텍스트와 조회·좋아요·댓글 아이콘 지표를 사용하도록 맞췄다. `ProjectCard`의 compact/preview 분기와 상세 전용 대비 규칙을 적용한 뒤 인증 desktop 캡처에서 구조를 확인했다.
- 최신 인증 캡처는 상호작용 후 최상단 복귀를 거쳐 생성했으며, 별도 viewport 캡처에서 데스크톱·모바일 헤더는 모두 원본 CSS의 상단 여백에 해당하는 `top=16px`으로 확인됐다. 따라서 이전 full-page 이미지에서 헤더가 본문 중간에 보인 현상은 제품 레이아웃 결함이 아니라 캡처 시점 문제였다.

판정: `partial`

남은 확인: 동일 fixture의 모바일 정보 계층과 데스크톱 대표 결과물 폭 차이를 최종 시각 기준으로 판정한다. 원본·Svelte Power BI host 높이와 댓글 footer, 모바일 링크 stacking은 기능/UX 기준으로 확인됐다.

## 이번 수정

- `svelte_app/src/app.css`의 모바일 media query에서 등록 hero thumbnail preview와 상세 hero card preview를 원본처럼 숨겼다.
- `svelte_app/src/lib/components/ProjectBodyEditor.svelte`의 문단 형식 버튼 묶음을 `Normal/H1/H2/H3` 선택기로 정리하고, 위첨자·아래첨자·글자 색상 서식을 추가했다. 선택 위치·본문 동기화 시 현재 heading 상태가 함께 갱신되도록 보강했다.
- toolbar select가 `.project-form select { width: 100% }`에 의해 데스크톱에서 과도하게 늘어나거나 `Normal` 라벨을 자르지 않도록 전용 폭을 지정했다. 이미지·수식·코드·링크 계열의 화면 라벨은 원본 Quill처럼 compact icon 표기로 줄이고 접근 가능한 title/버튼 이름은 유지했다. 최신 등록 desktop 캡처에서 toolbar 한 줄 배치와 mobile 캡처에서 자연스러운 다중 행 접힘을 확인했다.
- 상세 hero 제목 크기를 실제 원본 캡처의 렌더링 스케일에 맞춰 데스크톱 `1.9rem`, 모바일 `1.5rem`으로 조정했다. 긴 동일 fixture 제목의 데스크톱 한 줄 표시와 모바일 축소 계층을 재캡처로 확인했다.
- `npm.cmd run check`: 0 errors / 0 warnings
- `npm.cmd run build`: 통과
- 인증 전체 suite 최신 실행: 데스크톱·모바일 합계 `34 passed, 14 skipped`. skip은 mutation/실제 외부 Power BI 상태에 의존하는 선택 테스트이며, 비변경 인증 UI 회귀는 모두 통과했다.
- 인증 전체 suite 첫 실행에서 토큰 `200` 직후 login 화면이 남는 단발성 세션 정착 경합이 1건 발생했으나, 성공 토큰 확인 후 목적지 재진입을 한정 적용해 재실행했다. 이후 등록·마이페이지·알림·수정·유효 상세 기본 흐름은 통과했고, 유효 상세 fixture를 명시한 상세 전용 실행은 데스크톱·모바일 `8 passed`였다.
- 등록 Tiptap 문단 형식 전환 표적 테스트: 데스크톱·모바일 합계 `2 passed`
- 등록 Tiptap 위첨자·아래첨자·이미지·수식 DOM 표적 검증: 위 표적 테스트에 포함되어 데스크톱·모바일 합계 `2 passed`
- sanitizer style 주입 검증: 안전한 색상 보존·위험 style 제거를 데스크톱·모바일 합계 `2 viewport passed`로 확인
- rich-body persistence 최신 검증: editor·상세·수정 재진입의 구조와 색상·글꼴·배경색·위첨자·아래첨자 mark를 데스크톱·모바일 모두 통과
- rich-body persistence 확장 검증: `https` 이미지와 inline math의 `src/alt/data-latex`가 editor·상세·수정 재진입에서 데스크톱·모바일 모두 유지
- rich-body persistence 파일 이미지 검증: `artifacts/test1_thumbnail.jpg`가 실제 Storage public URL로 업로드되고 URL 이미지와 함께 상세·수정 재진입에서 데스크톱·모바일 모두 유지
- 5176 기준 인증 핵심 페이지 재캡처: 8/8 통과
- 등록·상세 모바일 hero 회귀 검사: 4/4 통과
- 상세 모바일 DOM: iframe 1개, report/comments 존재, 댓글 9개, 날짜·액션 same-row, overflow 0
- 상세 fixture 탐색 테스트는 404 후보를 건너뛰고, 댓글 없는 유효 상세도 시각 캡처 대상으로 유지하도록 보강했다.
- 상세 캡처 테스트에 초기 viewport 좌표와 `detail-viewport.png`를 추가해 sticky 헤더의 full-page 스티칭 오판을 방지했다. 해당 회귀 테스트는 데스크톱·모바일 `2/2` 통과했다.
- 현재 생존 fixture `7553...`의 원본·Svelte 비로그인 동일 fixture 캡처를 desktop·mobile 모두 생성했다. 양쪽 댓글 수는 0개다.
- PBIX 교체 성공 orchestration 계약 테스트는 실제 Workspace를 변경하지 않고 데스크톱·모바일 `2/2` 통과했다. 기존 Embed URL·`supported` 상태 보존, `test.pbix` multipart 전달, 성공 후 상세 이동을 확인했다.
- 실제 PBIX 교체는 테스트 계정 소유 fixture에서 데스크톱·모바일 `2/2` 통과했다. Import `succeeded`, 프로젝트 `published/supported`, report/dataset/embed URL 존재, 상세 Power BI iframe `ready`를 확인했다.
- 최신 Svelte 비로그인 4개 핵심 라우트 캡처/회귀는 데스크톱·모바일 합계 `8 passed, 2 skipped`이며, 스킵은 고정 public detail fixture 미설정이다. 인증 상세는 `PLAYWRIGHT_PROJECT_ID=7553...`를 명시해 데스크톱·모바일 `2 passed`로 재생성했다.
- 모바일 `.powerbi-report`와 SDK 삽입 iframe을 shell 높이까지 확장해 보고서 조작 영역이 축소되지 않도록 수정했다. 상세 fixture 데스크톱·모바일 `2/2`, `check`, `build`가 통과했다.
- 상세 제목 스케일 수정 후 유효 fixture 상세 렌더링·populated 댓글 밀도 테스트는 데스크톱·모바일 합계 `4 passed`했다. 네트워크 권한이 없는 재실행은 Supabase 요청 차단(`ERR_NETWORK_ACCESS_DENIED`)으로 실패했으며 제품 실패로 집계하지 않는다.
- 같은 수정 후 Svelte 상세 metrics는 데스크톱 `powerBIStatus=ready`, shell/report `642/640px`, 모바일 `648.39/646.39px`, 삽입 iframe `318x640`, 수평 overflow `0`을 기록했다. 원본 인증 host `1192x640`/`424x640`과 비교해 대표 결과물 높이 기준은 `pass`로 판정한다.
- 원본 인증 내부 이동과 직접 URL 재진입 모두 정착 후 인증 상태가 확인됐다. 초기 로딩 셸과 최종 인증 상태를 구분해 두 경로 모두 `pass`로 분리한다.

### 인증 동일 Fixture 재검증

`로그인 → My Page → 내 프로젝트 보기 → 상세` 내부 이동으로 같은 fixture를 다시 맞췄다.

| viewport | 원본 인증 캡처 | Svelte 인증 캡처 | 공통 확인 | 대표 결과물 차이 |
| --- | --- | --- | --- | --- |
| desktop | `streamlit-7553-authenticated-root-entry-pbix-desktop.png` | `authenticated-routes-authe-56031--valid-project-fixture-auth-desktop/detail-authenticated.png` (ID 명시 재생성) | 같은 제목·hero·Power BI 탭·리포트·댓글 0개·작성자 액션 | 공통 shell 폭/inset은 조정 후 대응; 원본 SDK host `1192x640`, Svelte shell/report `642/640px`, iframe 내부 표시 방식은 별도 차이 |
| mobile | `streamlit-7553-authenticated-root-entry-pbix-mobile.png` | `authenticated-routes-authe-56031--valid-project-fixture-auth-mobile/detail-authenticated.png` (ID 명시 재생성) | 같은 제목·hero visual 숨김·Power BI 탭·리포트·댓글 0개·작성자 액션 | 원본 SDK host `424x640`, Svelte shell/report `648.39/646.39px`, iframe `318x640`; 모바일 정보 순서는 대응 |

- 원본 캡처의 desktop/mobile 모두 헤더에 `로그아웃`, 상세에 `수정`·`삭제`, 댓글 입력창이 보인다.
- 원본은 정식 루트 `app.py`로 실행하고 `--login --via-my-page --settle-seconds 20`으로 캡처했다. `--diagnose-embed`에서 `#folio-powerbi-report`, 중첩 iframe, visible host `1192x640`/`424x640`이 확인됐다.
- 최신 Svelte metrics는 `powerBIStatus=ready`, desktop shell/report `642/640px`, mobile shell/report `648.39/646.39px`, mobile iframe `318x640`, overflow 0을 기록했다. 양쪽 모두 Power BI iframe 내부 페이지 탭이 캡처됐으며, 이는 내부 콘텐츠 전체 성공이 아니라 보고서 host/탭 렌더링 증거다. 공통 shell의 데스크톱 outer width/header inset은 최신 CSS 조정 후 원본 제한 폭에 맞췄다.
- 이전 `streamlit-7553-authenticated-internal-navigation-*` 링크 fallback 캡처는 잘못된 원본 실행점·전역 CSS 상태가 섞인 stale evidence로 남겨두고, 최종 비교에는 이번 `root-entry-pbix-recompare` 산출물을 사용한다.
- Svelte는 SDK 오류 시 저장된 `power_bi_url`로 fallback iframe을 렌더링하도록 보강했으며, 이는 원본의 `_render_powerbi_embedded_viewer()` 실패 후 `_render_fallback_dashboard()` 분기와 대응한다.
- 외부 Power BI 프레임 차단 재현 테스트에서 데스크톱·모바일 모두 SDK shell 제거, fallback iframe 표시, overflow 0을 확인했다. 이 검증은 실제 Power BI 콘텐츠 성공이 아니라 오류 시 사용자에게 저장 URL 경로를 보장하는 동작 검증이다.
- 동일 상태 비교 산출물은 [same-project-detail-authenticated-20260828](../artifacts/ui-parity/same-project-detail-authenticated-20260828/)에 있다.

## 다음 순서

1. 직접 URL 인증 복원은 정착 후 정상임을 확인했으므로, 이후 캡처는 `target_settled` 상태를 기준으로 삼는다.
2. PBIX 동일 fixture의 host 높이·iframe 표시는 pass로 고정하고, Power BI host 내부 표시 방식과 모바일 상세 정보 계층을 UIUX 기준으로 판정한다. 댓글 density는 댓글이 있는 별도 fixture에서 비교한다.
3. 실제 테스트 계정 fixture에서 Power BI PBIX 교체 성공과 Import 완료·새 Embed 메타데이터 반영을 확인했다. 이후 반복 실행은 전용 격리 fixture에서만 수행한다.
4. 카드 수·콘텐츠 차이를 제거한 뒤 네 페이지의 최종 UIUX 판정을 `pass/partial/unknown`으로 갱신한다.

### 동일 Fixture 재검증 정정

- The Svelte detail capture used for the authenticated comparison was regenerated with `PLAYWRIGHT_PROJECT_ID=7553...`; its title now matches the Streamlit capture `Codex E2E PBIX 등록 검증 20260827-183237`.
- The previous `valid-project-fixture` capture showed a different SmartHRD project and must not be used as same-project visual evidence.
- Same-fixture result: Power BI host and mobile hero-hide behavior match structurally; common desktop content/header inset was adjusted to the original limited shell width. Both captures have zero comments, so comment density is `unknown` for this pair.
- Body sanitizer live result: `javascript:` href and `<script>` were removed on desktop/mobile, while the safe `https` link was preserved. Evidence: `artifacts/uiux-project-body-sanitizer-20260828/`.
- Body sanitizer 확장 결과: 위험 이미지 URL은 제거되고 안전한 `https` 이미지와 inline math `data-latex`만 desktop/mobile에 유지됐다.
- Notification authenticated result: desktop/mobile `8 passed` covering list render, separate project-view row, popover open/close, mark-all-read, project navigation, and mark-read. The functional and responsive information hierarchy is `pass`; common shell inset/width was corrected separately and the page-level full visual judgment remains `partial` because the source data states differ.

## 상세 populated 댓글 재검증

- 원본 `desktop-detail-known.png`와 `mobile-detail-known.png`에는 댓글이 존재하는 상세 상태가 포함되어 있다. 원본 코드 기준 댓글은 번호·작성자·본문·날짜를 기본 행으로 두고, 인증 상태의 답글/삭제 액션을 우측에 조밀하게 배치한다.
- Svelte는 `.comment-card`의 desktop grid와 `.comment-footer`를 사용해 같은 정보 계층을 유지하고, 모바일에서는 footer를 본문 아래 한 행으로 내려 날짜와 액션을 함께 배치한다.
- 실제 인증 GET mock으로 root 댓글 1개와 reply 1개를 구성해 `detail-comment-density.png`와 `detail-comment-delete-confirm.png`를 desktop/mobile로 생성했다. 날짜 표시, 답글 버튼, 삭제 확인·취소, reply 카드, 수평 overflow 0을 확인했으며 테스트 결과는 `2 passed`다.
- 이 검증은 댓글 목록 조회만 mock한 비변경 UI 검증이다. 삭제 확인에서 취소했기 때문에 실제 DB mutation은 발생하지 않는다.
- 판정: 댓글 정보 계층·밀도 `pass`. 실제 원본과 동일한 댓글 데이터 및 작성자 권한 상태의 픽셀 비교는 아직 `partial`이다.

## 2026-08-29 상세 액션 footer 재검증

- 원본 `folio_app/pages/project_detail.py:_render_hero_footer_actions`는 메타 정보와 별도로 우측 액션 흐름을 두고, 공유·좋아요·신고/수정/삭제 순으로 렌더링한다. 공유 기능은 Clipboard API가 없을 때 textarea 복사 fallback도 제공한다(`folio_app/components/share.py`).
- 이전 Svelte 상세는 `ProjectLikeButton`을 별도 `detail-action-primary` 영역에 두어 데스크톱에서 `링크 복사 → 수정/삭제 → 좋아요`처럼 보일 수 있었다. `svelte_app/src/routes/projects/[id]/+page.svelte`에서 좋아요를 같은 `detail-action-group` 안으로 이동해 원본 순서인 `링크 복사 → 좋아요 → 수정/삭제`로 맞췄다.
- Svelte 공유 동작에 `navigator.clipboard`가 없는 경우 `document.execCommand('copy')`를 사용하는 fallback을 추가했다. canonical share query(`page`, `project_id`, `utm_*`)는 기존과 같이 유지한다.
- 동일 fixture 상세의 fallback·hero·댓글 밀도 회귀를 데스크톱·모바일 합계 `6 passed`로 재실행했다. 캡처는 `artifacts/playwright/test-results/authenticated-routes-authe-56031--valid-project-fixture-auth-{desktop,mobile}/detail-viewport.png`에 있다.
- 판정: 액션 순서·반응형 배치 `pass`. 원본과 Svelte의 action chip 시각 스타일과 실제 클립보드 권한이 다른 브라우저에서의 성공 여부는 별도 환경 의존 항목으로 남긴다.

### 2026-08-29 toolbar 그룹 순서 보강

- 원본 Quill 기본 toolbar의 그룹 순서인 `글자 서식 → 색상 → 목록/정렬 → heading/size → 고급 블록 → 링크/이미지 → 글꼴`을 기준으로 `ProjectBodyEditor.svelte`의 toolbar DOM 순서를 재배치했다.
- 기존 Svelte에서 문단 형식이 첫 그룹에 있고 글꼴·색상이 글자 그룹에 섞여 있던 차이를 제거했다. 이미지 파일 업로드·링크 해제·undo/redo는 원본에 없는 Svelte 기능이므로 링크/편집 그룹의 보조 컨트롤로 유지했다.
- 최신 등록 상태 캡처 `artifacts/playwright/test-results/authenticated-routes-authe-d55a8-eview-and-draft-states-auth-{desktop,mobile}/submit-controls.png`에서 desktop은 원본 순서의 compact toolbar, mobile은 동일 그룹의 다중 행 접힘을 확인했다. 컨트롤 간 시각적 겹침과 수평 overflow는 확인되지 않았다.
- toolbar 재배치 후 등록 서식 상태와 수정 기존 상태 로드 회귀는 desktop/mobile 합계 `4 passed`다.
- 판정: toolbar 그룹 정보 계층·반응형 배치 `pass`. Quill/Tiptap 아이콘 glyph와 버튼 border/hover 표현의 픽셀 동일성은 `partial`로 남긴다.

### 2026-08-29 Quill Snow control 스타일 보강

- 로컬 원본 자산 `.venv/Lib/site-packages/streamlit_quill/frontend/build/quill.snow.css`에서 Quill toolbar button은 `height: 24px`, `width: 28px`, `padding: 3px 5px`, `border: none`이며 hover/focus/active 시 `#06c`로 색상만 바뀐다.
- Svelte `app.css`의 toolbar button과 picker를 이 값에 맞춰 transparent control, 24px 높이, compact padding, blue hover/active 배경으로 조정했다. 기존 rounded white button box와 그룹별 border를 제거해 원본 Snow 테마의 밀도를 반영했다.
- `authenticated-routes.spec.ts`에 7개 그룹 DOM 순서, button `border-style: none`, `height: 24px`, hover color `rgb(20, 89, 200)` assertion을 추가했다. desktop/mobile 합계 `2 passed`.
- 최신 desktop/mobile `submit-controls.png`에서 toolbar overflow·겹침 없이 desktop은 compact 단일 행, mobile은 같은 순서의 다중 행으로 표시된다.
- 판정: toolbar 그룹 순서·control 밀도·hover 상태 `pass`. 원본 Quill SVG icon과 Svelte text/pseudo glyph의 모양 자체는 구현 방식이 달라 `partial`이며, 등록/수정 전체 UIUX parity도 아직 `partial`이다.

## 2026-08-29 Quill 기본 서식 parity 보강

- 원본 `streamlit_quill`의 실제 기본 toolbar는 `.venv/Lib/site-packages/streamlit_quill/__init__.py`에 정의되어 있으며, `folio_app/components/project_body.py`는 별도 toolbar를 전달하지 않고 이 기본값을 사용한다. 원본 기준 서식 범위는 H1~H6, 글자 크기(`small/normal/large/huge`), 목록, 내어쓰기·들여쓰기, 정렬, 수식, 인용, 코드, 링크, 이미지, 글꼴, 색상·배경색, 위첨자·아래첨자까지다.
- 기존 Svelte 에디터는 H1~H3까지만 선택할 수 있고 글자 크기·들여쓰기 상태가 저장 구조에 없었다. `svelte_app/src/lib/components/ProjectBodyEditor.svelte`에 H1~H6 선택, `0.75em/1.5em/2.5em` 크기, 블록별 `data-indent` 0~6, 내어쓰기·들여쓰기 명령을 추가했다.
- `svelte_app/src/lib/format.ts`는 위 구조를 sanitizer 통과 후에도 보존하며, `svelte_app/src/app.css`는 H4~H6·크기·들여쓰기의 편집/미리보기 표시를 정의한다. 이 단계에서 원본에 없는 확장인 파일 업로드 이미지와 inline math 보존은 별도 기능으로 유지한다.
- `authenticated-routes.spec.ts`의 등록 에디터 표적 테스트에서 H6 전환, `1.5em` 크기 span, 들여쓰기 후 `data-indent="1"`, 내어쓰기 복원을 데스크톱·모바일에서 검증했다. 결과는 합계 `2 passed`다.
- 최신 검증은 `npm.cmd run check` 0 errors/0 warnings, `npm.cmd run build` 통과다. toolbar 상태 캡처는 `artifacts/playwright/test-results/authenticated-routes-authe-d55a8-eview-and-draft-states-auth-{desktop,mobile}/submit-controls.png`에 있다. 데스크톱은 한 줄 중심으로 렌더링되고 모바일은 여러 줄로 접히며, 현재 캡처에서 컨트롤 겹침은 확인되지 않았다.
- 판정: 원본 toolbar의 주요 서식 기능 대응 `pass`. 원본 Quill과 Tiptap의 아이콘 모양·버튼 그룹 경계·정확한 픽셀 배치는 아직 `partial`이며, 이번 기록만으로 등록 페이지 전체 UIUX parity 완료를 선언하지 않는다.

### 수정 화면 동일 서식 컨트롤 재검증

- `svelte_app/src/routes/projects/[id]/edit/+page.svelte`도 등록 화면과 동일한 `ProjectBodyEditor`를 사용하며, 기존 프로젝트 본문을 먼저 `bodyHtml`로 복원한 뒤 편집한다.
- 수정 페이지 인증 테스트의 기대 범위를 H1~H3에서 원본 기본 toolbar와 같은 H1~H6으로 갱신하고, 글자 크기 `Normal/Small/Large/Huge`, H6 전환 및 기존 h2 상태를 확인하도록 보강했다.
- 실제 인증 프로젝트의 수정 화면에서 기존 제목·본문 h2 4개·hero preview·조건부 PBIX/썸네일 입력을 확인한 뒤, 새 서식 컨트롤을 검증했다. desktop/mobile 합계 `2 passed`.
- 판정: 등록/수정 화면의 서식 컨트롤 구성·기존 본문 로드 `pass`. 수정 후 실제 mutation으로 H6·크기·들여쓰기가 DB 재진입까지 유지되는 것은 별도 opt-in persistence 증거로 남긴다.

### 2026-08-29 수정 저장 서식 persistence 재검증

- `scripts/verify-rich-body-persistence.mjs`를 확장해 snapshot 복구 fixture에 H6 블록, `1.5em` 글자 크기, `data-indent="1"` 들여쓰기를 추가하고 editor·상세·수정 재진입의 DOM shape를 비교했다.
- 검증 중 `svelte_app/src/lib/format.ts` 허용 태그 목록에 H6가 빠져 상세에서 H6 wrapper와 들여쓰기 메타가 제거되는 결함을 발견해 수정했다. 단일 커서 들여쓰기에서 여러 블록이 변경될 수 있던 `ProjectBodyEditor` 대상 선택도 함께 보강했다.
- 최종 결과는 desktop/mobile 각각 `editorHasStructure=true`, `detailHasStructure=true`, `editHasStructure=true`다. H6 텍스트·font-size·indent와 기존 목록·인용·링크·색상·글꼴·배경색·위첨자·아래첨자·이미지·inline math가 세 지점에서 유지됐다.
- 테스트는 `artifacts/uiux-rich-body-persistence-20260829/`에 캡처와 metrics를 저장했으며, 실행 후 fixture의 원본문 필드를 자동 원복했다.
- 판정: 등록/수정 본문의 기능적 저장·상세 표시·재편집 persistence `pass`. 원본 Quill의 내부 HTML sanitizer가 지원하는 범위와 Svelte의 확장 보존 범위는 다르므로 byte-level 동일성은 주장하지 않는다.
