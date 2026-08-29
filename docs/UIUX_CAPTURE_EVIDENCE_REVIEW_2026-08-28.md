# FOLIO UIUX 캡처 증거 재검토 2026-08-28

## 목적

Streamlit 원본과 Svelte 구현을 원본 코드, 원본 캡처, Svelte 코드, 실제 브라우저 DOM/캡처로 대조한다. 이 문서는 2026-08-28 Desktop Browser 캡처와 Playwright 인증 캡처를 합친 현재 증거 기준이다.

`pass`는 해당 항목의 코드·캡처·DOM 증거가 모두 있는 경우에만 사용한다. 데이터가 다르거나 상태를 재현하지 못한 항목은 `partial`, 증거가 없는 항목은 `unknown`으로 남긴다.

## 증거 범위와 한계

- Desktop Browser 결과: [README](../artifacts/browser-viewport-captures-2026-08-28T01-56-42-329Z/README.md), [capture-report.json](../artifacts/browser-viewport-captures-2026-08-28T01-56-42-329Z/capture-report.json)
- Desktop Browser 캡처는 `/my`, `/notifications`, `/submit`의 비로그인 상태다. 상세에 사용한 `7553d519-b395-464a-bd57-3b33100e2df1`는 데스크톱·모바일 모두 404다.
- Desktop Browser 결과의 모바일 문서 크기는 `375x860`으로 기록되어 있다. 정확한 `390x844` 인증 상태는 Playwright로 별도 캡처했다.
- Playwright는 `svelte_app/playwright.config.ts`의 `desktop 1440x1000`, `mobile 390x844` 설정을 사용한다.
- 인증 Playwright 현재 계정의 프로젝트 데이터는 원본 캡처의 고정 데이터와 다르다. 따라서 카드 수·문구·세로 길이의 픽셀 동일성은 별도 판정 대상이다.
- 초기 인증 테스트 결과는 관리형 서버에서 `26 passed, 4 skipped`였다. 고정 `PLAYWRIGHT_PROJECT_ID`가 없던 당시 상세 fallback·댓글 fixture가 스킵된 기록이며, 현재 기준은 아래 최신 `40 passed, 0 skipped` 실행 결과다.
- cross-origin dashboard iframe은 full-page 캡처에서 빈 패널처럼 저장될 수 있으므로, iframe 표시 여부는 전용 `dashboard-frame.png` 캡처와 DOM 크기 메트릭을 함께 판정한다.
- 상세 full-page 캡처는 댓글 상호작용 후 `scrollY=0`으로 복귀해 저장한다. 이전 위치에서 캡처하면 sticky 헤더가 중간에 합성될 수 있으므로 `detail-viewport.png`와 좌표 메트릭을 함께 증거로 사용한다.
- 기존 `same-project-detail-20260825`는 과거 fixture와 과거 포트의 산출물이며, 현재 유효한 동일 fixture 근거가 아니다. 원본 서버 재기동과 fixture 생존 확인 전까지 최종 parity 판정에 사용하지 않는다.
- 현재 생존 fixture `7553...`로 원본·Svelte 비로그인 상세를 desktop·mobile 재캡처했다. 동일 제목·히어로·리포트·댓글 0개는 확인했지만, 원본은 Embed 안내/링크를 보이고 Svelte는 Power BI 로딩 iframe 셸을 보여 대표 결과물 인증 parity는 `unknown`이다.
- 원본 인증은 내부 이동과 직접 상세 URL 재진입 모두 정착 후 유지됐다. 직접 URL은 초기 로딩 셸에서 잠시 `hasLogout=false`였지만, 정착 후 `hasLogout=true`, `folio/access_token`·`folio/refresh_token`·visitor cookie, 작성자 액션, 댓글 입력, visible Power BI host가 확인됐다. 따라서 직접 URL 인증 유지 판정은 `pass`이며, 초기 상태를 최종 상태로 오인하지 않도록 캡처 도구에 `target_initial`/`target_settled` 진단을 분리했다.

## 페이지별 증거표

