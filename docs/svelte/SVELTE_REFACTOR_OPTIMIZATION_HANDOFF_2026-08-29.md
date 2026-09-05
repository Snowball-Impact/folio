# FOLIO Svelte 리팩토링·최적화 인수인계

이 문서는 Streamlit 원본과의 UIUX/기능 클로닝을 마친 현재 시점에서, Svelte 프로젝트를 구조적으로 리팩토링하고 성능을 개선하기 위한 새 컨텍스트용 시작 문서다.

이 문서의 목적은 새로운 기능을 추가하는 것이 아니다. 이미 검증된 동작을 보존하면서 코드 중복, 상태 흐름, 렌더링 비용, 유지보수 위험을 줄이는 것이다.

## 1. 현재 기준점

| 항목 | 현재 값 |
|---|---|
| Repository | `C:\workspace\folio` |
| Svelte app | `svelte_app/` |
| Streamlit original | `folio_app/` |
| 현재 브랜치 | `spike/svelte-public-pages` |
| 최근 커밋 | `fbbde60 Complete Svelte UIUX parity and verification` |
| 원격 상태 | `origin/spike/svelte-public-pages`로 push 완료 |
| 기본 개발 서버 | `http://127.0.0.1:5174/` 또는 관리형 실행 시 사용 포트 |
| Cloudflare preview | `127.0.0.1:8788` |
| 기준 데스크톱 | `1440x900` 또는 캡처 요구에 따른 `1440x1000` |
| 기준 모바일 | `390x844` |

현재 커밋은 기능 회귀와 인증 상태 전이 검증을 포함한다. 작업 시작 시 이 기준점을 임의로 “미완성”으로 재구현하지 말고, 먼저 변경 대상과 보호해야 할 동작을 분리한다.

## 2. 먼저 읽을 문서

새 컨텍스트가 열리면 아래 순서로 읽는다.

1. `docs/common/PROJECT_CONTEXT.md`
2. 이 문서
3. `docs/common/ENGINEERING_PLAYBOOK.md`
4. `docs/svelte/SVELTE_DEVELOPMENT_ENVIRONMENT.md`
5. `docs/migration/UIUX_CAPTURE_EVIDENCE_REVIEW_2026-08-28.md`
6. 현재 요청과 직접 관련된 원본 페이지 코드와 Svelte route/component
7. 배포 작업이면 `docs/svelte/CLOUDFLARE_DEPLOYMENT.md`

문서의 판정이 실제 코드와 다르면 코드를 우선하고, 문서를 같은 작업 묶음에서 고친다. 오래된 캡처나 과거 문서의 `pass`를 현재 상태의 근거로 재사용하지 않는다.

## 3. 현재 검증된 상태

### 기능 기준

- 마이페이지: 프로필 편집, 프로젝트 관리 액션, 삭제 확인/취소 상태를 검증했다.
- 알림: 목록, 읽음 처리, 프로젝트 보기, 헤더 팝오버, ESC 닫기, 반응형 버튼 배치를 검증했다.
- 프로젝트 등록: 입력 검증, Tiptap 본문 서식, 미리보기, 태그/플랫폼, 썸네일 모드, PBIX 업로드 진행 상태를 검증했다.
- 프로젝트 수정: 기존 값 로드, 본문 persistence, 썸네일 삭제/변경 옵션, PBIX 교체 실패 시 기존 연결 보존을 검증했다.
- 상세: 프로젝트 hero, 본문, Power BI iframe 또는 fallback, 외부 dashboard iframe, 댓글 답글/삭제 확인 상태를 검증했다.
- 실제 PBIX fixture 등록/게시와 서식 persistence는 opt-in 테스트로 확인했다. 테스트 후 원복 절차를 유지해야 한다.

### UIUX 기준

