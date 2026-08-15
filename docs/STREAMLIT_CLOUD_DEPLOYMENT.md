# Streamlit Community Cloud 배포와 캡처 실험

FOLIO의 기본 무료 배포 채널은 Streamlit Community Cloud다. 현재 목표는 기존 Streamlit 앱을 유지하면서, Community Cloud 런타임에서 Playwright 기반 썸네일 자동 캡처가 실제로 동작하는지 검증하는 것이다.

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
POWERBI_TENANT_ID = "your-tenant-id"
POWERBI_CLIENT_ID = "your-client-id"
POWERBI_CLIENT_SECRET = "your-client-secret"
POWERBI_WORKSPACE_ID = "your-workspace-id"
PBIX_MAX_UPLOAD_MB = "100"
POWERBI_IMPORT_POLL_SECONDS = "100"
POWERBI_CAPTURE_READY_WAIT_SECONDS = "10"
```

`GA_MEASUREMENT_ID`, `SUPABASE_SERVICE_ROLE_KEY`, SMTP 값은 선택 항목이다. 이메일 알림과 서버측 Storage 작업을 안정적으로 쓰려면 `SUPABASE_SERVICE_ROLE_KEY`를 설정한다.
PBIX 업로드와 Power BI Embedded Viewer를 쓰려면 `POWERBI_*` 값 4개가 필요하다. Client Secret은 Streamlit Secrets에만 둔다. PBIX 게시 직후 자동 캡처가 너무 빨리 실행되면 `POWERBI_CAPTURE_READY_WAIT_SECONDS`를 늘려 Power BI 보고서 렌더링 준비 시간을 확보한다.

## 3. Supabase Auth URL

Supabase Dashboard의 Authentication > URL Configuration에서 Streamlit Cloud 주소를 등록한다.

- Site URL: `https://your-app.streamlit.app`
- Redirect URLs:
  - `https://your-app.streamlit.app`
  - `https://your-app.streamlit.app/?page=Login&verified=1`
  - `https://your-app.streamlit.app/?page=Login&reset=1`

`APP_URL`은 이 주소와 같아야 한다.

## 4. 배포 버전 표시

앱 하단 푸터 우측에는 `folio_app/app.py`의 `APP_VERSION`이 표시된다.

- 버전 값은 일반 수정이나 로컬 테스트 때마다 올리지 않는다.
- 실제 Streamlit Cloud에 배포할 커밋을 만들 때만 갱신한다.
- 권장 형식은 날짜 기반 `vYYYY.MM.DD.N`이다. 예: `v2026.08.15.2`
- 배포 후 사용자가 변경사항 반영 여부를 확인해야 할 때 푸터 중앙 버전을 기준으로 안내한다.

배포 전 체크:

1. `APP_VERSION`을 이번 배포 버전으로 올린다.
2. `python -m unittest discover -s tests`를 통과시킨다.
3. 커밋 후 `git push origin main`으로 Streamlit Cloud 자동 재배포를 트리거한다.
4. 배포된 앱 푸터 중앙 버전이 커밋의 `APP_VERSION`과 일치하는지 확인한다.

## 5. 자동 캡처 실험

자동 캡처 기능은 `folio_app/services/project_thumbnails.py`에서 Playwright를 사용한다. Playwright managed Chromium을 먼저 실행하고, 해당 브라우저 바이너리가 준비되지 않은 환경에서는 `CHROME_BINARY_PATH`의 시스템 Chromium으로 fallback한다. 실험은 배포 앱에서 실제 프로젝트 등록 또는 수정으로 진행한다.

1. Streamlit Cloud 앱을 재부팅한다.
2. 프로젝트 등록 화면에서 썸네일 모드를 `자동 캡처`로 선택한다.
3. 캡처 가능한 `power_bi_url` 또는 `report_url`을 입력한다.
4. 등록 완료 후 메시지가 `썸네일을 자동 캡처했습니다.`를 포함하는지 확인한다.
5. Supabase Storage의 `project-thumbnails` bucket에 `projects/<project-id>/thumbnail-<timestamp>.jpg`가 생성됐는지 확인한다.
6. 홈 카드와 상세 페이지에 썸네일이 표시되는지 확인한다.
7. 같은 프로젝트를 기본 커버나 직접 URL 썸네일로 바꿨을 때 기존 `projects/<project-id>/thumbnail*` 파일이 삭제되는지 확인한다.
8. 다시 자동 캡처로 바꿨을 때 public URL에 cache-busting query가 붙고, 홈 카드에서 새 이미지가 보이는지 확인한다.

실패하면 Streamlit Cloud logs에서 아래 항목을 먼저 본다.

- Playwright 브라우저 실행 실패
- 시스템 `chromium` 실행 파일 탐색 실패
- iframe 대상 사이트의 embed 차단 또는 timeout
- Supabase Storage bucket 생성/업로드 권한 실패
- 썸네일 mode 전환 후 기존 Storage 파일 삭제 실패

### PBIX 게시 후 캡처 확인

Power BI 플랫폼에서 PBIX를 업로드하고 썸네일 모드를 `자동 캡처`로 둔 경우, Import 성공 뒤 `POWERBI_CAPTURE_READY_WAIT_SECONDS`만큼 기다린 다음 Streamlit 페이지가 아니라 Power BI report HTML을 직접 렌더링해 캡처한다.

1. 100MB 이하 PBIX를 업로드한다.
2. 등록 완료 메시지와 Power BI 게시 성공 상태를 확인한다.
3. Supabase `powerbi_reports`에 report/dataset/embed URL 메타데이터가 저장됐는지 확인한다.
4. Supabase Storage `project-thumbnails/projects/<project-id>/thumbnail-<timestamp>.jpg`가 생성됐는지 확인한다.
5. 홈 카드와 상세 히어로 우측 썸네일에 캡처 이미지가 보이는지 확인한다.

## 6. 커스텀 도메인 우회

Streamlit Community Cloud는 `*.streamlit.app` 서브도메인을 제공한다. 완전한 커스텀 도메인을 직접 연결할 수 없으면, 별도 정적 호스팅에서 전체 화면 iframe shell을 둔다.

```html
<iframe src="https://your-app.streamlit.app/?embed=true"></iframe>
```

이 방식은 주소창을 커스텀 도메인처럼 보이게 할 수 있지만, 앱의 실제 origin은 `streamlit.app`이다. 인증 redirect, 쿠키, 브라우저 iframe 정책을 배포 후 반드시 확인한다.

## 7. 한계

- Community Cloud는 무료 서비스이므로 cold start, resource limit, hibernation 영향이 있을 수 있다.
- Streamlit Cloud의 일부 서버 설정은 `.streamlit/config.toml`보다 우선한다.
- Chromium 자동 캡처는 외부 iframe 정책과 런타임 패키지 상태에 영향을 받는다.
- 캡처가 안정적이지 않으면 관리자 배치 캡처 또는 별도 캡처 worker로 분리한다.