| 영역 | 원본 코드 근거 | 원본 캡처 근거 | Svelte 코드 근거 | Svelte DOM/캡처 근거 | 판정 |
|---|---|---|---|---|---|
| 마이페이지: 비로그인 가드와 히어로 | `folio_app/pages/protected.py:67-80`에서 히어로와 로그인 필요 흐름 | `artifacts/ui-parity/streamlit/desktop-my-page.png`, `mobile-my-page.png` | `svelte_app/src/routes/my/+page.svelte`의 `needsLogin` 분기와 히어로 | Desktop Browser `desktop-my.dom.txt`, `mobile-my.dom.txt`; Playwright 인증 캡처에도 동일 히어로 이미지 확인 | pass |
| 마이페이지: 프로필·통계·프로젝트 관리 | `protected.py:106-129`, `157-189`; 원본 포트폴리오 카드에 태그·지표·보기/수정/삭제가 포함됨 | 원본 마이페이지 캡처에서 프로필 편집은 우측, 카드 하단에 태그·지표, 우측 액션 3개 | `svelte_app/src/routes/my/+page.svelte:174-270`; `app.css:3504-3613` | `my-authenticated.png` 데스크톱/모바일, `authenticated-metrics.json`: 프로젝트 카드 2개, 버튼 8개, 모바일 가로 overflow 0 | partial: 원본 고정 데이터는 1개 프로젝트, 인증 계정은 2개라 동일 데이터 픽셀 비교는 아님 |
| 마이페이지: 태그·지표 가시성 | `folio_app/components/portfolio_items.py:16-50`; 원본 태그/metrics를 카드 footer에 렌더링 | 원본 카드에서 태그와 조회·좋아요·댓글·공개 상태가 보임 | `my/+page.svelte:245-258`; `app.css:3590-3608`에서 muted 지표와 원본 계열 태그 색상 | Playwright 테스트가 `.portfolio-card-footer .tag`, `.portfolio-card-meta` 가시성을 직접 검증했고 인증 캡처에서 표시됨 | pass |
| 마이페이지: 동일 데이터 카드 footer·통계·삭제 확인 | `folio_app/components/profile_summary.py:7-50`, `components/portfolio_items.py:16-50`; metrics는 아이콘과 aria-label로, 태그는 전체 렌더링 | `artifacts/ui-parity/streamlit/desktop-my-page.png`, `mobile-my-page.png`의 `1/1/23/2`, 6개 태그, 아이콘형 조회·좋아요·댓글·공개 상태, 우측 3개 액션 | `svelte_app/src/routes/my/+page.svelte:245-275`, `app.css:3590-3670`; footer 아이콘 SVG·전체 태그·삭제 확인 모달 | 동일 fixture mock 테스트가 프로필/통계 `1/1/23/2`, 6개 태그, 4개 aria-label 지표, 보기·수정·삭제, 삭제 확인·취소, desktop/mobile overflow 0을 검증하고 `my-same-fixture.png`, `my-same-fixture-delete-confirm.png`를 생성 | pass: 동일 데이터 상태의 구조·기능 증거 확보; 픽셀 차이는 viewport/렌더링 환경으로 별도 판단 |
| 마이페이지: 프로필 편집 위치 | `protected.py:157-165`의 프로필 overview와 편집 버튼 | 원본 캡처에서 `프로필 편집`이 프로필 패널 하단 우측 | `my/+page.svelte:174-200`; `.profile-summary` flex 정렬 | Playwright가 편집 버튼 우측 경계를 프로필 패널 65% 이후로 검증 | pass |
| 알림: 목록·읽음 처리·날짜·행 구조 | `folio_app/pages/notifications.py:33-89`; `styles/notifications.py:11-110`의 3열 행, 읽음 처리, `YYYY-MM-DD HH:mm` 및 프로젝트 보기 별도 행 | `desktop-notifications.png`의 `최근 알림`, 상태·제목·전체 시각·프로젝트 보기 행 | `svelte_app/src/routes/notifications/+page.svelte:94-140`; `svelte_app/src/app.css:3141-3219` | 최신 `notifications-authenticated.png` 데스크톱/모바일에서 상태·제목·시간 행과 우측 프로젝트 보기 행을 확인; `authenticated-routes.spec.ts:31-45`가 버튼 하단 배치·우측 정렬·폭 제한·overflow 0을 검증 | pass: 원본의 데스크톱/모바일 행 정보 계층과 버튼 위치를 DOM·캡처로 확인 |
| 알림: 동일 read 상태·헤더 동기화 | `folio_app/pages/notifications.py:43-59`는 페이지 렌더 후 unread를 전체 읽음 처리하고, `styles/notifications.py:11-110`은 읽음 행을 유지 | `artifacts/ui-parity/streamlit/desktop-notifications.png`, `mobile-notifications.png`의 3개 읽음 행, `YYYY-MM-DD HH:mm`, 우측 프로젝트 보기, 헤더 새 알림 배지 없음 | `notifications/+page.svelte:25-63`, `AuthNav.svelte:34-66`의 자동 읽음 이벤트 동기화; `app.css:240-255`는 caret과 배지 selector 분리 | 동일 3개 mock 알림 테스트가 desktop/mobile에서 3개 read 행, 날짜·제목·액션, PATCH payload, 헤더 unread badge 제거, overflow 0을 검증하고 `notifications-same-state.png`를 생성 | pass: 동일 상태 기능·정보 계층 확보; 픽셀 차이는 viewport 차이로 별도 판단 |
| 알림: 헤더 알림 팝오버와 상호작용 | 원본 레이아웃/알림 서비스 코드 및 기존 캡처 기록에 존재 | 기존 원본 캡처 및 별도 알림 UI 비교 대상 | `AuthNav.svelte`의 `aria-expanded` 토글·팝오버 렌더링 | Playwright 인증 테스트가 데스크톱·모바일에서 닫힘→열림, 알림 목록 표시, `Escape` 닫힘을 검증; `notification-popover.png` 저장 | pass: 핵심 열기/닫기 상태 전이 증거 확보 |
| 알림: 읽음 처리·프로젝트 이동 | `folio_app/pages/notifications.py:33-89`의 읽음 처리와 프로젝트 연결 흐름 | 원본 알림 행의 프로젝트 보기 액션 | `notifications/+page.svelte`, `AuthNav.svelte`, `lib/notifications.ts`의 `markNotificationRead`·`markAllNotificationsRead` | Playwright가 mock 알림으로 `모두 읽음` 후 0개 상태, 개별 알림의 읽음 `PATCH`와 프로젝트 상세 이동을 데스크톱·모바일에서 검증 | pass: 실제 side effect 없이 요청·상태·이동 계약 확인 |
| 프로젝트 등록: 비로그인 가드·히어로 | `folio_app/pages/protected.py:31-56`의 등록 페이지 가드와 히어로 | 원본 `desktop-submit.png`와 Desktop Browser submit 캡처 | `svelte_app/src/routes/submit/+page.svelte`, `ProjectHeroThumbnailPreview.svelte` | Desktop Browser 비로그인 DOM/캡처, Playwright 인증 `submit-authenticated.png` 데스크톱/모바일 | pass: 가드와 주요 히어로/폼 진입 상태 확인 |
| 프로젝트 등록: 기본 정보·링크·썸네일 미리보기 | 원본 등록 캡처의 기본 정보/산출물 링크/썸네일 설정 2열 구조 | 원본 첫 화면의 두 열 입력과 우측 썸네일 설정 | `submit/+page.svelte`, `ProjectFormOverview.svelte`, `ProjectHeroThumbnailPreview.svelte`, `ProjectCard.svelte` | 인증 metrics: form 1, input 15, project card 1; Playwright가 이미지 업로드·URL·화면 캡처·PBIX 선택 전환을 데스크톱·모바일에서 검증; `submit-controls.png` 저장 | pass: 입력 상태 전환과 미리보기 반영 증거 확보 |
| 프로젝트 등록: hero 미리보기 정보 계층 | `folio_app/components/project_form.py:82-120`, `folio_app/components/ui.py:128-158`의 project card preview, 작성자 fallback과 icon metrics | `desktop-submit.png` hero 카드 하단의 `작성자`, 조회·좋아요·댓글 아이콘 및 밝은 요약 텍스트 | `ProjectHeroThumbnailPreview.svelte`, `ProjectCard.svelte:31-71`, `app.css:2530-2565`, `:6350-6365` | 인증 등록 상태 테스트가 desktop에서 작성자와 3개 `aria-label` 지표를 확인하고, mobile에서는 원본 규칙대로 preview 숨김을 확인; `submit-empty-baseline.png` 재생성 | pass: hero preview 구조·대비·반응형 표시 규칙 확보 |
| 프로젝트 수정: 실제 썸네일 업로드·복구 | 원본 수정 폼의 썸네일 파일 연결·삭제 흐름 | 원본 등록/수정 캡처의 썸네일 선택 상태 | `edit/+page.svelte`의 `uploadProjectThumbnail`·`deleteProjectThumbnail` 연계 | opt-in `@mutation-thumbnail` 테스트가 `artifacts/test1_thumbnail.jpg`를 실제 업로드해 상세 이미지·기존 썸네일 삭제 옵션을 확인하고 auto-cover로 복구; 데스크톱·모바일 2/2 통과 | pass: Storage/DB 연결 후 복구까지 확인 |
| 프로젝트 등록: 본문 서식과 미리보기 | 원본 등록 캡처에서 `프로젝트 내용`이 다음 섹션으로 이어짐 | 원본 `desktop-submit.png`의 본문 영역 | `ProjectBodyEditor.svelte`, `projectBody.ts`, `format.ts`의 sanitize 경로 | 인증 캡처에 Tiptap 툴바, 익명 섹션 h2, `본문 미리보기`가 표시됨; Playwright가 미리보기 열림과 h2 4개를 데스크톱·모바일에서 검증; sanitizer에서 script 제거; 실제 persistence 검증에서 상세·수정 재진입까지 확인 | pass: 본문 구조·미리보기·위험 콘텐츠 차단·저장 재진입 증거 확보; Quill과의 glyph 픽셀 parity는 별도 partial |
| 프로젝트 수정: 기존 상태 로드와 미리보기 | 원본 보호 페이지의 내 프로젝트 수정 진입 흐름과 등록 폼 재사용 구조 | 원본 마이페이지의 프로젝트 관리 영역 및 수정 진입 상태 | `svelte_app/src/routes/projects/[id]/edit/+page.svelte`, `ProjectFormOverview.svelte`, `ProjectBodyEditor.svelte` | Playwright 인증 테스트가 마이페이지의 실제 수정 링크를 따라가 기존 제목·썸네일 모드·히어로 미리보기·본문 h2 4개·모바일 overflow 0을 검증; `edit-existing-state.png` 저장; rich-body persistence에서 서식 재진입 확인 | pass: 기존 상태 로드와 서식 재편집 상태 증거 확보 |
| 프로젝트 수정: 저장 요청과 상세 이동 | 원본 수정 완료 후 프로젝트 상세로 이어지는 보호 페이지 흐름 | 원본 수정/상세 전환 흐름 | `edit/+page.svelte`의 `submitProject` → `updateProject` → `goto` | 실제 실행 서버 `5176`을 명시한 Playwright가 Supabase `PATCH` payload, 상세 URL, hero와 기존 제목을 desktop/mobile에서 확인; opt-in mutation에서 상세·수정·마이페이지 재진입과 원복 확인 | pass: 실제 fixture의 저장 반영·재진입·복구 증거 확보 |
| 프로젝트 수정: 실제 fixture 저장 반영·복구 | 원본 수정 저장이 프로젝트 데이터에 반영되는 흐름 | 원본 수정 후 상세/내 프로젝트에서 변경 내용을 확인하는 흐름 | `edit/+page.svelte`의 실제 저장 경로와 `projects.ts:updateProject` | opt-in `@mutation` 테스트가 한 줄 소개 marker를 실제 저장한 뒤 상세·수정 재진입·마이페이지 카드에서 확인하고, 원래 값으로 복구; 데스크톱·모바일 2/2 통과 | pass: 한 필드의 실제 persistence와 복구 증거 확보; PBIX/썸네일 후속 저장은 별도 |
| 프로젝트 수정: PBIX 게시 실패 안전성 | 원본 요구사항상 새 Import 실패 시 기존 Power BI 게시본 유지 | 원본 PBIX 처리 진행/실패 상태 흐름 | `edit/+page.svelte`에서 새 PBIX가 있을 때 기존 `power_bi_url`을 먼저 지우지 않는 저장 payload | opt-in `@mutation-pbix-safe` 테스트가 기존 Embed URL·`supported` 상태 보존, 게시 실패 메시지, 수정 폼 유지 상태를 데스크톱·모바일에서 검증; 2/2 통과 | partial: 클라이언트 저장·게시 orchestration은 검증, 실제 Power BI Import 성공/실패 응답은 별도 환경 검증 필요 |
| 프로젝트 수정: 실제 PBIX 교체 성공 | 원본 `services/powerbi.py`의 Import polling → Report metadata 조회 → `powerbi_reports` upsert → 프로젝트 상태 갱신 | 실제 테스트 계정 fixture의 PBIX 교체 실행 캡처 | `edit/+page.svelte`, `powerbi-publish.ts`, `api/projects/[id]/powerbi-publish/+server.ts` | `@mutation-pbix-live` 데스크톱·모바일 `2/2`; 실제 `test.pbix` 게시 후 상세 Power BI iframe `ready`, DB 상태 `published/supported`, `import_status=succeeded`, report/dataset/embed URL 존재, 오류 없음 | pass: 테스트 계정 fixture 기준 실제 Import 및 메타데이터 반영 |
| 마이페이지: 프로필 저장 | `folio_app/pages/protected.py:211-263`의 프로필 수정 폼과 저장 흐름 | 원본 프로필 편집 상태의 입력·저장 액션 | `my/+page.svelte`의 `saveProfile`, `lib/auth.ts:updateProfile` | Playwright가 공백이 포함된 이름을 입력해 normalized `profiles PATCH` payload를 확인하고 성공 메시지·편집 폼 닫힘을 데스크톱·모바일에서 검증 | pass: 실제 프로필 변경 없이 저장 계약과 UI 상태 전이 확인 |
| 상세: 히어로·대시보드·댓글 영역 | `folio_app/pages/project_detail.py:109-133`, `161-192`; 항상 댓글 섹션 렌더링 | 유효한 원본 기준 캡처 `artifacts/ui-parity/streamlit/desktop-detail-known.png` | `svelte_app/src/routes/projects/[id]/+page.svelte:184-342`, `ProjectComments.svelte`, `PowerBIReport.svelte` | Playwright 인증 상세 캡처 `detail-authenticated.png` 및 초기 viewport `detail-viewport.png` 데스크톱/모바일; metrics에 detail card, visual panel, iframe, report, comments 모두 존재 | pass: 실제 유효 프로젝트 SSR 200과 구조 렌더링을 확인. 동일 fixture 픽셀 parity는 별도 |
| 상세: hero 제목·카드 정보 계층 | `folio_app/styles/hero.py:485-515`, `components/ui.py:74-158`의 상세 hero와 project card 규칙 | 동일 fixture 원본 인증 desktop/mobile 캡처에서 데스크톱 제목 한 줄, 모바일 축소 제목, 카드 밝은 요약·아이콘 지표 | `svelte_app/src/app.css:2980-2997`, 모바일 `:5789-5795`, 상세 대비 `:3794-3803`; `ProjectCard.svelte` compact/preview icon metrics | `authenticated-routes-authe-56031--valid-project-fixture-auth-{desktop,mobile}/detail-viewport.png`; desktop 제목 한 줄·밝은 요약·3개 icon metrics, mobile 제목 축소·overflow 0; 상세 테스트 합계 4 passed | pass: 시각 정보 계층·줄바꿈·카드 지표를 캡처와 DOM으로 확인 |
| 상세: populated 댓글 정보 계층·밀도 | `folio_app/components/project_comments.py:185-240`, `folio_app/styles/detail_comments.py:85-165`, `200-230`, `336-416`에서 번호·작성자·본문·날짜와 답글/삭제 액션을 조밀하게 배치 | `artifacts/ui-parity/streamlit/desktop-detail-known.png`, `mobile-detail-known.png`에 댓글 카드와 날짜 상태 확인 | `svelte_app/src/lib/components/ProjectComments.svelte:190-231`; `app.css:4868-5008`, 모바일 `app.css:6716-6794`의 grid/footer 구조 | 인증 GET mock populated 테스트가 root/reply 2개를 렌더링하고 `detail-comment-density.png`, `detail-comment-delete-confirm.png` desktop/mobile을 생성; 날짜 표시·답글·삭제 확인·취소·same-row 메트릭 통과 | pass: desktop/mobile `2 passed`, 실제 DB mutation 없음 |
| 상세: iframe 조건과 댓글 밀도 | 원본 상세는 시각 패널·링크·댓글을 프로젝트 상태에 따라 렌더링 | 원본 상세 기준 캡처와 기존 댓글 비교 기록 | `+page.svelte:274-316`에서 dashboard URL이면 iframe, `ProjectComments.svelte:189-229`, `app.css:4784-4876`에서 날짜/액션을 같은 grid 행에 배치 | Playwright metrics에서 양 viewport 모두 iframe 1개와 표시 크기 확인, 전용 `dashboard-frame.png`에 SmartHRD 화면 렌더링 확인, 댓글 카드 9개·날짜/액션 same row·overflow 0 | pass: full-page 캡처의 iframe 공백은 캡처 한계이며 전용 iframe 캡처에서는 콘텐츠 표시 |
| 상세: 댓글 답글·삭제 확인 상호작용 | `folio_app/components/project_comments.py:135-182`의 답글 열기/취소, `:218-253`의 삭제 확인/취소 | 원본 상세 캡처 및 댓글 행의 답글·삭제 액션 | `svelte_app/src/lib/components/ProjectComments.svelte`의 `replyTargetId`·`deleteConfirmId` 상태 전이 | 인증 Playwright 상세 테스트가 데스크톱·모바일에서 답글 열기/취소와 삭제 확인/취소를 실행; 해당 시나리오 2/2 통과 | pass: 실제 side effect 없이 상태 전이를 검증 |

