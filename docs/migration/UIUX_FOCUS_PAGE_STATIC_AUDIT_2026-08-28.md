# 핵심 4개 페이지 정적 대조

작성일: 2026-08-28

범위: 마이페이지, 알림, 프로젝트 등록/수정, 프로젝트 상세.

주의: 이 문서는 2026-08-28 초기 정적 감사 기록이다. 당시 Browser runtime 미연결로 DOM/새 캡처 칸을 `unknown`으로 남겼지만, 이후 Playwright 인증 캡처·DOM·기능 테스트가 추가되었다. 최신 증거와 판정은 `UIUX_CAPTURE_EVIDENCE_REVIEW_2026-08-28.md`와 `UIUX_FOCUS_CAPTURE_COMPARISON_2026-08-28.md`를 기준으로 한다.

## 환경 상태

| 항목 | 결과 |
|---|---|
| Svelte managed server | `127.0.0.1:5174` HTTP 200 |
| 테스트 fixture | `artifacts/test.pbix` 존재 |
| 테스트 계정 key | 존재 여부 확인, 값은 비공개 |
| Browser runtime | 당시 `agent.browsers.list() = []` |
| 새 DOM/캡처 | 당시 blocked, 이후 Playwright 증거로 보강 |

## 증거표

| 영역 | 원본 코드 근거 | Svelte 코드 근거 | 정적 판정 | DOM/캡처 |
|---|---|---|---|---|
| My Page hero/login | `folio_app/pages/protected.py:67-79`, `layout.py:201-240` | `src/routes/my/+page.svelte` hero와 login required 분기 | pass | unknown |
| My Page profile summary | `profile_summary.py`, `protected.py:157-164` | `src/routes/my/+page.svelte` profile fields/about/stats | pass | unknown |
| My Page profile edit | `protected.py:211-261`, form submit/cancel | `src/routes/my/+page.svelte` `editingProfile`, `saveProfile` | pass | unknown |
| My Page portfolio actions | `portfolio_items.py`, `protected.py:167-199`의 보기/수정/삭제 | `src/routes/my/+page.svelte` portfolio card와 동일 3개 action | pass | unknown |
| My Page delete confirmation | `protected.py:105-153`의 dialog | `src/routes/my/+page.svelte` modal dialog | pass | unknown |
| My Page unread state | `annotate_unread_comment_status`, portfolio NEW badge | `project.has_unread_comments` 기반 `NEW` badge | pass | unknown |
| Notifications page | `pages/notifications.py:12-56` hero/panel/auto-read | `src/routes/notifications/+page.svelte` hero/list/auto-read | pass | unknown |
| Notification item action | 원본 `notification_item`의 상태/title/time + 프로젝트 보기 | Svelte 상태/title/time + 프로젝트 보기 | pass | unknown |
| Header notification preview | `components/layout.py:154-201` popover, 최근 5개, 모두 읽음/모두 보기 | 현재 Svelte는 `AuthNav`의 badge와 알림 전체 페이지 중심 | partial | unknown |
| Submit/Edit overview | `project_form.py:182-265` 좌우 기본 정보/산출물 링크 그룹 | `ProjectFormOverview.svelte`와 submit/edit route | pass | unknown |
| Submit/Edit thumbnail | 원본 `project_form.py:407-453`의 auto/url/upload/capture/delete 분기 | `ProjectHeroThumbnailPreview.svelte`, thumbnail handlers, mode controls | pass | unknown |
| Submit/Edit platform/PBIX | 원본 `project_form.py:461-494` Power BI 선택·PBIX·삭제 | submit/edit PBIX input, publish/unlink, progress steps | pass | unknown |
| Submit/Edit body editor | 원본 `project_body.py:37-64` editor + `본문 미리보기` | `ProjectBodyEditor.svelte`, Tiptap, preview, `h2` sync | pass | unknown |
| Submit/Edit save flow | 원본 `project_editor.py`의 저장·게시·캡처 순서 | submit/edit route의 save → upload → publish → capture | pass | unknown |
| Detail hero card | 원본 `layout.py:201-240` + `_detail_hero_card_html` | detail hero의 `ProjectCard compact` | pass | unknown |
| Detail iframe fallback | `project_detail_content.py`의 normalized Power BI URL | `canRenderDashboardFrame = hasDashboardUrl`, iframe fallback | pass | unknown |
| Detail action footer | 원본 `share.py`, `hero_footer.py`, detail actions | Svelte `detail-footer-row`와 action groups | partial | unknown |
| Detail comments | 원본 `project_comments.py` tree/reply/delete/pagination | `ProjectComments.svelte` tree/reply/delete/pagination | pass | unknown |
| Comment row density | 원본 body/actions/date dense row | Svelte has dedicated action/date row CSS after correction | partial | unknown |
| Detail report body | 원본 `프로젝트 리포트` card 안 sanitized body | Svelte report card + sanitized sections | pass | unknown |
| Detail back context | 원본 query context navigation | Svelte home/reference back context | partial | unknown |

## 현재 정적 결론

1. 네 페이지 모두 핵심 기능 컴포넌트는 존재한다.
2. 가장 큰 남은 기능 parity 후보는 알림 header preview popover다.
3. 상세 footer와 댓글 row는 구조를 보정했지만, 동일 viewport의 실제 geometry 확인 전에는 pass로 승격하지 않는다.
4. 등록/수정은 submit/edit route, preview, Tiptap, PBIX, thumbnail workflow가 코드상 연결되어 있다. 실제 브라우저에서는 mode별 입력 반영과 저장 후 상세 반영을 다시 확인해야 한다.
5. My Page는 원본의 query-param edit flow를 Svelte 독립 edit route로 바꾼 구조적 차이가 있다. 기능적으로는 대응하지만 URL/전환 감각은 별도 비교가 필요하다.

## 브라우저 복구 후 실행할 검증

1. `my-page`, `my-profile-edit-open`, `my-delete-confirm`, `my-unread-badge-fixture`를 desktop/mobile로 캡처한다.
2. `notifications`, header notification preview, unread auto-read, project navigation을 캡처·assert한다.
3. submit/edit에서 empty, typed, platform/PBIX, thumbnail URL/upload/capture, validation error를 실행한다.
4. detail에서 iframe success/fallback/failure, share, report, owner delete, comment reply/delete/pagination을 실행한다.
5. 각 상태에 원본 코드·원본 캡처·Svelte 코드·Svelte DOM/캡처·기능 assertion을 붙인다.
