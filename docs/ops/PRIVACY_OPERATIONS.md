# 개인정보·정책 운영 체크리스트

이 문서는 FOLIO SvelteKit/Cloudflare 앱의 실제 구현과 정책 고지 사이의 정합성을 점검하기 위한 운영 메모다. 법률 검토를 대체하지 않으며, 공개 출시 전 최종 문구는 서비스 운영자가 확인한다.

## 현재 처리 표면

| 영역 | 현재 구현 | 정책 고지에 반영할 내용 |
|---|---|---|
| 인증 | Supabase Auth, browser session storage | 이메일, 이름, 소속, 로그인 세션 |
| 프로젝트 | Supabase DB, Supabase Storage, Power BI 연동 | 프로젝트 등록 정보, 공개 링크, 썸네일, 본문 이미지, PBIX 게시 결과 |
| 댓글·신고 | comments, notifications, content_reports | 댓글, 알림, 신고 사유와 메모 |
| 약관 동의 | `/api/policy-consents`, `user_policy_consents` | 정책 버전, 동의 시각, IP, User-Agent |
| 계정 삭제 요청 | `/api/account-deletion-requests`, `account_deletion_requests` | 요청 시각, 계정 이메일, 처리 상태, 선택 메모 |
| 조회수 | `localStorage` 익명 visitor id, DB에는 hash 저장 | 조회수 중복 집계용 익명 식별자 |
| Google Analytics | 선택형 `PUBLIC_GA_MEASUREMENT_ID` | 페이지 경로, 브라우저·기기·유입 정보 등 GA4 기본 측정 항목 |
| 관측성 | 선택형 `PUBLIC_RUM_ENDPOINT` | 경로, Web Vitals, Power BI load metric 같은 비식별 성능 이벤트 |
| 외부 서비스 | Cloudflare, Supabase, Microsoft Power BI/Fabric, Google Analytics, SMTP provider | 배포, 인증·DB·스토리지, 보고서 게시·임베드, 방문 분석, 이메일 알림 |

## 정책 버전 운영

- `policy_versions`는 `terms`, `privacy` 각각 활성 버전 1개를 유지한다.
- 정책 본문을 실질적으로 바꾸면 기존 row를 덮어쓰지 않고 새 `version`을 만든다.
- 새 버전을 활성화하면 신규 가입자는 새 버전에 동의한다.
- 기존 사용자가 활성 `terms`, `privacy` 중 동의하지 않은 버전이 있으면 로그인 후 `/policy/consent`에서 재동의를 받는다.
- 현재 적용 후보 SQL은 `supabase/update_policy_versions_2026_09_09.sql`이다.

## 운영 DB 적용 순서

1. 처리방침 문구를 운영자가 최종 확인한다.
2. 기존 사용자 재동의가 필요한 변경인지 판단한다.
3. 필요 시 공지 계획을 준비하고, `/policy/consent` 재동의 화면 문구가 변경 내용과 맞는지 확인한다.
4. Supabase SQL Editor에서 `supabase/update_policy_versions_2026_09_09.sql`을 실행한다.
5. `policy_versions`에서 `terms`, `privacy`의 활성 버전이 각각 하나인지 확인한다.
6. 신규 가입 테스트 후 `user_policy_consents`에 새 버전 동의 row가 생성되는지 확인한다.
7. 기존 테스트 계정으로 로그인해 `/policy/consent` 재동의 후 목적지로 돌아가는지 확인한다.

## 계정 삭제 요청 운영

- 현재 마이 페이지 UI와 API 접수는 기본 feature flag off 상태다. Admin 사용자 관리 화면과 함께 UX를 재설계한 뒤 활성화한다.
- 기능을 활성화하면 사용자는 마이 페이지에서 계정 삭제 요청을 접수할 수 있다.
- 앱은 즉시 계정과 콘텐츠를 삭제하지 않고 `account_deletion_requests`에 `open` 상태로 기록한다.
- 같은 사용자는 `open`, `reviewing` 상태 요청을 중복 접수할 수 없다.
- 운영자는 요청자 본인 확인, 프로젝트 공개 상태, Supabase Storage 파일, Power BI 게시 리소스, 댓글·알림 영향을 확인한 뒤 처리한다.
- 처리 완료 후 `status='resolved'`, `resolved_at`, `operator_note`를 남긴다. 요청 철회나 오접수는 `cancelled`로 닫는다.
- 운영 DB에 이 기능을 적용하려면 `supabase/create_account_deletion_requests.sql`을 실행한다.
- 후속 TODO: Admin 사용자 관리 화면에 계정 삭제 요청 목록, 상태 필터, 처리 상태 변경 UI를 추가한다. Admin UI가 생기기 전에는 Supabase Table Editor 또는 SQL Editor에서 확인한다.

## 출시 전 빠뜨리기 쉬운 확인

- 개인정보 처리방침의 수집 항목이 실제 코드의 저장 항목과 맞는지 확인한다.
- footer 문의 이메일, 약관 문의 이메일, 개인정보 문의 이메일을 하나로 맞춘다.
- `PUBLIC_RUM_ENDPOINT`를 켠 경우 endpoint 운영자, 보관 기간, payload 예시를 별도로 기록한다.
- `PUBLIC_GA_MEASUREMENT_ID`를 켠 경우 GA4 Web stream URL, 데이터 보관 기간, 내부 트래픽 제외 설정, 개인정보 처리방침 문구를 확인한다.
- SMTP 제공자를 바꾸면 처리방침의 외부 서비스 항목도 같이 확인한다.
- 계정 삭제 요청을 실제 삭제까지 자동화하기 전에는 Auth user, profile, project, storage, Power BI 리소스 처리 범위를 운영자가 최종 확인한다.
