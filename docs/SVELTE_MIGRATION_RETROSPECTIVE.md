# Svelte Migration Retrospective

이 문서는 Streamlit 기반 FOLIO MVP를 SvelteKit으로 단계 이전하면서 얻은 교훈을 기록한다. 목적은 구현 기록을 자랑하는 것이 아니라, 다음 전환·배포·검증 작업에서 같은 판단을 더 빠르고 차분하게 반복하기 위한 것이다.

## 2026-08-24 중간 정리

### 현재 도달점

- Streamlit의 홈, 프로젝트 상세, Power BI 레퍼런스, Power BI 콘텐츠 허브 흐름을 SvelteKit 공개 화면으로 재구성했다.
- Supabase RPC와 테이블 계약을 먼저 정의하고, Svelte 화면은 그 계약에 맞춰 구현했다.
- 프로젝트 등록, 수정, 마이페이지, 알림, 좋아요, 댓글, 썸네일 업로드/캡처, PBIX 게시, SMTP 댓글 이메일 알림까지 Node SSR 서버 엔드포인트로 이전했다.
- `@sveltejs/adapter-node` 기반 빌드로 전환했고, `npm.cmd run verify` 한 번으로 check, build, Node route smoke, Supabase contract smoke, security smoke를 실행하게 만들었다.
- 원격 Supabase에는 thumbnail mode, home snapshot platform filter, project detail platform key 관련 patch를 적용했고 contract smoke로 확인했다.

### 가장 큰 판단

Svelte 전환은 화면을 예쁘게 다시 만드는 일이 아니라, Streamlit에 묶여 있던 제품 흐름을 데이터 계약과 서버 런타임 계약으로 분리하는 작업이었다.

처음부터 홈/상세/콘텐츠의 화면 우선순위와 Supabase RPC 응답 모양을 문서화한 것이 전환 속도를 올렸다. 반대로 데이터 계약이 조금이라도 흔들릴 때는 화면 코드를 고치는 것보다 RPC, env, 원격 SQL 적용 상태를 먼저 확인하는 편이 빨랐다.

## 교훈

### 1. 데이터 계약을 먼저 닫으면 프론트엔드 전환이 작아진다

홈과 상세는 `home_project_snapshot`, `project_detail_snapshot` 같은 snapshot RPC를 기준으로 옮겼다. 이 덕분에 Svelte 쪽은 Streamlit의 내부 query 조합을 복사하지 않고, 화면에 필요한 payload만 받아 렌더링할 수 있었다.

다음에도 프레임워크 전환을 할 때는 화면 컴포넌트보다 먼저 다음을 고정한다.

- route별 필요한 데이터
- nullable field
- enum 값
- 공개/비공개/삭제 visibility 규칙
- 정렬과 필터가 DB에서 처리되는지 클라이언트에서 처리되는지
- 기존 row와 신규 row 모두가 같은 타입으로 보이는지

### 2. SvelteKit 앱은 정적 프론트가 아니라 Node SSR 앱이다

FOLIO Svelte 앱은 단순 공개 조회 앱으로 시작했지만, 실제 범위는 PBIX 게시, 썸네일 업로드, 썸네일 캡처, SMTP 이메일, service role Supabase 작업을 포함한다. 이 기능들은 브라우저와 static hosting에 둘 수 없다.

따라서 SvelteKit 전환의 배포 단위는 `adapter-static`이 아니라 `@sveltejs/adapter-node`다. 배포 대상도 private env, 긴 요청, 파일 업로드, Chromium 실행 가능성을 기준으로 골라야 한다.

### 3. `.env` 호환은 작은 일이지만 전환을 막을 수 있다

기존 Streamlit 환경은 `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_ANON_KEY` 같은 legacy 이름을 사용했고, SvelteKit은 `PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_PUBLISHABLE_KEY`를 기대한다. 이 차이 때문에 앱 코드가 맞아도 smoke가 실패할 수 있었다.

전환기에는 새 env 이름만 강요하지 말고, 검증 스크립트가 legacy 이름을 읽어 현재 운영 환경과 새 앱 사이를 이어주게 하는 편이 안전하다. 단, 브라우저에 노출되는 값과 서버 전용 secret은 끝까지 분리해야 한다.

