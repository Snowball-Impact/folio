# UI Parity Capture Report

Captured and audited on 2026-08-24 from local Streamlit, local Svelte Cloudflare preview, and source code inspection.

## Capture Set

- Streamlit base: `http://127.0.0.1:8501`
- Svelte base: `http://127.0.0.1:8788`
- Capture manifest: `artifacts/ui-parity/manifest.md`
- Streamlit screenshots: `artifacts/ui-parity/streamlit/`
- Svelte screenshots: `artifacts/ui-parity/svelte/`
- Svelte cutover recaptures after audit: `artifacts/ui-parity/svelte-cutover/`
- Viewports: desktop `1440px`, mobile `390px`
- Authenticated captures used `FOLIO_TEST_ID` and `FOLIO_TEST_PW` from local env.

Total captured screenshots: 70 PNG files.

## Visual Parity Reaudit

Reaudited after the 2026-08-24 cutover work because functional smoke coverage was ahead of visual parity. Conclusion: the Svelte app is closer on routes and data contracts than on original Streamlit visual behavior. Treat the items below as remaining visual parity blockers before claiming the Svelte UI matches the current FOLIO app.

### Confirmed Missing Or Weak Visual Parity

| Area | Streamlit/design-system source | Current Svelte state | Priority |
| --- | --- | --- | --- |
| Brand logo | `folio_app/components/layout.py` renders `static_image_src("logo.webp")`; design system requires left Folio logo image | Implemented after reaudit: Svelte header and favicon now use `/logo.webp` | Done |
| Header active state | `docs/common/DESIGN_SYSTEM.md` requires current page underline | Implemented after reaudit: nav links now receive active state and underline styling | Done |
| Home hero | `folio_app/pages/home.py` defines 4 `_HOME_HERO_SLIDES` with animated track and dots | Implemented after reaudit: Svelte home now uses a 4-slide animated carousel plus first-slide clone | Done |
| Home hero visual assets | Streamlit first slide uses `hero-preview-home.jpg`; other slides use guide/Power BI/study flows | Implemented after reaudit: Svelte uses `/hero-preview-home.jpg` plus guide/Power BI/study visual flows | Done |
| Home browse panel | Streamlit home includes project count-up, search input, popular tag pills, and platform scope handling | Implemented after reaudit: Svelte home now has count-up, GET search, popular tag pills, and query-driven filtering for Power BI scope | Done |
| Home gallery rails | `folio_app/components/home_gallery.py` renders `data-folio-rail`, arrow buttons, custom scrollbar, and smooth horizontal scrolling | Implemented after reaudit: `ProjectRail.svelte` now uses horizontal scroll rails, arrow buttons, thumb scrollbar, and mobile snap scrolling | Done |
| Project cards | Streamlit card system uses 16:9 tiles, stretched link, 24 auto-cover variations, and 5px blue hover border | Implemented after reaudit: Svelte cards now use 16:9 overlay cards with thumbnail support and 24 auto-cover gradient/pattern variants | Done |
| Static image assets | Streamlit static assets include `logo.webp`, `hero-preview-home.jpg`, `hero-submit.webp`, `hero-my-page-v2.webp`, `gapyear-hero-banner.jpg`, `snowball-impact.webp`, `vision-snowball.webp`, and platform logos | Implemented after reaudit: Svelte static now carries the Streamlit hero/brand/about/cert/platform image assets needed by current parity work | Done |
| Reference hero | Streamlit reference hero positions platform logo and tabs as the right-side visual contract | Implemented after reaudit: Svelte Reference hero now uses right-aligned platform logo and platform tab UI, with Power BI active | Done |
| Power BI heroes | Streamlit has topic-specific hero shells and visual styles for news/learning/community/certification | Implemented after reaudit: Svelte Power BI hub now uses topic-specific hero copy, gradients, logo visual, and certification badge/poster visual | Done |
| About page visuals | Streamlit About uses banner/brand imagery from `gapyear-hero-banner.jpg`, `snowball-impact.webp`, and `vision-snowball.webp` styles | Implemented after reaudit: Svelte About now ports the gapyear banner, Snowball Impact team section, service flow, and vision image/phase overlay | Done |
| Submit/My Page heroes | Streamlit shared hero uses page-specific image assets such as `hero-submit.webp` and `hero-my-page-v2.webp` | Implemented after reaudit: Svelte Submit and My Page now use shared image hero panels with the Streamlit page-specific assets | Done |
| Notifications visual polish | Streamlit Notifications uses the shared image hero plus a compact bordered notification panel/list | Implemented after reaudit: Svelte Notifications now uses `/hero-my-page-v2.webp` image hero and compact Streamlit-like notification rows | Done |
| Detail hero/action polish | Streamlit Project Detail uses a compact shared hero with card visual and footer action row | Implemented after reaudit: Svelte detail now separates title/card hero from meta/action footer row and tunes compact controls | Done |

