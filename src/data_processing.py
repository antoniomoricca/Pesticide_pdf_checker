import pandas as pd
from src.european_db_API_calls import get_substance_mrl_EU

def enrich_json_ids(data_json, df_prod, df_pest):
    """ Enrich the json with the product_id and substance_id from the EU database"""
    
    prod_match = df_prod[df_prod['product_name'].str.contains(data_json['Product'], case=False, na=False)]
    data_json['product_id'] = int(prod_match.iloc[0]['product_id'] if not prod_match.empty else None)

    for mol in data_json['Pesticide_molecules']:
        match = df_pest[df_pest['substance_name'].str.contains(mol['Molecule'], case=False, na=False)]
        if match.empty:
            # This part has been add to ensure to avoid problems due to a misspelling in the molecule name
            name = mol['Molecule']
            while len(name) > 2 and match.empty:
                name = name[:-1]
                match = df_pest[df_pest['substance_name'].str.contains(name, case=False, na=False)]
        mol['substance_id'] = int(match.iloc[0]['substance_id'] if not match.empty else None)

    return data_json


def add_mrl_limits(data_json):
    """ Add the MRL limits to the json using the EU API"""
    for mol in data_json['Pesticide_molecules']:
        product_id = data_json['product_id']
        substance_id = mol['substance_id']
        if product_id and substance_id:
            result = get_substance_mrl_EU(product_id=product_id, substance_id=substance_id)
            if result:
                mol['MRL_limit'] =(result[0].get('mrl_value_only', 0))
            else:
                mol['MRL_limit'] = None
        else:
            mol['MRL_limit'] = None
    return data_json

def print_conformity_report(data_json):
    """ Print a conformity report based on the json data"""

    all_yes = True
    rows = []
    for mol in data_json['Pesticide_molecules']:
        if mol.get('MRL_limit', 0) == "No MRL required":
            yes = True
        else:
            yes = float(mol.get('Measured', 0)) <= float(mol.get('MRL_limit', 0))
        rows.append({
            "Product - EU ": data_json['Product'],
            "Product - Analysis ": data_json['Product name on the analysis report'],
            "Molecule - EU": mol['Molecule'],
            "Molecule - Analysis": mol['Molecule in the report'],
            "Analysis_result": mol['Measured'],
            "MRL_limit": mol.get('MRL_limit', ""),
            "Compliant": "Conforme" if yes else "Non Conforme"
        })
        if not yes: violating_molecule = mol['Molecule']; all_yes=False
    print(pd.DataFrame(rows).to_string(index=False))
    print('\n')
    print("The product is compliant" if all_yes else f"The product is not compliant")