# routes/graph.py
from flask import Blueprint, render_template, jsonify
from services.graph_service import GraphService

graph_bp = Blueprint('graph', __name__)

@graph_bp.route('/graph')
def view_graph():
    return render_template('graph.html')

@graph_bp.route('/api/graph-data')
def api_graph_data():
    data = GraphService.get_network_json()
    return jsonify(data)