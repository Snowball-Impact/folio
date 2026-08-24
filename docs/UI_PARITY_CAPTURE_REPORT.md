# UI Parity Capture Report

Captured on 2026-08-24 from local Streamlit and local Svelte Cloudflare preview.

## Capture Set

- Streamlit base: `http://127.0.0.1:8501`
- Svelte base: `http://127.0.0.1:8788`
- Capture manifest: `artifacts/ui-parity/manifest.md`
- Streamlit screenshots: `artifacts/ui-parity/streamlit/`
- Svelte screenshots: `artifacts/ui-parity/svelte/`
- Viewports: desktop `1440px`, mobile `390px`
- Authenticated captures used `FOLIO_TEST_ID` and `FOLIO_TEST_PW` from local env.

Total captured screenshots: 70 PNG files.

## Screen Coverage

| Area | Streamlit | Svelte | Status |
| --- | --- | --- | --- |
| Home gallery | `/?page=Home` | `/` | Covered in both |
| Project detail | `/?page=Home&project_id=...` | `/projects/[id]` | Covered in both |
| Power BI content | `/?page=Power BI&topic=...` | `/powerbi` | Covered, but information architecture differs |
| Power BI references | `/?page=Reference&platform=powerbi` | `/references/powerbi` | Covered in both |
| Auth login | `/?page=Login` | `/login` | Covered in both |
| Signup | `/?page=Sign Up` | `/signup` | Covered in both |
| Password reset | Login inline reset flow | `/reset-password` | Covered differently |
| Submit project | `/?page=Submit` | `/submit` | Covered in both |
| My page | `/?page=My Page` | `/my` | Covered in both |
| Notifications | `/?page=Notifications` | `/notifications` | Covered in both |
| Project edit | `/?page=My Page&edit_project=...` | `/projects/[id]/edit` | Covered, but tested project may not be editable by test user |
| About | `/?page=About` | `/about` | Missing in Svelte, captured as 404 |
| Policy | `/?page=Policy&type=...` | `/policy?type=...` | Missing in Svelte, captured as 404 |
| Tableau/Data Studio/Streamlit references | `/?page=Reference&platform=...` | no route | Missing in Svelte |
| Profile / portfolio | `/?page=Profile`, `/?page=My Portfolio` | no route | Missing in Svelte |

## Main Differences

### 1. Navigation Scope

Streamlit has a broader header model:

- Anonymous: Home, About, Power BI menu, Submit, Login
- Authenticated: Home, About, Power BI menu, Submit, My Page, Logout, Notifications
- Power BI popover links to news, community, learning, certifications, and Power BI references
- Reference platform menu exists in code for visible reference platforms

Svelte has a simpler top nav:

- Anonymous: Home, References, Power BI, Login, Signup
- Authenticated: Home, References, Power BI, Submit, My Page, Notifications, user identity, Logout

Impact: Svelte is cleaner and URL-native, but it does not yet expose About, policy, profile, portfolio, or per-topic Power BI navigation from the header.

### 2. Power BI Content Structure

Streamlit separates Power BI content by query topic:

- `topic=news`
- `topic=learning`
- `topic=community`
- `topic=cert` / `certifications`
- Power BI reference entry via the Power BI menu

Svelte currently consolidates Power BI content into `/powerbi`.

Impact: Svelte has the content hub working, but parity with Streamlit's topic-specific URL states and menu behavior is incomplete.

### 3. Reference Platform Scope

Streamlit captures include:

- Power BI
- Tableau
- Data Studio
- Streamlit

Svelte currently implements only:

- `/references/powerbi`
- sort states `latest`, `likes`, `views`

Impact: This matches the Svelte phase priority for Power BI first, but it is not full Streamlit parity.

### 4. Static Service Pages

Streamlit includes:

- About
- Privacy policy
- Terms policy

Svelte returned 404 for:

- `/about`
- `/policy?type=privacy`

Impact: These are required before production cutover if Cloudflare Svelte is replacing the Streamlit public site.

### 5. Authenticated Account Surface

Both apps cover submit, my page, notifications, and edit entry points.

Known limitation in this capture:

- The known public project ID was used for edit screenshots.
- If the test account is not the owner, the Svelte edit route shows the protected/not-found state rather than a populated edit form.
- A follow-up owner-owned fixture project should be created for visual edit-form parity.

### 6. Routing Model

Streamlit uses query-param routing:

- `/?page=Home`
- `/?page=Reference&platform=powerbi`
- `/?page=Home&project_id=...`

Svelte uses real URL routes:

- `/`
- `/references/powerbi`
- `/projects/[id]`

Impact: Svelte improves sharability and deployment semantics, but old query-param URLs need redirect or compatibility decisions before migration.

## Priority Gaps Before Cutover

1. Add Svelte About page.
2. Add Svelte policy pages or static policy route handling.
3. Decide whether non-Power BI reference platforms are in scope for initial cutover.
4. Add Power BI topic URL states or tabs if Streamlit parity is required.
5. Capture edit screen with an owner-owned fixture project.
6. Add redirect compatibility for important Streamlit query-param URLs.
7. Manually review generated screenshots in `artifacts/ui-parity/` for visual spacing, mobile overflow, and header differences.

## Notes

- Browser connector was unavailable in this session, so screenshots were produced with local Selenium/Chrome automation.
- Image files were generated successfully, but in-session image preview was blocked by the Windows sandbox helper. The files are available in the workspace for manual review.
- Local Svelte verification had already passed before this capture set.

