# FOLIO 프로젝트 컨텍스트

새 대화에서 작업을 이어갈 때 이 문서를 먼저 읽어라.
코드와 문서가 다르면 코드베이스를 확인한 뒤 이 문서를 고쳐라.
민감 정보(API 키, 비밀번호 등)는 이 문서에 기록하지 않는다.

---

## 프로젝트 개요

**FOLIO** — 데이터 분석 프로젝트를 포트폴리오 자산으로 등록·탐색·공유하는 MVP.
핵심 메시지: "발표로 끝나지 않는 프로젝트 / AI 시대에는 휴먼 인사이트가 자산이다."

- **스택**: Streamlit + Supabase (PostgreSQL + Auth)
- **실행**: `streamlit run app.py` → `http://localhost:8501`
- **엔트리**: 루트 `app.py` → `folio_app/app.py:main()`

---

## 파일 구조 (핵심만)

```
folio_app/
  app.py                  # 진입점. 쿠키 복구, 라우팅, 온보딩 체크
  styles/                 # 전역 CSS 주입 (apply_global_styles), 화면 영역별로 모듈 분리
  config.py               # 환경변수 로드 (get_settings)
  navigation.py           # 내부 이동 공통 헬퍼와 허용 라우트
  components/
    layout.py             # render_header(), render_hero()
    ui.py                 # clean_html(), 공통 UI 헬퍼
    project_form.py       # 프로젝트 등록/수정 폼
  pages/
    home.py               # 홈 + 탐색 허브 + 상세 뷰
    project_detail.py     # 상세 렌더링 (home에서 project_id 쿼리로 호출)
    auth.py               # render_login(), render_signup()
    gallery.py            # 레거시 → Home으로 리다이렉트
    protected.py          # render_submit(), render_my_page() (프로필+포트폴리오 통합). render_my_portfolio()/render_profile()은 My Page로 리다이렉트만 하는 레거시 라우트 핸들러
    onboarding.py         # 약관 동의 온보딩
  services/
    auth.py               # get_current_user(), sign_in/out, restore_session()
    profiles.py           # get_profile(), update_profile(), get_onboarding_status()
    projects.py           # CRUD + 좋아요 + 통계
    project_drafts.py     # 사용자·작업별 세션 초안 저장·복구·삭제
    project_content.py    # 프로젝트 본문 HTML 허용 목록 정제
    supabase_client.py    # Streamlit 세션별 Supabase client
  static/
    hero-preview.png      # 홈 히어로 우측 미리보기 이미지
```

---

## 구현 완료 기능

| 기능 | 파일 | 비고 |
|------|------|------|
| 회원가입 / 이메일 인증 | `auth.py` | Supabase Auth |
| 로그인 / 로그아웃 | `auth.py`, `app.py` | EncryptedCookieManager로 세션 유지 |
| 온보딩 (약관 동의) | `onboarding.py`, `profiles.py` | 첫 로그인 후 강제 진입 |
| 프로필 조회 / 수정 | `protected.py` | 이름, 소속, 자기소개 |
| 프로젝트 등록 / 수정 / 삭제 | `protected.py`, `project_form.py` | |
| 홈 탐색 (검색, 태그, 정렬) | `home.py` | Gallery 페이지 없음, Home이 탐색 허브 |
| 프로젝트 상세 | `project_detail.py` | `?project_id=` 쿼리로 Home 안에서 렌더링 |
| 좋아요 | `projects.py`, `project_detail.py` | 비로그인 → Login으로 이동 |
| 푸터 | `app.py` | Copyright © 2026 Snowball Impact |

---

## 라우팅 구조

`st.query_params["page"]` 값으로 화면 전환. 모든 페이지 이동은 `st.rerun()`.

| page 값 | 화면 | 비고 |
|---------|------|------|
| Home (기본) | 홈 + 탐색 허브 | `?project_id=` 있으면 상세 |
| Login | 로그인 | |
| Sign Up | 회원가입 | nav에 노출 안 됨, 링크로만 접근 |
| Submit | 프로젝트 등록 | 로그인 필요 |
| My Page | 프로필 + 내 포트폴리오 통합 | 로그인 필요 |
| My Portfolio | 레거시 | My Page로 리다이렉트 |
| Profile | 레거시 | My Page로 리다이렉트 |
| Gallery | 레거시 | Home으로 리다이렉트 |

---

## 네비게이션 구조 (중요)

**인증 상태나 데이터를 변경하는 동작에는 HTML `<a href>` 링크를 사용하지 않는다.**

이유: HTML 링크 클릭 → 브라우저 전체 리로드 → WebSocket 끊김 → `session_state` 초기화 → `get_current_user() = None` → 로그인 상태 소실.

**현재 구현**: `navigation.py`의 `navigate()`가 `st.query_params` + `st.rerun()` 패턴을 통합한다. 공개 프로젝트 카드 전체 클릭은 탐색 UX를 위해 HTML 링크를 허용한다.

```python
# 비로그인 nav: 홈, 로그인
# 로그인 nav:   홈, 프로젝트 제출, 마이 페이지, 로그아웃
```