- 핵심 정보 계층, 모바일 hero 노출 규칙, 댓글 날짜/답글/삭제 액션의 조밀한 행 배치는 보강됐다.
- 전체 UIUX가 원본과 픽셀 단위로 완료된 것은 아니다.
- 동일 데이터와 외부 iframe 렌더링이 완전히 일치하지 않는 항목은 `partial`로 남긴다.
- Quill과 Tiptap의 아이콘 glyph, 일부 공통 shell의 폭과 inset은 기능 parity와 분리해 시각 차이로 기록한다.

### 마지막 검증 결과

- 인증 UI 회귀: 데스크톱/모바일 합계 `40 passed, 0 skipped`
- `npm.cmd run check`: `0 errors / 0 warnings`
- `npm.cmd run build`: SvelteKit Cloudflare production build 성공
- 최신 기준 URL과 fixture는 실행 시 환경 문서 및 테스트 변수에서 다시 확인한다. ID를 문서에 임의로 새로 만들지 않는다.

## 4. 리팩토링의 목표와 금지 범위

### 목표

1. route별 중복 상태와 변환 로직을 줄인다.
2. `app.css`의 중복·충돌·과도한 전역 선택자를 줄인다.
3. SSR/load, 인증, mutation, UI 상태의 경계를 명확하게 한다.
4. Tiptap, Power BI, iframe, 이미지 등 비용이 큰 기능의 로딩을 필요 시점으로 늦춘다.
5. 기능과 UIUX를 보존하는 작은 단위의 변경으로 유지보수성을 높인다.

### 금지 범위

- 원본 캡처를 다시 확인하지 않은 채 전역 CSS를 대규모로 재작성하지 않는다.
- “더 현대적인 UI”를 이유로 원본의 정보 계층, 액션 순서, 조밀도를 임의로 바꾸지 않는다.
- 리팩토링 중에 Cloudflare 배포 전용 문제, 새 기능, 데이터베이스 구조 변경을 한 번에 섞지 않는다.
- 실제 side effect가 발생하는 테스트를 기본 회귀 suite에 넣지 않는다.
- 증거가 없는 항목을 `pass`로 올리지 않는다. 증거가 없으면 `unknown`이다.

## 5. 반드시 기억할 교훈

### 5.1 전수 조사와 완료 선언

“페이지를 열어 봤다”는 전수 조사 증거가 아니다. 페이지별로 다음 다섯 가지가 있어야 한다.

| 증거 | 확인 내용 |
|---|---|
| 원본 코드 | 실제 렌더 조건, 상태 전이, 액션 순서, 데이터 계약 |
| 원본 캡처 | 같은 viewport와 같은 상태인지 |
| Svelte 코드 | route, component, CSS, API/load 경로 |
| Svelte DOM/캡처 | 실제 표시, 크기, visibility, selector, overflow |
| 검증 명령 | check/build 및 위험도에 맞는 브라우저/통합 테스트 |

데이터, 인증 상태, viewport, 외부 iframe이 다르면 “시각적으로 비슷하다”와 “동일하다”를 분리해서 기록한다.

### 5.2 원본 캡처 URL과 상태를 먼저 검증

- 과거 원본 수정 캡처는 폐기된 `edit_project` query를 사용해 마이페이지를 캡처한 적이 있다.
- 현재 원본 query는 `edit_project_id`이며, 가장 신뢰할 수 있는 수정 화면 재현은 마이페이지에서 실제 `수정` 버튼을 클릭하는 흐름이다.
- 캡처 파일명만 믿지 말고 URL, h1, 폼 값, 로그인 상태, 페이지 marker를 함께 확인한다.
- 캡처 자동화가 실패하면 제품 버그가 아니라 서버, 포트, 로그인, session, localStorage, selector, fixture 문제일 수 있다.

### 5.3 브라우저 런타임은 별도의 증거 계층

- 서버가 살아 있는 것과 브라우저가 실제 DOM을 읽는 것은 다른 문제다.
- Selenium/Playwright selector가 실패하면 먼저 실제 DOM의 `type`, label, placeholder, role을 확인한다.
- Svelte input에는 `type="text"`가 생략될 수 있으므로 `input[type="text"]`만 사용하지 않는다. 다음 형태를 우선한다.

  `input:not([type]), input[type="text"], textarea`

