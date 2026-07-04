# routes/proteins.py
from flask import Blueprint, render_template, current_app, abort
import pandas as pd
import os
from services.uniprot_service import UniProtService

proteins_bp = Blueprint('proteins', __name__)

@proteins_bp.route('/proteins')
def list_proteins():
    data_path = os.path.join(current_app.config['DATA_DIR'], 'proteins.csv')
    try:
        df = pd.read_csv(data_path)
        prots_list = df.to_dict(orient='records')
    except Exception as e:
        print(f"Error loading proteins: {e}")
        prots_list = []
    return render_template('proteins.html', proteins=prots_list)

@proteins_bp.route('/protein/<uniprot_id>')
def protein_details(uniprot_id):
    data_dir = current_app.config['DATA_DIR']
    try:
        df_p = pd.read_csv(os.path.join(data_dir, 'proteins.csv'))
        
        # Match protein row
        prot_rows = df_p[df_p['UniProt_ID'].astype(str).str.upper() == str(uniprot_id).upper()]
        if prot_rows.empty:
            abort(404)
            
        protein = prot_rows.iloc[0].to_dict()
        
        # Live external API fetch from UniProt
        api_data = UniProtService.fetch_protein_details(uniprot_id)
        
    except Exception as e:
        print(f"Error loading protein details: {e}")
        abort(500)
        
    return render_template('protein_details.html', protein=protein, api_data=api_data)