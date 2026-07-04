# services/prediction_service.py
import pandas as pd
import os
from flask import current_app

class PredictionService:
    @staticmethod
    def get_all_predictions():
        """
        Loads the predictions.csv file safely and converts it to a list of dicts.
        """
        data_path = os.path.join(current_app.config['DATA_DIR'], 'predictions.csv')
        if not os.path.exists(data_path):
            return []
        
        try:
            df = pd.read_csv(data_path)
            # Ensure proper column headers exist
            df.columns = [col.strip() for col in df.columns]
            return df.to_dict(orient='records')
        except Exception as e:
            print(f"Error reading predictions: {e}")
            return []

    @staticmethod
    def filter_predictions(source_plant=None, chemical=None, min_confidence=0.0):
        """
        Applies filters to the predictions dataset.
        """
        predictions = PredictionService.get_all_predictions()
        if not predictions:
            return []
            
        df = pd.DataFrame(predictions)
        
        if source_plant and source_plant != "All Plants":
            df = df[df['Source Plant'] == source_plant]
            
        if chemical and chemical != "All Chemicals":
            df = df[df['Chemical'] == chemical]
            
        if min_confidence > 0.0:
            df = df[df['Confidence'] >= min_confidence]
            
        return df.to_dict(orient='records')