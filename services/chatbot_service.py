# services/chatbot_service.py
# Purpose: Core NLP search, pathway routing, and in-memory indexing engine.
# Note: Exceptions are allowed to bubble up naturally for stack-trace debugging.

import pandas as pd
import os
import re
from flask import current_app
from services.pubchem_service import PubChemService

class ChatbotService:
    # Class-level cache variables to ensure datasets are loaded only ONCE at boot
    _initialized = False
    _status = "OFFLINE"
    
    plants_df = pd.DataFrame()
    chems_df = pd.DataFrame()
    prots_df = pd.DataFrame()
    interactions_df = pd.DataFrame()
    predictions_df = pd.DataFrame()
    
    # Conversational context memory to resolve pronouns (e.g., "it")
    # Structure: { session_id: { "last_entity_type": "plant", "last_entity_name": "Neem" } }
    conversational_memory = {}

    @classmethod
    def initialize_knowledge_base(cls):
        """
        Loads all CSV datasets into RAM at boot.
        Uses system paths safely.
        """
        if cls._initialized:
            return

        print("\n" + "="*50)
        print("🤖 [PHYTO-AI] INITIALIZING KNOWLEDGE BASE ENGINE...")
        print("="*50)
        
        data_dir = current_app.config['DATA_DIR']
        
        files_to_load = {
            'plants_df': ('plants.csv', 'Plants Specimen'),
            'chems_df': ('phytochemicals.csv', 'Chemical Compounds'),
            'prots_df': ('proteins.csv', 'Target Proteins'),
            'interactions_df': ('interactions.csv', 'Known Interactions'),
            'predictions_df': ('predictions.csv', 'GNN Predictions')
        }
        
        success_count = 0
        
        for attr, (filename, label) in files_to_load.items():
            path = os.path.join(data_dir, filename)
            # Fallback pathing check for predictions output names
            if filename == 'predictions.csv' and not os.path.exists(path):
                path = os.path.join(data_dir, 'FIXED_FINAL_REPORT.csv')

            print(f"Loading {label:18} Data from: {filename}...")
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    # Clean column whitespace to prevent KeyErrors
                    df.columns = [col.strip() for col in df.columns]
                    setattr(cls, attr, df)
                    success_count += 1
                except Exception as e:
                    print(f"❌ [ERROR] Failed to load {filename}: {str(e)}")
                    raise e
            else:
                print(f"❌ [MISSING] Database file not found: {filename}")

        if success_count >= 4: # Standard operating minimum
            cls._status = "ONLINE"
            cls._initialized = True
            print("="*50)
            print("🏆 KNOWLEDGE BASE STACK BUILT SUCCESSFULLY!")
            print("🟢 DATABASE STATUS: ONLINE & READY")
            print("="*50 + "\n")
        else:
            cls._status = "OFFLINE"
            print("="*50)
            print("❌ [CRITICAL ERROR] KNOWLEDGE BASE LOAD FAILURE")
            print("🔴 DATABASE STATUS: OFFLINE")
            print("="*50 + "\n")

    @classmethod
    def query_bot(cls, user_query, session_id="default"):
        """
        Main entry point for NLP user queries.
        Processes context, detects intent, and dispatches to sub-handlers.
        """
        if not cls._initialized:
            cls.initialize_knowledge_base()
            if cls._status == "OFFLINE":
                raise FileNotFoundError("The on-premise knowledge datasets failed to load. Check data/ folder.")

        query_clean = user_query.lower().strip()
        
        # 1. Resolve Conversational Pronoun Context (e.g. "What does it do?")
        query_clean = cls._resolve_pronoun_context(query_clean, session_id)
        
        # 2. Intent Dispatcher Routing
        
        # Scenario A: Directory List queries
        if any(x in query_clean for x in ["list plants", "show anti-diabetic plants", "medicinal plants", "show plants"]):
            return cls._handle_list_plants()
            
        if any(x in query_clean for x in ["list chemicals", "list compounds", "list phytochemicals"]):
            return cls._handle_list_chemicals()
            
        if any(x in query_clean for x in ["list proteins", "show proteins", "target proteins"]):
            return cls._handle_list_proteins()

        # Scenario B: Pathway Tracing Query (e.g., "pathway from Gymnema to DPP4")
        pathway_match = re.search(r'(?:pathway from|pathway)\s+([a-zA-Z\s]+)\s+to\s+([a-zA-Z0-9\-\s]+)', query_clean)
        if pathway_match:
            start_entity = pathway_match.group(1).strip()
            end_entity = pathway_match.group(2).strip()
            return cls._handle_pathway_trace(start_entity, end_entity)

        # Scenario C: Specific Species (Plant) query
        for _, row in cls.plants_df.iterrows():
            common_name = row['Common_Name_of_Plant'].lower()
            plant_id = row['Plant_ID'].lower()
            if common_name in query_clean or plant_id in query_clean:
                cls._set_session_context(session_id, "plant", row['Common_Name_of_Plant'])
                return cls._format_plant_response(row)

        # Scenario D: Specific Chemical compound query
        for _, row in cls.chems_df.iterrows():
            chem_name = row['Chemical_Name'].lower()
            cid = str(row['PubChem_CID'])
            if chem_name in query_clean or cid == query_clean:
                cls._set_session_context(session_id, "chemical", row['Chemical_Name'])
                return cls._format_chemical_response(row)

        # Scenario E: Specific Receptor Target Protein query
        for _, row in cls.prots_df.iterrows():
            prot_name = row['Protein_Name'].lower()
            gene_name = row['Gene_Name'].lower()
            uniprot = row['UniProt_ID'].lower()
            if prot_name in query_clean or gene_name in query_clean or uniprot in query_clean:
                cls._set_session_context(session_id, "protein", row['Protein_Name'])
                return cls._format_protein_response(row)

        # Fallback spelling suggestions
        return cls._generate_spelling_suggestions(user_query)

    # =================================================================
    # Blueprints Intent Sub-Handlers (Explicit operations)
    # =================================================================

    @classmethod
    def _handle_list_plants(cls):
        names = cls.plants_df['Common_Name_of_Plant'].tolist()
        li_items = "".join([f"<li>🌱 {name}</li>" for name in names])
        return f"🌿 **Anti-Diabetic Botanical Specimens in Database:**<br/><ul style='margin-top:5px; padding-left:20px;'>{li_items}</ul>"

    @classmethod
    def _handle_list_chemicals(cls):
        names = cls.chems_df['Chemical_Name'].head(15).tolist() # Limit display density for aesthetics
        li_items = "".join([f"<li>🧪 {name}</li>" for name in names])
        return f"🔬 **Top Mapped Phytochemical Compounds:**<br/><ul style='margin-top:5px; padding-left:20px;'>{li_items}</ul>"

    @classmethod
    def _handle_list_proteins(cls):
        names = cls.prots_df['Protein_Name'].tolist()
        li_items = "".join([f"<li>🧬 {name}</li>" for name in names])
        return f"🧬 **Human Target Proteins in Database:**<br/><ul style='margin-top:5px; padding-left:20px;'>{li_items}</ul>"

    @classmethod
    def _handle_pathway_trace(cls, start_name, end_name):
        """
        Traces molecular paths from Plant -> Chemical -> Protein targets.
        """
        # Search Plant Specimen
        start_plant = None
        for _, row in cls.plants_df.iterrows():
            if start_name in row['Common_Name_of_Plant'].lower() or start_name in row['Plant_ID'].lower():
                start_plant = row
                break

        if not start_plant:
            return f"🤖 **Assistant:** I could not locate a botanical specimen matching '{start_name}'."

        p_name = start_plant['Common_Name_of_Plant']
        p_id = start_plant['Plant_ID']

        # Search Target Protein
        target_prot = None
        for _, row in cls.prots_df.iterrows():
            if end_name in row['Protein_Name'].lower() or end_name in row['Gene_Name'].lower() or end_name in row['UniProt_ID'].lower():
                target_prot = row
                break

        if not target_prot:
            return f"🤖 **Assistant:** I could not locate a pathological protein target matching '{end_name}'."

        pr_name = target_prot['Protein_Name']
        pr_gene = target_prot['Gene_Name']

        # Find if plant compounds connect to the target
        compounds = cls.chems_df[cls.chems_df['Plant_Source'] == p_id]
        if compounds.empty:
            return f"🤖 **Assistant:** Mapped specimen **{p_name}** has no active chemical isolates."

        bridge_chem = None
        confidence = 0.0

        for _, chem in compounds.iterrows():
            c_name = chem['Chemical_Name']
            match = cls.predictions_df[
                (cls.predictions_df['Chemical'].str.lower() == c_name.lower()) & 
                (cls.predictions_df['Target Protein'].str.lower() == pr_name.lower())
            ]
            if not match.empty:
                bridge_chem = c_name
                confidence = float(match.iloc[0]['Confidence'])
                break

        if bridge_chem:
            return f"""
            🗺️ **GNN Mapped Pathway Discovery Found:**
            
            <div style="background-color: var(--deep-space); padding: 15px; border-radius: 8px; border-left: 4px solid var(--accent-blue); line-height: 1.8; margin-top: 10px;">
                <strong>🌱 Plant Source:</strong> {p_name}<br/>
                <span style="color: var(--text-muted); display:block; text-align:center; font-size:1.2rem; margin: -5px 0;">↓ contains</span>
                <strong>🧪 Isolated Compound:</strong> {bridge_chem}<br/>
                <span style="color: var(--text-muted); display:block; text-align:center; font-size:1.2rem; margin: -5px 0;">↓ targets (GNN Predicted)</span>
                <strong>🧬 Receptor Target:</strong> {pr_name} (Gene: {pr_gene})<br/>
                <hr style="border:none; border-top:1px solid var(--border-color); margin:8px 0;"/>
                <strong>🎯 AI Prediction Confidence:</strong> <span style="color: var(--accent-emerald); font-weight:bold;">{confidence:.2%}</span>
            </div>
            """
            
        return f"🤖 **Assistant:** While **{p_name}** contains bioactive compounds, our GNN has not predicted high-affinity interactions between them and **{pr_name}**."

    # =================================================================
    # RESPONSE FORMATTING ENGINE
    # =================================================================

    @classmethod
    def _format_plant_response(cls, row):
        plant_id = row['Plant_ID']
        chems = cls.chems_df[cls.chems_df['Plant_Source'] == plant_id]['Chemical_Name'].tolist()
        chem_str = ", ".join(chems) if chems else "No listed active isolates."
        
        return f"""
        🌱 **Botanical Specimen Mapped Profile:**
        
        - **Common Name:** {row['Common_Name_of_Plant']}
        - **Scientific Taxonomy:** *{row.get('Scientific_Name', 'Taxonomy pending')}*
        - **Traditional Medical Efficacy:** {row.get('Traditional_Uses', 'N/A')}
        - **Active Isolated Compounds:** {chem_str}
        <br/>*Navigate to the Specimens Page or click on the specimen cards to run automated pathway predictions.*
        """

    @classmethod
    def _format_chemical_response(cls, row):
        chem_name = row['Chemical_Name']
        cid = int(row['PubChem_CID'])
        p_id = row['Plant_Source']
        
        plant_match = cls.plants_df[cls.plants_df['Plant_ID'] == p_id]
        plant_name = plant_match['Common_Name_of_Plant'].values[0] if not plant_match.empty else "N/A"
        
        # Fetch properties dynamically from PubChem PUG REST API
        api_data = PubChemService.fetch_molecular_data(cid)
        
        return f"""
        🧪 **Phytochemical Specimen Molecular Profile:**
        
        - **Compound Name:** {chem_name}
        - **PubChem CID:** {cid}
        - **Molecular Formula:** <code>{api_data.get('formula', 'N/A')}</code>
        - **Botanical Origin Specimen:** {plant_name}
        - **IUPAC Systematic Name:** {api_data.get('iupac', 'N/A')}
        - **SMILES string:** <code>{api_data.get('smiles', 'N/A')}</code>
        """

    @classmethod
    def _format_protein_response(cls, row):
        prot_name = row['Protein_Name']
        gene = row['Gene_Name']
        uniprot_id = row['UniProt_ID']
        
        return f"""
        🧬 **Target Receptor Pathological Profile:**
        
        - **Protein Name:** {prot_name}
        - **Gene Symbol:** {gene}
        - **UniProt Accession ID:** <code>{uniprot_id}</code>
        - **Pathological Function:** {row.get('Biological_Function', 'Biological pathway metadata mapped inside protein database.')}
        """

    # =================================================================
    # CONVERSATIONAL CONTEXT MEMORY & HELPERS
    # =================================================================

    @classmethod
    def _resolve_pronoun_context(cls, query_clean, session_id):
        """
        Replaces conversational pronouns ("it", "this compound") 
        with the last searched entity name.
        """
        session_data = cls.conversational_memory.get(session_id)
        if not session_data:
            return query_clean
            
        pronoun_patterns = [r"\bit\b", r"\bthis plant\b", r"\bthis compound\b", r"\bthis protein\b", r"\bthis target\b"]
        
        for pattern in pronoun_patterns:
            if re.search(pattern, query_clean):
                query_clean = re.sub(pattern, session_data["last_entity_name"].lower(), query_clean)
                break
                
        return query_clean

    @classmethod
    def _set_session_context(cls, session_id, entity_type, entity_name):
        cls.conversational_memory[session_id] = {
            "last_entity_type": entity_type,
            "last_entity_name": entity_name
        }

    @classmethod
    def _generate_spelling_suggestions(cls, query):
        """
        Finds spelling suggestions if no exact entity matches.
        """
        query_words = query.lower().split()
        suggestions = []
        
        # Gather all valid database names
        all_labels = []
        all_labels.extend(cls.plants_df['Common_Name_of_Plant'].tolist())
        all_labels.extend(cls.chems_df['Chemical_Name'].tolist())
        all_labels.extend(cls.prots_df['Protein_Name'].tolist())
        all_labels.extend(cls.prots_df['Gene_Name'].tolist())

        for word in query_words:
            if len(word) < 4:
                continue
            for label in all_labels:
                if word in label.lower() or label.lower() in word:
                    if label not in suggestions:
                        suggestions.append(label)

        if suggestions:
            suggest_str = ", ".join([f"<strong>{s}</strong>" for s in suggestions[:3]])
            return f"🤖 **Assistant:** I couldn't locate an exact match. <br/>Did you mean: {suggest_str}?"
            
        return "🤖 **Assistant:** I couldn't find an exact match in our botanical databases. Try asking: *'Tell me about Gymnema'* or *'Show compounds in Coriander'*."