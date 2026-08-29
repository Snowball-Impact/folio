# UIUX Structural Parity Audit

Audited on 2026-08-25. This is the structural pass requested after the earlier screenshot-only audit missed stateful UI details.

## Scope

This audit compares the original Streamlit app and the Svelte app by responsibility structure and workflow state. It uses:

- Existing Streamlit captures: `artifacts/ui-parity/streamlit/`
- Existing Svelte captures: `artifacts/ui-parity/svelte-current/`
- Fresh latest Svelte captures: `artifacts/uiux-svelte-current-20260825-135436/`
- Fresh latest-vs-Streamlit metrics: `artifacts/uiux-svelte-current-20260825-135436/streamlit-comparison-metrics.md`
- Previous state reaudit: `docs/UIUX_STATE_REAUDIT_2026-08-25.md`

Important limitation: Streamlit was not running on `127.0.0.1:8501` during this pass, so the original baseline is the existing 2026-08-24 capture set. Svelte was recaptured from `127.0.0.1:5174` after the latest submit/edit changes.

## Structural Method

A page is checked across four layers:

1. Route/shell: URL, auth gate, header/footer, page hero.
2. Workflow orchestration: how state flows between preview, form, validation, mutation, progress, and navigation.
3. Component responsibility: whether repeated UI is centralized or duplicated across routes.
4. State matrix: empty, populated, interactive, error, success, owner/non-owner, mobile.

Parity is not accepted from one full-page screenshot. The screenshot must name its auth state, owner state, fixture project, and workflow state.

## Fresh Svelte Capture Summary

Latest Svelte recapture output:

- Manifest: `artifacts/uiux-svelte-current-20260825-135436/manifest.md`
- DOM report: `artifacts/uiux-svelte-current-20260825-135436/report.json`
- Screenshots: `artifacts/uiux-svelte-current-20260825-135436/*.png`

Key latest-vs-original metrics:

| Screen | Streamlit | Latest Svelte | Ratio | Structural reading |
| --- | ---: | ---: | ---: | --- |
| desktop-home | 1424x889 | 1424x1747 | 1.97 | Svelte home remains longer; inspect rail/hero density. |
| desktop-submit | 1424x1050 | 1424x1845 | 1.76 | Much improved from old 6849px capture, but still longer due rich editor and preview. |
| desktop-edit | 1424x1076 | 1424x869 | 0.81 | Invalid parity proof: current fixture is not editable by test user. |
| desktop-my-page | 1424x1039 | 1424x1130 | 1.09 | Comparable length; now needs state-level checks. |
| desktop-notifications | 1424x1028 | 1424x968 | 0.94 | Comparable length; auto-read/header-popover states need capture. |
| desktop-detail | 1424x3622 | 1424x2193 | 0.61 | Shorter; inspect whether content/comment/pagination states are missing. |
| mobile-home | 500x2072 | 500x1966 | 0.95 | Comparable, but latest capture reports horizontal overflow. |
| mobile-submit | 500x2789 | 500x3239 | 1.16 | Comparable length after fixes, but latest capture reports horizontal overflow. |
| mobile-edit | 500x2756 | 500x869 | 0.32 | Invalid parity proof: current fixture is not editable by test user. |
| mobile-my-page | 500x2778 | 500x1590 | 0.57 | Shorter; inspect missing/closed states vs original. |
| mobile-notifications | 500x2767 | 500x1115 | 0.40 | Shorter; likely fewer notifications/state differences. |
| mobile-detail | 500x7901 | 500x2234 | 0.28 | Shorter; likely fewer content/comment states than original capture. |

Capture instrumentation issue: several pages report `no page hero detected` because the selector list does not include all current hero classes such as `submit-hero`, `policy-page-hero`, and `about-gapyear-hero`. This does not mean the hero is absent. The capture script must be updated before final sign-off.

Repeated mobile overflow signal:

- `mobile-submit`, `mobile-my-page`, `mobile-notifications`, `mobile-project-edit-known`, and `mobile-onboarding` report `scrollWidth=718` at `viewportWidth=500`, i.e. `218px` overflow.
- `mobile-home` reports `63px` overflow.
- This is a structural CSS issue candidate. It may come from fixed-width nav/header/menu content, toolbar controls, preview card, or action rows. It needs DOM element-level overflow tracing, not visual guessing.

