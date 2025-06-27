from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from schemas import QueryRequest, QueryResponse, TableResult, ChartResult
import os
from langchain_agent.mongo_tool import MongoTool
from langchain_agent.sql_tool import SQLTool
from langchain_community.chat_models import ChatOpenAI

from functools import lru_cache
import re

def clean_llm_output(output):
    if isinstance(output, dict):
        return output
    if "Final Answer:" in output:
        final = output.split("Final Answer:")[-1].strip()
        return "Final Answer: " + final
    output = re.sub(r"Action:.*", "", output)
    output = re.sub(r"Action Input:.*", "", output)
    return output.strip()

# Classifier prompt
CLASSIFIER_PROMPT = """
You are an expert assistant. Classify the following user question as either 'mongo' (if it is about client profiles, risk, preferences, demographics, etc.) or 'sql' (if it is about portfolios, transactions, stock holdings, values, relationship managers, etc.).

Question: {query}

Respond with only 'mongo' or 'sql'.
"""

def get_default_llm():
    # Always use OpenRouter for better SQL generation
    return ChatOpenAI(
        model_name="deepseek/deepseek-r1-0528:free",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )

def classify_query(query: str) -> str:
    llm = get_default_llm()
    prompt = CLASSIFIER_PROMPT.format(query=query)
    result = llm.predict(prompt).strip().lower()
    if 'mongo' in result:
        return 'mongo'
    return 'sql'

mongo_tool = MongoTool()
sql_tool = SQLTool()

app = FastAPI()

# Allow frontend dev
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
# load_dotenv()
# class Settings(BaseSettings):
#     FRONTEND_URL: str = os.getenv("FRONTEND_URL")

# settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    try:
        # Classify the query
        db_type = classify_query(req.query)
        print(f"[API] Query classified as: {db_type}")
        if db_type == 'mongo':
            print(f"[API] Calling MongoDB tool with query: {req.query}")
            tool_result = mongo_tool._run(req.query)
        else:
            print(f"[API] Calling SQL tool with query: {req.query}")
            tool_result = sql_tool._run(req.query)
        cleaned_result = clean_llm_output(tool_result)
        if isinstance(cleaned_result, dict):
            text = cleaned_result.get("text", "No answer available.")
            table = {
                "columns": cleaned_result.get("columns", []),
                "rows": cleaned_result.get("rows", [])
            } if ("columns" in cleaned_result and "rows" in cleaned_result) else {"columns": [], "rows": []}
            chart = cleaned_result.get("chart", None)
        else:
            text = str(cleaned_result)
            table = {"columns": [], "rows": []}
            chart = None
        return {
            "text": text or "No answer available.",
            "table": table if table else {"columns": [], "rows": []},
            "chart": chart if chart else None
        }
    except Exception as e:
        import traceback
        print(f"[API] Error: {e}")
        print(f"[API] Error type: {type(e)}")
        print(f"[API] Full traceback:")
        traceback.print_exc()
        return {
            "text": f"Sorry, I couldn't process your question. Please try rephrasing or ask about client profiles or portfolios. (Error: {e})",
            "table": {"columns": [], "rows": []},
            "chart": None
        }
