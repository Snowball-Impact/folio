# Focus UIUX Parity Reaudit - 2026-08-25

## Inputs

- Original Streamlit screenshots: `artifacts/ui-parity/streamlit/`
- Latest Svelte state-aware screenshots: `artifacts/uiux-svelte-current-20260825-184335/`
- Focus comparison sheets: `artifacts/ui-parity/focus-comparison-20260825-145519/`
- Detail comparison sheets: `artifacts/ui-parity/detail-comparison-20260825-175343/`
- Latest Svelte manifest: `artifacts/uiux-svelte-current-20260825-184335/manifest.md`
- Latest Svelte overflow trace: `artifacts/uiux-svelte-current-20260825-184335/overflow-trace.md`

## Method

This pass compares four focused surfaces by structure and workflow state, not by full-page height alone:

1. Project submit/edit form
2. My Page
3. Notifications
4. Project detail

For each surface, the comparison checks:

- Page shell: hero, header, footer, responsive width
- User workflow: empty, populated, interaction, error, owner/non-owner states
- Functional affordances: controls the original exposes and whether Svelte exposes them
- Visual hierarchy: whether the first screen communicates the same job and next action
- Capture confidence: whether the screenshot represents the right auth/owner/data state

## Generated Comparison Artifacts

- `focus-desktop-common.png`: Streamlit vs Svelte for submit, edit, my, notifications, detail on desktop
- `focus-mobile-common.png`: Streamlit vs Svelte for submit, edit, my, notifications, detail on mobile
- `svelte-submit-states-desktop.png`: Svelte-only submit workflow states on desktop
- `svelte-submit-states-mobile.png`: Svelte-only submit workflow states on mobile
- `svelte-auth-interactions.png`: Svelte-only My/Notification interaction states
- `metrics.md`: dimensions and first-viewport lightness metrics

## Metric Snapshot

| Pair | Height ratio | Reading |
| --- | ---: | --- |
| desktop submit | 1.76 | Svelte is much taller; rich editor plus hero preview makes the form less compact than Streamlit. |
| desktop edit | 1.99 | Owner edit now captures correctly, but Svelte is nearly twice as tall as Streamlit edit-query. |
| desktop my-page | 1.09 | Similar height; structural parity is plausible. |
| desktop notifications | 0.94 | Similar height; structural parity is plausible for populated state. |
| desktop detail | 0.61 | Svelte detail is much shorter; likely missing/condensed project body, visual, or comment state compared with original fixture. |
| mobile submit | 1.16 | Similar height after overflow fix; workflow states need visual review. |
| mobile edit | 1.22 | Slightly taller; acceptable if controls are complete. |
| mobile my-page | 0.57 | Svelte is much shorter; likely fixture/data state mismatch or missing repeated portfolio items. |
| mobile notifications | 0.40 | Svelte is much shorter; likely fewer notifications or missing before/after unread state fixture. |
| mobile detail | 0.28 | Svelte is far shorter; not safe to claim parity without same project body/comment fixture. |

## Project Submit/Edit

### Original Streamlit Structure

Source: `folio_app/components/project_form.py`, `folio_app/components/project_editor.py`

The original form is a single shared renderer used by both submit and edit. It contains:

- intro copy
- bordered overview section with two columns
- basic info inputs: title, one-liner, tags
- platform radio
- conditional PBIX upload
- edit-only PBIX deletion checkbox when an existing Power BI report exists
- resource links: Embed Code, GitHub URL, Web App URL
- thumbnail mode radio: auto cover, upload, URL, capture
- conditional thumbnail URL input
- conditional thumbnail upload input
- edit-only thumbnail delete checkbox
- capture-mode guidance
- rich project body editor
- edit-only visibility setting
- submit/cancel actions
- validation for URL normalization, PBIX extension/size, thumbnail extension/mime/size
- progress handling for thumbnail capture and PBIX publish/replace

### Current Svelte Structure

Sources:

