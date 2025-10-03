from src.get_llm_response import get_llm_response
from src.pdf_parser import pdf_to_text, preprocess_image
from src.get_llm_response import get_llm_response
from src.european_db_API_calls import fetch_all_data
from src.european_db_API_calls import get_substance_mrl_EU
from src.data_processing import enrich_json_ids
from src.data_processing import add_mrl_limits
from src.data_processing import print_conformity_report
import pandas as pd
from langgraph.graph import StateGraph, END, START
from typing import TypedDict
import json


class State(TypedDict):
    """
    Represents the state passed through the LangGraph workflow:
    - pdf_path (str): local path to PDF
    - text (str): extracted text from the PDF
    - json_data (dict): structured data
    - df_prod (pd.DataFrame): EU products database
    - df_pest (pd.DataFrame): EU pesticides database
    """
    pdf_path: str
    text: str
    json_data: dict
    df_prod: pd.DataFrame
    df_pest: pd.DataFrame


# Below all the nodes of the graph
def ocr_node(state):
    text = pdf_to_text(state["pdf_path"])
    return {**state, "text": text}

def llm_node(state):
    response = get_llm_response(state["text"])
    response = response.strip()
    if response.startswith('```'):
        response = response.split('\n', 1)[1]
    if response.endswith('```'):
        response = response.rsplit('\n', 1)[0]
    
    json_data = json.loads(response)
    return {**state, "json_data": json_data}

def enrich_node(state):
    json_data = enrich_json_ids(state["json_data"], state["df_prod"], state["df_pest"])
    return {**state, "json_data": json_data}

def mrl_node(state):
    json_data = add_mrl_limits(state["json_data"])
    return {**state, "json_data": json_data}

def final_node(state: State) -> State:
    print_conformity_report(state["json_data"])
    return state

def build_workflow():
    """
    Build and compile the LangGraph workflow. the workflow is simple but robust.
    Output:
        the compiled graph ready to run.
    """
    workflow = StateGraph(State)
    workflow.add_node("ocr", ocr_node)
    workflow.add_node("llm", llm_node)
    workflow.add_node("enrich", enrich_node)
    workflow.add_node("mrl", mrl_node)
    workflow.add_node("Report", final_node)

    workflow.set_entry_point("ocr")
    workflow.add_edge("ocr", "llm")
    workflow.add_edge("llm", "enrich")
    workflow.add_edge("enrich", "mrl")
    workflow.add_edge("mrl", "Report")
    workflow.add_edge("Report", END)

    return workflow.compile()
