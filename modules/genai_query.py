"""
GenAI Query layer for AI BI Copilot.

Uses LangChain + OpenAI to translate natural language questions into SQL,
execute them against the SQLite database, and return a plain-English answer.

Usage::

    from modules.genai_query import ask_question

    answer = ask_question("Which region had the highest revenue last quarter?")

Sample questions
----------------
- "Which region had the highest revenue last quarter?"
- "What is the average cycle time for order fulfilment?"
- "Show me the top 3 product categories with the most negative customer reviews."
- "What percentage of orders were delayed by more than 2 days?"
"""

from pathlib import Path

# Load .env early so the API key is available before any LangChain import
from dotenv import load_dotenv

load_dotenv()

import os

_DB_PATH = Path(__file__).parent.parent / "data" / "business_data.db"


def _build_chain():
    """Build and return the LangChain SQL query chain.

    Returns ``None`` and prints an error message when the OpenAI API key is
    absent or when the database file does not exist.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        print("⚠️  OPENAI_API_KEY is not set.  Please copy .env.example to .env and add your key.")
        return None

    if not _DB_PATH.exists():
        print(f"⚠️  Database not found at {_DB_PATH}.  Run `python data/generate_data.py` first.")
        return None

    try:
        from langchain_community.utilities import SQLDatabase
        from langchain_openai import ChatOpenAI
        from langchain.chains import create_sql_query_chain
        from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import PromptTemplate
        from langchain_core.runnables import RunnablePassthrough
        from operator import itemgetter

        db = SQLDatabase.from_uri(f"sqlite:///{_DB_PATH}")
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        write_query = create_sql_query_chain(llm, db)
        execute_query = QuerySQLDataBaseTool(db=db)

        answer_prompt = PromptTemplate.from_template(
            """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
        )

        chain = (
            RunnablePassthrough.assign(query=write_query).assign(
                result=itemgetter("query") | execute_query
            )
            | answer_prompt
            | llm
            | StrOutputParser()
        )
        return chain
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️  Failed to build LangChain chain: {exc}")
        return None


def ask_question(question: str) -> str:
    """Translate a natural language *question* into SQL and return the answer.

    Parameters
    ----------
    question:
        A business question in plain English.

    Returns
    -------
    str
        A natural language answer, or an error message when the chain cannot
        be initialised.
    """
    chain = _build_chain()
    if chain is None:
        return (
            "⚠️  The AI query layer is unavailable.  "
            "Check that OPENAI_API_KEY is set and the database exists."
        )
    try:
        return chain.invoke({"question": question})
    except Exception as exc:  # noqa: BLE001
        return f"⚠️  Error answering question: {exc}"


if __name__ == "__main__":
    print("🤖 AI BI Copilot — Interactive Query CLI")
    print("   Type your business question and press Enter.")
    print("   Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("❓ Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue
        print(f"\n💬 Answer: {ask_question(user_input)}\n")
