# llm.py
import google.generativeai as genai
from sqlalchemy import text
import re
import logging

# Configure Gemini
genai.configure(api_key="AIzaSyDBgCUh5nMajD5dR-CuijJqTS4C69p8XwY")  # <-- replace with your actual key

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Prompt template for Gemini
SQL_PROMPT = """
You are an expert data assistant. Convert the following natural language question into a valid SQLite SQL query.
The database schema is:
- Table: profiles
  Columns: platform, latitude, longitude, date
- Table: measurements
  Columns: profile_id, depth, temperature, salinity

Rules:
- Use JOIN only if necessary: join profiles.platform = measurements.profile_id
- Do NOT use any column that does not exist
- Always return valid SQLite syntax

- Return ONLY the SQL query, no explanation

Question: {question}
"""

def clean_sql(sql: str) -> str:
    """Remove unwanted characters or markdown formatting and ensure SQL starts with SELECT."""
    sql = sql.strip()
    # Remove markdown backticks
    sql = re.sub(r"^```sql|```$", "", sql, flags=re.MULTILINE).strip()
    # Remove any text before the first SELECT/UPDATE/INSERT/DELETE
    match = re.search(r"(SELECT|INSERT|UPDATE|DELETE).*", sql, flags=re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(0)
    return sql


def generate_sql(question: str) -> str:
    """Generate SQL query from natural language using Gemini."""
    prompt = SQL_PROMPT.format(question=question)
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
    sql = clean_sql(response.text)
    logging.info(f"Generated SQL: {sql}")
    return sql

def execute_sql(sql: str, db):
    """Execute SQL query and return results."""
    try:
        result = db.execute(text(sql)).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        logging.error(f"SQL execution failed: {e}")
        return {"error": str(e)}

def query_ocean_data(question: str, db):
    """Main pipeline: NL → SQL → Execution → Result"""
    if not question or not question.strip():
        return {"error": "Empty query", "sql_query": None}

    try:
        sql = generate_sql(question)
        results = execute_sql(sql, db)
        return {
            "question": question,
            "sql_query": sql,
            "results": results
        }
    except Exception as e:
        return {
            "question": question,
            "error": str(e)
        }