### Reaudit Notes

- The previous report mixed functional parity and visual parity too closely. `npm run smoke` passing means routes/endpoints render and data contracts hold; it does not mean the screens match Streamlit.
- The capture manifest already includes Streamlit desktop/mobile screens for Home, Reference platforms, Power BI topics, About, Policy, Detail, Login, Signup, Submit, My Page, Notifications, and Edit. Those screenshots remain the visual baseline.
- In-session image preview was blocked by the Windows sandbox helper, so this reaudit relies on capture inventory, source-code structure, static asset inventory, and earlier Selenium/PIL nonblank checks. Manual side-by-side review of `artifacts/ui-parity/streamlit/` and `artifacts/ui-parity/svelte*/` is still required before final sign-off.

### Visual Parity Implementation Order

1. Done: move Folio logo/favicon assets into Svelte, replace text brand with image logo, and add active nav underline.
2. Done: rebuild the Svelte home hero as the Streamlit 4-slide carousel with dots and the same copy/visual concepts.
3. Done: add the home browse panel: count-up project total, search input, popular tag pills, and query-driven filtering.
4. Done: replace static home grids with horizontal `ProjectRail` behavior: arrow buttons, scroll snapping/smooth scroll, and scrollbar/thumb affordance.
5. Done: port card auto-cover variations and tune hover/border/card density against Streamlit captures.
6. Done: port Reference hero and Power BI topic-specific hero visual contracts, including certification badge/poster media.
7. Done: About, Submit, My Page, Notifications, and Detail visual contracts ported for the current parity pass.

## Codebase Audit Scope

The audit scanned these source areas:

- Streamlit routes: `folio_app/app.py`, `folio_app/pages/*`
- Streamlit UI components: `folio_app/components/*`
- Streamlit services: `folio_app/services/*`
- Svelte routes: `svelte_app/src/routes/**`
- Svelte components: `svelte_app/src/lib/components/*`
- Svelte client/server services: `svelte_app/src/lib/**/*.ts`
- Supabase schema and contracts: `supabase/schema.sql`, `docs/common/DATA_MODEL.md`, `docs/svelte/SVELTE_PHASE0_DATA_CONTRACTS.md`

## Screen And Feature Coverage

