# 상세 페이지 UIUX Parity 재감사

이번 재감사는 상세 페이지의 기능과 구조를 원본 코드, 최신 동일 fixture 캡처, Svelte 코드 및 Playwright DOM 기준으로 다시 대조한 기록이다. 원본 인증은 내부 이동과 직접 URL 재진입 모두 정착 후 유지되며, 초기 로딩 셸과 최종 인증 상태를 분리해 판정했다.

| 영역 | 원본 코드 근거 | 원본 캡처 근거 | Svelte 코드 근거 | Svelte DOM/캡처 근거 | 판정 |
| --- | --- | --- | --- | --- | --- |
| 상세 흐름 | `folio_app/pages/project_detail.py:107-123`의 히어로 → 대표 결과물 → 리포트 → 댓글 | `artifacts/ui-parity/same-project-detail-20260828`의 동일 fixture 비로그인 캡처 | `svelte_app/src/routes/projects/[id]/+page.svelte:183-341` | Playwright 동일 fixture 캡처에 동일 섹션 존재 | pass: 구조 기준 |
| 히어로 카드 | `folio_app/pages/project_detail.py:112-114`, `folio_app/components/ui.py:141-160` | `artifacts/uiux-svelte-detail-hero-fix-20260827-170613` 기준 hero preview geometry 기록 | `+page.svelte:183-192`, `ProjectCard.svelte:27-65` | 기존 리포트에 desktop `470x264`, mobile `360x202`, 이미지/제목/요약/footer DOM 기록 | pass |
| processing/failed 대표 결과물 | `project_detail_content.py:20-44`에서 상태 메시지 뒤에도 action 링크 렌더링 | 원본 상세 상태 캡처 | `+page.svelte:274-315`에서 공통 패널과 링크 유지 | 이번 세션 새 브라우저 실측 없음 | partial |
| iframe URL | `project_detail_content.py:47-58`, `project_normalizers.py:170-183`에서 iframe `src` 추출 후 렌더링 | iframe 상태 캡처 및 dashboard breakdown | `projects.ts:747-756`, `+page.svelte:42-67,294-310`에서 동일 정규화 적용 | 기존 live PBIX 실측은 있으나 이번 변경 후 재실측 없음 | partial |
| Power BI iframe | `project_detail_content.py:81-90`, `dashboard.py:95-145` | dashboard iframe 캡처 | `+page.svelte:289-296`, `PowerBIReport.svelte` | 기존 PBIX E2E에서 실제 `reportEmbed` iframe 확인, 새 브라우저 세션은 없음 | partial |
| 리포트 카드 | `project_detail_content.py:113-135`의 단일 `프로젝트 리포트` 카드와 익명 섹션 | 동일 프로젝트 캡처 | `+page.svelte:318-327` | 기존 report selector 및 body text 기록 | pass |
| 댓글 dense row | `project_comments.py:182-230`, `detail_comments.py:293-299`의 index/author/body/date/actions 행 | 댓글 캡처 | `ProjectComments.svelte:189-227`, `app.css:4731-4853` | 기존 캡처에서 댓글 UI 확인, 이번 세션 새 DOM 없음 | partial |
| 댓글 페이지네이션 | `project_comments.py:37-67,112-134`, 최상위 댓글 20개 기준 | 원본 pagination style | `ProjectComments.svelte:42-52,170-186`에 최상위 트리 20개 기준 구현 | 브라우저 실측 없음 | partial |
| 소유자 액션/삭제·신고 | `project_detail.py:161-204,302-378` | owner/delete/report 캡처 | `+page.svelte:206-269` | 기존 상태 캡처에 modal/actions 기록, 새 세션 없음 | partial |
| 모바일 overflow | 원본 responsive styles와 캡처 | `same-project-detail-20260828` mobile | `app.css` detail mobile rules | Playwright 동일 fixture mobile `scrollWidth=clientWidth=390`; 인증 상세 댓글 fixture도 overflow 0 | pass |

## 이번 수정

- 댓글을 원본처럼 최상위 댓글 20개 단위로 페이지 분리했다. 답글 트리는 해당 최상위 댓글 아래에 유지한다.
- 페이지 번호는 `1`, `2 / N` 형식으로 표시하고, 번호는 페이지 사이에서 이어진다.
- 상세 페이지가 iframe 전체 코드를 저장한 레거시 데이터도 `src` URL로 정규화해 iframe과 대시보드 링크에 사용한다.
- `processing/failed` 상태에서도 대표 결과물 패널과 외부 리소스 링크가 사라지지 않도록 공통 패널 구조로 통합했다.

## 검증 상태

- `npm.cmd run check`: 0 errors, 0 warnings
- `npm.cmd run build`: 통과
- `git diff --check`: CRLF 변환 경고만 확인
- 동일 fixture 비로그인 원본·Svelte 캡처: desktop/mobile 생성
- 인증 Svelte 상세 DOM/캡처: desktop/mobile `2/2` 통과
- 원본 인증 상세는 내부 이동과 직접 URL 재진입에서 로그인·작성자 액션·댓글 입력까지 정착 후 확인했다. 직접 URL 초기 로딩 셸은 최종 상태와 분리했으며, 세션 복원은 `pass`다.

## 다음 실측

1. 직접 URL 인증 복원은 정착 후 정상임을 확인했다. 동일 fixture에서 iframe `src`, 패널 상태, resource links를 양쪽에서 재측정한다.
2. 댓글 21개 이상 fixture에서 `1 / 2`, 이전/다음, root numbering과 reply tree를 확인한다.
3. desktop/mobile overlay로 hero footer, visual panel, report, comments 사이의 실제 간격을 비교한다.
## 수정 페이지 재감사

| 영역 | 원본 근거 | Svelte 근거 | 판정 |
| --- | --- | --- | --- |
| 기존 썸네일 모드 복원 | `folio_app/components/project_editor.py:228-240`는 저장된 `thumbnail_mode`를 유지 | `svelte_app/src/routes/projects/[id]/edit/+page.svelte:266-284`가 `value.thumbnail_mode`를 그대로 복원 | pass |
| 기존 Power BI 게시본 감지 | `project_editor.py:299-305`는 URL 또는 `powerbi_reports` 레코드로 감지 | `svelte_app/src/routes/api/projects/[id]/powerbi-publish/+server.ts` GET과 `svelte_app/src/lib/powerbi-publish.ts`가 소유자 게시본 존재 여부 조회 | pass |
| PBIX 연결 삭제 UI | 원본 `project_form.py:475-495`의 기존 연결 삭제 후 업로드 전환 | `ProjectFormOverview.svelte:62-78`, 수정 페이지의 `hasPowerbiReport` 상태 | partial: 새 브라우저 DOM 미실측 |
| 본문·썸네일·PBIX 저장 순서 | 원본 `project_editor.py:162-207` | `edit/+page.svelte:101-182` | partial: 새 E2E 미실행 |

이번 수정 후 정적 검증은 `npm.cmd run check` 0 errors/0 warnings로 통과했다. 새 브라우저 런타임이 없어 수정 페이지의 실제 상태 전환과 저장 후 상세 반영은 아직 `unknown`이다.