- `svelte_app/src/routes/submit/+page.svelte`
- `svelte_app/src/routes/projects/[id]/edit/+page.svelte`
- `svelte_app/src/lib/components/ProjectFormOverview.svelte`
- `svelte_app/src/lib/components/ProjectHeroThumbnailPreview.svelte`
- `svelte_app/src/lib/components/ProjectBodyEditor.svelte`

Current Svelte now has:

- shared overview component
- hero thumbnail preview bound to form state
- title/one-liner/tags inputs
- platform radio
- conditional PBIX file input
- resource link fields
- thumbnail mode radio
- conditional thumbnail upload/URL/capture help
- Tiptap body editor with formatting toolbar
- edit-only visibility card
- validation error state capture
- localStorage submit draft

### Gaps

P0/P1 gaps that remain:

- Edit-only existing thumbnail deletion is now implemented in Svelte edit mode. The owner edit capture confirms `기존 캡처본 삭제 후 재캡처` / `기존 썸네일 삭제` copy is present when an existing thumbnail is available.
- Edit-only existing PBIX connection deletion is now implemented in Svelte edit mode. The owner edit capture confirms `기존 Power BI 게시본 연결 삭제` is present when a Power BI report URL exists.
- Progress UI is now structurally implemented for submit/edit. Svelte shows a reusable operation progress panel with step labels, percentage, active/done/error states for project save, thumbnail upload/delete/capture, PBIX publish, and PBIX unlink. It is client-side step progress rather than server-streamed progress callbacks.
- Submit/edit compactness is weaker on desktop. Svelte submit is 1.76x original height and owner edit is 1.99x original height. The form is functionally richer now, but less dense than the original first-screen composition.
- Edit draft persistence is absent. Streamlit edit goes through session draft state; Svelte only has submit localStorage draft.
- Field-level URL feedback is less visible in Svelte. Streamlit gives immediate helper/error feedback around URL fields; Svelte defers more validation to submit/service responses.

### Recommended Fix Plan

1. Add edit-only deletion controls to `ProjectFormOverview.svelte`: `delete_thumbnail`, `delete_pbix` bindable fields or callbacks.
2. Extend `ProjectSubmitInput`/update payload handling so edit can request thumbnail deletion and PBIX metadata unlink without accidental file deletion surprises.
3. Add operation progress state blocks for PBIX publish/replace and thumbnail capture/upload.
4. Add edit draft persistence or intentionally document why Svelte edit should not persist drafts.
5. Tighten desktop vertical rhythm of submit/edit: reduce hero/form gaps and rich editor min-height for desktop if visual parity is prioritized over authoring comfort.

## My Page

### Original Streamlit Structure

Source: `folio_app/pages/protected.py`

The original My Page contains:

- auth gate
- shared page hero
- profile overview card rendered as one compact block
- profile edit mode as a full replacement view
- portfolio heading
- one bordered container per portfolio item
- item meta and unread comment annotation
- actions: view, edit, delete
- delete confirmation dialog
- empty portfolio CTA

### Current Svelte Structure

Source: `svelte_app/src/routes/my/+page.svelte`

Current Svelte contains:

- auth gate via `currentSession`
- page hero
- profile summary and stats grid
- inline profile edit card
- portfolio section
- portfolio card list
- view/edit/delete actions
- modal delete confirmation dialog
- empty portfolio CTA

### Gaps

- Mobile My Page is much shorter than original: 0.57x height. This is probably fixture/data-count mismatch, but it means visual parity cannot be signed off from current screenshots.
- Project deletion confirmation now uses a modal dialog in Svelte, matching the Streamlit `프로젝트 삭제` dialog pattern with project title, irreversible-warning copy, cancel, and `삭제하기` action.
- Original annotates unread comment status in portfolio items. Svelte now computes unread external-comment status for My Page projects and renders a `NEW` badge next to the project title when `has_unread_comments` is true.
- Profile edit mode in Streamlit replaces the main content after hero; Svelte opens inline below profile summary. This is usable, but structurally different.

### Recommended Fix Plan

1. Add or seed a My Page fixture with comparable number of projects/comments before visual sign-off.
2. Keep delete modal regression coverage through `my-delete-confirm`.
3. Keep `my-unread-badge-fixture` in the capture harness for visual regression coverage; add a real DB seeded unread case only if end-to-end data verification is required.
4. Capture empty portfolio state separately using a dedicated fixture account.

