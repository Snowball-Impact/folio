# PaaS 배포 운영 절차

FOLIO의 운영 배포 기준은 Streamlit Community Cloud 자동 배포에서 Docker 기반 PaaS 배포로 전환한다. 앱은 계속 Streamlit으로 실행하지만, 런타임은 직접 관리하는 컨테이너가 된다.

## 1. 권장 방향

1. 저장소 루트의 `Dockerfile`로 이미지를 빌드한다.
2. PaaS는 Dockerfile 또는 컨테이너 이미지를 지원하는 Web Service로 생성한다.
3. 서비스는 HTTP 포트를 `0.0.0.0`에 바인딩한다.
4. PaaS가 `PORT` 환경 변수를 제공하면 그 값을 사용하고, 없으면 기본 `8501`을 사용한다.
5. Supabase DB/RLS 적용과 앱 배포는 계속 별도 배포 단위로 관리한다.

이 구조는 Render, Fly.io, Railway 같은 PaaS에 모두 이식하기 쉽다. 특정 플랫폼 기능에 묶이는 설정 파일은 플랫폼이 확정된 뒤 추가한다.

## 2. 컨테이너 구성

`Dockerfile`은 다음을 포함한다.

- Python 3.12 slim 런타임
- `requirements.txt` 기반 Python 의존성
- 서버 측 썸네일 캡처용 시스템 Chromium
- 한국어 렌더링을 위한 Noto CJK 폰트
- `CHROME_BINARY_PATH=/usr/bin/chromium`
- Streamlit health check: `/_stcore/health`
- 실행 명령: `streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}`

로컬 이미지 빌드:

```powershell
docker build -t folio .
```

로컬 컨테이너 실행:

```powershell
docker run --rm -p 8501:8501 --env-file .env folio
```

확인:

```powershell
curl http://localhost:8501/_stcore/health
```

## 3. PaaS 환경 변수

PaaS에는 `.env` 파일을 올리지 않고, 플랫폼의 Environment Variables 또는 Secrets에 아래 값을 등록한다.

필수:

```text
SUPABASE_URL
SUPABASE_PUBLISHABLE_KEY
APP_URL
COOKIE_PASSWORD
```

운영 권장:

```text
GA_MEASUREMENT_ID
SUPABASE_SERVICE_ROLE_KEY
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_FROM_EMAIL
SMTP_FROM_NAME
SMTP_USE_TLS
THUMBNAIL_STORAGE_BUCKET
```

Power BI 게시/임베드:

```text
POWERBI_TENANT_ID
POWERBI_CLIENT_ID
POWERBI_CLIENT_SECRET
POWERBI_WORKSPACE_ID
POWERBI_API_BASE_URL
PBIX_MAX_UPLOAD_MB
POWERBI_IMPORT_POLL_SECONDS
POWERBI_CAPTURE_READY_WAIT_SECONDS
```

컨테이너 기본값이 있으므로 보통 직접 설정하지 않아도 되는 값:

```text
CHROME_BINARY_PATH=/usr/bin/chromium
```

## 4. Supabase Auth URL

PaaS 도메인이 확정되면 Supabase Dashboard의 Authentication > URL Configuration을 갱신한다.

- Site URL: `https://your-paas-domain`
- Redirect URLs:
  - `https://your-paas-domain`
  - `https://your-paas-domain/?page=Login&verified=1`
  - `https://your-paas-domain/?page=Login&reset=1`

`APP_URL`도 같은 도메인으로 설정한다.

## 5. 플랫폼별 메모

### Render

- Web Service는 public HTTP 앱에 맞다.
- Dockerfile 기반 배포를 사용한다.
- 서비스는 `0.0.0.0`에 바인딩해야 한다.
- Render의 기본 포트는 `10000`이며, `PORT` 환경 변수 또는 서비스 설정으로 포트를 전달할 수 있다.

### Fly.io

- Streamlit 앱을 컨테이너 이미지로 배포하는 흐름이 자연스럽다.
- `fly launch`로 `fly.toml`을 생성한 뒤 필요한 리전, 메모리, 동시성 값을 조정한다.
- 앱 메모리는 최소 1GB부터 시작해 PBIX 처리와 Chromium 캡처 중 메모리 사용량을 보고 조정한다.

### Railway

- Dockerfile 또는 빌드팩 기반 배포가 가능하다.
- Dockerfile을 사용할 때 start command에서 환경 변수 확장이 필요하면 shell form을 사용한다.
- 현재 Dockerfile은 자체 `CMD`에서 `${PORT:-8501}`를 처리한다.

## 6. 배포 체크리스트

