# FOLIO

발표로 끝나지 않는 프로젝트.

FOLIO는 데이터 분석 프로젝트를 포트폴리오 자산으로 축적하고 공유하는 Streamlit + Supabase 기반 MVP입니다.

## 현재 구현 범위

- Supabase Auth 기반 로그인/회원가입/로그아웃
- 암호화 쿠키 기반 로그인 유지
- 첫 로그인 후 이용약관·개인정보 처리방침 동의 온보딩
- 사용자 프로필 자동 생성, 조회 및 수정
- 프로젝트 등록, 수정, 삭제
- Quill 자유 입력 본문과 기본 정보 옆 실시간 카드 미리보기 기반 프로젝트 작성
- 홈 화면 안의 태그 중심 프로젝트 탐색
- 검색, 태그 필터, 최신순/조회수순/좋아요순 정렬
- Home 안에서 `project_id` 쿼리 기반 상세 페이지 렌더링
- 세션별 중복 증가를 방지하는 조회수 RPC 연동
- `likes` 테이블 기반 좋아요 추가·취소 및 좋아요순 정렬
- Power BI iframe 또는 embed URL 표시
- 보고서/GitHub/썸네일 URL 선택 입력
- 프로젝트 본문 HTML 허용 목록 정제

## 실행

1. Python 가상환경을 만들고 의존성을 설치합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Supabase 프로젝트를 만들고 SQL Editor에서 `supabase/schema.sql`을 실행합니다.

3. `.env.example`을 참고해 `.env`를 생성합니다.

```text
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-supabase-publishable-key
APP_URL=http://localhost:8501
COOKIE_PASSWORD=replace-with-a-long-random-cookie-password
```

4. 앱을 실행합니다.

```powershell
streamlit run app.py
```

기본 로컬 주소는 `http://localhost:8501`입니다.

Windows 개발 환경에서는 구·신 Streamlit 프로세스가 같은 포트를 함께 점유하는 문제를 막기 위해
파일 자동 감시를 끕니다. 코드 수정 후 화면이 갱신되어야 할 때는 실행 중인 서버를 종료하고
`streamlit run app.py`를 다시 실행합니다.

## 애플리케이션 진입 구조

FOLIO에는 이름이 같은 `app.py`가 두 개 있지만 역할이 다릅니다.

```text
streamlit run app.py
        │
        ▼
루트 app.py
  - Streamlit 페이지 기본 설정
  - folio_app.app.main() 호출
        │
        ▼
folio_app/app.py
  - 환경 설정과 로그인 쿠키 준비
  - 인증 세션 복구와 온보딩 확인
  - URL의 page 값에 맞는 화면 함수 호출
  - 공통 헤더와 푸터 출력
```

- 루트 `app.py`는 Streamlit이 직접 실행하는 **얇은 실행 진입점**입니다. `st.set_page_config()`를 가장 먼저 호출한 후 실제 앱의 `main()`으로 넘깁니다.
- `folio_app/app.py`는 애플리케이션의 **실제 조정자**입니다. 인증, 쿠키, 라우팅, 온보딩과 화면 렌더링 순서를 관리합니다.
- 배포 설정의 Main file path에는 루트의 `app.py`를 지정합니다. `folio_app/app.py`를 직접 실행하지 않습니다.

## URL과 페이지 코드 연결

이 프로젝트는 Streamlit의 파일 기반 멀티페이지 디렉터리를 사용하지 않습니다. `?page=` 쿼리값을 `folio_app/app.py`가 읽어 해당 렌더 함수를 호출합니다.

| URL 또는 `page` 값 | 화면 | 담당 코드 |
|---|---|---|
| `/` 또는 `?page=Home` | 홈, 검색, 태그 필터, 프로젝트 목록 | `pages/home.py:render()` |
| `?page=Home&project_id=...` | 프로젝트 상세 | `pages/project_detail.py:render()` |
| `?page=Login` | 로그인 | `pages/auth.py:render_login()` |
| `?page=Sign+Up` | 회원가입, 인증 메일 재발송 | `pages/auth.py:render_signup()` |
| `?page=Submit` | 프로젝트 등록 | `pages/protected.py:render_submit()` |
| `?page=My+Page` | 프로필, 통계, 내 프로젝트 조회·수정·삭제 | `pages/protected.py:render_my_page()` |
| `?page=My+Portfolio`, `?page=Profile` | 기존 URL 호환용 My Page 리다이렉트 | `pages/protected.py:render_my_portfolio()`, `render_profile()` |
| `?page=Gallery` | 기존 URL 호환용 Home 리다이렉트 | `pages/gallery.py:render()` |
| 로그인 직후 필요한 경우 | 약관·개인정보 동의 온보딩 | `pages/onboarding.py:render()` |

