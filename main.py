from src.european_db_API_calls import get_db_prod, get_db_pest
from src.langgraph_builder import build_workflow
import pandas as pd

pdf_path = "data/pdfs/Analysis-Example-3_B.pdf"
def main(pdf_path):
    # Eu Product and Pesticides database download from the API
    df_prod = get_db_prod()
    df_pest = get_db_pest()

    # Langgraph build
    app = build_workflow()

    # Graph execution
    result = app.invoke({"pdf_path": pdf_path,
                        "df_prod": df_prod,
                        "df_pest": df_pest
                        })

if __name__ == "__main__":
    main(pdf_path)