# UI Parity Capture Report

Captured and audited on 2026-08-24 from local Streamlit, local Svelte Cloudflare preview, and source code inspection.

## Capture Set

- Streamlit base: `http://127.0.0.1:8501`
- Svelte base: `http://127.0.0.1:8788`
- Capture manifest: `artifacts/ui-parity/manifest.md`
- Streamlit screenshots: `artifacts/ui-parity/streamlit/`
- Svelte screenshots: `artifacts/ui-parity/svelte/`
- Viewports: desktop `1440px`, mobile `390px`
- Authenticated captures used `FOLIO_TEST_ID` and `FOLIO_TEST_PW` from local env.

Total captured screenshots: 70 PNG files.

## Codebase Audit Scope

The audit scanned these source areas:

- Streamlit routes: `folio_app/app.py`, `folio_app/pages/*`
- Streamlit UI components: `folio_app/components/*`
- Streamlit services: `folio_app/services/*`
- Svelte routes: `svelte_app/src/routes/**`
- Svelte components: `svelte_app/src/lib/components/*`
- Svelte client/server services: `svelte_app/src/lib/**/*.ts`
- Supabase schema and contracts: `supabase/schema.sql`, `docs/DATA_MODEL.md`, `docs/SVELTE_PHASE0_DATA_CONTRACTS.md`

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
| Content report / 신고 | detail report dialog, `content_reports` | no visible report UI | Missing in Svelte |
| Share button | project share button/handler | no visible share control | Missing in Svelte |
| Power BI content | `/?page=Power BI&topic=...` | `/powerbi?topic=...` | Covered in both, UX differs |
| Power BI topic aliases | `news`, `learning`, `community`, `cert`/`certifications` | `news`, `learning`, `community`, `certifications` | Partial: `cert` alias not supported in Svelte |
| Power BI references | `/?page=Reference&platform=powerbi` | `/references/powerbi` | Covered in both |
| Reference sorting | latest, likes, views-style order | `latest`, `likes`, `views` | Covered for Power BI |
| Tableau/Data Studio/Streamlit references | `platform=tableau/datastudio/streamlit` | no route | Missing in Svelte |
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
| Project delete | My Page/detail delete controls | My Page delete controls | Partial: Svelte lacks owner delete control on detail |
| Notifications page | `/?page=Notifications` | `/notifications` | Covered in both |
| Header notification popover | Streamlit popover preview + mark all | nav badge + full page | Partial in Svelte |
| About | `/?page=About` | `/about` | Missing in Svelte, captured as 404 |
| Policy pages | `/?page=Policy&type=privacy/terms` | `/policy?type=...` | Missing in Svelte, captured as 404 |
| Footer policy links | footer links to policy/contact | copyright-only footer | Partial in Svelte |
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

Impact: Svelte has topic support and bundled CSV content. Remaining parity gaps are header navigation, the `cert` query alias, and any Streamlit-specific pagination/tab behavior.

### 3. Reference Platform Scope

Streamlit has code and captured screens for:

- Power BI
- Tableau
- Data Studio
- Streamlit

Svelte currently implements only:

- `/references/powerbi`
- sort states `latest`, `likes`, `views`

Impact: This matches the current Svelte migration priority for Power BI first, but it is not full Streamlit parity.

### 4. Project Detail Actions

Streamlit project detail includes:

- Like/unlike
- Back to gallery/reference context
- Owner edit button
- Owner delete button
- Report dialog for non-owner content reports
- Share button/handler
- Comments, replies, delete, pagination

Svelte project detail includes:

- Like/unlike
- Power BI embed/fallback viewer
- Resource links
- Report sections
- Comments, replies, delete
- Back to home gallery

Impact: Svelte covers the core consumption flow, but owner actions, report/share affordances, contextual back navigation, and comment pagination are not at Streamlit parity.

### 5. Authenticated Account Surface

Both apps cover submit, my page, notifications, profile editing, project edit, and project deletion.

Differences:

- Streamlit routes `Profile` and `My Portfolio` back into My Page.
- Svelte implements the equivalent profile/portfolio surface inside `/my`, without alias routes.
- Streamlit detail also exposes owner delete/edit actions; Svelte centralizes project management in `/my` and `/projects/[id]/edit`.
- The visual edit capture used a known public project ID. If the test account is not the owner, the edit screenshot shows the protected/not-found path rather than a populated edit form.

### 6. Static Service Pages

Streamlit includes:

- About
- Privacy policy
- Terms policy
- Footer policy/contact links

Svelte returned 404 for:

- `/about`
- `/policy?type=privacy`

Impact: These are required before production cutover if the Cloudflare Svelte app replaces the Streamlit public site.

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

Impact: Svelte improves sharability and deployment semantics, but old query-param URLs need redirect or compatibility decisions before migration.

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

- `content_reports` reporting workflow
- Google Analytics virtual pageview tracking
- Header notification preview popover
- Multi-platform reference browsing beyond Power BI
- About/policy content pages

## Priority Gaps Before Cutover

1. Add Svelte About page.
2. Add Svelte policy pages or static policy route handling.
3. Add footer links for policy/contact destinations.
4. Decide whether non-Power BI reference platforms are in scope for initial cutover.
5. Add query compatibility redirects for important Streamlit URLs.
6. Add Power BI `topic=cert` alias and expose topic links from navigation if parity is required.
7. Add project detail report/share controls, or explicitly defer them.
8. Decide whether owner edit/delete controls should appear on Svelte detail or remain only in My Page.
9. Capture edit screen with an owner-owned fixture project.
10. Manually review generated screenshots in `artifacts/ui-parity/` for visual spacing, mobile overflow, and header differences.

## Notes

- Browser connector was unavailable in this session, so screenshots were produced with local Selenium/Chrome automation.
- Image files were generated successfully, but in-session image preview was blocked by the Windows sandbox helper. The files are available in the workspace for manual review.
- During Streamlit capture, runtime deprecation warnings appeared for `st.cache` and `st.components.v1.html`; this does not block parity but is another reason to continue the Svelte migration.
- Local Svelte verification had already passed before this capture set.
