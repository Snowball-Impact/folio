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

## 3. API Key 확인

1. Supabase 프로젝트에서 **Project Settings**로 이동합니다.
2. **API** 메뉴를 엽니다.
3. 다음 값을 확인합니다.
   - Project URL
   - anon public key

## 4. `.env` 파일 생성

프로젝트 루트에 `.env` 파일을 만들고 아래 형식으로 입력합니다.

```text
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
APP_URL=http://localhost:8501
```

주의:

- `service_role` key를 넣지 않습니다.
- `.env`는 `.gitignore`에 포함되어 있으므로 저장소에 커밋되지 않습니다.

## 5. 앱 재시작

`.env`를 만든 뒤 Streamlit 서버를 재시작합니다.

```powershell
streamlit run app.py
```

## 6. 인증 테스트

1. 앱에서 `Sign Up`으로 이동합니다.
2. 이메일, 비밀번호, 이름, 기관명을 입력해 회원가입합니다.
3. Supabase Auth의 Users 목록에 사용자가 생성되었는지 확인합니다.
4. Supabase Table Editor의 `profiles` 테이블에 같은 사용자의 row가 생성되었는지 확인합니다.
   - 이메일 인증이 켜져 있어도 DB 트리거가 `profiles` row를 생성해야 합니다.
5. 로그아웃합니다.
6. 같은 계정으로 로그인합니다.
7. 로그인 후 메뉴가 다음처럼 바뀌는지 확인합니다.
   - `Submit`
   - `My Portfolio`
   - `Profile`

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

회원가입 후 인증 메일을 받지 못했다면 앱의 `Sign Up` 화면 하단에서 **인증 메일 다시 받기**를 사용할 수 있습니다.

중요한 흐름:

- 회원가입 버튼을 누르면 Supabase Auth 사용자와 `profiles` row가 먼저 생성됩니다.
- 이메일 인증은 그 다음 단계입니다.
- 따라서 이미 가입된 이메일은 다시 회원가입할 수 없습니다.
- 인증을 완료하지 못한 사용자는 재가입이 아니라 **인증 메일 재발송**을 사용합니다.

1. `Sign Up` 화면으로 이동합니다.
2. 하단의 `인증 메일 재발송 이메일`에 가입한 이메일을 입력합니다.
3. `인증 메일 다시 보내기`를 클릭합니다.
4. 메일함과 스팸함을 확인합니다.

Supabase rate limit에 걸리면 잠시 후 다시 시도합니다.
