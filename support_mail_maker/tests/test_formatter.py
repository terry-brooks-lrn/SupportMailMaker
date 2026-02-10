import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock
from formatter import Formatter, Item, ItemType


class TestFormatterInit:
    def test_valid_date_parsing(self):
        f = Formatter(publish_date="2025-06-15")
        assert f.publish_date == datetime(2025, 6, 15)

    def test_publish_date_is_datetime_in_context(self):
        f = Formatter(publish_date="2025-03-15")
        assert f.context["publish_date"] == datetime(2025, 3, 15)
        assert isinstance(f.context["publish_date"], datetime)

    def test_context_has_empty_content_lists(self):
        f = Formatter(publish_date="2025-01-01")
        content = f.context["content"]
        assert content["issues"] == []
        assert content["oops"] == []
        assert content["wins"] == []
        assert content["news"] == []

    def test_context_content_has_trend_html_default(self):
        f = Formatter(publish_date="2025-01-01")
        content = f.context["content"]
        assert "trend_html" in content
        assert content["trend_html"] == ""

    def test_html_starts_empty(self):
        f = Formatter(publish_date="2025-01-01")
        assert f.html == ""

    def test_markdown_starts_empty(self):
        f = Formatter(publish_date="2025-01-01")
        assert f.markdown == ""

    def test_content_data_starts_empty(self):
        f = Formatter(publish_date="2025-01-01")
        assert f.content_data == {}

    def test_invalid_date_format_raises(self):
        with pytest.raises(ValueError):
            Formatter(publish_date="15-03-2025")

    def test_invalid_date_string_raises(self):
        with pytest.raises(ValueError):
            Formatter(publish_date="not-a-date")


class TestFormatterEditionMonth:
    """Tests for edition_month context variable (one month before publish_date)."""

    def test_edition_month_is_previous_month(self):
        f = Formatter(publish_date="2025-06-15")
        edition = f.context["edition_month"]
        assert edition.month == 5
        assert edition.year == 2025

    def test_edition_month_january_wraps_to_december(self):
        f = Formatter(publish_date="2025-01-10")
        edition = f.context["edition_month"]
        assert edition.month == 12
        assert edition.year == 2024

    def test_edition_month_february_to_january(self):
        f = Formatter(publish_date="2026-02-09")
        edition = f.context["edition_month"]
        assert edition.month == 1
        assert edition.year == 2026

    def test_edition_month_december_to_november(self):
        f = Formatter(publish_date="2025-12-01")
        edition = f.context["edition_month"]
        assert edition.month == 11
        assert edition.year == 2025

    def test_edition_month_is_datetime_instance(self):
        f = Formatter(publish_date="2025-03-15")
        assert isinstance(f.context["edition_month"], datetime)

    def test_edition_month_day_overflow_safe(self):
        """March 31 -> previous month is Feb which has no 31st day.
        Using day=1 in the implementation prevents ValueError."""
        f = Formatter(publish_date="2025-03-31")
        edition = f.context["edition_month"]
        assert edition.month == 2
        assert edition.year == 2025

    def test_publish_date_unchanged_after_edition_month_calc(self):
        f = Formatter(publish_date="2025-06-15")
        assert f.context["publish_date"] == datetime(2025, 6, 15)


class TestFormatterDictAccess:
    def test_getitem_existing_attr(self, formatter):
        assert formatter["html"] == ""

    def test_getitem_nonexistent_attr_returns_none(self, formatter):
        assert formatter["nonexistent"] is None

    def test_setitem(self, formatter):
        formatter["html"] = "<p>Test</p>"
        assert formatter.html == "<p>Test</p>"

    def test_iter(self, formatter):
        attrs = list(formatter)
        assert "publish_date" in attrs
        assert "html" in attrs
        assert "markdown" in attrs
        assert "content_data" in attrs
        assert "context" in attrs


