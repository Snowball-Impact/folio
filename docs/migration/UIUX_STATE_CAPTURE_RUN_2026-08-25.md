# UIUX State Capture Run - 2026-08-25 14:36 KST

## Purpose

This run upgrades the Svelte UIUX audit from a page-list screenshot pass to a state-aware comparison pass. It exists because previous audits treated important screens as single static pages and missed owner-only edit flows, submit workflow variants, thumbnail preview states, and interaction states.

## Latest Artifact

- Capture root: `artifacts/uiux-svelte-current-20260825-145519`
- Manifest: `artifacts/uiux-svelte-current-20260825-145519/manifest.md`
- Machine report: `artifacts/uiux-svelte-current-20260825-145519/report.json`
- Overflow trace: `artifacts/uiux-svelte-current-20260825-145519/overflow-trace.md`
- Screenshot count: 66 PNG files
- Base URL: `http://127.0.0.1:5174`

## Harness Improvements

- Added state metadata per capture: `auth_state`, `project_owner_state`, `workflow_state`, `fixture_project_id`.
- Expanded hero detection to include current Svelte hero classes: `.submit-hero`, `.my-hero`, `.notification-hero`, `.policy-page-hero`, `.about-gapyear-hero`, `.project-detail-image-hero`.
- Added owner edit resolution from `/my`, producing `project-edit-owner` in addition to the fixed `project-edit-known` failure/permission state.
- Added submit workflow captures: empty draft, typed fields, manual thumbnail URL, capture selected, Power BI selected, validation error.
- Added My Page interaction captures: profile edit open, delete confirm first click.
- Added notification header hover capture.
- Added horizontal overflow element tracing with tag, class, rect, text sample, and selected computed styles.

## Focus Pages: Current Signals

| Page/state | Desktop signal | Mobile signal | Interpretation |
| --- | --- | --- | --- |
| `submit` | hero=1, overview=1, thumbnail preview=1, editor=1, overflow=0 | same structural elements, overflow=218px | Structure exists; mobile global/auth-shell overflow remains. |
| `submit-thumbnail-url` | height=1956, expected controls visible by selector | height=3349, overflow=218px | Thumbnail URL workflow is capturable and should be visually compared against Streamlit. |
| `submit-capture-selected` | height=1907, expected controls visible | height=3301, overflow=218px | Capture mode state is now covered. |
| `submit-powerbi-selected` | height=1990, editor=1 | height=3414, overflow=218px | Power BI/PBIX conditional area is now covered. |
| `submit-validation-error` | visible error selector expected | mobile same plus overflow=218px | Validation state is covered; error warning is expected for this state. |
| `project-edit-owner` | hero=1, overview=1, thumbnail preview=1, editor=1 | same structural elements, overflow=218px | Owner edit is now correctly captured. This replaces the previous false comparison against inaccessible edit. |
| `project-edit-known` | no hero/h1 + error selector | same plus overflow=218px | This is a permission/not-owner fixture, not the canonical edit UI. Keep it as negative state only. |
| `my-page` | hero=1, overflow=0 | overflow=218px | Main structure present; mobile width bug remains. |
| `my-profile-edit-open` | profile edit state captured | overflow=218px | Profile edit state is now covered. |
| `my-delete-confirm` | first-click confirm captured | overflow=218px | Destructive confirmation state is covered without deleting data. |
| `notifications` | hero=1, overflow=0 | overflow=218px | Page state covered; mobile width bug remains. |
| `notifications-header-hover` | hover state captured | overflow=218px, 13 traced nodes | Header notification popover overflows on mobile; trace points to `.nav-submenu.notification-submenu` at right=718. |

## Remaining P0/P1 UIUX Gaps

1. Mobile authenticated shell overflow: `submit`, `my-page`, `notifications`, `project-edit-owner`, and their interaction states all report `scrollWidth=718` with viewport `500`, causing `218px` horizontal overflow. The element tracer does not find inner overflowing descendants for most of these states, so the likely source is a layout/root/header width rule or off-canvas nav positioning rather than a single form/card child.
2. Mobile notification hover popover overflow is concrete: `.nav-submenu.notification-submenu` reaches right=718 with width=260. It needs mobile-specific anchoring, clamping, or disabled hover behavior.
3. Home/onboarding carousel-style hero intentionally contains a wide `.home-hero-track`; the current tracer flags it even when `overflowX=0` on desktop. Treat this as a review item, not automatically a defect, unless the viewport has actual horizontal scroll.
4. The capture harness can now detect Tiptap toolbar presence, but it does not yet click every formatting command. Add command-level interaction checks if editor behavior parity becomes the next target.

## Code Fix Applied During This Run

- Registered `@tiptap/extension-underline` in `ProjectBodyEditor.svelte` because the toolbar exposed a `U` button but the editor extensions did not include Underline.
- Added `@tiptap/extension-underline` as a direct dependency in `svelte_app/package.json` and root package-lock dependency block.

## Verification

- `python -m py_compile tools\\capture_svelte_uiux.py`: pass
- `npm.cmd run check`: pass, 0 errors / 0 warnings
- `npm.cmd run build`: pass
- Final recapture after mobile overflow fix: pass, 66 screenshots generated

## Next Recommended Work

1. Fix the mobile authenticated shell overflow first. Start at header/nav/root width rules and validate against `submit`, `my-page`, `notifications`, and `project-edit-owner` mobile screenshots.
2. Fix/clamp mobile notification popover positioning using the trace in `overflow-trace.md`.
3. Do visual parity review of the new submit states against the Streamlit capture set: empty form, filled form, thumbnail URL, capture mode, Power BI/PBIX, validation error.
4. Extend the harness to click Tiptap formatting commands and assert resulting DOM marks/nodes for bold, italic, underline, headings, lists, quotes, code block, link, undo/redo.

## Follow-Up Fix: Mobile Horizontal Overflow

After the state-aware capture, the repeated `218px` mobile overflow on authenticated pages was traced to the hidden notification submenu inside the wrapped mobile nav. The mobile media query had changed `.notification-submenu` to `right: auto`, so the absolutely positioned 260px popover extended from the far-right `알림` nav item and inflated the document width.

Fixes applied:

- Mobile `.notification-submenu` now keeps `right: 0` and sets `left: auto`.
- `html, body` now use `overflow-x: clip` to prevent carousel internals from creating user-visible horizontal page scroll.
- The capture harness now records `rawWidth` and `bodyWidth`, but bases `overflowX` on `documentElement.scrollWidth` so clipped carousel internals are not reported as page-level overflow.

