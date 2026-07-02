"""
QueryGenie — Ask your database questions in plain English.

Run:  streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from db_setup import build, DB_PATH
from nl2sql import ask, get_schema

load_dotenv()

st.set_page_config(page_title="QueryGenie — Text to SQL", page_icon="🧞")

# Build the sample database on first run so the app works instantly.
if not os.path.exists(DB_PATH):
    build()

st.title("🧞 QueryGenie")
st.caption("Ask questions in plain English — QueryGenie writes the SQL, runs it, and shows the answer.")

# --- Sidebar: schema + examples -------------------------------------------- #
with st.sidebar:
    st.header("Database schema")
    st.code(get_schema(DB_PATH), language="text")
    st.divider()
    st.header("Try asking")
    examples = [
        "How many orders were placed in total?",
        "Which product generated the most revenue?",
        "List the top 3 customers by total spend.",
        "What is the total revenue per product category?",
        "Which city has the most customers?",
    ]
    for ex in examples:
        st.markdown(f"- {ex}")

# --- Main --------------------------------------------------------------------#
question = st.text_input(
    "Your question", placeholder="e.g. Which product generated the most revenue?"
)

if st.button("Ask", type="primary") and question:
    try:
        with st.spinner("Generating SQL and querying..."):
            sql, columns, rows = ask(DB_PATH, question)

        st.subheader("Generated SQL")
        st.code(sql, language="sql")

        st.subheader("Result")
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df, use_container_width=True)
            # If the result looks like a simple label/number pair, chart it.
            if df.shape[1] == 2 and pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
                st.bar_chart(df.set_index(df.columns[0]))
        else:
            st.info("The query ran successfully but returned no rows.")
    except Exception as e:  # noqa: BLE001 — surface any error to the user
        st.error(f"Something went wrong: {e}")
