import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def check_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY non trouvée dans .env")
        return

    print(f"🔑 Clé trouvée (se termine par ...{api_key[-4:]})")
    genai.configure(api_key=api_key)

    print("\n--- Modèles Disponibles ---")
    try:
        models = genai.list_models()
        for m in models:
            if "generateContent" in m.supported_generation_methods:
                print(f"✅ {m.name} (Pris en charge)")
    except Exception as e:
        print(f"❌ Erreur lors du listage des modèles : {e}")
        return

    print("\n--- Test de Génération (Free Tier Check) ---")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Bonjour, es-tu opérationnel ? Réponds par 'OUI'.")
        print(f"🤖 Réponse : {response.text.strip()}")
        print("✅ Le Free Tier semble actif et fonctionnel.")
    except Exception as e:
        print(f"❌ Erreur de génération : {e}")

if __name__ == "__main__":
    check_gemini()
