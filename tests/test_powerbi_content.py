import unittest

from folio_app.services.powerbi_content import build_news_items, community_groups, learning_categories


class PowerBIContentTests(unittest.TestCase):
    def test_build_news_items_merges_update_video_by_release(self) -> None:
        updates = [
            {
                "release_label": "June 2026 update",
                "version": "2.155.756.0",
                "section": "Reporting",
                "feature_title_en": "Shape Map is generally available",
                "source_url": "https://learn.microsoft.com/update",
            }
        ]
        videos = [
            {
                "title_en": "Power BI Update - June 2026",
                "video_url": "https://youtube.com/watch?v=test",
            }
        ]

        items = build_news_items(updates, [], videos)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].label, "월간 정기 업데이트")
        self.assertEqual(items[0].title, "6월 2026 업데이트 · v2.155.756.0")
        self.assertEqual(items[0].video_row, videos[0])
        self.assertIn("Shape Map", items[0].bullets[0])

    def test_build_news_items_adds_newer_official_video_without_learn_release(self) -> None:
        updates = [
            {
                "release_label": "July 2026 update",
                "version": "2.156.951.0",
                "section": "Overview",
                "source_url": "https://learn.microsoft.com/update",
            }
        ]
        videos = [
            {
                "title_en": "Power BI Update - August 2026",
                "title_ko": "Power BI Update - August 2026",
                "summary_ko": "Power BI 실무 학습에 참고할 수 있는 영상입니다.",
                "video_url": "https://youtube.com/watch?v=august",
            },
            {
                "title_en": "Power BI Update - July 2026",
                "video_url": "https://youtube.com/watch?v=july",
            },
        ]

        items = build_news_items(updates, [], videos)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].label, "공식 업데이트 영상")
        self.assertEqual(items[0].title, "8월 2026 업데이트 공식 영상")
        self.assertEqual(items[0].source_row["source_url"], "https://youtube.com/watch?v=august")
        self.assertEqual(items[0].video_row, videos[0])
        self.assertEqual(items[1].label, "월간 정기 업데이트")
        self.assertEqual(items[1].video_row, videos[1])

    def test_build_news_items_sorts_changelog_after_newer_update(self) -> None:
        updates = [{"release_label": "June 2026 update", "section": "Overview"}]
        changelog = [
            {
                "release_label": "January 2026 QFE 1",
                "version": "2.150.2102.0",
                "released_at": "January 28, 2026",
                "fix_en": "Fixed an issue where view switcher icons were displayed incorrectly.",
            }
        ]

        items = build_news_items(updates, changelog, [])

        self.assertEqual([item.label for item in items], ["월간 정기 업데이트", "패치 로그"])
        self.assertIn("보기 전환 아이콘", items[1].bullets[0])

    def test_community_groups_keeps_all_tab_first(self) -> None:
        rows = [{"topic": "DAX", "published_at": "2026-06-01"}, {"topic": "Copilot", "published_at": "2026-07-01"}]

        groups = community_groups(rows)

        self.assertEqual(list(groups.keys())[:3], ["전체", "Copilot", "DAX"])

    def test_learning_categories_excludes_update_videos(self) -> None:
        rows = [
            {"topic": "공식 학습", "title_en": "Get started with Power BI"},
            {"topic": "공식 학습", "title_en": "Power BI Update - June 2026"},
        ]

        groups = learning_categories(rows)

        self.assertEqual(len(groups["공식 학습"]), 1)


if __name__ == "__main__":
    unittest.main()