### 4. 원격 SQL 적용 상태는 코드 리뷰만으로 알 수 없다

로컬 스키마와 patch 파일이 맞아도 원격 Supabase가 예전 상태면 Svelte 앱은 실패한다. 특히 RPC 응답 필드, enum/check 제약, index, upsert 제약은 실제 원격 DB에서 확인해야 한다.

이번 전환에서는 사용자가 SQL patch를 적용한 뒤 `smoke:supabase`로 다음 계약을 확인했다.

- `projects.thumbnail_mode`가 `upload`를 포함하는지
- `home_project_snapshot`이 Power BI 기본 scope를 빠르게 반환하는지
- `project_detail_snapshot`이 `platform_key`와 `thumbnail_mode`를 반환하는지
- `powerbi_reports`가 `project_id` upsert 계약을 만족하는지

앞으로 DB patch가 있으면 문서에 “적용했다”만 남기지 말고, 원격 contract smoke를 완료 조건으로 둔다.

### 5. 검증은 명령 하나로 수렴시켜야 한다

개별 검증 명령이 많아질수록 마지막에 무엇을 실행했는지 흐려진다. 지금은 `npm.cmd run verify`가 다음을 한 번에 확인한다.

```powershell
npm.cmd run check
npm.cmd run build
npm.cmd run smoke
npm.cmd run smoke:supabase
npm.cmd run smoke:security
```

이 구조가 생긴 뒤부터 “현재 완료 상태인가?”라는 질문에 더 짧게 답할 수 있게 됐다. 다음 단계에서는 브라우저 E2E도 가능하면 같은 verify 계열로 묶는다.

### 6. 보안 smoke는 작아도 가치가 크다

이번 보안 smoke는 복잡한 인증 시나리오 전체를 테스트하지 않는다. 대신 실패 비용이 큰 경계를 빠르게 확인한다.

- private env 이름이 client source에 들어가지 않는지
- private env 값이 build client bundle에 들어가지 않는지
- thumbnail, thumbnail capture, PBIX publish, comment email endpoint가 익명 POST를 401로 거절하는지

이 정도만 있어도 “서버 전용 secret을 실수로 클라이언트에 넣는” 유형의 회귀를 초기에 잡을 수 있다.

### 7. SvelteKit CSRF 보호와 앱 인증 검증은 구분한다

FormData POST를 익명으로 보냈을 때 SvelteKit CSRF 보호가 라우트 코드보다 먼저 403을 반환했다. 이것은 보안상 나쁜 실패가 아니지만, 우리가 확인하려던 것은 endpoint 내부의 bearer token gate였다.

보안 smoke에서는 파일 업로드 본문을 보내지 않고 같은 origin POST로 인증 gate만 확인하게 바꿨다. 앞으로도 프레임워크 보호 계층과 앱 로직 보호 계층을 구분해서 테스트한다.

### 8. Windows PowerShell은 문서/JSON 편집에서 함정이 있다

PowerShell `Set-Content -Encoding utf8`은 환경에 따라 BOM을 붙일 수 있고, JSON 파일에 BOM이 붙으면 Vite가 `package.json`을 읽지 못한다. Markdown 안의 backtick도 문자열 치환 중 escape로 해석되어 문서가 깨질 수 있었다.

교훈은 단순하다.

- JSON은 BOM 없는 UTF-8로 저장한다.
- Markdown의 backtick이 들어간 치환은 줄 단위로 처리한다.
- 문서 수정 후 `git diff --check`를 본다.
- `package.json`을 건드린 뒤에는 바로 `npm.cmd run build`나 `npm.cmd run check`로 읽기 오류를 잡는다.

### 9. 자동화가 닫는 범위와 사람이 눌러야 하는 범위를 분리한다

현재 자동 검증은 빌드, 공개 route, Supabase contract, basic security를 닫는다. 하지만 다음은 실제 브라우저와 실제 계정이 필요하다.

- 회원가입, 로그인, 비밀번호 재설정
- 온보딩 정책 동의
- 프로젝트 등록/수정/삭제
- 썸네일 업로드와 Storage public URL 확인
- Playwright/Chromium 기반 썸네일 캡처
- PBIX 실제 import와 Power BI embed token
- SMTP 실제 발송
- 댓글, 답글, 알림 읽음 처리

