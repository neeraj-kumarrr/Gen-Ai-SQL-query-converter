from fastapi import FastAPI , Depends , HTTPException
from pydantic import BaseModel
from typing import Dict
import sqlite3

def get_db_connection():

    conn = sqlite3.connect(":memory:" , check_same_thread= False)
    conn.execute( "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT , age INTEGER)")
    conn.execute("INSERT INTO users (name , age) VALUES ('Neeraj' , 22) , ('bob' , 23)")
    conn.commit()
    return conn

main_data = get_db_connection()

app = FastAPI()

def authenticate(api_key:str = "demo_api_key"):
    if api_key != "demo_api_key":
        return HTTPException(status_code = 403 , details = "invalid api key")
    return api_key

class QuerySet(BaseModel):
    query:str

def get_translate_query(query:str) -> str:
    if "users" in query.lower():
        return "SELECT * FROM users;" 
    return "Invalid select from users"

def execute_query(sql_query: str):
    try:
        cursor = main_data.execute(sql_query)
        cursor.fetchall()
        return cursor
    except Exception as e:
        return str(e)
    
@app.post("/query")
def process_query(request:QuerySet , api_key:str = Depends(authenticate)):
    sql_query = get_translate_query(request.query)
    response = execute_query(sql_query)
    return { "query":request.query ,"translate_query": sql_query , "response": response }

@app.get("/explain")
def explanation(query:str , api_key : str = Depends(authenticate)):
    sql_query = get_translate_query(query)
    return { "query": query , "translate_query": sql_query}

@app.get("/validate")
def validation(query:str , api_key:str = Depends(authenticate)):
    sql_query = get_translate_query(query)
    is_validate = "invalid" not in sql_query
    return {"query":query , "is_valid": is_validate }



