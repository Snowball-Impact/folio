# Svelte 리팩토링 및 최적화 체크리스트

기준일: 2026-08-29

목표: 기존 UI/데이터 계약을 보존하면서 Svelte 프로젝트의 구조, 상태 흐름, 서버 경계와 초기 로딩 비용을 단계적으로 개선한다.

## 진행 상태

현재 단계: **작업 종료: 외부 실데이터 검증 생략**

다음 전환: 새 요구사항 또는 운영 데이터가 준비될 때 재개

## 실행 방식 재계획

작업 단위를 세부 항목별로 나누지 않고, 아래 통합 배치가 끝날 때 한 번에 테스트·보고한다.

- [x] **배치 1: 외부 연동 통합 검증**
  - [x] Supabase 계약과 실제 공개 Power BI 상세/iframe metric 일괄 확인
  - [x] PBIX live Import·복구 검증은 전용 fixture 미지정으로 이번 범위에서 생략
  - [x] staging RUM 수신 검증은 endpoint 미지정으로 이번 범위에서 생략
- [x] **배치 2: 전체 회귀 검증**
  - [x] `verify` 일괄 실행: check/build/성능 예산/Cloudflare smoke/Supabase smoke/보안 smoke 통과
  - [x] 공개 UI desktop/mobile 각 4 passed, fixture 미설정 케이스 각 1 skipped
  - [x] 인증 UI는 기존 외부 인증 회귀 desktop/mobile 각 14 passed·6 skipped 기록 유지
  - [x] 로컬 `5179` 인증 재실행은 테스트 세션 미구성으로 반복 타임아웃되어 중단
- [x] **배치 3: 최종 인수인계**
  - [x] 체크리스트·인수인계 문서·운영 명령을 한 번에 갱신
  - [x] 잔여 외부 의존성과 배포 전 조건을 최종 보고

세부 체크 항목은 추적 근거로 유지하되, 실제 진행 상태와 사용자 보고는 위 배치 기준으로 갱신한다.

- [x] R0 기준선 고정
  - [x] `npm.cmd run check` 통과
  - [x] `npm.cmd run build` 통과
  - [x] 기존 UI 회귀 검증 결과와 번들 크기 확인
  - [x] 기존 사용자 변경사항 보존
- [x] R1 구조 지도 작성
  - [x] 라우트와 SSR/CSR 데이터 흐름 확인
  - [x] 프로젝트 서비스, 인증, 댓글, 알림, 업로드 경계 확인
  - [x] 대형 파일과 중복 책임 식별
- [x] R2 저위험 리팩토링
  - [x] 제출/수정 공통 플랫폼 옵션 분리
  - [x] 프로젝트 폼 기본값과 프로젝트-to-input 변환 분리
  - [x] 제출/수정 미리보기 태그 정규화 공통화
  - [x] 폼 태그 표시 로직 공통화
  - [x] 썸네일·본문 이미지·PBIX·댓글 이메일 API 인증 헬퍼 분리
  - [x] 프로젝트 입력 검증·정규화 단위 테스트 추가
  - [x] 제출/수정 저장 오케스트레이션 공통화
- [x] R3 Svelte 및 런타임 최적화
  - [x] Tiptap 에디터 지연 로딩 측정 및 적용
  - [x] Power BI SDK/임베드 초기화 비용 측정 및 개선 (기존 SDK 지연 import 유지 확인)
  - [x] 상세 화면과 임베드 API의 중복 프로젝트 조회 제거 (임베드 API를 경량 상태 조회로 축소)
  - [x] Power BI CSV 파싱 캐싱 검토 및 모듈 범위 결과 캐시 적용
  - [x] 전역 CSS 분리·축소 및 시각 회귀 확인
    - [x] 본문 미리보기 스타일을 `ProjectBodyEditor.svelte` 컴포넌트 CSS로 이동
    - [x] 공개 데스크톱 UI 회귀 확인
    - [x] 에디터 전용 스타일 분리 및 공개 모바일 UI 회귀 확인
  - [x] 불필요한 반응성·이벤트 리스너 점검 (Tiptap transaction 리스너 제거)