## Notifications

### Original Streamlit Structure

Sources:

- `folio_app/pages/notifications.py`
- `folio_app/components/layout.py`

Original behavior:

- shared notification page hero
- notification panel with heading
- list item status: `새 알림` / `읽음`
- per-notification project open button
- page-open auto mark-all-read after rendering unread notifications
- header popover with latest 5 notifications
- header popover has mark-all and view-all actions

### Current Svelte Structure

Sources:

- `svelte_app/src/routes/notifications/+page.svelte`
- `svelte_app/src/lib/components/AuthNav.svelte`

Current behavior:

- page hero
- notification panel and list
- auto-read state recorded as `방금 읽음`
- project open button
- mark-all action if unread remains
- header hover popover with latest notifications
- mobile popover overflow fixed

### Gaps

- Mobile notifications height is 0.40x original. This likely reflects fewer notification rows or auto-read fixture state, not necessarily missing layout.
- The original popover is a Streamlit popover opened by click; Svelte uses hover/focus submenu. That is a UX divergence, especially on touch devices.
- The original page captures unread before auto-read visually for a moment; Svelte immediately mutates local state to read after load. The state-aware harness captures the final page, not pre-auto-read.

### Recommended Fix Plan

1. Decide whether header notifications should be click/toggle popover instead of hover/focus to better match Streamlit and mobile expectations.
2. Add a harness state that seeds or intercepts unread notifications before auto-read, then captures pre-read and post-read states.
3. Use a fixture with comparable notification count for Streamlit-vs-Svelte visual parity.

## Project Detail

### Original Streamlit Structure

Source: `folio_app/pages/project_detail.py`

Original detail includes:

- loading shell
- project detail hero with project card preview
- footer action row: author/date meta, view/public/comment metrics, like, report, owner edit/delete, share handler
- visual panel when project has a dashboard/report
- project report sections
- comments section
- back action
- view tracking

### Current Svelte Structure

Source: `svelte_app/src/routes/projects/[id]/+page.svelte`

Current detail includes:

- detail hero with compact project card preview
- meta/action footer row
- like button
- share action
- owner edit/delete dialog or non-owner report dialog
- report modal
- flow nav
- visual panel for Power BI or iframe URL
- report sections
- comments component
- back action

### Gaps

- Latest same-name known detail remains shorter than original because the fixture has only one report section and one comment. However, the authenticated owner detail fixture with four sections and nine comments is now 1.02x the original desktop height, so the earlier desktop length gap was mostly fixture/data mismatch. Mobile owner detail remains 0.49x the original mobile height, so mobile density/content-flow parity still needs visual sign-off.
- Current Svelte converts section body HTML to plain text via `plainTextFromHtml(body)`, so rich body formatting created by Tiptap may not render on detail. This is a functional/UIUX gap against a rich editor workflow.
- Loading shell state was not captured in the latest Svelte run.
- Report modal state, owner delete dialog state, liked visual state, and comment draft state are now included in the latest full capture set.
- Same-fixture content parity is partly narrowed: latest owner detail proves Svelte can render a full multi-section/multi-comment detail page, but the Streamlit and Svelte screenshots are still not the same project fixture.

### Recommended Fix Plan

1. Render sanitized project body HTML on detail instead of flattening all section bodies to plain text, or define a restricted HTML renderer for Tiptap output.
2. Keep detail workflow regression coverage for non-owner report modal, owner delete dialog, liked visual state, and comment draft. Loading shell and comment success/error visual fixtures are now captured; true DB-mutating comment submit still needs isolated end-to-end coverage if required.
3. Re-run Streamlit and Svelte against the exact same project fixture, especially on mobile, before final visual sign-off.

## Updated Priority Queue

P0:

1. Exact same-fixture recapture for detail/my/notifications before declaring final visual parity; detail desktop is close with owner data, but mobile still needs focused review.
2. Add real DB seeded unread-comment capture if end-to-end data verification is required; visual fixture coverage is now present.

P1:

