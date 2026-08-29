# Svelte 개발·테스트 환경 기준

작성일: 2026-08-28

이 문서는 현재 `svelte_app/` 코드와 UIUX 검증에 사용하는 실행 환경의 기준 문서다. Streamlit 원본 환경과 Svelte/Cloudflare 환경을 섞어 판단하지 않는다.

## 환경 구분

| 구분 | 기준 | 주소/명령 | 용도 |
|---|---|---|---|
| Streamlit 원본 | Python + Streamlit | `streamlit run app.py` / `http://127.0.0.1:8501` | 원본 기능·UI 비교 |
| Svelte 일반 개발 | SvelteKit + Vite | `npm.cmd run dev -- --host 127.0.0.1 --port 5173` | 빠른 컴포넌트 개발 |
| Svelte 관리형 개발 | SvelteKit + Cloudflare adapter + local Wrangler paths | `npm.cmd run dev:managed -- --Port 5174` | Windows에서 UIUX 검증 |
| Svelte Playwright UIUX | Playwright + Chromium, 독립 browser context | `npm.cmd run test:ui` | Svelte DOM·기능·데스크톱/모바일 캡처 |
| Cloudflare preview | Wrangler Pages runtime | `npm.cmd run preview:cloudflare` / `127.0.0.1:8788` | 배포 runtime smoke |

현재 Svelte의 배포 adapter는 `@sveltejs/adapter-cloudflare`다. `adapter-node`는 과거 마이그레이션 기록에 등장하는 historical state이며 현재 실행 기준이 아니다.

## 필수 파일과 변수

- 앱 코드: `svelte_app/`
- Svelte 설정: `svelte_app/vite.config.ts`
- 의존성: `svelte_app/package.json`, `svelte_app/package-lock.json`
- 원본 환경: 루트 `.env`
- Svelte 환경: `svelte_app/.env` 또는 실행 환경 변수
- 샘플 PBIX: `artifacts/test.pbix`
- 관리형 Wrangler 경로: 저장소 루트 `.runtime/`

공개 Supabase 값은 `PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_PUBLISHABLE_KEY`를 사용한다. service role, Power BI secret, SMTP password는 server-only 변수이며 문서·로그·캡처에 값을 남기지 않는다.

## 설치와 실행

```powershell
cd C:\workspace\folio\svelte_app
npm.cmd install
npm.cmd run dev:managed -- --Port 5174
```

`dev:managed`는 `XDG_CONFIG_HOME`과 `MINIFLARE_REGISTRY_PATH`를 저장소 내부 `.runtime/`으로 지정한다. 사용자 프로필의 Wrangler registry/log에 쓰다가 발생하는 Windows `EPERM`을 피하기 위한 실행 경로다.

## 검증 단계

### 정적·빌드 검증

```powershell
npm.cmd run check
npm.cmd run build
git diff --check
```

### Cloudflare runtime smoke

```powershell
npm.cmd run smoke
npm.cmd run smoke:supabase
npm.cmd run smoke:security
npm.cmd run verify
```

`verify`는 check, Cloudflare build, Wrangler route smoke, Supabase contract smoke, security smoke를 묶는다. 이것은 브라우저 UIUX parity를 보장하지 않는다.

### UIUX capture gate

```powershell
npm.cmd run diagnose:browser
npm.cmd run preflight:uiux
```

UIUX 캡처 전에는 다음 조건을 별도로 통과시킨다.

- 대상 서버에 리스너가 하나만 있다.
- `/`, `/my`, `/notifications`, `/submit`이 HTTP 200이다.
- 테스트 계정 key 존재 여부를 확인하되 값은 출력하지 않는다.
- `artifacts/test.pbix`가 존재한다.
- Browser runtime이 연결되어야 DOM/스크린샷을 `pass`로 판정한다.

Browser runtime이 없으면 서버·코드 조사는 계속할 수 있지만 DOM/캡처 증거는 `unknown`이다. Selenium/Playwright를 조용한 대체 수단으로 사용하지 않는다.

### Playwright 독립 검증 환경

Playwright는 Desktop/Chrome Browser 연동과 별개의 독립 Chromium을 실행한다. 현재 Svelte UIUX 검증에서는 다음 명령으로 사용한다.

```powershell
cd C:\workspace\folio\svelte_app
npx.cmd playwright install chromium
npm.cmd run dev:managed -- --Port 5174
npm.cmd run test:ui
```

현재 기본 프로젝트는 데스크톱 `1440x1000`과 모바일 `390x844`이며, `/`, `/my`, `/notifications`, `/submit`을 각각 실행한다. 결과는 `artifacts/playwright/report/`, `artifacts/playwright/test-results/`에 저장한다. Playwright의 기본 `baseURL`은 `http://127.0.0.1:5174`이므로, 관리형 서버가 다른 포트로 실행되면 테스트 명령과 캡처 보고서에 같은 `PLAYWRIGHT_BASE_URL`을 반드시 지정한다.

예를 들어 5174가 이미 사용 중이라 5176에서 서버를 실행했다면 다음처럼 연결 대상을 고정한다.

```powershell
$env:PLAYWRIGHT_BASE_URL = 'http://127.0.0.1:5176'
npm.cmd run test:ui
```

인증 workflow는 별도 setup에서 storage state를 생성한다. 인증 파일에는 쿠키와 localStorage가 들어갈 수 있으므로 저장소에 커밋하지 않고, draft 정리도 `folio-submit-draft:*` 키만 대상으로 한다. 독립 Playwright 결과는 Desktop Browser 세션의 증거가 아니며, 실제 Chrome 세션 검증은 별도 surface로 기록한다.

