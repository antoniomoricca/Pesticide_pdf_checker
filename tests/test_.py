from src.european_db_API_calls import get_db_prod, get_db_pest
from src.langgraph_builder import build_workflow
import pytest
import pandas as pd

PDF_FILES = [
    "data/pdfs/Analysis-Example-1_B.pdf",
    "data/pdfs/Analysis-Example-2_B.pdf",
    "data/pdfs/Analysis-Example-3_B.pdf"
]

@pytest.fixture(scope="module")
def dbs():
    """Load the EU DBs from local CSVs for tests."""
    df_prod = pd.read_csv("data/df_prod.csv")
    df_pest = pd.read_csv("data/df_pest.csv")
    return df_prod, df_pest

@pytest.mark.parametrize("pdf_path", PDF_FILES)
def test_pdf_workflow(pdf_path, dbs):
    df_prod, df_pest = dbs

    # Build the LangGraph workflow
    app = build_workflow()

    
    state = app.invoke({
        "pdf_path": pdf_path,
        "df_prod": df_prod,
        "df_pest": df_pest
    })

    assert "text" in state, "State must contain 'text'"
    assert state["text"], "Extracted text should not be empty"
    assert "json_data" in state, "State must contain 'json_data'"
    assert state["json_data"], "JSON data should not be empty"
