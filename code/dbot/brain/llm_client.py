"""
llm_client.py — Cerveau IA de D-Bot (Interface Ollama locale)

Ce module gère la communication avec le serveur Ollama local (localhost:11434).
Il implémente la mémoire conversationnelle et le Function Calling (recherche web).

Prérequis :
  pip install ollama ddgs
  ollama serve  (doit être actif avant de lancer le chatbot)

Sélection du modèle (par ordre de priorité) :
  1. Variable d'environnement : DBOT_LLM_MODEL=nemotron-mini
  2. Argument constructeur  : DbotBrain(model_name="gemma3:4b")
  3. Défaut                 : nemotron-mini (recommandé Mai 2026)

Référence : annexes/jetson/installation/47_Cerveau_IA_Ollama_LLM.md
"""

import ollama
import os
import time

try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False
    print("⚠ [Cerveau] ddgs non installé. Recherche web désactivée. Lancez : pip3 install ddgs")


# Modèle par défaut recommandé (Mai 2026) — voir Doc 47 pour le comparatif
# Peut être surchargé via la variable d'environnement DBOT_LLM_MODEL
DEFAULT_MODEL = os.environ.get("DBOT_LLM_MODEL", "nemotron-mini")


def perform_web_search(query: str) -> str:
    """
    Interroge DuckDuckGo et retourne un résumé des résultats.
    Utilisé par le LLM via Function Calling pour les questions sur l'actualité.

    Args:
        query (str): Requête de recherche.

    Returns:
        str: Résumé des 2 premiers résultats, ou message d'erreur.
    """
    print(f"🔍 [Cerveau] Recherche web : '{query}'...")
    if not HAS_DDGS:
        return "Erreur : l'outil duckduckgo-search n'est pas installé."
    try:
        with DDGS() as ddgs:
            # 2 résultats max pour économiser la RAM de la Jetson
            results = [r for r in ddgs.text(query, max_results=2)]
            if not results:
                return "Aucun résultat trouvé."
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Erreur réseau DuckDuckGo : {e}"


# Schéma de l'outil de recherche (standard Ollama Function Calling)
WEB_SEARCH_TOOL = {
    'type': 'function',
    'function': {
        'name': 'search_web',
        'description': (
            'Recherche des données factuelles à jour sur internet. '
            'À utiliser IMPÉRATIVEMENT si la question demande une actualité, '
            'une date précise ou un fait hors de tes connaissances.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': 'Les mots-clés de la recherche (ex: Vainqueur ballon or 2025)'
                }
            },
            'required': ['query']
        }
    }
}


class DbotBrain:
    """
    Interface avec le LLM local (Ollama) pour la conversation de D-Bot.

    Gère la mémoire conversationnelle et le Function Calling (recherche web).
    Le modèle est sélectionnable via la variable d'environnement DBOT_LLM_MODEL.

    Args:
        model_name (str): Nom du modèle Ollama. Par défaut : DEFAULT_MODEL
            (défini par DBOT_LLM_MODEL ou 'nemotron-mini').
            Voir Doc 47 pour le comparatif complet des modèles.

    Raises:
        Exception: Si le serveur Ollama n'est pas accessible (vérifiez `ollama serve`).

    Example:
        brain = DbotBrain()                        # Utilise le modèle recommandé
        brain = DbotBrain(model_name="qwen2.5:3b") # Forcer un modèle spécifique
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.system_prompt = (
            "Tu es D-Bot, un robot quadrupède compagnon, intelligent et amical. "
            "Règle 1 : Tes réponses doivent être toujours très concises pour l'oral, "
            "jamais de longues explications. "
            "Règle 2 : Réponds systématiquement en français. "
            "Règle 3 : Ne fais jamais de supposition sur des événements récents, "
            "utilise ton outil search_web si tu as le moindre doute."
        )
        self.reset_memory()
        print(f"🧠 [Cerveau] Initialisé — Modèle : {self.model_name}")
        print(f"   (Pour changer : DBOT_LLM_MODEL=<nom> python3 chatbot_local_v2.py)")

    def reset_memory(self):
        """Remet la conversation à zéro (garde le prompt système)."""
        self.chat_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def generate_response(self, user_text: str) -> str:
        """
        Génère une réponse à partir du texte utilisateur.

        Processus :
          1. Appel au LLM — il répond ou demande à utiliser un outil (web search).
          2. Si Function Calling : exécute la recherche et rappelle le LLM.
          3. Retourne la réponse finale.

        Args:
            user_text (str): Phrase de l'utilisateur transcrite par Whisper.

        Returns:
            str: Réponse du robot à synthétiser via TTS.
        """
        self.chat_history.append({"role": "user", "content": user_text})

        try:
            start_time = time.time()

            # Acte 1 : Le LLM répond ou demande l'outil
            response = ollama.chat(
                model=self.model_name,
                messages=self.chat_history,
                tools=[WEB_SEARCH_TOOL]
            )

            # L'IA veut-elle utiliser la recherche web ?
            if response['message'].get('tool_calls'):
                self.chat_history.append(response['message'])

                for tool in response['message']['tool_calls']:
                    if tool['function']['name'] == 'search_web':
                        query_arg = tool['function']['arguments'].get('query')
                        search_result = perform_web_search(query_arg)
                        self.chat_history.append({
                            'role': 'tool',
                            'content': search_result,
                            'name': 'search_web'
                        })

                # Acte 2 : Le LLM lit les résultats et formule la réponse finale
                response = ollama.chat(
                    model=self.model_name,
                    messages=self.chat_history
                )

            elapsed = time.time() - start_time
            ai_text = response['message']['content']
            self.chat_history.append({"role": "assistant", "content": ai_text})

            print(f"🧠 [Cerveau] Réponse en {elapsed:.2f}s ({self.model_name})")
            return ai_text

        except Exception as e:
            print(f"❌ [Cerveau] Erreur Ollama : {e}")
            print("   💡 Vérifiez que 'ollama serve' est actif (voir Doc 47)")
            return "Une interférence vient de perturber mon réseau neuronal."

    def trim_memory(self, max_messages: int = 10):
        """
        Écrête l'historique pour éviter la saturation de la VRAM Jetson.
        Conserve toujours le message système en position 0.

        Args:
            max_messages (int): Nombre de messages à conserver (hors système).
        """
        if len(self.chat_history) > max_messages + 1:
            self.chat_history = [self.chat_history[0]] + self.chat_history[-max_messages:]


if __name__ == "__main__":
    print(f"\n--- Test Cerveau D-Bot (modèle : {DEFAULT_MODEL}) ---")
    print("Assurez-vous qu'Ollama est actif : ollama serve\n")

    brain = DbotBrain()
    question = "Quelles sont les grosses annonces sur les robots humanoïdes le mois dernier ?"
    print(f"👤 Question : {question}")
    reponse = brain.generate_response(question)
    print(f"🤖 D-Bot : {reponse}")
