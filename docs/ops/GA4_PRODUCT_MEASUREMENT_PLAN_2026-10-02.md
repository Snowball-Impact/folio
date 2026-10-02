# GA4 Product Measurement 개선 계획 (2026-10-02)

## 배경

Meta 광고 기간(2026-09-22~30)에 Acquisition은 확인됐지만 `view_item`, `project_submit`, `login`, `pbix_import_success`, `project_share_open`이 GA4에 없어서 Experience·Create·Interact를 판정할 수 없었다. 코드 점검 결과 Svelte 앱은 SPA `page_view`만 전송하고 있었으며, 핵심 Product Event는 구현되지 않은 상태였다.

## 이번 구현

| 이벤트 | 발생 조건 | 전송 파라미터 |
|---|---|---|
| `view_item` | 프로젝트 상세 화면 진입 | `project_id`, `platform`, `content_type=project` |
| `login` | 이메일 로그인 성공 | `method=email` |
| `project_submit` | 신규 프로젝트의 전체 저장 workflow 성공 | `project_id`, `platform`, `has_pbix` |
| `pbix_import_success` | 신규 PBIX 게시 또는 기존 PBIX 교체 성공 | `project_id`, `operation=create|replace` |
| `share` | 프로젝트 공유 링크 복사 성공 | `method=copy_link`, `content_type=project`, `item_id` |
| `project_share_open` | FOLIO 공유 UTM으로 프로젝트 상세 진입 | `project_id`, `platform` |

`project_share_open`은 같은 브라우저 세션에서 같은 프로젝트당 한 번만 전송한다. 새 공유 링크는 프로젝트 상세 URL을 직접 가리키며, 과거 형식의 `/?page=Home&project_id=...` 링크도 서버 리다이렉트 과정에서 UTM 파라미터를 보존한다.

## 개인정보·보안 원칙

- 이메일, 사용자 ID, 사용자 이름, PBIX 파일명, 오류 메시지는 GA4로 전송하지 않는다.
- `project_id`는 공개 콘텐츠 식별 목적으로만 사용한다.
- 분석 호출은 브라우저에서만 실행하고 인증 성공 여부를 바꾸거나 서버 권한 판단에 사용하지 않는다.
- GA 로더가 없거나 차단돼도 모든 제품 기능은 정상적으로 계속된다.

## GA4 설정

GA4 관리 화면에서 다음 이벤트 파라미터를 이벤트 범위 맞춤 측정기준으로 등록한다.

- `project_id`
- `platform`
- `operation`
- `has_pbix`

권장 핵심 이벤트(Key event)는 `project_submit`이다. `login`, `view_item`, `share`, `project_share_open`은 초기에는 일반 이벤트로 두고 빈도와 품질을 먼저 확인한다. `pbix_import_success`는 PBIX 퍼널을 별도로 운영할 때 핵심 이벤트로 승격한다.

## 검증 절차

배포 후 GA4 DebugView 또는 Realtime에서 다음 순서로 검증한다.

1. 프로젝트 상세 진입 → `view_item`
2. 공유 링크 복사 → `share`
3. 복사한 링크를 새 시크릿 세션에서 열기 → `project_share_open`
4. 테스트 계정 로그인 → `login`
5. 일반 프로젝트 등록 → `project_submit`
6. 테스트 PBIX 프로젝트 등록 또는 교체 → `pbix_import_success`

각 이벤트는 성공 동작에서 한 번만 발생하고 이메일·파일명 등 개인정보가 파라미터에 없는지 확인한다. GA4 표준 보고서 반영에는 처리 시간이 걸릴 수 있으므로 즉시 검증은 DebugView/Realtime을 사용한다.

## 다음 분석 기준

- Discover: Paid sessions, new users, landing users
- Experience: `view_item` 사용자 수, 랜딩 → 다른 프로젝트 전환율, 참여 시간
- Create: 로그인 사용자 대비 `project_submit` 전환율, `pbix_import_success` 성공률
- Interact: `share` → `project_share_open` 전환율
- Return: 신규 유입 cohort의 7일·28일 재방문율

좋아요와 댓글은 현재 핵심 측정 공백을 닫은 뒤 2차로 `like`, `comment_create` 이벤트를 추가한다.

### 광고 랜딩 탐색 개선

광고 트래픽이 한 프로젝트에 집중되고 전체 콘텐츠 탐색 여부를 확인할 수 없었던 문제를 줄이기 위해 프로젝트 상세 하단에 관련 프로젝트 최대 4개를 노출한다. 같은 태그를 가장 우선하고, 같은 플랫폼·조회수·최신성 순으로 보조 정렬한다. 관련 카드 클릭은 `related_project_click`으로 기록하며 현재 프로젝트 `project_id`, 이동할 `target_project_id`, 대상 `platform`을 전송한다.

다음 광고 실험에서는 `view_item` 사용자 중 `related_project_click` 발생 사용자 비율을 상세 → 추가 탐색 전환율로 사용한다.

## 2026-10-02 운영 배포 검증

- GitHub `main`: `e2279c6` 푸시 완료
- Cloudflare Pages 배포: `https://da7d7a76.folio-5l4.pages.dev`
- 운영 도메인 `folio.it.kr`, `www.folio.it.kr`: HTTP 200
- 실제 운영 Chromium 검증:
  - 프로젝트 상세 `view_item` 확인
  - 공유 링크 복사 `share` 확인
  - 새 세션의 공유 링크 진입 `project_share_open` 확인
  - 테스트 계정 로그인 성공 `login` 확인
- GA4 Data API 즉시 재조회: 신규 이벤트 행은 아직 없음. 표준 보고 처리 지연을 고려해 다음 날 재확인한다.

운영 점검은 `node scripts/verify-ga4-product-events.mjs https://folio.it.kr`로 반복할 수 있다. 로컬 `.env`에 테스트 계정이 있으면 `login`까지 검사하고, 없으면 공개 이벤트만 검사한다. 이 스크립트는 프로젝트 등록이나 PBIX 교체를 수행하지 않는다.

배포 과정에서 `wrangler.jsonc`의 프로젝트명이 실제 Pages 프로젝트와 다른 `folio-svelte`로 설정돼 기본 배포 명령이 실패하는 문제를 발견했다. 실제 프로젝트명 `folio`로 수정해 이후 `npm run deploy:cloudflare`가 올바른 대상을 사용하도록 했다.
