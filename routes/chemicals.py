# routes/chemicals.py
from flask import Blueprint, render_template, current_app, abort
import pandas as pd
import os
from services.pubchem_service import PubChemService

chemicals_bp = Blueprint('chemicals', __name__)

@chemicals_bp.route('/chemicals')
def list_chemicals():
    data_path = os.path.join(current_app.config['DATA_DIR'], 'phytochemicals.csv')
    try:
        df = pd.read_csv(data_path)
        chems_list = df.to_dict(orient='records')
    except Exception as e:
        print(f"Error loading chemicals: {e}")
        chems_list = []
    return render_template('chemicals.html', chemicals=chems_list)

@chemicals_bp.route('/chemical/<cid>')
def chemical_details(cid):
    data_dir = current_app.config['DATA_DIR']
    try:
        df_c = pd.read_csv(os.path.join(data_dir, 'phytochemicals.csv'))
        df_p = pd.read_csv(os.path.join(data_dir, 'plants.csv'))
        
        # Match chemical row
        chem_rows = df_c[df_c['PubChem_CID'].astype(str) == str(cid)]
        if chem_rows.empty:
            abort(404)
            
        chem = chem_rows.iloc[0].to_dict()
        
        # Fetch botanical origin
        plant_rows = df_p[df_p['Plant_ID'] == chem['Plant_Source']]
        plant = plant_rows.iloc[0].to_dict() if not plant_rows.empty else {"Common_Name_of_Plant": "Unknown", "Plant_ID": "N/A"}
        
        # Live external API fetch
        api_data = PubChemService.fetch_molecular_data(cid)
        
    except Exception as e:
        print(f"Error loading chemical details: {e}")
        abort(500)
        
    return render_template('chemical_details.html', chem=chem, plant=plant, api_data=api_data)