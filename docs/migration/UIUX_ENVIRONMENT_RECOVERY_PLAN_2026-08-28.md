# UIUX 환경 구성 재발 방지 계획

작성일: 2026-08-28

## 결론

최근 실패는 하나의 권한 문제가 아니었다. 브라우저 런타임 연결, 실행기 브리지, Cloudflare 로컬 registry 경로, 인증/fixture, 증거 시점이 서로 다른 계층인데도 하나의 캡처 단계로 묶어 진행한 것이 반복 실패의 공통 원인이다.

## 원인 분석

| 계층 | 확인된 원인 | 제품 결함 여부 | 재발 방지 |
|---|---|---|---|
| 브라우저 연결 | 현재 세션에 연결된 브라우저가 0개이고 브라우저 제어 surface도 노출되지 않음 | 제품 결함 아님 | 캡처 전 browser availability를 별도 판정하고 없으면 DOM/capture는 unknown 처리 |
| 개발 서버 | Cloudflare adapter의 Miniflare/Wrangler가 사용자 프로필의 xdg.config registry/log에 쓰기를 시도해 EPERM 발생 | 제품 결함 아님, 실행 설정 문제 | 프로젝트 내부 XDG_CONFIG_HOME/MINIFLARE_REGISTRY_PATH를 사용하는 dev:managed 명령 고정 |
| SSR 외부 조회 | 브라우저 Playwright 요청은 허용돼도 샌드박스에서 시작한 Wrangler 서버의 Supabase SSR 요청은 차단될 수 있음. 이 경우 클라이언트 목록은 보이는데 SSR 상세가 404처럼 보임 | 제품 결함으로 단정 금지, 서버 실행 권한 문제 가능 | 관리형 서버를 승인된 네트워크 권한으로 시작하고, 상세 URL HTTP 200을 브라우저 테스트 전에 별도 확인 |
| 명령 실행 | Windows sandbox 실행기에서 setup refresh 오류와 apply_patch helper 오류 발생 | 제품 결함 아님 | 작업 도구 실패와 앱 실패를 분리 기록. 수정은 검증된 파일 편집 경로와 check로 확인 |
| 인증/자동화 | env 누락, session 삭제, selector 불일치가 로그인 실패로 보일 수 있음 | 미판정 | secret 값은 출력하지 않고 key 존재·session·현재 URL·필드 count를 순서대로 확인 |
| 비교 증거 | stale capture, 다른 fixture, 다른 viewport를 섞으면 높이와 상태가 왜곡됨 | 제품 결함 아님 | 페이지·viewport·fixture·workflow별 evidence matrix를 만들고 unknown을 pass로 승격하지 않음 |

## 적용한 1차 조치

- tools/start_svelte_dev.ps1 추가: 프로젝트 내부 .runtime/ 경로를 만들고 Wrangler 환경 변수를 지정한다.
- svelte_app/package.json에 dev:managed 명령 추가.
- .runtime/를 gitignore에 추가해 registry/log가 작업 트리에 섞이지 않게 했다.
- Engineering Playbook의 브라우저 fallback 규칙을 현재 검증 정책에 맞게 수정했다.

## 단계별 실행 게이트

### Gate 0: 도구 표면

- 브라우저 런타임 availability를 먼저 확인한다.
- 브라우저가 없으면 서버·정적 코드 조사는 진행할 수 있지만 DOM/스크린샷 판정은 unknown으로 봉인한다.
- 실행기 또는 이미지 helper 오류는 제품 오류로 기록하지 않는다.

### Gate 1: 로컬 서버

- npm.cmd run dev:managed -- --Port 5174로 서버를 시작한다.
- npm.cmd run preflight:uiux로 Gate 0·1의 strict 검사를 실행한다. 브라우저 런타임이 UNKNOWN이면 종료 코드 2로 캡처를 차단한다.
- netstat -ano로 대상 포트가 하나인지 확인한다.
- /, /my, /notifications, /submit에 HTTP 요청해 200과 HTML body를 확인한다.
- 500이면 먼저 응답 본문의 runtime path/permission을 확인하고 UI 분석을 중단한다.
- SSR이 외부 Supabase를 호출하는 라우트는 브라우저 네트워크 허용만으로 충분하지 않다. 서버 프로세스 자체의 네트워크 권한을 확인하고, 대표 상세 URL의 HTTP status가 200인지 먼저 기록한다.