## 인증 동일 Fixture 추가 증거

- 원본 `folio_app/app.py`의 상세 공개 빠른 경로가 CookieManager를 건너뛰어 로그인 쿠키를 복원하지 못하던 문제를 제거했다. 상세도 쿠키 준비·복원 단계를 거치도록 변경했고, 직접 URL은 정착 후 인증 상태를 확인했다.
- `folio_app/services/auth_restore.py`는 유효한 `set_session()` 뒤 프로필·정책 동의 보정 실패를 인증 실패로 전파하지 않는다. 회귀 테스트는 `tests/test_auth_stability.py`에 있다.
- 원본 내부 이동 및 직접 URL 인증 캡처에서 데스크톱·모바일 모두 `로그아웃`, 작성자용 `수정/삭제`, 댓글 입력창이 확인됐다. 직접 URL의 초기 로딩 셸은 정착 후 인증 상태로 전환되므로 캡처 대기 조건을 포함해 `pass`로 판정한다.
- 원본·Svelte 동일 fixture 인증 비교는 프로젝트 ID를 명시해 다시 생성한 [same-project-detail-authenticated-20260828](../artifacts/ui-parity/same-project-detail-authenticated-20260828/)에 저장했다. 정식 루트 `app.py` 기준 원본과 Svelte 모두 같은 제목의 Power BI iframe host/페이지 탭을 보였다. 비교 리포트는 `root-entry-pbix-recompare`다. 이전 캡처가 다른 프로젝트였던 사실은 최신 산출물로 정정한다.
- 위 페이지별 표의 상세 행에서 `valid-project-fixture` 캡처를 동일 fixture 근거로 기록한 부분은 폐기한다. 해당 캡처는 다른 SmartHRD 프로젝트였으며, 동일 fixture 판정은 ID를 명시해 재생성한 캡처와 `root-entry-pbix-recompare`만 사용한다. 동일 fixture 댓글 수는 0개이므로 댓글 밀도는 `unknown`이다.
- 이전 원본 링크 fallback 캡처와 `0x0/hidden` 계측은 잘못된 직접 실행점 및 전역 CSS 규칙이 섞인 상태였다. 전역 숨김 규칙을 좁히고 루트 `app.py`로 재실행한 결과 PBIX host가 visible이 됐다.
- Svelte는 `PowerBIReport`의 SDK `error` 상태를 부모 상세 페이지로 전달하고, 저장된 `power_bi_url`이 있으면 `.dashboard-frame` fallback으로 전환하도록 보강했다. URL이 없을 때만 오류 패널을 유지한다.
- 이 fallback은 외부 `app.powerbi.com` 프레임 요청을 차단한 Playwright 재현 테스트로 확인했다. 데스크톱·모바일 모두 `powerBIShell=false`, `fallbackFrame=true`, 수평 overflow 0이었고 산출물은 `artifacts/playwright/test-results/authenticated-routes-authe-424ce--Power-BI-frame-errors-auth-{desktop,mobile}/`에 있다.

## 외부 iframe fixture 추가 증거

- 비-PBIX 공개 fixture `eaa667f4-23d2-4720-b2bc-ea4bc1ac3da2`를 원본 정식 진입점 `app.py`와 Svelte에서 각각 캡처했다. 원본은 `app.py` 기준 외부 대시보드 iframe이 desktop `1208x520`, mobile `424x520`으로 보였고, Svelte도 desktop·mobile 모두 실제 Data Studio 화면 픽셀이 표시됐다.
- 원본의 전역 `iframe[title="st.iframe"]:not([src])` 숨김 규칙은 `components.html()` 정상 iframe까지 숨길 수 있어, 실제 `height=0` 속성/스타일을 가진 스크립트 전용 iframe만 대상으로 좁혔다. 수정 후 원본 진단에서 대시보드 컴포넌트 host가 visible이 됐다.
- 이 비교의 산출물은 [external-dashboard-fixture-20260828](../artifacts/ui-parity/external-dashboard-fixture-20260828/)이다. Streamlit 모바일 결과 이미지가 브라우저 최소 폭 때문에 `500px`로 생성되어 Svelte `390px`와의 픽셀 parity는 `partial`로 두고, 콘텐츠 표시 기능은 `pass`로 분리한다.

## 이번 재검토에서 확인된 수정 사항