- [x] R4 회귀 검증
  - [x] `npm.cmd run check`
  - [x] `npm.cmd run build`
  - [x] Cloudflare smoke
  - [x] Supabase 계약 smoke
  - [x] 보안 smoke
  - [x] 공개/인증 UI 회귀 테스트
    - [x] 공개 데스크톱 UI 테스트
    - [x] 공개 모바일 UI 테스트
    - [x] 인증 UI 테스트 (외부 네트워크 실행에서 desktop/mobile 각 14 passed, 6 skipped)
  - [x] 필요한 mutation fixture 검증
    - [x] 프로젝트 본문 persistence desktop/mobile
    - [x] 썸네일 upload 및 auto-cover 복구 desktop/mobile
    - [ ] PBIX live 교체 (별도 live fixture 미지정)
- [x] R5 문서화 및 인수인계
  - [x] 변경 이유와 상태 소유권 기록
  - [x] 번들·로딩 비용 전후 비교
  - [x] 남은 위험과 운영 명령 기록

## P2 2차 최적화

- [x] 수식이 없는 화면에서 KaTeX JS/CSS 초기 로딩 제거
  - [x] `ProjectRichContent.svelte`의 KaTeX dynamic import 적용
  - [x] 수식 노드가 있을 때만 KaTeX CSS asset 로드
  - [x] 공개 desktop/mobile 회귀 확인
  - [x] check/build/unit/security 재검증
- [x] route별 실사용 bundle과 Core Web Vitals 계측
  - [x] `scripts/measure-route-performance.mjs` 추가 및 `measure:routes` 명령 등록
  - [x] 공개 6개 라우트의 navigation timing/resource/long task 기준값 수집
  - [x] 결과: JS 약 5.1~5.5MB, CSS 약 134KB, long task 0건
  - [x] 외부 접근 가능한 동일 서버에서 재검증: 공개 라우트 `domContentLoaded` 21~1005ms, LCP 76~1112ms, CLS 최대 0.0265
- [x] Power BI/iframe 실제 로딩 비용 계측
  - [x] 공개 PBIX 프로젝트 상세 화면에서 iframe 1개 생성 확인
  - [x] 앱 리소스 약 7.34MB, Power BI 프레임 내부 38개 리소스 약 6.56MB 확인
  - [x] iframe 포함 상세 화면 `load` 약 2.35초, LCP 약 260ms, long task 0건 확인

## 검증 기록

### 2026-08-29