Verification from `artifacts/uiux-svelte-current-20260825-145519/report.json`:

- `mobile submit`: `overflowX=0`, `scroll.width=500`
- `mobile my-page`: `overflowX=0`, `scroll.width=500`
- `mobile notifications`: `overflowX=0`, `scroll.width=500`
- `mobile project-edit-owner`: `overflowX=0`, `scroll.width=500`
- `mobile notifications-header-hover`: `overflowX=0`, `scroll.width=500`
- `overflow-trace.md`: no entries

Remaining warnings are expected workflow states only: fixed non-owner edit fixture and submit validation-error state.
## Follow-Up Capture: Edit Deletion Parity

A later full capture was generated after adding the original Streamlit edit-only deletion controls to Svelte.

- Capture root: `artifacts/uiux-svelte-current-20260825-153740`
- Report entries: 68
- Screenshot count: 66 PNG files
- Actual horizontal overflow states: 0
- Expected warnings only: non-owner edit fixture and submit validation-error fixture
- `project-edit-owner` desktop/mobile body text confirms `기존 Power BI 게시본 연결 삭제` and `기존 캡처본 삭제 후 재캡처`

This corrects the earlier project submit/edit gap where the audit had identified missing edit-only deletion affordances.
## Follow-Up Capture: My Page Delete Dialog

A later full capture was generated after changing Svelte My Page project deletion from inline confirmation to a modal dialog.

- Capture root: `artifacts/uiux-svelte-current-20260825-161200`
- Report entries: 68
- Screenshot count: 66 PNG files
- Actual horizontal overflow states: 0
- Expected warnings only: non-owner edit fixture and submit validation-error fixture
- `my-delete-confirm` desktop/mobile confirms `프로젝트 삭제`, irreversible-warning copy, `취소`, and `삭제하기`
## Follow-Up Capture: My Page Unread Comment Badge

A later full capture was generated after adding Svelte My Page unread-comment badge support.

- Capture root: `artifacts/uiux-svelte-current-20260825-163404`
- Report entries: 68
- Screenshot count: 66 PNG files
- Actual horizontal overflow states: 0
- Expected warnings only: non-owner edit fixture and submit validation-error fixture
- `my-page` and `my-delete-confirm` did not show `NEW` in this fixture, because the current signed-in data has no project with unread external comments.

Implementation note: unread status now follows the original Streamlit structure by comparing the latest comment from another author against `project_comment_reads.last_read_at` for the current user, then exposing `has_unread_comments` to the My Page portfolio card.
## Follow-Up Capture: NEW Badge Visual Fixture

A later full capture was generated after adding `my-unread-badge-fixture` to the state-aware capture harness.

- Capture root: `artifacts/uiux-svelte-current-20260825-164634`
- Report entries: 70
- Screenshot count: 68 PNG files
- Actual horizontal overflow states: 0
- Expected warnings only: non-owner edit fixture and submit validation-error fixture
- `desktop my-unread-badge-fixture`: `unread_badge=1`, `NEW` present in body text, no warnings
- `mobile my-unread-badge-fixture`: `unread_badge=1`, `NEW` present in body text, no warnings

This closes visual regression coverage for the My Page unread-comment badge without mutating the shared database fixture. A real DB-seeded unread case can still be added later for end-to-end data verification.
## Follow-Up Capture: Detail Dialog and Workflow States

A later full capture was generated after changing Svelte detail owner deletion to a modal dialog and expanding detail workflow captures.

- Capture root: `artifacts/uiux-svelte-current-20260825-171630`
- Report entries: 80
- Screenshot count: 78 PNG files
- Actual horizontal overflow states: 0
- Expected warnings only: non-owner edit fixture and submit validation-error fixture
- `project-detail-owner` desktop/mobile: owner detail page resolved from My Page, no warnings
- `project-detail-report-modal` desktop/mobile: modal present, `콘텐츠 신고` and report prompt present, no warnings
- `project-detail-delete-dialog` desktop/mobile: modal present, `.detail-delete-dialog=1`, `삭제하기` present, no warnings
- `project-detail-comment-draft` desktop/mobile: comment form draft state captured, no warnings
- `project-detail-liked-fixture` desktop/mobile: active liked visual fixture captured without mutating likes, no warnings

This closes the previously missing detail modal/confirmation capture coverage. At this point deterministic loading/skeleton and comment result states were still open; they are covered by the later detail loading/comment fixture capture below.
## Follow-Up Capture: Detail Loading and Comment Result Fixtures

A later full capture was generated after adding visual fixtures for detail loading and comment result states.

- Capture root: `artifacts/uiux-svelte-current-20260825-173409`
- Report entries: 90
- Screenshot count: 88 PNG files
- Actual horizontal overflow states: 0
- Expected warnings: non-owner edit fixture, submit validation-error fixture, and detail comment-error fixture
- `project-detail-loading-fixture` desktop/mobile: `detail_loading=2`, no warnings
- `project-detail-comment-success-fixture` desktop/mobile: `댓글이 등록되었습니다.` present, no warnings
- `project-detail-comment-error-fixture` desktop/mobile: `댓글 내용을 입력하세요.` present, expected visible-error warning

The loading and comment result states are visual fixtures only. They intentionally avoid inserting/deleting database comments during the shared UIUX capture run.
## Follow-Up Comparison: Detail Same-Data Triage

A later comparison pass generated detail-only contact sheets after simplifying Svelte detail output/resource/report structure toward the original Streamlit renderer.

- Latest Svelte capture root: `artifacts/uiux-svelte-current-20260825-184335`
- Detail comparison root: `artifacts/ui-parity/detail-comparison-20260825-184926`
- `desktop-known`: height ratio `0.59`
- `desktop-owner`: height ratio `1.02`
- `mobile-known`: height ratio `0.33`
- `mobile-owner`: height ratio `0.57`

Conclusion: desktop detail parity is no longer blocked by a general Svelte layout shortfall; the owner fixture proves a full Svelte detail page can match the original height closely. Remaining detail clone risk is concentrated in mobile layout/density and exact same-project fixture alignment.
## Follow-Up Capture: Detail Mobile Clone Tuning

A complete state-aware capture was generated after mobile detail layout tuning.

