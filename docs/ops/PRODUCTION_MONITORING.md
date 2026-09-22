# 프로덕션 모니터링 및 롤백 체크리스트

목표: Cloudflare Pages에 배포된 루트 SvelteKit 앱의 가용성, 에러, 성능을 확인하고 문제 발생 시 빠르게 이전 정상 배포로 되돌린다.

## 최근 운영 검증 기록 (2026-09-21)

- 공개 production 경로 `/`, `/powerbi`, `/references/powerbi`, `/policy/privacy`: 모두 HTTP 200.
- 응답 보안 헤더: HSTS `max-age=31536000; includeSubDomains; preload`, CSP 존재, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin` 확인.
- `npm.cmd run check:embeds -- --base-url https://folio.it.kr --platform powerbi --limit 5 --concurrency 2`: 최근 Power BI 5개 PASS, FAIL 0, FALLBACK 0, WARN 0.
- 운영 Supabase 읽기 전용 smoke: `home_project_snapshot`, `project_detail_snapshot`, `powerbi_reports` 계약 통과.

## 모니터링 표면

| 영역 | 1차 도구 | 확인 항목 |
|---|---|---|
| 배포 상태 | Cloudflare Pages Deployments | 최신 production deployment, commit SHA, build log |
| 런타임 오류 | Cloudflare Pages Functions logs | request id, status, route, exception |
| 트래픽/성능 | Cloudflare Analytics, Web Analytics, 선택형 RUM endpoint | 방문수, 4xx/5xx, LCP/CLS/INP, Power BI iframe init |
| 외부 의존성 | Supabase Dashboard, Power BI/Fabric Admin, SMTP provider | Auth, RPC, Storage, embed token, email delivery |
| 인프라 보안 | Cloudflare WAF Dashboard | Sensitive API rate limit 규칙 상태 및 block 이력 |
| 회귀 | `npm.cmd run verify`, `npm.cmd run test:ui` | build, smoke, security, public route UI |

## 배포 직후 확인

- [ ] Cloudflare Pages production deployment가 성공 상태인지 확인한다.
- [ ] 배포 commit SHA가 기대한 GitHub merge commit과 같은지 확인한다.
- [ ] `/`, `/powerbi`, `/references/powerbi`, 공개 `/projects/:id`가 200으로 열린다.
- [ ] Power BI/Fabric fixture와 외부 HTTPS iframe fixture 상세에서 대표 결과물이 렌더링되고, Console에 CSP `frame-src` 또는 `Refused to frame` 오류가 없다. 외부 iframe은 현재 프로젝트 URL의 origin이 상세 HTML CSP에 포함되어야 한다.
- [ ] 상세 HTML 응답의 `Content-Security-Policy`에 `https://app.fabric.microsoft.com`이 포함된다.
- [ ] 등록된 Power BI 및 시각화 대시보드 임베드 무결성 점검 스크립트를 실행해 정상 로딩을 확인한다 (`npm.cmd run check:embeds -- --base-url https://folio.it.kr --platform powerbi`).
- [ ] 로그인, 로그아웃, `/my`, `/submit` 접근 흐름이 동작한다.
- [ ] Supabase Auth/RPC/Storage 요청에 비정상 401, 403, 500이 급증하지 않는다.
- [ ] 브라우저 Network/Source에 `SUPABASE_SERVICE_ROLE_KEY`, `POWERBI_CLIENT_SECRET`, `SMTP_PASSWORD` 값이 보이지 않는다.
- [ ] `supabase/add_server_rate_limits_and_secure_views.sql`을 적용한 뒤, 애플리케이션 rate limit이 민감 API 연속 호출에 `429`와 `Retry-After`를 반환하는지 확인한다. 이전 버전의 SQL을 이미 적용했다면 먼저 `supabase/fix_server_rate_limit_request_time.sql`도 적용한다.
- [ ] Cloudflare WAF에서 `Sensitive API rate limit` 규칙이 Active 상태로 정상 동작 중인지 확인한다. 이는 애플리케이션 제한을 보완하는 외곽 방어 계층이다.