인증 테스트에서 Supabase 토큰 요청이 `200`이어도 세션 persistence와 보호 route의 `getSession()` 확인 사이에 짧은 경합이 생길 수 있다. 이 경우 제품 인증 실패로 분류하지 않고, 테스트 헬퍼가 성공 토큰 응답을 확인한 뒤 목적지 route를 한 번 재진입한다. 재진입 후에도 `/login`에 남거나 인증 오류 메시지가 있으면 실패로 기록한다.

기본 `npm.cmd run test:ui:auth`는 실제 DB·Storage·Power BI Workspace를 변경할 수 있는 `@mutation*` 테스트를 제외한다. 테스트 fixture를 명시하고 복구 조건을 확인한 경우에만 다음처럼 opt-in 실행한다.

```powershell
$env:PLAYWRIGHT_MUTATION_PROJECT_ID = '<fixture-project-id>'
$env:PLAYWRIGHT_PBIX_SAFE_PROJECT_ID = '<powerbi-fixture-project-id>'
$env:PLAYWRIGHT_PBIX_LIVE_PROJECT_ID = '<test-owned-powerbi-project-id>'
npx.cmd playwright test tests/uiux/authenticated-routes.spec.ts --grep '@mutation' --project=desktop --project=mobile
npx.cmd playwright test tests/uiux/authenticated-routes.spec.ts --grep '@mutation-pbix-safe' --project=desktop --project=mobile
npx.cmd playwright test tests/uiux/authenticated-routes.spec.ts --grep '@mutation-pbix-live' --project=desktop --project=mobile
```

`PLAYWRIGHT_MUTATION_PROJECT_ID` 썸네일 테스트는 기존 썸네일이 없는 `auto_cover` fixture에서만 실행되며, 업로드 후 auto-cover로 복구한다. PBIX 안전 테스트는 게시 실패 응답을 mock하므로 Workspace를 변경하지 않는다. 실제 PBIX 성공 재게시 테스트는 격리된 Power BI Workspace에서 별도로 수행한다.

PBIX 교체 성공의 클라이언트 orchestration은 별도의 비변경 인증 테스트에서도 확인한다. 이 테스트는 기존 Embed URL·`supported` 상태를 유지한 프로젝트 수정 payload, `artifacts/test.pbix` multipart 전달, 성공 응답 후 상세 이동을 mock으로 검증한다. 실제 성공 검증은 `PLAYWRIGHT_PBIX_LIVE_PROJECT_ID`를 명시한 경우에만 수행하며, 테스트 계정 소유 fixture와 복구 계획을 확인한 뒤 실행한다. 실제 Import 완료와 새 report 메타데이터 반영은 2026-08-28 테스트 계정 fixture에서 `succeeded`로 확인했다.

## 테스트 책임 범위

| 검증 | 닫히는 범위 | 닫히지 않는 범위 |
|---|---|---|
| `check`/`build` | Svelte 타입·빌드 오류 | 실제 인증·DB·브라우저 동작 |
| Cloudflare smoke | 공개 route, 익명 mutation 차단 | 실제 사용자 workflow |
| Supabase smoke | RPC·schema·RLS 계약 일부 | 실제 계정 권한 전체 |
| security smoke | client bundle secret leak, 익명 endpoint 차단 | 배포 환경의 모든 secret 설정 |
| UIUX capture | 동일 viewport의 DOM·상태·캡처 비교 | Browser runtime 미연결 상태 |
| staging QA | 실제 계정·PBIX·Storage·이메일 | 로컬 check/build 대체 불가 |

## 포트와 프로세스 규칙

- Streamlit 원본은 `8501`, Svelte 일반 개발은 `5173`, 관리형 UIUX 서버는 `5174`, Cloudflare preview는 `8788`을 사용한다.
 - 캡처 전에 대상 포트 리스너가 하나인지 확인한다.
 - 오래된 서버가 최신 코드처럼 보이는 경우 새 서버를 추가로 띄우지 말고 기존 프로세스와 포트를 먼저 정리한다.
- Playwright 실행 전에 `PLAYWRIGHT_BASE_URL`과 실제 서버 포트가 일치하는지 확인한다. 다른 포트를 바라본 404/구버전 결과는 제품 버그 증거로 사용하지 않는다.
- 원본과 Svelte를 비교할 때 viewport, 인증 상태, query/path, fixture, 실행 서버를 기록한다.
- Streamlit 상세 캡처는 기본 3초 대기만으로 로딩 셸을 저장할 수 있다. 실제 fixture를 비교할 때는 `tools/capture_streamlit_scroll.py`에 `--wait-for-text`, `--settle-seconds`를 지정하고, 인증 비교는 `--login`을 사용해 보이는 로그아웃 메뉴와 세션 유지 여부를 확인한다. 로그인 후 대상 페이지에서 다시 로그인 상태가 풀리면 캡처를 성공으로 분류하지 않는다.

## 관련 기준 문서

- `docs/common/ENGINEERING_PLAYBOOK.md`
- `docs/svelte/SVELTE_E2E_READINESS.md`
- `docs/svelte/SVELTE_STAGING_QA_RUNBOOK.md`
- `docs/svelte/CLOUDFLARE_DEPLOYMENT.md`
- `docs/migration/UIUX_ENVIRONMENT_RECOVERY_PLAN_2026-08-28.md`