- Complete capture root: `artifacts/uiux-svelte-current-20260825-184335`
- Detail comparison root: `artifacts/ui-parity/detail-comparison-20260825-184926`
- Report entries: 90
- Screenshot count: 88 PNG files
- Actual horizontal overflow states: 0
- Expected warnings: non-owner edit fixture, submit validation-error fixture, and detail comment-error fixture
- Detail known mobile height: `2129 -> 2581` in comparison output, ratio `0.27 -> 0.33`
- Detail owner mobile height: `3843 -> 4506` in comparison output, ratio `0.49 -> 0.57`

Additional post-capture implementation:

- Detail visual panels now mark Tableau projects with `tableau-output` and reserve `1232px` for their iframe, mirroring the original Streamlit `embedded_dashboard_height()` Tableau branch.
- `npm.cmd run check` and `npm.cmd run build` pass after this branch.
- A later smoke capture at `artifacts/uiux-svelte-current-20260825-181546` is intentionally not promoted as latest complete evidence because authenticated mobile capture failed login and omitted owner/detail workflow states.
## Follow-Up Capture: Same Project Detail Baseline

A same-project detail baseline was generated with Streamlit running locally on `127.0.0.1:8501` and Svelte using `artifacts/uiux-svelte-current-20260825-184335`.

- Project ID: `dd1ed00c-1458-4f8e-92cb-4f31e319625d`
- Streamlit desktop capture: `artifacts/ui-parity/same-project-detail-20260825/streamlit-desktop-known.png`, size `(1408, 1409)`
- Streamlit mobile capture: `artifacts/ui-parity/same-project-detail-20260825/streamlit-mobile-known.png`, size `(500, 1093)`
- Same-project metrics: `artifacts/ui-parity/same-project-detail-20260825/same-project-metrics.md`
- Same-project Svelte/Streamlit height ratios after visual-state fix: desktop `1.04`, mobile `1.95`
- Measurement script: `tools/measure_same_project_detail.py`
- Comparison script: `tools/compare_same_project_detail.py`

Interpretation:

- The previous old Streamlit mobile detail screenshot `(500, 7901)` should not be used as the final reference for this known project.
- Current live Streamlit collapses or hides the dashboard component iframe in this public detail capture, while Svelte keeps a visible iframe area. This is now a product decision point, not just a spacing issue.
## Follow-Up Capture: Detail Visual Output States

A complete state-aware Svelte capture was generated after splitting representative output into embedded/external-only/failed states.

- Capture root: `artifacts/uiux-svelte-current-20260825-184335`
- Detail comparison root: `artifacts/ui-parity/detail-comparison-20260825-184926`
- Report entries: 90
- Screenshot count: 88 PNG files
- Actual horizontal overflow states: 0
- New captured states: `project-detail-external-only-fixture`, `project-detail-embed-failed-fixture`
- External-only fixture selector count: desktop/mobile `detail_external_only=2`
- Embed-failed fixture selector count: desktop/mobile `detail_embed_failed=2`
- Same-project public detail ratios: desktop `1.04`, mobile `1.95`

This confirms the previous same-project desktop gap was mostly the unconditional Svelte iframe. Mobile remains larger because of stacked mobile detail structure, not representative output iframe height.
## Follow-Up Capture: Detail State Split and Mobile Tightening Final Pass

A later complete state-aware Svelte capture supersedes the earlier `184335` detail evidence for current clone review.

- Capture root: `artifacts/uiux-svelte-current-20260825-190153`
- Detail comparison root: `artifacts/ui-parity/detail-comparison-20260825-190914`
- Report entries: 90
- Screenshot count: 88 PNG files
- Actual horizontal overflow states: 0
- Expected workflow warnings: 10
- Detail known desktop height in capture report: `1420`
- Detail known mobile height in capture report: `1721`
- External-only fixture: desktop/mobile `detail_external_only=2`
- Embed-failed fixture: desktop/mobile `detail_embed_failed=2`

The same-project public detail comparison now reports:

- Desktop: Streamlit `(1408, 1409)` vs Svelte `(1424, 1389)`, ratio `0.99`
- Mobile: Streamlit `(500, 1093)` vs Svelte `(500, 1690)`, ratio `1.55`

Implementation notes:

- The detail page no longer renders the Svelte-only section flow nav.
- Mobile detail hides the hero thumbnail preview and uses a more compact footer row.
- Representative output now has explicit supported, external-only, and failed visual states so capture analysis does not confuse a plain external URL with a large embedded dashboard.
- The remaining clone gap is mobile detail height/rhythm, especially sections after the hero and comments/footer spacing.
## Follow-Up Fix: Detail Mobile Compact Rhythm Second Pass

A second mobile-detail tightening pass was completed after the first state split and nav removal pass.

Changes applied:

- Mobile detail hero spacing and title/copy scale were reduced.
- Mobile detail footer meta/action gaps and button heights were reduced.
- Visual/report/comments panel margins and padding were tightened on mobile only.
- External-only/failed representative-output panels now use a shorter mobile empty-state height.
- Mobile report body line-height and paragraph spacing were reduced.
- Mobile comments were compacted: smaller form textarea, shorter buttons, tighter divider/list/card spacing, and a two-column comment index/content row instead of a full separate index line.
- Mobile site footer vertical padding was reduced.

Focused evidence:

- Detail-only Svelte capture root: `artifacts/uiux-svelte-detail-current-20260825-193146`
- Same-project metrics: `artifacts/ui-parity/same-project-detail-20260825/same-project-metrics.md`
- Detail-only capture heights: desktop `1420`, mobile `1374`, warnings `ok`
- Same-project public detail desktop ratio: `0.99`
- Same-project public detail mobile ratio: `1.23`, improved from the previous `1.55`

Updated conclusion:

- Desktop public detail remains aligned.
- Mobile public detail is now much closer to Streamlit while preserving the Svelte app's footer and representative-output behavior.
- Remaining mobile delta is about `250px` in the rendered comparison image, so the next pass should be visual rather than purely metric-driven: inspect first viewport proportions, footer necessity, and exact comment/login-note rendering against the original screenshot.
## Follow-Up Fix: Mobile Detail Visual Pass Final

A visual contact-sheet pass was completed after the numeric mobile-detail tightening.

Additional changes applied:

