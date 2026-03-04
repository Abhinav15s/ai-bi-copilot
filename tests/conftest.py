"""Shared pytest fixtures for AI BI Copilot tests."""
import pandas as pd
import pytest


@pytest.fixture()
def sample_reviews_df():
    return pd.DataFrame({
        "review_text": [
            "Excellent product, exceeded all expectations!",
            "Very disappointed with the product quality.",
            "Product works as described, nothing special.",
            "Outstanding support team, will definitely buy again.",
            "Numerous bugs and the documentation is poor.",
        ],
        "product_category": ["Electronics", "Software", "Services", "Hardware", "Consulting"],
        "customer_segment": ["Enterprise", "SMB", "Startup", "Government", "Enterprise"],
        "rating": [5, 1, 3, 5, 2],
    })


@pytest.fixture()
def sample_events_df():
    from datetime import datetime, timedelta
    rows = []
    base = datetime(2024, 1, 1, 9, 0)
    for case_id in ["case-001", "case-002", "case-003"]:
        ts = base
        for activity, duration in [("Order Received", 10.0), ("Credit Check", 60.0), ("Fulfillment", 120.0), ("Shipping", 300.0), ("Delivered", 20.0)]:
            rows.append({
                "case_id": case_id,
                "activity": activity,
                "timestamp": ts,
                "duration_minutes": duration,
                "resource": "Alice",
            })
            ts += timedelta(minutes=duration)
        base += timedelta(days=1)
    return pd.DataFrame(rows)
