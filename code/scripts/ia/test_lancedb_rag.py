import os
import lancedb
import pypdf
from typing import List

# Configuration des chemins (Partagé)
DB_PATH = "/Users/Shared/AI_Shared_Knowledge/lancedb"
DOCS_PATH = "/Users/Shared/Mon Google Drive Physique/Documentation" # Dossier source

def test_indexation():
    print(f"--- Initialisation de LanceDB sur {DB_PATH} ---")
    db = lancedb.connect(DB_PATH)
    
    # Trouver un PDF de test dans la doc
    pdf_files = [f for f in os.listdir(DOCS_PATH) if f.endswith('.pdf')]
    if not pdf_files:
        # Chercher dans les sous-dossiers si nécessaire
        for root, dirs, files in os.walk(DOCS_PATH):
            for file in files:
                if file.endswith(".pdf"):
                    pdf_files.append(os.path.join(root, file))
                    break
            if pdf_files: break

    if not pdf_files:
        print("❌ Aucun fichier PDF trouvé pour le test dans le répertoire Documentation.")
        return

    test_file = pdf_files[0] if '/' in pdf_files[0] else os.path.join(DOCS_PATH, pdf_files[0])
    print(f"📖 Lecture du fichier de test : {os.path.basename(test_file)}")

    # Extraction du texte
    try:
        reader = pypdf.PdfReader(test_file)
        data = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                data.append({
                    "text": text,
                    "metadata": {"source": os.path.basename(test_file), "page": i + 1}
                })
        
        print(f"✅ {len(data)} pages extraites.")

        # Création de la table (mode overwrite pour le test)
        table_name = "test_table"
        tbl = db.create_table(table_name, data=data, mode="overwrite")
        print(f"🚀 Table '{table_name}' créée avec succès dans LanceDB.")

        # Test de recherche simple (FTS ou Vectorielle)
        query = "robot" # Terme générique
        print(f"🔍 Recherche du terme : '{query}'...")
        results = tbl.search(query).limit(3).to_list()
        
        if results:
            print(f"✨ {len(results)} résultats trouvés :")
            for res in results:
                print(f" - [{res['metadata']['source']} p.{res['metadata']['page']}] : {res['text'][:100]}...")
        else:
            print("⚠️ Aucun résultat trouvé (vérifiez le contenu du PDF).")

    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")

if __name__ == "__main__":
    # S'assurer que le dossier DB existe
    os.makedirs(DB_PATH, exist_ok=True)
    test_indexation()
