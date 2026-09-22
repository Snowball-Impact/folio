# FOLIO 프로젝트 포트폴리오 자료

이 문서는 FOLIO를 채용 포트폴리오, 프로젝트 소개서, 발표 자료로 재구성할 때 사용하는 사실 기반 원자료다. 기능을 나열하기보다 문제, 설계 판단, 보안 경계, 운영 검증, 남은 과제를 하나의 서사로 연결한다.

## 한 문장 요약

FOLIO는 데이터 시각화 프로젝트를 발견하고 직접 경험하고 공유할 수 있도록 만든 SvelteKit 기반 커뮤니티 플랫폼으로, Power BI·Tableau·Looker Studio·Streamlit·GitHub Pages 임베드와 사용자 프로젝트 관리, 댓글·좋아요·알림을 하나의 운영 가능한 서비스로 통합했다.

## 문제와 목표

데이터 시각화 결과물은 이미지나 링크만으로는 분석 맥락과 실제 인터랙션을 전달하기 어렵다. FOLIO는 다음 문제를 해결하는 것을 목표로 했다.

- 프로젝트의 문제 정의·데이터·분석 과정·인사이트와 실제 결과물을 한 화면에서 연결한다.
- 외부 대시보드를 상세 페이지에서 바로 경험하되, 임베드가 불가능하거나 만료된 경우에도 원본 링크와 맥락을 보존한다.
- 사용자가 자신의 프로젝트를 등록하고 공개 범위, 썸네일, PBIX 게시 상태, 댓글과 알림을 관리할 수 있게 한다.
- Cloudflare Pages와 Supabase를 이용해 작은 팀도 반복 가능한 배포·검증·운영 체계를 갖추도록 한다.

## 제품 표면

| 영역 | 구현 근거 |
|---|---|
| 탐색 | 홈 카드 레일, 검색·태그·정렬, Power BI 레퍼런스 허브 (`src/routes/+page.svelte`, `src/lib/projects.ts`) |
| 상세 경험 | 프로젝트 본문, 외부 대시보드 iframe, 외부 링크 fallback, 댓글·좋아요 (`src/routes/projects/[id]/`) |
| 창작자 관리 | 프로필, 통계, 내 프로젝트의 보기·수정·삭제, 댓글 unread 상태 (`src/routes/my/+page.svelte`) |
| 등록·수정 | 본문 sanitizer, URL 정규화, 썸네일 업로드/캡처, PBIX 게시 흐름 (`src/routes/submit/`, `src/routes/projects/[id]/edit/`) |
| 커뮤니티 | 댓글, 1단계 답글, 알림, 선택적 이메일 알림 (`src/lib/comments.ts`, `src/lib/notifications.ts`) |
| 분석 | GA4·RUM 계약·Meta Pixel을 CSP와 함께 관리 (`src/routes/+layout.svelte`, `docs/svelte/SVELTE_RUM_CONTRACT_2026-08-29.md`) |

## 기술 아키텍처

```text
Browser
  -> SvelteKit routes / server endpoints
  -> Cloudflare Pages runtime
      -> Supabase Auth / Postgres + RLS / RPC / Storage
      -> Power BI API 및 Browser Rendering
      -> SMTP provider
```

- SvelteKit은 파일 기반 라우팅, SSR, 서버 endpoint, 클라이언트 UI를 담당한다.
- Cloudflare Pages는 `@sveltejs/adapter-cloudflare` 기반으로 배포한다.
- Supabase는 Auth·PostgreSQL·RLS·Storage를 제공하고, 홈/상세 snapshot RPC로 화면에 필요한 payload를 묶는다.
- 서비스 역할 키, Power BI secret, SMTP password는 `src/lib/server/`와 서버 endpoint에서만 사용한다.
- Streamlit 구현은 현재 운영 코드가 아니라 `archive/` 백업과 historical 문서로 경계를 분리했다.

## 중요한 설계 판단

### 임베드는 정상·실패 상태를 모두 제품 경험으로 취급

외부 대시보드는 삭제, 권한 변경, `X-Frame-Options`, CSP, provider 장애로 언제든 실패할 수 있다. 따라서 FOLIO는 iframe 성공만을 전제로 하지 않고 `supported`, `external_only`, `failed` 상태와 외부 링크 fallback을 함께 설계했다.

### UI가 아닌 여러 계층에서 권한을 닫음

브라우저에서 버튼을 숨기는 것만으로는 보안 경계가 되지 않는다. 서버는 bearer token과 소유권을 확인하고, Supabase RLS/RPC는 최종 권한을 판단하며, Cloudflare WAF는 고비용 POST 경로의 외곽 rate limit을 담당한다.

