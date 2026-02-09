import pytest
from app import normalize_csv_rows, CSV_COLUMN_ALIASES, _ALIAS_LOOKUP, _coerce_bool


class TestCSVColumnAliases:
    """Verify that the alias map covers every required internal key and
    that real-world CSV header variants are recognised."""

    def test_all_internal_keys_present(self):
        expected_internal_keys = {"type", "include", "customer", "url",
                                  "topic_domain", "title", "summary"}
        assert set(CSV_COLUMN_ALIASES.keys()) == expected_internal_keys

    def test_alias_lookup_is_lowercased(self):
        for alias_key in _ALIAS_LOOKUP:
            assert alias_key == alias_key.lower().strip()

    @pytest.mark.parametrize("csv_header,expected_key", [
        # type aliases
        ("section", "type"),
        ("type", "type"),
        ("ticket_type", "type"),
        ("Section", "type"),
        ("TICKET_TYPE", "type"),
        # topic_domain aliases
        ("topic_domain", "topic_domain"),
        ("Topic/Domain", "topic_domain"),
        ("topic/domain", "topic_domain"),
        # title
        ("title", "title"),
        ("Title", "title"),
        # customer
        ("customer", "customer"),
        ("Customer", "customer"),
        # summary aliases
        ("summary", "summary"),
        ("subject matter/summary", "summary"),
        ("Subject Matter/Summary", "summary"),
        # url aliases
        ("ticket_link", "url"),
        ("link", "url"),
        ("Link", "url"),
        # include aliases
        ("add_to_edition", "include"),
        ("add_to_edition?", "include"),
        ("Add_To_Edition?", "include"),
        ("include", "include"),
    ])
    def test_alias_resolves_to_internal_key(self, csv_header, expected_key):
        assert _ALIAS_LOOKUP.get(csv_header.lower().strip()) == expected_key


class TestCoerceBool:
    """Tests for _coerce_bool — CSV string → Python bool conversion."""

    @pytest.mark.parametrize("value", [True, False])
    def test_bool_passthrough(self, value):
        assert _coerce_bool(value) is value

    @pytest.mark.parametrize("value", ["true", "True", "TRUE", "tRuE"])
    def test_true_string_variants(self, value):
        assert _coerce_bool(value) is True

    @pytest.mark.parametrize("value", ["1", "yes", "Yes", "YES", "✅"])
    def test_other_truthy_strings(self, value):
        assert _coerce_bool(value) is True

    @pytest.mark.parametrize("value", ["false", "False", "FALSE", "0", "no", "❌", "", "random"])
    def test_falsy_strings(self, value):
        assert _coerce_bool(value) is False

    def test_none_returns_false(self):
        assert _coerce_bool(None) is False

    def test_integer_zero_returns_false(self):
        assert _coerce_bool(0) is False

    def test_integer_one_returns_false(self):
        """Integers are not strings — _coerce_bool only accepts str/bool."""
        assert _coerce_bool(1) is False

    def test_whitespace_padded_true(self):
        assert _coerce_bool("  true  ") is True

    def test_whitespace_padded_checkmark(self):
        assert _coerce_bool(" ✅ ") is True


