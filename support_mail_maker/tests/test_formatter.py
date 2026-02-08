import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock
from formatter import Formatter, Item, ItemType


class TestFormatterInit:
    def test_valid_date_parsing(self):
        f = Formatter(publish_date="2025-06-15")
        assert f.publish_date == datetime(2025, 6, 15)

    def test_publish_date_formatted_in_context(self):
        f = Formatter(publish_date="2025-03-15")
        assert f.context["publish_date"] == "03/15/2025"

    def test_context_has_empty_content_lists(self):
        f = Formatter(publish_date="2025-01-01")
        content = f.context["content"]
        assert content["issues"] == []
        assert content["oops"] == []
        assert content["wins"] == []
        assert content["news"] == []

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
        # raw_content_data has 5 items but 1 is excluded (❌)
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
                "include": "❌",
            }
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
                "include": "✅",
            }
        ]
        formatter.set_raw_content(data)

        # Mock valid_JSON_input to raise ValidationError
        from jsonschema import ValidationError
        with patch("formatter.valid_JSON_input", side_effect=ValidationError("invalid")):
            result = await formatter.send_to_press_async()
            assert result is False
