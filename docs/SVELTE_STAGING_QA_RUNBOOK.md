# Svelte Staging QA Runbook

이 문서는 SvelteKit 앱을 staging 또는 production-like 환경에 올린 뒤 사람이 직접 눌러 확인할 순서를 정리한다. 전체 go/no-go 기준은 `SVELTE_E2E_READINESS.md`를 따르고, 이 문서는 실행 순서와 기록 형식을 담당한다.

## 0. QA 원칙

- 자동 검증과 수동 QA를 섞어 말하지 않는다.
- 테스트 계정, 테스트 프로젝트, 테스트 PBIX는 운영 데이터와 구분한다.
- secret 값은 캡처, 문서, 로그에 남기지 않는다.
- 실패는 즉시 고치기보다 reproduction, expected, actual, severity를 먼저 기록한다.
- no-go 항목은 우회하지 않는다. 특히 auth, visibility, secret leak, PBIX 원본 보관은 배포 차단 사유다.

## 1. 사전 준비

### 자동 gate

`C:\workspace\folio\svelte_app`에서 실행한다.

```powershell
npm.cmd install
npm.cmd run verify
```

통과 기준:

- Svelte/TypeScript check 0 errors
- adapter-node build 성공
- public route smoke 성공
- Supabase contract smoke 성공
- security smoke 성공

### staging env

배포 환경에 아래 값이 설정되어 있어야 한다. 값 자체는 문서에 쓰지 않는다.

Required:

- `PUBLIC_SUPABASE_URL`
- `PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `APP_URL`
- `THUMBNAIL_STORAGE_BUCKET`

Power BI, PBIX를 이번 QA 범위에 포함할 때:

- `POWERBI_TENANT_ID`
- `POWERBI_CLIENT_ID`
- `POWERBI_CLIENT_SECRET`
- `POWERBI_WORKSPACE_ID`
- `POWERBI_API_BASE_URL`
- `PBIX_MAX_UPLOAD_MB`
- `POWERBI_IMPORT_POLL_SECONDS`
- `POWERBI_CAPTURE_READY_WAIT_SECONDS`

SMTP를 이번 QA 범위에 포함할 때:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_FROM_NAME`
- `SMTP_USE_TLS`

Thumbnail capture를 이번 QA 범위에 포함할 때:

- Playwright 또는 system Chromium 사용 가능
- 필요한 경우 `CHROME_BINARY_PATH`
- host memory, sandbox, request timeout 확인

## 2. 테스트 데이터

아래 값을 QA 시작 전에 적어둔다.

| 항목 | 값 |
|---|---|
| Staging URL |  |
| Supabase project |  |
| 테스트 작성자 계정 |  |
| 테스트 댓글 작성자 계정 |  |
| 공개 테스트 프로젝트 ID |  |
| 비공개 테스트 프로젝트 ID |  |
| PBIX 테스트 파일명 |  |
| QA 시작 시각 |  |
| QA 담당자 |  |

## 3. Public Smoke

1. `/`를 anonymous browser에서 연다.
2. 홈 카드 레일이 보이고 Power BI 중심 콘텐츠가 먼저 보이는지 확인한다.
3. `/references/powerbi`를 연다.
4. 최신순, 조회수순, 좋아요순 정렬을 눌러 카드 목록이 바뀌는지 확인한다.
5. `/powerbi`를 연다.
6. 업데이트, 학습, 커뮤니티, 자격증 탭 또는 섹션이 로드되는지 확인한다.
7. 공개 프로젝트 상세 `/projects/:id`를 연다.
8. 상세 히어로, 본문, 작성자, 링크, 댓글 영역이 깨지지 않는지 확인한다.
9. private 또는 deleted 프로젝트가 anonymous에서 보이지 않는지 확인한다.

기록:

| Check | Pass/Fail | Notes |
|---|---|---|
| Home anonymous load |  |  |
| Power BI references |  |  |
| Power BI content hub |  |  |
| Public project detail |  |  |
| Private/deleted hidden |  |  |