class TestNormalizeCSVRows:
    """Tests for normalize_csv_rows — the bridge between CSV headers and
    the internal keys that collate_content expects."""

    @pytest.fixture
    def real_world_row(self):
        """A row as csv.DictReader produces from the real production CSV."""
        return {
            "ticket_type": "Issue",
            "add_to_edition?": "TRUE",
            "owner": "Jane Doe",
            "customer": "Acme Corp",
            "link": "https://support.example.com/tickets/100",
            "Topic/Domain": "Authentication",
            "title": "Login timeout on SSO",
            "subject matter/summary": "Users experience timeout when authenticating via SSO.",
            "notes": "Internal follow-up required.",
            "": None,
            "client_number": "64",
        }

    @pytest.fixture
    def template_style_row(self):
        """A row using the upload-template header convention."""
        return {
            "section": "Win",
            "topic_domain": "Performance",
            "title": "Reduced response time",
            "customer": "Beta Inc",
            "summary": "Average response time reduced by 40%.",
            "owner": "John Smith",
            "ticket_link": "https://support.example.com/tickets/200",
            "add_to_edition": "true",
            "notes": "",
        }

    @pytest.fixture
    def real_world_rows(self, real_world_row):
        """Multiple rows simulating a realistic CSV upload."""
        return [
            real_world_row,
            {
                "ticket_type": "Win",
                "add_to_edition?": "TRUE",
                "owner": "John Smith",
                "customer": "Beta Inc",
                "link": "https://support.example.com/tickets/200",
                "Topic/Domain": "Performance",
                "title": "Reduced response time",
                "subject matter/summary": "Average response time reduced by 40%.",
                "notes": "",
                "": None,
                "client_number": "200",
            },
            {
                "ticket_type": "Oops",
                "add_to_edition?": "FALSE",
                "owner": "Alice",
                "customer": "Gamma LLC",
                "link": "",
                "Topic/Domain": "Billing",
                "title": "Incorrect billing calculation",
                "subject matter/summary": "Monthly invoices were miscalculated for a subset of users.",
                "notes": "",
                "": None,
                "client_number": "103",
            },
        ]

    def test_real_world_row_maps_all_keys(self, real_world_row):
        result = normalize_csv_rows([real_world_row])
        assert len(result) == 1
        row = result[0]
        assert row["type"] == "Issue"
        assert row["include"] is True
        assert row["customer"] == "Acme Corp"
        assert row["url"] == "https://support.example.com/tickets/100"
        assert row["topic_domain"] == "Authentication"
        assert row["title"] == "Login timeout on SSO"
        assert row["summary"] == "Users experience timeout when authenticating via SSO."

    def test_template_style_row_maps_all_keys(self, template_style_row):
        result = normalize_csv_rows([template_style_row])
        row = result[0]
        assert row["type"] == "Win"
        assert row["include"] is True
        assert row["customer"] == "Beta Inc"
        assert row["url"] == "https://support.example.com/tickets/200"
        assert row["topic_domain"] == "Performance"
        assert row["title"] == "Reduced response time"
        assert row["summary"] == "Average response time reduced by 40%."

    def test_unmapped_columns_are_dropped(self, real_world_row):
        result = normalize_csv_rows([real_world_row])
        row = result[0]
        assert "owner" not in row
        assert "notes" not in row
        assert "client_number" not in row
        assert "" not in row

    def test_multiple_rows(self, real_world_rows):
        result = normalize_csv_rows(real_world_rows)
        assert len(result) == 3
        assert result[0]["type"] == "Issue"
        assert result[1]["type"] == "Win"
        assert result[2]["type"] == "Oops"

    def test_empty_input(self):
        assert normalize_csv_rows([]) == []

    def test_missing_csv_column_defaults_to_empty_or_false(self):
        """If a CSV row is missing a mapped column, string fields default to ''
        and include defaults to False."""
        incomplete_row = {"ticket_type": "News", "customer": "Delta Corp"}
        result = normalize_csv_rows([incomplete_row])
        row = result[0]
        assert row["type"] == "News"
        assert row["customer"] == "Delta Corp"
        assert row["include"] is False
        assert row["url"] == ""
        assert row["topic_domain"] == ""
        assert row["title"] == ""
        assert row["summary"] == ""

    def test_none_values_handled(self):
        """If a CSV cell is None (can happen with DictReader), normalise gracefully."""
        row_with_none = {
            "ticket_type": "Issue",
            "Topic/Domain": None,
            "title": None,
            "customer": "Test",
            "subject matter/summary": None,
            "link": None,
            "add_to_edition?": None,
        }
        result = normalize_csv_rows([row_with_none])
        row = result[0]
        assert row["include"] is False
        assert row["url"] == ""
        assert row["topic_domain"] == ""
        assert row["title"] == ""
        assert row["summary"] == ""

    def test_include_true_coerced(self, real_world_row):
        """The 'TRUE' string in add_to_edition? must become boolean True."""
        result = normalize_csv_rows([real_world_row])
        assert result[0]["include"] is True

    def test_include_false_coerced(self, real_world_rows):
        """The 'FALSE' string in add_to_edition? must become boolean False."""
        result = normalize_csv_rows(real_world_rows)
        assert result[2]["include"] is False

    def test_include_is_always_bool(self, real_world_rows):
        """Every normalised row's include value must be a bool."""
        result = normalize_csv_rows(real_world_rows)
        for row in result:
            assert isinstance(row["include"], bool)

    def test_output_only_contains_internal_keys(self, real_world_row):
        result = normalize_csv_rows([real_world_row])
        row = result[0]
        assert set(row.keys()) == set(CSV_COLUMN_ALIASES.keys())

    def test_case_insensitive_header_matching(self):
        """Headers with mixed case should still resolve correctly."""
        row = {
            "TICKET_TYPE": "Issue",
            "ADD_TO_EDITION?": "true",
            "CUSTOMER": "Test Co",
            "LINK": "https://example.com",
            "TOPIC/DOMAIN": "Testing",
            "TITLE": "Test title",
            "SUBJECT MATTER/SUMMARY": "Test summary",
        }
        result = normalize_csv_rows([row])
        r = result[0]
        assert r["type"] == "Issue"
        assert r["include"] is True
        assert r["customer"] == "Test Co"
        assert r["url"] == "https://example.com"
        assert r["topic_domain"] == "Testing"
        assert r["title"] == "Test title"
        assert r["summary"] == "Test summary"

    @pytest.mark.parametrize("edition_value,expected", [
        ("TRUE", True),
        ("true", True),
        ("True", True),
        ("1", True),
        ("yes", True),
        ("✅", True),
        ("FALSE", False),
        ("false", False),
        ("0", False),
        ("no", False),
        ("❌", False),
        ("", False),
    ])
    def test_add_to_edition_coercion_variants(self, edition_value, expected):
        """Various CSV string values for add_to_edition? should coerce correctly."""
        row = {
            "ticket_type": "Issue",
            "Topic/Domain": "Auth",
            "title": "Test",
            "customer": "Test Co",
            "subject matter/summary": "Summary",
            "link": "",
            "add_to_edition?": edition_value,
        }
        result = normalize_csv_rows([row])
        assert result[0]["include"] is expected

    def test_none_header_key_is_skipped(self):
        """Rows from DictReader can have None as a key for extra commas."""
        row = {
            "ticket_type": "Issue",
            "customer": "Test",
            "add_to_edition?": "TRUE",
            None: "extra value",
        }
        result = normalize_csv_rows([row])
        assert result[0]["type"] == "Issue"
        assert result[0]["include"] is True