### Gate 2: 인증·fixture

- .env는 값이 아닌 필요한 key 존재만 검사한다.
- 테스트 시작 전 localStorage를 전체 삭제하지 않고 folio-submit-draft:*만 정리한다.
- artifacts/test.pbix 존재와 확장자를 확인한다.
- 로그인 후 current URL, session 존재, owner project id를 기록한다.

### Gate 3: 캡처·기능

- 동일 fixture로 원본/Svelte를 맞춘다.
- 각 페이지를 empty, populated, interactive, error/success, owner/non-owner, mobile 상태로 분리한다.
- selector count, overflow, screenshot, workflow state를 함께 저장한다.
- 자동화가 실패하면 selector/auth/session/fixture/server 순서로 원인을 분리한 뒤에만 제품 결함을 판정한다.

### Gate 4: 완료 판정

- 원본 코드·원본 캡처·Svelte 코드·Svelte DOM/캡처·check·필요 시 build가 모두 있어야 pass다.
- 브라우저 미연결, fixture 불일치, stale artifact는 unknown 또는 partial이다.
- 최종 문서에는 실행 시각, base URL, viewport, fixture, 상태, artifact 경로를 남긴다.

## 다음 실행 순서

1. 새 세션에서 브라우저 런타임 연결 여부를 Gate 0으로 확인한다.
2. npm.cmd run dev:managed로 서버를 시작하고 Gate 1을 통과시킨다.
3. 마이페이지·알림에 대해 동일 인증 fixture의 상태 캡처를 다시 만든다.
4. 팝오버 좌표, 프로필 저장, 삭제 취소/확정, 알림 자동 읽음과 프로젝트 이동을 기능 assertion으로 남긴다.
5. 수정·상세 페이지로 확장하고 페이지별 증거표를 갱신한다.
6. 마지막에 check/build과 evidence completeness 검사를 실행한다.

## 현재 남은 제약

- 브라우저 런타임은 이 세션에서 연결되지 않았다. 따라서 브라우저 기반 단계는 계획만 준비됐고 실제 pass 판정은 아직 아니다.
- dev:managed 서버 실행과 주요 SSR smoke는 확인했지만, 브라우저 캡처 연결은 별도 런타임이 필요하다.
- 2026-08-28 재현에서 일반 `dev`는 사용자 프로필 Wrangler 경로 EPERM으로 실패했고, `dev:managed`를 네트워크 허용 상태로 시작한 뒤 상세 URL이 404에서 200으로 회복됐다. 따라서 향후 상세 캡처는 `dev:managed` + 서버 네트워크 게이트를 함께 통과해야 한다.
- uiux_preflight.py가 package JSON, PBIX fixture, 테스트 key 존재, 서버 HTTP 200을 검사하도록 추가했으며 5177 테스트 서버에서 로컬 조건은 PASS, 브라우저 런타임은 UNKNOWN으로 확인했다.
- npm.cmd run check, npm.cmd run build, python -m py_compile tools\uiux_preflight.py를 다시 통과시켰다.

## 2026-08-28 브라우저 연결 재진단

브라우저 런타임 연결 실패를 저장소와 호스트 환경으로 나누어 재확인했다.

| 점검 항목 | 결과 | 해석 |
|---|---|---|
| Chrome 실행 파일 | 설치됨, 버전 확인됨 | 브라우저 바이너리 자체의 부재는 아님 |
| Browser Chrome 확장 | 대상 Chrome 프로필에서 `installed=false`, `enabled=false` | 브라우저 제어 확장 미설치 또는 미활성 |
| Native Messaging 호스트 | 예상 manifest 파일과 HKCU Chrome registry key가 모두 없음 | 확장과 Codex 런타임을 잇는 호스트 브리지 미설치/미등록 |
| Browser runtime discovery | `agent.browsers.list()` 결과 `[]` | 연결된 제어 대상 브라우저가 없음 |
| 프로세스 확인 | `tasklist`가 `Access denied` 반환 | 관리형 Windows 권한 제한. Chrome 부재의 근거로 사용하지 않음 |

