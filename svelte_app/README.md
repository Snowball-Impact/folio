# FOLIO Svelte Spike

SvelteKit 기반 FOLIO 공개 조회 화면 스파이크입니다. 현재 범위는 Phase 1 P0에 해당하는 홈(`/`)과 프로젝트 상세(`/projects/:id`)입니다.

## Setup

```powershell
npm install
Copy-Item .env.example .env
```

`.env`에는 공개 Supabase 값만 넣습니다.

```text
PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-supabase-publishable-key
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
- Auth, likes, comments, submit/edit, Power BI Embed Token API, references, and Power BI content hub are not part of this first spike.