헤더는 `st.container(key="folio_header")`와 `.st-key-folio_header` 선택자로 스코프 지정.

---

## CSS 아키텍처

### 파일 구조: 화면 영역별 모듈 분리 (2026-07-06 리팩토링)

`folio_app/styles.py` 단일 파일(2400줄+)이 계속 커지면서 죽은 선택자·중복 선언이 쌓였다. `folio_app/styles/` 패키지로 분리했다:

```
folio_app/styles/
  __init__.py          # apply_global_styles() -- 아래 모듈들의 CSS를 정해진 순서로 이어붙여 st.html() 1회 호출
  tokens.py            # :root 토큰, 전역 리셋(stApp/사이드바 숨김/CookieManager iframe 숨김/block-container), 푸터
  header.py            # 상단 헤더(브랜드, nav 버튼, 로그인 버튼, 메뉴 팝오버)
  hero.py              # 홈 히어로 + 서브페이지 공용 히어로(render_hero) + 히어로 푸터 액션 + 다크 히어로
  buttons_inputs.py     # 전역 버튼/입력 필드 스타일
  browse_panel.py       # 홈 탐색(검색/태그/정렬) 패널
  cards.py              # 홈 프로젝트 카드 그리드 + 자동 커버 아트
  shared.py             # folio-tags/folio-tag/folio-detail-meta/folio-muted (카드·히어로·상세 공용)
  auth.py               # 로그인/회원가입 카드
  onboarding.py         # 온보딩(약관 동의) 카드
  project_form.py        # 프로젝트 등록/수정 폼 + 공개 설정 토글
  portfolio.py           # 내 포트폴리오 카드
  detail_page.py         # 프로젝트 상세 페이지(메타 행, 본문 섹션, 대시보드/첨부 사이드바)
  profile.py             # 프로필 페이지
```

각 모듈은 `<style>` 태그 없이 순수 CSS 텍스트를 담은 `CSS` 상수만 노출한다. `__init__.py`가 고정된 순서로 이어붙여 기존과 동일하게 `st.html()`을 1회만 호출한다 (스타일 전용 콘텐츠가 이벤트 컨테이너에 배치되어 인증 rerun 중에도 CSS가 유지되는 특성은 그대로 유지됨).

**분리 시 검증 방법**: 선택자+선언을 정규화해 분리 전/후 CSS를 구조적으로 비교하는 스크립트로 전체 선택자 집합과 선언 내용이 1:1로 동일함을 확인했다(의도적으로 제거한 죽은 선택자 제외). 이 방법은 이후 CSS 파일을 다시 재구성할 때도 재사용 가능하다.

**새 섹션을 추가할 때**: 어느 화면에 속하는지 위 표에서 가장 가까운 모듈을 찾아 그 모듈의 `CSS` 상수에 추가한다. 새 화면 영역이면 새 모듈을 만들고 `__init__.py`의 `_SECTIONS` 튜플에 등록한다 (등록 순서 = 최종 CSS 내 등장 순서 = 동일 선택자·동일 명시도 충돌 시 타이브레이크 순서이므로, 특정 선택자를 다른 모듈의 규칙보다 나중에 덮어써야 한다면 순서에 유의).

### 핵심 패턴: key 기반 스코프

`st.container(key="...")`가 생성하는 `.st-key-*` 클래스로 컨테이너를 직접 타겟팅한다. 상위 래퍼까지 매칭하는 광범위한 `:has()`는 피한다.

```python
# 코드
with st.container(border=False, key="folio_header"):
    ...

# CSS
.st-key-folio_header {
    background: #08142b;
    ...
}
```

### 현재 컨테이너 key

| key | 용도 |
|------------|------|
| `folio_header` | 헤더 컨테이너 |
| `folio_browse_panel` | 홈 탐색 패널 |
| `folio_auth_shell` | 인증 카드 전체 |
| `folio_auth_form` | 인증 폼 카드 |
| `folio_onboarding_card` | 온보딩 카드 |

### 주의사항

- `stVerticalBlockBorderWrapper` 전역 스타일은 모든 `border=True` 컨테이너에 적용되므로 직접 수정하지 않는다.
- `.stButton>button` 전역 규칙은 `buttons_inputs.py`에 1개만 유지 (중복 시 충돌).
- 헤더 내 nav 버튼은 `.st-key-folio_header .stButton > button`으로 별도 오버라이드.
- 사용하지 않는 컴포넌트 선택자는 기능 변경 직후 제거하고, 중복 선언은 한 섹션에만 유지한다. (2026-07-06 리팩토링에서 이 원칙을 어긴 죽은 CSS ~450줄과 그 CSS만을 위해 남아있던 미사용 Python 함수 3개를 정리했다 — 아래 "최근 작업 요약" 참고.)
- 새 CSS 선택자를 추가하기 전에 그 클래스/키가 실제로 어떤 `.py` 파일에서 렌더링되는지 먼저 확인한다. 렌더링 코드가 바뀌거나 삭제됐는데 CSS만 남으면 이번처럼 다음 정리 때까지 죽은 채로 쌓인다.

---

## Streamlit CSS 한계 (학습)