class TestNormalizeCSVRowsIntegration:
    """End-to-end: normalised CSV rows should be accepted by Formatter.collate_content."""

    @pytest.fixture
    def normalised_rows(self):
        """Rows as they would appear after normalize_csv_rows."""
        return [
            {
                "type": "Issue",
                "include": True,
                "customer": "Acme Corp",
                "url": "https://support.example.com/tickets/100",
                "topic_domain": "Authentication",
                "title": "Login timeout on SSO",
                "summary": "Users experience timeout when authenticating via SSO.",
            },
            {
                "type": "Win",
                "include": True,
                "customer": "Beta Inc",
                "url": "https://support.example.com/tickets/200",
                "topic_domain": "Performance",
                "title": "Reduced response time",
                "summary": "Average response time reduced by 40%.",
            },
            {
                "type": "Oops",
                "include": False,
                "customer": "Gamma LLC",
                "url": "",
                "topic_domain": "Billing",
                "title": "Incorrect billing calculation",
                "summary": "Monthly invoices were miscalculated.",
            },
        ]

    async def test_collate_content_with_normalised_csv_rows(self, formatter, normalised_rows):
        """Normalised CSV rows should be correctly collated by the Formatter."""
        formatter.set_raw_content(normalised_rows)
        result = await formatter.collate_content()
        assert result is True
        assert len(formatter.get_items("issues")) == 1
        assert len(formatter.get_items("wins")) == 1
        assert len(formatter.get_items("oops")) == 0  # excluded (include=False)

    async def test_collate_preserves_title_from_csv(self, formatter, normalised_rows):
        formatter.set_raw_content(normalised_rows)
        await formatter.collate_content()
        issue = formatter.get_items("issues")[0]
        assert issue["title"] == "Login timeout on SSO"

    async def test_collate_preserves_summary_from_csv(self, formatter, normalised_rows):
        formatter.set_raw_content(normalised_rows)
        await formatter.collate_content()
        issue = formatter.get_items("issues")[0]
        assert issue["summary"] == "Users experience timeout when authenticating via SSO."

    async def test_collate_preserves_domain_from_csv(self, formatter, normalised_rows):
        formatter.set_raw_content(normalised_rows)
        await formatter.collate_content()
        issue = formatter.get_items("issues")[0]
        assert issue["domain"] == "Authentication"

    async def test_full_real_world_csv_round_trip(self, formatter):
        """Simulate the complete path with real-world CSV headers."""
        raw_csv_rows = [
            {
                "ticket_type": "Issue",
                "Topic/Domain": "API Issue",
                "title": "Rate limiting too aggressive",
                "customer": "MegaCorp",
                "subject matter/summary": "API rate limits trigger at 50% of documented threshold.",
                "owner": "Dev Team",
                "link": "https://support.example.com/tickets/999",
                "add_to_edition?": "TRUE",
                "notes": "Priority fix needed.",
                "": None,
                "client_number": "42",
            },
            {
                "ticket_type": "News",
                "Topic/Domain": "Platform",
                "title": "New dashboard released",
                "customer": "All Customers",
                "subject matter/summary": "The v2 analytics dashboard is now available.",
                "owner": "Product",
                "link": "",
                "add_to_edition?": "TRUE",
                "notes": "",
                "": None,
                "client_number": "100",
            },
            {
                "ticket_type": "Oops",
                "Topic/Domain": "Billing",
                "title": "Skipped item",
                "customer": "Nobody",
                "subject matter/summary": "This should not appear.",
                "owner": "QA",
                "link": "",
                "add_to_edition?": "FALSE",
                "notes": "",
                "": None,
                "client_number": "999",
            },
        ]
        normalised = normalize_csv_rows(raw_csv_rows)
        formatter.set_raw_content(normalised)
        result = await formatter.collate_content()
        assert result is True
        assert len(formatter.get_items("issues")) == 1
        assert len(formatter.get_items("news")) == 1
        assert len(formatter.get_items("oops")) == 0
        assert formatter.get_items("issues")[0]["title"] == "Rate limiting too aggressive"
        assert formatter.get_items("news")[0]["domain"] == "Platform"

    async def test_full_template_csv_round_trip(self, formatter):
        """Simulate the complete path with template-style CSV headers."""
        raw_csv_rows = [
            {
                "section": "Issue",
                "topic_domain": "API",
                "title": "Template style issue",
                "customer": "TemplateCo",
                "summary": "A summary from the template.",
                "owner": "Dev",
                "ticket_link": "https://support.example.com/tickets/555",
                "add_to_edition": "true",
                "notes": "",
            },
        ]
        normalised = normalize_csv_rows(raw_csv_rows)
        formatter.set_raw_content(normalised)
        result = await formatter.collate_content()
        assert result is True
        assert len(formatter.get_items("issues")) == 1
        assert formatter.get_items("issues")[0]["title"] == "Template style issue"
