# 🧞 QueryGenie — Natural Language to SQL

QueryGenie lets anyone query a relational database **without knowing SQL**. You
type a question in plain English ("Which product generated the most revenue?"),
and QueryGenie uses an LLM to:

1. Read the database schema,
2. Generate the correct SQL query,
3. **Validate that the query is read-only** (safety guard),
4. Execute it and show the results — with an automatic chart.

> Text-to-SQL is one of the highest-value real-world LLM applications (BI tools,
> analytics copilots, internal dashboards). This project demonstrates it end to
> end, including the safety layer that production systems require.

---

## ✨ Features

- **Schema-aware prompting** — the model is grounded in the real table/column
  names, so it writes queries that actually run.
- **Read-only safety guard** — every generated query is checked; anything that
  could modify data (`INSERT/UPDATE/DELETE/DROP/...`) is refused before execution.
- **Zero setup data** — a realistic sample SQLite store database (customers,
  products, orders) is generated automatically on first run.
- **Auto-visualisation** — two-column numeric results are charted instantly.
- **Model-agnostic** — any OpenAI-compatible API (Groq *(free)*, OpenAI, or a
  local Ollama model).

## 🧠 Tech stack

`Python` · `Streamlit` · `SQLite` · `pandas` · `OpenAI SDK`

## 🏗️ How it works

```
Question ─▶ read schema ─▶ LLM writes SQL ─▶ safety check ─▶ run on SQLite ─▶ table + chart
```

---

## 🚀 Setup (3 steps)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your API key
```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
```
Get a **free** key from Groq: https://console.groq.com/keys — then set
`LLM_API_KEY` inside `.env`.

### 3. Run
```bash
streamlit run app.py
```
The sample database builds automatically. Type a question (see the examples in
the sidebar) and press **Ask**.

> Want to rebuild the sample data manually? Run `python db_setup.py`.

---

## 📁 Project structure
```
querygenie/
├── app.py            # Streamlit UI
├── nl2sql.py         # Text-to-SQL engine + read-only safety guard
├── db_setup.py       # Generates the sample SQLite database
├── llm.py            # OpenAI-compatible LLM client
├── requirements.txt
└── .env.example      # configuration template
```

## 💡 Resume bullet (example)
> Built **QueryGenie**, a Text-to-SQL analytics assistant that converts natural
> language into validated, read-only SQL using schema-aware LLM prompting,
> executes it against SQLite, and auto-visualises results — including a safety
> layer that blocks any data-modifying queries.

## 🔧 Possible extensions
- Point it at your own SQLite / PostgreSQL database.
- Add multi-turn follow-up questions and query history.
- Add "explain this query" and automatic result summaries.