페이지 주소를 추가하거나 변경할 때는 `folio_app/navigation.py`의 `ROUTABLE_PAGES`와 `folio_app/app.py`의 `page_handlers`를 함께 수정합니다.

## Python 파일별 역할

### 실행·설정

| 파일 | 역할 |
|---|---|
| `app.py` | Streamlit 페이지 설정 후 `folio_app.app.main()`을 호출하는 실행 진입점 |
| `folio_app/app.py` | 앱 초기화, 쿠키 세션 복구, 로그아웃, 레거시 URL 정리, 온보딩 검사, 페이지 라우팅, 푸터 출력 |
| `folio_app/config.py` | 로컬 `.env`, 환경변수, Streamlit Cloud `st.secrets`를 읽어 Supabase·앱·쿠키 설정 제공 |
| `folio_app/navigation.py` | 허용 페이지 목록과 `st.query_params` + `st.rerun()` 기반 내부 이동 제공 |
| `folio_app/styles/` | 화면 영역별로 나뉜 CSS 모듈과, 이를 이어붙여 `st.html()`로 1회 주입하는 `apply_global_styles()` |
| `folio_app/__init__.py` | `folio_app`을 Python 패키지로 인식시키는 초기화 파일 |

### 페이지

| 파일 | 역할 |
|---|---|
| `folio_app/pages/home.py` | 홈 히어로, 검색·태그·정렬 폼, 공개 프로젝트 카드 목록 렌더링 |
| `folio_app/pages/project_detail.py` | 프로젝트 본문, 작성자, 조회수, 좋아요, Power BI, 첨부 링크 렌더링 |
| `folio_app/pages/auth.py` | 로그인, 회원가입, 입력 검증, 인증 메일 재발송 UI |
| `folio_app/pages/onboarding.py` | 최초 로그인 사용자의 프로필 확인과 약관·개인정보 동의 UI |
| `folio_app/pages/protected.py` | 로그인이 필요한 프로젝트 등록 화면과, 프로필·통계·내 프로젝트 조회·수정·삭제를 한 화면에 담은 My Page |
| `folio_app/pages/gallery.py` | 과거 Gallery 주소를 Home으로 보내는 호환용 페이지 |
| `folio_app/pages/__init__.py` | `pages` 패키지 초기화 파일 |

### 공통 컴포넌트

| 파일 | 역할 |
|---|---|
| `folio_app/components/layout.py` | 공통 헤더·메뉴, 페이지 히어로, 정적 이미지 로딩 |
| `folio_app/components/project_form.py` | 등록·수정 공용 폼, Quill 편집기, 본문 섹션 파싱, URL 검증, 카드 미리보기 |
| `folio_app/components/ui.py` | 태그, 프로젝트 카드 HTML, 일반 텍스트 변환 등 공통 UI 유틸리티 |
| `folio_app/components/__init__.py` | `components` 패키지 초기화 파일 |

### Supabase 서비스

| 파일 | 역할 |
|---|---|
| `folio_app/services/supabase_client.py` | Streamlit 세션별 Supabase client 생성·폐기와 만료 JWT 복구 |
| `folio_app/services/auth.py` | 회원가입, 로그인, 로그아웃, 토큰 저장과 쿠키 세션 복구 |
| `folio_app/services/profiles.py` | 프로필 생성·조회·수정, 온보딩 정책과 사용자 동의 처리 |
| `folio_app/services/projects.py` | 프로젝트 CRUD, 공개 목록·검색·정렬, 작성자 정보, 조회수, 좋아요, 캐시 관리 |
| `folio_app/services/project_content.py` | 사용자 작성 HTML의 허용 태그·링크 검사와 위험 요소 제거 |
| `folio_app/services/__init__.py` | `services` 패키지 초기화 파일 |

