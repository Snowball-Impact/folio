# UIUX State Reaudit: Existing Captures

Reaudited on 2026-08-25 using the existing Streamlit and Svelte capture artifacts. This pass applies the lesson from the submit-page miss: visual parity must be checked as workflow-state parity, not only as page-level screenshot similarity.

## Inputs

- Original baseline: `artifacts/ui-parity/streamlit/`
- Previous Svelte baseline: `artifacts/ui-parity/svelte/`
- Current recapture baseline from 2026-08-24: `artifacts/ui-parity/svelte-current/`
- Generated focused comparison artifacts: `artifacts/ui-parity/state-reaudit/`
- Source references:
  - Streamlit project form: `folio_app/components/project_form.py`
  - Streamlit notifications: `folio_app/pages/notifications.py`
  - Streamlit header notifications: `folio_app/components/layout.py`
  - Streamlit profile/portfolio: `folio_app/pages/protected.py`, `folio_app/components/profile_summary.py`, `folio_app/components/portfolio_items.py`
  - Streamlit detail actions: `folio_app/pages/project_detail.py`, `folio_app/components/share.py`
  - Svelte submit/edit: `svelte_app/src/routes/submit/+page.svelte`, `svelte_app/src/routes/projects/[id]/edit/+page.svelte`
  - Svelte notifications/header: `svelte_app/src/routes/notifications/+page.svelte`, `svelte_app/src/lib/components/AuthNav.svelte`
  - Svelte my/detail: `svelte_app/src/routes/my/+page.svelte`, `svelte_app/src/routes/projects/[id]/+page.svelte`

Note: local image preview failed in the Windows sandbox, so this reaudit uses generated image metrics/contact sheets, capture inventory, prior reports, and source-code inspection. The focused contact sheet is available at `artifacts/ui-parity/state-reaudit/focused-first-viewport-contact-sheet.png` for manual review.

## Capture Validity

The existing captures are useful but not all equally current.

- `artifacts/ui-parity/svelte-current/` is newer than `artifacts/ui-parity/svelte/`, so it should be the primary Svelte comparison set.
- Submit/edit screenshots in `svelte-current/` predate the later Tiptap, overview, and hero thumbnail preview fixes. They are valid evidence of what was missed, but stale as proof of the current implementation.
- `desktop-edit-known.png` and `mobile-edit-known.png` are suspiciously small compared with the Streamlit edit captures. Treat them as likely protected/not-owner or incomplete-state captures until recaptured with an owner-owned fixture.
- The large Svelte heights for submit/my/notifications may include authenticated wrapper or capture-state artifacts. Do not interpret height alone as UX failure without DOM/state recapture.

## Metrics From Existing Captures

| Screen | Streamlit | Svelte current | Height ratio | Streamlit light@900 | Svelte light@900 | Reading |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| desktop-submit | 1424x1050 | 1424x6849 | 6.52 | 0.761 | 0.810 | Major capture/state mismatch plus real form-density risk. |
| mobile-submit | 500x2789 | 500x8845 | 3.17 | 0.758 | 0.806 | Same risk on mobile; old capture is stale after form fixes. |
| desktop-edit | 1424x1076 | 1424x6756 | 6.28 | 0.803 | 0.849 | Needs owner-state recapture; current image likely not enough for edit parity. |
| mobile-edit | 500x2756 | 500x8752 | 3.18 | 0.789 | 0.827 | Needs owner-state recapture and mobile workflow check. |
| desktop-my-page | 1424x1039 | 1424x6818 | 6.56 | 0.803 | 0.637 | Svelte has more visual weight, likely expanded management UI. |
| mobile-my-page | 500x2778 | 500x8814 | 3.17 | 0.789 | 0.704 | Portfolio/profile state likely too expanded or capture includes extra content. |
| desktop-notifications | 1424x1028 | 1424x6787 | 6.60 | 0.819 | 0.824 | Visual density similar at top, but height/state mismatch remains. |
| mobile-notifications | 500x2767 | 500x8783 | 3.17 | 0.736 | 0.760 | Needs recapture after confirming auto-read and header popover state. |
| desktop-detail | 1424x3622 | 1424x6942 | 1.92 | 0.765 | 0.882 | Svelte detail first viewport was much lighter/emptier in old capture. |
| mobile-detail | 500x7901 | 500x8938 | 1.13 | 0.757 | 0.600 | Mobile detail may be closer in length but structurally different. |

