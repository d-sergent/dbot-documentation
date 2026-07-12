from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def check_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY non trouvée dans .env")
        return

    print(f"🔑 Clé trouvée (se termine par ...{api_key[-4:]})")
    client = genai.Client(api_key=api_key)

    print("\n--- Modèles Disponibles ---")
    try:
        models = client.models.list()
        for m in models:
            if m.supported_actions and "generateContent" in m.supported_actions:
                print(f"✅ {m.name} (Pris en charge)")
    except Exception as e:
        print(f"❌ Erreur lors du listage des modèles : {e}")
        return

    print("\n--- Test de Génération (Free Tier Check) ---")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Bonjour, es-tu opérationnel ? Réponds par 'OUI'."
        )
        print(f"🤖 Réponse : {response.text.strip()}")
        print("✅ Le Free Tier semble actif et fonctionnel.")
    except Exception as e:
        print(f"❌ Erreur de génération : {e}")

if __name__ == "__main__":
    check_gemini()