헤더/네비처럼 항상 보이는 요소는 `position:absolute` + `top:50%`/`margin:auto` 수동 중앙정렬 대신 **flex/grid 네이티브 정렬(`align-items`, `justify-content`)을 먼저 시도**한다 (`min-height`만 있는 컨테이너는 `top:50%`가 조용히 static position으로 대체되어 로그인 전/후 마크업 차이에 따라 위치가 흔들렸던 사례). 현재 헤더는 이 원칙에 따라 `display:flex; flex-direction:row; align-items:center; justify-content:space-between;`로 구성되어 있다(`folio_app/styles/header.py`).

---

## 세션 / 인증 구조

```
앱 로드
  └─ EncryptedCookieManager.ready() 대기
      └─ 쿠키에서 access_token / refresh_token 복구 시도
          └─ restore_session() → Supabase
              └─ 성공: session_state에 user 저장 → st.rerun()
              └─ 실패: 쿠키 삭제
                  ├─ 공개 페이지: 비로그인 상태로 조용히 계속
                  └─ 보호 페이지: Login으로 이동해 안내 표시
```

- `get_current_user()`: `session_state["folio_user"]` 반환. 없으면 None.
- 로그아웃: `?logout=1` 쿼리 → `sign_out()` → 쿠키 삭제 → 홈 이동.
- Supabase client는 `st.cache_resource` 전역 공유가 아니라 Streamlit 세션별로 생성해 Auth 상태가 사용자 간 섞이지 않게 한다.
- 로그아웃 시 토큰과 함께 세션의 Supabase client도 폐기한다.
- 프로필 복구는 기존 프로필을 덮어쓰지 않고, 누락됐을 때만 생성한다.
- 약관·동의 조회가 실패하면 서비스를 우회시키지 않고 재시도 화면을 표시한다.

---

## Supabase 스키마 (핵심 테이블)

```sql
profiles       (id, email, name, organization, bio, created_at)
projects       (id, author_id, title, one_liner, tags[], is_public, view_count, ...)
likes          (user_id, project_id, created_at)
policy_versions (id, policy_type, version, is_active, content, effective_at)
user_policy_consents (user_id, policy_version_id, consented_at)
```

- `projects.category` 컬럼은 DB에서 제거됨 (코드에도 없음).
- 좋아요 수는 `projects` 컬럼이 아니라 `likes` 테이블에서 계산함.
- RLS 활성화 상태. anon 클라이언트로 공개 프로젝트만 읽기 가능.
- 인증 사용자는 공개 여부와 관계없이 본인이 작성한 프로젝트를 읽을 수 있다. 원격 DB에는 최신 `schema.sql` 재적용이 필요하다.

### 공개 탐색 조회

- 공개 프로젝트는 500건 단위로 전체 페이지 조회하며 원본 결과를 30초 캐시한다.
- 인기 태그는 별도 DB 요청 없이 같은 공개 프로젝트 캐시에서 계산한다.
- 공개 프로필은 60초, 프로젝트별 좋아요 수는 15초 캐시한다.
- 프로젝트 CRUD, 조회수 증가, 좋아요 변경 시 관련 캐시를 즉시 무효화한다.

### 프로젝트 작성 UX

- 기본 정보와 Home 카드 미리보기를 하나의 카드에 2열로 배치하며, 미리보기는 항상 표시하고 입력에 맞춰 갱신한다.
- 모바일에서는 기본 정보·카드 미리보기와 관련 링크 3열을 각각 1열로 전환한다.
- 프로젝트 본문 편집기 아래에 접을 수 있는 본문 미리보기를 제공한다.
- Quill이 섹션 제목에 HTML 속성을 추가해도 문제 정의·사용 데이터·분석 과정·핵심 인사이트를 분리한다.
- 선택 URL은 입력 위치에서 즉시 형식을 검증하고 제출 시 다시 최종 검증한다.
- 등록·수정·삭제 완료 메시지는 `session_state`에 임시 보관해 rerun 뒤에도 표시한다.

### 상세·포트폴리오 UX

- 상세 화면은 첨부 자료가 있으면 2열, 없으면 본문 전체 폭 1열로 렌더링한다.
- 상세 좋아요와 목록 복귀는 HTML 링크가 아닌 Streamlit 버튼을 사용한다.
- My Page는 프로필·통계와 내 프로젝트 관리 목록을 한 화면에 표시한다.
- 프로젝트 정보와 보기·수정·삭제 액션을 하나의 `border=True` 컨테이너로 묶고, 모바일에서는 액션을 카드 하단 가로 3열로 배치한다.

### 테스트 범위

- `python -m unittest discover -s tests -v`
- 라우팅, 인증 클라이언트 격리, 온보딩 오류 처리, 프로필 보존
- 프로젝트 HTML 정제, 본문 섹션 파싱, URL 정규화, 태그·검색 필터
- 실제 로그인, 프로젝트 CRUD, 공개→비공개 전환, 작성자 비공개 열람, 좋아요와 조회수는 테스트 계정으로 브라우저 검증을 완료했다. 상세 결과는 `docs/INTEGRATION_VALIDATION.md`를 참고한다.
- 신규 회원가입·이메일 인증·최초 온보딩과 서로 다른 두 계정 간 권한 격리는 아직 검증하지 않았다.

