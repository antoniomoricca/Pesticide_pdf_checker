import httpx
import pandas as pd

BASE_URL_PRODUCT = "https://api.datalake.sante.service.ec.europa.eu/sante/pesticides/pesticide_residues_products"
BASE_URL_PEST = "https://api.datalake.sante.service.ec.europa.eu/sante/pesticides/active_substances"
BASE_URL_PCR="https://api.datalake.sante.service.ec.europa.eu/sante/pesticides/product-current-mrl-all-residues"
BASE_URL_MRL = "https://api.datalake.sante.service.ec.europa.eu/sante/pesticides/pesticide_residues_mrls"
HEADERS = { "Content-Type": "application/json","Cache-Control": "no-cache",}
PARAMS = {"format": "json", "api-version": "v2.0","language":"en"}
PARAMS_MRL = {"format": "json", "api-version": "v2.0"}
PARAMS_PEST = {"format": "json", "api-version": "v2.0"}

def fetch_all_data(url, params, timeout=30.0) -> list[dict]:
    """ Function to retrieve the data for different EU API endpoint"""
    all_items: list[dict] = []
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        payload = resp.json()
        all_items.extend(payload.get("value", []))
        next_link = payload.get("nextLink")
        while next_link:
            resp = client.get(next_link, headers=HEADERS)
            resp.raise_for_status()
            payload = resp.json()
            all_items.extend(payload.get("value", []))
            next_link = payload.get("nextLink")
    return all_items

def get_substance_mrl_EU(product_id: int, substance_id:int ):
    """ Allow to retrieve the MLR for a couple (product id/ substance id)"""
    params = PARAMS_MRL | {"pesticide_residue_id": substance_id, "product_id": product_id }
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(BASE_URL_MRL, headers=HEADERS, params=params)
        resp.raise_for_status()
        payload = resp.json()
        data = payload.get("value", [])
        data = [mlr for mlr in data if mlr.get("applicability_text") == "Applicable"]
    return data

def get_db_prod():
    prod=fetch_all_data(url=BASE_URL_PRODUCT,params=PARAMS) 
    df_prod=pd.DataFrame(prod)
    return df_prod

def get_db_pest():
    pest=fetch_all_data(url=BASE_URL_PEST,params=PARAMS_PEST) 
    df_pest=pd.DataFrame(pest)
    return df_pest