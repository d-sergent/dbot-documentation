import ollama
import time

class DbotBrain:
    """
    Interface avec le LLM local (Ollama) pour générer les réponses du robot.
    Gère le contexte de la conversation et le prompt système.
    """
    def __init__(self, model_name="qwen2.5:3b"):
        self.model_name = model_name
        
        # Le Prompt Système définit la personnalité du robot
        self.system_prompt = (
            "Tu es D-Bot, un robot quadrupède compagnon, intelligent et amical. "
            "Règle 1 : Tes réponses doivent être toujours très concises (2 à 3 phrases maximum) pour être lues à l'oral. "
            "Règle 2 : Ne fais jamais de listes à puces. "
            "Règle 3 : Réponds toujours de manière directe et en français."
        )
        
        self.reset_memory()
        print(f"[Cerveau] Initialisé avec le modèle local : {self.model_name}")

    def reset_memory(self):
        """Efface l'historique de la conversation."""
        self.chat_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def generate_response(self, user_text: str) -> str:
        """
        Envoie le texte de l'utilisateur au LLM local et retourne la réponse.
        Garde en mémoire les messages précédents.
        """
        self.chat_history.append({"role": "user", "content": user_text})
        
        try:
            start_time = time.time()
            
            # Appel API ultra-rapide en local (localhost:11434)
            response = ollama.chat(
                model=self.model_name,
                messages=self.chat_history
            )
            
            elapsed = time.time() - start_time
            ai_text = response['message']['content']
            
            # Ajoute la réponse à l'historique
            self.chat_history.append({"role": "assistant", "content": ai_text})
            
            print(f"🧠 [Cerveau] Réponse générée localement en {elapsed:.2f}s")
            return ai_text
            
        except Exception as e:
            print(f"❌ [Cerveau] Erreur Ollama : {e}")
            return "Une erreur de connexion interne avec mon réseau de neurones vient de se produire."

    def trim_memory(self, max_messages=10):
        """Évite que l'historique ne devienne trop lourd pour la RAM de 8 Go."""
        # Garde toujours le prompt système (index 0)
        if len(self.chat_history) > max_messages + 1:
            self.chat_history = [self.chat_history[0]] + self.chat_history[-(max_messages):]

if __name__ == "__main__":
    # Test unitaire rapide
    brain = DbotBrain()
    print("\n--- Test Cerveau Local ---")
    question = "Bonjour D-bot, comment te sens-tu ?"
    print(f"👤 User: {question}")
    reponse = brain.generate_response(question)
    print(f"🤖 D-Bot: {reponse}")