- 인증 테스트에서 `localStorage.clear()`를 사용하면 Supabase session까지 지워질 수 있다. draft 정리는 `folio-submit-draft:*` 키만 대상으로 한다.
- 같은 selector가 여러 요소에 매치되면 가장 가까운 route/component 범위로 제한한다. 댓글 삭제를 찾을 때 페이지 상단 프로젝트 삭제 버튼을 선택했던 오판이 있었다.
- 브라우저 런타임이 없으면 코드와 서버 점검은 계속할 수 있지만 DOM/캡처 판정은 `unknown`이다.

### 5.4 fixture와 404 처리

- 상세 테스트는 자동으로 첫 프로젝트를 선택하지 않는다. 테스트 목적에 맞는 유효한 project ID를 명시한다.
- 404 프로젝트, 삭제된 프로젝트, 댓글이 없는 프로젝트는 서로 다른 상태다.
- 404 후보를 제품 오류로 단정하지 말고 응답 status, project ID, 인증 상태, fixture 생성 시점을 함께 기록한다.
- 같은 데이터 비교가 필요하면 원본과 Svelte에 같은 fixture를 주고, 카드 수·댓글 수·본문·thumbnail·dashboard URL을 먼저 비교한다.

### 5.5 iframe과 visual preview

- iframe 요소가 존재하는 것만으로 dashboard가 동작한다고 말하지 않는다.
- Power BI SDK host, 삽입 iframe, fallback frame, 외부 dashboard는 각각 별도 상태다.
- 전체 페이지 캡처에서 iframe 내부가 비어 보일 수 있으므로, 전용 iframe 캡처와 DOM metric을 함께 남긴다.
- 저장된 dashboard URL이 있으면 원본의 표시 조건에 맞게 iframe 또는 fallback을 렌더링해야 한다.
- preview가 보이는 것만으로 통과시키지 않는다. sanitizer, 저장 payload, 상세 재진입에서 semantic structure가 유지되는지 확인한다.
- 기본 auto-cover 모드에는 `<img>`가 없을 수 있다. `img` 수가 0이면 auto-cover/card cover DOM과 실제 배경 표시를 확인한다.

### 5.6 본문 에디터와 sanitizer

- 원본 본문은 하나의 문자열로만 저장되는 것이 아니라 `problem`, `dataset`, `process`, `insights` 필드로 분해된다.
- Tiptap editor의 HTML은 저장 직전 네 개 필드로 동기화하고, 출력 시에도 sanitizer를 통과시킨다.
- `<h2>`, 목록, 인용, 안전한 링크가 editor, preview, 상세, 수정 재진입에서 유지되는지 확인한다.
- `<script>`, `javascript:` 링크, 위험 속성은 제거되어야 한다.
- Quill과 Tiptap의 toolbar glyph가 다르므로 기능 범위와 아이콘 픽셀 parity를 별도 판정한다.

### 5.7 댓글 밀도와 행 구조

- 날짜와 답글/삭제 버튼은 사용자가 한 묶음으로 인식하는 같은 footer/grid 행에 있어야 한다.
- 모바일에서도 날짜가 버튼과 겹치거나 다음 줄로 밀려 정보 계층이 깨지지 않는지 확인한다.
- 댓글 답글 열기/취소와 삭제 확인/취소는 실제 mutation 없이 상태 전이만 검증할 수 있다.
- 댓글 mutation을 검증할 때는 mock payload, trim, refresh, count 갱신, 이메일 endpoint 호출을 분리해서 확인한다.

### 5.8 인증과 mutation

- 보호 페이지 접근, Supabase session 복구, RLS, API endpoint 인증은 서로 다른 계층이다.
- UI에서 버튼을 숨기는 것은 보안 검증이 아니다.
- 기본 회귀는 mock 또는 읽기 전용으로 유지한다.
- 실제 PBIX 업로드, thumbnail 업로드, 본문 저장은 `@mutation` 계열 opt-in 테스트로 실행하고 snapshot/원복을 보장한다.
- PBIX 교체 실패 시 기존 Embed URL을 먼저 지우지 않는다.

