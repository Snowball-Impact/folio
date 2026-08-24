# FOLIO Svelte Spike

SvelteKit 기반 FOLIO Cloudflare 전환 앱입니다. 현재 범위는 공개 조회뿐 아니라 홈(`/`), 프로젝트 상세(`/projects/:id`), Power BI 레퍼런스(`/references/powerbi`), Power BI 콘텐츠 허브(`/powerbi`), 인증/온보딩, 프로젝트 등록·수정, 마이페이지, 알림, 좋아요/댓글, 썸네일/PBIX 서버 엔드포인트까지 포함합니다.

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
CHROME_BINARY_PATH=
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
npm run verify
```

Equivalent expanded commands:

```powershell
npm run check
npm run build
npm run smoke
npm run smoke:supabase
npm run smoke:security
```

## Cloudflare Preview And Deploy

```powershell
npm run build
npm run preview:cloudflare
npm run deploy:cloudflare
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
- Project submit at `/submit` creates authenticated `projects` rows with the existing title/body/link/platform/tag/visibility contract, can upload JPG/PNG/WebP thumbnails through a server endpoint backed by `SUPABASE_SERVICE_ROLE_KEY`, can capture thumbnails through a server Playwright runtime when available, and can publish Power BI `.pbix` files through a server-only Power BI Import endpoint.
- My Page at `/my` lists the signed-in user's non-deleted projects, summarizes project/view/like/comment counts, edits `profiles.name/organization/bio`, links to detail/edit, and soft-deletes projects with the existing `status='deleted'` contract.
- Project edit at `/projects/:id/edit` lets the project author update the same basic title/body/link/platform/tag/visibility contract as submit, replace uploaded/captured thumbnails, and publish a replacement `.pbix` for Power BI projects.
- Notifications at `/notifications` list the signed-in user's `notifications`, expose unread counts in the header, mark one notification read when opening a project, and support marking all unread notifications read.
- Project detail supports authenticated like/unlike against the `likes` table and falls back to a login prompt for anonymous visitors.
- Project detail reads public comments, renders root comments with replies, lets authenticated users create root comments/replies/delete their own comments, creates in-app comment notifications for project authors, requests best-effort SMTP email notifications through a server endpoint, and marks project comment notifications/read state when the author opens the detail page.
- Automatic thumbnail capture requires Playwright and Chromium in the server runtime; without them the endpoint returns a safe setup error.

## Deployment Runtime

The spike now uses `@sveltejs/adapter-cloudflare` because the chosen deployment target is Cloudflare Workers/Pages. It is not a static-only deployment: project submission, PBIX publishing, thumbnail upload/capture, and SMTP notification endpoints still require server runtime access to private environment variables.

Automatic thumbnail capture is not Cloudflare-compatible as currently implemented because it depends on local Playwright/Chromium. For Cloudflare staging, use manual URL/upload thumbnails or replace capture with Cloudflare Browser Run before enabling it.

Use [../docs/CLOUDFLARE_DEPLOYMENT.md](../docs/CLOUDFLARE_DEPLOYMENT.md) for the Cloudflare deployment plan, [../docs/SVELTE_E2E_READINESS.md](../docs/SVELTE_E2E_READINESS.md) as the staging and production go/no-go checklist, then run [../docs/SVELTE_STAGING_QA_RUNBOOK.md](../docs/SVELTE_STAGING_QA_RUNBOOK.md) for manual staging QA.
