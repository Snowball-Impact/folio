import unittest
from datetime import UTC, datetime

from folio_app.components.home_gallery import _rail_title_html
from folio_app.components.portfolio_items import portfolio_item_html
from folio_app.components.ui import _cover_variant, render_project_card_html


class HomeGalleryRailTests(unittest.TestCase):
    def test_rail_title_highlights_key_words(self) -> None:
        self.assertIn(
            '<span class="folio-gallery-rail-highlight">새로 공개</span>된 프로젝트',
            _rail_title_html("recent", "새로 공개된 프로젝트를 먼저 살펴보세요."),
        )
        self.assertIn(
            '<span class="folio-gallery-rail-highlight">조회수</span>가 높은 프로젝트',
            _rail_title_html("views", "조회수가 높은 프로젝트를 빠르게 훑어보세요."),
        )
        self.assertIn(
            '<span class="folio-gallery-rail-highlight">좋아요</span>를 많이 받은 프로젝트',
            _rail_title_html("likes", "좋아요를 많이 받은 프로젝트를 확인해보세요."),
        )

    def test_rail_title_escapes_unhighlighted_text(self) -> None:
        rendered = _rail_title_html("custom", "위험 <script>")

        self.assertEqual(rendered, "위험 &lt;script&gt;")


class AutomaticProjectCoverTests(unittest.TestCase):
    def test_same_project_always_uses_same_cover_variant(self) -> None:
        project = {"id": "project-123", "title": "분석 프로젝트"}
        self.assertEqual(_cover_variant(project), _cover_variant(dict(project)))

    def test_card_contains_four_tags_and_more_count_tooltip(self) -> None:
        project = {
            "id": "project-123",
            "title": "고객 <이탈> 분석",
            "tags": ["Python", "고객&분석", "세 번째", "네 번째", "다섯 번째"],
            "one_liner": "프로젝트 설명",
        }

        rendered = render_project_card_html(project)

        self.assertIn("고객 &lt;이탈&gt; 분석", rendered)
        self.assertIn("#Python", rendered)
        self.assertIn("#고객&amp;분석", rendered)
        self.assertIn("#세 번째", rendered)
        self.assertIn("#네 번째", rendered)
        self.assertIn("+1", rendered)
        self.assertIn('title="Python, 고객&amp;분석, 세 번째, 네 번째, 다섯 번째"', rendered)
        self.assertNotIn("#다섯 번째", rendered)
        self.assertEqual(rendered.count("고객 &lt;이탈&gt; 분석"), 1)
        self.assertIn('aria-label="조회수 0"', rendered)
        self.assertIn('aria-label="좋아요 0"', rendered)
        self.assertIn('aria-label="댓글 0"', rendered)
        self.assertNotIn("조회 0 · 좋아요 0", rendered)

    def test_card_keeps_summary_and_empty_tag_zones_separate(self) -> None:
        project = {
            "id": "project-no-tags",
            "title": "태그 없는 프로젝트",
            "one_liner": "요약만 있는 프로젝트",
            "tags": [],
        }

        rendered = render_project_card_html(project)

        self.assertIn("folio-home-card-summary-zone", rendered)
        self.assertIn("folio-home-card-tags-zone", rendered)
        self.assertIn("요약만 있는 프로젝트", rendered)
        self.assertNotIn("folio-home-card-tags\"><span", rendered)

    def test_card_cover_omits_generic_portfolio_eyebrow(self) -> None:
        project = {
            "id": "project-cover-copy",
            "title": "간결한 커버 프로젝트",
        }

        rendered = render_project_card_html(project)

        self.assertNotIn("PROJECT PORTFOLIO", rendered)

    def test_card_uses_thumbnail_image_when_available(self) -> None:
        project = {
            "id": "project-thumbnail",
            "title": "썸네일 프로젝트",
            "thumbnail_url": "https://example.com/thumb.png",
        }

        rendered = render_project_card_html(project)

        self.assertIn("folio-home-card-has-thumbnail", rendered)
        self.assertIn("folio-home-card-cover-image", rendered)
        self.assertIn('src="https://example.com/thumb.png"', rendered)
        self.assertIn('alt="썸네일 프로젝트 대표 이미지"', rendered)
        self.assertIn("folio-home-card-overlay", rendered)
        self.assertIn("썸네일 프로젝트", rendered)
        self.assertNotIn("folio-auto-cover", rendered)

    def test_card_uses_data_image_thumbnail_for_local_preview(self) -> None:
        project = {
            "id": "project-thumbnail-preview",
            "title": "업로드 미리보기",
            "thumbnail_url": "data:image/png;base64,aW1hZ2U=",
        }

        rendered = render_project_card_html(project)

        self.assertIn("folio-home-card-has-thumbnail", rendered)
        self.assertIn('src="data:image/png;base64,aW1hZ2U="', rendered)
        self.assertNotIn("folio-auto-cover", rendered)

    def test_card_falls_back_to_auto_cover_for_invalid_thumbnail(self) -> None:
        project = {
            "id": "project-invalid-thumbnail",
            "title": "잘못된 썸네일 프로젝트",
            "thumbnail_url": "javascript:alert(1)",
        }

        rendered = render_project_card_html(project)

        self.assertIn("folio-auto-cover", rendered)
        self.assertNotIn("folio-home-card-has-thumbnail", rendered)
        self.assertNotIn("folio-home-card-cover-image", rendered)

    def test_author_organization_is_shown_when_present(self) -> None:
        project = {
            "id": "project-456",
            "title": "제목",
            "author": {"name": "홍길동", "organization": "스노우볼"},
        }

        rendered = render_project_card_html(project)

        self.assertIn("홍길동 · 스노우볼", rendered)

    def test_author_line_falls_back_to_name_only_without_organization(self) -> None:
        project = {
            "id": "project-789",
            "title": "제목",
            "author": {"name": "홍길동"},
        }

        rendered = render_project_card_html(project)

        self.assertIn(">홍길동<", rendered)
        self.assertNotIn(" · ", rendered)

    def test_card_omits_hover_preview_without_preview_url(self) -> None:
        project = {
            "id": "project-no-preview",
            "title": "미리보기 없는 프로젝트",
        }

        rendered = render_project_card_html(project)

        self.assertNotIn("folio-home-card-has-preview", rendered)
        self.assertNotIn("folio-home-card-preview", rendered)
        self.assertNotIn("data-folio-preview-src", rendered)

    def test_card_shows_activity_badge_for_recent_project(self) -> None:
        project = {
            "id": "project-recent",
            "title": "새 프로젝트",
            "created_at": datetime.now(UTC).isoformat(),
        }

        rendered = render_project_card_html(project)

        self.assertIn("folio-home-card-activity-badge", rendered)
        self.assertIn(">NEW</span>", rendered)

    def test_card_shows_comment_activity_badge_for_recent_comment(self) -> None:
        project = {
            "id": "project-comment-recent",
            "title": "댓글이 달린 프로젝트",
            "created_at": "2020-01-01T00:00:00+00:00",
            "latest_comment_at": datetime.now(UTC).isoformat(),
        }

        rendered = render_project_card_html(project)

        self.assertIn("folio-home-card-activity-badge", rendered)
        self.assertIn("댓글 NEW", rendered)

    def test_portfolio_item_shows_new_badge_for_unread_comments(self) -> None:
        project = {
            "id": "project-unread",
            "title": "댓글 달린 프로젝트",
            "tags": [],
            "has_unread_comments": True,
        }

        rendered = portfolio_item_html(project)
        self.assertIn("folio-portfolio-card-new-badge", rendered)
        self.assertIn("NEW", rendered)

    def test_portfolio_item_shows_powerbi_processing_status_badge(self) -> None:
        project = {
            "id": "project-processing",
            "title": "처리 중 프로젝트",
            "tags": [],
            "status": "processing",
        }

        rendered = portfolio_item_html(project)

        self.assertIn("folio-portfolio-card-status-badge", rendered)
        self.assertIn("처리 중", rendered)

    def test_portfolio_item_shows_powerbi_failed_status_badge(self) -> None:
        project = {
            "id": "project-failed",
            "title": "실패 프로젝트",
            "tags": [],
            "status": "failed",
        }

        rendered = portfolio_item_html(project)

        self.assertIn("folio-portfolio-card-status-badge", rendered)
        self.assertIn("게시 실패", rendered)


if __name__ == "__main__":
    unittest.main()
