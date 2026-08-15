# Power BI Community Blog

Microsoft Fabric Community의 Power BI Community Blog RSS 기반 수집 결과입니다.

`Power BI > 커뮤니티 소식` 메뉴에서 사용합니다.

정기 운영에서는 통합 명령을 사용합니다.

```powershell
python tools\collect_powerbi_all.py
```

개별 갱신이 필요할 때는 아래 명령을 사용합니다.

```powershell
python tools\collect_powerbi_community_blog.py
```

수집 항목은 원문 제목, 한국어 제목, 한국어 요약, 작성자, 게시일, 주제, 원문 링크입니다.
개별 글 페이지의 메타데이터는 접근 제한이 있을 수 있어 기본 수집에서는 RSS 필드만 사용합니다.