| Area | Streamlit | Svelte | Codebase status |
| --- | --- | --- | --- |
| Home gallery | `/?page=Home` | `/` | Covered in both |
| Home search/filter | search, tag, platform filters | platform fixed to Power BI snapshot | Partial in Svelte |
| Project detail | `/?page=Home&project_id=...` | `/projects/[id]` | Covered in both |
| Project view count | `increment_project_view_count` | `recordProjectView()` RPC | Covered in both |
| Like button | detail like button | `ProjectLikeButton.svelte` | Covered in both |
| Comments/replies | comment tree, reply, delete, pagination | comment tree, reply, delete | Partial: Svelte lacks explicit pagination UI |
| Comment notifications | DB notification + email request | DB notification + email API | Covered in both |
| Content report / 신고 | detail report dialog, `content_reports` | detail report form inserting `content_reports` | Added after audit; screenshot captured, live auth check still needed |
| Share button | project share button/handler | detail link copy control | Added after audit; screenshot captured |
| Power BI content | `/?page=Power BI&topic=...` | `/powerbi?topic=...` | Covered in both, UX differs |
| Power BI topic aliases | `news`, `learning`, `community`, `cert`/`certifications` | `news`, `learning`, `community`, `cert`/`certifications` | Covered after audit; smoke tested |
| Power BI references | `/?page=Reference&platform=powerbi` | `/references/powerbi` | Covered in both |
| Reference sorting | latest, likes, views-style order | `latest`, `likes`, `views` | Covered for Power BI |
| Tableau/Data Studio/Streamlit references | `platform=tableau/datastudio/streamlit` | `/references/tableau`, `/references/datastudio`, `/references/streamlit` | Routes added after audit; card population depends on platform-tag/url data quality |
| Auth login | `/?page=Login` | `/login` | Covered in both |
| Signup | `/?page=Sign Up` | `/signup` | Covered in both |
| Signup policy consent | Streamlit signup checkboxes | Svelte signup + onboarding gate | Covered differently |
| Password reset | inline reset/update flow in Login | `/reset-password` request/update flow | Covered differently |
| Onboarding | gated policy consent page | `OnboardingGate` + `/onboarding` | Covered in both |
| Submit project | `/?page=Submit` | `/submit` | Covered in both |
| Project edit | `/?page=My Page&edit_project=...` | `/projects/[id]/edit` | Covered in both |
| PBIX publish | Streamlit server/service flow | `/api/projects/[id]/powerbi-publish` | Covered in both |
| Thumbnail upload | Streamlit upload controls | `/api/projects/[id]/thumbnail` | Covered in both |
| Thumbnail capture | Streamlit capture controls | `/api/projects/[id]/thumbnail-capture` | Covered in both, Cloudflare runtime depends on Playwright availability |
| My page | `/?page=My Page` | `/my` | Covered in both |
| Profile edit | `Profile` redirects to My Page | profile edit is inside `/my` | Functionally covered in Svelte, no separate route |
| My portfolio | redirects to My Page | portfolio list inside `/my` | Functionally covered in Svelte, no separate route |
| Project delete | My Page/detail delete controls | My Page and owner detail delete controls | Covered after audit; anonymous legacy edit smoke reaches protected edit route |
| Notifications page | `/?page=Notifications` | `/notifications` | Covered in both |
| Header notification popover | Streamlit popover preview + mark all | nav badge + full page | Partial in Svelte |
| About | `/?page=About` | `/about` | Added after audit; recaptured |
| Policy pages | `/?page=Policy&type=privacy/terms` | `/policy/:type` plus `/policy?type=...` redirect | Added after audit; recaptured and smoke tested |
| Footer policy links | footer links to policy/contact/version | footer links to terms/privacy/contact/version | Covered after audit; recaptured |
| Analytics | GA virtual page views | no equivalent found | Missing in Svelte |

## Main Differences

### 1. Navigation Scope

Streamlit has a broader header model:

- Anonymous: Home, About, Power BI menu, Submit, Login
- Authenticated: Home, About, Power BI menu, Submit, My Page, Logout, Notifications
- Power BI popover links to news, community, learning, certifications, and Power BI references
- Notification popover shows recent items, project links, and mark-all-read

Svelte has a simpler top nav:

- Anonymous: Home, References, Power BI, Login, Signup
- Authenticated: Home, References, Power BI, Submit, My Page, Notifications, user identity, Logout

Impact: Svelte is cleaner and URL-native, but it does not yet expose About, policy, profile/portfolio aliases, per-topic Power BI navigation from the header, or the notification preview popover.

### 2. Power BI Content Structure

Both apps support topic states for Power BI content.

Streamlit topics:

- `topic=news`
- `topic=learning`
- `topic=community`
- `topic=cert` / `topic=certifications`
- Power BI reference entry via the Power BI menu

Svelte topics:

- `/powerbi` defaults to `news`
- `/powerbi?topic=learning`
- `/powerbi?topic=community`
- `/powerbi?topic=certifications`
- `/powerbi?topic=cert` alias

Status: Svelte has topic support, bundled CSV content, and the `cert` alias after audit. Remaining parity gaps are header topic navigation and any Streamlit-specific pagination/tab behavior.

### 3. Reference Platform Scope

Streamlit has code and captured screens for:

- Power BI
- Tableau
- Data Studio
- Streamlit

Svelte currently implements only:

- `/references/powerbi`
- sort states `latest`, `likes`, `views`

Status: Svelte now exposes platform-specific reference routes for Tableau, Data Studio, and Streamlit as well as Power BI. Remaining parity risk is data completeness and whether each platform has enough tagged/url-detectable projects.

