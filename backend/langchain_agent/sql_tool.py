from langchain.tools import BaseTool
from db.mysql import SessionLocal
from sqlalchemy import text
from langchain_agent.sql_generator import generate_sql
from decimal import Decimal

class SQLTool(BaseTool):
    name: str = "SQLTool"
    description: str = (
        "Use this tool to answer questions about portfolio values, transactions, and stock info from MySQL. "
        "For example: portfolio value, top portfolios, stock holdings, etc."
    )

    def _run(self, query: str):
        # Use the LLM to generate SQL from the NL query
        sql_query = generate_sql(query)
        print(f"[SQLTool] Generated SQL: {sql_query}")
        session = SessionLocal()
        try:
            result = session.execute(text(sql_query))
            # Fetch all rows before closing session
            rows = result.fetchall()
            columns = result.keys()
            print(f"[SQLTool] Query columns: {columns}")
            print(f"[SQLTool] Query rows: {rows}")
            if not rows:
                return {
                    "columns": list(columns),
                    "rows": [],
                    "chart": None,
                    "text": "No results found for your query. Please try a different question about portfolios or transactions."
                }
            # Try to extract chart (string + numeric columns)
            chart = None
            str_idx = None
            num_idx = None
            print(f"[SQLTool] Chart debugging - columns: {columns}")
            print(f"[SQLTool] Chart debugging - first row: {rows[0]}")
            print(f"[SQLTool] Chart debugging - column types: {[type(row[i]) for i, row in enumerate([rows[0]])]}")
            for i, col in enumerate(columns):
                print(f"[SQLTool] Column {i} ({col}): type={type(rows[0][i])}, value={rows[0][i]}")
                if isinstance(rows[0][i], str) and str_idx is None:
                    str_idx = i
                    print(f"[SQLTool] Found string column at index {i}: {col}")
                if isinstance(rows[0][i], (int, float, Decimal)) and num_idx is None:
                    num_idx = i
                    print(f"[SQLTool] Found numeric column at index {i}: {col}")
            print(f"[SQLTool] Chart indices - str_idx: {str_idx}, num_idx: {num_idx}")
            if str_idx is not None and num_idx is not None:
                labels = [str(row[str_idx]) for row in rows]
                data = [float(row[num_idx]) for row in rows]  # Convert Decimal to float for chart
                # Convert RMKeyView to list for proper indexing
                columns_list = list(columns)
                chart = {
                    "labels": labels,
                    "data": data,
                    "label": columns_list[num_idx]
                }
                print(f"[SQLTool] Chart created: {chart}")
            else:
                print(f"[SQLTool] No chart created - missing string or numeric column")
            return {
                "columns": list(columns),
                "rows": [list(row) for row in rows],
                "chart": chart,
                "text": f"Results for: {query}"
            }
        except Exception as e:
            print(f"[SQLTool] SQLTool error: {e}")
            return {
                "columns": [],
                "rows": [],
                "chart": None,
                "text": "Sorry, I couldn't process your question or it doesn't match available portfolio data. Please ask about portfolio value, top portfolios, stock holdings, etc."
            }
        finally:
            session.close()

    def _arun(self, query: str):
        raise NotImplementedError("SQLTool does not support async yet.")