- 마이페이지 프로젝트 카드의 태그와 metrics가 흰 배경에서 사라지던 문제를 원본 색상 계열과 muted 텍스트로 조정했다.
- 마이페이지 `프로필 편집` 버튼이 중앙에 놓이던 문제를 프로필 패널 우측 정렬로 조정했다.
- 알림과 댓글 날짜를 원본 기준인 `YYYY-MM-DD HH:mm`으로 맞췄다.
- 상세 대시보드는 URL이 존재하면 iframe을 렌더링할 수 있도록 조건을 확인했다.
- Power BI SDK 임베드에는 loaded/rendered 상태를 DOM 속성으로 노출하고, 직접 dashboard iframe은 전용 요소 캡처로 실제 콘텐츠 표시를 확인하도록 검증 경로를 보강했다.
- 모바일 Power BI SDK iframe이 `420px` shell 안에서 `154px`로 축소되던 문제를 `.powerbi-report`와 삽입 iframe의 최소 높이 보정으로 수정했다. 최신 동일 fixture 캡처에서 데스크톱 shell/report `642/640px`, 모바일 `648.39/646.39px`, iframe `318x640`, overflow `0`을 확인했다. 원본 인증 host `1192x640`/`424x640`과 비교해 host 높이·조작 영역 확보는 `pass`다.
- 댓글 액션과 날짜를 `comment-footer` 한 행으로 묶어 모바일에서도 삭제 확인 상태의 버튼이 날짜를 침범하지 않도록 조정했다.
- 댓글 상호작용 테스트에서 처음에는 페이지 상단 프로젝트 삭제 버튼을 잘못 선택했고, 이후 댓글 카드 범위로 선택자를 제한해 테스트 오판을 제거했다.
- 마이페이지 프로필 편집·프로젝트 삭제 확인 취소, 헤더 알림 팝오버 열기·ESC 닫기, 등록 입력 상태 전환을 인증 테스트로 검증했다.
- 알림 읽음 처리·프로젝트 보기와 마이페이지 프로필 저장은 mock 요청으로 side effect 없이 payload·상태·이동을 검증했다.
- 원본 알림은 상태·제목·시간 콘텐츠 행 뒤에 `프로젝트 보기` 버튼이 별도 행으로 배치된다. Svelte가 버튼을 같은 데스크톱 행에 붙이고 모바일 전체 폭으로 확장하던 차이를 `.notification-item` 블록 레이아웃과 우측 자동 여백으로 수정했다. 최신 인증 캡처와 데스크톱·모바일 `6 passed` 회귀에서 위치·폭·수평 overflow를 확인했다.
- 기존 PBIX 교체 실패 시 기존 Embed URL을 먼저 지우지 않도록 수정하고, 게시 실패 mock에서 기존 연결 보존을 검증했다.
- 원본 모바일 hero 규칙을 재대조해 등록 미리보기와 상세 hero 카드가 모바일에서 노출되던 Svelte 예외를 제거했다. 수정 근거는 `folio_app/styles/hero.py:618-626`과 `svelte_app/src/app.css`의 모바일 media query다.
- 수정 후 `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5176`로 핵심 인증 route를 재실행해 8/8 통과했다. 등록 모바일 preview 숨김, 상세 모바일 hero card 숨김, 대표 결과물 iframe 유지와 댓글 9개를 확인했다.
- 등록·상세의 데스크톱·모바일 회귀 검사 4/4에서 모바일 hero 숨김 CSS를 직접 검증했다.
- 상세 fixture 탐색 중 404 후보가 발견됐고, 테스트가 이를 제품 오류로 오판하지 않도록 404 후보 건너뛰기와 댓글 없는 유효 상세 fallback을 추가했다.
- 원본 저장 흐름은 `project_body` 전체 컬럼이 아니라 `problem/dataset/process/insights` 네 개의 HTML 필드로 분해해 저장한다. Svelte의 비변경 수정 저장 테스트에 네 필드가 `<p>` HTML을 유지해 전송되는지 추가했고, 데스크톱·모바일 인증 suite에서 모두 통과했다. 이는 저장 payload 계약의 `pass` 근거이며 실제 DB 저장 후 서식 재진입은 별도다.
- opt-in 실제 서식 persistence 검증은 `svelte_app/scripts/verify-rich-body-persistence.mjs`로 수행했다. 테스트 프로젝트를 snapshot한 뒤 Tiptap에서 `h2`, `ul/li`, `blockquote`, `a[href]`를 입력하고 저장했으며, 상세 페이지와 수정 페이지 재진입에서 구조·텍스트·링크 URL을 데스크톱·모바일 모두 확인했다. 실행 후 원본 본문 필드는 자동 복구했다.

## 검증 결과

- `npm.cmd run check`: 통과, 0 errors / 0 warnings
- `npm.cmd run build`: 통과
- `npm.cmd run test:ui`: 최신 실행에서 비로그인 핵심 라우트 데스크톱·모바일 `8 passed, 2 skipped`; 스킵은 고정 public detail fixture 미설정이다. 최신 4개 라우트 캡처는 `artifacts/playwright/test-results/routes-*`에 생성됐다.
- `npm.cmd run test:ui:auth`: 기본 인증 회귀 suite는 mutation 테스트를 제외하고 실행하며, 스킵 수는 fixture 설정에 따라 달라진다.
- 인증 suite 전체 실행 결과(최신, `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5176`, 유효 `PLAYWRIGHT_PROJECT_ID` 지정): 데스크톱·모바일 합계 `40 passed, 0 skipped`; 공통 헤더 popover, 등록 validation·preview, 수정 기존 상태·저장·상세 이동, PBIX 교체 계약, 유효 상세 fixture, Power BI fallback, 댓글 등록 mock을 포함한다. 실패와 skip은 없었다. 이전 `24 passed, 10 skipped`, `30 passed, 4 skipped`, `34 passed` 결과는 base URL 또는 선택적 fixture 미지정·이전 코드 기준 진단 실행으로 대체한다.
- 실제 서식 persistence 실행: 데스크톱·모바일 모두 `editorHasStructure/detailHasStructure/editHasStructure=true`; h2·목록·인용·`https://example.com/reference` 링크가 상세와 수정 재진입에서 유지됐다. 결과 캡처와 metrics는 [uiux-rich-body-persistence-20260828](../artifacts/uiux-rich-body-persistence-20260828/)에 있다. sanitizer 라이브 주입도 데스크톱·모바일에서 `javascript:` 링크 href 제거, `script` 0개, 안전한 `https` 링크의 `target=_blank`·`rel=noreferrer` 유지를 확인했다.
- 댓글 등록 계약 테스트: 데스크톱·모바일 `2/2` 통과. mock insert payload, trim, 성공 메시지, 목록 refresh, 댓글 수 갱신, 이메일 알림 endpoint 호출을 확인했으며 실제 DB mutation은 발생시키지 않았다.
- PBIX 교체 성공 orchestration 계약 테스트: 데스크톱·모바일 `2/2` 통과. 실제 Power BI Workspace를 변경하지 않고 기존 Embed URL·`supported` 상태 보존, `artifacts/test.pbix` multipart 전달, 성공 응답 후 상세 이동을 확인했다.
- 실제 PBIX 교체 성공 테스트: `PLAYWRIGHT_PBIX_LIVE_PROJECT_ID=7553...`를 지정해 데스크톱·모바일 `2/2` 통과했다. Import 완료 후 상세 `powerBIStatus=ready`, 프로젝트 `published/supported`, `powerbi_reports.import_status=succeeded`, report/dataset/embed URL 존재, 오류 없음까지 토큰 없이 확인했다.
- opt-in `@mutation` 실제 fixture 테스트: 2/2 통과, 한 줄 소개 저장 반영 및 원복(데스크톱·모바일)
- opt-in `@mutation-thumbnail` 실제 fixture 테스트: 2/2 통과, JPG 업로드·상세 표시·auto-cover 복구(데스크톱·모바일)
- opt-in `@mutation-pbix-safe` 테스트: 2/2 통과, 기존 Embed URL 보존·게시 실패 UI 상태(데스크톱·모바일)
- 인증 캡처: [Playwright test-results](../artifacts/playwright/test-results/)
- 전체 라우트·뷰포트별 익명 캡처: [browser-viewport-captures](../artifacts/browser-viewport-captures-2026-08-28T01-56-42-329Z/)
- 핵심 4페이지 시각 비교: [UIUX_FOCUS_CAPTURE_COMPARISON_2026-08-28](UIUX_FOCUS_CAPTURE_COMPARISON_2026-08-28.md), [focus-compare artifacts](../artifacts/ui-parity/focus-compare-20260828/)
- 최신 핵심 인증 캡처는 관리형 서버 포트 `5176` 기준으로 생성했다. Playwright 기본 포트 `5174`와 다르면 `PLAYWRIGHT_BASE_URL`을 명시해야 한다.
- 상세 viewport 회귀: 데스크톱·모바일 `2/2` 통과. 현재 공통 shell 기준 헤더 좌표는 데스크톱·모바일 모두 `top=16px`; 상호작용 후 최상단 복귀를 검증했다.
- 동일 fixture 비로그인 상세 캡처: 원본·Svelte desktop/mobile `2쌍` 생성, 양쪽 댓글 0개. 원본 인증 내부 이동 상세도 desktop/mobile로 추가 생성했다. 비교 산출물은 `artifacts/ui-parity/same-project-detail-20260828`에 있다.
- 정식 루트 `app.py`로 재생성한 PBIX 인증 상세 비교는 `artifacts/ui-parity/same-project-detail-authenticated-20260828/root-entry-pbix-recompare`에 있다. 원본·Svelte 모두 Power BI host와 내부 페이지 탭이 표시됐다.
- 원본 직접 URL 정착 상태 재현 캡처는 `artifacts/ui-parity/same-project-detail-authenticated-20260828/direct-url-repro-settled.png`와 `direct-url-repro-settled-mobile.png` 및 실행 로그의 `target_initial`/`target_settled` 진단을 사용한다. 데스크톱·모바일 모두 초기에는 `hasLogout=false`, 정착 후에는 `hasLogout=true`와 visible host가 확인됐다.
- 동일 fixture Svelte 직접 상세 URL 진입도 데스크톱·모바일 `2/2` 통과했다. 인증 후 상세 구조, Power BI 상태, 댓글 영역, overflow 0을 확인했다.

