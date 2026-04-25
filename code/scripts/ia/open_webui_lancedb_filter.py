"""
title: LanceDB Expert RAG
author: D-Bot Project
author_url: https://github.com/d-sergent/dbot-documentation
version: 1.0.0
"""

import os
import lancedb
from pydantic import BaseModel, Field
from typing import Optional, List

class Filter:
    class Valves(BaseModel):
        db_path: str = Field(
            default="/Users/Shared/AI_Shared_Knowledge/lancedb",
            description="Chemin vers la base LanceDB partagée."
        )
        collection_name: str = Field(
            default="technical_docs",
            description="Nom de la table de documentation."
        )
        top_k: int = Field(
            default=5,
            description="Nombre de résultats à récupérer."
        )

    def __init__(self):
        self.valves = self.Valves()

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Récupération de la question de l'utilisateur
        messages = body.get("messages", [])
        if not messages:
            return body
        
        last_message = messages[-1]["content"]
        
        try:
            # Connexion à la base LanceDB
            db = lancedb.connect(self.valves.db_path)
            
            # Vérifier si la table existe
            if self.valves.collection_name not in db.table_names():
                print(f"⚠️ Table {self.valves.collection_name} non trouvée.")
                return body

            tbl = db.open_table(self.valves.collection_name)
            
            # Recherche sémantique
            results = tbl.search(last_message).limit(self.valves.top_k).to_list()
            
            if results:
                context = "\n".join([f"- {r['text']}" for r in results])
                
                # Injection du contexte dans le message système ou avant la question
                prompt_injection = f"\n\nCONTEXTE TECHNIQUE (LanceDB) :\n{context}\n\nUtilise ce contexte pour répondre à la question suivante."
                messages[-1]["content"] = prompt_injection + "\n\nQUESTION : " + last_message
                
                print(f"✅ RAG activé : {len(results)} extraits injectés.")
            
        except Exception as e:
            print(f"❌ Erreur RAG : {e}")
            
        return body