### 운영 가능한 검증을 코드로 남김

수동 확인에 의존하지 않도록 `check:embeds`가 Supabase에서 대상 프로젝트를 읽고 HTTP probe, Playwright 렌더링, CSP 위반, 오류 문구, iframe 크기를 검사한다. 운영 점검은 `docs/ops/PRODUCTION_MONITORING.md`의 체크리스트와 연결된다.

## 보안 개선 사례

초기 보안 점검에서 발견된 위험을 기능 수정으로 끝내지 않고 방어 계층과 회귀 검증까지 연결했다.

| 위험 | 대응 | 검증 근거 |
|---|---|---|
| 댓글 내용의 SMTP DATA 명령 주입 | RFC 5321 dot-stuffing과 줄바꿈 정규화 (`src/lib/server/smtp.ts`) | `tests/unit/smtp.test.ts` |
| 임의 외부 URL iframe/캡처 SSRF | trusted HTTPS host allowlist, CSP 동적 origin 제한, 캡처 source 재검증 | `projectInput`·`security-headers` 단위 테스트 |
| 공개 snapshot RPC의 무제한 인자 | public wrapper에서 limit/tag/sample cap 적용 | `supabase/harden_public_security_boundaries.sql` |
| processing/failed 프로젝트 공개 | 공개 상세 wrapper가 `is_public=true AND status='published'`만 통과 | Supabase 정책/RPC 확인 |
| 프로젝트 삭제 후 Storage 고아 파일 | 서버 DELETE endpoint가 Storage prefix를 반복 삭제한 뒤 soft delete | `src/routes/api/projects/[id]/+server.ts` |
| 직접 삭제·삭제 상태 우회 | delete RLS policy 제거, update `WITH CHECK`에서 deleted 차단 | 운영 SQL Editor 조회 결과 |
| 프레임워크·전송 헤더 노출 | HSTS preload 적용, `x-sveltekit-page` 제거, CSP/Permissions-Policy 설정 | production 응답 헤더 점검 |

## 검증과 운영 증거

2026-09-21 기준 확인된 결과:

- `npm.cmd run check`: Svelte diagnostics 0 errors / 0 warnings
- `npm.cmd run test:unit`: 30 passed
- `npm.cmd run build`: Cloudflare adapter build passed
- 로컬 Playwright UI: 20 passed, 외부 fixture가 필요한 4개는 명시적 skip
- Supabase read-only smoke: `home_project_snapshot`, `project_detail_snapshot`, `powerbi_reports` 통과
- Production `/`, `/powerbi`, `/references/powerbi`, `/policy/privacy`: 모두 200
- Production HSTS, CSP, `nosniff`, `X-Frame-Options`, Referrer-Policy 확인
- Production Power BI 임베드 최근 5개: PASS 5, FAIL 0, FALLBACK 0, WARN 0

재현 명령은 [PRODUCTION_MONITORING.md](../ops/PRODUCTION_MONITORING.md), [SVELTE_DEVELOPMENT_ENVIRONMENT.md](../svelte/SVELTE_DEVELOPMENT_ENVIRONMENT.md), 루트 [README.md](../../README.md)에 정리되어 있다.

## UI/UX 캡처 자료

최근 Playwright UI 검증에서 생성된 캡처를 우선 사용한다. 아래 산출물은 2026-09-21 13:26경 생성된 결과이며, 화면 설명·레이아웃·반응형 비교 자료로 활용할 수 있다. 캡처는 `artifacts/` 아래 로컬 검증 산출물이므로 외부 포트폴리오에 공유할 때는 필요한 이미지만 별도 export한다.

### 대표 데스크톱 화면

- [홈 탐색·카드 레일](../../artifacts/playwright/test-results/routes-home-renders-a-capture-ready-page-desktop/home.png)
- [Power BI 콘텐츠 허브](../../artifacts/playwright/test-results/routes-powerbi-renders-a-capture-ready-page-desktop/powerbi.png)
- [프로젝트 등록 진입 화면](../../artifacts/playwright/test-results/routes-submit-renders-a-capture-ready-page-desktop/submit.png)
- [마이페이지·포트폴리오 관리](../../artifacts/playwright/test-results/routes-my-page-renders-a-capture-ready-page-desktop/my-page.png)
- [Power BI 레퍼런스 갤러리](../../artifacts/playwright/test-results/routes-references-powerbi-renders-a-capture-ready-page-desktop/references-powerbi.png)

### 모바일 대응 화면