class TestFormatterAddItem:
    def test_add_issue_item(self, formatter, sample_item):
        formatter.add_item("issues", sample_item)
        assert len(formatter.context["content"]["issues"]) == 1

    def test_add_item_stores_dict_format(self, formatter, sample_item):
        formatter.add_item("issues", sample_item)
        stored = formatter.context["content"]["issues"][0]
        assert stored["title"] == "Login timeout on SSO"
        assert isinstance(stored["item_type"], str)

    def test_add_multiple_items_to_same_category(self, formatter):
        item1 = Item(
            title="Item 1", domain="D1", summary="S1",
            customer="C1", item_type="Issue",
        )
        item2 = Item(
            title="Item 2", domain="D2", summary="S2",
            customer="C2", item_type="Issue",
        )
        formatter.add_item("issues", item1)
        formatter.add_item("issues", item2)
        assert len(formatter.context["content"]["issues"]) == 2

    def test_add_items_to_different_categories(
        self, formatter, sample_item, sample_win_item, sample_oops_item, sample_news_item
    ):
        formatter.add_item("issues", sample_item)
        formatter.add_item("wins", sample_win_item)
        formatter.add_item("oops", sample_oops_item)
        formatter.add_item("news", sample_news_item)
        assert len(formatter.context["content"]["issues"]) == 1
        assert len(formatter.context["content"]["wins"]) == 1
        assert len(formatter.context["content"]["oops"]) == 1
        assert len(formatter.context["content"]["news"]) == 1


class TestFormatterGetItems:
    def test_get_items_empty(self, formatter):
        assert formatter.get_items("issues") == []

    def test_get_items_after_add(self, formatter, sample_item):
        formatter.add_item("issues", sample_item)
        items = formatter.get_items("issues")
        assert len(items) == 1
        assert items[0]["title"] == "Login timeout on SSO"


class TestFormatterSetRawContent:
    def test_set_raw_content_with_list(self, formatter, raw_content_data):
        formatter.set_raw_content(raw_content_data)
        assert formatter.content_data == raw_content_data

    def test_set_raw_content_with_string(self, formatter):
        data = '{"key": "value"}'
        formatter.set_raw_content(data)
        assert formatter.content_data == data

    def test_set_raw_content_with_empty_list(self, formatter):
        formatter.set_raw_content([])
        assert formatter.content_data == []


class TestFormatterCollateContent:
    async def test_collate_content_categorizes_items(self, formatter, raw_content_data):
        formatter.set_raw_content(raw_content_data)
        result = await formatter.collate_content()
        assert result is True
        assert len(formatter.get_items("issues")) == 1
        assert len(formatter.get_items("wins")) == 1
        assert len(formatter.get_items("oops")) == 1
        assert len(formatter.get_items("news")) == 1

    async def test_collate_content_skips_excluded_items(self, formatter, raw_content_data):
        formatter.set_raw_content(raw_content_data)
        await formatter.collate_content()
        total_items = (
            len(formatter.get_items("issues"))
            + len(formatter.get_items("wins"))
            + len(formatter.get_items("oops"))
            + len(formatter.get_items("news"))
        )
        # raw_content_data has 5 items but 1 is excluded (include=False)
        assert total_items == 4

    async def test_collate_content_empty_data(self, formatter):
        formatter.set_raw_content([])
        result = await formatter.collate_content()
        assert result is True
        assert formatter.get_items("issues") == []

    async def test_collate_content_all_excluded(self, formatter):
        data = [
            {
                "title": "Skipped",
                "topic_domain": "General",
                "summary": "Not included",
                "customer": "Nobody",
                "type": "Issue",
                "url": "",
                "include": False,
            }
        ]
        formatter.set_raw_content(data)
        result = await formatter.collate_content()
        assert result is True
        assert formatter.get_items("issues") == []

    async def test_collate_content_only_includes_true_items(self, formatter):
        """Only items with include is True should be collated; all other values are excluded."""
        data = [
            {
                "title": "Included",
                "topic_domain": "Auth",
                "summary": "Should be included",
                "customer": "Acme",
                "type": "Issue",
                "url": "",
                "include": True,
            },
            {
                "title": "Excluded False",
                "topic_domain": "Auth",
                "summary": "Should be excluded",
                "customer": "Beta",
                "type": "Issue",
                "url": "",
                "include": False,
            },
            {
                "title": "Excluded None",
                "topic_domain": "Auth",
                "summary": "None include field",
                "customer": "Gamma",
                "type": "Issue",
                "url": "",
                "include": None,
            },
            {
                "title": "Excluded Truthy String",
                "topic_domain": "Auth",
                "summary": "String 'True' is not boolean True",
                "customer": "Delta",
                "type": "Issue",
                "url": "",
                "include": "True",
            },
            {
                "title": "Excluded Zero",
                "topic_domain": "Auth",
                "summary": "Integer 0 is not True",
                "customer": "Epsilon",
                "type": "Issue",
                "url": "",
                "include": 0,
            },
        ]
        formatter.set_raw_content(data)
        await formatter.collate_content()
        assert len(formatter.get_items("issues")) == 1
        assert formatter.get_items("issues")[0]["title"] == "Included"

    async def test_collate_content_missing_include_key_is_excluded(self, formatter):
        """Items without an 'include' key should be excluded."""
        data = [
            {
                "title": "No include key",
                "topic_domain": "Auth",
                "summary": "Missing include field entirely",
                "customer": "Acme",
                "type": "Issue",
                "url": "",
            },
        ]
        formatter.set_raw_content(data)
        result = await formatter.collate_content()
        assert result is True
        assert formatter.get_items("issues") == []


