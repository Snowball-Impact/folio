# FOLIO Svelte Spike

SvelteKit 기반 FOLIO 공개 조회 화면 스파이크입니다. 현재 범위는 홈(`/`), 프로젝트 상세(`/projects/:id`), Power BI 레퍼런스(`/references/powerbi`), Power BI 콘텐츠 허브(`/powerbi`), 이메일 Auth 시작점(`/login`, `/signup`)입니다.

## Setup

```powershell
npm install
Copy-Item .env.example .env
```

`.env`에는 공개 Supabase 값과, Power BI 토큰 API를 켤 때만 서버 전용 Power BI 값을 넣습니다.

```text
PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-supabase-publishable-key
POWERBI_TENANT_ID=your-tenant-id
POWERBI_CLIENT_ID=your-client-id
POWERBI_CLIENT_SECRET=your-client-secret
POWERBI_API_BASE_URL=https://api.powerbi.com/v1.0/myorg
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
- Project detail supports authenticated like/unlike against the `likes` table and falls back to a login prompt for anonymous visitors.
- Project detail reads public comments, renders root comments with replies, lets authenticated users create root comments/replies/delete their own comments, creates in-app comment notifications for project authors, and marks project comment notifications/read state when the author opens the detail page.
- SMTP email notification dispatch and submit/edit are not part of this spike.
