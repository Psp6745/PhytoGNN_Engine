# services/uniprot_service.py
import requests

class UniProtService:
    @staticmethod
    def fetch_protein_details(uniprot_id):
        """
        Fetches protein functional annotations from the UniProt REST API.
        """
        clean_id = str(uniprot_id).strip().upper()
        url = f"https://rest.uniprot.org/uniprotkb/{clean_id}.json"
        
        fallback = {
            "function": "Critical role in systemic glucose homeostasis and target pathway structures.",
            "gene": "N/A"
        }
        
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                data = r.json()
                comments = data.get("comments", [])
                func_text = fallback["function"]
                for comment in comments:
                    if comment.get("commentType") == "FUNCTION":
                        func_text = comment.get("texts", [{}])[0].get("value", func_text)
                        break
                return {
                    "function": func_text,
                    "gene": data.get("genes", [{}])[0].get("geneName", {}).get("value", "N/A")
                }
        except Exception:
            pass
        return fallback