# 비밀번호 재설정 404 장애 기록 — 2026-10-02

## 요약

- 증상: 비밀번호 찾기 메일의 재설정 링크를 누르면 404가 표시됨
- 영향: 잘못된 템플릿으로 발송된 비밀번호 재설정 메일에서 새 비밀번호 입력 화면에 진입할 수 없음
- 직접 원인: Supabase Reset password 메일 템플릿이 `{{ .RedirectTo }}&token_hash=...`를 사용함
- 조치: `&token_hash`를 `?token_hash`로 변경하고 운영 Supabase 설정에 저장함

## 원인

앱은 다음 redirect URL을 전달한다.

```text
https://folio.it.kr/reset-password
```

장애 당시 템플릿은 쿼리스트링이 없는 URL 뒤에 `&`를 붙였다.

```html
{{ .RedirectTo }}&token_hash={{ .TokenHash }}&type=recovery
```

그 결과 메일 링크가 다음 형태로 만들어졌다.

```text
https://folio.it.kr/reset-password&token_hash=...&type=recovery
```

이는 `/reset-password`의 query가 아니라 `/reset-password&token_hash=...`라는 별도 path다. 운영 환경에서 같은 형태의 경로가 HTTP 404를 반환하는 것을 재현했다.

## 점검 결과

- `https://folio.it.kr/reset-password`: HTTP 200
- `https://www.folio.it.kr/reset-password`: HTTP 200
- 잘못된 `/reset-password&token_hash=...` 형식: HTTP 404
- Supabase Site URL: `https://folio.it.kr`
- Supabase Redirect URLs에 `https://folio.it.kr/**`, `https://www.folio.it.kr/**` 등록 확인
- Cloudflare Pages 프로젝트 `folio`에 `folio.it.kr`, `www.folio.it.kr`, `folio-5l4.pages.dev` 연결 확인

따라서 앱 라우트나 Cloudflare custom domain이 아니라 이메일 템플릿의 URL 조합이 직접 원인이었다.

## 적용한 수정

2026-10-02 운영 Supabase의 **Authentication > Emails > Reset password** 템플릿을 다음과 같이 변경해 저장했다.

```html
{{ .RedirectTo }}?token_hash={{ .TokenHash }}&type=recovery
```

## 후속 확인

1. 변경 이후 새 비밀번호 재설정 메일을 요청한다.
2. 링크가 `/reset-password?token_hash=...&type=recovery`인지 확인한다.
3. 새 비밀번호 입력 화면이 표시되는지 확인한다.
4. 비밀번호 변경 후 새 비밀번호로 로그인되는지 확인한다.

기존에 발송된 메일의 잘못된 링크는 복구되지 않으므로 새 메일 요청이 필요하다.
