import pytest
from formatter import Item, ItemType


class TestItemType:
    def test_issue_value(self):
        assert ItemType.ISSUE.value == "Issue"

    def test_win_value(self):
        assert ItemType.WIN.value == "Win"

    def test_oops_value(self):
        assert ItemType.Oops.value == "Oops"

    def test_news_value(self):
        assert ItemType.News.value == "News"

    def test_enum_members_count(self):
        assert len(ItemType) == 4

    def test_enum_iteration(self):
        values = [t.value for t in ItemType]
        assert set(values) == {"Issue", "Win", "Oops", "News"}


class TestItemCreation:
    def test_create_issue_item(self, sample_item):
        assert sample_item["title"] == "Login timeout on SSO"
        assert sample_item["topic_domain"] == "Authentication"
        assert sample_item["summary"] == "Users experience timeout when authenticating via SSO."
        assert sample_item["customer"] == "Acme Corp"
        assert sample_item["item_type"] == ItemType.ISSUE
        assert sample_item["ticket_url"] == "https://support.example.com/tickets/12345"

    def test_create_item_without_ticket_url(self):
        item = Item(
            title="Test",
            domain="General",
            summary="A test item",
            customer="Test Customer",
            item_type="Win",
        )
        assert item["ticket_url"] is None

    def test_create_item_with_each_type(self):
        for type_str, expected_enum in [
            ("Issue", ItemType.ISSUE),
            ("Win", ItemType.WIN),
            ("Oops", ItemType.Oops),
            ("News", ItemType.News),
        ]:
            item = Item(
                title="Test",
                domain="General",
                summary="Summary",
                customer="Customer",
                item_type=type_str,
            )
            assert item["item_type"] == expected_enum

    def test_create_item_case_insensitive_type(self):
        for type_str in ["issue", "ISSUE", "Issue", "iSSuE"]:
            item = Item(
                title="Test",
                domain="General",
                summary="Summary",
                customer="Customer",
                item_type=type_str,
            )
            assert item["item_type"] == ItemType.ISSUE


class TestItemValidation:
    def test_validate_valid_types(self):
        assert Item.validate_item_type("Issue") == ItemType.ISSUE
        assert Item.validate_item_type("Win") == ItemType.WIN
        assert Item.validate_item_type("Oops") == ItemType.Oops
        assert Item.validate_item_type("News") == ItemType.News

    def test_validate_case_insensitive(self):
        assert Item.validate_item_type("issue") == ItemType.ISSUE
        assert Item.validate_item_type("WIN") == ItemType.WIN
        assert Item.validate_item_type("oops") == ItemType.Oops
        assert Item.validate_item_type("NEWS") == ItemType.News

    def test_validate_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid Item Type"):
            Item.validate_item_type("Bug")

    def test_validate_empty_string_raises(self):
        with pytest.raises(ValueError, match="Invalid Item Type"):
            Item.validate_item_type("")

    def test_create_item_with_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid Item Type"):
            Item(
                title="Test",
                domain="General",
                summary="Summary",
                customer="Customer",
                item_type="InvalidType",
            )


class TestItemDictAccess:
    def test_getitem(self, sample_item):
        assert sample_item["title"] == "Login timeout on SSO"

    def test_setitem(self, sample_item):
        sample_item["title"] = "Updated Title"
        assert sample_item["title"] == "Updated Title"

    def test_setitem_validates_item_type(self, sample_item):
        sample_item["item_type"] = "Win"
        assert sample_item["item_type"] == ItemType.WIN

    def test_setitem_invalid_item_type_raises(self, sample_item):
        with pytest.raises(ValueError, match="Invalid Item Type"):
            sample_item["item_type"] = "InvalidType"

    def test_iter(self, sample_item):
        keys = list(sample_item)
        assert "title" in keys
        assert "topic_domain" in keys
        assert "summary" in keys
        assert "customer" in keys
        assert "item_type" in keys
        assert "ticket_url" in keys

    def test_getitem_missing_key_raises(self, sample_item):
        with pytest.raises(KeyError):
            _ = sample_item["nonexistent_key"]


class TestItemRepr:
    def test_repr_contains_item(self, sample_item):
        repr_str = repr(sample_item)
        assert repr_str.startswith("Item(")
        assert "Login timeout on SSO" in repr_str


class TestItemDictFormat:
    def test_in_dict_format_returns_dict(self, sample_item):
        result = sample_item.in_dict_format()
        assert isinstance(result, dict)

    def test_in_dict_format_keys(self, sample_item):
        result = sample_item.in_dict_format()
        expected_keys = {"title", "domain", "summary", "customer", "item_type", "ticket_url"}
        assert set(result.keys()) == expected_keys

    def test_in_dict_format_values(self, sample_item):
        result = sample_item.in_dict_format()
        assert result["title"] == "Login timeout on SSO"
        assert result["domain"] == "Authentication"
        assert result["summary"] == "Users experience timeout when authenticating via SSO."
        assert result["customer"] == "Acme Corp"
        assert result["item_type"] == "Issue"  # String value, not enum
        assert result["ticket_url"] == "https://support.example.com/tickets/12345"

    def test_in_dict_format_item_type_is_string(self, sample_item):
        result = sample_item.in_dict_format()
        assert isinstance(result["item_type"], str)

    def test_in_dict_format_none_ticket_url(self):
        item = Item(
            title="Test",
            domain="General",
            summary="Summary",
            customer="Customer",
            item_type="Win",
        )
        result = item.in_dict_format()
        assert result["ticket_url"] is None
