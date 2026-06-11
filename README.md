# FOLIO

발표로 끝나지 않는 프로젝트.

FOLIO는 데이터 분석 프로젝트를 포트폴리오 자산으로 축적하고 공유하는 Streamlit + Supabase 기반 MVP입니다.

## Week 1 Goal

- Streamlit 앱 뼈대
- Supabase 연결 준비
- 회원가입 / 로그인 / 로그아웃
- 로그인 후 `profiles` 테이블 자동 생성
- Home, Gallery, Login, Sign Up, About, Submit, My Portfolio, Profile 기본 화면

## Setup

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
```

4. 앱을 실행합니다.

```powershell
streamlit run app.py
```

## Notes

- Supabase 이메일 인증이 켜져 있으면 회원가입 직후 자동 로그인되지 않을 수 있습니다. 이 경우 이메일 인증 후 로그인하면 `profiles` row가 생성됩니다.
- Week 2에서 `projects` 테이블을 실제 프로젝트 등록/목록/상세 화면과 연결합니다.
