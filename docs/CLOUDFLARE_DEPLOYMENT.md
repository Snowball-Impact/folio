# Cloudflare Deployment Plan

FOLIO SvelteKit 앱을 Cloudflare에 배포하기 위한 기준 문서다. 현재 앱은 공개 조회 화면뿐 아니라 Supabase service role endpoint, PBIX 게시, 썸네일 업로드/캡처, SMTP 댓글 이메일 알림을 포함하므로 정적 호스팅만으로는 부족하다.

## Decision

Cloudflare 배포 타깃은 Cloudflare Pages static-only가 아니라 SvelteKit Cloudflare adapter가 생성하는 Worker/Pages runtime이다.

Cloudflare 공식 SvelteKit Workers 가이드는 기존 SvelteKit 프로젝트에서 `wrangler deploy`가 SvelteKit을 감지해 `@sveltejs/adapter-cloudflare`, `.svelte-kit/cloudflare/_worker.js`, `.svelte-kit/cloudflare` assets, `nodejs_compat` 설정을 생성한다고 설명한다.

Cloudflare Pages 가이드도 SvelteKit preset의 build directory를 `.svelte-kit/cloudflare`로 안내한다. 따라서 FOLIO의 Cloudflare 전환은 `@sveltejs/adapter-node` 유지가 아니라 Cloudflare adapter 전환을 전제로 한다.

## Official Constraints To Design Around

- Workers Free plan CPU time is 10 ms. Workers Paid can use up to 5 min CPU time, default 30 sec.
- Workers memory is 128 MB per isolate.
- Request body max depends on Cloudflare account plan: Free/Pro 100 MB, Business 200 MB, Enterprise 500 MB by default.
- Worker compressed size is 3 MB on Free and 10 MB on Paid.
- SvelteKit Cloudflare builds target `.svelte-kit/cloudflare`.
- Browser automation on Cloudflare should use Browser Run with `@cloudflare/playwright` and a browser binding, not local Chromium from the filesystem.

Sources:

- https://developers.cloudflare.com/workers/framework-guides/web-apps/sveltekit/
- https://developers.cloudflare.com/pages/framework-guides/deploy-a-svelte-kit-site/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/browser-run/playwright/


## Current Implementation Status

Completed locally:

- `@sveltejs/adapter-cloudflare` is installed and active.
- `wrangler` is installed as a dev dependency.
- `svelte_app/wrangler.jsonc` defines `pages_build_output_dir=.svelte-kit/cloudflare`, `compatibility_date=2025-12-01`, and `nodejs_compat`.
- `npm.cmd run build` creates `.svelte-kit/cloudflare`.
- `npm.cmd run smoke:cloudflare` starts local `wrangler pages dev`, checks `/`, `/powerbi`, `/references/powerbi`, and verifies anonymous protected POST endpoints return 401.
- `npm.cmd run verify` passes with Cloudflare build, Cloudflare smoke, Supabase contract smoke, and security bundle scan.

Still requires staging validation:

- Cloudflare project creation and dashboard env/secrets.
- Real Cloudflare preview/deploy URL smoke.
- Auth redirect URL configuration in Supabase.
- PBIX, thumbnail capture, and SMTP decisions under Workers constraints.
## Compatibility Audit

| Area | Current implementation | Cloudflare fit | Action |
|---|---|---|---|
| Public routes | SvelteKit SSR/load, Supabase RPC | Likely compatible | Build with Cloudflare adapter and smoke test |
| Supabase browser auth | `@supabase/supabase-js`, public env | Compatible | Keep `PUBLIC_SUPABASE_*` |
| Supabase service role endpoints | `$env/dynamic/private`, fetch-based Supabase client | Likely compatible | Configure Cloudflare secrets |
| Power BI content hub | Runtime `node:fs/promises` reads CSV from `docs/curation` | Risky | Convert CSV to bundled static data or import as raw at build time |
| Thumbnail upload | `await file.arrayBuffer()` then Supabase Storage upload | Works for small files; memory-sensitive | Keep 5 MB limit, verify on Workers |
| PBIX upload | FormData file upload then Power BI Import | High risk at 100 MB due request body/account limit and 128 MB memory | Lower MVP limit for Cloudflare or stream/offload to separate service |
| PBIX polling | Long network wait loop | Possible on Paid, risky on Free | Prefer async job/short polling, document no-go on Free |
| Thumbnail capture | Dynamic import `playwright`, local Chromium/`CHROME_BINARY_PATH` | Not compatible as-is | Replace with Cloudflare Browser Run or disable capture on Cloudflare MVP |
| SMTP email | `node:net`, `node:tls` custom SMTP socket | Needs Workers TCP/TLS validation | Prefer HTTP email provider API for Cloudflare MVP |
| Smoke tests | `wrangler pages dev` smoke | Compatible locally | Use `npm.cmd run smoke:cloudflare` and `npm.cmd run verify` |