---

## 작업 원칙

- 단순 CSS/문구 변경은 검증 생략.
- Python 구조 변경은 관련 파일만 Read 후 수정.
- Streamlit 전역 CSS 오염 주의 — 컨테이너 key 기반 스코프 우선.
- 인증 및 상태 변경 동작은 `navigate()`와 Streamlit 버튼 사용. 공개 카드 링크만 예외.
- 한글 문구: `word-break: keep-all` + 적절한 `max-width`.
- 카드 HTML을 `st.markdown()`으로 렌더링 시 들여쓰기 주의 (`clean_html()` 활용).
- 사용자 프로젝트 본문은 저장 시와 표시 시 `sanitize_project_html()`로 정제.
- 셀레니움 동적 테스트나 스크린샷 검증은 **수정사항이 크리티컬하거나 원인 파악이 어려울 때만** 한다. 원인이 명확한 단순 CSS/문구 변경은 `py_compile` + 유닛 테스트로 끝내고 브라우저 검증은 생략한다. 확인이 필요할 때도 캡처 후 `artifacts/` 임시 이미지는 정리한다.
- 같은 증상(예: 정렬/위치가 자꾸 미세하게 어긋남)이 서로 다른 수정으로 세 번 이상 재발하면, 패치를 더 쌓지 말고 **접근 방식 자체를 재검토(리팩토링)**하는 걸 먼저 고려한다. 헤더를 `position:absolute` 트릭으로 여러 번 고치다 계속 재발한 뒤 flex-row로 다시 짜서 근본 해결한 사례 참고 ("Streamlit CSS 한계" 섹션).
- 버그를 추론할 때는 앱 코드뿐 아니라 **Streamlit 프레임워크 자체의 알려진 동작/한계**도 항상 초기 가설에 넣는다 (`st.columns()`의 내부 ResizeObserver, 위젯 버전별 API 변경, 서드파티 컴포넌트 iframe 타이밍 등).
- 로그인 등 실제 인증 세션이 있어야 확인되는 UI는, 계정이 없어도 `get_current_user()`를 몽키패치해서 두 상태를 나란히 렌더링·비교할 수 있다 → `tools/probe_header_auth_states.py` 참고.
- 캡처 스크립트: `tools/capture_streamlit_scroll.py` (의존: selenium, Pillow → `requirements-dev.txt`).
- 페이지 전환 CLS 측정 스크립트: `tools/measure_transition_cls.py` (Selenium, `scrollTop`/`scrollHeight`/헤더·히어로 좌표를 시간대별로 기록).
- 인증 상태별 UI 비교 스크립트: `tools/probe_header_auth_states.py` (`get_current_user()` 몽키패치로 로그인 세션 없이 logged_in/logged_out 헤더를 나란히 렌더링).

### 작업 실행 프로토콜 (진단 → 수정 → 검증)

과거 세션에서 같은 요청을 여러 번 반복 수정한 원인은 구현 난이도보다 진단 순서가 늦었던 데 있었다. 아래를 기본 흐름으로 쓴다.

1. **완료 조건을 수정 전에 구체화한다.** "정렬을 맞춰라" → `left/right` 좌표 일치, "크기를 통일" → `width/height` 일치, "상태 변경" → 입력 상태·DB 결과·rerun 후 화면 상태를 각각 정의. 모호한 "비슷하게"를 CSS 값 추정으로 반복 보정하지 않는다.
2. **1차 수정이 화면과 다르면 즉시 실측한다.** UI는 Selenium `execute_script()`로 대상·조상 래퍼의 좌표/computed style을 확인한다 (`stColumn`이 실제 컬럼 testid, `st.button()`은 `stElementContainer → stButton → stTooltipHoverTarget → button` 구조일 수 있음에 유의). 인증은 `session_state` / Supabase Auth 세션 / PostgREST JWT를 분리해서 확인한다. 캡처 이미지만 보고 2~4px씩 누적 보정하지 않는다.
3. **관련 변경을 한 번의 응집된 패치로 처리한다.** 함수 시그니처를 바꾸면 모든 호출부·반환 데이터·테스트를 같은 차례에 검색한다. UI 요소를 이동하면 기존 로직과 죽은 CSS도 함께 제거한다.
4. **검증은 위험도에 맞게 계층화한다.** CSS 한 줄은 문법 확인, Python 흐름은 관련 테스트 + `py_compile`, 공통 서비스/인증/DB payload는 회귀 테스트 후 전체 테스트 1회. 동일한 전체 테스트·전체 캡처를 작은 수정마다 반복하지 않는다. PC 1440×900 / 모바일 390×844를 기본 검증 크기로 쓰고, 임시 캡처는 `artifacts/`에서 삭제한다.
5. **외부 적용이 필요한 순간을 일찍 알린다.** RLS/스키마/배포 설정처럼 로컬 코드만으로 끝나지 않는 작업은 즉시 구분하고, 실행 가능한 SQL/절차를 제공하되 원격 적용 전에는 "완료"라고 하지 않는다.
6. **작업 종료 시 다음 세션 진입 비용을 없앤다.** 현재 상태·남은 문제·완료 기준을 이 문서에 짧게 갱신한다.

