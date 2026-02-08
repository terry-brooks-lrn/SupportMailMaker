import sys
import os
import json
import pytest

# Add the support_mail_maker package to the path so tests can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Ensure logs directory exists before utils module initializes logger
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "logs"), exist_ok=True)

from formatter import Item, ItemType, Formatter
from utils import load_schema


@pytest.fixture
def sample_item_data():
    return {
        "title": "Login timeout on SSO",
        "domain": "Authentication",
        "summary": "Users experience timeout when authenticating via SSO.",
        "customer": "Acme Corp",
        "item_type": "Issue",
        "ticket_url": "https://support.example.com/tickets/12345",
    }


@pytest.fixture
def sample_item(sample_item_data):
    return Item(**sample_item_data)


@pytest.fixture
def sample_win_item():
    return Item(
        title="Reduced response time",
        domain="Performance",
        summary="Average response time reduced by 40%.",
        customer="Beta Inc",
        item_type="Win",
        ticket_url="https://support.example.com/tickets/67890",
    )


@pytest.fixture
def sample_oops_item():
    return Item(
        title="Incorrect billing calculation",
        domain="Billing",
        summary="Monthly invoices were miscalculated for a subset of users.",
        customer="Gamma LLC",
        item_type="Oops",
    )


@pytest.fixture
def sample_news_item():
    return Item(
        title="New API endpoint launched",
        domain="Platform",
        summary="The v3 API endpoint is now available for all customers.",
        customer="All Customers",
        item_type="News",
    )


@pytest.fixture
def formatter():
    return Formatter(publish_date="2025-03-15")


@pytest.fixture
def raw_content_data():
    return [
        {
            "title": "Login timeout on SSO",
            "topic_domain": "Authentication",
            "summary": "Users experience timeout when authenticating via SSO.",
            "customer": "Acme Corp",
            "type": "Issue",
            "url": "https://support.example.com/tickets/12345",
            "include": "✅",
        },
        {
            "title": "Reduced response time",
            "topic_domain": "Performance",
            "summary": "Average response time reduced by 40%.",
            "customer": "Beta Inc",
            "type": "Win",
            "url": "https://support.example.com/tickets/67890",
            "include": "✅",
        },
        {
            "title": "Incorrect billing calculation",
            "topic_domain": "Billing",
            "summary": "Monthly invoices were miscalculated.",
            "customer": "Gamma LLC",
            "type": "Oops",
            "url": "",
            "include": "✅",
        },
        {
            "title": "New API endpoint launched",
            "topic_domain": "Platform",
            "summary": "The v3 API endpoint is now available.",
            "customer": "All Customers",
            "type": "News",
            "url": "",
            "include": "✅",
        },
        {
            "title": "Skipped item",
            "topic_domain": "Other",
            "summary": "This item should be excluded.",
            "customer": "Nobody",
            "type": "Issue",
            "url": "",
            "include": "❌",
        },
    ]


@pytest.fixture
def valid_schema():
    import utils
    # Reset cache to ensure we always load from the actual file
    saved = utils.SUPPORT_MAIL_SCHEMA
    utils.SUPPORT_MAIL_SCHEMA = None
    schema = load_schema()
    yield schema
    # Restore whatever was cached before
    utils.SUPPORT_MAIL_SCHEMA = saved


@pytest.fixture
def valid_context():
    return {
        "publish_date": "2025-03-15",
        "content": {
            "issues": [
                {
                    "title": "Login timeout",
                    "customer": "Acme Corp",
                    "summary": "Users experience timeout.",
                    "item_type": "Issue",
                }
            ],
            "oops": [],
            "wins": [],
            "news": [],
        },
    }