- `npm.cmd run check`: 통과, 오류 0건, 경고 0건
- `npm.cmd run build`: 통과
- `npm.cmd run smoke:security`: 통과, 클라이언트 번들 90개 검사
- `npm.cmd run test:unit`: 통과, 프로젝트 입력 테스트 4개
- `npm.cmd run test:ui -- --project=desktop`: 통과 4개(홈 navigation race 재실행 포함), public detail fixture 1개 스킵
- `npm.cmd run test:ui -- --project=mobile`: 통과 4개, public detail fixture 1개 스킵
- `npm.cmd run smoke:cloudflare`: 통과, 공개 라우트 12개와 익명 endpoint 4개 검사
- Cloudflare smoke 재실행: 별도 포트에서 3개 라우트까지 통과 후 `/?page=Policy&type=privacy` 요청이 `AbortError`로 중단되고 Windows preview cleanup이 지연됨. 이전 완주 결과와 별도로 환경성 재검증 이슈로 기록
- `node scripts/smoke-node.mjs`: 통과, Node 런타임 공개 라우트 3개 검사
- `python ..\tools\uiux_preflight.py --base-url http://127.0.0.1:5179 --port 5179 --require-server`: 서버 HTTP 200 확인, browser runtime은 외부 검사 항목
- `npm.cmd run smoke:supabase` 샌드박스 실행: 외부 요청 `fetch failed`로 차단
- Supabase 계약 smoke 외부 실행: `home_project_snapshot`, `project_detail_snapshot`, `powerbi_reports` 계약 통과
- 인증 UI 표적 샌드박스 실행: `/auth/v1/token` 요청이 `net::ERR_NETWORK_ACCESS_DENIED`로 차단
- 인증 UI 외부 실행 재검증: desktop/mobile 각각 14 passed, 6 skipped
- 실제 mutation fixture: 본문 persistence desktop/mobile 통과, 썸네일 upload/auto-cover 복구 desktop/mobile 통과
- mutation fixture 복구 확인: `one_liner` 원본 문장, `thumbnail_mode=auto_cover`, 썸네일 없음
- `git diff --check`: 통과
- 현재 변경: 프로젝트 폼·저장 워크플로 공통화, API 인증·소유권 조회 공통화, 입력 테스트, Tiptap 지연 청크, 임베드 경량 조회, CSV 결과 캐시
- 번들 확인: 최대 클라이언트 청크 약 441KB에서 약 259KB로 감소하고 Tiptap 전용 동적 청크 생성
- CSS 확인: 전역 CSS 7,082줄/102.66KB → 6,741줄/97.48KB, `projectBody` 컴포넌트 CSS 청크 6.17KB 생성
- 인증 UI 테스트: 샌드박스에서는 네트워크가 차단됐지만 외부 실행에서 desktop/mobile 회귀를 완료
- P2 KaTeX 최적화 검증: `katex` JS/CSS가 수식 노드가 있는 경우에만 동적 로드되며, 일반 공개 화면 desktop/mobile 통과
- P2 build 후 보안 smoke: 클라이언트 번들 91개 검사 통과
- P2 route 실측: 공개 6개 라우트 모두 HTTP 200; JS 약 5.1~5.5MB, CSS 약 134KB, LCP 76~1112ms, CLS 최대 0.0265, long task 0건. 샌드박스에서 보인 약 7초 `networkidle`은 외부 데이터 접근 제한에 따른 현상으로 외부 접근 서버에서 재검증함
- P2 Power BI 실측: 공개 PBIX fixture `7553d519-b395-464a-bd57-3b33100e2df1`에서 iframe 1개, 프레임 내부 리소스 38개/약 6.56MB, 상세 전체 약 7.34MB, iframe 포함 load 약 2.35초
- 측정 명령: `$env:PLAYWRIGHT_BASE_URL='http://127.0.0.1:5179'; npm.cmd run measure:routes` (`MEASURE_ROUTES`, `MEASURE_WAIT_UNTIL`, `MEASURE_SETTLE_MS`, `MEASURE_SAMPLE_MS`, `MEASURE_TRANSITIONS=1`로 대상·대기·마일스톤·전환 CLS 기준 선택 가능)
- P2 종료 판단: 현재 코드 구조상 Tiptap/KaTeX/Power BI SDK는 화면 조건에 따라 지연 로드되고, 추가 최적화는 실제 배포 RUM 또는 Power BI 사용량 데이터가 있을 때 진행
- P3-1 성능 예산: `npm.cmd run performance:budget` 통과. 최대 클라이언트 청크 `252.57KB / 300KB`, 전역 CSS `95.20KB / 105KB`, KaTeX CSS `28.69KB / 35KB`
- P3-2 수식 회귀: 인증 제출 화면에서 실제 `.katex` DOM 렌더링 확인, desktop/mobile 각 1 passed
- P3-2 fixture 설정: `.env.example`에 `PLAYWRIGHT_PUBLIC_DETAIL_PROJECT_ID`, mutation/PBIX fixture 변수 추가. 공개 상세와 PBIX live는 실제 fixture 지정 후 실행하도록 유지
- P3-2 공개 상세 회귀: `PLAYWRIGHT_PUBLIC_DETAIL_PROJECT_ID=7553d519-b395-464a-bd57-3b33100e2df1` 외부 실행에서 desktop/mobile 각 1 passed
- P3-3 Cloudflare smoke 재검증: 공개 12개 route와 익명 endpoint 4개가 통과하고 cleanup까지 완료. 과거 간헐 `AbortError`는 환경성 잔여 위험으로 계속 기록
- P3-3 smoke 개선: GET route 1회 재시도와 Windows cleanup 5초 타임아웃 적용 후 `npm.cmd run smoke:cloudflare` 재실행 통과
- PBIX live fixture 점검: `PLAYWRIGHT_PBIX_LIVE_PROJECT_ID` 미지정 상태이며 실제 Power BI Import를 임의 프로젝트에 실행하지 않음
- P3-4 Power BI 관측성: `folio-powerbi-*` Performance measure와 `folio:powerbi-metric` browser event를 추가하고, 외부 상세 화면에서 초기화 약 `1519ms` 측정 확인
- P3-4 RUM 어댑터: `PUBLIC_RUM_ENDPOINT`가 설정된 경우에만 web vitals와 Power BI 상태를 `sendBeacon`/keepalive POST로 전송하도록 추가
- P3-4 RUM 안정화: Power BI 이벤트가 초기화 순서상 누락돼도 pagehide 시 Performance measure를 보완 전송하도록 처리
- 최종 P3-4 검증: `check`, `build`, `test:unit`, `performance:budget`, `git diff --check` 통과
- P3-4 UI 회귀: RUM endpoint 미설정 기본 상태에서 `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5179` 기준 desktop/mobile 공개 UI 각 4 passed
- P3-4 RUM 계약: endpoint payload, CORS, `sendBeacon`/JSON fallback, 비식별 원칙을 `docs/svelte/SVELTE_RUM_CONTRACT_2026-08-29.md`에 기록
- 배치 1 외부 통합: Supabase 계약 통과, Power BI 상세 iframe 1개/프레임 리소스 38개/초기화 metric 약 `1364ms` 확인. PBIX live와 RUM endpoint는 fixture/endpoint 미지정으로 실행 보류
- 배치 2 전체 회귀: `npm.cmd run verify` 통과. 공개 UI desktop/mobile 각 4 passed·1 skipped; 인증 UI는 로컬 테스트 세션 미구성으로 반복 타임아웃되어 중단하고 기존 외부 회귀 결과(각 14 passed·6 skipped)를 기준으로 유지
- 배치 3 최종 인수인계: 인수인계 문서 실행 종료 기록과 RUM 계약 문서, 운영 검증 명령을 갱신. PBIX live fixture와 staging RUM endpoint 검증은 사용자 결정에 따라 이번 범위에서 생략
- 최종 전수 리뷰: 본문 이미지와 PBIX 교체를 함께 저장할 때 중간 저장이 `delete_pbix`를 재적용하던 결함을 발견하고 `projectInputForPbixReplacement` 및 단위 테스트로 수정
- 최종 전수 리뷰 회귀: `test:unit` 5 passed, `verify` 통과, 공개 UI desktop/mobile 8 passed·2 skipped