따라서 이번 연결 실패의 직접 원인은 Svelte 앱의 인증값, PBIX fixture, dev server가 아니라 현재 Windows 사용자 프로필의 브라우저 통합 설치·등록 상태다. 저장소에서 Chrome 프로필이나 Windows registry를 임의로 수정해 해결할 수 있는 종류가 아니며, 현재 노출된 도구에도 Browser 확장/Native Host 설치기가 없다.

### 외부 복구가 필요한 작업

1. Codex/호스트 앱을 완전히 재시작하고 Browser 통합이 활성화된 새 세션을 연다.
2. 관리형 장비 정책으로 확장이 자동 배포되는 환경이면 Browser Chrome 확장과 Native Messaging 호스트를 같은 Windows 사용자 프로필에 재설치·등록한다.
3. 새 세션에서 `agent.browsers.list()`가 하나 이상의 브라우저를 반환하는지 확인한다.
4. 저장소에서 `npm.cmd run diagnose:browser`를 실행해 Chrome·확장·Native Host 상태를 확인한다.
5. 그 뒤 `npm.cmd run preflight:uiux`를 실행한다. `browser_runtime`이 UNKNOWN이면 캡처와 UIUX pass 판정을 시작하지 않는다.

현재 상태에서 Chrome을 직접 열거나 Selenium/Playwright로 우회하는 것은 이 Browser 런타임 연결을 복구한 것이 아니므로 검증 방법으로 채택하지 않는다.

### 확장 설치 후 재확인

사용자가 ChatGPT Desktop 앱을 설치하고 로그인한 뒤 현재 호스트 상태를 다시 점검했다.

- Chrome extension: `installed=true`, `enabled=true`, selected profile `Default`
- Native Host: `manifestPath` 파일은 생성됨, HKCU NativeMessagingHosts registry key는 없음
- Browser client bootstrap 재시도 후 `agent.browsers.list()` 결과: `[]`

따라서 확장 설치 자체는 완료됐고, 현재 남은 문제는 **Native Host registry 등록 또는 Desktop 브라우저 세션 초기화**다. 추가로 `Browser`/`Chrome`이라는 플러그인을 Plugin Directory에서 검색하는 단계는 필요하지 않다. 공식 설정 경로는 ChatGPT Desktop의 `Settings > Computer Use`이며, 해당 브라우저가 `Manage` 상태인지 확인한 뒤 새 Work/Codex 대화에서 `@Chrome` 또는 내장 브라우저를 선택해야 한다. Native Host manifest나 registry key를 저장소 스크립트로 직접 생성하지 않는다.

### Desktop 브라우저 오픈 후 VS Code 세션 재확인

사용자가 ChatGPT Desktop에서 브라우저를 열었지만, 현재 VS Code Codex 세션에서는 다음이 모두 실패했다.

- `agent.browsers.list()` 결과: `[]`
- `agent.browsers.get("iab")`: Browser unavailable
- `agent.browsers.get("chrome")`: Browser unavailable

따라서 Desktop에서 열린 브라우저와 현재 VS Code 작업 세션은 아직 같은 Browser 제어 surface로 연결되지 않았다. 이 상태에서는 VS Code 세션에서 브라우저 캡처를 완료했다고 말하지 않는다. Desktop의 `Settings > Computer Use`에서 `Manage` 상태를 확인하고 새 Desktop Codex 대화에서 브라우저를 선택해 작업을 이어가거나, VS Code에서는 기존 Selenium 캡처 경로를 별도 자동화용으로 사용해야 한다.

이후 사용자가 Desktop 설정과 새 `@Browser` 대화를 완료했다고 알렸지만, 현재 VS Code 작업 세션의 재확인 결과도 `agent.browsers.list() = []`였다. 따라서 이 세션에서 Desktop 브라우저를 인계받을 수 있다는 전제는 폐기한다.
