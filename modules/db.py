"""
Database connection helpers for AI BI Copilot.

Usage::

    from modules.db import get_engine, run_query

    df = run_query("SELECT * FROM transactions LIMIT 10")
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Path to the SQLite database, relative to this file's location
_DB_PATH = Path(__file__).parent.parent / "data" / "business_data.db"


def get_engine(db_path: Path = _DB_PATH) -> Engine:
    """Return a SQLAlchemy engine connected to the SQLite database.

    Parameters
    ----------
    db_path:
        Path to the SQLite ``.db`` file.  Defaults to ``data/business_data.db``.
    """
    return create_engine(f"sqlite:///{db_path}")


def get_connection(db_path: Path = _DB_PATH):
    """Return a raw DBAPI connection to the SQLite database.

    Parameters
    ----------
    db_path:
        Path to the SQLite ``.db`` file.
    """
    engine = get_engine(db_path)
    return engine.connect()


def run_query(sql: str, db_path: Path = _DB_PATH) -> pd.DataFrame:
    """Execute *sql* and return the result as a :class:`pandas.DataFrame`.

    Parameters
    ----------
    sql:
        SQL query string to execute.
    db_path:
        Path to the SQLite ``.db`` file.
    """
    engine = get_engine(db_path)
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)