### 5.9 환경과 Cloudflare

- 현재 Svelte adapter는 `@sveltejs/adapter-cloudflare`다. adapter-node 기준 문서를 현재 실행 기준으로 사용하지 않는다.
- `.xdg-config/.wrangler`는 로컬 Wrangler 로그/registry이며 배포에 필요한 파일이 아니다. 저장소에 커밋하지 않는다.
- 배포에는 `svelte_app/wrangler.jsonc`, Cloudflare adapter, 빌드 결과, dashboard variables/secrets가 필요하다.
- Cloudflare Pages 배포가 성공해도 PBIX 크기 제한, 로컬 Playwright thumbnail capture, socket SMTP는 별도 호환성 결정이 필요하다.
- `npm.cmd run build` 성공은 실제 Cloudflare preview/deploy와 동일하지 않다.

### 5.10 테스트 비용 관리

- 작은 CSS 문구나 저위험 국소 변경마다 인증 40개 전체를 반복하지 않는다.
- 여러 저위험 변경을 하나의 작업 묶음으로 모아 `check`와 필요한 표적 테스트를 한 번 실행한다.
- 상태 전이, auth, persistence, iframe, sanitizer, mutation orchestration을 바꾸면 표적 테스트를 우선하고 묶음 종료 시 전체 suite를 실행한다.
- 시각 변경은 관련 viewport의 캡처와 DOM metric을 남긴다. 코드 구조만 바꾼 경우 캡처를 자동으로 요구하지 않는다.
- 테스트를 생략할 때는 생략 이유와 대체 확인을 결과에 남긴다.

## 6. 리팩토링 실행 순서

### Phase R0. 기준선 고정

- `git status --short`와 현재 commit을 기록한다.
- `npm.cmd run check`, `npm.cmd run build`를 실행한다.
- 필요한 경우 인증 suite를 기준 fixture와 함께 1회 실행한다.
- 현재 동작을 바꾸지 않는 리팩토링인지, UI 변경까지 포함하는지 범위를 한 문장으로 고정한다.

### Phase R1. 구조 지도 작성

먼저 아래 영역의 중복과 경계를 목록화한다.

- `src/routes/`: load, auth gate, mutation, 페이지 조합
- `src/lib/components/`: ProjectCard, project form, editor, comments, PowerBI
- `src/lib/`: format, project body, auth, API/data mapping
- `src/app.css`: global shell, page sections, responsive overrides, duplicate selectors
- `tests/`: fixture 선택, mock, opt-in mutation, viewport project 설정

이 단계에서는 코드를 고치지 않고 “중복”, “상태 소유자”, “외부 side effect”, “시각 계약”을 표로 만든다.

### Phase R2. 저위험 구조 리팩토링

권장 순서:

1. 타입과 상수 중복 통합
2. 순수 formatter/normalizer 추출
3. 반복되는 project display model 변환 통합
4. 컴포넌트 내부의 파생 상태와 이벤트 handler 정리
5. route별 중복 error/loading/empty 상태 정리
6. CSS selector 중복과 dead rule 정리

각 단계에서 public route, DOM marker, form name, test selector, API payload를 보존한다.

### Phase R3. 선택적 성능 최적화

측정 결과가 있는 항목만 적용한다.

- 최초 화면에 필요 없는 Tiptap extension과 editor initialization 지연
- Power BI SDK와 외부 iframe의 조건부 로딩
- 중복 Supabase fetch와 동일 데이터의 재변환 제거
- 큰 이미지의 크기/지연 로딩/불필요한 재요청 점검
- SSR에서 계산 가능한 값을 client effect로 미루지 않기
- `app.css`의 중복 규칙과 과도한 selector 범위 축소
- bundle 분석 후 실제 큰 dependency만 분리

