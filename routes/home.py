# Create a folder structure named 'routes/' and populate:

# --- routes/home.py ---
from flask import Blueprint, render_template, current_app
import pandas as pd
import os

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    data_dir = current_app.config['DATA_DIR']
    try:
        p_count = len(pd.read_csv(os.path.join(data_dir, 'plants.csv')))
        c_count = len(pd.read_csv(os.path.join(data_dir, 'phytochemicals.csv')))
        pr_count = len(pd.read_csv(os.path.join(data_dir, 'proteins.csv')))
    except Exception:
        p_count, c_count, pr_count = 0, 0, 0
    return render_template('index.html', p_count=p_count, c_count=c_count, pr_count=pr_count)

# --- routes/plants.py ---
from flask import Blueprint, render_template, current_app
import pandas as pd
import os

plants_bp = Blueprint('plants', __name__)

@plants_bp.route('/plants')
def list_plants():
    df = pd.read_csv(os.path.join(current_app.config['DATA_DIR'], 'plants.csv'))
    return render_template('plants.html', plants=df.to_dict(orient='records'))

@plants_bp.route('/plant/<plant_id>')
def plant_details(plant_id):
    df_p = pd.read_csv(os.path.join(current_app.config['DATA_DIR'], 'plants.csv'))
    df_c = pd.read_csv(os.path.join(current_app.config['DATA_DIR'], 'phytochemicals.csv'))
    
    plant = df_p[df_p['Plant_ID'] == plant_id].to_dict(orient='records')[0]
    compounds = df_c[df_c['Plant_Source'] == plant_id].to_dict(orient='records')
    return render_template('plant_details.html', plant=plant, compounds=compounds)

# --- routes/chemicals.py ---
from flask import Blueprint, render_template, current_app
import pandas as pd
import os
from services.pubchem_service import PubChemService

chemicals_bp = Blueprint('chemicals', __name__)

@chemicals_bp.route('/chemicals')
def list_chemicals():
    df = pd.read_csv(os.path.join(current_app.config['DATA_DIR'], 'phytochemicals.csv'))
    return render_template('chemicals.html', chemicals=df.to_dict(orient='records'))

@chemicals_bp.route('/chemical/<cid>')
def chemical_details(cid):
    df_c = pd.read_csv(os.path.join(current_app.config['DATA_DIR'], 'phytochemicals.csv'))
    df_p = pd.read_csv(os.path.join(current_app.config['DATA_DIR'], 'plants.csv'))
    
    chem = df_c[df_c['PubChem_CID'] == int(cid)].to_dict(orient='records')[0]
    plant = df_p[df_p['Plant_ID'] == chem['Plant_Source']].to_dict(orient='records')[0]
    
    api_data = PubChemService.fetch_molecular_data(cid)
    return render_template('chemical_details.html', chem=chem, plant=plant, api_data=api_data)

# --- routes/proteins.py ---
from flask import Blueprint, render_template, current_app
import pandas as pd
import os
from services.uniprot_service import UniProtService

proteins_bp = Blueprint('proteins', __name__)

@proteins_bp.route('/proteins')
def list_proteins():
    df = pd.read_csv(os.path.join(current_app.config['DATA_DIR'], 'proteins.csv'))
    return render_template('proteins.html', proteins=df.to_dict(orient='records'))

@proteins_bp.route('/protein/<uniprot_id>')
def protein_details(uniprot_id):
    df_p = pd.read_csv(os.path.join(current_app.config['DATA_DIR'], 'proteins.csv'))
    protein = df_p[df_p['UniProt_ID'] == uniprot_id].to_dict(orient='records')[0]
    
    api_data = UniProtService.fetch_protein_details(uniprot_id)
    return render_template('protein_details.html', protein=protein, api_data=api_data)

# --- routes/predictions.py ---
from flask import Blueprint, render_template, current_app
import pandas as pd
import os

predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/predictions')
def list_predictions():
    df = pd.read_csv(os.path.join(current_app.config['DATA_DIR'], 'predictions.csv'))
    return render_template('predictions.html', predictions=df.to_dict(orient='records'))

# --- routes/analytics.py ---
from flask import Blueprint, render_template

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def show_analytics():
    return render_template('analytics.html')

# --- routes/graph.py ---
from flask import Blueprint, render_template, jsonify
from services.graph_service import GraphService

graph_bp = Blueprint('graph', __name__)

@graph_bp.route('/graph')
def view_graph():
    return render_template('graph.html')

@graph_bp.route('/api/graph-data')
def api_graph_data():
    return jsonify(GraphService.get_network_json())

# --- routes/chatbot.py ---
from flask import Blueprint, request, jsonify, render_template
from services.chatbot_service import ChatbotService

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot')
def show_chatbot():
    return render_template('chatbot.html')

@chatbot_bp.route('/chatbot/query', methods=['POST'])
def query():
    user_text = request.json.get('message', '')
    res = ChatbotService.query_bot(user_text)
    return jsonify({"response": res})