class TestFormatterSaveToFile:
    async def test_save_to_file_html(self, formatter, tmp_path):
        content = "<html><body>Test</body></html>"
        with patch("formatter.pathlib.Path.cwd", return_value=tmp_path):
            path = await Formatter.save_to_file("test_output", content)
        assert path is not None
        assert path.endswith(".html")
        with open(path) as f:
            assert f.read() == content

    async def test_save_to_file_markdown(self, formatter, tmp_path):
        content = "# Test Markdown"
        with patch("formatter.pathlib.Path.cwd", return_value=tmp_path):
            path = await Formatter.save_to_file("test_output", content, file_ext="md")
        assert path is not None
        assert path.endswith(".md")
        with open(path) as f:
            assert f.read() == content

    async def test_save_to_file_custom_extension(self, formatter, tmp_path):
        content = "plain text content"
        with patch("formatter.pathlib.Path.cwd", return_value=tmp_path):
            path = await Formatter.save_to_file("test_output", content, file_ext="txt")
        assert path.endswith(".txt")


class TestFormatterSendToPress:
    async def test_send_to_press_returns_false_without_publish_date(self, formatter):
        formatter.context["publish_date"] = None
        formatter.set_raw_content([])
        result = await formatter.send_to_press_async()
        assert result is False

    async def test_send_to_press_with_valid_content(self, formatter, raw_content_data):
        formatter.set_raw_content(raw_content_data)
        formatter.context["publish_date"] = "2025-03-15"
        with patch.object(formatter, "publish_async", new_callable=AsyncMock) as mock_publish:
            result = await formatter.send_to_press_async()
            assert result is True
            mock_publish.assert_awaited_once()

    async def test_send_to_press_with_invalid_schema_returns_false(self, formatter):
        formatter.context["publish_date"] = "2025-03-15"
        # Set content that will collate but fail schema validation
        data = [
            {
                "title": "Test",
                "topic_domain": "General",
                "summary": "Summary",
                "customer": "Customer",
                "type": "Issue",
                "url": "",
                "include": True,
            }
        ]
        formatter.set_raw_content(data)

        # Mock valid_JSON_input to return False (validation failure)
        with patch("formatter.valid_JSON_input", return_value=False):
            result = await formatter.send_to_press_async()
            assert result is False

    async def test_send_to_press_does_not_publish_on_validation_failure(self, formatter):
        formatter.context["publish_date"] = "2025-03-15"
        data = [
            {
                "title": "Test",
                "topic_domain": "General",
                "summary": "Summary",
                "customer": "Customer",
                "type": "Issue",
                "url": "",
                "include": True,
            }
        ]
        formatter.set_raw_content(data)

        with patch("formatter.valid_JSON_input", return_value=False), \
             patch.object(formatter, "publish_async", new_callable=AsyncMock) as mock_publish:
            result = await formatter.send_to_press_async()
            assert result is False
            mock_publish.assert_not_awaited()
