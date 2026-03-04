"""
Sentiment analysis engine for AI BI Copilot.

Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) to classify
customer review text.

Usage::

    from modules.sentiment_engine import analyze_reviews_df, get_sentiment_summary
"""

import sys
from pathlib import Path

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Support running this file directly as a script
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """Analyse the sentiment of a single *text* string using VADER.

    Parameters
    ----------
    text:
        The review or comment string to analyse.

    Returns
    -------
    dict
        ``{"compound": float, "label": "positive" | "neutral" | "negative"}``
    """
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return {"compound": round(compound, 4), "label": label}


def analyze_reviews_df(df: pd.DataFrame) -> pd.DataFrame:
    """Add ``sentiment_score`` and ``sentiment_label`` columns to *df*.

    Parameters
    ----------
    df:
        DataFrame containing at minimum a ``review_text`` column.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with two additional columns appended.
    """
    results = df["review_text"].apply(analyze_sentiment)
    df = df.copy()
    df["sentiment_score"] = results.apply(lambda r: r["compound"])
    df["sentiment_label"] = results.apply(lambda r: r["label"])
    return df


def get_sentiment_summary(df: pd.DataFrame) -> dict:
    """Return aggregate sentiment statistics for a reviews DataFrame.

    The input DataFrame must have already been processed by
    :func:`analyze_reviews_df` (i.e. it must contain ``sentiment_label`` and
    ``sentiment_score`` columns).

    Parameters
    ----------
    df:
        Processed reviews DataFrame.

    Returns
    -------
    dict
        Keys: ``counts`` (dict), ``percentages`` (dict),
        ``avg_score_by_category`` (dict).
    """
    total = len(df)
    counts = df["sentiment_label"].value_counts().to_dict()
    percentages = {k: round(v / total * 100, 2) for k, v in counts.items()}
    avg_score_by_category = (
        df.groupby("product_category")["sentiment_score"]
        .mean()
        .round(4)
        .to_dict()
    )
    return {
        "counts": counts,
        "percentages": percentages,
        "avg_score_by_category": avg_score_by_category,
    }


if __name__ == "__main__":
    from modules.db import run_query

    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading reviews …")
    reviews = run_query("SELECT * FROM customer_reviews")
    enriched = analyze_reviews_df(reviews)

    summary = get_sentiment_summary(enriched)
    print("\n💬 Sentiment Summary")
    print(f"   Counts      : {summary['counts']}")
    print(f"   Percentages : {summary['percentages']}")
    print("\n   Avg score by category:")
    for cat, score in summary["avg_score_by_category"].items():
        print(f"     {cat}: {score}")

    out_path = output_dir / "sentiment_results.csv"
    enriched.to_csv(out_path, index=False)
    print(f"\n✅ Results saved to {out_path}")