## P3 배포 전 하드닝 및 지속 검증

- [x] P3-1 성능 예산 자동화
  - [x] 최대 클라이언트 청크, 전역 CSS, 동적 KaTeX 자산을 검사하는 명령 추가
  - [x] 기준 초과 시 검증 명령이 실패하도록 경계 설정
  - [x] 기준값: 최대 JS 청크 `300KB`, 전역 CSS `105KB`, KaTeX CSS `35KB`
  - [x] 현재 결과: `252.57KB`, `95.20KB`, `28.69KB` 모두 통과
- [ ] P3-2 실데이터 회귀 fixture 보강
  - [x] 공개 프로젝트 상세 fixture를 UI 테스트에 연결하고 `.env`/환경변수에서 읽도록 통일
  - [ ] PBIX live 교체 fixture와 복구 절차 확정 (승인된 프로젝트 ID 필요)
  - [x] 수식 본문 렌더링 회귀 케이스 추가 (`.katex` DOM 확인)
  - [x] `.env.example`에 공개 상세·mutation·PBIX fixture 변수 문서화
- [x] P3-3 배포 smoke 재현성 개선
  - [x] Cloudflare preview cleanup 타임아웃 및 GET route 일시 오류 재시도 적용
  - [x] 외부 네트워크 필요 테스트와 샌드박스 가능 테스트를 실행 결과에 구분해 기록