**피해야 할 패턴**: DOM 확인 없이 padding 반복 조정 · Streamlit 내부 래퍼를 추측한 선택자 사용 · 오류 문구만 보고 인증 실패로 단정 · 함수 인자 하나만 고치고 다른 호출부 미확인 · 외부 DB 정책 미적용을 앱 코드로 우회 · 매 단계 대형 파일/전체 diff 반복 출력.

### 로그인 전환 시 레이아웃 플래시 방지

- 전역 CSS는 `st.markdown()`이 아니라 `apply_global_styles()`의 스타일 전용 `st.html()`로 주입한다 (`st.markdown()`은 rerun 시 본문 DOM과 함께 교체되어 스타일이 잠깐 빠질 수 있음). style-only 콘텐츠는 메인 레이아웃이 아닌 이벤트 컨테이너에 배치되어 인증 rerun 중에도 CSS가 안정적으로 유지된다.
- CookieManager 동기화 iframe은 전역 CSS에서 계속 숨긴다. 인증 전환 중 이 iframe이 노출되면 레이아웃이 튀는 것처럼 보일 수 있다.

### 상세 페이지 현재 레이아웃 기준

- 히어로 본문과 푸터 콘텐츠의 실제 좌우 좌표가 일치해야 한다.
- 푸터는 `작성자 / 소속 / 등록일`과 `조회수 / 공개 상태`를 하나의 정보 스트립으로 묶는다.
- 좋아요만 작은 pill 형태의 Streamlit 액션 버튼으로 유지한다.
- 상세 푸터의 공개 상태는 읽기 전용이다. 공개 여부 변경은 `마이 페이지 → 수정 → 프로젝트 공개`에서 저장한다.
- 본문은 `프로젝트 리포트` 카드 하나에 문제 정의·사용 데이터·분석 과정·핵심 인사이트를 구분선으로 연결한다.
- 수정 화면의 공개 설정 카드는 폼 최하단 좌측에 두고 취소/저장 액션은 우측에 둔다.
- `홈 갤러리로 돌아가기`는 프로젝트 비주얼 카드 하단에 둔다. 비주얼 카드가 없으면 본문 하단에 둔다.
- 프로젝트 비주얼은 `대시보드`와 `첨부 자료` 사이에만 구분선을 둔다.
- 대시보드 iframe과 링크 버튼은 프로젝트 비주얼 카드 안에서 `max-width: 100%`를 유지한다.

### 인증/RLS 작업 교훈

- `session_state`에 사용자가 있다고 해서 PostgREST 요청도 인증된 것은 아니다.
- 작성자 전용 mutation 전에 `ensure_authenticated_session()`으로 세션을 갱신하고 갱신된 access token을 `client.postgrest.auth()`에 명시적으로 적용한다.
- 프로젝트 UPDATE는 `return=representation`을 사용하지 않는다. 공개→비공개 변경 직후 변경 행을 다시 SELECT해 반환하면 원격 RLS 정책과 충돌할 수 있으므로 `return=minimal`과 영향 행 count로 성공을 판정한다.
- 인증 재동기화 후에도 42501이 발생하면 로그인 오류로 오진하지 않는다. 원격 DB에 `Users can read own projects`와 `Users can update own projects` 정책이 누락된 것이므로 `supabase/fix_project_owner_rls.sql`을 SQL Editor에서 적용한다.
- 비로그인 또는 유령 세션에서 mutation을 보내 RLS 원문 오류를 노출하지 않는다. 세션을 정리하고 Login으로 이동시킨다.
- RLS 관련 변경은 단위 테스트만으로 완료로 판단하지 않고 실제 테스트 계정으로 공개↔비공개 전환을 확인한다.

---

## 최근 작업 요약

### CSS 리팩토링 (2026-07-06)

`folio_app/styles.py`(2405줄) 전체를 감사해 스타일 중심으로 정리했다. 요청 계기: 파일이 계속 커지며 중복·죽은 CSS가 쌓였다.

