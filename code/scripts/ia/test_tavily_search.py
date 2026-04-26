import os
from tavily import TavilyClient

# Configuration
TAVILY_API_KEY = "VOTRE_CLE_ICI" # Ou export TAVILY_API_KEY=... dans votre terminal

def test_tavily_search(query: str):
    print(f"--- Recherche Tavily pour : '{query}' ---")
    
    # Initialisation du client
    # Il est préférable d'utiliser une variable d'environnement
    api_key = os.getenv("TAVILY_API_KEY", TAVILY_API_KEY)
    if api_key == "VOTRE_CLE_ICI":
        print("❌ Erreur : Veuillez renseigner votre clé API Tavily.")
        return

    client = TavilyClient(api_key=api_key)

    try:
        # Recherche orientée "Recherche" (search_depth="advanced")
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True, # Demande une synthèse à l'IA de Tavily
            include_raw_content=False
        )

        # Affichage de la synthèse de Tavily
        if response.get("answer"):
            print(f"\n💡 Synthèse de Tavily :\n{response['answer']}\n")

        # Affichage des sources
        print("🌐 Sources trouvées :")
        for i, res in enumerate(response.get("results", [])):
            print(f" {i+1}. [{res['title']}]({res['url']})")
            print(f"    - Score de pertinence : {res['score']:.2f}")
            # print(f"    - Extrait : {res['content'][:150]}...")

    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {e}")

if __name__ == "__main__":
    # Exemple de recherche robotique
    q = "derniers prix et specs moteur DJI M3508 avril 2026"
    test_tavily_search(q)