- [홈 모바일](../../artifacts/playwright/test-results/routes-home-renders-a-capture-ready-page-mobile/home.png)
- [Power BI 허브 모바일](../../artifacts/playwright/test-results/routes-powerbi-renders-a-capture-ready-page-mobile/powerbi.png)
- [프로젝트 등록 모바일](../../artifacts/playwright/test-results/routes-submit-renders-a-capture-ready-page-mobile/submit.png)
- [마이페이지 모바일](../../artifacts/playwright/test-results/routes-my-page-renders-a-capture-ready-page-mobile/my-page.png)
- [Power BI 레퍼런스 모바일](../../artifacts/playwright/test-results/routes-references-powerbi-renders-a-capture-ready-page-mobile/references-powerbi.png)

각 캡처와 함께 생성된 `page-metrics.json`에는 viewport, 수평 overflow, 주요 요소 수, iframe source가 기록되어 있어 화면 이미지와 동작 검증 결과를 함께 제시할 수 있다. 전체 Playwright 보고서는 [HTML report](../../artifacts/playwright/report/index.html)에서 확인한다.

## 포트폴리오에서 깊게 보여줄 주요 기능

### 1. 임베드가 제품의 핵심 경험인 갤러리

카드 클릭에서 상세 진입, iframe 렌더링, CSP 동적 허용, 외부 링크 fallback, provider 오류 상태까지 하나의 흐름으로 설계했다. 단순히 URL을 저장하는 기능이 아니라 “작동하는 시각화 결과물을 발견하고 바로 경험한다”는 제품 가치를 구현한 부분이다.

### 2. 작성자를 위한 프로젝트 운영 도구

`/my`는 프로필·통계·프로젝트 목록을 합친 관리 공간이다. 프로젝트 공개 상태, 수정·삭제, 썸네일 모드, unread 댓글 상태를 한곳에서 처리하고, 삭제는 서버 endpoint가 Storage 정리와 DB soft delete를 순서대로 수행한다.

### 3. PBIX와 외부 콘텐츠를 함께 다루는 비동기 흐름

PBIX 업로드, Power BI Import polling, Embed URL/metadata 반영, 썸네일 캡처를 하나의 저장 흐름에 연결하되 실패 시 기존 프로젝트와 초안을 보존한다. Power BI secret과 임시 PBIX는 브라우저에 노출하거나 영구 Storage에 남기지 않는 경계를 유지한다.

### 4. 커뮤니티 기능을 제품 맥락에 연결

댓글·답글·좋아요·알림·이메일 알림을 프로젝트 상세와 마이페이지에 연결했다. 댓글이 등록되면 작성자에게 내부 알림을 만들고, SMTP 설정이 있을 때만 선택적으로 이메일을 발송해 외부 메일 장애가 핵심 작성 흐름을 막지 않도록 했다.

### 5. 운영자 없이도 반복 가능한 콘텐츠 품질 관리

`check:embeds`는 등록된 외부 대시보드를 주기적으로 점검한다. URL allowlist, HTTP 응답, iframe 차단 헤더, Playwright 실제 렌더링, 오류 문구, CSP 위반을 한 번에 확인하고 오래된 콘텐츠를 숨김·fallback 대상으로 판단할 수 있다.

## 작업 과정에서 얻은 핵심 교훈

### 화면 문제는 CSS 값보다 구조를 먼저 본다

Streamlit에서 SvelteKit으로 이전하며 wrapper, column, iframe, hydration이 실제 DOM과 정렬을 바꾸는 사례를 겪었다. 동일한 행으로 읽혀야 하는 정보는 동일한 컨테이너에 배치하고, 반복되는 보정값보다 구조적 원인을 먼저 확인하는 원칙을 세웠다.

### 정상 상태보다 실패 상태를 먼저 설계한다

외부 대시보드 만료, 권한 부족, CSP 차단, Power BI Import 실패, Storage 오류는 예외가 아니라 실제 운영 상태다. 그래서 `supported`·`external_only`·`failed`, loading·retry·fallback UI를 데이터 모델과 화면 양쪽에 반영했다.

### UI 테스트와 운영 검증은 서로 대체하지 않는다

단위 테스트는 URL 정규화·보안 헤더·SMTP 인코딩을 빠르게 닫고, Playwright는 실제 DOM·모바일 overflow·iframe 렌더링을 확인한다. Supabase smoke와 production 점검은 RLS/RPC·헤더·외부 provider까지 별도로 확인한다. `verify` 하나의 성공만으로 모든 사용자 흐름이 보장된다고 가정하지 않는다.

### 권한은 세션, 서버, DB, 인프라를 겹쳐서 닫는다

