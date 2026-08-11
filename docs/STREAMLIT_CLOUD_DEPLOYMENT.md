# Streamlit Community Cloud 배포와 캡처 실험

FOLIO의 기본 무료 배포 채널은 Streamlit Community Cloud다. 현재 목표는 기존 Streamlit 앱을 유지하면서, Community Cloud 런타임에서 Chromium/Selenium 기반 썸네일 자동 캡처가 실제로 동작하는지 검증하는 것이다.

## 1. 배포 채널

- 배포 서비스: Streamlit Community Cloud
- 앱 진입점: 루트 `app.py`
- 기본 URL: `https://<custom-subdomain>.streamlit.app`
- 의존성:
  - Python: `requirements.txt`
  - Linux packages: `packages.txt`

루트의 `packages.txt`에는 자동 캡처를 위해 아래 패키지가 들어 있다.

```text
chromium
chromium-driver
```

## 2. Secrets

Streamlit Cloud App settings > Secrets에 아래 값을 등록한다. TOML 형식으로 입력하며 Markdown 코드 블록 없이 붙여넣는다.

```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "your-supabase-publishable-key"
APP_URL = "https://your-app.streamlit.app"
COOKIE_PASSWORD = "replace-with-a-long-random-cookie-password"
GA_MEASUREMENT_ID = "G-XXXXXXXXXX"
SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"
SMTP_HOST = "smtp.example.com"
SMTP_PORT = "587"
SMTP_USERNAME = "your-smtp-user"
SMTP_PASSWORD = "your-smtp-password"
SMTP_FROM_EMAIL = "noreply@example.com"
SMTP_FROM_NAME = "FOLIO"
SMTP_USE_TLS = "true"
THUMBNAIL_STORAGE_BUCKET = "project-thumbnails"
CHROME_BINARY_PATH = "/usr/bin/chromium"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
POWERBI_TENANT_ID = "your-tenant-id"
POWERBI_CLIENT_ID = "your-client-id"
POWERBI_CLIENT_SECRET = "your-client-secret"
POWERBI_WORKSPACE_ID = "your-workspace-id"
PBIX_MAX_UPLOAD_MB = "100"
POWERBI_IMPORT_POLL_SECONDS = "100"
```

`GA_MEASUREMENT_ID`, `SUPABASE_SERVICE_ROLE_KEY`, SMTP 값은 선택 항목이다. 이메일 알림과 서버측 Storage 작업을 안정적으로 쓰려면 `SUPABASE_SERVICE_ROLE_KEY`를 설정한다.
PBIX 업로드와 Power BI Embedded Viewer를 쓰려면 `POWERBI_*` 값 4개가 필요하다. Client Secret은 Streamlit Secrets에만 둔다.

## 3. Supabase Auth URL

Supabase Dashboard의 Authentication > URL Configuration에서 Streamlit Cloud 주소를 등록한다.

- Site URL: `https://your-app.streamlit.app`
- Redirect URLs:
  - `https://your-app.streamlit.app`
  - `https://your-app.streamlit.app/?page=Login&verified=1`
  - `https://your-app.streamlit.app/?page=Login&reset=1`

`APP_URL`은 이 주소와 같아야 한다.

## 4. 자동 캡처 실험

자동 캡처 기능은 `folio_app/services/project_thumbnails.py`에서 Selenium Chrome driver를 사용한다. 실험은 배포 앱에서 실제 프로젝트 등록 또는 수정으로 진행한다.

1. Streamlit Cloud 앱을 재부팅한다.
2. 프로젝트 등록 화면에서 썸네일 모드를 `자동 캡처`로 선택한다.
3. 캡처 가능한 `power_bi_url` 또는 `report_url`을 입력한다.
4. 등록 완료 후 메시지가 `썸네일을 자동 캡처했습니다.`를 포함하는지 확인한다.
5. Supabase Storage의 `project-thumbnails` bucket에 `projects/<project-id>/thumbnail.jpg`가 생성됐는지 확인한다.
6. 홈 카드와 상세 페이지에 썸네일이 표시되는지 확인한다.
7. 같은 프로젝트를 기본 커버나 직접 URL 썸네일로 바꿨을 때 기존 `projects/<project-id>/thumbnail.jpg`가 삭제되는지 확인한다.
8. 다시 자동 캡처로 바꿨을 때 public URL에 cache-busting query가 붙고, 홈 카드에서 새 이미지가 보이는지 확인한다.

실패하면 Streamlit Cloud logs에서 아래 항목을 먼저 본다.

- `chromium` 또는 `chromedriver` 실행 파일 탐색 실패
- Selenium session 생성 실패
- iframe 대상 사이트의 embed 차단 또는 timeout
- Supabase Storage bucket 생성/업로드 권한 실패
- 썸네일 mode 전환 후 기존 Storage 파일 삭제 실패

### PBIX 게시 후 캡처 확인

Power BI 플랫폼에서 PBIX를 업로드하고 썸네일 모드를 `자동 캡처`로 둔 경우, Import 성공 뒤 Streamlit 페이지가 아니라 Power BI report HTML을 직접 렌더링해 캡처한다.

1. 100MB 이하 PBIX를 업로드한다.
2. 등록 완료 메시지와 Power BI 게시 성공 상태를 확인한다.
3. Supabase `powerbi_reports`에 report/dataset/embed URL 메타데이터가 저장됐는지 확인한다.
4. Supabase Storage `project-thumbnails/projects/<project-id>/thumbnail.jpg`가 생성됐는지 확인한다.
5. 홈 카드와 상세 히어로 우측 썸네일에 캡처 이미지가 보이는지 확인한다.

## 5. 커스텀 도메인 우회

Streamlit Community Cloud는 `*.streamlit.app` 서브도메인을 제공한다. 완전한 커스텀 도메인을 직접 연결할 수 없으면, 별도 정적 호스팅에서 전체 화면 iframe shell을 둔다.

```html
<iframe src="https://your-app.streamlit.app/?embed=true"></iframe>
```

이 방식은 주소창을 커스텀 도메인처럼 보이게 할 수 있지만, 앱의 실제 origin은 `streamlit.app`이다. 인증 redirect, 쿠키, 브라우저 iframe 정책을 배포 후 반드시 확인한다.

## 6. 한계

- Community Cloud는 무료 서비스이므로 cold start, resource limit, hibernation 영향이 있을 수 있다.
- Streamlit Cloud의 일부 서버 설정은 `.streamlit/config.toml`보다 우선한다.
- Chromium 자동 캡처는 외부 iframe 정책과 런타임 패키지 상태에 영향을 받는다.
- 캡처가 안정적이지 않으면 관리자 배치 캡처 또는 별도 캡처 worker로 분리한다.