## 4. Auth And Onboarding

1. `/signup`에서 새 테스트 계정을 만든다.
2. Supabase Auth에 사용자가 생성됐는지 확인한다.
3. `profiles` row가 생성되거나 첫 로그인 후 생성되는지 확인한다.
4. `/login`으로 로그인한다.
5. 필요한 경우 policy onboarding이 뜨는지 확인한다.
6. 필수 약관에 동의한 뒤 원래 가려던 보호 route로 돌아가는지 확인한다.
7. `/reset-password` recovery link 흐름은 Supabase redirect URL이 staging URL로 잡힌 뒤 별도 확인한다.

기록:

| Check | Pass/Fail | Notes |
|---|---|---|
| Signup creates auth user |  |  |
| Profile created/updated |  |  |
| Login restores session |  |  |
| Onboarding blocks and releases |  |  |
| Password recovery callback |  |  |

## 5. Project Mutation

작성자 계정으로 진행한다.

1. `/submit`에서 공개 프로젝트를 만든다.
2. 홈과 상세에서 공개 프로젝트가 보이는지 확인한다.
3. `/submit`에서 비공개 프로젝트를 만든다.
4. anonymous browser에서 비공개 프로젝트가 보이지 않는지 확인한다.
5. `/my`에서 내 프로젝트만 보이는지 확인한다.
6. `/projects/:id/edit`에서 제목, 본문, 태그, 링크, visibility를 수정한다.
7. 변경값이 상세와 홈 카드에 반영되는지 확인한다.
8. `/my`에서 soft delete를 실행한다.
9. 삭제된 프로젝트가 공개 목록과 내 목록에서 기대대로 숨겨지는지 확인한다.

기록:

| Check | Pass/Fail | Notes |
|---|---|---|
| Public project submit |  |  |
| Private project hidden |  |  |
| My page ownership |  |  |
| Edit persists fields |  |  |
| Soft delete hides project |  |  |

## 6. Thumbnails

1. manual URL 모드로 이미지 URL을 저장한다.
2. 상세와 카드에 이미지가 표시되는지 확인한다.
3. upload 모드로 JPG, PNG, WebP 중 하나를 업로드한다.
4. Supabase Storage `project-thumbnails` bucket에 파일이 생성되는지 확인한다.
5. `projects.thumbnail_mode='upload'`와 `thumbnail_url`이 갱신되는지 확인한다.
6. capture 모드를 선택하고 Power BI embed 또는 report URL을 대상으로 캡처한다.
7. 성공 시 `thumbnail_mode='capture'`와 Storage 파일 생성 여부를 확인한다.
8. Chromium이 없거나 캡처가 실패하면 프로젝트 생성/수정 자체가 막히지 않고 안전한 오류가 표시되는지 확인한다.

기록:

| Check | Pass/Fail | Notes |
|---|---|---|
| Manual thumbnail URL |  |  |
| Upload thumbnail storage |  |  |
| Upload DB update |  |  |
| Capture thumbnail storage |  |  |
| Capture failure safe |  |  |

## 7. Power BI And PBIX

Power BI tenant와 workspace가 staging용으로 준비됐을 때만 진행한다.

1. 기존 public iframe URL 프로젝트가 fallback viewer로 렌더되는지 확인한다.
2. `.pbix`가 아닌 파일 업로드가 거절되는지 확인한다.
3. `PBIX_MAX_UPLOAD_MB`를 넘는 파일이 거절되는지 확인한다.
4. 정상 PBIX를 업로드한다.
5. import polling 후 `powerbi_reports`가 upsert되는지 확인한다.
6. 프로젝트 `status`가 `published`가 되는지 확인한다.
7. `/api/projects/:id/powerbi-embed`가 정상 응답하는지 확인한다.
8. embed token이 DB에 저장되지 않는지 확인한다.
9. 실패 케이스에서 프로젝트가 `failed`로 표시되고 secret이나 provider 원문이 사용자에게 노출되지 않는지 확인한다.
10. PBIX와 capture를 함께 켰을 때 `POWERBI_CAPTURE_READY_WAIT_SECONDS` 이후 report page 캡처가 실행되는지 확인한다.

