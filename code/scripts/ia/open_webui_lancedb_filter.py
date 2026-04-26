import os
import lancedb
from pydantic import BaseModel, Field
from typing import Optional, List

class Tools:
    def __init__(self):
        # Configuration des chemins
        self.db_path = "/Users/Shared/AI_Shared_Knowledge/lancedb"
        self.collection_name = "technical_docs"

    def search_technical_docs(self, query: str) -> str:
        """
        Recherche des informations techniques précises dans la documentation locale du robot (datasheets, specs moteurs, etc.).
        :param query: La question technique ou les mots-clés de recherche.
        :return: Les extraits les plus pertinents trouvés dans la base de connaissances.
        """
        try:
            # Connexion à la base LanceDB
            db = lancedb.connect(self.db_path)
            
            # Vérifier si la table existe
            if self.collection_name not in db.table_names():
                return "⚠️ Erreur : La base de documentation n'est pas encore indexée dans LanceDB."

            tbl = db.open_table(self.collection_name)
            
            # Recherche sémantique (top 5)
            results = tbl.search(query).limit(5).to_list()
            
            if not results:
                return "🔍 Aucune information pertinente trouvée dans la documentation locale pour cette requête."

            # Formatage de la réponse pour l'IA
            context = "\n\n".join([
                f"--- SOURCE : {r['metadata'].get('source', 'Inconnu')} (Page {r['metadata'].get('page', '?')}) ---\n{r['text']}" 
                for r in results
            ])
            
            return f"Voici les extraits de la documentation technique locale :\n\n{context}"
            
        except Exception as e:
            return f"❌ Erreur lors de la recherche dans LanceDB : {str(e)}"