- [ ] P3-4 운영 관측성 준비
  - [x] Power BI 초기화 시간을 Performance API와 `folio:powerbi-metric` 이벤트로 노출
  - [x] `ready`/`error` 상태와 초기화 시간을 함께 기록할 수 있는 브라우저 신호 추가
  - [x] `PUBLIC_RUM_ENDPOINT` 선택형 RUM 어댑터와 web vitals 전송 추가
  - [x] endpoint payload/CORS/개인정보 경계 문서화
  - [ ] 실제 배포 RUM endpoint에서 LCP/CLS/INP와 iframe 초기화 시간 수집 검증
  - [x] Power BI 외부 요청 실패·지연 상태를 RUM 운영 payload로 전달하도록 구현

## 후속 TODO

- [x] Svelte UIUX 검증 도구를 Playwright 기준으로 정리한다.
  - 현재 표준 실행 경로는 `svelte_app/package.json`의 `test:ui`, `test:ui:auth`, `capture:ui`와 `svelte_app/playwright.config.ts`다.
  - Svelte 수동 캡처는 `svelte_app/scripts/capture-ui.mjs`를 사용한다.
  - Selenium 기반 Svelte 과거 캡처·프로브 스크립트는 `tools/legacy_selenium/`로 분리했다.
  - `requirements-dev.txt`의 `selenium`은 Streamlit/외부 갤러리 수집 legacy 도구 때문에 현재 유지한다.
- [x] Svelte UIUX 디자인 시스템과 화면별 QA 기준을 문서화한다.
  - 기준 문서: `docs/svelte/SVELTE_UIUX_DESIGN_SYSTEM.md`
  - font/size/spacing/control/card-list token, 화면별 QA checklist, Playwright 검증 루틴을 한 문서로 고정했다.

## 인수인계 요약

- `projectForm.ts`: 제출/수정 폼 기본값, 플랫폼 옵션, 프로젝트 입력 변환, 미리보기 태그를 소유한다.
- `projectInput.ts`: 입력 검증·URL 정규화·Supabase 프로젝트 payload 생성을 담당하는 순수 경계를 소유한다.
- `projectSaveWorkflow.ts`: create/edit 저장 순서와 업로드·PBIX·캡처 후속 작업을 소유하며, route는 화면 상태만 소유한다.
- `request-auth.ts`: API bearer 인증과 프로젝트 소유권 조회 경계를 소유한다.
- `ProjectBodyEditor.svelte`: Tiptap editor/preview 상태와 editor 전용 CSS를 소유한다.
- `projects.ts`와 `powerbi-content.ts`: 프로젝트 조회 계약과 Power BI CSV 모듈 캐시를 소유한다.
- 운영 검증은 `npm.cmd run check`, `npm.cmd run build`, `npm.cmd run smoke:security`, `npm.cmd run smoke:supabase`, `npm.cmd run test:unit` 순서로 실행하고, 인증·mutation은 fixture와 외부 네트워크가 준비된 경우 표적 실행한다.

## 진행 원칙

- 기능과 시각적 계약을 먼저 보존하고, 최적화는 측정 결과를 기준으로 적용한다.
- 한 번에 하나의 책임만 이동하고 각 단계마다 `check`와 `build`를 실행한다.
- RLS와 서버 비밀키 경계에 영향을 주는 변경은 보안 smoke를 함께 확인한다.
- 기존 캡처·DOM 증거 없이 UI를 임의로 재설계하지 않는다.