## 다음 작업 순서

1. 마이페이지는 동일 데이터 기반의 기능 증거는 확보했지만, 원본 고정 데이터와 인증 계정의 카드 수가 달라 최종 시각 parity는 `partial`이다. 다음 비교는 카드 수가 같은 격리 fixture에서 수행한다.
2. 등록/수정 본문의 기능 persistence는 `pass`로 고정한다. 남은 것은 Quill SVG glyph와 Tiptap control의 시각 차이, 그리고 등록/수정 전체 화면의 동일 fixture 캡처 비교다.
3. 상세의 iframe·fallback·액션 순서·댓글 행 밀도 기능은 `pass`로 고정한다. 남은 것은 외부 Power BI 렌더링 차이를 제외한 동일 fixture 시각 비교와 모바일 정보 계층의 `partial` 해소다.
4. 반복 가능한 Workspace 운영 검증은 전용 fixture를 사용하고, 실제 PBIX 교체 테스트는 명시적 opt-in으로만 실행한다.

현재 결론은 마이페이지·알림·등록·상세의 핵심 화면 구조와 주요 인증 상태, 상세 iframe, 댓글 행 밀도 및 답글/삭제 확인 상태 전이, 마이페이지/알림 헤더/등록 입력, 수정 페이지 기존 상태 로드, 알림/프로필 side effect 계약, 텍스트 필드의 실제 저장 반영, 썸네일 실제 업로드·복구, PBIX 실제 교체 성공·실패 경로까지 증거가 확보됐다. 원본 모바일 hero visual 규칙과 Svelte의 등록/상세 예외는 수정 후 5176 기준 재캡처로 확인했다. 그러나 네 페이지 전체의 기능/UIUX 클론이 완료된 상태는 아니며, 동일 fixture 기반 최종 시각 비교는 아직 `partial`, 반복 가능한 격리 Workspace 운영 검증은 별도 과제로 남아 있다.

## 최신 점검 보강

- 마이페이지 인증 캡처는 현재 `5176` 서버에서 데스크톱·모바일 `2 passed`로 재생성했다. 산출물은 `artifacts/playwright/test-results/authenticated-routes-authe-1eb4f-rs-authenticated-state-auth-{desktop,mobile}/my-authenticated.png`다.
- 마이페이지 캡처에서 프로필 편집 위치, 통계 칩, 프로젝트 카드 footer, 보기·수정·삭제 액션, 모바일 hero 숨김을 확인했다. 원본은 1개 프로젝트, Svelte는 2개 프로젝트라 카드 수 기반 픽셀 비교는 `partial`이다.
- 프로필 편집 취소 및 프로젝트 삭제 확인 모달 취소는 데스크톱·모바일 `2 passed`이며, 산출물은 `artifacts/playwright/test-results/authenticated-routes-authe-fae12--dialogs-cancel-safely-auth-{desktop,mobile}/my-interactions.png`다. 실제 mutation은 발생시키지 않았다.
- sanitizer 라이브 검증은 `svelte_app/scripts/verify-project-body-sanitizer.mjs`로 수행했다. snapshot 후 `javascript:` 링크와 `<script>`를 주입하고 상세 DOM을 데스크톱·모바일에서 확인한 결과 위험 링크 href 제거, script 0개, 실행 플래그 미발생, 정상 `https` 링크·`target=_blank`·`rel=noreferrer` 유지가 모두 통과했다. 테스트 후 원본문은 자동 복구했다. 결과는 [uiux-project-body-sanitizer-20260828](../artifacts/uiux-project-body-sanitizer-20260828/)에 있다.
- 알림 최신 인증 검증은 현재 `5176` 서버에서 데스크톱·모바일 `8 passed`다. 목록 렌더링, 상태·제목·날짜, 별도 행의 프로젝트 보기, 헤더 팝오버 열기/닫기, 모두 읽음, 프로젝트 이동 및 읽음 처리까지 확인했다. 캡처는 `artifacts/playwright/test-results/authenticated-routes-authe-eb0dd-rs-authenticated-state-auth-{desktop,mobile}/notifications-authenticated.png`와 `authenticated-routes-authe-47b74-pover-opens-and-closes-auth-{desktop,mobile}/notification-popover.png`다.
- 알림의 기능·반응형 정보 계층은 `pass`다. 데스크톱 시각 비교에서 원본의 인셋 헤더·제한 폭과 Svelte의 넓은 outer content가 다른 점은 남아 있어 전체 UIUX 판정은 `partial`로 유지한다.

## 자동 커버 변형 규칙 재검증

- 원본 `folio_app/components/ui.py:_cover_variant`는 프로젝트 ID 또는 제목을 UTF-8로 인코딩한 SHA-256 digest의 앞 2바이트를 읽어 24개 변형으로 나눈다.
- Svelte의 기존 `ProjectCard.svelte`는 FNV-1a 계열 해시를 사용해 같은 프로젝트도 다른 색상 변형을 선택할 수 있었다. 이 구현은 원본과의 시각 비교 근거로 부적합해 제거했다.
- `svelte_app/src/lib/cover.ts`에 원본과 동일한 동기 SHA-256 계산을 추가하고 `ProjectCard.svelte`에서 공용으로 사용하도록 수정했다. 등록 기본 미리보기 키 `submit-preview`는 원본과 동일하게 `folio-auto-cover-18`을 선택한다.
- `authenticated-routes.spec.ts`의 등록 상태 테스트가 desktop/mobile에서 변형 클래스와 변형 18의 계산 CSS(`rgb(163, 95, 183)`)를 모두 검증한다. 결과는 `2 passed`다.
- 기본 상태 캡처는 `artifacts/playwright/test-results/authenticated-routes-authe-d55a8-eview-and-draft-states-auth-{desktop,mobile}/submit-empty-baseline.png`에 저장했다. 입력·썸네일 전환 후 상태인 `submit-controls.png`와 섞지 않고 원본 `desktop-submit.png`/`mobile-submit.png`와 비교한다.
- `npm.cmd run check`는 0 errors/0 warnings, `npm.cmd run build`는 통과했다. 이 수정은 자동 커버 선택 규칙의 parity를 보강한 것이며, 등록 페이지 전체 UIUX parity 완료를 의미하지 않는다.

## 등록 폼 라벨·도움말 재검증

- 원본 `folio_app/components/project_form.py`는 제목·한 줄 소개·태그·Embed Code 입력에 도움말을 연결하고, 태그 라벨에는 현재 플랫폼 기준 미리보기 태그를 표시한다.
- Svelte `ProjectFormOverview.svelte`에 입력별 키보드 접근 가능한 `?` 도움말 버튼과 native tooltip을 추가했다. 태그 라벨도 플랫폼 변경에 따라 `태그`/`태그 #Power BI` 형태로 갱신된다.
- 등록 인증 테스트가 desktop/mobile에서 제목 도움말의 48자 안내, 기본 태그 라벨, Power BI 선택 후 `#Power BI` 라벨을 확인했다. 결과는 `2 passed`다.
- 최신 기본 등록 캡처는 `submit-empty-baseline.png`로 저장했으며, 원본 초기 등록 캡처와 입력 전환 후 캡처를 구분해 비교한다.

## 등록·수정 오류 상태 접근성 재검증

- 원본은 프로젝트 검증 실패 시 `처리 결과` 오류 영역을 폼 상단에 유지하고, 필수값·URL·PBIX·썸네일 조건을 통과시키지 않는다.
- Svelte 등록·수정 폼의 오류 영역에 `role="alert"`와 `aria-live="assertive"`를 부여해 오류가 발생하면 보조기술에도 즉시 전달되도록 했다.
- 등록 인증 테스트는 빈 제목, 잘못된 GitHub URL, 잘못된 썸네일 URL, 캡처 입력 소스 부족, 이미지 미선택을 각각 검증했다. 각 오류 후 입력 폼은 유지됐고 프로젝트 POST는 0회였다. desktop/mobile `2 passed`.
- 현재 증거는 등록 페이지의 client-side 차단 상태 기준이다. 실제 Supabase 오류 응답이나 수정 페이지의 각 오류 조합은 기존 PBIX 실패 안전성 테스트와 별도 fixture 검증으로 분리한다.

## 공통 헤더 popover 재검증

- 원본 `folio_app/components/layout.py`는 Power BI 메뉴와 로그인 사용자 알림을 클릭형 `st.popover`로 렌더링하며, Power BI 항목에는 하위 콘텐츠 이동 메뉴를 포함한다.
- Svelte `AuthNav.svelte`의 Power BI 메뉴를 hover 의존 서브메뉴에서 `aria-expanded`를 가진 명시적 버튼 popover로 전환했다. 알림 버튼에는 펼침 상태를 나타내는 caret을 추가했고, 두 메뉴는 바깥 클릭·Escape로 닫힌다.
- Playwright 인증 테스트가 알림과 Power BI popover의 닫힘→열림→Escape 닫힘, 하위 메뉴 콘텐츠 표시를 desktop/mobile에서 확인했다. 합계 `4 passed`.
- 메뉴 기능 parity는 `pass`다. 헤더의 desktop 외곽 inset/폭은 공통 shell 시각 차이로 별도 `partial` 판정을 유지한다.

