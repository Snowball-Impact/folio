# Svelte RUM 연동 계약

기준일: 2026-08-29

## 활성화

배포 환경에 `PUBLIC_RUM_ENDPOINT`를 설정하면 `src/lib/rum.ts`가 브라우저에서 RUM 이벤트를 전송한다. 값이 비어 있으면 관측성 코드는 초기화되지 않는다.

```env
PUBLIC_RUM_ENDPOINT=https://rum.example.com/v1/events
```

## 이벤트 형식

모든 이벤트는 다음 공통 필드를 포함한다.

```json
{
  "source": "folio-svelte",
  "path": "/projects/example",
  "timestamp": "2026-08-29T00:00:00.000Z",
  "type": "web-vitals"
}
```

`web-vitals` 이벤트는 `lcp`(ms), `cls`, `inp`(ms)를 추가한다. 값이 관측되지 않은 지표는 `null`이다.

`powerbi` 이벤트는 `status`(`ready` 또는 `error`)와 `durationMs`를 추가한다. Power BI 외부 iframe 자체의 네트워크 리소스는 브라우저 보안 경계상 별도 전송하지 않고, 앱이 측정한 초기화 시간만 기록한다.

## Endpoint 요구사항

- `POST` 요청을 수락한다.
- `sendBeacon` 요청의 `text/plain;charset=UTF-8` body와 fallback `application/json` body를 모두 JSON으로 파싱한다.
- 브라우저 origin에 대해 CORS를 허용한다.
- 인증 토큰이나 사용자 식별자를 요구하지 않는다. 현재 payload에는 세션 ID, 이메일, 프로젝트 제목을 포함하지 않는다.
- 수집 실패는 사용자 화면에 노출하지 않고 브라우저에서 무시한다.

## 배포 검증

1. staging endpoint를 `PUBLIC_RUM_ENDPOINT`에 설정한다.
2. 공개 페이지 이동 후 pagehide/visibilitychange에서 `web-vitals` 수신을 확인한다.
3. Power BI 상세 페이지에서 `powerbi` 이벤트의 `ready`/`durationMs` 수신을 확인한다.
4. endpoint 미설정 환경에서 외부 POST가 발생하지 않는지 확인한다.

현재 저장소에서는 endpoint 미설정 기본 동작과 Power BI Performance measure 생성을 검증했다. 실제 endpoint 수신 검증은 staging URL이 준비된 후 수행한다.
