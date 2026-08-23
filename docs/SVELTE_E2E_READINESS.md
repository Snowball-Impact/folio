# Svelte E2E Readiness Checklist

This checklist is the handoff gate for moving the SvelteKit spike from local implementation to a staging or production-like environment.

## Goal

Validate that the SvelteKit app can replace the Streamlit public/user flows for home, project detail, auth, project submission, Power BI publishing, thumbnails, comments, notifications, and email delivery.

## Build Gate

- [ ] `npm.cmd install` completes in `svelte_app/`.
- [ ] `npm.cmd run check` returns 0 Svelte/TypeScript errors.
- [ ] `npm.cmd run build` completes with `@sveltejs/adapter-node`.
- [ ] The generated app starts with `node build`.
- [ ] The host exposes private env vars only to server code.

## Environment Gate

Required:

- [ ] `PUBLIC_SUPABASE_URL`
- [ ] `PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- [ ] `SUPABASE_SERVICE_ROLE_KEY`
- [ ] `APP_URL`
- [ ] `THUMBNAIL_STORAGE_BUCKET`

Power BI:

- [ ] `POWERBI_TENANT_ID`
- [ ] `POWERBI_CLIENT_ID`
- [ ] `POWERBI_CLIENT_SECRET`
- [ ] `POWERBI_WORKSPACE_ID`
- [ ] `POWERBI_API_BASE_URL`
- [ ] `PBIX_MAX_UPLOAD_MB`
- [ ] `POWERBI_IMPORT_POLL_SECONDS`
- [ ] `POWERBI_CAPTURE_READY_WAIT_SECONDS`

SMTP:

- [ ] `SMTP_HOST`
- [ ] `SMTP_PORT`
- [ ] `SMTP_USERNAME`
- [ ] `SMTP_PASSWORD`
- [ ] `SMTP_FROM_EMAIL`
- [ ] `SMTP_FROM_NAME`
- [ ] `SMTP_USE_TLS`

Thumbnail capture:

- [ ] Playwright is installed in the server runtime, or capture is explicitly accepted as disabled.
- [ ] Chromium is available through Playwright or `CHROME_BINARY_PATH`.
- [ ] The host allows Chromium sandbox requirements, memory, and request time.

## Supabase Contract Gate

- [ ] Apply `supabase/schema.sql` or equivalent patches to the remote project.
- [ ] `projects.thumbnail_mode` accepts `auto_cover`, `manual_url`, `capture`, and `upload`.
- [ ] `home_project_snapshot` returns `thumbnail_mode`.
- [ ] `project_detail_snapshot` returns `thumbnail_mode` and `platform_key`.
- [ ] `powerbi_reports` supports upsert on `project_id`.
- [ ] `notifications`, `project_comment_reads`, `comments`, and `likes` RLS policies match the Svelte browser/client usage.
- [ ] `project-thumbnails` Storage bucket is public or returns usable public URLs.

## Public Flow Tests

- [ ] `/` loads for anonymous users.
- [ ] Home project rails show Power BI-first content.
- [ ] `/projects/:id` loads a public published project.
- [ ] Deleted and private projects are not visible publicly.
- [ ] View count increments once per anonymous viewer/day.
- [ ] `/references/powerbi` loads and sorting works.
- [ ] `/powerbi` loads curated content tabs.

## Auth And Account Tests

- [ ] `/signup` creates a Supabase Auth user.
- [ ] Signup metadata creates or updates `profiles`.
- [ ] `/login` restores browser session.
- [ ] `/reset-password` accepts Supabase recovery callbacks.
- [ ] Required policy onboarding blocks authenticated routes until accepted.
- [ ] `/my` lists only the signed-in user's non-deleted projects.
- [ ] Profile name, organization, and bio updates persist.

## Project Mutation Tests

- [ ] `/submit` creates a public project.
- [ ] `/submit` creates a private project that does not appear publicly.
- [ ] `/projects/:id/edit` updates title/body/link/tag/visibility fields.
- [ ] `/my` soft delete sets `status='deleted'` and hides the project.
- [ ] Manual thumbnail URL persists.
- [ ] Thumbnail upload stores a file and updates `thumbnail_mode='upload'`.
- [ ] Thumbnail capture stores a file and updates `thumbnail_mode='capture'`.

## Power BI Tests

- [ ] Existing public iframe URL renders through fallback.
- [ ] Published PBIX project returns `/api/projects/:id/powerbi-embed`.
- [ ] Embed token is generated server-side and is not stored in DB.
- [ ] PBIX upload rejects non-`.pbix` files.
- [ ] PBIX upload enforces `PBIX_MAX_UPLOAD_MB`.
- [ ] PBIX import success upserts `powerbi_reports`.
- [ ] PBIX import success sets project `status='published'`.
- [ ] PBIX import failure sets project `status='failed'` without exposing secrets.
- [ ] PBIX plus automatic thumbnail capture waits for `POWERBI_CAPTURE_READY_WAIT_SECONDS` and captures the report page.

## Community Tests

- [ ] Authenticated users can like/unlike a project.
- [ ] Anonymous visitors see a login prompt for likes/comments.
- [ ] Authenticated users can create root comments.
- [ ] Authenticated users can create one-level replies.
- [ ] Authors can delete their own comments.
- [ ] Project authors receive in-app comment notifications.
- [ ] Opening the project marks related notifications as read.
- [ ] SMTP comment email is sent when configured.
- [ ] Missing or failing SMTP does not fail comment creation.

## Security Checks

- [ ] Service role key is not included in client bundle or public env.
- [ ] Power BI client secret is not included in client bundle.
- [ ] Embed tokens are returned only from server endpoints.
- [ ] Project mutation endpoints verify bearer token and project ownership.
- [ ] Thumbnail and PBIX endpoints reject anonymous requests.
- [ ] Comment email endpoint only accepts requests from the comment author.

## Go/No-Go

Go when:

- [ ] Build gate passes.
- [ ] Environment gate is fully configured or intentionally waived.
- [ ] Supabase contract gate passes against the target remote database.
- [ ] All public, auth, project, Power BI, and community tests pass.
- [ ] Known failures are documented with owner, severity, and mitigation.

No-go when:

- [ ] Auth/session recovery is unreliable.
- [ ] Public/private/deleted visibility rules fail.
- [ ] PBIX publish leaks secrets or stores raw PBIX files.
- [ ] Server endpoints fail without useful user-facing errors.
- [ ] Thumbnail capture blocks project creation instead of failing safely.
