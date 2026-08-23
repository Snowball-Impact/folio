# FOLIO Svelte Spike

SvelteKit 기반 FOLIO 공개 조회 화면 스파이크입니다. 현재 범위는 홈(`/`), 프로젝트 상세(`/projects/:id`), Power BI 레퍼런스(`/references/powerbi`), Power BI 콘텐츠 허브(`/powerbi`), 이메일 Auth 시작점(`/login`, `/signup`)입니다.

## Setup

```powershell
npm install
Copy-Item .env.example .env
```

`.env`에는 공개 Supabase 값과, 서버 전용 기능을 켤 때만 private 값을 넣습니다.

```text
PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-supabase-publishable-key
SUPABASE_SERVICE_ROLE_KEY=
APP_URL=http://localhost:5173
POWERBI_TENANT_ID=your-tenant-id
POWERBI_CLIENT_ID=your-client-id
POWERBI_CLIENT_SECRET=your-client-secret
POWERBI_WORKSPACE_ID=your-workspace-id
POWERBI_API_BASE_URL=https://api.powerbi.com/v1.0/myorg
PBIX_MAX_UPLOAD_MB=100
POWERBI_IMPORT_POLL_SECONDS=100
POWERBI_CAPTURE_READY_WAIT_SECONDS=10
THUMBNAIL_STORAGE_BUCKET=project-thumbnails
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_FROM_NAME=FOLIO
SMTP_USE_TLS=true
```

## Development

```powershell
npm run dev -- --host 127.0.0.1 --port 5173
```

## Validation

```powershell
npm run check
npm run build
```

## Current Scope

- Home calls `home_project_snapshot` with `p_platform_key='powerbi'`.
- Project detail calls `project_detail_snapshot`.
- Detail view count calls `increment_project_view_count` from the browser with a local anonymous UUID.
- Project detail calls `/api/projects/:id/powerbi-embed` for Power BI projects, renders with `powerbi-client` when an embed token is available, and falls back to the stored iframe URL.
- Power BI references query public `projects`, apply the Streamlit platform marker rules, support latest/likes/views sorting, and reuse `ProjectCard`.
- Power BI content hub reads curated CSV files from `docs/curation/powerbi_*` on the SvelteKit server and exposes news, learning, community, and certification views.
- Login and signup use Supabase Auth from the browser. Signup sends `name` and `organization` through user metadata so the existing `handle_new_user` trigger can create `profiles`.
- Password reset uses Supabase recovery links at `/reset-password` and accepts `code`, `token_hash`, or access/refresh token recovery callbacks before updating the password.
- Policy consent onboarding reads active `policy_versions`, checks `user_policy_consents`, gates authenticated public routes, and stores missing required consents before returning users to their requested page.
- Project submit at `/submit` creates authenticated `projects` rows with the existing title/body/link/platform/tag/visibility contract and can upload JPG/PNG/WebP thumbnails through a server endpoint backed by `SUPABASE_SERVICE_ROLE_KEY`.
- My Page at `/my` lists the signed-in user's non-deleted projects, summarizes project/view/like/comment counts, edits `profiles.name/organization/bio`, links to detail/edit, and soft-deletes projects with the existing `status='deleted'` contract.
- Project edit at `/projects/:id/edit` lets the project author update the same basic title/body/link/platform/tag/visibility contract as submit.
- Notifications at `/notifications` list the signed-in user's `notifications`, expose unread counts in the header, mark one notification read when opening a project, and support marking all unread notifications read.
- Project detail supports authenticated like/unlike against the `likes` table and falls back to a login prompt for anonymous visitors.
- Project detail reads public comments, renders root comments with replies, lets authenticated users create root comments/replies/delete their own comments, creates in-app comment notifications for project authors, and marks project comment notifications/read state when the author opens the detail page.
- SMTP email notification dispatch, PBIX publish, and automatic thumbnail capture are not part of this spike.

## Server Boundary Backlog

The remaining Streamlit parity features require server-only secrets or server-side browser automation:

- PBIX publishing: authenticated route action or endpoint must verify the Supabase user, accept a `.pbix`, enforce `PBIX_MAX_UPLOAD_MB`, call Power BI Import APIs with `POWERBI_WORKSPACE_ID`, poll import status, upsert `powerbi_reports`, and update the project status/embed URL.
- Automatic thumbnail capture: server runtime must provide Chromium/Playwright, render the external report or generated Power BI embed document, capture an image, upload it, and update `projects.thumbnail_url`.
- SMTP email notification dispatch: comment creation currently creates in-app `notifications`; email delivery needs a server-side worker/endpoint with `SUPABASE_SERVICE_ROLE_KEY` and SMTP settings.
- Deployment adapter: `@sveltejs/adapter-auto` builds locally but emits a warning until the final host is chosen. Pick the adapter for the target platform before production cutover.
