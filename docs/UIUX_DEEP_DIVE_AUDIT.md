# UI/UX Deep Dive Audit: Streamlit Original vs Current Svelte

Audited on 2026-08-24 from the original Streamlit screenshots and a fresh current Svelte recapture.

## Inputs

- Original Streamlit captures: `artifacts/ui-parity/streamlit/`
- Current Svelte recaptures: `artifacts/ui-parity/svelte-current/`
- Side-by-side contact sheets: `artifacts/ui-parity/design-audit/`
- Design rubric: `docs/DESIGN_SYSTEM.md`
- Current parity report: `docs/UI_PARITY_CAPTURE_REPORT.md`
- Layout/harmony reaudit: `docs/UI_LAYOUT_HARMONY_DEEP_DIVE.md`

Generated comparison sheets:

- `artifacts/ui-parity/design-audit/core-desktop.png`
- `artifacts/ui-parity/design-audit/content-desktop.png`
- `artifacts/ui-parity/design-audit/static-auth-desktop.png`
- `artifacts/ui-parity/design-audit/core-mobile.png`
- `artifacts/ui-parity/design-audit/content-mobile.png`

Note: in-session image preview failed because the Windows sandbox image helper could not open local images. The audit therefore combines fresh screenshots, contact-sheet artifacts, screenshot dimension/color metrics, source-code inspection, and the design-system contract.

## Step 1. Design System Rubric

The Streamlit original is not just a collection of pages. It has a clear product rhythm:

- Light UI with `--folio-bg`, white surfaces, navy header, subtle blue-gray borders.
- Hero-first pages: left copy, right 16:9 visual, 220px-ish hero height, visual hidden on mobile when it would make the page too long.
- Dense but calm operational surfaces: submit, my page, notifications, detail should avoid marketing-like oversized sections.
- Home gallery is the visual center: logo header, animated hero, browse/search panel, horizontal rails, 16:9 overlay project cards.
- Metadata and actions should stay in one container. Detail actions should not be scattered across columns.
- Cards should have stable 16:9 dimensions, restrained hover, title 2 lines, summary 1 line, tags/metas compact.

Current Svelte now follows many of these contracts structurally, but several screens still feel different in density, page length, route breadth, and interaction model.

## Step 2. Global Differences

### 2.1 Page Density And Vertical Rhythm

The largest remaining UI/UX difference is density.

Representative screenshot heights:

| Screen | Streamlit desktop | Current Svelte desktop | Difference |
| --- | ---: | ---: | ---: |
| Home | 889px | 1683px | Svelte much taller |
| Detail | 3622px | 6942px | Svelte much taller |
| Submit | 1050px | 6849px | Svelte dramatically taller |
| My Page | 1039px | 6818px | Svelte dramatically taller |
| Notifications | 1028px | 6787px | Svelte dramatically taller |
| Power BI Learning | 3688px | 7066px | Svelte much taller |
| About | 3655px | 6973px | Svelte much taller |

This does not automatically mean every Svelte screen is visually worse. Some Svelte screens include full forms and expanded content that Streamlit may have captured in a collapsed/auth-specific state. But as a UX signal, Svelte currently tends to expose more vertical content at once and creates longer scroll paths.

Design impact:

- Streamlit feels more compact and app-like.
- Svelte feels more document-like on submit, my page, notifications, detail, and long content pages.
- The Svelte migration should decide whether longer pages are intentional. If not, the next pass should compress forms/panels and reintroduce section-level progressive disclosure.

### 2.2 First-Viewport Lightness

The first viewport of several Svelte screens is lighter/whiter than Streamlit.

Examples from first 900px:

| Screen | Streamlit very-light ratio | Svelte very-light ratio | Reading |
| --- | ---: | ---: | --- |
| Detail desktop | 0.585 | 0.795 | Svelte first screen is much emptier/lighter |
| Submit desktop | 0.493 | 0.697 | Svelte form entry feels more spacious and less dense |
| Notifications desktop | 0.633 | 0.710 | Svelte has less visual weight in the first viewport |
| Home mobile | 0.329 | 0.501 | Svelte mobile home is much lighter and likely less rail/card-forward |

Design impact:

- The Svelte UI has a cleaner modern feel, but some pages lose the Streamlit app density.
- The original often uses surface/border/card rhythm to make panels feel intentional even when light.
- Svelte should reduce large empty white zones, especially where users are managing content rather than reading a landing page.

### 2.3 Navigation Model

Streamlit exposes more of the product through a single-page app style query navigation:

- Reference supports Power BI, Tableau, Data Studio, Streamlit.
- Header has notification preview behavior.
- Power BI topic navigation is more visible in the original.

Svelte is URL-native and cleaner, but still simpler in several navigation surfaces:

- Reference now has platform-specific Svelte routes for Power BI, Tableau, Data Studio, and Streamlit; the remaining concern is whether each platform has enough tagged/url-detectable project data.
- Header notification is a badge/link rather than a preview popover.
- Some Streamlit query compatibility exists, but `/?project_id=...` currently returns 200 without clearly redirecting in the local smoke.

UX impact:

- Svelte is technically cleaner and more shareable.
- Streamlit exposes adjacent destinations more visibly.
- Before production cutover, decide whether disabled platform tabs and simpler notification nav are product decisions or unfinished parity.

## Step 3. Screen-By-Screen Audit

### 3.1 Home

What now matches better:

- Folio logo is restored in the header.
- Header active underline exists.
- 4-slide hero concept is present.
- Browse panel, search, popular tags, top-10 tag cap, and rail behavior have been ported.
- Project cards now use 16:9 overlay cards and auto-cover variants.

Remaining differences:

- Svelte desktop home is much taller than Streamlit: 1683px vs 889px. This suggests the current Svelte home exposes more content vertically or the rails/panels consume more height.
- Streamlit home captured as a compact gallery-first screen. Svelte appears more spacious and less compressed.
- Mobile home first viewport is much lighter in Svelte. This can make the app feel less content-dense and may delay the first meaningful project card.

Recommended next inspection:

- Confirm whether the first project rail appears above the fold on desktop and mobile.
- Check rail card width/spacing against Streamlit: Svelte should show enough neighboring cards to communicate horizontal browsing.
- Validate that hero carousel height and browse panel margins do not push gallery content too far down.

Priority: High, because Home is the product's reference screen.

### 3.2 Project Detail

What now matches better:

- Detail hero has been split into compact hero plus meta/action footer row.
- Right-side project card visual is preserved.
- Like/share/report/edit/delete are visible in one action area.

Remaining differences:

- Svelte detail remains much taller: 6942px vs Streamlit 3622px desktop, 8938px vs 7901px mobile.
- First viewport is much lighter in Svelte: 0.795 very-light ratio vs 0.585 Streamlit. The hero may still read as too empty compared with the original detail capture.
- Svelte includes richer visible report/share/owner controls, which is good functionally but can make the hero/action area feel busier unless compacted carefully.
- Back navigation differs: Streamlit returns to contextual gallery/back label; Svelte currently uses a simple home gallery link.

Recommended next inspection:

- Compare detail footer row button widths and alignment with Streamlit `Detail Action Bar` rules.
- Check whether report form expansion shifts content excessively.
- Preserve Svelte's improved report/share functionality, but keep default view compact.

Priority: High, because detail is the conversion/consumption screen.

### 3.3 Submit

What now matches better:

- Submit hero uses `/hero-submit.webp` with the shared image hero pattern.
- Copy now matches Streamlit more closely.

Remaining differences:

- Submit is the largest density gap: Streamlit desktop 1050px vs Svelte desktop 6849px; mobile 2789px vs 8845px.
- Streamlit's capture likely shows a tighter project editor flow, while Svelte exposes many sections in one long page.
- The Svelte form may be functionally more complete, but the UX burden is higher.

Recommended next inspection:

- Break submit into clearer progressive sections or collapsible advanced areas.
- Keep top-level required fields compact.
- Move PBIX/thumbnail advanced operations below a clear secondary boundary.
- Re-check mobile form field heights and section gaps.

Priority: High for actual user submission completion.

### 3.4 My Page

What now matches better:

- My Page hero uses `/hero-my-page-v2.webp`.
- Profile summary was moved below the hero to keep the original shared hero rhythm.

Remaining differences:

- My Page is much taller in Svelte: 6818px desktop vs 1039px Streamlit; 8814px mobile vs 2778px Streamlit.
- Svelte may be showing expanded profile/edit/portfolio controls with more vertical padding than original.
- Streamlit profile summary design calls for centered values and compact stat chips. Svelte should be checked for that visual contract.

Recommended next inspection:

- Recompare profile summary: center alignment, 20px key values, compact stat chips.
- Compact portfolio management cards if they are full-width and vertically stacked.
- Ensure empty states clearly point to the next action.

Priority: Medium-high.

### 3.5 Notifications

What now matches better:

- Notifications uses `/hero-my-page-v2.webp` shared hero.
- List rows now follow compact state pill/title/time structure more closely.

Remaining differences:

- Svelte page is still far taller in captured full-page height. Some of this may be caused by authenticated state/capture height, but the page should be manually checked.
- Streamlit auto-marks notifications read when the page opens; Svelte requires explicit `모두 읽음`. This is not only UI but interaction semantics.
- Header notification preview popover is still absent in Svelte.

Recommended next inspection:

- Decide whether auto-mark-read on page open should be preserved.
- Decide whether header preview popover is required for launch parity or explicitly deferred.
- Check empty/loading/auth states visually.

Priority: Medium.

### 3.6 Reference

What now matches better:

- Power BI reference hero uses right-side logo and platform tabs.
- Sorting routes exist for latest/likes/views.

Remaining differences:

- Streamlit reference includes Tableau, Data Studio, and Streamlit platform pages. Svelte now exposes matching platform routes after the follow-up implementation.
- Streamlit reference captures are visually heavy/content-rich. Svelte Power BI reference is closer, but platform breadth is missing.
- Svelte first viewport has less navy/dark weight than Streamlit reference. It may look cleaner but less like the original reference hub.

Recommended next inspection:

- Treat non-Power BI reference platforms as either launch blockers or documented deferrals.
- If deferring, avoid presenting disabled tabs in a way that looks broken.
- Compare card density and sort tab positioning across reference pages.

Priority: High if full Streamlit replacement is the goal; medium if Power BI-first cutover is accepted.

### 3.7 Power BI Hub

What now matches better:

- Topic-specific heroes were ported for news, learning, community, and certifications.
- Certification visual uses PL-300 and BI specialist assets.

Remaining differences:

- Svelte Power BI Learning is extremely tall in the fresh capture: 7066px desktop and 8969px mobile. Original is also long, but Svelte is longer.
- Topic navigation still feels simpler than original Streamlit topic navigation and docs expectations.
- Learning/community content density needs review: Svelte may be stacking cards/rows with more vertical breathing room.

Recommended next inspection:

- Compare topic tab visibility and active state.
- Compress learning/community content rows if they have excessive vertical padding.
- Check mobile topic navigation stickiness or horizontal overflow behavior.

Priority: Medium-high.

### 3.8 About

What now matches better:

- Gapyear banner, Snowball Impact section, service flow, and vision image overlay were ported.
- Desktop and mobile current Svelte dimensions are now close to the original About: desktop 6973 vs 3655 still longer, mobile 8876 vs 7934 closer.

Remaining differences:

- Svelte desktop About is almost twice as tall as Streamlit, likely due to full-page capture behavior or extra layout spacing.
- Need manual side-by-side inspection of the vision label placement and image crop.
- Streamlit About has a very specific banner/caption rhythm; Svelte should preserve the caption's compactness.

Recommended next inspection:

- Compare gapyear banner crop and caption height.
- Compare Snowball image aspect ratio and team copy width.
- Compare vision label positions on desktop and mobile.

Priority: Medium.

### 3.9 Auth And Policy

What now matches better:

- Login/signup/reset and policy routes exist in Svelte.
- Policy pages are no longer missing.

Remaining differences:

- Auth pages are visually simpler in Svelte than the Streamlit auth shell.
- Policy pages are content-complete enough for cutover, but final legal copy approval is still separate from visual parity.
- Streamlit auth shell uses a specific centered card/surface rhythm; Svelte should be checked for card width, button hierarchy, and helper-link placement.

Priority: Medium-low for visual parity, high for production content/legal accuracy.

## Submit/Edit Follow-Up Lesson: State Parity Gap