### 4. Project Detail Actions

Streamlit project detail includes:

- Like/unlike
- Back to gallery/reference context
- Owner edit button
- Owner delete button
- Report dialog for non-owner content reports
- Share button/handler
- Comments, replies, delete, pagination

Svelte project detail now includes:

- Like/unlike
- Link copy share control
- Non-owner report form backed by `content_reports`
- Owner edit/delete controls
- Power BI embed/fallback viewer
- Resource links
- Report sections
- Comments, replies, delete
- Back to home gallery

Status: detail action parity was improved after the initial capture. Desktop/mobile screenshots and DOM overflow checks passed for anonymous detail. Remaining differences are contextual back navigation, comment pagination, visual action-bar polish, and authenticated owner/non-owner mutation checks.

### 5. Authenticated Account Surface

Both apps cover submit, my page, notifications, profile editing, project edit, and project deletion.

Differences:

- Streamlit routes `Profile` and `My Portfolio` back into My Page.
- Svelte implements the equivalent profile/portfolio surface inside `/my`, without alias routes.
- Svelte now exposes owner edit/delete actions on detail as well as project management in `/my` and `/projects/[id]/edit`.
- The visual edit capture used a known public project ID. If the test account is not the owner, the edit screenshot shows the protected/not-found path rather than a populated edit form.

### 6. Static Service Pages

Streamlit includes:

- About
- Privacy policy
- Terms policy
- Footer policy/contact links

Initial Svelte capture returned 404 for:

- `/about`
- `/policy?type=privacy`

Status: `/about`, `/policy/:type`, `/policy?type=...` redirects, and footer policy/contact/version links were added after this audit. Desktop/mobile cutover screenshots were captured under `artifacts/ui-parity/svelte-cutover/`, and DOM overflow checks passed.

### 7. Routing Model

Streamlit uses query-param routing:

- `/?page=Home`
- `/?page=Reference&platform=powerbi`
- `/?page=Home&project_id=...`
- `/?page=Power BI&topic=learning`
- `/?page=My Page&edit_project=...`

Svelte uses real URL routes:

- `/`
- `/references/powerbi`
- `/projects/[id]`
- `/powerbi?topic=learning`
- `/projects/[id]/edit`

Status: Svelte improves sharability and now redirects the main Streamlit query-param URLs for Home, project detail, Reference, Power BI, Login, Sign Up, Submit, My Page/Profile/My Portfolio, Notifications, About, and Policy. Project-detail legacy redirects and edit redirects still need live fixture smoke with real IDs.

## Design System Parity

Design audit reference: `docs/common/DESIGN_SYSTEM.md` plus Streamlit styles in `folio_app/styles/*` and Svelte global styles in `svelte_app/src/app.css`.

### Token Alignment

Svelte matches the core FOLIO tokens:

- `--folio-navy: #0b1f3f`
- `--folio-blue: #1459c8`
- `--folio-mint: #0a9485`
- `--folio-bg: #f4f7fd`
- `--folio-surface: #ffffff`
- `--folio-border: #dce5f7`
- `--folio-muted: #5c6f8a`
- `--folio-subtle: #eef3fd`
- Inter/system font stack
- 14px base body size, `line-height: 1.6`, `word-break: keep-all`

Impact: The Svelte app preserves the main visual language and should not feel like a separate brand.

### Layout And Surface Alignment

Covered well in Svelte:

- Light blue-gray app background with white surfaces.
- `max-width: 1440px` page shell.
- Dark navy sticky header.
- Hero sections use white surface, border, 16px radius, and desktop padding close to the design system.
- Cards and panels use restrained 8px radius.
- Project cards use 16:9 cover area, title/summary/tags/meta ordering, and restrained hover behavior.
- Buttons, chips, inputs, panels, and forms mostly follow the documented token set.

Differences:

- Svelte uses a global `--folio-shadow` and applies visible shadows to many hero/card surfaces; the design system emphasizes border/surface first and limited decoration.
- Streamlit's home gallery is rail-oriented; Svelte uses static grids for rails/references, so the home-gallery interaction feel is not identical.
- Svelte mobile heroes collapse to one column, but some visual panels remain visible where the design system says visuals can be hidden if they make mobile too long.

### Header Alignment