## 알림 기준

- 5분 동안 5xx가 5건 이상이면 장애 후보로 본다.
- 홈 또는 공개 상세가 2회 연속 실패하면 rollback 여부를 판단한다.
- 로그인/프로젝트 등록/Power BI embed 중 하나가 production에서 재현 가능하게 실패하면 no-go로 본다.
- Power BI/Fabric iframe이 비어 있거나 CSP에 의해 차단되면 즉시 no-go로 보고 마지막 정상 Pages deployment로 rollback을 검토한다.
- Supabase 또는 Power BI provider 장애가 원인이면 앱 rollback보다 provider status와 fallback UI를 먼저 확인한다.

## 롤백

Cloudflare Pages UI에서 먼저 롤백한다.

1. Cloudflare Dashboard에서 프로젝트를 연다.
2. **Workers & Pages → 해당 Pages 프로젝트 → Deployments**로 이동한다.
3. 마지막 정상 deployment를 찾는다.
4. **Rollback to this deployment** 또는 동일 의미의 rollback action을 실행한다.
5. production URL에서 핵심 route를 다시 확인한다.
6. GitHub에는 별도 fix PR 또는 revert PR을 만들어 코드 기준도 정리한다.

Git 기준까지 되돌려야 하면 main에서 revert PR을 만든다.

```powershell
git switch main
git pull origin main
git revert <bad-merge-or-commit-sha> --no-edit
git push origin HEAD
```

## 원인 조사

- Cloudflare deployment log와 Functions log에서 같은 시각의 request id를 모은다.
- Supabase Dashboard에서 Auth, Database, Storage error를 같은 시간대로 확인한다.
- Power BI embed 문제는 embed token endpoint 응답, iframe 생성 여부, iframe 최종 URL, HTML response CSP, provider status를 분리해서 본다. 외부 iframe 프로젝트 상세는 전체 문서 응답의 CSP를 사용해야 한다.
- 사용자 데이터 변경이 관련되면 DB 수정 전에 affected row, user id, project id를 먼저 기록한다.

## 후속 정리

- rollback이 끝나면 원인, 영향 범위, 되돌린 deployment/commit, 재배포 여부를 `docs/common/PROJECT_CONTEXT.md` 또는 별도 incident note에 남긴다.
- 임시 env/secrets 변경을 했다면 Cloudflare와 로컬 `.env` 차이를 확인한다.
- 같은 장애가 재발할 수 있으면 `npm.cmd run verify` 또는 Playwright smoke에 회귀 케이스를 추가한다.

## 인프라 보안 및 WAF 설정 가이드

### 1. Cloudflare WAF Rate Limiting 룰 개요
Cloudflare WAF Rate Limiting은 운영 중 제한값을 조정하는 주 제어면이며, 애플리케이션의 서버 측 rate limit은 WAF 설정 누락·우회에 대비한 보조 안전망이다. WAF와 별개로 `supabase/add_server_rate_limits_and_secure_views.sql`을 배포 전에 적용해야 하며, 이 SQL은 서버에서 호출되는 원자적 제한 함수와 조회수 기록 함수를 생성한다. 이미 이전 버전을 적용한 환경은 배포 전에 `supabase/fix_server_rate_limit_request_time.sql`을 한 번 실행한다. 이 hotfix는 함수 정의만 교체하므로 반복 실행해도 안전하다.

- **규칙명:** `Sensitive API rate limit`
- **현재 match 식:** `http.request.method eq "POST" and (path contains "/thumbnail-capture" or path contains "/powerbi-publish" or path contains "/email-notification")`
- **대상 엔드포인트:** 썸네일 자동 캡처, Power BI 게시/연결, 이메일 알림 발송
- **동일 특성:** IP
- **현재 임계값:** 위 세 경로의 요청을 합산하여 IP당 **10초 동안 5회**
- **조치 (Action):** Block (HTTP 상태 코드 429 Too Many Requests 발생)
- **프론트엔드 대응:** API 호출에서 HTTP 429 응답을 수신하는 경우, "요청이 너무 많습니다. 잠시 후 다시 시도해주세요." 라는 사용자 친화적인 메시지를 출력합니다.