- **버그 수정**: `/* ── Profile ──` 주석이 닫는 `*/` 없이 이어지다 우연히 `/* ── Generic card ── */`(같은 줄에 열고 닫음)에서 닫히는 바람에, 프로필 페이지가 실제로 쓰는 `.folio-profile-header`/`.folio-avatar`/`.folio-profile-info-name`/`.folio-profile-info-org`/`.folio-profile-bio`/`.st-key-profile_overview`/`st.metric` 스타일 전체가 통째로 죽어 있었다(프로필 페이지가 무스타일로 렌더링됨). 주석을 닫아 복구.
- **죽은 CSS ~450줄 제거**: 렌더링 코드가 없거나(레거시 히어로/갤러리 카드, 미사용 백링크·첨부링크 클래스), 렌더링 함수 자체가 어디서도 호출되지 않거나(`render_portfolio_card_html`, `render_gallery_card_html`, `render_placeholder_card`), 클래스명이 실제 마크업과 어긋난(`folio-visibility-pill` vs 실제 `folio-detail-visibility-stat`, `folio-detail-visibility` vs 실제 클래스 없음) 선택자들을 확인 후 제거. 검증은 각 클래스/키를 `grep`으로 모든 `.py` 파일과 대조해 실제 호출부가 있는지 하나씩 확인하는 방식으로 진행했다.
- **중복 선언 통합**: 좋아요 버튼(`st-key-detail_like_action`) 스타일이 서로 다른 3곳(구 상세 히어로, 히어로 푸터 액션, "Like button styling" 섹션)에 흩어져 있었다 — `detail_like_action`은 항상 `folio_hero_footer_actions` 안에서만 렌더링되므로, 실제 캐스케이드 결과(어느 선언이 specificity로 이겼는지)를 계산해 하나의 규칙으로 합쳤다.
- **파일 분리**: `folio_app/styles.py` → `folio_app/styles/` 패키지(화면 영역별 14개 모듈). 자세한 구조는 위 "CSS 아키텍처 → 파일 구조" 참고.
- **연쇄 Python 정리**: 위 죽은 CSS의 원인이었던 미사용 함수 3개(`render_portfolio_card_html`, `render_gallery_card_html` in `ui.py`, `render_placeholder_card` in `layout.py`)와 `render_hero()`의 미사용 `footer_html` 매개변수를 제거했다(호출부가 전혀 없음을 grep으로 확인, 테스트도 참조하지 않음).
- **검증**: 분리 전/후 CSS를 선택자+선언 단위로 정규화해 구조적으로 비교하는 스크립트로 완전히 동일함을 확인(의도적으로 제거한 항목 제외). `python -m unittest discover -s tests`(32개) 통과, 모든 페이지/컴포넌트 모듈 import 스모크 테스트 통과. 화면 동작 자체는 바꾸지 않는 리팩토링이라 브라우저 검증은 생략함 — 다음에 실제로 화면을 열 때 프로필 페이지가 정상적으로 스타일링되는지(버그 수정 확인 차원) 한 번 확인하면 좋음.
- **후속 정리 (같은 날, 서비스 레이어)**: CSS 정리와 같은 패턴(정의는 됐는데 아무도 안 부르는 함수)을 서비스 레이어에서도 스캔해 3개를 정리했다. `is_authenticated()`(`services/auth.py`), `set_project_visibility()`(`services/projects.py`)는 호출부가 없어 삭제. `count_author_stats()`(`services/projects.py`)는 정작 자기 자신은 안 쓰이면서 `protected.py`의 프로필 화면이 똑같은 통계 집계 로직을 인라인으로 중복 구현하고 있었다 — 원래 시그니처(`author_id`를 받아 내부에서 `list_projects_by_author()`를 다시 호출)대로 그냥 재사용하면 프로필 화면이 이미 가져온 목록을 두고 DB를 한 번 더 호출하게 되므로, 시그니처를 `projects: list[dict]`를 받도록 바꿔 `protected.py`가 이미 조회한 목록을 그대로 넘기게 했다(중복 호출 없이 중복 로직만 제거).
- `app.py`의 `_sync_browser_auth_storage()`에 죽은 분기가 하나 더 있었다: `cookies.get("restore_failed") == "1"` 체크와 `st.session_state.pop("folio_restore_failed", ...)` 모두, 그 값을 세팅하는 코드가 어디에도 없어 항상 거짓/no-op이었다. 삭제.

### 미해결: 로그인·서브페이지 전환 시 헤더 순간 깨짐 (관찰됨, 2026-07-06)

**증상**: 로그인하는 순간 헤더가 잠깐 깨졌다가 원상복구된다. 로그인 후 처음 서브페이지(Submit/My Portfolio/Profile 등)로 이동할 때도 한 번 더 발생한다. 그 이후로는 재발하지 않는다(같은 세션에서 다시 로그인하거나 다른 서브페이지로 이동해도 안 나타남).

**작업 가설 (미확정)**: "한 번만 발생하고 다시 안 나타난다"는 패턴은 세션(브라우저 탭)당 한 번만 초기화되는 리소스를 의심하게 한다.
- 로그인 시: `EncryptedCookieManager`가 토큰을 브라우저에 쓸 때(`cookies.save()`) 처음으로 `"CookieManager.sync_cookies.save"` 키의 커스텀 컴포넌트(별도 iframe)가 새로 마운트된다. 이 라이브러리는 `st.cache`/`key=` 기반 위젯이 아니라 `components.declare_component()`로 만든 순수 커스텀 컴포넌트라서, 우리 CSS가 의존하는 `.st-key-*` 클래스가 애초에 붙지 않는다(Streamlit 소스 확인: `.st-key-*`는 button/checkbox 등 내장 위젯 엘리먼트 코드에서만 명시적으로 부여됨). 그래서 이 iframe은 `iframe[title*="CookieManager"]` 같은 속성 기반 선택자로만 숨길 수 있는데, 이 선택자는 iframe에 해당 속성이 실제로 채워진 뒤에야 매치된다 — 최초 마운트 시 그 잠깐의 간극에서 래퍼가 잠깐 정상 크기로 보였다가(레이아웃 밀림) CSS가 따라잡으며 복구되는 것일 수 있다.
- 서브페이지 이동 시: 해당 페이지에서만 쓰는 위젯(`st.toggle`, `st.dialog`, Quill 커스텀 컴포넌트 등)이 이 세션에서 처음 마운트되며 비슷한 종류의 콜드 스타트 비용이 들 수 있다.
- 두 경우 모두, 한 번 마운트된 컴포넌트는 이후 세션 동안 그대로 남아있어 재마운트 비용이 없다 — "그 이후로는 재발하지 않음"과 부합.

