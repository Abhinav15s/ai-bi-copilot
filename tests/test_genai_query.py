"""Unit tests for modules.genai_query (offline / no API key required)."""
from modules.genai_query import _extract_sql_query, ask_question


def test_extract_sql_query_plain():
    raw = "SELECT * FROM transactions;"
    result = _extract_sql_query(raw)
    assert "SELECT" in result.upper()


def test_extract_sql_query_strips_code_fence():
    raw = "```sql\nSELECT * FROM transactions\n```"
    result = _extract_sql_query(raw)
    assert "```" not in result
    assert "SELECT" in result.upper()


def test_extract_sql_query_strips_sqlquery_marker():
    raw = "SQLQuery: SELECT * FROM transactions"
    result = _extract_sql_query(raw)
    assert "SQLQuery:" not in result
    assert "SELECT" in result.upper()


def test_extract_sql_query_strips_answer_suffix():
    raw = "SELECT * FROM transactions;\nSQLResult: 1200\nAnswer: There are 1200 transactions."
    result = _extract_sql_query(raw)
    assert "Answer:" not in result
    assert "SQLResult:" not in result


def test_ask_question_no_api_key(monkeypatch):
    """ask_question should return a warning string when no API key is set."""
    monkeypatch.setenv("GROQ_API_KEY", "")
    # Reset the module-level chain cache so it re-evaluates
    import modules.genai_query as gq
    gq._chain_cache = None
    result = ask_question("How many transactions are there?")
    assert isinstance(result, str)
    assert "unavailable" in result.lower() or "⚠️" in result


def test_extract_sql_query_ends_with_semicolon():
    raw = "SELECT COUNT(*) FROM transactions"
    result = _extract_sql_query(raw)
    assert result.endswith(";")