최적화 후에는 기능이 같아도 로딩 순서, iframe ready 상태, hydration, 접근성 focus가 바뀔 수 있으므로 표적 브라우저 검증이 필요하다.

### Phase R4. 회귀와 문서 정리

- 변경 묶음의 `check`와 `build`를 실행한다.
- 영향 route의 표적 테스트와 필요한 viewport 캡처를 실행한다.
- 상태 전이나 공통 컴포넌트를 바꿨다면 인증 suite를 한 번 실행한다.
- 결과를 `docs/migration/UIUX_CAPTURE_EVIDENCE_REVIEW_2026-08-28.md` 또는 새 리팩토링 기록에 추가한다.
- 변경 파일, 검증 결과, 남은 `partial/unknown`, 다음 작업을 커밋 전에 요약한다.

## 7. 검증 명령 기준

### 기본 확인

```powershell
cd C:\workspace\folio\svelte_app
npm.cmd run check
npm.cmd run build
```

### 비인증 UI

```powershell
npm.cmd run test:ui
```

### 인증 UI

실제 `.env` 값은 출력하지 않는다. 테스트 계정과 fixture는 환경 변수로 주입한다.

```powershell
$env:PLAYWRIGHT_BASE_URL="http://127.0.0.1:5176"
$env:PLAYWRIGHT_PROJECT_ID="<valid-project-id>"
npm.cmd run test:ui:auth -- --project=desktop --project=mobile
```

### 선택적 실제 side effect

`@mutation`, `@mutation-thumbnail`, `@mutation-pbix-safe`, `@mutation-pbix-live`는 일반 회귀에 포함하지 않는다. 실행 전 대상 project, 원복 가능성, 외부 서비스 비용과 상태 변경을 확인한다.

## 8. 완료 정의

리팩토링/최적화 작업 하나의 완료는 다음을 의미한다.

- 변경 목적과 영향 범위가 문서에 한 문장으로 적혀 있다.
- 중복 제거 또는 성능 개선이 실제 코드 diff로 확인된다.
- 기존 route, auth, payload, semantic HTML, responsive behavior가 유지된다.
- 위험도에 맞는 `check`, `build`, 표적 테스트가 통과한다.
- UI 변경이면 데스크톱/모바일 DOM 또는 캡처 근거가 있다.
- side effect가 있는 테스트는 대상과 원복 결과가 기록되어 있다.
- 남은 차이는 `pass`, `partial`, `fail`, `unknown` 중 하나로 표시한다.
- 문서에 없는 완료 선언을 하지 않는다.

## 9. 작업 보고 형식

각 작업 종료 시 아래 형식으로 짧게 기록한다.

```text
범위: [이번에 바꾼 것]
보존한 계약: [route / DOM / payload / auth / responsive]
변경 파일: [핵심 파일]
검증: [명령과 결과]
판정: [pass / partial / fail / unknown]
남은 위험: [없음 또는 구체적 항목]
다음 작업: [한 단계]
```

## 10. 모델 선택 가이드

이 저장소 작업은 단순 코드 생성보다 원본 코드 조사, 캡처/DOM 증거 확인, 인증과 fixture 분리, 단계적 리팩토링, 테스트 비용 조절이 중요하다.

권장 기준은 다음과 같다.

- 현재 사용 중인 모델이 GPT-5.6 계열이고 긴 컨텍스트와 도구 사용이 안정적이라면, 전체 리팩토링 주 모델은 그대로 유지하는 편이 안전하다.
- GPT-5.5 `medium`으로 바꾸는 것도 가능하다. OpenAI 공식 문서는 GPT-5.5를 코딩·도구 중심·다단계 작업에 적합하다고 설명하고, `medium`을 품질·신뢰성·지연·비용의 균형점으로 권장한다.
- 다만 모델을 바꾸면 기존 지시문을 그대로 복사하지 말고, 이 문서와 성공 기준을 기준으로 짧은 baseline 작업을 먼저 실행한다.
- 5.5 `medium`은 문서 정리, 국소 리팩토링, 표적 테스트에는 충분하다. 여러 페이지의 원본/Svelte/브라우저 증거를 동시에 재검증하는 큰 작업에서는 현재 모델을 유지하고, 5.5는 비용·속도 비교용으로 제한하는 것이 좋다.
- 모델 변경 여부와 관계없이 “전수 조사”, “완료”는 위 증거표와 검증 결과가 있을 때만 사용한다.