## 공통 헤더 시각 판정 보강

- 원본 캡처의 desktop 헤더는 본문과 같은 제한 폭의 인셋 컨테이너 안에 있고, Power BI와 알림에 펼침 상태를 나타내는 affordance가 있다.
- Svelte의 Power BI trigger·알림 caret·popover 동작은 원본의 기능 흐름과 일치하도록 보완했다. 다만 Svelte `.site-header-inner`는 현재 더 넓은 `max-width`와 outer padding을 사용하므로, 헤더 외곽 폭과 본문 인셋의 픽셀 parity는 `partial`이다.
- 이 차이는 전체 페이지 밀도 조정보다 영향 범위가 크므로, 4개 핵심 페이지의 동일 fixture 최종 캡처를 기준으로 공통 shell 값을 한 번에 조정한다.

## 수정 페이지 조건부 제어 재검증

- 원본 `folio_app/components/project_form.py`는 기존 Power BI 게시본이 있을 때 연결 삭제 체크박스를 보여주고, 삭제를 선택한 경우에만 PBIX 업로드 입력을 연다. 기존 썸네일도 삭제를 선택한 경우에만 새 이미지 업로드 입력을 연다.
- Svelte `ProjectFormOverview.svelte`의 `hasPowerbiReport`, `delete_pbix`, `hasExistingThumbnail`, `delete_thumbnail` 조건을 실제 수정 화면에 적용하고 있다.
- 수정 상태 Playwright 테스트는 desktop/mobile에서 기존 제목·본문·미리보기·hero 카피를 확인한 뒤, PBIX 삭제 체크의 업로드 입력 표시/해제 복원 흐름을 검증한다. 썸네일 보유 fixture에서는 삭제 체크 후 이미지 입력 표시와 해제 복원까지 조건부로 검증한다. 결과는 `2 passed`다.
- 수정 hero 카피도 원본 코드의 `프로젝트 정보와 대표 썸네일을 업데이트하세요.`로 맞췄다. 전체 수정 저장 parity는 실제 fixture mutation 테스트와 분리해 판정한다.

## 수정 저장·상세 접근 조건 재검증

- 원본 `folio_app/services/project_queries.py:get_project`는 상세 RPC가 비어도 프로젝트 테이블을 다시 조회하고, 소유자 RLS가 본인 프로젝트를 읽을 수 있게 한다. Svelte fallback이 `is_public = true`를 다시 강제하면 마이페이지에서 수정한 비공개 프로젝트의 상세 이동이 404가 될 수 있었다.
- `svelte_app/src/lib/projects.ts:loadProjectDetail`에서 fallback의 공개 필터를 제거하고, table 조회 직전에 `currentSession()`을 기다리도록 수정했다. 공개 프로젝트는 기존 공개 RLS가 보호한다. 다만 상세 route가 `+page.server.ts`를 사용하고 현재 인증 세션이 localStorage 기반이므로, 작성자 비공개 상세의 직접 진입은 아직 별도 검증 대상이다.
- 인증 전체 회귀는 실행 서버 `5176`과 유효 fixture를 명시한 최신 `npm.cmd run test:ui:auth`에서 `36 passed, 0 skipped`로 통과했다. 저장 payload의 네 HTML 섹션, PBIX multipart 요청, 알림·Power BI popover, 등록 validation, 유효 상세 hero, Power BI frame fallback, populated 댓글, 댓글 등록 mock을 desktop/mobile에서 모두 확인했다.
- 저장 직후 상세 hero와 상세 상호작용은 현재 유효한 공개 fixture에서 desktop/mobile 모두 확인됐다.

## Playwright 실행 대상 정정

- `svelte_app/playwright.config.ts`의 기본 `baseURL`은 `http://127.0.0.1:5174`이고, 현재 관리형 Vite 서버는 포트 충돌로 `http://127.0.0.1:5176`에서 실행 중이었다.
- `5174`를 대상으로 실행한 이전 인증 결과의 상세 404는 제품 증거로 사용할 수 없는 환경 오판이었다. `cmd /d /s /c "set PLAYWRIGHT_BASE_URL=http://127.0.0.1:5176&& set PLAYWRIGHT_PROJECT_ID=...&& npm.cmd run test:ui:auth"`로 재실행한 결과는 desktop/mobile `36 passed, 0 skipped`다. 실제 fixture ID는 로그나 문서에 비밀값과 함께 기록하지 않고 테스트 환경에서만 주입한다.
- 앞으로 캡처·Playwright·DOM 결과에는 실제 서버 URL을 함께 기록하고, base URL이 다르면 `PLAYWRIGHT_BASE_URL`을 명시한다.

## 공통 shell 시각 parity 재검증

- 원본 `folio_app/styles/streamlit_overrides.py`와 `folio_app/styles/header.py`는 헤더를 `margin-top: 16px`, `min-height: 64px`, 둥근 모서리와 그림자가 있는 독립 영역으로 렌더링한다. 원본 캡처에서도 헤더와 본문이 같은 중앙 제한 폭 안에 놓인다.
- 기존 Svelte는 데스크톱에서 `.site-header` 배경이 viewport 전체 폭을 차지하고, `.page-shell`과 `.site-footer`도 `1440px` 기준으로 더 넓게 배치되어 있었다. 이 차이는 4개 핵심 페이지에 반복됐다.
- `svelte_app/src/app.css`를 다음처럼 조정했다.
  - `.site-header`: `max-width: 1254px`, `margin-top: 16px`, 둥근 모서리와 원본 계열 그림자
  - `.site-header-inner`: 독립 header 내부 여백과 원본에 맞춘 데스크톱 내비게이션 `14px`
  - `.page-shell`, `.site-footer`: 내부 콘텐츠 폭이 `1254px`가 되도록 `1310px` outer max-width
  - `.page-shell` desktop top padding: `20px`로 조정해 헤더 하단에서 첫 hero까지의 간격을 원본에 맞춤
- 모바일 전용 header margin, 세로 내비게이션, page padding 규칙은 기존 media query를 유지했다.
- 변경 후 실제 인증 캡처 `my-authenticated.png`, `notifications-authenticated.png`, `submit-authenticated.png`, `detail-authenticated.png`를 desktop/mobile로 재생성했다. 핵심 캡처 테스트 `renders`는 `8 passed`였고, 상세 유효 fixture 회귀는 헤더 좌표 기준 수정 후 desktop/mobile `4 passed`였다.
- 현재 판정: 공통 shell의 desktop 외곽 폭·상단 inset은 `pass`로 상향할 수 있는 근거가 생겼다. 다만 원본과 인증 계정의 데이터·viewport 상태가 다른 페이지 전체 픽셀 parity는 여전히 `partial`이며, 동일 fixture 기반의 각 페이지 최종 시각 판정은 별도 표로 유지한다.

## 2026-08-29 상세 액션 순서 보강

- 원본 상세 footer의 액션 순서는 `folio_app/pages/project_detail.py:_render_hero_footer_actions` 기준 공유·좋아요·신고/수정/삭제다. 원본 공유 버튼은 `folio_app/components/share.py`에서 Clipboard API 실패 시 textarea fallback을 사용한다.
- Svelte `projects/[id]/+page.svelte`는 좋아요를 공유·수정/삭제와 같은 `.detail-action-group` 안으로 이동했고, 공유 복사에 동일한 fallback 경로를 추가했다. 모바일에서도 같은 DOM 순서를 유지한다.
- 동일 fixture 상세 회귀는 desktop/mobile 합계 `6 passed`였고, 최신 `detail-viewport.png`에서 원본과 동일한 액션 순서를 확인했다. 기능/UIUX 판정은 `pass`; 전체 페이지 픽셀 parity는 데이터 및 외부 Power BI 렌더링 차이 때문에 기존처럼 `partial`이다.

## 2026-08-29 등록 에디터 기본 서식 증거 보강

| 영역 | 원본 코드 근거 | 원본 캡처 근거 | Svelte 코드 근거 | Svelte DOM/캡처 근거 | 판정 |
| --- | --- | --- | --- | --- | --- |
| 블록 heading | `streamlit_quill/__init__.py` 기본 toolbar의 `header: [1,2,3,4,5,6,False]` | `artifacts/ui-parity/streamlit/desktop-submit.png`의 Quill header control | `ProjectBodyEditor.svelte`의 `BlockFormat`, StarterKit heading levels `[1,2,3,4,5,6]` | 등록 표적 테스트에서 H6 선택 후 heading DOM 확인, desktop/mobile `2 passed` | pass |
| 글자 크기 | 기본 toolbar의 `size: [small,False,large,huge]` | 원본 등록 toolbar의 size control | `ProjectBodyEditor.svelte`의 size select와 `format.ts` safe font-size whitelist | `1.5em` span style을 desktop/mobile에서 확인, `2 passed` | pass |
| 들여쓰기 | 기본 toolbar의 `indent: -1/+1` | 원본 등록 toolbar의 indent controls | `BlockIndent` extension, `data-indent` 0~6, `changeIndent()` | 들여쓰기 `data-indent="1"` 생성과 내어쓰기 복원을 desktop/mobile에서 확인 | pass |
| toolbar 시각 | 원본 Quill 기본 toolbar 그룹 구조 | 원본 desktop/mobile 등록 캡처 | Tiptap toolbar 그룹 및 compact labels | `submit-controls.png`에서 desktop 단일 행 중심, mobile 다중 행 접힘 확인 | partial |

