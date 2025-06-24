from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from schemas import QueryRequest, QueryResponse, TableResult, ChartResult
from langchain_agent.echo_chain import run_echo_chain

app = FastAPI()

# Allow frontend dev
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()
class Settings(BaseSettings):
    FRONTEND_URL: str = os.getenv("FRONTEND_URL")

settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    query_text = req.query.lower()
    # Hardcoded SQL for key business questions
    def get_hardcoded_sql(question: str):
        q = question.lower().strip()
        import re
        if "top five portfolios" in q or "top 5 portfolios" in q:
            return "SELECT client_name, portfolio_value FROM portfolios ORDER BY portfolio_value DESC LIMIT 5;"
        if "breakup of portfolio values per relationship manager" in q:
            return "SELECT relationship_manager, SUM(portfolio_value) as total_value FROM portfolios GROUP BY relationship_manager ORDER BY total_value DESC;"
        if "top relationship managers" in q:
            return "SELECT relationship_manager, SUM(portfolio_value) as total_value FROM portfolios GROUP BY relationship_manager ORDER BY total_value DESC LIMIT 5;"
        if "highest holders of" in q:
            match = re.search(r"highest holders of ([\w\s]+)", q)
            if match:
                stock = match.group(1).strip().replace("'", "''")
                return f"SELECT client_name, portfolio_value FROM portfolios WHERE stock = '{stock}' ORDER BY portfolio_value DESC;"
        return None

    from db.mysql import SessionLocal
    from sqlalchemy import text
    session = SessionLocal()
    try:
        sql_query = get_hardcoded_sql(req.query)
        if sql_query:
            try:
                result = session.execute(text(sql_query))
                rows = result.fetchall()
                columns = result.keys()
                table = TableResult(columns=list(columns), rows=[list(row) for row in rows])
                # Try to generate a chart if possible
                chart = None
                if table and table.columns and table.rows:
                    # Find first string column and first numeric column
                    import numbers
                    str_idx = None
                    num_idx = None
                    for i, col in enumerate(table.columns):
                        # Check first row for type
                        if len(table.rows) > 0:
                            val = table.rows[0][i]
                            try:
                                float_val = float(val)
                                if num_idx is None:
                                    num_idx = i
                            except (ValueError, TypeError):
                                if str_idx is None:
                                    str_idx = i
                    if str_idx is not None and num_idx is not None:
                        labels = [str(row[str_idx]) for row in table.rows]
                        data = [float(row[num_idx]) for row in table.rows]
                        chart = {
                            "labels": labels,
                            "data": data,
                            "label": table.columns[num_idx]
                        }
                return QueryResponse(
                    text=f"Results for: {req.query}",
                    table=table,
                    chart=chart
                )
            except Exception as e:
                # If LLM generates invalid SQL, fallback to echo chain
                text_resp = run_echo_chain(req.query)
                return QueryResponse(
                    text=f"LLM SQL generation failed: {e}\n\n{text_resp}",
                    table=None,
                    chart=None
                )
            finally:
                session.close()
        else:
            try:
                # Use the improved async SQL generator with timeout and strict schema
                from langchain_agent.sql_generator import generate_sql_async, get_portfolios_schema
                import asyncio
                schema = get_portfolios_schema()
                sql_query = asyncio.run(generate_sql_async(req.query, schema=schema, timeout=30))
                if sql_query.lower().startswith("sorry, i cannot answer"):
                    return QueryResponse(
                        text=sql_query,
                        table=None,
                        chart=None
                    )
                if sql_query.lower().startswith("-- sql generation timed out"):
                    return QueryResponse(
                        text=sql_query,
                        table=None,
                        chart=None
                    )
                result = session.execute(text(sql_query))
                rows = result.fetchall()
                columns = result.keys()
                table = TableResult(columns=list(columns), rows=[list(row) for row in rows])
                # Try to generate a chart if possible
                chart = None
                if table and table.columns and table.rows:
                    # Find first string column and first numeric column
                    import numbers
                    str_idx = None
                    num_idx = None
                    for i, col in enumerate(table.columns):
                        # Check first row for type
                        if len(table.rows) > 0:
                            val = table.rows[0][i]
                            try:
                                float_val = float(val)
                                if num_idx is None:
                                    num_idx = i
                            except (ValueError, TypeError):
                                if str_idx is None:
                                    str_idx = i
                    if str_idx is not None and num_idx is not None:
                        labels = [str(row[str_idx]) for row in table.rows]
                        data = [float(row[num_idx]) for row in table.rows]
                        chart = {
                            "labels": labels,
                            "data": data,
                            "label": table.columns[num_idx]
                        }
                return QueryResponse(
                    text=f"Results for: {req.query}",
                    table=table,
                    chart=chart
                )
            except Exception as e:
                # If LLM generates invalid SQL, fallback to echo chain
                text_resp = run_echo_chain(req.query)
                return QueryResponse(
                    text=f"LLM SQL generation failed: {e}\n\n{text_resp}",
                    table=None,
                    chart=None
                )
            finally:
                session.close()
    except Exception as e:
        # Fallback to LLM echo/analysis
        text_resp = run_echo_chain(req.query)
        return QueryResponse(
            text=f"An error occurred: {e}\n\n{text_resp}",
            table=None,
            chart=None
        )
