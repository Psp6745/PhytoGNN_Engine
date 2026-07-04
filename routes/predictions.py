# routes/predictions.py
from flask import Blueprint, render_template, current_app
import pandas as pd
import os

predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/predictions')
def list_predictions():
    data_path = os.path.join(current_app.config['DATA_DIR'], 'predictions.csv')
    try:
        df = pd.read_csv(data_path)
        # Ensure numbers render beautifully in tables
        df['Confidence'] = df['Confidence'].astype(float)
        preds_list = df.to_dict(orient='records')
    except Exception as e:
        print(f"Error loading predictions: {e}")
        preds_list = []
        
    return render_template('predictions.html', predictions=preds_list)