자동 smoke가 통과했다고 운영 준비가 끝난 것은 아니다. 자동화된 gate와 staging manual QA를 구분해서 보고해야 한다.

### 10. Streamlit 대비 Svelte 코드량 증가는 자연스럽다

Streamlit은 화면 선언, 서버 상태, 렌더링, 사용자 이벤트를 한 Python 런타임 안에서 처리한다. SvelteKit은 route, load, component, client action, server endpoint, shared type, validation, smoke script가 분리된다.

그래서 같은 기능을 옮기면 파일과 코드량은 늘어난다. 대신 얻는 것은 다음이다.

- 화면 구조와 서버 secret 경계가 더 명확하다.
- 공개 route와 mutation endpoint를 독립적으로 검증할 수 있다.
- 브라우저 상호작용과 SSR 데이터를 분리해 유지보수할 수 있다.
- 배포 전 smoke와 security gate를 자동화하기 쉽다.

코드량 증가는 실패가 아니라 경계가 명시화된 비용이다. 다만 UI 컴포넌트 중복이 늘어날 때는 공통화 기준을 다시 봐야 한다.

### 11. 라우트 구현과 메뉴 노출은 별개로 검증한다

이번 UI parity 점검에서 Svelte에는 회원가입 메뉴, 독립 레퍼런스 메뉴, 홈 카드 상단 플랫폼 뱃지처럼 원본 Streamlit 헤더/카드에는 없던 요소가 남아 있었다. 반대로 프로젝트 등록 메뉴와 알림 `N` 배지처럼 원본에 보이던 요소는 노출 조건이 달라져 있었다.

원인은 기능 단위로 route와 컴포넌트 존재 여부를 확인하면서, 원본 캡처의 헤더 노출 조건과 카드 내부 정보 밀도를 별도 계약으로 닫지 않은 것이다. 앞으로 parity 작업은 다음을 분리해서 확인한다.

- route가 존재하는지
- 메뉴에 노출되는지
- 비로그인/로그인 상태별 노출 조건이 원본과 같은지
- 홈 필터/태그처럼 RPC 응답과 클라이언트 fallback이 같은 제외 규칙을 쓰는지
- 카드 위계에서 원본에 없던 badge, eyebrow, metadata가 추가되지 않았는지

### 12. 작은 UI 수정은 먼저 selector 계약을 닫고 편집한다

이번 nav font/underline/card footer 같은 작은 수정이 예상보다 오래 걸렸다. 원인은 구현 난이도보다 작업 순서와 편집 환경에 있었다.

- `app.css`가 이미 큰 누적 diff를 가진 상태라 전체 diff가 노이즈가 컸고, 이번 변경만 빠르게 읽기 어려웠다.
- `apply_patch`가 Windows sandbox helper 오류로 실패해 PowerShell 문자열 치환으로 우회했다.
- PowerShell here-string, quote, LF/CRLF 차이 때문에 첫 치환 패턴이 빗나갔다.
- 처음부터 정확한 selector와 DOM 블록을 짧게 캡처한 뒤 바꾸지 않아, “수정 -> 확인 -> 재수정” 루프가 늘어났다.
- nav에는 `a`와 `button`이 섞여 있었는데, 처음에는 hover underline을 `a` 중심으로 생각해 button parity를 마지막에 다시 잡았다.

다음부터 사소한 UI 수정은 바로 코드를 쓰기 전에 3분 안에 아래 계약을 닫는다.

1. 바꿀 DOM 블록 1개와 CSS selector 1개를 짧게 확인한다.
2. link/button처럼 같은 시각 역할을 하는 요소 타입을 모두 열거한다.
3. LF/CRLF가 섞인 파일은 here-string 치환보다 좁은 수동 편집 또는 AST/formatter 친화적 변경을 우선한다.
4. 전체 diff 대신 `rg`와 작은 `Get-Content -Skip/-First`로 변경 범위만 검증한다.
5. 마지막에는 `npm.cmd run check`와 해당 파일 `git diff --check`만 우선 돌리고, 빌드는 범위가 커질 때 추가한다.

