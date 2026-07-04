# services/graph_service.py
import pandas as pd
import os
from flask import current_app

class GraphService:
    @staticmethod
    def get_network_json():
        """
        Loads CSV files and converts them into an interactive Vis.js node-link format.
        Uses isolated boundaries to prevent crashes on missing or corrupt datasets.
        """
        data_dir = current_app.config['DATA_DIR']
        
        plants = pd.DataFrame()
        chems = pd.DataFrame()
        prots = pd.DataFrame()
        interactions = pd.DataFrame()

        # Load each file safely
        try:
            plants = pd.read_csv(os.path.join(data_dir, 'plants.csv'))
        except Exception as e:
            print(f"Graph Engine warning: plants.csv failed to load: {e}")

        try:
            chems = pd.read_csv(os.path.join(data_dir, 'phytochemicals.csv'))
        except Exception as e:
            print(f"Graph Engine warning: phytochemicals.csv failed to load: {e}")

        try:
            prots = pd.read_csv(os.path.join(data_dir, 'proteins.csv'))
        except Exception as e:
            print(f"Graph Engine warning: proteins.csv failed to load: {e}")

        try:
            interactions = pd.read_csv(os.path.join(data_dir, 'interactions.csv'))
        except Exception as e:
            print(f"Graph Engine warning: interactions.csv failed to load: {e}")

        nodes = []
        edges = []
        color_map = {'plant': '#2ecc71', 'chemical': '#3498db', 'protein': '#e74c3c'}
        added_node_ids = set()

        # 1. Add Plant Nodes
        if not plants.empty:
            for _, row in plants.iterrows():
                p_id = str(row.get('Plant_ID', '')).strip()
                if p_id and p_id not in added_node_ids:
                    nodes.append({
                        "id": p_id,
                        "label": str(row.get('Common_Name_of_Plant', p_id)).strip(),
                        "group": "plant",
                        "title": f"Plant: {row.get('Scientific_Name', 'N/A')}",
                        "color": color_map['plant'],
                        "size": 25
                    })
                    added_node_ids.add(p_id)

        # 2. Add Chemical Nodes
        if not chems.empty:
            for _, row in chems.iterrows():
                cid = str(row.get('PubChem_CID', '')).split('.')[0].strip() # Clean float indices
                if cid and cid != 'nan' and cid not in added_node_ids:
                    nodes.append({
                        "id": cid,
                        "label": str(row.get('Chemical_Name', f"CID {cid}")).strip(),
                        "group": "chemical",
                        "title": f"Phytochemical ID: {cid}",
                        "color": color_map['chemical'],
                        "size": 18
                    })
                    added_node_ids.add(cid)
                
                # Create edges linking Plant -> Chemical
                p_source = str(row.get('Plant_Source', '')).strip()
                if cid and p_source and p_source in added_node_ids:
                    edges.append({
                        "from": cid,
                        "to": p_source,
                        "label": "isolated_from",
                        "color": "#27ae60"
                    })

        # 3. Add Protein Nodes
        if not prots.empty:
            for _, row in prots.iterrows():
                pid = str(row.get('UniProt_ID', '')).strip().upper()
                if pid and pid not in added_node_ids:
                    nodes.append({
                        "id": pid,
                        "label": str(row.get('Gene_Name', pid)).strip(),
                        "group": "protein",
                        "title": f"Target: {row.get('Protein_Name', 'N/A')}",
                        "color": color_map['protein'],
                        "size": 20
                    })
                    added_node_ids.add(pid)

        # 4. Add Known Target Connections (Relational lines)
        if not interactions.empty and 'PubChem_CID' in interactions.columns:
            for _, row in interactions.iterrows():
                cid = str(row.get('PubChem_CID', '')).split('.')[0].strip()
                pid = str(row.get('UniProt_ID', '')).strip().upper()
                if cid in added_node_ids and pid in added_node_ids:
                    edges.append({
                        "from": cid,
                        "to": pid,
                        "label": "targets",
                        "color": "#c0392b"
                    })

        return {"nodes": nodes, "edges": edges}