1. `python -m unittest discover -s tests` 통과.
2. `python -m pyflakes folio_app app.py tests` 통과.
3. `docker build -t folio .` 성공.
4. `docker run --rm -p 8501:8501 --env-file .env folio`로 로컬 컨테이너 기동.
5. `/_stcore/health`가 정상 응답.
6. 로그인, 공개 프로젝트 목록, 상세, 댓글, 신고 접수 확인.
7. 자동 썸네일 캡처를 쓰는 경우 Supabase Storage에 파일 생성 확인.
8. PaaS 도메인으로 `APP_URL`과 Supabase Auth URL 갱신.
9. 배포 후 푸터 버전과 실제 커밋 확인.

## 7. 운영 판단 기준

- Streamlit Cloud의 sleep/cold start 영향이 줄어드는지 본다.
- Chromium 자동 캡처가 재현 가능하게 동작하는지 본다.
- 메모리 부족이나 request timeout이 PBIX 게시/캡처에 영향을 주는지 본다.
- 커스텀 도메인, 로그, 재시작, 롤백, 환경 변수 변경이 운영자가 감당 가능한지 본다.
- 비용은 무료 한도보다 안정성을 우선한다. 실제 플랫폼과 인스턴스 크기는 트래픽과 캡처/PBIX 사용량을 본 뒤 확정한다.

## 8. TODO: SvelteKit 전환 검토

Streamlit 유지 배포와 별개로, 장기적으로 공개 사용자 화면을 SvelteKit으로 전환하는 옵션을 검토한다. 목적은 첫 로딩 속도, 상세 페이지 전환 속도, 모바일 UI, 커스텀 도메인 운영, 커뮤니티/Admin 확장성을 개선하는 것이다.

### 후보 운영 구조

권장 후보:

```text
도메인 구매처: 가비아/후이즈/Namecheap 등
DNS/SSL/보안: Cloudflare DNS
공개 웹앱: SvelteKit + Cloudflare Pages
데이터/Auth: Supabase 유지
브라우저 캡처: Cloudflare Browser Rendering 또는 Fly.io/Cloud Run 전용 API
```

대안:

- `SvelteKit + Vercel + 캡처 API 별도`: 프론트엔드 개발 경험은 좋지만 Chromium 캡처는 별도 서버를 권장한다.
- `SvelteKit + Fly.io 단일 서버`: 앱과 캡처를 한 서버에서 처리하기 쉽지만 CDN형 프론트보다 글로벌 정적 전달 이점은 작다.
- `SvelteKit + Cloud Run 단일 서버`: 컨테이너 자유도는 높지만 도메인/비용/콜드스타트 관리가 상대적으로 무겁다.

### 예상 리소스

| 범위 | 예상 기간 | 설명 |
|---|---:|---|
| 공개 화면만 전환 | 1~2주 | 홈, 갤러리, 상세, Power BI 콘텐츠 조회 |
| 사용자 기능 포함 | 3~5주 | 로그인, 좋아요, 댓글, 신고, 알림, 마이페이지 |
| 프로젝트 등록/수정 포함 | 5~7주 | 폼, 임시저장, 썸네일, 검증, 업로드까지 이전 |
| 관리자/수집/운영까지 정리 | 7~10주+ | 관리자 페이지, 콘텐츠 업데이트, 캡처 워커, 배포 자동화 |

### 주요 리스크

- Supabase Auth를 Streamlit `session_state`/쿠키 복구 방식에서 브라우저/SSR 기준으로 다시 설계해야 한다.
- RLS를 유지하면서 클라이언트 직접 조회와 서버 전용 API 범위를 명확히 나눠야 한다.
- 프로젝트 등록/수정 폼은 현재 UI와 상태 관리가 가장 복잡해 재구현 비용이 크다.
- 썸네일 자동 캡처는 Svelte 앱 내부가 아니라 별도 Worker/API로 분리해야 안정적이다.
- 댓글, 알림, 신고는 권한 체크와 읽음 처리 흐름을 다시 검증해야 한다.
- `st.cache_data`, `st.session_state`, `st.rerun()`에 기대는 화면 상태와 캐시를 SvelteKit 로딩 함수, 브라우저 상태, 서버 캐시로 옮겨야 한다.

### 권장 진행 순서

1. 별도 브랜치와 앱 디렉터리에서 SvelteKit 스파이크를 만든다.
2. 공개 조회 화면부터 이전한다: 홈, 갤러리, 상세, Power BI 콘텐츠.
3. Supabase Auth와 RLS 접근 방식을 검증한다.
4. 좋아요, 댓글, 신고, 알림을 이전한다.
5. 프로젝트 등록/수정과 썸네일 캡처를 이전한다.
6. 캡처는 Cloudflare Browser Rendering을 먼저 검토하고, 인증 또는 Chromium 제약이 크면 Fly.io/Cloud Run 전용 Playwright 워커로 분리한다.
7. Streamlit 앱은 전환 기간 동안 운영 백업으로 유지한다.
