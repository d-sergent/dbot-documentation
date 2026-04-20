import ollama
import time
import json

try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False
    print("⚠ [Cerveau] duckduckgo-search non installé. Exécutez : pip3 install duckduckgo-search")

def perform_web_search(query: str) -> str:
    """Interroge discrètement DuckDuckGo et retourne un résumé brut."""
    print(f"🔍 [Cerveau] Demande d'Outil : Recherche web en cours pour '{query}'...")
    if not HAS_DDGS:
        return "Erreur locale: L'outil duckduckgo-search n'est pas installé sur le système."
        
    try:
        with DDGS() as ddgs:
            # On prend juste 2 extraits pour économiser la RAM de la Jetson
            results = [r for r in ddgs.text(query, max_results=2)]
            
            if not results:
                return "Aucun résultat trouvé sur internet."
                
            # Compile les petites descriptions textuelles
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Erreur réseau lors de la recherche DuckDuckGo : {e}"

# Outil standard Ollama (Function Calling Schema JSON)
WEB_SEARCH_TOOL = {
    'type': 'function',
    'function': {
        'name': 'search_web',
        'description': 'Recherche des données factuelles à jour sur internet. A utiliser IMPÉRATIVEMENT si la question demande une actualité, une date précise ou un fait hors de tes connaissances.',
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': 'Les mots-clés de la recherche Google (ex: Vainqueur ballon d or 2025)'
                }
            },
            'required': ['query']
        }
    }
}

class DbotBrain:
    """
    Interface avec le LLM local (Ollama) augmentée de l'intelligence contextuelle.
    """
    def __init__(self, model_name="qwen2.5:3b"):
        self.model_name = model_name
        self.system_prompt = (
            "Tu es D-Bot, un robot quadrupède compagnon, intelligent et amical. "
            "Règle 1 : Tes réponses doivent être toujours très concises pour l'oral, jamais de longues explications. "
            "Règle 2 : Réponds systématiquement en français. "
            "Règle 3 : Ne fais jamais de supposition sur des événements récents, utilise ton outil search_web si tu as le moindre doute."
        )
        self.reset_memory()
        print(f"[Cerveau] Initialisé avec le modèle : {self.model_name}")

    def reset_memory(self):
        self.chat_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def generate_response(self, user_text: str) -> str:
        self.chat_history.append({"role": "user", "content": user_text})
        
        try:
            start_time = time.time()
            
            # Acte 1 : On demande au LLM s'il connaît la réponse, ou s'il a besoin que Python l'aide
            response = ollama.chat(
                model=self.model_name,
                messages=self.chat_history,
                tools=[WEB_SEARCH_TOOL]
            )
            
            # L'IA a-t-elle décidé d'utiliser l'outil au lieu de parler directement ?
            if response['message'].get('tool_calls'):
                # On ajoute ce "Mouvement de pensée" à l'historique
                self.chat_history.append(response['message'])
                
                # Exécute tous les outils demandés
                for tool in response['message']['tool_calls']:
                    if tool['function']['name'] == 'search_web':
                        query_arg = tool['function']['arguments'].get('query')
                        # Exécution du script Python de routine web
                        target_result = perform_web_search(query_arg)
                        
                        # Retourne le résultat du script (ex: 2 articles de journaux) dans le cerveau de l'IA
                        self.chat_history.append({
                            'role': 'tool',
                            'content': target_result,
                            'name': 'search_web'
                        })
                
                # Acte 2 : Deuxième appel à l'IA, maintenant elle lit l'article injecté et génère sa phrase finale !
                response = ollama.chat(
                    model=self.model_name,
                    messages=self.chat_history
                )
            
            elapsed = time.time() - start_time
            ai_text = response['message']['content']
            
            # Ajoute le discours final à la mémoire
            self.chat_history.append({"role": "assistant", "content": ai_text})
            
            print(f"🧠 [Cerveau] Réponse compilée en {elapsed:.2f}s")
            return ai_text
            
        except Exception as e:
            print(f"❌ [Cerveau] Erreur Ollama : {e}")
            return "Une interférence vient de perturber mon réseau neuronal."

    def trim_memory(self, max_messages=10):
        """Évite que l'historique ne sature le VRAIM de la Jetson."""
        if len(self.chat_history) > max_messages + 1:
            self.chat_history = [self.chat_history[0]] + self.chat_history[-(max_messages):]

if __name__ == "__main__":
    brain = DbotBrain()
    print("\n--- Test Cerveau Symbiotique (Local + Tools) ---")
    question = "Quelles sont les grosses annonces sur les robots humanoïdes le mois dernier ?"
    print(f"👤 User: {question}")
    reponse = brain.generate_response(question)
    print(f"🤖 D-Bot (Réponse finale) : {reponse}")