Streamlit design system header:

- Dark navy surface.
- Left logo image.
- Right nav.
- Current page is shown with underline.
- Power BI uses a popover menu.
- Notifications can appear as a popover with recent items.

Svelte header:

- Dark navy surface and right nav are aligned.
- Brand is text `FOLIO`, not the Streamlit logo image.
- No active underline/current-page state.
- Power BI is a single link, not a topic popover.
- Notifications are a badge link, not a preview popover.

Impact: Header is functionally simpler and visually close, but not design-system parity.

### Hero Alignment

Svelte generally follows the Page Hero rules:

- White surface.
- 1px border.
- 16px radius.
- Desktop padding close to `28px 42px 34px`.
- Large navy title, muted description, blue eyebrow.

Gaps:

- Streamlit reference hero has platform logo/tabs positioning rules; Svelte reference visual uses a two-column decorative mini panel and currently only Power BI.
- About hero and policy page hero do not exist in Svelte.
- CTA/spacer consistency for subpage heroes was not fully verified visually because in-session image preview was unavailable.

### Project Card Alignment

Svelte aligns with the card system in these ways:

- 16:9 card cover.
- Title, summary, tags, meta ordering.
- Tags are pill-shaped and subdued.
- Hover is restrained: slight translate and blue border.
- No iframe hover preview or large scale hover.

Gaps:

- Streamlit has 24 auto-cover color/pattern variations; Svelte currently uses a simpler gradient fallback unless `thumbnail_url` exists.
- Streamlit card rail behavior and incremental reference loading are richer than Svelte's static grid/load-more pattern.
- Need manual screenshot review for title clamp, Korean wrapping, and mobile card density.

### Detail Page Alignment

Streamlit design system calls out a compact detail action bar:

- View count, comment count, public status, link copy, and like should sit in a coherent action group.
- Like should remain adjacent to the action group.
- External result links should live below the representative result section.

Svelte detail:

- Like is shown in the hero action area.
- View/like/comment counts are metadata pills in the hero.
- External links are placed below the representative visual section, which is aligned.
- Link copy/share and report actions are absent.

Impact: Svelte detail is readable and token-aligned, but it does not yet match the detailed action-bar composition specified by the design system.

### Form And Profile Alignment

Svelte aligns with:

- Section-card form layout.
- 8px radius inputs/buttons.
- Primary/secondary button styles.
- Profile summary inside My Page.
- Empty states with next action.

Gaps:

- Streamlit form section headers use title-left/description-right patterns more explicitly; Svelte form headers are simpler stacked blocks.
- Streamlit project form includes richer platform/thumbnail/PBIX helper panels and preview affordances.
- Svelte profile summary is functionally equivalent but visually less close to the documented centered profile summary pattern.

### Footer Alignment

Streamlit footer includes:

- Copyright.
- Version/metadata center slot.
- Policy/contact links.

Svelte footer currently includes only:

- `Copyright © 2026 Snowball Impact. All rights reserved.`

Impact: Footer is not design-system parity and should be updated alongside About/policy routes.

### Design Priority Gaps

1. Add logo image usage or decide that text brand is the new standard.
2. Add active nav underline/current-page styling.
3. Add Power BI topic navigation in the header or another design-system-consistent place.
4. Add notification preview popover or document the simpler badge-link decision.
5. Add footer policy/contact links and optional version slot.
6. Bring Svelte detail action bar closer to `Detail Action Bar` guidance: view/comment/public/copy/like grouping.
7. Recreate or deliberately simplify Streamlit's 24 auto-cover card variation system.
8. Review mobile screenshots manually for hero visual hiding, card density, and Korean wrapping.

## Documentation Audit

Documentation audit references: `README.md`, `docs/README.md`, `docs/common/PROJECT_CONTEXT.md`, `docs/common/MVP_PRD.md`, `docs/migration/SVELTE_MIGRATION_PRD.md`, `docs/common/FOLIO_Community_PRD.md`, `docs/common/FOLIO_Admin_PRD.md`, `docs/common/USER_FLOWS.md`, `docs/svelte/CLOUDFLARE_DEPLOYMENT.md`, `docs/svelte/SVELTE_E2E_READINESS.md`, `docs/svelte/SVELTE_STAGING_QA_RUNBOOK.md`, `docs/common/COMMENT_FEATURE_PLAN.md`, `docs/common/DECISIONS.md`, `docs/common/ENGINEERING_PLAYBOOK.md`, `docs/common/SUPABASE_SETUP.md`, and `docs/streamlit/INTEGRATION_VALIDATION.md`.