## Page Structure Map

### Submit/Edit Project

Original Streamlit structure:

- `folio_app/components/project_editor.py`
  - `render_submit_project_form(user_id)`
  - `render_edit_project_form(author_id, project)`
- Shared form renderer: `folio_app/components/project_form.py::render_project_form`
  - intro row
  - overview section: left basic info, right resource links
  - platform panel
  - thumbnail panel
  - rich body editor
  - action row
  - visibility setting for edit
  - returns form data, submitted, cancelled
- Data/progress/mutation responsibility:
  - draft load/save/clear
  - validation
  - build payload
  - create/update project
  - PBIX publish/replacement/delete
  - thumbnail upload/capture/delete
  - success navigation

Current Svelte structure:

- Routes:
  - `svelte_app/src/routes/submit/+page.svelte`
  - `svelte_app/src/routes/projects/[id]/edit/+page.svelte`
- Shared components:
  - `ProjectFormOverview.svelte`
  - `ProjectHeroThumbnailPreview.svelte`
  - `ProjectBodyEditor.svelte`
- Services:
  - `projects.ts`
  - `powerbi-publish.ts`
  - `thumbnails.ts`
  - `projectBody.ts`

Structural parity status:

| Responsibility | Streamlit | Current Svelte | Status |
| --- | --- | --- | --- |
| Shared submit/edit form structure | One `render_project_form` | Shared overview/body components, route-level orchestration | Partial parity |
| Hero preview from form state | `hero_preview_project()` + project card HTML | `ProjectHeroThumbnailPreview` derived from route state | Improved, needs state recapture |
| Overview 2-column structure | Single bordered overview container | `ProjectFormOverview` | Improved |
| Platform radio and PBIX affordance | Platform panel with PBIX upload/delete | Platform panel with PBIX upload/replacement hint | Partial: delete missing |
| Thumbnail modes | auto/upload/url/capture + edit delete | auto/upload/url/capture | Partial: edit delete/re-capture controls missing |
| Drafts | Session-state project drafts | localStorage submit draft; no edit draft | Partial |
| Body editor | Original rich body editor and parser | Tiptap editor and parser | Improved, needs saved-render recapture |
| Validation | Central validation with URL/file errors | Route checks plus `projects.ts` validation | Partial: locality and file-size/type parity need check |
| Progress UI | Progress panels for capture/PBIX | Button submitting text; endpoint calls | Partial: progress parity missing |
| Visibility | Edit action row | Edit bottom card | Mostly aligned |

P0 gaps:

- Edit fixture capture is invalid because test user cannot edit the known project.
- Existing thumbnail delete and PBIX delete are structurally present in Streamlit but not equivalently exposed in Svelte.
- Edit draft persistence is present in Streamlit but absent in Svelte.
- Progress panels for thumbnail capture/PBIX publish are not structurally equivalent.
- Mobile overflow must be traced before visual sign-off.

### My Page

Original Streamlit structure:

- `folio_app/pages/protected.py::render_my_page`
  - auth gate
  - shared page hero
  - profile overview card
  - profile edit mode
  - portfolio section heading
  - portfolio item cards
  - view/edit/delete buttons
  - empty portfolio CTA
  - unread comment badge in portfolio item

Current Svelte structure:

- `svelte_app/src/routes/my/+page.svelte`
  - auth gate via `currentSession`
  - hero
  - `profile-summary`
  - inline profile edit toggle/form
  - `portfolio-section`
  - portfolio cards and view/edit/delete/delete-confirm

Structural parity status:

| Responsibility | Streamlit | Current Svelte | Status |
| --- | --- | --- | --- |
| Profile summary | Centered compact overview | Present | Needs visual/state recapture |
| Profile edit | Explicit edit mode | Present | Needs edit-open capture |
| Portfolio populated | Cards with meta/status/new badge | Present | Partial: unread badge parity needs confirmation |
| Portfolio empty | CTA to submit | Present | Needs empty fixture capture |
| Delete confirmation | Button state/confirmation | Present | Needs interaction capture |
| Mobile action layout | Streamlit stacked columns | Svelte reports overflow | Gap candidate |

