# FOLIO

발표로 끝나지 않는 프로젝트.

FOLIO는 데이터 분석 프로젝트를 포트폴리오 자산으로 축적하고 공유하는 Streamlit + Supabase 기반 MVP입니다.

## 현재 구현 범위

- Supabase Auth 기반 로그인/회원가입/로그아웃
- 암호화 쿠키 기반 로그인 유지
- 첫 로그인 후 이용약관·개인정보 처리방침 동의 온보딩
- 사용자 프로필 자동 생성, 조회 및 수정
- 프로젝트 등록, 수정, 삭제
- Quill 자유 입력 본문과 카드 미리보기 기반 프로젝트 작성
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
SUPABASE_ANON_KEY=your-supabase-anon-key
APP_URL=http://localhost:8501
COOKIE_PASSWORD=replace-with-a-long-random-cookie-password
```

4. 앱을 실행합니다.

```powershell
streamlit run app.py
```

기본 로컬 주소는 `http://localhost:8501`입니다.

## 배포

이 앱은 지속 실행되는 Streamlit 서버가 필요하므로 Vercel Functions에 직접 배포하지 않습니다. MVP 배포는 Streamlit Community Cloud를 권장합니다.

1. 저장소를 GitHub에 push합니다.
2. Streamlit Community Cloud에서 저장소와 `app.py`를 선택합니다.
3. 배포 환경의 Secrets에 다음 값을 등록합니다.

```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_ANON_KEY = "your-supabase-anon-key"
APP_URL = "https://your-app.streamlit.app"
COOKIE_PASSWORD = "replace-with-a-long-random-cookie-password"
```

4. Supabase의 Authentication > URL Configuration에서 배포 주소를 Site URL과 Redirect URL에 등록합니다.

`service_role` 키와 로컬 `.env`는 저장소 또는 배포 설정에 노출하지 않습니다.

## 주요 문서

- 작업 전 가장 먼저 확인할 문서: `docs/PROJECT_CONTEXT.md`
- 제품/기획 개요: `docs/PRD.md`
- 현재 화면 구조: `docs/WIREFRAME.MD`
- Supabase 설정: `docs/SUPABASE_SETUP.md`
- Week 1 완료 기록: `docs/WEEK1_BUILD_CHECKLIST.md`
- Week 2 완료 기록: `docs/WEEK2_BUILD_CHECKLIST.md`

현재 우선순위는 실제 Supabase 통합 검증, 오류 처리 보강, 라이트 테마 재설계, 작성 초안 보호 순입니다. 상세 기준은 `docs/PROJECT_CONTEXT.md`를 따릅니다.

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
