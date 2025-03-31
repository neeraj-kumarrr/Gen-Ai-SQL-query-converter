import os
import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

# Ensure the correct PORT is used for deployment
port = int(os.environ.get("PORT", 10000))

# Initialize FastAPI app
app = FastAPI()

def db_connection():
    """Creates a persistent SQLite database instead of an in-memory database."""
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            age INTEGER
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:  # Only insert data if the table is empty
        cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", [
            ("Neeraj", 22),
            ("Ranjan", 25)
        ])
        conn.commit()
    return conn

# Database connection
main_data = db_connection()

class QueryRequest(BaseModel):
    query: str

def authentication(api_key: str = "demo_api_key"):
    """Simple API key authentication."""
    if api_key != "demo_api_key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

def get_translate_query(queryset: str) -> str:
    """Translates user input to an SQL query."""
    if "users" in queryset.lower():
        return "SELECT * FROM users;"
    return "SELECT 'Invalid query';"

def execute_query(sql_query: str):
    """Executes an SQL query and returns the result."""
    try:
        cursor = main_data.cursor()
        cursor.execute(sql_query)
        return cursor.fetchall()
    except Exception as e:
        return str(e)

@app.post("/query")
def process_query(request: QueryRequest, api_key: str = Depends(authentication)):
    """Processes a user query and returns SQL execution results."""
    sql_query = get_translate_query(request.query)
    response = execute_query(sql_query)
    return {"query": request.query, "translated_sql_query": sql_query, "response": response}

@app.get("/explain")
def explain_query(query: str, api_key: str = Depends(authentication)):
    """Explains what SQL query will be executed for a given input."""
    sql_query = get_translate_query(query)
    return {"query": query, "sql_query": sql_query}

@app.get("/validate")
def data_validate(query: str, api_key: str = Depends(authentication)):
    """Validates if the query can be executed."""
    sql_query = get_translate_query(query)
    is_valid = "Invalid" not in sql_query
    return {"query": query, "is_valid": is_valid}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