### Current Migration Contract

The Svelte migration PRD originally staged the work as:

- P0/Phase 1: public home and project detail.
- P1/Phase 3: Power BI references and Power BI content hub.
- P2/Phase 4: auth, onboarding, likes, comments, reports, notifications.
- P3/Phase 5: submit/edit, thumbnail upload/capture, PBIX publish.
- P4/Phase 6: admin, community board, URL compatibility, production cutover.

Current Svelte code is already beyond the first public spike and covers most P0-P3/P5 surfaces. The remaining PRD-level work is therefore not only Streamlit visual parity; it is mostly cutover hardening plus P4/P6 operating features.

### Product Docs Gaps Beyond Current Svelte Scope

Docs that define product scope beyond the current Svelte app add these gaps:

- Community board: `docs/common/FOLIO_Community_PRD.md` defines a unified `/community` board for notices, questions, tips, and misc posts. It reuses the existing comment system, but still needs `community_posts`, board list/detail/write/edit/delete flows, pinned notices, view counts, and admin hiding/deletion. This is not the same as project detail comments and is not implemented in the Svelte app.
- Admin: `docs/common/FOLIO_Admin_PRD.md` defines `/admin` as a post-management console, not an approval system. It covers overview, project management, community management, comment management, user lookup, content reports, and Power BI curation workflow triggers. None of this is present in the Svelte UI.
- Content reports: Admin PRD and migration PRD keep `content_reports` as a required operations signal. Svelte now exposes project detail 신고 after audit, but the admin review surface is still missing.
- Content Feed: `docs/common/MVP_PRD.md` keeps a future `contents`/feed foundation for Power BI/Fabric updates, tutorials, jobs, newsletters, and collected links. The Svelte Power BI hub covers curated content display, but the broader feed product and DB-backed contents model remain future work.
- File report foundation: HTML/Markdown report support and Notebook/GitHub/nbviewer registration are documented future tracks. Current Svelte remains project/link/PBIX oriented.
- Social and GitHub import: `docs/common/MVP_PRD.md` still lists social links and GitHub URL import as TODO/future; neither should be treated as present Svelte parity.
- Analytics: MVP and Streamlit ADRs require GA-style page/event tracking. Streamlit has virtual pageview workarounds; Svelte has no equivalent tracking layer found in the audited code.

### Cutover And Routing Docs Gaps

- Query-param compatibility is now implemented for the main Streamlit URLs on the Svelte root route. Cloudflare smoke covers representative Home, About, Policy, Power BI `topic=cert`, and real fixture project detail/reference/edit legacy URLs.
- About and policy pages are documented public surfaces and are present in Streamlit. Svelte now has `/about`, `/policy/privacy`, `/policy/terms`, and `/policy?type=...` redirects; cutover screenshots were captured.
- Footer links and version/contact/policy placement are documented in project context and implemented in Streamlit. Svelte now exposes terms, privacy, contact, and version in the footer; cutover screenshots were captured.
- Header behavior is documented as a navigation and discovery surface, especially the Power BI topic menu and notification preview. Svelte exposes simpler links and should either implement the richer surface or document the intentional simplification.

### Cloudflare Docs Gaps

`docs/svelte/CLOUDFLARE_DEPLOYMENT.md` and the staging QA docs distinguish local Svelte feature completeness from Cloudflare production readiness:

- Cloudflare adapter build, bundled curation CSVs, route smoke, Supabase contract smoke, and security bundle scan are implemented verification gates.
- First Cloudflare staging should avoid pretending Workers is a long-running Node server. PBIX import over about 25 MB, local Playwright thumbnail capture, and socket-based SMTP need explicit decisions: disable, move to Cloudflare-native services, or offload to a separate Node/container worker.
- Real Cloudflare preview/deploy URL smoke is still required after dashboard variables/secrets are configured.
- Manual staging QA remains required for login, recovery, submit/edit, PBIX import, thumbnail upload/capture, comments, notifications, and email delivery.

