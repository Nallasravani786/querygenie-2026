"""
Text-to-SQL engine.

Given a natural-language question, it:
  1. Reads the live database schema (table + column names).
  2. Asks the LLM to write a single, safe SELECT query for that schema.
  3. Validates the query is read-only (blocks anything destructive).
  4. Executes it and returns the rows.

The read-only guard is important: it means the LLM can never DROP, DELETE
or UPDATE your data, even if a prompt tried to make it.
"""

from __future__ import annotations

import re
import sqlite3

from llm import chat

# Statements we refuse to run — this is a read-only assistant.
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|truncate|attach|pragma)\b",
    re.IGNORECASE,
)


def get_schema(db_path: str) -> str:
    """Return a compact text description of every table and its columns."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]

    lines = []
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        cols = [f"{c[1]} ({c[2]})" for c in cur.fetchall()]
        lines.append(f"TABLE {table}: {', '.join(cols)}")
    conn.close()
    return "\n".join(lines)


def _clean_sql(text: str) -> str:
    """Strip markdown fences / prose the model may add."""
    text = text.strip()
    # Remove ```sql ... ``` fencing if present.
    fence = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    # Keep only up to the first statement terminator.
    text = text.split(";")[0].strip()
    return text


_SYSTEM_PROMPT = (
    "You are an expert data analyst who writes SQLite SQL. "
    "Given a database schema and a question, return ONE valid SQLite SELECT "
    "query that answers it. Rules: return SQL only, no explanation; use only "
    "tables and columns from the schema; never write anything that modifies "
    "data (no INSERT/UPDATE/DELETE/DROP)."
)


def generate_sql(question: str, schema: str) -> str:
    """Ask the LLM to convert a question into a SQL query."""
    user_prompt = (
        f"Database schema:\n{schema}\n\n"
        f"Question: {question}\n\n"
        "SQLite SELECT query:"
    )
    raw = chat(
        [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )
    return _clean_sql(raw)


def is_safe(sql: str) -> bool:
    """True only if the query is a single read-only SELECT statement."""
    if not sql.lower().lstrip().startswith("select"):
        return False
    if _FORBIDDEN.search(sql):
        return False
    return True


def run_query(db_path: str, sql: str):
    """Execute a validated SELECT and return (columns, rows)."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        return columns, rows
    finally:
        conn.close()


def ask(db_path: str, question: str):
    """Full pipeline: question -> SQL -> validated execution."""
    schema = get_schema(db_path)
    sql = generate_sql(question, schema)
    if not is_safe(sql):
        raise ValueError(f"Refused to run a non read-only query:\n{sql}")
    columns, rows = run_query(db_path, sql)
    return sql, columns, rows
