# FOLIO

좋은 데이터 시각화 프로젝트를 발견하고, 직접 경험하고, 함께 이야기하는 커뮤니티.

현재 FOLIO의 메인 애플리케이션은 저장소 루트의 SvelteKit 앱입니다. 기존 Streamlit MVP는 로컬 백업 zip(`archive/streamlit_app_20260909.zip`)과 historical 문서로만 보관하며, 새 개발과 배포는 SvelteKit + Cloudflare Pages 기준으로 진행합니다.

## 현재 구조

```text
package.json              # SvelteKit 앱 스크립트와 의존성
src/                      # SvelteKit routes, components, client/server lib
static/                   # 정적 이미지와 폰트
svelte.config.js          # Cloudflare adapter 설정
vite.config.ts            # Vite/SvelteKit 설정
wrangler.jsonc            # Cloudflare Pages runtime 설정
supabase/                 # Supabase schema
docs/                     # 현재 기준 문서와 historical 기록
archive/                  # 로컬 전용 백업(zip), Git 추적 제외
```

## 실행

Windows 로컬 개발은 Wrangler/Miniflare registry를 저장소 내부 `.runtime/`으로 고정하는 managed 명령을 사용합니다.

```powershell
npm.cmd ci
npm.cmd run dev:managed -- --Port 5174
```

일반 검증:

```powershell
npm.cmd run check
npm.cmd run build
npm.cmd run test:unit
```

전체 smoke 묶음:

```powershell
npm.cmd run verify
```

Playwright UI 검증:

```powershell
npm.cmd run test:ui
```

## 배포

기본 배포 채널은 Cloudflare Pages입니다.

Cloudflare Pages 설정:

```text
Root directory: 비움 또는 repository root
Build command: npm run build
Build output directory: .svelte-kit/cloudflare
Production branch: main
```

로컬 Cloudflare preview:

```powershell
npm.cmd run preview:cloudflare
```

수동 배포:

```powershell
npm.cmd run build
npm.cmd run deploy:cloudflare
```

필수 배포 문서는 [docs/svelte/CLOUDFLARE_DEPLOYMENT.md](docs/svelte/CLOUDFLARE_DEPLOYMENT.md)를 따릅니다.

## 환경 변수

루트 `.env` 또는 배포 환경 변수에 설정합니다. 값은 문서와 로그에 남기지 않습니다.

필수:

- `PUBLIC_SUPABASE_URL`
- `PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `APP_URL`
- `THUMBNAIL_STORAGE_BUCKET`

선택:

- Power BI/PBIX: `POWERBI_TENANT_ID`, `POWERBI_CLIENT_ID`, `POWERBI_CLIENT_SECRET`, `POWERBI_WORKSPACE_ID`, `POWERBI_API_BASE_URL`, `PBIX_MAX_UPLOAD_MB`
- Thumbnail capture: `THUMBNAIL_CAPTURE_ENABLED`, `THUMBNAIL_CAPTURE_PROVIDER`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_BROWSER_RENDERING_API_TOKEN`
- Email: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME`, `SMTP_USE_TLS`
- RUM: `PUBLIC_RUM_ENDPOINT`, `PUBLIC_RUM_SAMPLE_RATE`

## 주요 기능

- Supabase Auth 기반 로그인, 회원가입, 비밀번호 재설정
- 회원가입 단계의 필수 약관/개인정보 처리방침 동의
- 홈 프로젝트 탐색, 검색, 태그, 정렬, 카드 레일
- Power BI 레퍼런스와 큐레이션 콘텐츠 허브
- 프로젝트 등록, 수정, 삭제, 공개/비공개
- Tiptap 기반 프로젝트 본문 편집과 HTML sanitizer
- 썸네일 업로드, 직접 URL, 자동 캡처
- PBIX 업로드와 Power BI 게시/임베드 메타데이터
- 프로젝트 상세, 좋아요, 댓글, 1단계 답글, 알림, 선택적 이메일 알림

## 문서

새 작업 컨텍스트에서는 먼저 [docs/README.md](docs/README.md)를 읽고, 작업 대상에 맞는 문서를 선택합니다.

- 현재 프로젝트 상태: [docs/common/PROJECT_CONTEXT.md](docs/common/PROJECT_CONTEXT.md)
- 아키텍처: [docs/common/ARCHITECTURE.md](docs/common/ARCHITECTURE.md)
- 개발 원칙: [docs/common/ENGINEERING_PLAYBOOK.md](docs/common/ENGINEERING_PLAYBOOK.md)
- Svelte 개발 환경: [docs/svelte/SVELTE_DEVELOPMENT_ENVIRONMENT.md](docs/svelte/SVELTE_DEVELOPMENT_ENVIRONMENT.md)
- Cloudflare 배포: [docs/svelte/CLOUDFLARE_DEPLOYMENT.md](docs/svelte/CLOUDFLARE_DEPLOYMENT.md)
- Staging QA: [docs/svelte/SVELTE_STAGING_QA_RUNBOOK.md](docs/svelte/SVELTE_STAGING_QA_RUNBOOK.md)
- 운영 모니터링: [docs/ops/PRODUCTION_MONITORING.md](docs/ops/PRODUCTION_MONITORING.md)

과거 Streamlit 운영 문서와 Svelte migration 증거는 각각 [docs/streamlit/](docs/streamlit/)과 [docs/migration/](docs/migration/)에 historical record로 보관합니다.

## 레거시 Streamlit

Streamlit 구현은 현재 운영 기준이 아닙니다. 원본 소스는 로컬 백업 zip(`archive/streamlit_app_20260909.zip`)에 보관하고, repository root의 실행 기준은 SvelteKit입니다.