**확인 안 된 것**: 위 가설은 정적 코드 분석(Streamlit 설치 패키지 소스 확인 포함)으로 도출했고, 실제 DevTools Network 탭이나 `PerformanceObserver({type:'layout-shift'})` 계측으로 실측 확인은 하지 않았다. `is_authenticated`/`set_project_visibility`/`count_author_stats`/`restore_failed` 죽은 코드 정리는 이 조사 과정에서 발견해 함께 반영했지만, 헤더 깨짐 증상 자체를 없애지는 못했을 가능성이 있다(재현 확인 필요). 확정하려면 `tools/measure_transition_cls.py` 계열 도구로 로그인 순간과 첫 서브페이지 진입 순간을 실측해야 한다.

### 완료: 페이지 전환 CLS 개선 (2026-07-06)

Streamlit 1.41.1 → 1.58.0 업그레이드로 근본 해결(`st.columns()` 내부 ResizeObserver 오버슈트가 프레임워크 차원에서 고쳐짐). 헤더도 `st.columns()`를 걷어내고 flex-row로 재구성(위 "Streamlit CSS 한계" 참고).

**남은 것**: 홈 화면 검색/태그 필터 패널 등 다른 `st.columns()` 사용처는 리사이즈 시 여전히 작은 흔들림이 있음(범위상 보류). 로그인 세션에서 메뉴 팝오버(`st.popover`) 동작 재확인 필요.

## 다음 작업 우선순위

현재 MVP 핵심 기능과 단위 테스트는 구현되어 있다. 새 기능을 늘리기 전에 아래 순서로 배포 안정성을 높인다.

1. **완료: 오류 처리와 운영 진단 보강**
   - 프로젝트 mutation·좋아요·인증·프로필·온보딩에서 공급자 예외 원문을 제거하고 서버 로그에만 남긴다.
   - 프로필 없음, 좋아요 0건, 빈 작성자 정보와 실제 조회 실패를 서비스 오류로 구분한다.
   - 마이 페이지 프로필과 상세 좋아요 상태에 재시도 흐름을 추가하고, 조회수 RPC 실패는 완료 처리하지 않는다.
   - JWT 복구 후 재실패, 로그인 프로필 복구 실패, 공급자 로그아웃 실패도 진단 로그를 남긴다.
   - 오류 처리 테스트 8개를 추가해 전체 단위 테스트 50개가 통과한다.
2. **완료: 일간 순조회수 적용**
   - ADR-012에 따른 `project_views`, RPC, 익명 방문자 쿠키와 앱 호출 로직을 로컬과 원격 Supabase에 적용했다.
   - 쿠키 유지, RPC 결과 구분, 실패 후 재시도, SQL 중복·작성자 제외 계약 테스트를 추가했다.
   - 실제 anon 호출, 하드 리로드, 작성자 본인 열람 제외와 직접 테이블 접근 차단을 검증했다.
   - 기존 조회수와 검증 기록을 초기화하고 새 정책 기준으로 집계를 시작했다. 상세 결과는 `docs/INTEGRATION_VALIDATION.md`를 참고한다.
3. **미검증 인증 흐름 확인**
   - 별도 테스트 계정 사용 승인 후 회원가입, 이메일 인증, 최초 온보딩을 확인한다.
   - 서로 다른 두 계정 사이의 작성자 전용 수정·삭제 RLS를 확인한다.
4. **완료: 프로젝트 작성 초안 보호**
   - 신규 등록과 프로젝트별 수정 초안을 사용자 ID와 작업 ID로 분리해 `session_state`에 임시 보존한다.
   - 일반 입력과 Quill 본문 반환값을 매 rerun마다 함께 저장하고 폼 재진입 시 복구한다.
   - 등록·수정 성공, 수정 취소, `초안 지우기`에서 초안과 관련 위젯 상태를 제거한다.
   - 위젯 상태 삭제는 다음 rerun의 렌더 전에 수행해 Streamlit 상태 변경 제약을 피한다.
   - 초안 격리·복구·삭제 테스트 6개를 추가해 전체 단위 테스트 56개가 통과한다.
5. **테스트와 문서 보강**
   - CRUD, 좋아요, 조회수 실패, 쿠키 복구, 비공개 접근 흐름의 테스트를 추가한다.
   - 기능 변경 시 이 문서와 관련 체크리스트를 함께 갱신한다.

### 완료: 코덱스 UI/UX 리뷰 대응 (2026-07-07)