### Documentation Consistency Notes

- `svelte_app/README.md` was stale at the top: it still described the app as a public-read spike while the current scope includes auth, onboarding, submit/edit, my page, notifications, comments, thumbnail endpoints, and PBIX endpoints. The opening scope should stay aligned with the expanded migration state.
- `docs/common/PROJECT_CONTEXT.md` still describes the main stack and deployment channel from the Streamlit-era handoff. It is useful historical context, but for current Svelte/Cloudflare acceptance the newer Svelte migration, Cloudflare, E2E, staging QA, retrospective, and this parity report should take precedence.
- `docs/README.md` says `legacy/` is historical context. Legacy wireframes can reinforce UX intent, but they should not override `PROJECT_CONTEXT.md`, live code, Supabase schema, or the current Svelte migration docs.
- `docs/common/COMMENT_FEATURE_PLAN.md` says comment edit and richer feedback were excluded from the first comment MVP, while `docs/common/MVP_PRD.md` mentions comment edit/admin delete as a broader community target. Treat comment edit as future product scope, not a current Streamlit-to-Svelte parity blocker.

### Documentation-Based Priority Additions

If the target is full documented product parity rather than only Streamlit public-page parity, add these to the cutover backlog:

1. Public/legal pages: implemented and recaptured in Svelte after audit; still needs final content approval.
2. Report flow: Svelte project detail 신고 UI and admin review contract.
3. URL compatibility: main Reference platform/sort query URLs now redirect to platform-specific Svelte routes; continue smoke testing real project/detail legacy URLs.
4. Analytics: Svelte pageview and key event tracking equivalent to the Streamlit GA contract.
5. Community board: `/community` list/detail/write/edit/delete plus shared comments.
6. Admin MVP: post-management console for projects, community posts, comments, reports, users, and Power BI curation workflow triggers.
7. Cloudflare heavy-feature decisions: PBIX size/runtime, thumbnail capture runtime, SMTP provider/runtime.
8. Future product scope: content feed, HTML/Markdown reports, Notebook/GitHub links, social links, and GitHub import.

## Data And Service Parity

Core Supabase contracts used by Svelte match the Streamlit data model:

- `home_project_snapshot`
- `project_detail_snapshot`
- `increment_project_view_count`
- `projects`
- `public_profiles`
- `likes`
- `comments`
- `project_comment_reads`
- `notifications`
- `policy_versions`
- `user_policy_consents`
- `powerbi_reports`

Svelte also implements server-only Power BI and upload endpoints:

- `GET /api/projects/[id]/powerbi-embed`
- `POST /api/projects/[id]/powerbi-publish`
- `POST /api/projects/[id]/thumbnail`
- `POST /api/projects/[id]/thumbnail-capture`
- `POST /api/comments/[id]/email-notification`

Notable Streamlit-side service areas not yet surfaced in Svelte UI:

- `content_reports` reporting workflow: detail form added after audit; admin review surface still missing
- Google Analytics virtual pageview tracking
- Header notification preview popover
- Multi-platform reference browsing beyond Power BI
- About/policy content pages: added after audit and recaptured

## Priority Gaps Before Cutover

1. Decide whether non-Power BI reference platforms are in scope for initial cutover.
2. Run authenticated live checks for report submit, owner edit/delete visibility, and owner delete mutation.
3. Decide whether contextual back navigation and comment pagination are required for initial cutover.
4. Capture edit screen with an owner-owned fixture project.
5. Manually review generated screenshots in `artifacts/ui-parity/` and `artifacts/ui-parity/svelte-cutover/` for final visual sign-off.
6. Make Cloudflare heavy-feature decisions for PBIX size/runtime, thumbnail capture runtime, and SMTP provider/runtime.

## Notes

- Browser connector was unavailable in this session, so screenshots were produced with local Selenium/Chrome automation.
- Image files were generated successfully, but in-session image preview was blocked by the Windows sandbox helper. Cutover recaptures were additionally checked with PIL dimensions/variance and Selenium DOM overflow measurements.
- During Streamlit capture, runtime deprecation warnings appeared for `st.cache` and `st.components.v1.html`; this does not block parity but is another reason to continue the Svelte migration.
- Local Svelte verification had already passed before this capture set.