The first submit/edit comparison under-detected UIUX gaps because it treated the form as static layout parity. The original Streamlit form should be audited as a stateful workflow, not a screenshot-only surface.

Required future comparison matrix for submit/edit:

| Workflow area | Required parity check |
| --- | --- |
| Hero preview | Title, one-liner, tags, thumbnail, counters, and visibility/status respond to current form state. |
| Thumbnail modes | `auto_cover`, `upload`, `manual_url`, and `capture` each have visible UI state and a clear preview/result expectation. |
| Platform/PBIX | Power BI selection changes both validation and PBIX upload affordance without hiding the primary Embed Code path. |
| Overview form | Basic info and resource links remain one structural group with a clear left/right relationship on desktop and stacked grouping on mobile. |
| Rich body editor | Formatting controls, section template, parsed payload fields, and saved detail rendering stay aligned. |
| Validation/error state | Required fields and mode-specific errors are visible near the affected workflow, not only as a page-level failure. |
| Edit-specific state | Existing project values, existing thumbnail, public/private setting, and replacement uploads are distinguishable from a new submit draft. |

Concrete lesson from the 2026-08-25 submit work: the Svelte hero initially reused a generic `ProjectCard`, which looked structurally close but missed the explicit thumbnail-preview UX. The fix was to add a dedicated hero thumbnail preview that exposes the selected thumbnail mode and renders uploaded/URL/default/capture-pending states.

## Step 4. Cross-Cutting UX Risks

### Risk 1. Svelte Is Cleaner But Less Compact

The migration has improved structure and URL semantics, but many current screens are longer. This can hurt operational flows: submit, my page, notifications, and edit should feel efficient.

### Risk 2. Some Parity Work Improved First-Viewport Appearance But Not Full-Page Flow

Hero assets and visual contracts are mostly restored. The next issue is page rhythm below the hero: section spacing, form density, list density, and card rail positioning.

### Risk 3. Streamlit Has More Route Breadth In Reference

Reference platform route breadth has been added in Svelte. The remaining product risk is data quality: projects need reliable `platform_key`, tags, or URL markers for each platform to populate the pages.

### Risk 4. Interaction Semantics Differ

Examples:

- Notifications read behavior: automatic in Streamlit, explicit in Svelte.
- Header notification preview: present in Streamlit, absent in Svelte.
- Detail back navigation: contextual in Streamlit, simpler in Svelte.
- Submit flow: likely more expanded in Svelte.

These are UIUX differences, not just visual differences.

## Step 5. Recommended Next Deep-Dive Order

1. Home first viewport and rail density.
2. Submit form compression/progressive disclosure.
3. Detail footer/action row and contextual back navigation.
4. My Page profile/portfolio density.
5. Reference platform breadth decision.
6. Notifications semantics: auto-read and header preview.
7. Power BI topic content density.
8. Auth/policy final polish.

## Step 6. Actionable Backlog

| Priority | Area | Action |
| --- | --- | --- |
| P0 | Home | Verify and tune above-the-fold hierarchy: logo/header, hero, browse panel, first rail visibility. |
| P0 | Submit | Reduce vertical burden with tighter sections or progressive disclosure for advanced fields. |
| P0 | Detail | Confirm compact footer row, contextual back behavior, and default report/share states. |
| P1 | Reference | Validate platform data quality and card population for Tableau/Data Studio/Streamlit routes before cutover. |
| P1 | My Page | Compact profile summary and portfolio management cards. |
| P1 | Notifications | Decide auto-read vs explicit read behavior and header preview popover scope. |
| P1 | Power BI | Tune topic content density and topic navigation visibility. |
| P2 | Auth/Policy | Polish auth shell and get final legal copy approval. |

## Current Conclusion

The Svelte app has closed many visual parity gaps at the component level: logo, heroes, cards, rails, About visuals, Submit/My Page/Notifications hero assets, and Detail action grouping. The remaining gap is now less about missing assets and more about UI rhythm: page length, density, interaction semantics, and product breadth.

For a Cloudflare cutover, the most important question is whether the Svelte app should match Streamlit's compact operational feel or intentionally move toward a more expanded web-app layout. If the answer is parity, the next design pass should focus on compression and first-viewport utility rather than adding more visual elements.