- Mobile global header now renders as an inset rounded navy card, matching the Streamlit mobile header silhouette instead of a full-bleed bar.
- Detail footer metadata now separates author/organization/date text lines from compact metric chips.
- Detail footer now includes the original-style visibility chip (`공개` / `비공개`).
- Detail actions were reordered so resource/report actions sit before the like control, closer to the original mobile action cluster.
- Mobile external-only `대표 결과물` now uses a low-weight guide sentence and full-width outline buttons instead of a heavy filled message box and primary blue button.
- Mobile visual/report headings now use a thin divider under the heading, matching the original section-card rhythm.

Final focused evidence:

- Detail-only Svelte capture root: `artifacts/uiux-svelte-detail-current-20260825-194825`
- Same-project comparison: `artifacts/ui-parity/same-project-detail-20260825/same-project-metrics.md`
- Desktop ratio: `0.99`
- Mobile ratio: `1.23`
- First viewport color balance improved: Streamlit light/navy `0.638/0.097`, Svelte `0.617/0.093`
- Detail-only capture warnings: `ok`

Interpretation:

- The first viewport is now visually much closer: rounded mobile header, compact metadata/action cluster, and outline output links align with the original Streamlit screenshot.
- The remaining height delta is mostly from Svelte rendering comments and the global app footer in the same captured page, while the current Streamlit same-project reference ends around the report area.
- Further reductions should be made only after deciding whether Svelte should hide/relocate global footer or comments in public mobile detail, because those are product behavior decisions rather than spacing defects.
## Follow-Up Finding: Comments Should Stay Visible

The original Streamlit detail code was rechecked after the final mobile visual pass.

Relevant source behavior:

- `folio_app/pages/project_detail.py` always calls `render_comments_section(project_id, user, project.get("author_id"))` after report rendering.
- `folio_app/components/project_comments.py` renders the login note for anonymous users and then the comment list/empty state.

Decision:

- Do not hide Svelte comments on anonymous mobile detail only to reduce height.
- The remaining mobile delta should be treated as styling parity for the comments/login-note/footer area, not as a missing opportunity to remove functionality.
- The final mobile same-project ratio remains `1.23`, with the first viewport color balance now close to the original.
## Follow-Up Fix: Submit/Edit Desktop Compact Rhythm

A focused submit/edit density pass was completed after detail mobile parity work.

Changes applied:

- Submit/edit hero padding and preview width were reduced on desktop.
- Project form spacing was tightened while preserving the original two-column overview structure.
- Overview section, platform panel, thumbnail panel, and form section padding/gaps were reduced.
- Tiptap toolbar controls were made more compact.
- The Tiptap editing surface now uses a smaller internal viewport with vertical scrolling, so long templates no longer stretch the whole page as much while all formatting features remain available.

Focused evidence:

- Svelte form capture root: `artifacts/uiux-svelte-form-current-20260825-195741`
- Form comparison sheets: `artifacts/ui-parity/form-comparison-20260825-195741`
- Desktop submit: Streamlit `(1424, 1050)` vs Svelte `(1424, 1517)`, ratio `1.45`, improved from the earlier `1.76`
- Desktop edit: Streamlit `(1424, 1076)` vs Svelte `(1424, 1700)`, ratio `1.58`, improved from the earlier `1.99`
- Mobile submit: Streamlit `(500, 2789)` vs Svelte `(500, 2571)`, ratio `0.92`
- Mobile edit: Streamlit `(500, 2756)` vs Svelte `(500, 2967)`, ratio `1.08`
- Capture warnings: `ok` for submit and owner edit across desktop/mobile

Interpretation:

- The previous desktop form gap was mainly caused by the expanded rich editor and looser Svelte spacing, not by missing controls.
- Desktop is still taller than Streamlit because Svelte exposes a richer Tiptap toolbar and live thumbnail preview, but the density is now closer without removing authoring functionality.
- Mobile form parity is acceptable by height; future work should focus on visual details and interaction behavior, not broad compaction.## Follow-Up Fix: Header Notifications Click Popover

The original Streamlit header notification behavior was rechecked before making the Svelte change.

Relevant source behavior:

- `folio_app/components/layout.py` uses `st.popover("알림", icon=":material/notifications:", key="nav_Notifications", help="알림", width="content")`.
- The popover shows the latest five notifications, read/unread state, project navigation, `모두 읽음`, and `모두 보기`.

Changes applied:

- `svelte_app/src/lib/components/AuthNav.svelte` now uses a button-driven notification popover instead of relying on hover/focus opening.
- The popover refreshes notification data when opened.
- Outside click and `Escape` close the popover.
- Opening a notification closes the popover before navigating.
- The capture harness now records `notifications-header-popover` with workflow `header_notification_click`.

Focused evidence:

- Svelte notification capture root: `artifacts/uiux-svelte-notifications-current-20260825-200657`
- Captured files: `desktop-notifications-header-popover.png`, `mobile-notifications-header-popover.png`
- Capture warnings: `ok` across desktop/mobile
- Horizontal overflow trace: no entries
- Pixel-diff check against default notifications page confirmed state changes: desktop bbox `(1105, 26, 1424, 394)`, mobile bbox `(0, 103, 85, 457)`

Interpretation:

- This closes a structural clone gap: the original interaction is click-to-open popover, not hover-only navigation.
- Remaining notification work should compare popover microcopy, card spacing, badge treatment, and empty/read state visuals against the original screenshots.
## Follow-Up Fix: Notifications Page State Language

A second notifications pass compared the Streamlit page implementation and styles against the current Svelte route.

Relevant source behavior:

- `folio_app/pages/notifications.py` keeps unauthenticated users on the notifications page after the hero and shows `알림을 확인하려면 로그인이 필요합니다.` with a login button.
- Notification rows render status, title, timestamp, and an optional `프로젝트 보기` action.
- The original row state language is limited to `새 알림` and `읽음`.
- The original empty state says `아직 새 알림이 없습니다.`.

Changes applied:

- `svelte_app/src/routes/notifications/+page.svelte` now shows the login-required state in-place instead of immediately redirecting unauthenticated users.
- Removed the Svelte-only row body text from the notifications list to match the original row density.
- Replaced the Svelte-only `방금 읽음` visible badge language with the original `읽음` / `새 알림` state language.
- Removed the Svelte-only `auto-read` visual badge color treatment.
- Matched the empty-state copy to `아직 새 알림이 없습니다.`.

Focused evidence:

- Authenticated notification capture root: `artifacts/uiux-svelte-notifications-current-20260825-214918`
- Guest notification capture root: `artifacts/uiux-svelte-notifications-guest-20260825-215019`
- Authenticated page heights: desktop `869`, mobile `1066`, warnings `ok`
- Guest page heights: desktop `869`, mobile `885`, warnings `ok`
- Horizontal overflow trace: no entries for both captures
- Header click popover pixel-diff still confirms open state: desktop bbox `(1105, 26, 1424, 394)`, mobile bbox `(0, 103, 85, 457)`

Interpretation:

- The notifications page is now structurally closer to Streamlit: hero, in-place auth prompt, bordered panel, row status/title/time/action, and page-open auto-read semantics.
- Remaining notification parity work is visual micro-tuning: exact popover background/lightness, button shape inside Streamlit popover, and fixture parity for notification count.
## Follow-Up Fix: My Page Structural Clone Pass

A My Page pass compared the original Streamlit implementation with the Svelte route and tightened the Svelte structure toward the original screen contract.

Relevant source behavior:

- `folio_app/pages/protected.py` keeps unauthenticated users on the My Page route after the hero and shows `마이 페이지를 이용하려면 로그인이 필요합니다.` with a login button.
- Profile edit is a distinct state: when editing, Streamlit renders the edit card and returns before the profile overview/project list.
- The profile overview uses field-style rows for `작성자`, `소속`, and `이메일`, followed by a bio paragraph and pill stats.
- Streamlit profile stats are `전체 프로젝트`, `공개 프로젝트`, `누적 조회`, and `총 좋아요`.
- Project cards are compact management rows: title, optional `NEW`, optional processing/failed status, one-line summary, tags, metrics/visibility, and `보기`/`수정`/`삭제` actions.

Changes applied:

- `svelte_app/src/routes/my/+page.svelte` now renders the unauthenticated state in-place instead of immediately navigating to login.
- Profile editing now mirrors the original state split: the edit form is shown without also rendering the profile overview and project list.
- Replaced the Svelte dashboard-style profile block with the original field-style profile summary.
- Changed stats from the previous Svelte set to the original-style `전체 프로젝트`, `공개 프로젝트`, `누적 조회`, `총 좋아요` set.
- Reworked the portfolio card markup so visibility is in the metadata cluster instead of a prominent title badge.
- Kept `NEW`, processing, and failed badges in the title line, matching the original portfolio card behavior.
- Updated `svelte_app/src/app.css` to match the original profile/portfolio density: bordered profile panel, centered fields, pill stats, compact project rows, and mobile two-column profile fields.

Focused evidence:

- Guest My Page capture root: `artifacts/uiux-svelte-my-guest-20260827-153040`
- Guest page heights: desktop `869`, mobile `885`, warnings `ok`
- Horizontal overflow trace: no entries
- `npm.cmd run check`: passed
- `npm.cmd run build`: passed
- `git diff --check`: no whitespace errors; CRLF warnings only

Capture limitation:

- Authenticated My Page recapture could not be completed in this environment because `FOLIO_TEST_ID` / `FOLIO_TEST_PW` were not available to the capture harness. The earlier attempted authenticated capture fell back to `login_failed`.
- Once test credentials are restored, rerun the focused My Page capture and compare `my-page`, `my-profile-edit-open`, `my-unread-badge-fixture`, and `my-delete-confirm` against the Streamlit references.

Interpretation:

- This closes the largest structural mismatch on My Page: Svelte no longer reads as a separate dashboard design, and now follows the original Streamlit field-summary plus compact portfolio management list.
- Remaining My Page work is fixture-based visual tuning under authenticated data: exact card height, action button width, project metadata wrapping, and delete dialog proportions.
## Follow-Up Correction: Test Credentials and PBIX Fixture

A capture blocker was rechecked after the test-account environment variables were pointed out.

Findings:

- The root `.env` does contain test login variables under `test_id` and `test_pw`.
- `tools/capture_svelte_uiux.py` already loads those variables with trimmed keys, so the earlier `login_failed` capture was not caused by missing credentials.
- The Svelte app reads Supabase values from `$env/dynamic/public`, so the dev server must receive `PUBLIC_SUPABASE_URL` and `PUBLIC_SUPABASE_PUBLISHABLE_KEY`.
- The root `.env` contains `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY`; for local Svelte captures, map those to the `PUBLIC_` names when launching `npm run dev`.
- A sample PBIX fixture exists at `artifacts/test.pbix`.

Changes applied:

- `tools/capture_svelte_uiux.py` now resolves a PBIX fixture from `FOLIO_TEST_PBIX_PATH`, `test_pbix_path`, or the default `artifacts/test.pbix`.
- The submit workflow now captures `submit-pbix-file-selected` after selecting the sample PBIX in the Power BI platform state.

Focused evidence:

- Authenticated My Page capture root: `artifacts/uiux-svelte-my-current-20260827-154107`
- My Page capture states covered: `my-page`, `my-profile-edit-open`, `my-unread-badge-fixture`, `my-delete-confirm` on desktop/mobile
- My Page warnings: `ok` across captured authenticated states
- My Page comparison: `artifacts/ui-parity/my-comparison-20260827-154107/my-page-metrics.md`
- Desktop My Page ratio: Streamlit `(1424, 1039)` vs Svelte `(1424, 1009)`, ratio `0.97`
- Mobile My Page ratio: Streamlit `(500, 2778)` vs Svelte `(500, 1137)`, ratio `0.41`; this remains fixture-count driven and should not be interpreted as layout parity by height alone.
- Submit PBIX fixture capture root: `artifacts/uiux-svelte-submit-pbix-current-20260827-154423`
- PBIX selected states captured: `desktop-submit-pbix-file-selected.png`, `mobile-submit-pbix-file-selected.png`
- Submit PBIX fixture warnings: `ok`; validation-error states intentionally report visible error selectors.

Interpretation:

- The previous authenticated My Page capture limitation was an environment-launch issue, not a missing test account.
- Future Svelte visual capture runs should launch the dev server with public Supabase env aliases mapped from the root `.env` before running Selenium.
- PBIX upload visual states can now be included in submit/edit UIUX parity checks without triggering actual Power BI publish submission.
## Follow-Up Fix: PBIX Upload UI State Parity

The Streamlit PBIX upload controls were rechecked against the Svelte submit/edit form.

Relevant source behavior:

- `folio_app/components/project_form.py` labels the uploader as `PBIX 파일 업로드`.
- The original uploader help communicates the max upload size, and CSS replaces the dropzone instruction with `최대 100MB / 파일 · PBIX`.
- The privacy warning is a separate warning alert below the uploader: `개인정보, 사내 데이터, 비공개 고객 정보가 포함된 PBIX는 업로드하지 마세요.`.
- In edit mode with an existing Power BI report, Streamlit first shows `기존 Power BI 게시본 연결 삭제`; the PBIX uploader appears only after that checkbox is selected.

Changes applied:

- `svelte_app/src/lib/components/ProjectFormOverview.svelte` now uses the original uploader label `PBIX 파일 업로드`.
- PBIX file help now uses `최대 100MB / 파일 · PBIX`.
- The PBIX privacy warning is now rendered as a separate warning block instead of being merged into the file help text.
- Edit mode with an existing Power BI report now hides the PBIX uploader until `기존 Power BI 게시본 연결 삭제` is checked, matching the original state gate.
- Thumbnail upload help was aligned to the same compact file instruction rhythm: `최대 5MB / 파일 · JPG, PNG, WebP`.
- `tools/capture_svelte_uiux.py` now captures edit PBIX states: `project-edit-powerbi-selected`, `project-edit-pbix-replace-enabled`, and `project-edit-pbix-file-selected`.

Focused evidence:

- Submit PBIX capture root: `artifacts/uiux-svelte-submit-pbix-current-20260827-155037`
- Submit PBIX selected states: `desktop-submit-pbix-file-selected.png`, `mobile-submit-pbix-file-selected.png`
- Edit PBIX capture root: `artifacts/uiux-svelte-edit-pbix-current-20260827-155338`
- Edit PBIX states covered on desktop/mobile: `project-edit-powerbi-selected`, `project-edit-pbix-replace-enabled`, `project-edit-pbix-file-selected`
- PBIX fixture: `artifacts/test.pbix`
- Capture warnings: `ok` for submit/edit PBIX states; horizontal overflow trace has no entries

Interpretation:

- Submit and edit now expose PBIX upload as the original does: upload label, max-size instruction, warning alert, and edit replacement gate are structurally aligned.
- Remaining PBIX work should focus on actual publish integration testing separately, because UI capture intentionally selects the file without submitting to Power BI.

## Follow-Up Fix: Detail Comments and Hero Footer Parity

The project detail comment section and hero footer were rechecked against the original Streamlit source.

Relevant source behavior:

- `folio_app/components/project_comments.py` renders comments inside a bordered `project_comments_section` container with a compact heading card, login notice, divider, and paginated comment rows.
- `folio_app/styles/detail_comments.py` uses a dense row layout for desktop comments: index, author, body, date, and right-aligned actions. Replies use dot numbering such as `1.1` and a light blue reply background.
- `folio_app/styles/hero_footer.py` renders the detail footer as a thin action strip attached under the hero with compact pill controls and a subtle shadow.

Changes applied:

- `svelte_app/src/lib/components/ProjectComments.svelte` now preserves dot-style nested reply numbering and shows the original author badge when the comment author is the project author.
- `svelte_app/src/app.css` now styles the comments section as the original light-blue shell with a white heading card, compact login notice, divider, empty state, desktop row comments, reply highlight, and mobile stacked comment cards.
- The Svelte detail footer was tightened to the original attached action-strip proportions: smaller gap, 32px controls, larger horizontal padding on desktop, negative hero attachment offset, and subtle footer shadow.

Focused evidence:

- Detail comments/footer capture root: `artifacts/uiux-svelte-detail-comments-current-20260827-160557`
- Captured desktop/mobile states: loading fixture, external-only fixture, embed-failed fixture, report modal, liked fixture, comment draft, comment success fixture, comment error fixture, and owner delete dialog.
- Horizontal overflow trace: no entries.
- `npm.cmd run check`: passed with 0 errors and 0 warnings.
- `npm.cmd run build`: passed.
- `git diff --check` on touched files: no whitespace errors; CRLF warnings only.

Remaining detail-page clone work:

- Visually inspect the new screenshots against the original 70-shot Streamlit set once the image viewer path is stable in the tool runner.
- Continue with project detail modal/action microcopy and spacing parity if screenshot comparison shows residual drift.

## Follow-Up Fix: Detail Action State Parity

The project detail action controls were rechecked against the original Streamlit implementation.

Relevant source behavior:

- `folio_app/components/share.py` updates the share button label itself to `복사 완료` or `복사 실패`; it does not render a separate page-level success message.
- `folio_app/pages/project_detail.py` sends unauthenticated like/report interactions to Login instead of leaving an inline action state on the detail page.
- The original report dialog is compact: title `콘텐츠 신고`, prompt sentence, `신고 사유`, `메모`, and two full-width action buttons.
- The original delete dialog is compact: title `프로젝트 삭제`, confirmation sentence, irreversible-delete caption, and two full-width action buttons.

Changes applied:

- `svelte_app/src/routes/projects/[id]/+page.svelte` now uses a share button label state (`링크 복사` -> `복사 완료`/`복사 실패` -> `링크 복사`) and builds the original Streamlit-style shared URL with `page=Home`, `project_id`, and share UTM params.
- The detail share button now includes the original link icon shape and no longer creates a separate success message row.
- Unauthenticated report clicks now navigate to Login with a `next` return target.
- Report and delete modals no longer include Svelte-only English eyebrow text; report field label now matches the original `메모`.
- `svelte_app/src/lib/components/ProjectLikeButton.svelte` now navigates unauthenticated likes to Login with the current path as `next`.
- `tools/capture_svelte_uiux.py` now captures `project-detail-share-clicked` so share feedback is no longer omitted from detail-page parity checks.

Focused evidence:

- Detail action capture root: `artifacts/uiux-svelte-detail-actions-current-20260827-162135`
- Captured action states include desktop/mobile `project-detail-share-clicked`, `project-detail-report-modal`, and owner `project-detail-delete-dialog`.
- Horizontal overflow trace: no entries.
- `python -m py_compile tools\capture_svelte_uiux.py`: passed.
- `npm.cmd run check`: passed with 0 errors and 0 warnings.
- `npm.cmd run build`: passed.
- `git diff --check` on touched files: no whitespace errors; CRLF warnings only.

Remaining detail-page clone work:

- Compare final action screenshots against the original capture sheet visually when image inspection is stable.
- If needed, tune exact Streamlit dialog width and vertical button spacing after direct screenshot overlay review.

## Follow-Up Fix: Detail Visual, Report, and Back Action Parity