1. Header notification interaction pattern: click/toggle vs hover/focus.
2. Loading/modal/confirmation state captures for detail.
3. Submit/edit desktop density tuning.
4. Edit draft persistence decision.

## Status After This Pass

- Horizontal overflow P0: resolved in latest Svelte capture.
- Submit/edit structural shell: mostly aligned; edit-only deletion controls and progress UI are implemented, with desktop density still looser than original.
- My Page: basic shell aligned; delete dialog and unread badge logic are implemented, and visual `NEW` fixture capture now passes. Same-count fixture confidence is still weak.
- Notifications: page shell aligned, interaction pattern differs.
- Detail: rich body flattening fixed; owner/non-owner action, loading shell, liked state, comment draft, and comment success/error visual states are now captured. Latest desktop owner detail height is 1.02x Streamlit, but mobile owner detail is 0.57x; exact same-fixture mobile/content-dashboard parity remains before final visual sign-off.

## Follow-Up Fix: Detail Rich Body Rendering

The original Streamlit detail renderer preserves sanitized project section HTML through `sanitize_project_html(body)`. The Svelte detail route previously rendered each section with `plainTextFromHtml(body)`, which erased formatting produced by the Tiptap editor.

Fixes applied:

- Added `sanitizeProjectHtml` to `svelte_app/src/lib/format.ts` with a small allowlist for Tiptap/report tags and safe external links.
- Updated `svelte_app/src/routes/projects/[id]/+page.svelte` to render report bodies with `{@html sanitizeProjectHtml(body)}` inside `.report-section-content`.
- Added `.report-section-content` styles for paragraphs, headings, lists, blockquotes, code, marks, underline, links, and rules.

Focused recapture after the fix:

- Artifact: `artifacts/uiux-detail-rich-after-20260825-151007`
- Desktop detail: height `2248`, `overflowX=0`, warnings `[]`
- Mobile detail: height `2271`, `overflowX=0`, warnings `[]`

This closes the rich-editor-to-detail rendering gap. The remaining detail parity risk is fixture completeness: original Streamlit detail screenshots are still much taller, so Svelte needs same-project body/dashboard/comment fixture recapture before final visual parity sign-off.
## Follow-Up Fix: Edit-Only Deletion Controls

After re-checking the original Streamlit form renderer, two edit-only controls were confirmed as structural parity requirements rather than optional refinements:

- Existing thumbnail removal: `기존 썸네일 삭제` / `기존 캡처본 삭제 후 재캡처`
- Existing Power BI report unlink: `기존 Power BI 게시본 연결 삭제`

Svelte now mirrors these affordances in `ProjectFormOverview.svelte` for owner edit state only. The submit/edit input model carries `delete_thumbnail` and `delete_pbix`, the edit page calls dedicated client helpers, and the API now supports authenticated owner-only `DELETE` handlers for `/api/projects/[id]/thumbnail` and `/api/projects/[id]/powerbi-publish`.

Latest verification:

- `npm.cmd run check`: pass, 0 errors / 0 warnings
- `npm.cmd run build`: pass
- Latest state-aware recapture: `artifacts/uiux-svelte-current-20260825-153740/`
- Capture count: 66 PNG screenshots, 68 report entries
- Actual horizontal overflow states: 0
- Owner edit capture contains both deletion affordances on desktop and mobile
## Follow-Up Fix: Submit/Edit Operation Progress

The original Streamlit project editor uses a bordered `작업 진행` panel with progress text for long-running operations such as thumbnail capture, PBIX publish/replace, and Power BI render waiting. Svelte previously only changed the submit button text and surfaced errors after the async call.

Svelte now includes `OperationProgress.svelte`, reused by submit and owner edit pages. The panel is hidden while idle and appears only after validation passes and a save operation actually starts. It tracks:

- Project metadata save
- Existing thumbnail deletion
- Existing Power BI unlink
- Thumbnail image upload
- PBIX publish/replace
- Thumbnail auto capture
- Final completion

Each step can render pending, active, done, or error state. This gives Svelte structural UIUX parity with Streamlit's operation panel, with one implementation caveat: the Svelte progress percentages are client-side step estimates because the current fetch APIs do not stream backend progress callbacks to the browser.