- 이번 단계에서 확인한 원본 범위는 `folio_app/components/project_body.py`가 기본 `st_quill`을 호출한다는 사실과 `streamlit_quill` 패키지의 기본 toolbar 설정을 함께 근거로 삼았다. Svelte의 이미지 파일 업로드·Storage public URL·inline math는 원본 toolbar와의 동일성 주장이 아니라 기능 보강이다.
- `npm.cmd run check`: 0 errors / 0 warnings. `npm.cmd run build`: 통과.
- 결론: 등록 에디터의 기능적 서식 범위는 원본 기본 toolbar에 대응했지만, Quill/Tiptap의 아이콘·세부 spacing·그룹 표현은 아직 시각 비교 대상이다. 등록 페이지 전체 판정은 기존처럼 `partial`로 유지한다.

### 수정 화면 서식 컨트롤 증거

| 영역 | 원본 코드 근거 | 원본 캡처 근거 | Svelte 코드 근거 | Svelte DOM/캡처 근거 | 판정 |
| --- | --- | --- | --- | --- | --- |
| 등록/수정 공용 editor | `project_body.py`의 `render_project_body_editor`와 기본 `st_quill` 호출 | `desktop-submit.png`의 본문 editor 진입 | `projects/[id]/edit/+page.svelte`가 등록과 동일한 `ProjectBodyEditor` 사용 | 인증 수정 화면에서 기존 본문 h2 4개와 hero preview 로드 확인 | pass |
| 수정 서식 범위 | 기본 toolbar header `[1..6]`, size `[small,False,large,huge]` | 원본 Quill toolbar | `ProjectBodyEditor.svelte` H1~H6·size select | 수정 화면 H6 전환, size options, 기존 h2 선택 desktop/mobile `2 passed` | pass |

- 수정 페이지 검증은 저장 mutation을 수행하지 않는 실제 인증 UI 상태 검사다. 따라서 “수정 화면에서 컨트롤이 로드되고 기존 본문과 연결됨”은 `pass`, 수정 저장 후 새 서식의 DB 재진입은 별도 persistence 증거로 분리한다.

### 2026-08-29 수정 저장 서식 persistence 증거

| 영역 | 원본 코드 근거 | 원본 캡처 근거 | Svelte 코드 근거 | Svelte DOM/캡처 근거 | 판정 |
| --- | --- | --- | --- | --- | --- |
| H6·글자 크기·들여쓰기 저장 | 원본 기본 toolbar의 header `[1..6]`, size, indent 설정 | 원본 Quill 등록 editor toolbar | `ProjectBodyEditor.svelte`, `format.ts` H1~H6/size/indent 보존 | editor·상세·수정 재진입에서 H6 text, `1.5em`, `data-indent="1"` 일치 | pass |
| 수정 저장 재진입 | `project_body.py`의 섹션별 HTML 저장/파싱 구조 | 원본 등록·수정 화면의 본문 editor 흐름 | `edit/+page.svelte`의 `syncProjectBodyInput`과 `updateProject` | `verify-rich-body-persistence.mjs` desktop/mobile 모두 `editorHasStructure/detailHasStructure/editHasStructure=true` | pass |
| 위험/확장 콘텐츠 보존 | 원본 sanitizer는 허용 tag subset만 보존 | 원본 Quill 본문 표시 | Svelte sanitizer의 safe style/image/math 및 H6 허용 | 목록·인용·링크·mark·이미지·수식과 H6 shape 확인 | pass |

- 검증 도중 H6가 Svelte sanitizer 허용 목록에서 빠져 상세 표시에서 제거되는 결함을 발견했고 `format.ts`에 H6를 추가했다. 또한 단일 커서 들여쓰기 대상 계산을 수정했다.
- 실제 테스트 fixture를 snapshot한 뒤 저장하고, desktop/mobile 각각 상세·수정 재진입을 확인한 후 원본문을 자동 복구했다. 새 산출물은 [uiux-rich-body-persistence-20260829](../artifacts/uiux-rich-body-persistence-20260829/)다.
- 기능 persistence 판정은 `pass`지만, Quill/Tiptap의 HTML 표현과 toolbar 시각은 서로 달라 전체 등록/수정 UIUX parity는 여전히 `partial`이다.

### 2026-08-29 toolbar 그룹 순서 증거

| 영역 | 원본 코드 근거 | 원본 캡처 근거 | Svelte 코드 근거 | Svelte DOM/캡처 근거 | 판정 |
| --- | --- | --- | --- | --- | --- |
| toolbar 그룹 순서 | `streamlit_quill/__init__.py` 기본 toolbar 7개 배열 | 원본 등록 editor toolbar | `ProjectBodyEditor.svelte`의 그룹 DOM: 글자→색상→목록/정렬→문단/크기→고급→링크/이미지→글꼴 | desktop/mobile `submit-controls.png`와 인증 회귀 `4 passed` | pass |
| 반응형 접힘 | 원본 등록 toolbar의 mobile 캡처 | `mobile-submit.png` | `app.css`의 toolbar group wrap 규칙 | mobile에서 그룹 순서를 유지한 다중 행 렌더링, overflow 없음 | pass |
| 시각 glyph/border | Quill 기본 icon control | 원본 toolbar 캡처 | Tiptap compact labels와 CSS pseudo glyph | 기능은 대응하지만 glyph·border·hover는 별도 스타일 | partial |

- 이 단계는 toolbar DOM 순서를 원본 배열과 맞춘 것이다. 전체 등록 페이지의 높이·카드 데이터·에디터 내부 렌더링까지 동일하다고 판정하지 않는다.

### 2026-08-29 Quill Snow control 스타일 증거

| 영역 | 원본 코드 근거 | 원본 캡처 근거 | Svelte 코드 근거 | Svelte DOM/캡처 근거 | 판정 |
| --- | --- | --- | --- | --- | --- |
| 버튼 control box | `quill.snow.css`의 `border:none`, `height:24px`, `width:28px`, `padding:3px 5px` | 원본 등록 toolbar의 compact icon buttons | `app.css` `.rich-editor-toolbar button` | computed `border-style:none`, `height:24px` assertion desktop/mobile `2 passed` | pass |
| hover/active | Quill Snow hover/focus/active `color:#06c` | 원본 toolbar active affordance | `app.css` hover/focus/active blue state | hover computed color `rgb(20, 89, 200)` desktop/mobile `2 passed` | pass |
| icon glyph | Quill inline SVG icons | 원본 toolbar icon shape | Svelte accessible text + CSS pseudo glyph | 기능·대체 텍스트는 대응하지만 glyph shape는 다름 | partial |

- 이번 단계는 Quill CSS의 실제 로컬 패키지 자산을 기준으로 Svelte toolbar의 box model과 상태 색상을 조정한 것이다. Quill SVG 자산을 그대로 복제하지 않았으므로 아이콘 형태의 pixel parity는 계속 `partial`로 기록한다.

### 2026-08-29 전체 인증 UI 회귀 재검증

- `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5176`과 유효한 `PLAYWRIGHT_PROJECT_ID`를 지정해 `npm.cmd run test:ui:auth -- --project=desktop --project=mobile`을 실행했다.
- 데스크톱·모바일 합계 `40 passed, 0 skipped`였다. 마이페이지·알림·등록·수정·상세 렌더링, 헤더 알림 popover, 등록 validation/preview, 수정 기존 상태·저장 계약, PBIX 교체 계약, 상세 iframe/fallback, 댓글 mock과 상태 전이를 포함한다.
- 이번 실행은 `@mutation`을 제외한 인증 UI 회귀 suite이며, 실제 PBIX/Storage 변경을 발생시키지 않는다. 실제 fixture mutation 검증은 별도 opt-in 스크립트의 snapshot·복구 증거를 사용한다.
- `npm.cmd run check`도 재실행해 `0 errors / 0 warnings`를 확인했다. `git diff --check`는 오류 없이 줄바꿈 형식 경고만 출력했다.
- 판정: 현재 기능 회귀·인증 상태 전이는 `pass`. 동일 fixture 기반 전체 화면의 픽셀 parity와 Quill SVG glyph 및 Tiptap glyph의 차이는 여전히 `partial`이다.

### 2026-08-29 toolbar SVG glyph 및 알림 race 보강

- `RichEditorIcon.svelte`를 추가해 등록·수정 toolbar의 텍스트/pseudo glyph를 실제 inline SVG icon DOM으로 교체했다. 버튼의 `aria-label`과 title은 유지해 기능 및 접근성 계약을 보존했다.
- desktop/mobile `submit-controls.png`에서 toolbar는 desktop compact 단일 행, mobile 그룹 순서를 유지한 wrapping으로 표시되고, 아이콘 겹침·수평 overflow는 확인되지 않았다.
- 로그인 직후 헤더 알림의 비동기 초기 로드가 mock보다 먼저 끝날 수 있던 회귀 테스트 race를 수정했다. mock route 설치 후 인증 페이지를 재로드해 알림 ID를 결정적으로 고정한다.
- 표적 알림 이동 테스트 desktop/mobile `2 passed`, 전체 인증 suite desktop/mobile `40 passed`로 재검증했다.
- 판정: toolbar control 구조·접근성·반응형 배치 `pass`; 원본 Quill SVG와의 path-level 동일성은 아이콘 설계 차이로 `partial`이다.

