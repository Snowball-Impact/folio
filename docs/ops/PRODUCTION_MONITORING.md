# 프로덕션 모니터링 및 롤백 체크리스트

목표: Cloudflare Pages에 배포된 루트 SvelteKit 앱의 가용성, 에러, 성능을 확인하고 문제 발생 시 빠르게 이전 정상 배포로 되돌린다.

## 모니터링 표면

| 영역 | 1차 도구 | 확인 항목 |
|---|---|---|
| 배포 상태 | Cloudflare Pages Deployments | 최신 production deployment, commit SHA, build log |
| 런타임 오류 | Cloudflare Pages Functions logs | request id, status, route, exception |
| 트래픽/성능 | Cloudflare Analytics, Web Analytics, 선택형 RUM endpoint | 방문수, 4xx/5xx, LCP/CLS/INP, Power BI iframe init |
| 외부 의존성 | Supabase Dashboard, Power BI/Fabric Admin, SMTP provider | Auth, RPC, Storage, embed token, email delivery |
| 회귀 | `npm.cmd run verify`, `npm.cmd run test:ui` | build, smoke, security, public route UI |

## 배포 직후 확인

- [ ] Cloudflare Pages production deployment가 성공 상태인지 확인한다.
- [ ] 배포 commit SHA가 기대한 GitHub merge commit과 같은지 확인한다.
- [ ] `/`, `/powerbi`, `/references/powerbi`, 공개 `/projects/:id`가 200으로 열린다.
- [ ] 로그인, 로그아웃, `/my`, `/submit` 접근 흐름이 동작한다.
- [ ] Supabase Auth/RPC/Storage 요청에 비정상 401, 403, 500이 급증하지 않는다.
- [ ] 브라우저 Network/Source에 `SUPABASE_SERVICE_ROLE_KEY`, `POWERBI_CLIENT_SECRET`, `SMTP_PASSWORD` 값이 보이지 않는다.

## 알림 기준

- 5분 동안 5xx가 5건 이상이면 장애 후보로 본다.
- 홈 또는 공개 상세가 2회 연속 실패하면 rollback 여부를 판단한다.
- 로그인/프로젝트 등록/Power BI embed 중 하나가 production에서 재현 가능하게 실패하면 no-go로 본다.
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
- Power BI embed 문제는 embed token endpoint 응답, iframe 생성 여부, provider status를 분리해서 본다.
- 사용자 데이터 변경이 관련되면 DB 수정 전에 affected row, user id, project id를 먼저 기록한다.

## 후속 정리

- rollback이 끝나면 원인, 영향 범위, 되돌린 deployment/commit, 재배포 여부를 `docs/common/PROJECT_CONTEXT.md` 또는 별도 incident note에 남긴다.
- 임시 env/secrets 변경을 했다면 Cloudflare와 로컬 `.env` 차이를 확인한다.
- 같은 장애가 재발할 수 있으면 `npm.cmd run verify` 또는 Playwright smoke에 회귀 케이스를 추가한다.