The lower project detail content was rechecked against the original Streamlit source.

Relevant source behavior:

- `folio_app/components/project_detail_content.py` renders the visual result inside `project_detail_visual`, with a compact `대표 결과물` heading and resource link buttons after the dashboard/fallback state.
- `folio_app/styles/detail_visual.py` constrains the visual heading, captions, and resource buttons to a 900px content lane inside the full card.
- `folio_app/components/project_detail_content.py` renders the report as a single `folio-detail-content-card` with `프로젝트 리포트` heading and anonymous content sections, without visible per-section labels.
- `folio_app/styles/detail_page.py` uses 900px centered report sections, 14px body text, 1.78 line-height, and a pill-shaped back button with a subtle shadow.

Changes applied:

- `svelte_app/src/routes/projects/[id]/+page.svelte` now uses `detail-back-action-row` instead of inline styles for the lower back action.
- `svelte_app/src/app.css` now aligns the visual panel to the original card rhythm: 16px radius, 22px padding, hidden overflow, 900px heading/caption/resource-link lane, and 12px dashboard frame radius.
- The project report card now follows the original structure: 14px rounded card, 8px/28px/18px padding, centered 900px heading and sections, 14px body text, 1.78 line-height, navy paragraph/list text, and section bottom dividers.
- Mobile visual/report padding was adjusted to match the original compact 16px content lane instead of inheriting the overly generic 14px panel padding.
- The lower back action now matches the original pill button: right aligned, 34px height, muted text, 999px radius, and subtle shadow/hover treatment.

Focused evidence:

- Detail content capture root: `artifacts/uiux-svelte-detail-content-current-20260827-162949`
- Captured desktop/mobile states include visual loading, external-only, embed-failed, share clicked, report modal, liked fixture, comment draft/success/error, and owner delete dialog.
- Horizontal overflow trace: no entries.
- `npm.cmd run check`: passed with 0 errors and 0 warnings.
- `npm.cmd run build`: passed.
- `git diff --check` on touched files: no whitespace errors; CRLF warnings only.

Remaining detail-page clone work:

- Run a screenshot overlay/contact-sheet comparison against the original Streamlit detail captures once local image inspection is stable.
- If the overlay shows residual drift, tune exact vertical distances between hero footer, visual card, report card, comments, and back action.

## Correction: Verification Standard Tightening for Detail Clone

A review found that prior detail-page confirmation was too shallow.

What was missed:

- The original Streamlit detail page renders a dashboard iframe whenever `normalize_power_bi_embed_url(project.power_bi_url)` returns a valid URL. Svelte was gating iframe rendering behind `embed_status === 'supported'`, so valid dashboard URLs could fall into an external-only/empty fallback instead of rendering the iframe.
- The original Streamlit comment rows keep the comment body, action buttons, and created-at date visually on one dense row on desktop. Svelte had been styled as a grid, but the action buttons were placed on a second row, so the comment height was not actually cloned.
- The earlier use of capture `warnings: ok` was insufficient. That only proves no detected overflow or error selector, not visual or functional parity.

Fixes applied:

- `svelte_app/src/routes/projects/[id]/+page.svelte` now treats any saved `project.power_bi_url` as iframe-renderable, matching the original fallback behavior. Power BI embed-token failure no longer blocks iframe fallback when a dashboard URL exists.
- `svelte_app/src/lib/components/ProjectComments.svelte` now renders comment actions before the date in the row flow.
- `svelte_app/src/app.css` now uses a five-column desktop comment row: index, author, body, actions, date. Actions are nowrap and date is pinned to the right column.

Stronger evidence collected:

- DOM verification on the known detail page returned `iframe_count=1`, `embed_empty_count=0`, and an actual Fabric iframe `src`.
- DOM verification on a real comment row returned `same_row=true`; body/action/date top positions differed by about 1-2px.
- Final verification capture root: `artifacts/uiux-svelte-detail-fix-verification-20260827-165058`
- Capture warnings: `ok` for desktop/mobile detail states; horizontal overflow trace has no entries.
- `npm.cmd run check`: passed with 0 errors and 0 warnings.
- `npm.cmd run build`: passed.
- `git diff --check` on touched files: no whitespace errors; CRLF warnings only.

Updated rule for remaining clone work:

- Do not call a page/state cloned based only on screenshot-file existence or manifest warnings.
- For functional UI such as iframes, uploads, editor controls, notifications, and actions, verify the actual DOM/runtime state.
- For dense UI such as comment rows, cards, lists, and tables, verify layout geometry or direct visual overlay, not just CSS similarity.

## Correction: Detail Hero Visual Was Not Actually Cloned

A review found another first-viewport clone miss.

What was missed:

- The original Streamlit detail hero always uses `render_hero(..., image_html=_detail_hero_card_html(project))`, so the hero has a visual project-card slot.
- The original compact project card still renders cover media plus title, summary, tags, footer metadata, and metrics as an overlay.
- Svelte had passed `compact` to `ProjectCard`, but `ProjectCard.svelte` hid the whole card body when compact. That left the hero visual as only a background image/pattern without the original overlay information.
- Mobile detail also explicitly hid `.detail-card-preview`, removing the hero visual altogether.

Fixes applied:

- `svelte_app/src/lib/components/ProjectCard.svelte` now renders title, summary, tags, footer metadata, and metrics even in compact mode.
- `svelte_app/src/app.css` gives compact cards a tighter overlay layout suitable for hero preview.
- `.detail-card-preview` now has a real width (`min(100%, 470px)`) so it cannot collapse inside the detail hero grid.
- Mobile detail no longer hides the hero preview; it renders a smaller `360px` preview card.

Runtime evidence collected:

- Desktop detail hero preview measured `470x264` and `previewVisible=true`.
- Mobile detail hero preview measured `360x202` and `previewVisible=true`.
- The hero preview DOM contains image, title, summary, and footer metadata.
- New capture root: `artifacts/uiux-svelte-detail-hero-fix-20260827-170613`
- Horizontal overflow trace: no entries.
- `npm.cmd run check`: passed with 0 errors and 0 warnings.
- `npm.cmd run build`: passed.

Updated rule:

- For first-viewport clone checks, verify that the hero visual slot is not merely present in the DOM but has meaningful geometry and visible media/content.

## Correction: Submit/Edit Hero Preview Must Reuse Card Structure

A follow-up review found that the submit/edit hero preview was still structurally different from the original Streamlit form flow.

