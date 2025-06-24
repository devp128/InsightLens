from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

# Describe your MySQL schema for the LLM
SCHEMA_DESCRIPTION = '''
Database: portfolios
Table: portfolios
Columns:
- id: integer, primary key
- client_name: string (the name of the client)
- portfolio_value: decimal (the total value of the client portfolio)
- relationship_manager: string (the RM for the client)
- stock: string (the main stock held in this portfolio)
'''


STRICT_SQL_INSTRUCTIONS = """
You are an expert MySQL assistant for a wealth management firm.

ONLY use the following schema:
{schema}

- Use ONLY the columns and tables listed above. Do NOT use or invent any other column or table names.
- You must ALWAYS answer with ONLY a valid MySQL SELECT query, no matter what.
- If the question is ambiguous, make reasonable assumptions and still output a SQL query.
- NEVER give explanations, instructions, or commentary.
- If you cannot answer, output:
  SELECT 'Sorry, question cannot be answered with current schema.';

Question: {question}
SQL Query:
"""


prompt_template = PromptTemplate(
    input_variables=["question", "schema"],
    template=STRICT_SQL_INSTRUCTIONS
)

llm = ChatOpenAI(
    model_name="deepseek/deepseek-r1-0528:free",  # Or your OpenRouter model
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_API_BASE,
)

import re

import asyncio

def get_portfolios_schema():
    return SCHEMA_DESCRIPTION

async def generate_sql_async(question: str, schema: str = None, timeout: int = 30) -> str:
    if schema is None:
        schema = get_portfolios_schema()
    prompt = prompt_template.format(question=question, schema=schema)
    try:
        sql = await asyncio.wait_for(llm.apredict(prompt), timeout=timeout)
    except asyncio.TimeoutError:
        return "-- SQL generation timed out. Please try again later."
    sql = sql.strip()
    # Remove markdown/code block markers and leading 'sql' if present
    sql = re.sub(r"^(```sql|```|sql)", "", sql, flags=re.IGNORECASE).strip()
    sql = re.sub(r"```$", "", sql).strip()
    # Always extract the first valid SELECT statement (ignoring explanations)
    match = re.search(r"(SELECT .*?;)", sql, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1)
    # If the output does not start with SELECT, treat as error
    if not sql.strip().upper().startswith("SELECT"):
        return "-- LLM did not return a SQL query. Please rephrase your question or try again."
    return sql


def generate_sql(question: str, schema: str = None, timeout: int = 30) -> str:
    """
    Synchronous wrapper for generate_sql_async for compatibility.
    """
    import asyncio
    return asyncio.run(generate_sql_async(question, schema, timeout))

