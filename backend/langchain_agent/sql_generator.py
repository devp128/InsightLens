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
You are a data assistant helping users query an SQL database.

Use tools only if needed. After getting the correct results from a tool, do not suggest or execute another tool again.

IMPORTANT:
- Once you use a tool and receive the response, simply reply with the final result as:
  Final Answer: [Your answer here]
- Never include both a tool and final answer in the same message.
- Do NOT include tool usage if you already got the result.
- Only respond with the final result after receiving the query result.
- Do not describe what tool was used.
- Only return the answer in plain text starting with 'Final Answer:'
- If you cannot answer, output:
  SELECT 'Sorry, question cannot be answered with current schema.';

ONLY use the following schema:
{schema}

- Use ONLY the columns and tables listed above. Do NOT use or invent any other column or table names.
- You must ALWAYS answer with ONLY a valid MySQL SELECT query, no matter what.
- NEVER give explanations, instructions, or commentary.

Example:
SELECT relationship_manager, SUM(portfolio_value) AS total_portfolio_value
FROM portfolios
GROUP BY relationship_manager;

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

def extract_sql_query(llm_output: str) -> str:
    """Extract and clean SQL query from LLM output."""
    # Remove markdown formatting and labels
    cleaned = re.sub(r"(?i)sql\s*query\s*[:：]", "", llm_output)
    cleaned = re.sub(r"```sql|```", "", cleaned)
    cleaned = re.sub(r"^sql\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

def get_portfolios_schema():
    return SCHEMA_DESCRIPTION

async def generate_sql_async(question: str, schema: str = None, timeout: int = 60) -> str:
    if schema is None:
        schema = get_portfolios_schema()
    prompt = prompt_template.format(question=question, schema=schema)
    print("[SQLTool] Prompt to LLM:\n", prompt)
    try:
        raw_output = await asyncio.wait_for(llm.apredict(prompt), timeout=timeout)
        print("[SQLTool] LLM output:\n", raw_output)
        # Clean the output to extract only the SQL
        sql = extract_sql_query(raw_output)
        print("[SQLTool] Cleaned SQL:\n", sql)
    except asyncio.TimeoutError:
        print("[SQLTool] SQL generation timed out. Using fallback query.")
        return "SELECT relationship_manager, SUM(portfolio_value) AS total_portfolio_value FROM portfolios GROUP BY relationship_manager;"
    
    # Always extract the first valid SELECT statement (ignoring explanations)
    match = re.search(r"(SELECT .*?;)", sql, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1)
    # If the output does not start with SELECT, treat as error
    if not sql.strip().upper().startswith("SELECT"):
        print("[SQLTool] LLM did not return a SQL query. Using fallback query.")
        return "SELECT relationship_manager, SUM(portfolio_value) AS total_portfolio_value FROM portfolios GROUP BY relationship_manager;"
    
    # Validate that only allowed columns/tables are used
    allowed_columns = {"id", "client_name", "portfolio_value", "relationship_manager", "stock"}
    allowed_table = "portfolios"
    # Find all column/table names in SELECT, FROM, WHERE, GROUP BY, ORDER BY, but skip aliases after AS
    tokens = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", sql)
    skip_next = False
    for i, token in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue
        if token.lower() == "as":
            skip_next = True  # Skip alias name
            continue
        # Only check tokens that are not SQL keywords or aliases
        if token.lower() in {"select", "from", "where", "and", "or", "as", "group", "by", "order", "desc", "asc", "limit", "on", "sum", "count", "avg", "max", "min", "distinct", "join", "left", "right", "inner", "outer", "having"}:
            continue
        if token not in allowed_columns and token != allowed_table:
            print(f"[SQLTool] LLM used invalid column or table: {token}. Using fallback query.")
            return "SELECT relationship_manager, SUM(portfolio_value) AS total_portfolio_value FROM portfolios GROUP BY relationship_manager;"
    return sql

def generate_sql(question: str, schema: str = None, timeout: int = 30) -> str:
    """
    Synchronous wrapper for generate_sql_async for compatibility.
    """
    import asyncio
    return asyncio.run(generate_sql_async(question, schema, timeout))