### 기타 Python 파일

| 경로 | 역할 |
|---|---|
| `tests/test_*.py` | 설정, 인증 안정성, 라우팅, 본문 정제, 프로젝트 조회·폼 동작에 대한 단위 테스트 |
| `tools/capture_streamlit_scroll.py` | UI 변경 후 로컬 Streamlit 화면을 스크롤 캡처하는 개발 도구 |

화면 문구나 버튼은 주로 `pages/`, 반복 UI는 `components/`, 데이터 처리나 Supabase 호출은 `services/`, 색상·간격·폰트는 `styles/`에서 수정합니다.

## 배포

이 앱은 지속 실행되는 Streamlit 서버가 필요하므로 Vercel Functions에 직접 배포하지 않습니다. MVP 배포는 Streamlit Community Cloud를 권장합니다.

1. 저장소를 GitHub에 push합니다.
2. Streamlit Community Cloud에서 저장소와 `app.py`를 선택합니다.
3. 배포 환경의 Secrets에 다음 값을 등록합니다.

```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "your-supabase-publishable-key"
APP_URL = "https://your-app.streamlit.app"
COOKIE_PASSWORD = "replace-with-a-long-random-cookie-password"
```

4. Supabase의 Authentication > URL Configuration에서 배포 주소를 Site URL과 Redirect URL에 등록합니다.

`service_role` 키와 로컬 `.env`는 저장소 또는 배포 설정에 노출하지 않습니다.
Cloud Secrets 입력란에는 Markdown 코드 블록 표시 없이 TOML 내용만 붙여넣고, 저장 후 앱을 재부팅합니다. 앱은 루트 키를 우선 사용하며 `[supabase]` 섹션의 `url`과 `key` 형식도 호환합니다.

## 주요 문서

- 전체 문서 안내: [`docs/README.md`](docs/README.md)
- 시스템 아키텍처: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- 핵심 사용자 흐름: [`docs/USER_FLOWS.md`](docs/USER_FLOWS.md)
- ERD와 RLS 데이터 모델: [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md)
- 주요 설계 결정: [`docs/DECISIONS.md`](docs/DECISIONS.md)
- 개발 정책과 교훈: [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md)
- 작업 전 현재 컨텍스트: [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md)
- 제품/기획 개요: [`docs/PRD.md`](docs/PRD.md)
- 현재 화면 구조: [`docs/WIREFRAME.MD`](docs/WIREFRAME.MD)
- Supabase 설정: [`docs/SUPABASE_SETUP.md`](docs/SUPABASE_SETUP.md)

현재 우선순위는 실제 Supabase 통합 검증, 오류 처리 보강, 작성 초안 보호, 테스트와 문서 보강 순입니다. 상세 기준은 `docs/PROJECT_CONTEXT.md`를 따릅니다.

## 개발 메모

- 카테고리는 사용하지 않습니다. 탐색은 태그 중심입니다.
- 회원가입은 상단 메뉴에 노출하지 않고, 로그인 화면의 링크로 진입합니다.
- 인증 상태나 데이터를 변경하는 이동에는 HTML 링크 대신 공통 `navigate()`와 Streamlit 버튼을 사용합니다.
- Streamlit 전역 CSS는 다른 화면에 쉽게 영향을 주므로 컨테이너 `key` 기반으로 범위를 좁힙니다.
- 사용자 프로젝트 본문은 저장 및 출력 시 `sanitize_project_html()`로 정제합니다.
- 단순 문구/CSS 변경에는 과한 검증을 하지 않고, 파이썬 구조 변경 때 필요한 파일 단위로 확인합니다.
- UI/UX 수정 후에는 브라우저 스크롤 캡처로 실제 화면을 확인하고, 확인 후 캡처 파일은 삭제합니다.

## 개발 보조 도구

브라우저 스크롤 캡처 확인에는 별도 개발 의존성이 필요합니다.

```powershell
pip install -r requirements-dev.txt
```

캡처 산출물은 `artifacts/`에 생성되며 `.gitignore`로 제외됩니다.

## 테스트

표준 라이브러리 기반 단위 테스트는 다음 명령으로 실행합니다.

```powershell
python -m unittest discover -s tests -v
```