기록:

| Check | Pass/Fail | Notes |
|---|---|---|
| Iframe fallback render |  |  |
| Reject non-PBIX |  |  |
| Enforce max upload MB |  |  |
| PBIX import success |  |  |
| powerbi_reports upsert |  |  |
| Embed endpoint returns token |  |  |
| No token/secret persisted |  |  |
| Failure safe message |  |  |
| PBIX plus capture |  |  |

## 8. Community And Notifications

작성자 계정과 댓글 작성자 계정 두 개로 진행한다.

1. anonymous 상태에서 좋아요와 댓글 입력이 로그인 prompt로 이어지는지 확인한다.
2. 로그인 상태에서 좋아요를 누르고 다시 취소한다.
3. 댓글 작성자 계정으로 root comment를 작성한다.
4. 같은 계정으로 reply를 작성한다.
5. 본인 댓글 삭제가 가능한지 확인한다.
6. 작성자 계정으로 로그인해 `/notifications`에 댓글 알림이 생겼는지 확인한다.
7. 알림을 눌러 상세로 이동했을 때 해당 프로젝트 댓글 알림이 read 처리되는지 확인한다.
8. SMTP가 설정되어 있으면 작성자에게 이메일이 발송되는지 확인한다.
9. SMTP 설정이 없거나 실패해도 댓글 작성은 성공하는지 확인한다.

기록:

| Check | Pass/Fail | Notes |
|---|---|---|
| Anonymous prompt |  |  |
| Like/unlike |  |  |
| Root comment |  |  |
| Reply |  |  |
| Own comment delete |  |  |
| In-app notification |  |  |
| Notification read state |  |  |
| SMTP email |  |  |
| SMTP failure does not block comment |  |  |

## 9. Security Spot Checks

자동 `smoke:security`가 통과한 뒤, staging에서 아래를 눈으로 확인한다.

1. browser devtools source와 network response에 `SUPABASE_SERVICE_ROLE_KEY`, `POWERBI_CLIENT_SECRET`, `SMTP_PASSWORD` 값이 보이지 않는다.
2. anonymous 상태에서 thumbnail, thumbnail capture, PBIX publish endpoint가 성공하지 않는다.
3. 다른 사용자 프로젝트를 수정하거나 삭제할 수 없다.
4. 다른 사용자의 comment email notification을 요청할 수 없다.
5. Power BI embed token은 server endpoint 응답으로만 오고 DB에 저장되지 않는다.

기록:

| Check | Pass/Fail | Notes |
|---|---|---|
| No private secrets in browser |  |  |
| Anonymous protected endpoints blocked |  |  |
| Cross-user project mutation blocked |  |  |
| Cross-user email notification blocked |  |  |
| Embed token not persisted |  |  |

## 10. Go/No-Go Summary

| Area | Status | Blocker? | Notes |
|---|---|---|---|
| Build/verify |  |  |  |
| Environment |  |  |  |
| Supabase contract |  |  |  |
| Public flow |  |  |  |
| Auth/account |  |  |  |
| Project mutation |  |  |  |
| Thumbnail |  |  |  |
| Power BI/PBIX |  |  |  |
| Community |  |  |  |
| Security |  |  |  |

Decision:

- [ ] Go
- [ ] Go with documented limitations
- [ ] No-go

No-go reasons:

- Auth/session recovery is unreliable.
- Public/private/deleted visibility rules fail.
- PBIX publish leaks secrets or stores raw PBIX files.
- Server endpoints fail without useful user-facing errors.
- Thumbnail capture blocks project creation instead of failing safely.