애플리케이션 제한은 다음의 고비용 경로에도 적용된다: Power BI embed 토큰 발급, Power BI 게시, 썸네일 캡처·업로드, 본문 이미지 업로드, 댓글 이메일 발송, 공개 프로젝트 조회수 기록. 사용자와 IP 버킷을 함께 사용하며, 제한 저장소를 확인할 수 없을 때는 요청을 거부한다.

일상적인 운영 조정은 Cloudflare Dashboard의 **Edit rate limiting rule**에서 한다. 앱의 `RATE_LIMIT_<ACTION>_MAX_REQUESTS` 및 `RATE_LIMIT_<ACTION>_WINDOW_SECONDS` 환경 변수는 기본값을 덮어쓰는 예외적 조정 수단이므로, 평소에는 등록할 필요가 없다. 값이 누락되거나 유효하지 않으면 안전한 기본값으로 동작한다.

현재 WAF 규칙은 `body-image`, 일반 `thumbnail` 업로드, `GET /powerbi-embed`을 포함하지 않는다. 이 경로들을 WAF로도 보호하려면 기존 규칙을 넓히기보다 별도 규칙을 만들고, 앱 서버 기본 제한과 Cloudflare 임계값을 함께 검토한다. 특히 공개 Power BI embed 토큰 발급에는 GET 전용 규칙을 사용한다.

### 2. WAF 작동 및 429 수동 검증 방법
배포 직후 또는 주기적 점검 시 아래 방법으로 동작을 검증할 수 있습니다.

1. 개발자 도구(F12)의 Network 탭을 엽니다.
2. 10초 안에 썸네일 직접 캡처 버튼을 6회 이상 누르거나, 스크립트 등을 이용해 `/api/projects/[id]/thumbnail-capture` 또는 `/api/projects/[id]/powerbi-publish`에 연속 POST 요청을 보냅니다.
3. WAF 임계값을 넘긴 요청이 HTTP `429`를 반환하는지 확인합니다. 앱 서버 제한으로 응답한 경우에는 `Retry-After` 헤더도 반환됩니다.

## 대시보드 임베드 무결성 점검 가이드 (`check:embeds`)

등록된 Power BI, Fabric, Tableau, Streamlit, GitHub Pages 대시보드의 임베드 아이프레임이 정상 로딩되는지 Playwright 헤드리스 브라우저를 통해 실시간 교차 검증한다.

### 1. 점검 파이프라인 구조
1. **도메인 화이트리스트 검증**: 신뢰할 수 있는 도메인(Power BI, Fabric, Tableau, Looker Studio, Streamlit, GitHub Pages) 여부 확인
2. **HTTP 소스 프로브**: 원본 URL의 200 OK 수신 및 `X-Frame-Options` 차단 헤더 존재 여부 감지
3. **실제 브라우저 렌더링 (Playwright)**:
   - 각 프로젝트 상세 페이지(`/projects/:id`)에 접속하여 `iframe.dashboard-frame` 생성 및 크기(너비×높이 > 0) 확인
   - 브라우저 콘솔에서 CSP `frame-src` 위반 이벤트 실시간 리스닝
   - 외부 링크 폴백(`embed-external-state`) 또는 에러(`embed-failed-state`) 상태 자동 판별

### 2. 실행 명령어
```powershell
# 로컬 개발 서버 기준 전체 대시보드 점검
npm.cmd run check:embeds

# 프로덕션 운영 서버 기준 Power BI 대시보드 점검
npm.cmd run check:embeds -- --base-url https://folio.it.kr --platform powerbi

# 최근 N개 프로젝트만 신속 점검
npm.cmd run check:embeds -- --limit 10

# 스크린샷 캡처 및 JSON 결과 보고서 저장
npm.cmd run check:embeds -- --screenshot --json artifacts/reports/embed-report.json
```

4. Cloudflare WAF Analytics 대시보드에서 `Sensitive API rate limit` 규칙에 의한 차단 로그(Block Event)가 카운트되는지 대조합니다.
