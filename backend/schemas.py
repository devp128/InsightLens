from pydantic import BaseModel
from typing import Optional, Any, List

class QueryRequest(BaseModel):
    query: str

class TableResult(BaseModel):
    columns: list[str]
    rows: list[list[Any]]

class ChartResult(BaseModel):
    labels: list[str]
    data: list[Any]

class QueryResponse(BaseModel):
    text: str
    table: Optional[TableResult] = None
    chart: Optional[ChartResult] = None
