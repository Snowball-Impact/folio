# FOLIO Week 1 구축 체크리스트

Week 1 범위는 Streamlit 앱 뼈대, Supabase 연결, 인증, 프로필, 기본 화면 구성이다.

## 1. 프로젝트 초기 구조

- [x] Streamlit 진입점 생성: `app.py`
- [x] 앱 패키지 구조 생성: `folio_app/`
- [x] 페이지, 컴포넌트, 서비스 계층 분리
- [x] 의존성 파일 생성: `requirements.txt`
- [x] Git 제외 파일 설정: `.gitignore`

## 2. 환경 설정

- [x] Supabase 환경 변수 예시 파일 생성: `.env.example`
- [x] 실제 `.env` 파일 생성
- [x] Streamlit 테마 설정: `.streamlit/config.toml`
- [x] `st.set_page_config()`를 엔트리 파일 최상단에서 먼저 호출하도록 정리

## 3. Supabase 연동 기반

- [x] Supabase client 생성 유틸 구현
- [x] 환경 변수 로딩 설정
- [x] Supabase 미설정 상태 안내 처리
- [x] JWT expired 발생 시 public read를 anon client로 복구하는 로직 추가

## 4. 인증 기능

- [x] 회원가입 서비스 구현
- [x] 로그인 서비스 구현
- [x] 로그아웃 서비스 구현
- [x] Streamlit session state 기반 로그인 상태 관리
- [x] 암호화 쿠키 기반 새로고침 후 로그인 유지
- [x] 로그아웃 시 쿠키 token 삭제
- [x] 이메일 정규화 및 형식 검증
- [x] 비밀번호 최소 8자 검증
- [x] 비밀번호 확인 입력
- [x] 이름과 소속 필수 입력 처리
- [x] 이미 가입된 이메일 회원가입 차단
- [x] 인증 메일 재발송 기능
- [x] 인증 메일 재발송 60초 쿨다운
- [x] 인증 완료 후 Login 페이지 이동 처리

## 5. 프로필 기능

- [x] `profiles` upsert 서비스 구현
- [x] `profiles` 조회 서비스 구현
- [x] Auth 사용자 생성 시 `profiles` 자동 생성 트리거 작성
- [x] Profile 화면에서 사용자 기본 정보와 통계 표시

## 6. Week 1 화면

- [x] Home
- [x] Gallery
- [x] Login
- [x] Sign Up
- [x] About
- [x] Submit
- [x] My Portfolio
- [x] Profile
- [x] 로그인 상태에 따른 메뉴 분기

## 7. DB 스키마

- [x] `profiles` 테이블 SQL 작성
- [x] `projects` 테이블 SQL 작성
- [x] `likes` 테이블 SQL 작성
- [x] 조회수 증가 RPC 작성: `increment_project_view_count`
- [x] 기본 index 작성
- [x] RLS 활성화 및 정책 작성
- [x] Supabase SQL Editor에서 최신 `supabase/schema.sql` 실행

## 8. 로컬 실행 및 검증

- [x] 의존성 설치
- [x] Streamlit 서버 실행
- [x] 로컬 HTTP 응답 확인: `http://localhost:8501`
- [x] 브라우저에서 인증 흐름 확인

## 현재 상태

Week 1 핵심 범위는 완료되었다.

이 문서는 완료 기록으로 유지한다. 현재 작업 기준과 최신 UX 상태는 `docs/PROJECT_CONTEXT.md`를 우선 참고한다.
