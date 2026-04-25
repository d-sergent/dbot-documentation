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

    for test_file in pdf_files:
        full_path = test_file if '/' in test_file else os.path.join(root, test_file)
        print(f"📖 Tentative de lecture : {os.path.basename(full_path)}")

        try:
            reader = pypdf.PdfReader(full_path)
            data = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and len(text.strip()) > 10:
                    data.append({
                        "text": text,
                        "metadata": {"source": os.path.basename(full_path), "page": i + 1}
                    })
            
            if not data:
                print(f"⚠️ Aucun texte extrait de {os.path.basename(full_path)}, essai du fichier suivant...")
                continue

            print(f"✅ {len(data)} pages extraites.")

            # Création de la table
            table_name = "test_table"
            tbl = db.create_table(table_name, data=data, mode="overwrite")
            print(f"🚀 Table '{table_name}' créée avec succès.")

            # Test de recherche
            query = "robot"
            print(f"🔍 Recherche du terme : '{query}'...")
            results = tbl.search(query).limit(3).to_list()
            
            if results:
                print(f"✨ {len(results)} résultats trouvés.")
                return # Succès, on s'arrête là
            
        except Exception as e:
            print(f"⚠️ Erreur sur {os.path.basename(full_path)} : {e}")
            continue

    print("❌ Échec : Aucun des PDFs testés n'a pu être indexé.")

if __name__ == "__main__":
    # S'assurer que le dossier DB existe
    os.makedirs(DB_PATH, exist_ok=True)
    test_indexation()