브라우저 session이 있어도 서버 endpoint가 bearer token과 소유권을 다시 확인하고, DB RLS/RPC가 최종 권한을 판단한다. Cloudflare WAF는 애플리케이션 rate limit을 보완한다. 한 계층의 실수를 다른 계층이 완화하도록 설계한 것이 핵심 보안 학습이다.

### 측정 가능한 기준을 먼저 만든다

UI는 1440×1000과 390×844 기준으로 수평 overflow·주요 요소·iframe source를 기록한다. 최적화는 체감이 아니라 route timing, LCP/CLS, 번들·CSS 예산, Power BI iframe 초기화 시간으로 판단한다. 과거 측정에서 최대 client chunk 약 252.57KB, 전역 CSS 약 95.20KB가 예산 안에 들어왔고, Power BI iframe 초기화 시간도 별도 metric으로 노출했다.

### 문서는 다음 작업자를 위한 인터페이스다

README는 실행 명령, active/historical 경계, 배포 위치를 고정하고, 운영 문서는 SQL 적용·WAF·429·임베드 점검 절차를 남긴다. 결정 이유와 검증 결과를 같은 문서에서 연결해 새 컨텍스트에서도 추측 없이 작업을 이어갈 수 있게 했다.

## 포트폴리오용 서술 문장

> 외부 대시보드 링크를 모아 보여주는 갤러리에서 출발했지만, 운영 중 발생하는 iframe 실패·권한 문제·만료 콘텐츠·보안 경계를 제품의 정상 상태로 모델링했다. SvelteKit과 Cloudflare Pages로 UI와 서버 경계를 재구성하고, Supabase RLS/RPC와 Storage 정책, Power BI 서버 연동, Playwright 기반 임베드 health check를 연결해 “보이는 화면”을 “운영 가능한 서비스”로 확장했다.

### 면접에서 설명할 수 있는 질문

- 왜 모든 외부 URL을 iframe에 넣지 않고 trusted host와 external fallback을 함께 두었는가?
- UI에서 삭제 버튼을 숨기는 것과 RLS에서 삭제 권한을 제거하는 차이는 무엇인가?
- Power BI Import와 썸네일 캡처가 실패했을 때 기존 사용자 데이터를 어떻게 보존하는가?
- 단위 테스트, Playwright, Supabase smoke, production check의 책임 범위를 어떻게 나눴는가?
- Streamlit historical 구현을 보존하면서 SvelteKit 루트 앱으로 전환한 이유와 위험은 무엇이었는가?
- 임베드 health check가 단순 HTTP 200 검사보다 실제로 어떤 운영 문제를 더 잘 잡는가?

## 포트폴리오에서 강조할 수 있는 역량

- 단순 화면 구현을 넘어 외부 provider 실패를 제품 상태와 fallback UX로 모델링한 점
- SvelteKit·Cloudflare·Supabase·Power BI를 연결하면서 server-only secret과 RLS 경계를 분리한 점
- 보안 finding을 코드·DB 정책·WAF·테스트·운영 문서로 닫은 점
- 실제 production URL에서 헤더와 임베드를 자동 점검하는 운영 도구를 직접 만든 점
- Streamlit 원본을 historical 경계로 보존하면서 SvelteKit 루트 앱으로 점진적으로 이전한 점

## 정직하게 함께 기록할 한계

- Codex Security 심층 스캔의 최종 리포트는 현재 저장소 핸드오프에 포함되어 있지 않다.
- 전체 임베드 348개 검증 결과는 자동 점검 커밋의 기록이며, 일상 운영에서는 `--limit` 표적 점검과 전체 점검을 구분한다.
- 운영 검증은 공개 경로·익명 계약·최근 임베드 중심이며, 실제 사용자 계정 mutation과 Power BI Workspace 변경 테스트는 fixture와 복구 계획이 필요하다.

## 포트폴리오 구성 제안

1. 문제: 데이터 시각화 결과물의 맥락과 상호작용을 함께 전달하기 어려웠다.
2. 해결: 프로젝트 등록·탐색·상세 임베드·커뮤니티를 하나의 SvelteKit 흐름으로 설계했다.
3. 기술적 난제: 외부 iframe 실패, PBIX 비밀키, RLS/RPC, Storage 삭제, SMTP 입력을 보안 경계로 분해했다.
4. 결과: 운영 가능한 Cloudflare/Supabase 서비스와 자동 임베드 health check를 만들었다.
5. 증거: 위 검증 수치, production 헤더, 임베드 PASS 리포트, 관련 커밋과 문서를 연결한다.