## 다음 작업자를 위한 체크리스트

1. 새 Svelte 화면을 만들기 전에 route별 데이터 계약을 먼저 문서화한다.
2. Supabase schema나 RPC를 바꾸면 원격 patch 적용과 `npm.cmd run smoke:supabase`를 완료 조건에 넣는다.
3. 서버 secret을 쓰는 기능이면 `adapter-node` 런타임과 private env availability를 먼저 확인한다.
4. `.env` 이름이 Streamlit legacy와 Svelte public/private 규칙 사이에서 맞는지 확인한다.
5. `npm.cmd run verify`를 마지막 gate로 사용한다.
6. 인증·업로드·PBIX·SMTP·캡처는 자동 smoke와 별개로 실제 계정 staging QA를 남긴다.
7. Windows에서 JSON/Markdown을 편집하면 BOM, backtick, CRLF 경고를 확인한다.
8. UI parity에서는 route 존재, 메뉴 노출, 인증 상태별 노출 조건, 카드 metadata 밀도를 각각 원본 캡처와 대조한다.
9. 작은 UI 수정은 DOM/selector/요소 타입 계약을 먼저 닫고, 큰 누적 diff 대신 변경 범위만 짧게 검증한다.

## 남은 리스크

- 실제 Power BI workspace 권한, PBIX import 시간, embed token 발급은 운영 tenant에서만 완전히 검증된다.
- 썸네일 캡처는 Playwright/Chromium 설치와 host sandbox 정책에 영향을 받는다.
- SMTP는 provider별 TLS/Auth 정책이 달라 staging에서 실제 발송 확인이 필요하다.
- Auth recovery callback은 Supabase URL configuration과 배포 도메인 설정까지 맞아야 한다.
- Streamlit과 Svelte가 한동안 공존하면 env, Supabase policy, 문서가 둘 중 하나 기준으로 drift될 수 있다.

## 기록 원칙

이 문서는 완료 보고서가 아니라 전환 중간 회고다. 실제 배포 또는 staging QA가 끝나면 아래 항목을 추가한다.

- 배포 플랫폼과 선택 이유
- staging QA 결과
- 실제 장애 또는 no-go 항목
- Streamlit에서 Svelte로 traffic을 넘기는 기준
- 남겨둘 Streamlit fallback 범위

## 원본 클로닝 회고: 파악 순서

이번 전환에서 가장 큰 교훈은 “코드베이스 전수 조사”와 “원본 UI 클로닝 조사”가 다르다는 점이다. 코드와 문서만 보면 route, 데이터, 컴포넌트는 파악할 수 있지만, 사용자가 보는 원본의 기본 상태와 상호작용 상태는 놓치기 쉽다.

다음 작업자는 원본 클로닝을 할 때 이 순서를 따른다.

1. 원본 Streamlit과 Svelte를 동시에 localhost로 띄운다.
2. 같은 viewport, 같은 인증 상태, 같은 query param으로 캡처한다.
3. screenshot만 보지 말고 DOM 수치를 저장한다. 최소 `x/y/w/h`, card count, row height, tab count, link count, scrollHeight를 남긴다.
4. closed/open/hover/click/pagination 상태를 각각 따로 캡처한다.
5. 원본에 없던 메뉴, badge, label, helper text가 Svelte에 추가되지 않았는지 확인한다.
6. 원본에 있던 CTA, 알림 badge, 프로젝트 등록, 영상 카드, 한글 요약, footer label이 빠지지 않았는지 확인한다.
7. 원본과 의도적으로 다르게 가는 부분은 “미완료”가 아니라 “제품 결정”으로 문서에 남긴다.
8. 마지막에 `npm.cmd run check`, `git diff --check`, screenshot/contact sheet/report artifact를 함께 남긴다.

특히 Streamlit의 `st.tabs`, `st.expander`, popover, custom HTML은 Svelte의 단순 card/list로 바꾸는 순간 정보 밀도와 사용 감각이 크게 달라진다. Power BI 업데이트 화면에서 접힌 row와 YouTube 영상 card를 늦게 잡은 것이 대표 사례다. 앞으로는 기능 구현보다 먼저 기본 UI 상태 계약을 정의한다.