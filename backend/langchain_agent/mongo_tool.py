from langchain.tools import BaseTool
from db.mongo import db
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
import os
import json
from decimal import Decimal

MONGO_SCHEMA = '''
Collection: clients
Fields:
- name: string (client names like "Alice", "Bob", "Charlie")
- risk: string (risk levels: "High", "Medium", "Low")
- age: integer (client ages like 45, 52, 38)
- city: string (cities like "Mumbai", "Delhi", "Bangalore", "Pune", "Chennai")
- preferences: array of strings (investment preferences like ["tech", "banking"], ["energy", "auto"])

Example queries:
- High risk clients: {{"risk": "High"}}
- Clients in Mumbai: {{"city": "Mumbai"}}
- Clients over 40: {{"age": {{"$gt": 40}}}}
- Tech preference clients: {{"preferences": "tech"}}
- High risk tech clients: {{"risk": "High", "preferences": "tech"}}
'''

MONGO_PROMPT = PromptTemplate(
    input_variables=["question", "schema"],
    template="""
You are a MongoDB expert. Generate a valid MongoDB filter JSON object based on the user's question.

IMPORTANT RULES:
- Output ONLY a valid MongoDB filter JSON object, nothing else
- No explanations, no commentary, no markdown formatting
- Use only the fields: name, risk, age, city, preferences
- For age comparisons, use MongoDB operators like {{"$gt": 40}} for "over 40"
- For array fields like preferences, use {{"preferences": "tech"}} to find clients with "tech" preference
- For exact matches, use {{"field": "value"}}
- For multiple conditions, use {{"field1": "value1", "field2": "value2"}}

Schema:
{schema}

Question: {question}

MongoDB Filter:
"""
)

llm = ChatOpenAI(
    model_name="deepseek/deepseek-r1-0528:free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

class MongoTool(BaseTool):
    name: str = "MongoTool"
    description: str = (
        "Use this tool to answer questions about client risk appetite, investment preferences, and profile info from MongoDB. "
        "For example: risk level, investment preferences, client demographics, etc."
    )

    def _run(self, query: str):
        prompt = MONGO_PROMPT.format(question=query, schema=MONGO_SCHEMA)
        print("[MongoTool] Prompt to LLM:\n", prompt)
        try:
            filter_str = llm.predict(prompt).strip()
            print("[MongoTool] LLM output:\n", filter_str)
            # Remove code block markers if present
            if filter_str.startswith("```json"):
                filter_str = filter_str[7:]
            if filter_str.startswith("```"):
                filter_str = filter_str[3:]
            filter_str = filter_str.strip('`\n ')
            
            # Fix common MongoDB operator issues
            # Replace quoted operators with unquoted ones
            filter_str = filter_str.replace('"$gt"', '$gt')
            filter_str = filter_str.replace('"$lt"', '$lt')
            filter_str = filter_str.replace('"$gte"', '$gte')
            filter_str = filter_str.replace('"$lte"', '$lte')
            filter_str = filter_str.replace('"$in"', '$in')
            filter_str = filter_str.replace('"$nin"', '$nin')
            
            print("[MongoTool] Cleaned filter string:\n", filter_str)
            mongo_filter = json.loads(filter_str)
        except Exception as e:
            print(f"[MongoTool] JSON parsing error: {e}")
            print("[MongoTool] LLM output could not be parsed as JSON, falling back to user-friendly message.")
            return {
                "text": "Sorry, I couldn't understand your question or it doesn't match client profile fields. Please ask about client name, risk, age, city, or preferences.",
                "columns": [],
                "rows": [],
                "chart": None
            }
        # Validate filter fields
        allowed_fields = {"name", "risk", "age", "city", "preferences"}
        if not isinstance(mongo_filter, dict) or any(k not in allowed_fields for k in mongo_filter.keys()):
            print(f"[MongoTool] Invalid filter fields: {mongo_filter}. Fallback to user-friendly message.")
            return {
                "text": "Sorry, your question doesn't match available client profile fields. Please ask about name, risk, age, city, or preferences.",
                "columns": [],
                "rows": [],
                "chart": None
            }
        projection = {"_id": 0, "name": 1, "risk": 1, "age": 1, "city": 1, "preferences": 1}
        try:
            results = list(db["clients"].find(mongo_filter, projection))
        except Exception as e:
            print(f"[MongoTool] MongoDB error: {e}. Fallback to user-friendly message.")
            return {
                "text": "Sorry, there was a problem accessing client data. Please try again later.",
                "columns": [],
                "rows": [],
                "chart": None
            }
        if not results:
            print("[MongoTool] No results for filter, fallback to user-friendly message.")
            return {
                "text": "No matching clients found for your query.",
                "columns": [],
                "rows": [],
                "chart": None
            }
        # Format as table
        columns = list(results[0].keys())
        rows = [list(doc.values()) for doc in results]
        print(f"[MongoTool] Query columns: {columns}")
        print(f"[MongoTool] Query rows: {rows}")
        # Try to extract chart (string + numeric columns)
        chart = None
        str_idx = None
        num_idx = None
        print(f"[MongoTool] Chart debugging - columns: {columns}")
        print(f"[MongoTool] Chart debugging - first row: {rows[0]}")
        print(f"[MongoTool] Chart debugging - column types: {[type(row[i]) for i, row in enumerate([rows[0]])]}")
        for i, col in enumerate(columns):
            print(f"[MongoTool] Column {i} ({col}): type={type(rows[0][i])}, value={rows[0][i]}")
            if isinstance(rows[0][i], str) and str_idx is None:
                str_idx = i
                print(f"[MongoTool] Found string column at index {i}: {col}")
            if isinstance(rows[0][i], (int, float, Decimal)) and num_idx is None:
                num_idx = i
                print(f"[MongoTool] Found numeric column at index {i}: {col}")
        print(f"[MongoTool] Chart indices - str_idx: {str_idx}, num_idx: {num_idx}")
        if str_idx is not None and num_idx is not None:
            labels = [str(row[str_idx]) for row in rows]
            data = [float(row[num_idx]) for row in rows]  # Convert to float for chart
            chart = {
                "labels": labels,
                "data": data,
                "label": columns[num_idx]
            }
            print(f"[MongoTool] Chart created: {chart}")
        else:
            print(f"[MongoTool] No chart created - missing string or numeric column")
        return {
            "columns": columns,
            "rows": rows,
            "chart": chart,
            "text": f"Results for: {query}"
        }

    def _arun(self, query: str):
        raise NotImplementedError("MongoTool does not support async yet.")
