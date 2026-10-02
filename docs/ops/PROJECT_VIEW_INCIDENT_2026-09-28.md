# 프로젝트 조회수 집계 장애 및 GA4 복구 기록 (2026-09-28)

## 요약

- 영향 기간: 2026-09-21 15:22 KST 이후부터 2026-09-28 수정 전까지
- 증상: GA4 주간 활성 사용자는 약 1,900명이었지만 `project_views`와 `projects.view_count`가 증가하지 않았다.
- 원인: `projects_power_bi_url_allowed_check`의 PostgreSQL 정규식에 JavaScript식 `\\.`가 들어갔다. 유효한 임베드 URL을 가진 기존 프로젝트도 `view_count` UPDATE 시 제약 위반이 발생했고, 같은 트랜잭션의 `project_views` INSERT도 롤백됐다.
- 운영 수정: 허용 호스트를 `[.]`로 표현하고, 선택적 숫자 포트와 표준 URL 경계 `(:[0-9]+)?([/?#]|$)`를 사용하도록 제약을 교체하고 검증했다.
- 데이터 복구: GA4의 `Date × Page path and screen class × Active users`를 기준으로 2026-09-22~27의 1,841건을 복구했다.

## 원인과 실패 경로

프로젝트 상세 진입은 다음 경로로 조회수를 기록한다.

`+page.svelte` → `recordProjectView` → `POST /api/projects/:id/view` → `record_server_project_view` → `project_views` INSERT → `projects.view_count` UPDATE

`projects_power_bi_url_allowed_check`는 `NOT VALID`로 추가되어 기존 행은 남아 있었지만, 해당 행을 UPDATE할 때는 즉시 평가된다. 잘못된 정규식이 유효한 URL까지 거부하면서 마지막 UPDATE가 실패했고, 함수 호출 전체가 롤백됐다. 따라서 API는 502를 반환했고 원장에도 복구 가능한 열람자 해시가 남지 않았다.

## 수정 및 검증

- `supabase/schema.sql`과 `supabase/harden_public_security_boundaries.sql`의 URL 제약을 수정했다.
- `supabase/fix_trusted_embed_url_constraint.sql`에 운영 교정 마이그레이션을 추가했다.
- `tests/unit/sql-constraints.test.ts`에서 세 SQL 파일의 정규식 일치 여부와 허용·차단 URL 계약을 애플리케이션 레벨에서 회귀 테스트한다. 실제 PostgreSQL 적용 결과는 아래 운영 검증으로 별도 확인했다.
- 허용: Power BI, Fabric, Tableau Public, Looker Studio, Streamlit, GitHub Pages의 HTTPS URL과 선택적 숫자 포트.
- 거부: HTTP, 유사 접미사 호스트, `@evil.example` 사용자정보 우회, 비숫자 포트.
- 수정 전 실제 프로젝트 조회 API는 HTTP 502였다.
- 수정 후 첫 호출은 HTTP 200, `{"counted":true}`였고 원장과 `view_count`가 42→43으로 함께 증가했다.
- 같은 날 동일 열람자의 재호출은 HTTP 200, `{"counted":false}`였다.
- 제약 케이스와 `pg_constraint.convalidated = true`를 확인했다.
- unit test 33개, `svelte-check`, production build가 모두 통과했다.

## GA4 복구 근거

- 차원: `Date`, `Page path and screen class`
- 측정항목: `Active users`
- 기간: 2026-09-22~2026-09-27, 날짜별 개별 조회
- 포함: 경로가 `/projects/<uuid>`인 행
- 제외: 홈, 로그인, 제출 페이지
- 9월 21일: 15:22 KST까지 원장이 정상 동작해 일 단위 GA4 값은 중복 위험이 있으므로 제외
- 9월 28일: 수정 당일의 부분 기간이고 정상 원장이 다시 동작하므로 제외

| 날짜 | 복구 건수 |
|---|---:|
| 2026-09-22 | 88 |
| 2026-09-23 | 302 |
| 2026-09-24 | 442 |
| 2026-09-25 | 299 |
| 2026-09-26 | 393 |
| 2026-09-27 | 317 |
| 합계 | 1,841 |

복구 SQL은 `supabase/backfill_project_views_from_ga4_20260922_20260927.sql`이다. `ga4-backfill-20260928:<date>:<project_id>:<sequence>`를 SHA-256으로 변환한 합성 `viewer_hash`와 `ON CONFLICT DO NOTHING`을 사용한다. 날짜는 세션 `DateStyle`과 무관하도록 `to_char(viewed_on, 'YYYY-MM-DD')`로 고정한다. 삽입 뒤 영향을 받은 프로젝트의 `view_count`를 원장 `count(*)`와 동기화하며, 1,841개 합성 행과 카운터 일치를 검증하지 못하면 트랜잭션을 중단한다.

운영 실행 결과(2026-09-28): `restored_ga4_views = 1841`, `counter_mismatches = 0`. 즉, 계획한 합성 원장 행이 모두 존재하고 영향을 받은 모든 프로젝트의 누적 카운터가 원장 합계와 일치한다.

## 복구 한계

원래 내부 요청이 전체 롤백되어 실제 열람자 해시는 복원할 수 없다. GA4 활성 사용자와 내부 IP/사용자 기반 일간 유니크는 식별 방식이 다르므로 1,841건은 가장 가까운 집계 기반 재구성이지 원본 이벤트의 정확한 복원은 아니다. 개인정보나 GA 사용자 ID는 저장하지 않았고 집계 수치만 합성 해시로 변환했다.

당시 확인 화면의 속성명, 차원, 측정항목, 기간과 집계값은 이 문서에 남겼지만 CSV 원본, 추출 시각, GA4 속성 시간대와 hostname 필터 상태는 별도 보존하지 않았다. 따라서 향후 독립 재현에는 제한이 있다. 후속 복구부터는 원본 export와 추출 조건을 함께 보존한다.

## 재발 방지

- 운영 제약 변경 후 실제 기존 행을 UPDATE하는 스모크 테스트를 수행한다.
- 조회 API의 5xx 비율과 `project_views`의 마지막 생성 시각을 모니터링한다.
- GA4 프로젝트 페이지 활성 사용자와 내부 일간 조회수 비율이 급변하면 경고한다.
- `NOT VALID` 제약도 새 INSERT/UPDATE에는 즉시 적용된다는 점을 마이그레이션 리뷰 체크리스트에 포함한다.

## 상위 모델 독립 감사 후속 조치 (2026-10-02)

- 복구 해시의 날짜 문자열이 세션 `DateStyle`에 따라 달라질 수 있던 문제를 확인했다. 모든 해시 생성·검증 지점에서 `to_char(viewed_on, 'YYYY-MM-DD')`를 사용해 기존 ISO 해시와 호환되면서 재실행 멱등성이 유지되도록 수정했다.
- 제약조건 교정 SQL의 `DROP → ADD → VALIDATE`를 명시적 `BEGIN`/`COMMIT`으로 묶어 자동 커밋 환경의 제약 공백을 제거했다.
- URL 테스트가 PostgreSQL 실행 테스트가 아닌 문자열 동기화 테스트뿐이었던 한계를 바로잡아 허용·차단 URL 계약, DateStyle 독립 해시, 교정 트랜잭션 순서 테스트를 추가했다.
- 후속 검증: unit test 37개 통과, `svelte-check` 오류·경고 0개, production build 성공, `git diff --check` 통과.
- 운영 DB의 기존 1,841개 행은 기본 ISO 날짜 표현으로 생성됐고 새 고정 표현과 동일하므로 데이터 재적용은 하지 않았다.
