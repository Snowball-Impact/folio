# FOLIO 사용자 플로우

이 문서는 사용자가 FOLIO를 발견하고, 가입하고, 프로젝트를 포트폴리오 자산으로 축적하는 핵심 여정을 설명한다.

## 1. 전체 사용자 여정

```mermaid
flowchart LR
    Discover[Home에서 프로젝트 탐색]
    Detail[프로젝트 상세 확인]
    Signup[회원가입]
    Verify[이메일 인증]
    Login[로그인]
    Consent[약관·개인정보 동의]
    Submit[프로젝트 작성]
    Publish[공개 등록]
    Manage[My Page에서 관리]
    Engage[조회·좋아요 축적]

    Discover --> Detail
    Detail --> Signup
    Signup --> Verify --> Login --> Consent
    Consent --> Submit --> Publish
    Publish --> Discover
    Publish --> Manage
    Discover --> Engage --> Manage
```

## 2. 회원가입과 온보딩

```mermaid
sequenceDiagram
    actor U as 사용자
    participant UI as FOLIO
    participant Auth as Supabase Auth
    participant DB as PostgreSQL

    U->>UI: 회원가입 정보 입력
    UI->>UI: 이메일·비밀번호·필수값 검증
    UI->>Auth: sign_up + 사용자 metadata
    Auth->>DB: auth.users 생성
    DB->>DB: trigger로 profiles 생성
    Auth-->>U: 인증 메일 발송
    U->>Auth: 이메일 인증 링크 클릭
    U->>UI: 이메일과 비밀번호로 로그인
    UI->>DB: 활성 정책과 기존 동의 조회
    alt 동의가 필요함
        UI-->>U: 이용약관·개인정보 처리방침 표시
        U->>UI: 필수 정책 동의
        UI->>DB: user_policy_consents 저장
    end
    UI-->>U: Home 진입
```

예외 흐름:

- 이미 가입된 이메일이면 재가입 대신 인증 메일 재발송 또는 로그인을 안내한다.
- 인증 메일은 60초 재발송 제한을 둔다.
- 정책 조회 실패 시 온보딩을 우회하지 않고 재시도를 제공한다.

## 3. 로그인 유지와 만료 복구

```mermaid
flowchart TD
    Visit[앱 재접속]
    Session{session_state에 사용자 존재?}
    Cookie{암호화 쿠키에 토큰 존재?}
    Restore[Supabase set_session]
    Success{복구 성공?}
    Public[비로그인 공개 화면 유지]
    Login[Login으로 이동]
    App[인증 상태로 앱 사용]

    Visit --> Session
    Session -- 예 --> App
    Session -- 아니오 --> Cookie
    Cookie -- 아니오 --> Public
    Cookie -- 예 --> Restore --> Success
    Success -- 예 --> App
    Success -- 아니오 --> Clear[쿠키와 세션 정리]
    Clear --> Protected{보호 페이지 요청?}
    Protected -- 예 --> Login
    Protected -- 아니오 --> Public
```

## 4. 프로젝트 등록

```mermaid
flowchart TD
    Start[Submit 진입]
    Auth{로그인 상태?}
    Basic[기본 정보 입력]
    Preview[Home 카드 실시간 미리보기]
    Body[Quill로 프로젝트 리포트 작성]
    Links[BI·GitHub·ETC 링크 입력]
    Validate{필수값·URL 검증}
    Save[projects INSERT]
    Detail[등록 프로젝트 상세로 이동]

    Start --> Auth
    Auth -- 아니오 --> Login[Login 이동]
    Auth -- 예 --> Basic
    Basic <--> Preview
    Basic --> Body --> Links --> Validate
    Validate -- 실패 --> Feedback[입력 위치에 오류 표시]
    Feedback --> Basic
    Validate -- 성공 --> Save --> Detail
```

- PC에서는 기본 정보와 카드 미리보기를 2열로, 모바일에서는 1열로 배치한다.
- 리포트는 문제 정의·사용 데이터·분석 과정·핵심 인사이트 구조를 권장한다.
- 본문은 HTML 허용 목록으로 정제한 뒤 저장한다.

## 5. 공개 탐색과 상세

```mermaid
flowchart LR
    Home[Home]
    Search[검색어]
    Tag[태그 필터]
    Sort[최신·조회·좋아요 정렬]
    Card[프로젝트 카드]
    Detail[상세 리포트]
    View[세션당 조회수 1회 증가]
    Like{좋아요 클릭}

    Home --> Search --> Card
    Home --> Tag --> Card
    Home --> Sort --> Card
    Card --> Detail --> View
    Detail --> Like
    Like -- 비로그인 --> Login[Login 이동]
    Like -- 로그인 --> Toggle[좋아요 추가·취소]
```

## 6. My Page 관리

```mermaid
flowchart TD
    MyPage[My Page]
    Profile[프로필·통계]
    Portfolio[내 프로젝트 목록]
    EditProfile[프로필 편집]
    View[상세 보기]
    Edit[프로젝트 수정]
    Visibility[공개·비공개 변경]
    Delete[삭제 확인 대화상자]

    MyPage --> Profile --> EditProfile
    MyPage --> Portfolio
    Portfolio --> View
    Portfolio --> Edit --> Visibility
    Portfolio --> Delete
```

프로필과 프로젝트 관리는 하나의 My Page에 통합한다. 기존 `My Portfolio`, `Profile` URL은 호환을 위해 My Page로 리다이렉트한다.

## 7. 권한별 기능

| 기능 | 비로그인 | 로그인 사용자 | 프로젝트 작성자 |
|---|---:|---:|---:|
| 공개 프로젝트 탐색·상세 | 가능 | 가능 | 가능 |
| 조회수 증가 | 가능 | 가능 | 가능 |
| 좋아요 | Login 안내 | 가능 | 가능 |
| 프로젝트 등록 | 불가 | 가능 | 가능 |
| 비공개 프로젝트 조회 | 불가 | 본인 것만 가능 | 가능 |
| 프로젝트 수정·삭제 | 불가 | 본인 것만 가능 | 가능 |
| My Page | 불가 | 가능 | 가능 |