Verification:

- `npm.cmd run check`: pass, 0 errors / 0 warnings
- `npm.cmd run build`: pass
## Follow-Up Fix: My Page Delete Dialog

The original Streamlit My Page opens `@st.dialog("프로젝트 삭제")` from each portfolio item. Svelte previously used an inline two-click delete confirmation inside the card, which was functionally safe but structurally different.

Svelte now opens a centered modal dialog from the portfolio `삭제` action. The dialog includes:

- `프로젝트 삭제` title
- selected project title in the confirmation sentence
- `삭제한 프로젝트는 복구할 수 없습니다.` warning
- `취소` and `삭제하기` actions
- disabled `삭제 중...` state while the delete request is running
- backdrop click close while idle

Latest verification:

- `npm.cmd run check`: pass, 0 errors / 0 warnings
- `npm.cmd run build`: pass
- Latest state-aware recapture: `artifacts/uiux-svelte-current-20260825-184335/`
- Capture count: 66 PNG screenshots, 68 report entries
- Actual horizontal overflow states: 0
- `my-delete-confirm` desktop/mobile body text confirms the modal dialog copy and actions
## Follow-Up Fix: My Page Unread Comment Badge

The original Streamlit My Page uses `annotate_unread_comment_status()` before rendering portfolio cards, then shows a compact `NEW` badge beside a project title when another user's latest comment is newer than the viewer's `project_comment_reads.last_read_at`.

Svelte now mirrors that structure:

- `ProjectCard` includes optional `has_unread_comments`.
- `listMyProjects()` first attaches public metadata, then annotates unread external-comment status from `comments` and `project_comment_reads` for the signed-in user.
- My Page portfolio title rows render `NEW` with `aria-label="안 본 댓글 있음"` when `project.has_unread_comments` is true.
- The badge is styled as a compact red status chip, separate from public/private and processing/failed chips.

Verification:

- `npm.cmd run check`: pass, 0 errors / 0 warnings
- `npm.cmd run build`: pass
- Latest state-aware recapture: `artifacts/uiux-svelte-current-20260825-184335/`
- Report entries: 70
- Screenshot count: 68 PNG files
- Actual horizontal overflow states: 0
- Remaining warnings are expected workflow states only: non-owner edit fixture, submit validation-error fixture, and detail comment-error fixture.

Capture note: the live authenticated fixture still has no naturally unread project state, but the capture harness now includes `my-unread-badge-fixture` for visual sign-off. Desktop and mobile both report `unread_badge=1`, `NEW` in body text, and no warnings.
## Follow-Up Fix: Detail Dialog and Workflow Captures

The original Streamlit detail page uses modal dialogs for both non-owner reporting and owner deletion. Svelte previously had a report modal, but its visible structure was thinner than the original, and owner deletion used an inline two-click confirmation.

Svelte now mirrors the original detail interactions more closely:

- Owner delete uses a modal dialog with `프로젝트 삭제`, project-title confirmation copy, irreversible-warning copy, `취소`, and `삭제하기`.
- Non-owner report modal now includes visible `콘텐츠 신고` heading and the original-style prompt asking what problem exists with the content.
- The report memo placeholder now matches the original example language around empty embedding/report links.
- The capture harness now resolves an owner detail page from My Page and captures detail owner state separately from the public known project.
- The capture harness now includes detail workflow states for report modal, liked visual state, comment draft, and owner delete dialog.

Verification:

- `npm.cmd run check`: pass, 0 errors / 0 warnings
- `npm.cmd run build`: pass
- `python -m py_compile tools\\capture_svelte_uiux.py`: pass
- Latest state-aware recapture: `artifacts/uiux-svelte-current-20260825-184335/`
- Report entries: 80
- Screenshot count: 78 PNG files
- Actual horizontal overflow states: 0
- `project-detail-report-modal` desktop/mobile: modal present, `콘텐츠 신고` and report prompt present, warnings `[]`
- `project-detail-delete-dialog` desktop/mobile: modal present, `.detail-delete-dialog=1`, `삭제하기` present, warnings `[]`
- `project-detail-comment-draft` desktop/mobile: comment form present, warnings `[]`
- `project-detail-liked-fixture` desktop/mobile: active liked visual fixture captured, warnings `[]`

