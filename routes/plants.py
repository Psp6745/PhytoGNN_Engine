# routes/plants.py
from flask import Blueprint, render_template, current_app, abort
import pandas as pd
import os

plants_bp = Blueprint('plants', __name__)

@plants_bp.route('/plants')
def list_plants():
    data_path = os.path.join(current_app.config['DATA_DIR'], 'plants.csv')
    try:
        df = pd.read_csv(data_path)
        plants_list = df.to_dict(orient='records')
    except Exception as e:
        print(f"Error loading plants: {e}")
        plants_list = []
    return render_template('plants.html', plants=plants_list)

@plants_bp.route('/plant/<plant_id>')
def plant_details(plant_id):
    data_dir = current_app.config['DATA_DIR']
    try:
        df_p = pd.read_csv(os.path.join(data_dir, 'plants.csv'))
        df_c = pd.read_csv(os.path.join(data_dir, 'phytochemicals.csv'))
        
        # Match the specific plant
        plant_rows = df_p[df_p['Plant_ID'].astype(str) == str(plant_id)]
        if plant_rows.empty:
            abort(404)
            
        plant = plant_rows.iloc[0].to_dict()
        compounds = df_c[df_c['Plant_Source'].astype(str) == str(plant_id)].to_dict(orient='records')
        
    except Exception as e:
        print(f"Error loading plant details: {e}")
        abort(500)
        
    return render_template('plant_details.html', plant=plant, compounds=compounds)