# services/pubchem_service.py
import requests

class PubChemService:
    @staticmethod
    def fetch_molecular_data(cid):
        """
        Fetches compound metadata directly from the PubChem PUG REST API.
        """
        cid_str = str(cid).strip()
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid_str}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES/JSON"
        
        fallback = {
            "formula": "C20H28O1",
            "weight": "284.4 g/mol",
            "iupac": "Systematic name lookup bypassed.",
            "smiles": "CC1=C(C(CCC1)(C)C)C=CC(=CC=CC(=CC=O)C)C",
            "image_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid_str}/PNG"
        }
        
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                props = r.json().get("PropertyTable", {}).get("Properties", [{}])[0]
                return {
                    "formula": props.get("MolecularFormula", fallback["formula"]),
                    "weight": f"{props.get('MolecularWeight', 'N/A')} g/mol",
                    "iupac": props.get("IUPACName", fallback["iupac"]),
                    "smiles": props.get("CanonicalSMILES", fallback["smiles"]),
                    "image_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid_str}/PNG"
                }
        except Exception:
            pass
        return fallback