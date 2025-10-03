from langchain.chat_models import init_chat_model
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
root_path = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(root_path, ".env")
load_dotenv(dotenv_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_llm_response(text):
    """ 
    This function is used to parse the text from the OCR and build a robust json to put all the information.
    The prompt has been written to make the LLM follow a specific output format. The temperature is set to 0.
    There is just one-shot example in the prompt, without real data, since the examples with real data.

    Input:
        Text
    Output:
        json
    """

    prompt = f"""
    You are an expert in European legislation on pesticides. You are provided with the following text extracted from a PDF containing analysis data:

    {text}

    From this text, extract the following information in JSON format:
    - Product name: use exactly the text as written in the PDF, do not translate or modify spelling.
    - Product: translate only the text of the product name into English. If there are other words, discard them. Do not add any category, type, or extra words.
    - Pesticide molecule(s) (there may be multiple) written in the text
    - Pesticide molecule(s) (there may be multiple) written in english considering the EU approved names
    - Analysis result. Use the dot as decimal separator
    - Unit of measurement

    Attention: the text may contain errors or may not be in English, so apply translation with caution.

    The JSON output should strictly follow this format:

    {{
    "Product name on the analysis report": "product_name_in_text_language",
    "Product": "product_name in english. Not the category, just the name",
    "Pesticide_molecules": [
        {{
        "Molecule in the report": "molecule_name written in the text",
        "Molecule": "molecule_name in english considering the EU approved names",
        "Measured": "value",
        "Unit": "unit"
        }},
        {{
        "Molecule in the report": "molecule_name written in the text",
        "Molecule": "molecule_name in english considering the EU approved names",
        "Measured": "value",
        "Unit": "unit"
        }}
    ]
    }}

    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    return response.choices[0].message.content