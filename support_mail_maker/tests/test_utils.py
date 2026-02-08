import json
import os
import pytest
from unittest.mock import patch, MagicMock
from utils import load_schema, valid_JSON_input, clear_logs, StreamToLogger, SUPPORT_MAIL_SCHEMA


class TestLoadSchema:
    def setup_method(self):
        """Reset the cached schema before each test."""
        import utils
        utils.SUPPORT_MAIL_SCHEMA = None

    def teardown_method(self):
        """Reset the cached schema after each test to avoid polluting other tests."""
        import utils
        utils.SUPPORT_MAIL_SCHEMA = None

    def test_load_schema_from_file(self):
        schema = load_schema()
        assert schema is not None
        assert isinstance(schema, dict)
        assert "$schema" in schema

    def test_schema_has_required_fields(self):
        schema = load_schema()
        assert "properties" in schema
        assert "publish_date" in schema["properties"]
        assert "content" in schema["properties"]

    def test_schema_required_list(self):
        schema = load_schema()
        assert "content" in schema["required"]
        assert "publish_date" in schema["required"]

    def test_schema_content_has_categories(self):
        schema = load_schema()
        content_props = schema["properties"]["content"]["properties"]
        assert "issues" in content_props
        assert "oops" in content_props
        assert "wins" in content_props
        assert "news" in content_props

    def test_schema_caching(self):
        """Second call should return the cached schema without re-reading the file."""
        schema1 = load_schema()
        with patch("builtins.open", side_effect=Exception("Should not read file again")):
            schema2 = load_schema()
        assert schema1 is schema2

    def test_load_schema_file_not_found_falls_back_to_url(self):
        import utils
        utils.SUPPORT_MAIL_SCHEMA = None

        mock_response = MagicMock()
        mock_response.content = json.dumps({"type": "object", "fallback": True}).encode()

        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch("utils.requests.get", return_value=mock_response) as mock_get:
                schema = load_schema(schema_path="/nonexistent/path.json")
                mock_get.assert_called_once()
                assert schema["fallback"] is True

    def test_load_schema_invalid_json_returns_empty_dict(self):
        import utils
        utils.SUPPORT_MAIL_SCHEMA = None

        with patch("builtins.open", MagicMock()):
            with patch("json.load", side_effect=json.JSONDecodeError("err", "", 0)):
                schema = load_schema()
                assert schema == {}


class TestValidJSONInput:
    def test_valid_input_returns_true(self, valid_context, valid_schema):
        result = valid_JSON_input(valid_context, valid_schema)
        assert result is True

    def test_missing_required_field_returns_false(self, valid_schema):
        invalid = {"content": {"issues": [], "oops": [], "wins": [], "news": []}}
        result = valid_JSON_input(invalid, valid_schema)
        assert result is False

    def test_missing_content_returns_false(self, valid_schema):
        invalid = {"publish_date": "2025-03-15"}
        result = valid_JSON_input(invalid, valid_schema)
        assert result is False

    def test_empty_input_returns_false(self, valid_schema):
        result = valid_JSON_input({}, valid_schema)
        assert result is False

    def test_valid_with_all_categories_populated(self, valid_schema):
        context = {
            "publish_date": "2025-03-15",
            "content": {
                "issues": [
                    {
                        "title": "Bug",
                        "customer": "Acme",
                        "summary": "A bug",
                        "item_type": "Issue",
                    }
                ],
                "oops": [
                    {
                        "title": "Oops",
                        "customer": "Beta",
                        "summary": "An oops",
                        "item_type": "Oops",
                    }
                ],
                "wins": [
                    {
                        "title": "Win",
                        "customer": "Gamma",
                        "summary": "A win",
                        "item_type": "Win",
                    }
                ],
                "news": [
                    {
                        "title": "News",
                        "customer": "Delta",
                        "summary": "Some news",
                        "item_type": "News",
                    }
                ],
            },
        }
        assert valid_JSON_input(context, valid_schema) is True

    def test_valid_with_empty_categories(self, valid_schema):
        context = {
            "publish_date": "2025-03-15",
            "content": {"issues": [], "oops": [], "wins": [], "news": []},
        }
        assert valid_JSON_input(context, valid_schema) is True

    def test_none_schema_returns_false(self):
        result = valid_JSON_input({"publish_date": "2025-01-01", "content": {}}, None)
        assert result is False

    def test_item_with_ticket_url(self, valid_schema):
        context = {
            "publish_date": "2025-03-15",
            "content": {
                "issues": [
                    {
                        "title": "Bug",
                        "customer": "Acme",
                        "summary": "A bug",
                        "item_type": "Issue",
                        "ticket_url": "https://support.example.com/tickets/1",
                    }
                ],
                "oops": [],
                "wins": [],
                "news": [],
            },
        }
        assert valid_JSON_input(context, valid_schema) is True

    def test_item_missing_required_fields_returns_false(self, valid_schema):
        context = {
            "publish_date": "2025-03-15",
            "content": {
                "issues": [
                    {
                        "title": "Bug",
                        # missing customer, summary, item_type
                    }
                ],
                "oops": [],
                "wins": [],
                "news": [],
            },
        }
        assert valid_JSON_input(context, valid_schema) is False


class TestClearLogs:
    def test_clear_logs_creates_empty_file(self, tmp_path):
        log_path = tmp_path / "main.log"
        log_path.write_text("Some log content\nMore logs\n")

        with patch("utils.log_file", str(log_path)):
            clear_logs()
        assert log_path.read_text() == ""

    def test_clear_logs_handles_missing_file(self, tmp_path):
        log_path = tmp_path / "nonexistent.log"
        with patch("utils.log_file", str(log_path)):
            # Should not raise - the function catches exceptions
            clear_logs()


class TestStreamToLogger:
    def test_write_logs_message(self):
        stream = StreamToLogger(level="INFO")
        with patch("utils.logger") as mock_logger:
            mock_opt = MagicMock()
            mock_logger.opt.return_value = mock_opt
            stream.write("Test log message")
            mock_opt.log.assert_called()

    def test_write_strips_whitespace(self):
        stream = StreamToLogger(level="WARNING")
        with patch("utils.logger") as mock_logger:
            mock_opt = MagicMock()
            mock_logger.opt.return_value = mock_opt
            stream.write("  message with spaces  \n")
            if mock_opt.log.called:
                logged_msg = mock_opt.log.call_args[0][1]
                assert logged_msg == logged_msg.rstrip()

    def test_write_empty_string_does_not_log(self):
        stream = StreamToLogger(level="INFO")
        with patch("utils.logger") as mock_logger:
            mock_opt = MagicMock()
            mock_logger.opt.return_value = mock_opt
            stream.write("")
            mock_opt.log.assert_not_called()

    def test_flush_does_not_raise(self):
        stream = StreamToLogger()
        stream.flush()  # Should not raise

    def test_default_level(self):
        stream = StreamToLogger()
        assert stream._level == "INFO"

    def test_custom_level(self):
        stream = StreamToLogger(level="ERROR")
        assert stream._level == "ERROR"

    def test_multiline_write(self):
        stream = StreamToLogger(level="INFO")
        with patch("utils.logger") as mock_logger:
            mock_opt = MagicMock()
            mock_logger.opt.return_value = mock_opt
            stream.write("line 1\nline 2\nline 3")
            assert mock_opt.log.call_count == 3