## Workflow-State Findings

### 1. Submit

Existing capture finding:

- The old Svelte submit capture showed a page-level match attempt but missed workflow signals. It did not prove parity for title/one-liner/tag changes flowing into the hero, thumbnail mode changes, upload preview, URL preview, capture-pending state, PBIX affordance, or validation locality.
- The old Svelte screenshot height was 6.52x the Streamlit desktop height, which made it obvious that capture analysis should have asked whether the form was in a comparable state.

Source-code parity baseline from Streamlit:

- Streamlit groups basic info and resource links into one `*_form_section_overview` container with two columns.
- Thumbnail and platform panels are not just controls; they are stateful affordances tied to preview, validation, upload/delete, and edit replacement behavior.
- Submit/edit forms use the same `render_project_form` structure and differ by visibility/delete/replacement options.

Current status after later fixes:

- Svelte now has `ProjectFormOverview` for the overview group.
- Svelte now has `ProjectHeroThumbnailPreview` for default/upload/URL/capture-pending states.
- Svelte now has Tiptap-based body editing.

Remaining required recapture states:

- Empty submit form.
- Typed title/one-liner/tags with hero preview updated.
- Thumbnail `upload` after file selection.
- Thumbnail `manual_url` after URL input.
- Thumbnail `capture` selected with no valid source and with valid source.
- Power BI selected, PBIX file control visible, Embed Code still primary.
- Validation error near submit attempt.
- Mobile stack for all above.

Priority: P0 recapture, because old screenshots no longer represent the current page.

### 2. Edit

Existing capture finding:

- The Svelte edit capture is not reliable as parity proof. Its file size and height profile suggest it may have captured a protected/not-owner or incomplete state instead of the populated owner edit form.
- The old comparison missed edit-specific state: existing thumbnail vs replacement thumbnail, existing Power BI report vs new PBIX, public/private status, cancel path, and submit result.

Source-code parity baseline from Streamlit:

- Edit reuses the same project form as submit but enables `show_visibility_setting`, existing thumbnail deletion, and existing PBIX replacement/delete paths.
- Visibility setting is part of the action workflow, not merely another resource input.

Current Svelte status:

- Edit now shares `ProjectFormOverview` with submit.
- Edit now has a hero thumbnail preview and a bottom public/private card.
- Svelte still needs a deliberate check for existing thumbnail replacement/delete parity and existing PBIX delete parity. Current code supports replacement upload but not a visibly equivalent delete control.

Priority: P0 owner-state recapture and gap decision.

### 3. My Page

Existing capture finding:

- Svelte current my-page capture is much taller than Streamlit. The top 900px is less light than Streamlit, meaning Svelte may show heavier/expanded controls rather than the compact profile-summary rhythm.
- Prior comparison treated profile and portfolio as broad coverage, but the workflow needs state checks: view mode, edit mode, empty portfolio, populated portfolio, unread comment badge, delete confirmation, and mobile actions.

Source-code parity baseline from Streamlit:

- `protected.py` renders a centered profile overview, an explicit profile edit mode, portfolio cards, view/edit/delete actions, unread comment notice, and empty project call-to-action.
- `profile_summary.py` and `portfolio_items.py` define compact information hierarchy.

Svelte source status:

- `/my` combines profile summary, edit form, portfolio list, edit/view/delete, delete confirmation, and empty handling.
- Needs visual recapture for profile edit open/closed states and delete confirmation. Static full-page captures do not cover these states.

Priority: P1 after submit/edit.

### 4. Notifications

