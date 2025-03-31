# Gen Ai market analytics Assignmen:

from fastapi import FastAPI , Depends ,HTTPException
from pydantic import BaseModel
from typing import Dict
import sqlite3
import os

port = int(os.environ.get("port",8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0" , port = port)
    






def db_connection():
    conn = sqlite3.connect(':memory:' , check_same_thread=False)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY , name TEXT ,age INTEGER)")
    conn.execute('INSERT INTO users (name, age) VALUES ("Neeraj", 22), ("Ranjan", 25)')
    conn.commit()
    return conn

main_data = db_connection()

app =FastAPI()

class QueryRequest(BaseModel):
    query: str

def authentication(api_key : str = "demo_api_key"):
    if api_key != "demo_api_key":
        raise HTTPException(status_code = 403 ,detail = "invalid api key")
    return api_key


def get_translate_query(queryset: str) -> str:
    
    if "users" in queryset:
        return "SELECT * FROM users;"
    return "SELECT 'Invalid query';"
    
        

def execute_query(sql_query: str):
    try:
        data = main_data.execute(sql_query)
        return data.fetchall()
    except Exception as e:
        return str(e)
    
@app.post("/query")
def process_query(request:QueryRequest, api_key: str = Depends(authentication)):
    sql_query = get_translate_query(request.query)
    response = execute_query(sql_query)
    return {"query": request.query , "translated_sql_query": sql_query , "response": response}

@app.get("/explain")
def explain_query(query:str, api_key: str = Depends(authentication)):
    sql_query = get_translate_query(query)
    return{"query": query , "sql_query": sql_query}

@app.get("/validate")
def data_validate(query:str , api_key:str = Depends(authentication)):
    sql_query = get_translate_query(query)
    is_validate = "Invalid" not in sql_query
    return {"query": query , "is_valid": is_validate}




        
    



    



    