P1 gaps:

- State-specific captures are missing: profile edit open, empty portfolio, delete confirmation, unread badge.
- Latest mobile capture reports `218px` overflow.

### Notifications

Original Streamlit structure:

- `folio_app/pages/notifications.py`
  - auth gate
  - page hero
  - notification panel
  - page-open auto read after rendering unread notifications
  - project item click marks individual read
- `folio_app/components/layout.py`
  - header notification popover
  - recent notifications
  - unread count
  - mark all
  - view all

Current Svelte structure:

- `svelte_app/src/routes/notifications/+page.svelte`
  - auth gate
  - page hero
  - list panel
  - auto mark-all after load
  - item click read + goto project
- `svelte_app/src/lib/components/AuthNav.svelte`
  - notification submenu with previews and actions

Structural parity status:

| Responsibility | Streamlit | Current Svelte | Status |
| --- | --- | --- | --- |
| Page-open auto read | Present | Present | Aligned |
| Header popover | Present | Present in code | Needs open-state capture |
| Item click read | Present | Present | Needs interaction capture |
| Empty state | Present | Present likely | Needs empty fixture capture |
| Mobile header behavior | Streamlit stacked nav | Svelte reports overflow | Gap candidate |

P1 gaps:

- Header popover open state was not captured.
- Auto-read transition is not captured as before/after state.
- Latest mobile capture reports `218px` overflow.

### Project Detail

Original Streamlit structure:

- `folio_app/pages/project_detail.py`
  - loading hero
  - detail hero with project card
  - summary/meta
  - action footer group: view/comment/public/share/like/report/edit/delete
  - contextual back action
  - representative visual/result
  - external resource links
  - report content
  - comments/replies/pagination
  - notification read handling for project comments

Current Svelte structure:

- `svelte_app/src/routes/projects/[id]/+page.svelte`
  - SSR loaded detail
  - hero with compact project card
  - detail footer row
  - like/share/report/edit/delete actions
  - report modal
  - section nav
  - representative output
  - report sections
  - comments component
  - back link based on query state

Structural parity status:

| Responsibility | Streamlit | Current Svelte | Status |
| --- | --- | --- | --- |
| Hero card visual | Present | Present | Needs visual recapture |
| Action/meta group | Unified footer row | Present but composition differs | Partial |
| Share | Present | Present | Needs copied-message capture |
| Like | Present | Present | Needs auth/anon state capture |
| Report | Non-owner dialog | Non-owner modal | Needs non-owner capture |
| Owner edit/delete | Present | Present | Needs owner capture |
| Contextual back | Query-state aware | Query-state aware for references/home | Partial, needs legacy/query capture |
| Result visual | Present | Present | Needs fixture content comparison |
| Comments/replies | Present with pagination | Present without explicit pagination | Partial |

P1 gaps:

- Owner/non-owner/anonymous state captures are missing.
- Report-open, share-message, delete-confirm, reply-open captures are missing.
- Svelte desktop detail is shorter than Streamlit; must confirm whether comments/content are missing or the fixture states differ.

### Home

Original Streamlit structure:

- Header
- 4-slide hero carousel
- Browse/search/filter panel
- Popular tags
- Horizontal rails with controls
- Project cards with 16:9 auto-cover/thumbnail

Current Svelte structure:

- Header
- 4-slide hero carousel
- Browse/search/tag filtering
- Rail sections with arrow buttons
- Project cards

Structural parity status:

- Desktop latest Svelte remains about 1.97x taller than original.
- Mobile length is comparable, but latest mobile reports `63px` overflow.
- Need element-level comparison of hero height, browse panel, first rail position, and rail card density.

Priority: P1 after submit/edit owner-state work.

### Reference

Original Streamlit structure:

- Platform-specific reference routes via query params: Power BI, Tableau, Data Studio, Streamlit
- Sort controls
- Project cards/load more/infinite-ish browsing
- Can route into detail with reference context

Current Svelte structure:

- Platform-specific URL routes
- Sort states
- Cards and load-more button
- Back context support in detail query state

Structural parity status:

- Platform breadth is present.
- Latest Svelte mobile reference pages are very long, especially Power BI and Data Studio around 7600px.
- Need verify card density and data correctness per platform, not only route existence.

Priority: P1/P2 depending on cutover scope.

### Power BI Hub

Original Streamlit structure:

- Topic routes: news, learning, community, cert
- Topic hero variations
- Topic content lists/cards/details

Current Svelte structure:

- `svelte_app/src/routes/powerbi/+page.svelte`
- Topic query support
- Topic-specific hero/content

Structural parity status:

- Latest Svelte desktop lengths are much lower than older captures and broadly reasonable: news 963, learning 1135, community 1697, cert 869.
- Need visual/manual review of topic navigation and item density, but no immediate structural blocker surfaced.

Priority: P2.

### About/Policy/Auth

Original Streamlit structure:

- About with gapyear hero/banner, team section, service flow, vision
- Policy pages
- Auth shell pages

Current Svelte structure:

- About, policy, login/signup/reset routes exist.
- Capture script does not detect their hero classes due selector coverage, so `no page hero detected` warnings are partly instrumentation defects.

Structural parity status:

- Routes exist and lengths are reasonable.
- Need update capture selector list before final sign-off.

Priority: P2.

## P0 Structural Gaps

1. **Edit parity cannot be judged yet.** Latest edit capture says `수정할 프로젝트를 찾을 수 없습니다.`. Need owner-owned project fixture or derive edit URL from `/my` correctly.
2. **Mobile overflow is repeated.** Latest Svelte captures show `218px` horizontal overflow on authenticated mobile pages. Need DOM overflow tracer.
3. **Submit/edit state matrix is incomplete.** Empty baseline exists, but typed/upload/manual-url/capture/PBIX/error/mobile states are not captured.
4. **Streamlit edit-only delete controls are not mapped.** Existing thumbnail delete and existing PBIX delete exist in Streamlit but not equivalently in Svelte.
5. **Progress UI parity is missing.** Streamlit shows operation progress for thumbnail capture/PBIX flows; Svelte mostly shows submit button pending text.

## P1 Structural Gaps

1. My Page needs profile edit, empty portfolio, unread badge, delete confirm captures.
2. Notifications needs header popover open, before/after auto-read, item click, empty state captures.
3. Detail needs anonymous/non-owner/owner, report-open, share-message, delete-confirm, reply-open captures.
4. Home needs element-level density comparison for hero/browse/first rail.
5. Reference needs platform data quality and card density checks.

## Required Capture Script Improvements

Before the next capture run, update capture automation to include:

- Hero selectors: `.submit-hero`, `.my-hero`, `.notification-hero`, `.policy-page-hero`, `.about-gapyear-hero`, `.project-detail-image-hero`.
- State fields in manifest: `auth_state`, `project_owner_state`, `fixture_project_id`, `workflow_state`.
- Element-level overflow tracing: list nodes whose right edge exceeds `window.innerWidth`, with selector, text sample, rect, computed width, min-width, display.
- Interaction states:
  - submit typed
  - submit thumbnail upload
  - submit thumbnail URL
  - submit capture selected
  - submit Power BI selected
  - submit validation error
  - edit owner loaded
  - edit existing thumbnail/PBIX states
  - my profile edit open
  - my delete confirm
  - notification popover open
  - detail report open
  - detail share message
  - detail owner delete confirm
  - comment reply open

## Completion Status

This pass completes a structural audit baseline, not final parity sign-off.

Completed:

- Existing capture inventory reviewed.
- Existing Streamlit baseline kept as source of truth.
- Latest Svelte full public/auth recapture completed from `127.0.0.1:5174`.
- Latest-vs-original size metrics generated.
- Focused page structure map completed.
- P0/P1 structural gaps identified.

Not complete:

- Original Streamlit was not freshly recaptured because `8501` was not running.
- Svelte edit owner-state capture is invalid with the known fixture.
- Interaction/state matrix captures are not yet complete.
- Mobile overflow root cause is not yet traced to exact elements.

## Next Action

The next implementation task should be the capture harness upgrade, not another visual tweak. Once the harness records owner/auth/workflow states and overflow elements, run the state matrix for Submit/Edit first. Only then should the remaining UI fixes be made.