이전 세션에서 코덱스에게 요청한 전반적 UI/UX 검토(PC·모바일, 로그인 상태) 결과를 코드로 하나씩 대조 검증한 뒤 세 가지를 수정했다.

- **Primary 버튼이 흰색으로 보이던 문제**: `project_form.py`의 등록 버튼은 이미 `type="primary"`였지만, `styles/buttons_inputs.py`의 전역 `.stButton > button` 규칙이 `kind` 속성 구분 없이 모든 버튼에 흰 배경을 강제해 무시되고 있었다. `[kind="primary"]` 전용 규칙(파란 배경, 흰 글자, hover 진한 파랑)을 추가해 해결.
- **모바일 Submit 폼이 2/3열을 유지해 입력창이 잘리던 문제**: `render_project_form()`은 PC 기준으로만 설계돼 `st.columns(2)`(기본정보/미리보기), `st.columns(3)`(BI/GitHub/ETC URL)을 그대로 쓰고, 기존 `@media (max-width: 860px)` 블록은 여백만 조정할 뿐 컬럼을 쌓지 않았다. `styles/project_form.py`의 반응형 블록에 `[data-testid="stHorizontalBlock"] { flex-direction: column }` + `[data-testid="stColumn"] { width: 100% }`를 추가해 모바일에서 1열로 전환.
- **모바일 마이페이지 보기/수정/삭제 버튼이 세로로 좁아 글자가 꺾이던 문제**: `protected.py`가 `st.columns([5, 1])`로 프로젝트 정보:액션을 나눠, 좁은 1/6 칸에 버튼 3개가 세로로 쌓이는 구조였다. `styles/portfolio.py`에 모바일 전용 규칙을 추가해 액션 컬럼을 프로젝트 정보 아래로 내리고(`flex-direction: column`), 그 안의 버튼 3개는 `display:flex; flex-direction:row`로 가로 배치.

검증은 `tools/probe_header_auth_states.py`와 같은 패턴으로 `get_current_user()`/`list_projects_by_author()`/`get_profile()`을 몽고패치하는 임시 스크립트를 만들어 실제 로그인 없이 Submit/My Page를 렌더링하고, Selenium으로 모바일 390×844 뷰포트를 캡처해 확인했다(임시 스크립트와 캡처 이미지는 확인 후 삭제). `python -m unittest discover -s tests`(32개) 통과.

**후속 (같은 날)**: 코덱스가 중간 우선순위로 지적한 "회원가입 화면에 로그인 전환 링크 없음"을 확인하는 과정에서, `WIREFRAME.MD`에 "회원가입 페이지 하단에는 로그인 전환 링크를 두지 않는다"가 의도된 규칙으로 명시돼 있는 걸 발견했다. 사용자에게 확인한 결과 그 규칙을 폐기하고 링크를 추가하기로 결정 — `auth.py`의 `render_signup()` 끝에 로그인 화면의 "처음이라면 회원가입하기"와 대칭되는 "이미 계정이 있다면 로그인하기" 버튼을 추가하고, `WIREFRAME.MD`의 규칙 문구도 갱신했다.

같은 확인 과정에서 문서 드리프트도 발견해 정리했다: `My Portfolio`/`Profile`은 코드상 이미 `My Page`로 통합됐고(`protected.py`의 `render_my_portfolio()`/`render_profile()`은 `navigate("My Page")`만 호출) 헤더 nav도 "마이 페이지" 하나뿐인데, `WIREFRAME.MD`·`PROJECT_CONTEXT.md`(이 문서)·`README.md`가 전부 예전 2-페이지 구조로 남아 있었다. 라우팅 표, nav 설명, 파일 역할 설명을 현재 코드 기준으로 갱신했다. `README.md`의 `folio_app/styles.py`(2026-07-06에 이미 패키지로 분리됨) 참조도 함께 바로잡았다.

남은 것: 모바일 상세 Power BI 임베드가 다소 무겁다는 지적은 아직 미착수.

### 종료: 라이트 테마 재설계 (2026-07-06, 재검토 후 대부분 이미 완료 상태로 확인)

이 항목은 원래 "다크 헤더 + 다크 히어로 이음새 gap이 어색하다"는 이유로 우선순위에 있었다. 재검토 결과 이미 실질적으로 해결되어 있었다: `render_hero()`의 `dark=True` 옵션(→ `.folio-page-hero-dark`)을 실제로 넘기는 호출부가 코드 어디에도 없어서, Home·Submit·My Portfolio·Profile·상세 페이지의 히어로는 전부 흰 배경(`--folio-surface`)이었다. 남는 다크 요소는 헤더(sticky, 둥근 카드)와 로그인/회원가입 카드 상단 배너뿐이고, 둘 다 페이지 배경에 바로 이어붙는 형태가 아니라 독립된 카드라서 애초에 우려했던 "이음새" 문제가 발생하지 않는 구조다. 죽은 `dark` 매개변수와 `.folio-page-hero-dark` CSS(+반응형 규칙)를 제거했다. 헤더/로그인 배너까지 라이트로 바꾸는 건 순수 취향 문제로 남겨두고, 이 우선순위 항목 자체는 닫는다.
