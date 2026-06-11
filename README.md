# FOLIO

발표로 끝나지 않는 프로젝트.

FOLIO는 데이터 분석 프로젝트를 포트폴리오 자산으로 축적하고 공유하는 Streamlit + Supabase 기반 MVP입니다.

## 현재 구현 범위

- Supabase Auth 기반 로그인/회원가입/로그아웃
- 암호화 쿠키 기반 로그인 유지
- 사용자 프로필 자동 생성 및 조회
- 프로젝트 등록, 수정, 삭제
- 자유 입력 본문 기반 프로젝트 작성
- 태그 중심 Gallery 탐색
- 검색, 태그 필터, 최신순/조회수순/좋아요순 정렬
- Gallery 안에서 `project_id` 쿼리 기반 상세 페이지 렌더링
- 조회수 증가 RPC 연동
- likes 테이블 기반 좋아요 수 계산
- Power BI iframe 또는 embed URL 표시
- 보고서/GitHub/썸네일 URL 선택 입력

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

## 주요 문서

- 제품/기획 개요: `docs/PRD.md`
- 현재 화면 구조: `docs/WIREFRAME.MD`
- Supabase 설정: `docs/SUPABASE_SETUP.md`
- 프로젝트 컨텍스트 및 개발 지침: `docs/PROJECT_CONTEXT.md`
- Week 1 완료 기록: `docs/WEEK1_BUILD_CHECKLIST.md`
- Week 2 완료 기록: `docs/WEEK2_BUILD_CHECKLIST.md`

## 개발 메모

- 카테고리는 사용하지 않습니다. 탐색은 태그 중심입니다.
- 회원가입은 상단 메뉴에 노출하지 않고, 로그인 화면의 링크로 진입합니다.
- Streamlit 전역 CSS는 다른 화면에 쉽게 영향을 주므로 전용 클래스 기준으로 좁게 수정합니다.
- 단순 문구/CSS 변경에는 과한 검증을 하지 않고, 파이썬 구조 변경 때 필요한 파일 단위로 확인합니다.