## Deployment Strategy

### Phase CF-0: Compatibility Prep

1. Done: install `@sveltejs/adapter-cloudflare` and Wrangler dev dependency.
2. Done: move adapter configuration from `@sveltejs/adapter-node` to Cloudflare adapter.
3. Done: add explicit `wrangler.jsonc` for reproducibility.
4. Done: add Cloudflare-specific preview/deploy/smoke commands.
5. Convert Power BI content CSV loading away from runtime filesystem access.
6. Run local `npm.cmd run check` and Cloudflare build.

Exit criteria:

- Cloudflare build produces `.svelte-kit/cloudflare`.
- Public routes still build.
- No private env is bundled into client assets.

### Phase CF-1: Public/Auth Staging

Scope:

- Home
- Project detail
- Power BI references
- Power BI content hub
- Login/signup/reset/onboarding
- Likes/comments/notifications if Supabase RLS passes
- Thumbnail upload only

Explicitly out of scope unless proven compatible:

- PBIX 100 MB import
- Local Playwright/Chromium thumbnail capture
- Raw SMTP socket email

Exit criteria:

- Cloudflare preview URL loads public routes.
- Supabase contract smoke passes.
- Manual staging QA public/auth/community flows pass.

### Phase CF-2: Heavy Feature Decisions

Choose one per feature.

PBIX:

- Option A: Lower `PBIX_MAX_UPLOAD_MB` for Cloudflare MVP and verify import memory behavior.
- Option B: Move PBIX import to a separate Node/Container worker and call it from Cloudflare.
- Option C: Keep PBIX disabled on Cloudflare until a queue/background architecture exists.

Thumbnail capture:

- Option A: Replace local Playwright with Cloudflare Browser Run.
- Option B: Move capture to a separate Node/Container worker.
- Option C: Disable capture and keep manual URL/upload modes.

SMTP:

- Option A: Replace raw SMTP with an HTTP email provider API.
- Option B: Validate Cloudflare TCP/TLS sockets with current SMTP provider.
- Option C: Disable email delivery while keeping in-app notifications.

## Recommended MVP Path

For first Cloudflare staging, ship this scope:

- Public browsing
- Auth/onboarding
- Project submit/edit/delete
- Likes/comments/in-app notifications
- Manual thumbnail URL
- Thumbnail upload
- Power BI iframe fallback
- Power BI content hub

Hold or feature-flag this scope:

- PBIX import over 25 MB
- Thumbnail capture
- SMTP email delivery

This gives us a deployable Cloudflare app without pretending Workers is a normal long-running Node server.

## Environment Mapping

Cloudflare variables/secrets:

Public/non-secret:

- `PUBLIC_SUPABASE_URL`
- `PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `APP_URL`
- `THUMBNAIL_STORAGE_BUCKET`
- `POWERBI_API_BASE_URL`
- `PBIX_MAX_UPLOAD_MB`
- `POWERBI_IMPORT_POLL_SECONDS`
- `POWERBI_CAPTURE_READY_WAIT_SECONDS`
- `SMTP_PORT`
- `SMTP_FROM_NAME`
- `SMTP_USE_TLS`

Secrets:

- `SUPABASE_SERVICE_ROLE_KEY`
- `POWERBI_TENANT_ID`
- `POWERBI_CLIENT_ID`
- `POWERBI_CLIENT_SECRET`
- `POWERBI_WORKSPACE_ID`
- `SMTP_HOST`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`

Note: `PUBLIC_*` values are browser-visible. Do not put service role, Power BI client secret, SMTP password, or provider tokens behind `PUBLIC_` names.

## Build Commands

Initial local commands after Cloudflare adapter work:

```powershell
cd svelte_app
npm.cmd install
npm.cmd run check
npm.cmd run build
```

Expected Cloudflare output:

```text
.svelte-kit/cloudflare
```

Dashboard Pages settings if using Pages Git integration:

```text
Framework preset: SvelteKit
Build command: npm run build
Build directory: .svelte-kit/cloudflare
```

Wrangler path if using Workers deploy:

```powershell
npx wrangler deploy
```

## No-Go Conditions

- Cloudflare build includes private env in client assets.
- Public/private/deleted project visibility differs from Supabase RLS expectations.
- PBIX upload buffers large files and causes memory failures.
- Thumbnail capture endpoint claims success without producing a Storage file.
- SMTP failure blocks comment creation.
- A feature silently degrades without clear user-facing message.

## Next Implementation Steps

1. Add Cloudflare adapter dependency and build config.
2. Replace Power BI content runtime filesystem reads.
3. Run Cloudflare build and fix adapter/runtime errors.
4. Add Cloudflare-specific deploy instructions to `svelte_app/README.md`.
5. Decide whether first Cloudflare staging disables PBIX/capture/SMTP or implements Cloudflare-native replacements.