Remaining detail clone work: true comment submit end-to-end verification still needs isolated fixture handling if mutation-level coverage is required. Same-project Streamlit/Svelte content-dashboard comparison is still required before declaring final visual parity.
## Follow-Up Fix: Detail Loading and Comment Result Fixtures

The original Streamlit detail page has a visible loading shell before project data resolves, and the comments section exposes success/error feedback around comment submission. Svelte's direct SSR route does not naturally expose a deterministic loading screenshot in the capture pass, so the state-aware harness now captures visual fixtures for these states without mutating shared data.

Added coverage:

- `project-detail-loading-fixture`: replaces the page body with a detail loading hero/card/content skeleton styled after the original Streamlit loading shell.
- `project-detail-comment-success-fixture`: injects the existing success message style with `댓글이 등록되었습니다.` above the comment form.
- `project-detail-comment-error-fixture`: injects the existing error message style with `댓글 내용을 입력하세요.` and marks the form as an error fixture.
- `detail_loading` selector was added to the capture report so skeleton presence is machine-checkable.

Verification:

- `npm.cmd run check`: pass, 0 errors / 0 warnings
- `npm.cmd run build`: pass
- `python -m py_compile tools\\capture_svelte_uiux.py`: pass
- Latest state-aware recapture: `artifacts/uiux-svelte-current-20260825-184335/`
- Report entries: 86
- Screenshot count: 84 PNG files
- Actual horizontal overflow states: 0
- `project-detail-loading-fixture` desktop/mobile: `detail_loading=2`, warnings `[]`
- `project-detail-comment-success-fixture` desktop/mobile: success text present, warnings `[]`
- `project-detail-comment-error-fixture` desktop/mobile: error text present; `visible error message selector detected` is expected for this fixture.

This closes deterministic visual coverage for detail loading and comment result states. It does not submit a real comment; mutation-level comment E2E should use an isolated project/comment fixture with cleanup.
## Follow-Up Comparison: Detail Same-Data Triage

A focused detail comparison pass was generated after simplifying Svelte detail report/visual structure to more closely match the original Streamlit renderer.

Structural adjustments made in Svelte detail:

- Visual panel heading now mirrors the original `대표 결과물` heading without extra descriptive copy or link-count chip.
- Resource action labels now include the original-style external-link marker: `대시보드 열기 ↗`, `보고서 보기 ↗`, `GitHub 보기 ↗`.
- Report heading now mirrors the original `프로젝트 리포트` content-card heading without extra intro copy or section-count chip.
- Report sections now render sanitized section body HTML directly, without added Svelte-only section numbers/titles.
- Back action now uses `← {backLabel}` like the original Streamlit back button.

Comparison artifact:

- Detail comparison root: `artifacts/ui-parity/detail-comparison-20260825-175343/`
- Svelte capture root: `artifacts/uiux-svelte-current-20260825-184335/`
- `desktop-known`: Streamlit `(1424, 3622)` vs Svelte `(1424, 2128)`, ratio `0.59`
- `desktop-owner`: Streamlit `(1424, 3622)` vs Svelte `(1424, 3681)`, ratio `1.02`
- `mobile-known`: Streamlit `(500, 7901)` vs Svelte `(500, 2129)`, ratio `0.27`
- `mobile-owner`: Streamlit `(500, 7901)` vs Svelte `(500, 3843)`, ratio `0.49`

Interpretation:

- The old desktop detail height gap was mostly a fixture/data mismatch. The owner fixture has four report sections and nine comments, and now lands very close to the original desktop height.
- The known fixture still remains short because it has one section and one comment.
- Mobile detail remains the largest unresolved clone risk. Even with the richer owner fixture, Svelte mobile is about half the original height, so the next focused pass should compare mobile spacing, iframe/dashboard height, comment nesting, and footer/header wrapping against the original screenshot.

Verification:

- `npm.cmd run check`: pass, 0 errors / 0 warnings
- `npm.cmd run build`: pass
- Latest state-aware recapture: `artifacts/uiux-svelte-current-20260825-184335/`
- Report entries: 86
- Screenshot count: 84 PNG files
- Actual horizontal overflow states: 0
- Detail comparison generated by `tools/compare_detail_parity.py`.
## Follow-Up Fix: Detail Mobile Clone Tuning

A focused mobile-detail pass was completed against the original Streamlit detail structure.

Changes applied:

- Mobile detail hero/card preview now stacks with original-like `20px 16px` padding and a stable compact preview cover height.
- Mobile detail footer meta/actions now wrap into full-width rows like the Streamlit footer action block.
- Mobile visual/report/comments panels now use tighter original-like padding and spacing.
- Mobile dashboard/PowerBI shells now reserve a `520px` minimum height, matching the original non-Tableau embedded dashboard default.
- Detail visual panels now detect Tableau output from `platform_key`, `project_type`, or `public.tableau.com` and reserve `1232px`, matching the original Streamlit Tableau branch from `embedded_dashboard_height()`.

Complete comparison artifact:

- Svelte capture root: `artifacts/uiux-svelte-current-20260825-184335/`
- Detail comparison root: `artifacts/ui-parity/detail-comparison-20260825-184926/`
- `desktop-known`: ratio `0.59`
- `desktop-owner`: ratio `1.02`
- `mobile-known`: old-baseline ratio is `0.27` after external-only correction; same-project ratio is `1.95`
- `mobile-owner`: old-baseline ratio is `0.51`; owner same-project baseline still needs authenticated Streamlit capture
- Full capture: 90 entries, 88 PNG files, 0 actual horizontal overflow states, 10 expected workflow warnings.

Post-change smoke capture note:

- `artifacts/uiux-svelte-current-20260825-181546/` was generated after adding the Tableau branch, but the authenticated mobile capture path failed login in that run and produced only 67 entries / 65 PNG files. Do not treat it as the latest complete state-aware capture.
- `npm.cmd run check` and `npm.cmd run build` pass after the Tableau branch.

Remaining clone risk:

- Same-project mobile detail parity is still not final because the current Streamlit mobile reference uses a much taller fixture. The next structural step is to capture/compare the exact same project data on both Streamlit and Svelte, including platform-specific dashboard height, report body length, and comment count.
## Follow-Up Comparison: Same Project Detail Baseline

A same-project public detail baseline was generated to separate real UIUX gaps from fixture mismatch.

Target project:

- `dd1ed00c-1458-4f8e-92cb-4f31e319625d`
- Title: `Insights in the Dutch Football competition (Ered`

Artifacts:

- Streamlit same-project captures: `artifacts/ui-parity/same-project-detail-20260825/streamlit-desktop-known.png`, `artifacts/ui-parity/same-project-detail-20260825/streamlit-mobile-known.png`
- Svelte comparison source: `artifacts/uiux-svelte-current-20260825-184335/`
- Same-project comparison metrics: `artifacts/ui-parity/same-project-detail-20260825/same-project-metrics.md`
- Same-project contact sheets: `desktop-known-same-project-*.png`, `mobile-known-same-project-*.png`

Findings:

- Same-project Streamlit current capture is much shorter than the older baseline: desktop `1409px`, mobile `1093px`.
- Same-project Svelte capture is taller: desktop `2128px`, mobile `2581px`.
- Same-project ratios are desktop `1.51x`, mobile `2.36x` Svelte/Streamlit.
- DOM measurement shows the main cause is the representative output iframe: Streamlit current runtime reports visible detail visual blocks around desktop `202px` / mobile `260px`, while Svelte reserves desktop `724px` / mobile `520px` for `.dashboard-frame`.
- This contradicts the earlier old-baseline comparison where Svelte appeared too short on mobile. The old `mobile-detail-known.png` baseline was therefore not a reliable same-project reference for final clone decisions.

Decision:

- Do not immediately shrink/remove the Svelte iframe just to match the current Streamlit runtime capture. Original Streamlit code still intends to render embedded dashboards through `render_embedded_dashboard()`, and matching a runtime-collapsed iframe would damage actual functionality.
- Treat the next task as a feature-preserving parity fix: define explicit visual states for `embedded`, `external-only`, and `embed-failed`, then compare each state independently.
## Follow-Up Fix: Detail Visual Output States

Svelte detail now separates representative output states instead of treating every saved `power_bi_url` as the same large iframe case.

Changes applied:

- `hasVisualOutput` now mirrors the original `project_visual_context()` more closely by including processing, failed, dashboard URL, report URL, and GitHub URL cases.
- The visual panel now exposes explicit classes for `tableau-output`, `external-only-output`, and `embed-failed-output`.
- `supported` dashboard URLs keep the iframe path; `external_only` and failed states render compact original-like message panels plus resource links.
- The capture harness now records `detail_external_only` and `detail_embed_failed` selector counts.
- The capture harness now includes `project-detail-external-only-fixture` and `project-detail-embed-failed-fixture` for desktop and mobile.

Verification:

- `npm.cmd run check`: pass, 0 errors / 0 warnings
- `npm.cmd run build`: pass
- `python -m py_compile tools\capture_svelte_uiux.py tools\compare_detail_parity.py tools\compare_same_project_detail.py tools\measure_same_project_detail.py`: pass
- Latest complete state-aware recapture: `artifacts/uiux-svelte-current-20260825-184335/`
- Report entries: 90
- Screenshot count: 88 PNG files
- Actual horizontal overflow states: 0
- `project-detail-external-only-fixture` desktop/mobile: `detail_external_only=2`, warnings `[]`
- `project-detail-embed-failed-fixture` desktop/mobile: `detail_embed_failed=2`, warnings `[]`

Same-project result after this fix:

- Same-project metrics: `artifacts/ui-parity/same-project-detail-20260825/same-project-metrics.md`
- `desktop-known`: `(1408, 1409)` Streamlit vs `(1424, 1461)` Svelte, ratio `1.04`
- `mobile-known`: `(500, 1093)` Streamlit vs `(500, 2135)` Svelte, ratio `1.95`

Remaining clone risk:

- Desktop same-project public detail is now close enough for structural parity review.
- Mobile same-project public detail is still too tall. The next fix should focus on mobile hero preview, detail footer row, flow nav, and section margins rather than iframe height.
## Follow-Up Fix: Detail State Split and Mobile Tightening Final Pass

A final detail-focused pass was completed after the representative-output state split and mobile detail tightening.

Changes applied:

- Svelte detail now separates supported embedded dashboards, external-only dashboard links, and embed-failed output states.
- The state-aware harness captures `project-detail-external-only-fixture` and `project-detail-embed-failed-fixture` on desktop and mobile.
- Mobile detail no longer shows the Svelte-only hero card preview; this better matches the current Streamlit mobile detail capture where the hero is compact.
- The Svelte-only detail flow nav was removed from the detail page markup.
- Mobile detail footer meta/actions were compacted into tighter full-width rows.

Latest evidence:

- Complete Svelte capture root: `artifacts/uiux-svelte-current-20260825-190153`
- Detail comparison root: `artifacts/ui-parity/detail-comparison-20260825-190914`
- Report entries: 90
- Screenshot count: 88 PNG files
- Actual horizontal overflow states: 0
- Expected workflow warnings: 10
- External-only fixture selector count: desktop/mobile `detail_external_only=2`
- Embed-failed fixture selector count: desktop/mobile `detail_embed_failed=2`

Same-project public detail result:

- `desktop-known`: Streamlit `(1408, 1409)` vs Svelte `(1424, 1389)`, ratio `0.99`
- `mobile-known`: Streamlit `(500, 1093)` vs Svelte `(500, 1690)`, ratio `1.55`

Updated conclusion:

- Desktop public detail is now structurally close enough for visual review.
- Mobile public detail is still taller than the current Streamlit same-project capture, but the gap is now reduced from `1.95x` to `1.55x`.
- The remaining mobile gap should be handled through mobile-specific section rhythm, comments area, and global detail/footer spacing, not by collapsing supported dashboard functionality.
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
