# llm_service.py
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import text

# Initialize Gemini
genai.configure(api_key="AIzaSyDBgCUh5nMajD5dR-CuijJqTS4C69p8XwY")
model = genai.GenerativeModel("gemini-1.5-flash")  # or gemini-1.5-pro


def clean_sql(sql: str) -> str:
    """Remove Markdown code block if present"""
    if sql.startswith("```"):
        sql = "\n".join(sql.split("\n")[1:-1])
    return sql.strip()

def query_ocean_data(natural_query: str, db: Session):
    """
    Translate natural language queries into SQL using Gemini and execute on DB.
    """
    # Prompt to instruct Gemini
    system_prompt = """You are an assistant that converts natural language queries into valid SQLite queries for oceanographic data.

Database schema:
- profiles(id, profile_id, lat, lon, time_utc)
- measurements(id, profile_id, depth, temperature, salinity)

Rules:
1. If joining measurements and profiles, always join measurements.profile_id = profiles.id
2. Use only columns listed above.
3. Always produce valid SQLite SQL.
4. Include LIMIT 5 for exploratory queries.

Example:
- '5 measurements at depth 1000' ->
  SELECT m.temperature, m.salinity, m.depth
  FROM measurements m
  LIMIT 5;

Convert this query into SQL:

"""


    full_prompt = f"{system_prompt}\n{natural_query}"

    try:
        response = model.generate_content(full_prompt)
        sql_response = clean_sql(response.text.strip())

    # Execute the SQL
        result = db.execute(text(sql_response)).fetchall()
        rows = [dict(r._mapping) for r in result]

        return {"query": natural_query, "sql": sql_response, "result": rows}
    except Exception as e:
        return {"error": str(e), "sql": sql_response if 'sql_response' in locals() else None}
