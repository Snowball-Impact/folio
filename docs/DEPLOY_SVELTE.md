# Svelte (svelte_app) 배포 가이드

이 문서는 `svelte_app`을 레포의 메인 프론트엔드로 배포하는 방법을 설명합니다. 이 레포는 `svelte_app` 폴더에 SvelteKit 코드가 있으며, 우리는 Cloudflare Pages를 기본 배포 채널로 사용하도록 구성합니다.

## 자동 배포(GitHub Actions)

레포에 `.github/workflows/deploy-svelte-pages.yml` 워크플로우가 추가되어 있습니다. `main` 브랜치에 푸시되면 자동으로 다음을 수행합니다:

- `svelte_app`에서 `npm ci` 실행
- `npm run build`로 빌드
- `wrangler pages deploy .svelte-kit/cloudflare --project-name <PROJECT>`로 Cloudflare Pages에 배포

### 필요한 시크릿

GitHub 리포지토리 Settings > Secrets에 다음 시크릿을 추가하세요:

- `CLOUDFLARE_API_TOKEN`: Cloudflare API 토큰(권한: Pages > Edit, Account > Read)
- `CLOUDFLARE_PAGES_PROJECT`: Cloudflare Pages 프로젝트 이름(예: `folio`)

Cloudflare에서 Pages 프로젝트가 아직 없다면 먼저 Pages에 프로젝트를 생성하고 `Build command`는 `npm run build`, `Build directory`는 `.svelte-kit/cloudflare`로 설정해 주세요.

## 수동 배포 (로컬)

로컬에서 수동으로 배포하려면:

```bash
cd svelte_app
npm ci
npm run build
npm run deploy:cloudflare
```

`deploy:cloudflare` 스크립트는 `wrangler pages deploy .svelte-kit/cloudflare`를 실행합니다. 로컬에서 실행하려면 `wrangler`가 설치되어 있고 `CLOUDFLARE_API_TOKEN`이 환경 변수로 설정되어 있어야 합니다.

## 배포 검증

- 배포 후 Pages 도메인(또는 커스텀 도메인)에서 루트 페이지가 Svelte 애플리케이션을 제공하는지 확인합니다.
- Playwright smoke tests(간단한 E2E)를 CI로 돌려 주요 흐름을 자동 검증하도록 권장합니다.

## 참고

Streamlit 앱은 `archive/streamlit_app`로 보관되어 있습니다. 필요시 해당 폴더의 지침을 따라 Streamlit을 개별적으로 배포하거나 참조하세요.