Existing capture finding:

- The prior report said Svelte lacked auto-read behavior, but current Svelte code now marks unread notifications read after page load. This is a clear example of a stale conclusion if screenshots and source are not separated.
- Existing screenshots still do not prove header notification preview parity or item click/read behavior.

Source-code parity baseline from Streamlit:

- Notification page text explicitly says opening the page marks new notifications read.
- After rendering unread notifications, Streamlit calls `mark_all_notifications_read`.
- Header has a notification popover with recent items, unread count, mark-all, and view-all actions.

Svelte source status:

- `/notifications` now auto-marks unread items read after `listNotifications()` and keeps auto-read IDs for visual state.
- `AuthNav.svelte` has a notification submenu with recent item preview and mark-all/view-all controls.

Remaining required recapture states:

- Header with unread badge closed.
- Header popover open with recent notifications.
- Notifications page immediately after load, showing auto-read transition/message/state.
- Empty notifications state.
- Mobile header/menu behavior.

Priority: P1; not necessarily a functional gap now, but stale screenshots need replacement.

### 5. Project Detail

Existing capture finding:

- Old Svelte detail first viewport was much lighter than Streamlit and almost 2x taller overall on desktop. The capture did not prove detail action-bar parity.
- The old comparison should have separated owner, non-owner, anonymous, report-open, delete-confirm, share-message, and comment states.

Source-code parity baseline from Streamlit:

- Detail uses hero card, meta summary, share/action group, like, report, edit, delete, contextual back, representative result, external links, report body, comments, notification read handling.

Svelte source status:

- Svelte detail includes like, share, report modal, owner edit/delete, representative visual, external links, report sections, and comments.
- Remaining likely gaps are contextual back navigation, comment pagination, exact action grouping, and state-specific screenshots.

Priority: P1, with owner/non-owner/anonymous state recapture.

## Cross-Cutting Reaudit Conclusion

The old audit found many real gaps, but it also under-specified the verification method. The main problem was not only missing UI; it was insufficient state coverage.

Revised rule for future parity sign-off:

- A page is not parity-complete until its state matrix is captured.
- A capture is not valid unless the auth/user/project ownership state is recorded.
- A generic component that looks close is not enough when the original UI communicates a workflow result, such as thumbnail preview, unread/read transition, delete confirmation, or public/private status.
- If a screenshot is extremely taller/shorter than its pair, first suspect capture state mismatch before making design conclusions.

## Updated Backlog From This Reaudit

| Priority | Area | Task | Why |
| --- | --- | --- | --- |
| P0 | Submit | Recapture current submit after the Tiptap, overview, and hero-thumbnail fixes in empty/typed/upload/url/capture/mobile states. | Existing captures are stale and missed the preview workflow. |
| P0 | Edit | Recapture with an owner-owned project and cover existing thumbnail, replacement upload, public/private, PBIX, cancel/save states. | Existing edit capture is not reliable parity proof. |
| P1 | My Page | Recapture profile view, profile edit, empty portfolio, populated portfolio, unread comment badge, delete-confirm states. | Static page capture hides key management workflows. |
| P1 | Notifications | Recapture header popover, page auto-read, item click, mark-all, empty, and mobile states. | Current code appears closer than old report, but screenshots are stale. |
| P1 | Detail | Recapture anonymous/non-owner/owner plus report-open, share-message, delete-confirm, comment/reply states. | Detail parity is stateful, not just layout. |
| P2 | Docs | Keep this state matrix linked from future parity reports. | Prevent repeating screenshot-only audits. |

## Next Verification Shape

For the next capture run, the script should emit a manifest with these fields for every screenshot:

- `screen`
- `app`
- `viewport`
- `auth_state`
- `project_owner_state`
- `fixture_project_id`
- `workflow_state`
- `url`
- `screenshot_path`
- `dom_height`
- `viewport_light_ratio`
- `notes`

Without these fields, the screenshot set can show visual differences but cannot support a parity claim.