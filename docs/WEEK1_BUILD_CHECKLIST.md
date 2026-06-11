# FOLIO Week 1 구축 체크리스트

## 1. 프로젝트 초기 구조

- [x] 1.1 Streamlit 진입점 생성
  - `app.py`
- [x] 1.2 앱 패키지 구조 생성
  - `folio_app/`
  - `folio_app/pages/`
  - `folio_app/components/`
  - `folio_app/services/`
- [x] 1.3 기본 의존성 파일 생성
  - `requirements.txt`
- [x] 1.4 Git 제외 파일 설정
  - `.gitignore`

## 2. 환경 설정

- [x] 2.1 Supabase 환경 변수 예시 파일 생성
  - `.env.example`
- [x] 2.2 실제 `.env` 파일 생성
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - 참고: `docs/SUPABASE_SETUP.md`
- [x] 2.3 Streamlit 테마 설정
  - `.streamlit/config.toml`

## 3. Supabase 연동 기반

- [x] 3.1 Supabase client 생성 유틸 구현
  - `folio_app/services/supabase_client.py`
- [x] 3.2 환경 변수 로딩 설정
  - `folio_app/config.py`
- [x] 3.3 Supabase 미설정 상태 안내 처리
  - 앱 상단 warning 표시

## 4. 인증 기능

- [x] 4.1 회원가입 서비스 구현
  - 이메일
  - 비밀번호
  - 이름
  - 기관명
- [x] 4.2 로그인 서비스 구현
- [x] 4.3 로그아웃 서비스 구현
- [x] 4.4 Streamlit session state 기반 로그인 상태 관리
- [x] 4.5 회원가입 또는 로그인 후 프로필 자동 생성 로직 구현
- [x] 4.6 실제 Supabase 프로젝트로 회원가입 테스트
  - 테스트 계정 회원가입 요청 성공
- [x] 4.7 실제 Supabase 프로젝트로 로그인 테스트
  - `ggmaeng@gmail.com` 계정 로그인 성공
- [x] 4.8 로그아웃 후 보호 메뉴 상태 확인
  - 브라우저에서 로그아웃 후 메뉴 전환 확인
- [x] 4.9 회원가입 UX 보강
  - 이메일 정규화
  - 이메일 형식 검증
  - 비밀번호 확인 입력
  - 비밀번호 최소 8자 검증
  - 소속 필수 입력 처리
  - 이메일 인증 안내 유지
  - Supabase 인증 오류 사용자 친화 메시지 처리
- [x] 4.10 이메일 인증 후 Login 페이지 이동 처리
  - 회원가입 시 Login 페이지 URL을 `email_redirect_to`로 전달
  - 인증 완료 후 Login 메뉴를 기본 선택
  - 인증 완료 안내 후 사용자가 직접 로그인
- [x] 4.11 이미 가입된 이메일 회원가입 차단
  - 이메일 입력 시 `profiles` 기준 중복 여부 확인
  - 중복 이메일이면 회원가입 버튼 비활성화
  - 서비스 계층에서도 회원가입 직전 중복 차단
- [x] 4.12 인증 메일 재발송 기능
  - Supabase `auth.resend(type=signup)` 연동
  - 재발송 시 `APP_URL`을 redirect URL로 전달
  - Sign Up 화면 하단에서 이메일 입력 후 재발송 가능
  - 이미 가입된 이메일 입력 시 재가입 대신 인증 메일 재발송 흐름 안내
- [x] 4.13 인증 UX 마감 보강
  - 인증 메일 재발송 60초 쿨다운
  - 인증 완료 안내 메시지 수동 dismiss 처리
- [x] 4.14 새로고침 후 로그인 유지
  - 로그인 성공 시 암호화 쿠키에 Supabase token 저장
  - 앱 시작 시 저장된 token으로 Supabase session 복원
  - 로그아웃 시 쿠키 token 삭제

## 5. 프로필 기능

- [x] 5.1 `profiles` upsert 서비스 구현
- [x] 5.2 `profiles` 조회 서비스 구현
- [x] 5.3 Profile 화면에서 사용자 기본 정보 표시
- [x] 5.4 Supabase `profiles` 테이블에 row 생성 확인
  - `auth.users` 생성 trigger로 `profiles` row 자동 생성 확인

## 6. Week 1 화면

- [x] 6.1 Home 화면 생성
- [x] 6.2 Gallery 자리 표시 화면 생성
- [x] 6.3 Login 화면 생성
- [x] 6.4 Sign Up 화면 생성
- [x] 6.5 About 화면 생성
- [x] 6.6 로그인 후 Submit 자리 표시 화면 생성
- [x] 6.7 로그인 후 My Portfolio 자리 표시 화면 생성
- [x] 6.8 로그인 후 Profile 화면 생성
- [x] 6.9 로그인 상태에 따른 내비게이션 분기

## 7. DB 스키마

- [x] 7.1 `profiles` 테이블 SQL 작성
- [x] 7.2 `projects` 테이블 SQL 작성
- [x] 7.3 `likes` 테이블 SQL 작성
- [x] 7.4 기본 index 작성
- [x] 7.5 RLS 활성화 및 정책 작성
- [x] 7.6 Supabase SQL Editor에서 최신 `supabase/schema.sql` 실행
  - 참고: `docs/SUPABASE_SETUP.md`
- [x] 7.7 Auth 사용자 생성 시 `profiles` 자동 생성 트리거 작성

## 8. 로컬 실행 및 검증

- [x] 8.1 Python 문법 컴파일 확인
  - `python -m compileall app.py folio_app`
- [x] 8.2 주요 패키지 import 확인
  - `streamlit`
  - `supabase`
  - `dotenv`
- [x] 8.3 의존성 설치
  - `pip install -r requirements.txt`
- [x] 8.4 Streamlit 서버 실행
- [x] 8.5 로컬 HTTP 응답 확인
  - `http://localhost:8501`
- [x] 8.6 `.env` 반영 후 Streamlit 서버 재시작
- [x] 8.7 브라우저에서 화면 직접 확인
  - 로그인/로그아웃 흐름 브라우저 확인

## 9. 현재 진행 위치

현재 완료 지점은 **4.8 로그아웃 후 보호 메뉴 상태 확인**입니다.

Supabase client와 `profiles`, `projects`, `likes` 테이블 접근은 확인됐습니다.

회원가입 요청은 한 차례 성공했지만 Supabase 이메일 인증 설정 때문에 즉시 세션이 발급되지 않아 앱 코드의 프로필 생성이 실행되지 않았습니다. 이를 보완하기 위해 `auth.users` 생성 시 `profiles`를 자동 생성하는 트리거를 `supabase/schema.sql`에 추가했고, 최신 SQL 재실행까지 완료했습니다.

Supabase rate limit 조정 후 테스트 회원가입과 `profiles` 자동 생성까지 확인했습니다.

Week 1 핵심 인증 흐름은 완료되었습니다.

다음 작업은 Week 1 마감 점검입니다. 전체 체크리스트를 확인한 뒤 남은 항목이 없으면 Week 2의 프로젝트 등록/갤러리/상세 페이지 구현으로 넘어갑니다.

Supabase 설정 절차는 `docs/SUPABASE_SETUP.md`에 정리되어 있습니다.