모델 전환을 실제로 결정할 때는 같은 작은 작업 2개를 비교한다.

1. `ProjectCard`와 공통 project display model의 중복을 찾아 구조 변경 계획 작성
2. 댓글 또는 본문 editor의 한정된 리팩토링과 `check`/표적 테스트 실행

비교 기준은 누락된 근거 수, 잘못 선택한 selector 수, 불필요한 테스트 실행 수, 최종 diff의 범위, 검증 성공 여부다. 속도만으로 모델을 판단하지 않는다.

공식 참고: [OpenAI GPT-5.5 model guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.5)

## 11. 새 컨텍스트의 첫 작업

첫 작업은 코드 수정이 아니라 다음 세 가지다.

1. `git status --short`와 현재 branch/commit 확인
2. 위의 기준 명령 실행 또는 최신 검증 기록 확인
3. 구조 지도 작성 후, 실제 중복이 확인된 가장 작은 리팩토링 하나를 선택

첫 리팩토링 후보는 `ProjectCard`와 project display model, 또는 `app.css`의 중복 selector처럼 기능 계약을 보존하기 쉬운 영역으로 시작한다. 인증, PBIX, iframe, 본문 persistence를 동시에 건드리지 않는다.

## 12. 2026-08-29 실행 종료 기록

이번 작업에서는 위 원칙에 따라 공통 project form/input/save workflow와 API 인증 헬퍼를 추출하고, Tiptap·KaTeX·Power BI의 조건부 로딩, Power BI 성능 신호, 선택형 RUM 어댑터, Cloudflare smoke 재현성, 성능 예산 검사를 반영했다.

최종 일괄 검증은 다음과 같다.

- `npm.cmd run verify`: check, build, 성능 예산, Cloudflare smoke, Supabase contract smoke, security smoke 통과
- 공개 UI: desktop/mobile 각 4 passed, 공개 상세 fixture 미설정 케이스 각 1 skipped
- 외부 공개 상세 fixture: desktop/mobile 각 1 passed
- 기존 외부 인증 회귀: desktop/mobile 각 14 passed·6 skipped
- mutation 회귀: 본문 persistence와 thumbnail auto-cover 원복 포함 통과

운영 시 `PUBLIC_RUM_ENDPOINT`를 배포 환경에 설정하면 web vitals와 Power BI metric 전송이 활성화된다. 실제 PBIX live Import/복구는 승인된 `PLAYWRIGHT_PBIX_LIVE_PROJECT_ID`와 원복 절차가 준비된 뒤에만 실행한다. 세부 상태와 명령은 `docs/svelte/SVELTE_REFACTOR_CHECKLIST_2026-08-29.md` 및 `docs/svelte/SVELTE_RUM_CONTRACT_2026-08-29.md`를 기준으로 한다.

이번 범위에서는 전용 PBIX live fixture와 staging RUM endpoint를 제공하지 않기로 결정했으므로, 두 외부 실데이터 검증은 생략한다. 일반 개발·빌드·회귀 검증의 완료 상태에는 영향을 주지 않는다.

최종 전수 리뷰에서 본문 이미지 업로드와 PBIX 교체를 동시에 수행할 때 중간 본문 저장이 `delete_pbix` 플래그를 재적용할 수 있는 경로를 확인했다. `projectInputForPbixReplacement`로 초기 저장과 중간 저장 모두 기존 연결 보존 규칙을 적용했으며, 단위 테스트와 전체 회귀를 다시 통과시켰다.
