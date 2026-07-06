# Supabase 설정 절차

이 문서는 Week 1 체크리스트의 **2.2**, **7.6**, **4.6~5.4**를 진행하기 위한 절차입니다.

## 1. Supabase 프로젝트 생성

1. Supabase에 로그인합니다.
2. 새 프로젝트를 생성합니다.
3. 프로젝트가 준비될 때까지 기다립니다.

## 2. DB 스키마 실행

1. Supabase 프로젝트에서 **SQL Editor**로 이동합니다.
2. `supabase/schema.sql` 파일 내용을 복사합니다.
3. SQL Editor에 붙여넣고 실행합니다.
4. Table Editor에서 다음 테이블이 생성되었는지 확인합니다.
   - `profiles`
   - `projects`
   - `likes`
5. Database Triggers에서 `on_auth_user_created` 트리거가 생성되었는지 확인합니다.

기존 프로젝트도 인증/RLS 정책이 변경되면 최신 `supabase/schema.sql`을 다시 실행합니다. 스키마는 `if not exists`, `drop policy if exists` 구문을 사용하므로 정책 갱신에도 같은 파일을 사용합니다.

### 공개 → 비공개 변경 시 42501 오류

로그인한 작성자가 공개 프로젝트는 수정할 수 있지만 비공개 저장에서 `42501` 오류를 받는다면 원격 DB의 작성자 SELECT/UPDATE 정책이 오래된 상태입니다.

1. Supabase **SQL Editor**를 엽니다.
2. `supabase/fix_project_owner_rls.sql` 내용을 실행합니다.
3. 앱에서 로그아웃 후 다시 로그인합니다.
4. `마이 페이지 → 수정 → 프로젝트 공개`를 끄고 저장합니다.

이 SQL은 작성자 본인의 프로젝트만 조회·수정할 수 있도록 `auth.uid() = author_id`를 검사합니다.

## 3. API Key 확인

1. Supabase 프로젝트에서 **Project Settings**로 이동합니다.
2. **API** 메뉴를 엽니다.
3. 다음 값을 확인합니다.
   - Project URL
   - Publishable key (`sb_publishable_...`)

## 4. `.env` 파일 생성

프로젝트 루트에 `.env` 파일을 만들고 아래 형식으로 입력합니다.

```text
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-supabase-publishable-key
APP_URL=http://localhost:8501
COOKIE_PASSWORD=replace-with-a-long-random-cookie-password
```

주의:

- `secret` 또는 `service_role` key를 넣지 않습니다.
- 기존 프로젝트의 legacy `anon` key는 `SUPABASE_ANON_KEY` 이름으로도 계속 사용할 수 있습니다.
- `.env`는 `.gitignore`에 포함되어 있으므로 저장소에 커밋되지 않습니다.
- `COOKIE_PASSWORD`는 로그인 유지용 암호화 쿠키에 사용하므로 운영 환경에서는 긴 임의 문자열로 설정합니다.

## 5. 앱 재시작

`.env`를 만든 뒤 Streamlit 서버를 재시작합니다.

```powershell
streamlit run app.py
```

## 6. 인증 테스트

1. 앱에서 `Login` 화면으로 이동합니다.
2. 로그인 화면의 회원가입 링크를 통해 `Sign Up` 화면으로 이동합니다.
   - 상단 햄버거 메뉴에는 `회원가입`을 노출하지 않습니다.
3. 이메일, 비밀번호, 이름, 기관명을 입력해 회원가입합니다.
4. Supabase Auth의 Users 목록에 사용자가 생성되었는지 확인합니다.
5. Supabase Table Editor의 `profiles` 테이블에 같은 사용자의 row가 생성되었는지 확인합니다.
   - 이메일 인증이 켜져 있어도 DB 트리거가 `profiles` row를 생성해야 합니다.
6. 로그아웃합니다.
7. 같은 계정으로 로그인합니다.
8. 로그인 후 햄버거 메뉴 안에 다음 메뉴가 표시되는지 확인합니다.
   - `Submit`
   - `My Page`

## 7. 이메일 인증 설정 참고

Supabase Auth에서 이메일 인증이 켜져 있으면 회원가입 직후 자동 로그인되지 않을 수 있습니다.

이 경우 정상 흐름은 다음과 같습니다.

1. 회원가입
2. 이메일 인증
3. 로그인
4. `profiles` row 생성 확인

빠른 MVP 테스트를 원하면 Supabase Auth 설정에서 이메일 인증을 임시로 끌 수 있습니다.

## 8. 이메일 인증 후 localhost 연결 거부 대응

이메일 인증 링크를 눌렀을 때 브라우저에서 `localhost` 연결이 거부되면 보통 다음 중 하나입니다.

1. Streamlit 서버가 실행 중이 아님
   - `streamlit run app.py`를 실행한 뒤 `http://localhost:8501`로 직접 접속합니다.
2. Supabase Auth 리다이렉트 URL이 앱 주소와 다름
   - Supabase Dashboard의 **Authentication > URL Configuration**에서 Site URL을 `http://localhost:8501`로 설정합니다.
   - Redirect URLs에도 `http://localhost:8501/**` 또는 `http://localhost:8501`을 추가합니다.
3. 이메일 인증 링크는 인증 완료용이고, 앱 로그인은 별도로 해야 함
   - 인증 완료 후 브라우저에서 `http://localhost:8501`을 직접 열고 `Login` 메뉴에서 같은 이메일/비밀번호로 로그인합니다.

현재 앱은 Supabase 인증 링크 클릭 후 자동 로그인하지 않습니다.

인증 메일 링크는 Login 화면으로 이동시키고, 사용자가 가입한 이메일과 비밀번호로 직접 로그인합니다.

권장 redirect URL은 다음 형태입니다.

```text
http://localhost:8501?page=Login&verified=1
```

Supabase가 `#access_token=...` fragment를 붙여서 돌려주더라도 앱은 자동 로그인에 사용하지 않습니다. 사용자는 Login 화면에서 직접 로그인합니다.

## 9. 인증 메일 재발송

회원가입 후 인증 메일을 받지 못했다면 앱의 `Sign Up` 화면 하단의 접힌 **인증 메일 다시 받기** 영역을 사용할 수 있습니다.

중요한 흐름:

- 회원가입 버튼을 누르면 Supabase Auth 사용자와 `profiles` row가 먼저 생성됩니다.
- 이메일 인증은 그 다음 단계입니다.
- 따라서 이미 가입된 이메일은 다시 회원가입할 수 없습니다.
- 인증을 완료하지 못한 사용자는 재가입이 아니라 **인증 메일 재발송**을 사용합니다.

1. `Login` 화면에서 회원가입 링크를 눌러 `Sign Up` 화면으로 이동합니다.
2. 하단의 `인증 메일 다시 받기` 영역을 펼칩니다.
3. `인증 메일 재발송 이메일`에 가입한 이메일을 입력합니다.
4. `인증 메일 다시 보내기`를 클릭합니다.
5. 메일함과 스팸함을 확인합니다.

Supabase rate limit에 걸리면 잠시 후 다시 시도합니다.