### 2026-08-29 모바일 헤더 밀도 보강

- 원본 모바일 인증 캡처의 헤더는 브랜드와 네비게이션이 짧은 2행으로 배치되며, 페이지 hero가 헤더 바로 아래에서 시작한다. 기존 Svelte는 header inner padding, brand height, nav gap 때문에 헤더가 과도하게 높았다.
- `svelte_app/src/app.css`의 모바일 breakpoint에서 header margin/padding, brand image height, nav gap/font/line-height를 함께 조정했다. 네비게이션의 2행 wrapping과 active 상태는 유지했다.
- 최신 mobile `my-authenticated.png`에서 헤더 높이와 hero 시작 위치가 축소되고, nav 텍스트·active underline·프로필/프로젝트 목록이 겹치지 않는 것을 확인했다. desktop은 같은 규칙의 영향을 받지 않는다.
- 이번 묶음의 desktop/mobile my·notifications·submit 인증 렌더 테스트는 `6 passed`였다.
- 판정: 모바일 헤더 정보 밀도·반응형 구조 `pass`; 원본과의 font rasterization 및 전체 데이터 상태 차이는 페이지 전체 픽셀 parity에서 별도 `partial`로 유지한다.

### 2026-08-29 마이페이지 관리 액션 스타일 보강

- 원본 `folio_app/pages/protected.py`의 프로젝트 관리 영역은 `보기`, `수정`, `삭제`를 모두 기본 `st.button`으로 렌더링한다. 삭제 확인 대화상자에서만 삭제 경고 스타일을 사용한다.
- Svelte 관리 카드에서만 삭제 버튼을 빨간색으로 강조하던 차이를 제거하고, 카드의 세 액션을 동일한 outline 스타일로 맞췄다. 삭제 확인 모달의 danger 버튼은 그대로 유지했다.
- populated 카드와 프로필/삭제 취소 흐름을 desktop/mobile에서 묶어 `4 passed`로 검증했다.
- 판정: 마이페이지 관리 액션의 정보 위계·상태 전이 `pass`. 원본 1개 프로젝트와 인증 계정 2개 프로젝트의 데이터 수 차이로 전체 페이지 픽셀 parity는 `partial`이다.

### 2026-08-29 등록·수정 화면 최종 캡처 대조

- 최신 Svelte 등록 상태는 `submit-authenticated.png`, 수정 기존 상태는 `edit-existing-state.png`로 desktop/mobile을 재생성해 원본 `desktop-submit.png`와 `mobile-submit.png`에 대조했다.
- 등록 화면은 hero preview, 기본 정보·산출물 링크 2열, 플랫폼/썸네일 선택, 본문 editor와 저장 액션의 구조·상태 반영을 유지한다. 모바일에서는 1열 전환과 editor toolbar wrapping을 확인했다.
- 수정 화면은 기존 제목·본문·Power BI 연결·썸네일 삭제 옵션·공개 설정을 로드하고 같은 editor를 재사용한다. 다만 로컬에 남은 원본 `desktop-edit-query.png`/`mobile-edit-query.png`는 수정 폼이 아니라 마이페이지 상태이므로 수정 화면의 동일 캡처 근거로 사용하지 않는다.
- 데이터·viewport·외부 iframe 상태가 다른 캡처를 억지로 픽셀 기준으로 맞추지 않고, 이번 묶음에서는 확인 가능한 액션 스타일만 수정했다. 등록/수정 전체 시각 parity는 `partial`로 유지한다.
- 등록 렌더·수정 기존 상태 desktop/mobile 합계 `8 passed`로 재검증했다.

### 2026-08-29 원본 수정 화면 재캡처 및 Hero 정정

- 이전 `artifacts/ui-parity/streamlit/desktop-edit-query.png`와 `mobile-edit-query.png`는 폐기된 `edit_project` query parameter를 사용해 수정 폼이 아닌 마이페이지 상태를 캡처한 산출물이었다.
- 원본 코드 `folio_app/navigation.py`와 `folio_app/pages/protected.py`의 실제 파라미터 `edit_project_id` 및 마이페이지의 `수정` 버튼 진입을 기준으로 캡처 도구에 `--via-my-page-edit` 경로를 추가했다.
- 테스트 사용자의 실제 소유 프로젝트를 마이페이지에서 직접 수정 진입시켜 다음 유효 캡처를 생성했다.
  - `artifacts/ui-parity/streamlit/original-edit-owner-20260829.png`
  - `artifacts/ui-parity/streamlit/original-edit-owner-mobile-20260829.png`
- 원본 재캡처에서 수정 Hero는 `EDIT`/`프로젝트 수정`/설명과 프로젝트 카드만 포함하고, 공개·플랫폼·최근 수정 상태 칩은 포함하지 않는 것으로 확인했다.
- Svelte `projects/[id]/edit/+page.svelte`의 추가 상태 칩 행을 제거하고, 원본과 같은 Hero 정보 계층을 복원했다. 기존 입력값, 썸네일/Power BI 삭제 조건부 UI, 본문 editor, 공개 설정과 저장 액션은 변경하지 않았다.
- 수정 페이지 실제 인증 검증 `edit page loads existing project state without mutation`은 `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5176`에서 desktop/mobile `2 passed`다. `npm.cmd run check`는 0 errors / 0 warnings다.
- 판정: 수정 Hero의 정보 계층 `pass`; 원본·Svelte가 서로 다른 프로젝트 데이터와 Tiptap/Quill toolbar 표현을 사용하는 전체 픽셀 parity는 계속 `partial`이다.

### 2026-08-29 상세 페이지 iframe·댓글 최종 재검증

- 원본 상세 근거는 `folio_app/pages/project_detail.py`, `folio_app/components/project_detail_content.py`, `folio_app/components/project_comments.py`와 `artifacts/ui-parity/streamlit/desktop-detail-known.png`, `mobile-detail-known.png`를 사용했다.
- 원본은 프로젝트 상태에 따라 Power BI embedded viewer 또는 외부 대시보드 iframe/fallback을 렌더링하고, 대표 결과물 아래 대시보드·보고서·GitHub 링크를 조건부로 노출한다.
- Svelte `projects/[id]/+page.svelte`는 실제 인증 fixture에서 `PowerBIReport` iframe이 `ready` 상태가 되고, 대표 결과물 패널·리포트·리소스 링크를 렌더링했다. 고정 fixture `7553d519-b395-464a-bd57-3b33100e2df1` 기준 상세 검증은 desktop/mobile `2 passed`다.
- 최신 Svelte 산출물은 `artifacts/playwright/test-results/authenticated-routes-authe-56031--valid-project-fixture-auth-{desktop,mobile}/detail-authenticated.png`와 `detail-authenticated-metrics.json`이다. 두 viewport 모두 가로 overflow가 없고, desktop Power BI shell 약 642px, mobile 약 648px의 실제 iframe geometry가 확인됐다.
- 상세 테스트를 fixture 없이 실행했을 때 임의 프로젝트의 오래된 날짜·최근 활동 상태를 고정 기대해 1건 오탐했다. 테스트를 `detailProjectId` 지정 여부에 따라 고정 fixture assertion과 실데이터 구조 assertion으로 분리했고, fixture 미지정 desktop/mobile도 `2 passed`로 통과했다.
- 댓글은 원본 `project_comments.py`의 날짜와 답글/삭제 액션 구조, Svelte `ProjectComments.svelte`의 compact footer를 populated fixture로 검증했다. 날짜와 액션 중심선 오차 8px 이내, 답글 열기·취소, 삭제 확인·취소가 desktop/mobile `2 passed`다.
- 판정: iframe 실제 렌더링·fallback 분기·리소스 링크·댓글 액션/밀도 기능은 `pass`. 원본 캡처와 최신 Svelte는 서로 다른 프로젝트/댓글 수와 외부 Power BI 콘텐츠를 사용하므로 전체 픽셀 parity는 `partial`이다.

### 2026-08-29 마일스톤 종료 검증

- 최신 수정 이후 `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5176`, 유효한 상세 fixture를 사용해 `npm.cmd run test:ui:auth -- --project=desktop --project=mobile`을 1회 실행했다.
- 인증 UI 회귀 결과는 desktop/mobile 합계 `40 passed`이며, 마이페이지·알림·등록·수정·상세·iframe fallback·댓글 상태 전이를 포함한다.
- `npm.cmd run check`: `0 errors / 0 warnings`.
- `npm.cmd run build`: SvelteKit Cloudflare production build 성공.
- 이번 마일스톤의 필수 기능 검증은 종료한다. Quill/Tiptap 아이콘 path-level pixel parity와 동일 데이터 기반 전체 오버레이 비교는 기능 blocker가 아닌 선택적 후속 polish로 남긴다.