What was missed:

- The original Streamlit submit/edit hero passes `render_project_card_html(hero_preview_project(...))` into `render_hero`, so the hero visual is the same project card renderer used elsewhere.
- Svelte used a separate `ProjectHeroThumbnailPreview` card design with its own visible header and duplicated card markup.
- The preview needed to be verified as a meaningful visual card: fixed geometry, visible title, visible one-liner, tags, metrics, and non-clickable preview behavior.
- Edit preview also exposed duplicate platform tags such as `#Power BI` and `#powerbi`, while the original `tags_with_platform()` removes platform aliases before adding the canonical platform label.
- The Tiptap toolbar exposed Link/Unlink controls, but `@tiptap/extension-link` was not declared as a direct dependency or configured in the editor.

Fixes applied:

- `ProjectHeroThumbnailPreview.svelte` now delegates to the shared `ProjectCard` renderer with `compact preview` mode.
- `ProjectCard.svelte` now supports a non-link `preview` mode so submit/edit hero previews do not navigate to fake project IDs.
- Submit/edit thumbnail preview state now preserves URL/capture-backed thumbnails where applicable.
- Submit/edit preview tag normalization now removes platform aliases before adding the canonical platform tag.
- `ProjectBodyEditor.svelte` now imports and configures the Tiptap Link extension, and package metadata declares it directly.
- Compact card summary text now has stable visible height to avoid clipping in hero preview cards.

Runtime evidence collected:

- Submit desktop preview: `440x248`, `tag=DIV`, `href=null`, title/summary/tags/metrics visible.
- Submit mobile preview: `418x235`, `tag=DIV`, `href=null`, title/summary/tags/metrics visible, `overflowX=0`.
- Submit typed state reflects title, one-liner, tags, and Power BI platform tag in the hero preview.
- Submit manual thumbnail URL state changes the preview from auto cover to `imgCount=1` with the entered URL.
- Submit PBIX state uses `artifacts/test.pbix`; file input is present and selected.
- Edit owner preview: `440x248`, `tag=DIV`, `href=null`, existing thumbnail `imgCount=1`, `overflowX=0`.
- Edit owner preview no longer duplicates `#powerbi`; observed tags were `#Power BI`, `#내일배움카드`, `#직업훈련`, `#시장분석`, `+1`.
- `npm.cmd run check`: passed with 0 errors and 0 warnings.

Updated rule:

- When the original reuses a shared renderer, the Svelte clone should reuse the equivalent shared component or document a deliberate reason not to. A visually similar one-off component is not enough for clone parity.

## Correction: Project Body Editor Preview and Default Body Sync

- Original evidence: `folio_app/components/project_body.py` renders the body editor with a `본문 미리보기` expander, and the default template is structured around `h2` sections (`문제 정의`, `사용 데이터`, `분석 과정`, `핵심 인사이트`).
- Original sanitizer evidence: `folio_app/services/project_content.py` allows both `h2` and `h3`, so section headings survive sanitization.
- Svelte miss: the rich editor had formatting controls but did not expose the original-style preview expander.
- Svelte miss: `svelte_app/src/lib/format.ts` allowed `h3/h4/h5` but not `h2`, so the default body sections could be visually present as text while losing semantic heading structure after sanitization.
- Svelte miss: submit/edit state could rely on parsed section fields without explicitly syncing the current editor HTML immediately before save.
- Fix applied: `ProjectBodyEditor.svelte` now includes a sanitized `본문 미리보기` expander below the editor.
- Fix applied: `submit/+page.svelte` and `projects/[id]/edit/+page.svelte` call `syncProjectBodyInput()` before submit/update validation, parsing current editor HTML into the original section fields.
- Fix applied: `format.ts` now allows `h2`, matching the original project body structure.
- Verification evidence: Selenium on `/submit` returned `hasPreview=true`, `summaryText=본문 미리보기`, `editorHeadings=[문제 정의, 사용 데이터, 분석 과정, 핵심 인사이트]`, `previewHeadings=[문제 정의, 사용 데이터, 분석 과정, 핵심 인사이트]`, `scriptInPreview=false`, `overflowX=-15`.
- Verification evidence: `npm.cmd run check` passed with 0 errors and 0 warnings; `npm.cmd run build` passed. `git diff --check` reported CRLF warnings only.
- Audit rule update: a visual preview is not enough. For editor/detail clone checks, verify semantic section tags survive the same sanitizer path used by display/save logic.

## Submit E2E Registration Evidence: PBIX Flow

- Route tested: `/submit` on the Svelte app with the configured test account and `artifacts/test.pbix`.
- Successful run artifact: `artifacts/uiux-submit-e2e-20260827/submit-e2e-report-proper-selector.json`.
- Filled state evidence: `checkedRadios=[powerbi, auto_cover]`, `pbixInputs=1`, `pbixSelected=true`, preview title/summary reflected the entered values, and preview tags were `#Power BI`, `#e2e`, `#clone-check`.
- Submit progress evidence: after submit, button text changed to `등록 중...` and the operation text reached `작업 진행 62% PBIX 파일을 Power BI Workspace에 게시하는 중입니다.`.
- Final state evidence: redirect reached `/projects/7553d519-b395-464a-bd57-3b33100e2df1`; detail `h1` matched the submitted title; tags matched the submitted platform/tag set; comments UI existed; horizontal overflow was not present.
- Power BI evidence: the registered PBIX produced a live `https://app.powerbi.com/reportEmbed?...` iframe on the Svelte detail page.
- Hero evidence: `heroExists=true` and `heroImageCount=0` for this run because the selected thumbnail mode was `auto_cover`. This is not an image-upload failure by itself; default-cover clone checks must verify the auto-cover/card cover DOM, not only `<img>` counts.
- Detail body evidence: `bodyH2=[프로젝트 리포트]`. This is consistent with the documented original detail renderer, which outputs a single `프로젝트 리포트` content card and anonymous sanitized body sections rather than visible per-section labels.
- Automation lesson: Svelte inputs in this form do not explicitly set `type="text"`; Selenium scripts must select `input:not([type])` or placeholders/labels, not only `input[type="text"]`.
- Automation lesson: do not use `localStorage.clear()` during auth E2E because it can remove Supabase session keys. Delete only `folio-submit-draft:*` keys when clearing drafts.
- Audit rule update: a failed E2E script is not product evidence until the script records actual field counts, checked radios, button text, and route/body state before and after submit.
