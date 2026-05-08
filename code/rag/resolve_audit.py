import os
import re
import json

# Chemins
AUDIT_FILE = "/Users/Shared/Mon Google Drive Physique/Documentation/annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md"
QUESTIONS_JSON = "/Users/Shared/Mon Google Drive Physique/Documentation/annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json"
OUTPUT_PROMPT = "/Users/Shared/Mon Google Drive Physique/Documentation/annexes/Outils_de_Travail/RAG/PROMPT_CORRECTION.md"

def load_questions_with_answers(json_path):
    """Charge le fichier JSON structuré avec questions et réponses"""
    if not os.path.exists(json_path):
        print(f"❌ Fichier JSON non trouvé : {json_path}")
        return []
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
        return questions
    except Exception as e:
        print(f"❌ Erreur lors du chargement du JSON : {e}")
        return []

def main():
    print("======================================================")
    print("🤖 ASSISTANT DE RÉSOLUTION D'AUDIT D-BOT")
    print("======================================================\n")
    
    # Charger les questions avec réponses depuis le JSON structuré
    questions = load_questions_with_answers(QUESTIONS_JSON)
    
    if not questions:
        print("✅ Aucune question trouvée. Tout semble parfait !")
        return

    print(f"🔍 {len(questions)} question(s) d'intégrité détectée(s).")
    print(f"📥 Chargées depuis : {QUESTIONS_JSON}\n")
    
    # Vérifier l'existence du fichier d'audit référencé dans le prompt
    if not os.path.exists(AUDIT_FILE):
        print(f"⚠️  ATTENTION : Le fichier d'audit {AUDIT_FILE} n'existe pas.")
        print(f"⚠️  Le prompt généré demande à l'agent de le lire, ce qui causera une erreur.\n")
    else:
        print(f"✅ Fichier d'audit trouvé : {AUDIT_FILE}\n")
    
    answers = []
    for i, q in enumerate(questions, 1):
        print(f"--- Question {i} / {len(questions)} ---")
        print(f"📌 Thème : {q.get('section', 'Contexte inconnu')}")
        print(f"❓ {q.get('question', '')}\n")
        
        # Utiliser la réponse du JSON si présente
        ans = q.get('answer', '').strip()
        if ans:
            print(f"🤖 Réponse IA : {ans}\n")
            answers.append(f"- Décision pour '{q.get('section', 'Inconnu')}' : {ans}")
        else:
            print(f"⚠️  Aucune réponse fournie pour cette question.\n")
        
        print("")
        
    if not answers:
        print("❌ Aucune réponse fournie. Annulation.")
        return

    # Génération du prompt agentique
    prompt = f"""Lis le fichier d'audit `annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md`. 
J'ai analysé les incohérences. Voici mes décisions techniques officielles pour mettre à jour la documentation :

{chr(10).join(answers)}

Ta mission :
1. Scanne l'ensemble de la documentation (avec tes outils de recherche) pour localiser tous les fichiers qui contiennent les anciennes valeurs contradictoires.
2. RÈGLE D'OR : Ne touche jamais aux valeurs situées dans des études d'hypothèses, des alternatives ou des brouillons. Uniquement les spécifications de la version officielle.
3. PRÉPARE UN PLAN DOCUMENTÉ : Crée un fichier markdown `annexes/Outils_de_Travail/RAG/PLAN_CORRECTION.md`. 
   Dans ce fichier, tu dois :
   - Rappeler mes décisions techniques (pour assurer un suivi clair).
   - Lister précisément les fichiers que tu vas modifier, avec "Ancienne valeur -> Nouvelle valeur".
   - Lister les équations/calculs (levier, couple, etc.) que tu vas devoir recalculer.
4. ATTENDS MA VALIDATION : Ne modifie aucun autre fichier tant que je n'ai pas lu le plan et répondu "OK".
5. CRITIQUE : Une fois validé, modifie les fichiers de doc et mets à jour les résultats mathématiques."""

    with open(OUTPUT_PROMPT, "w", encoding="utf-8") as f:
        f.write(prompt)

    print("======================================================")
    print("✅ PROMPT GÉNÉRÉ AVEC SUCCÈS !")
    print("======================================================")
    print("Le prompt a été copié et sauvegardé.")
    print("Pour exécuter la correction, collez ce texte dans l'interface de votre choix :")
    print("  1. ANTIGRAVITY : Collez ici même pour que je (Antigravity) m'en charge.")
    print("  2. CONTINUE (VS Code) : Collez dans le chat pour utiliser l'IA de votre choix (OpenRouter, locale, etc).")
    print("  3. vMLX STUDIO : Collez dans le chat si le serveur MCP y est actif.")
    print("------------------------------------------------------\n")
    print("\033[96m" + prompt + "\033[0m")
    print("\n======================================================")
    print(f"💾 Ce prompt a aussi été sauvegardé dans : {OUTPUT_PROMPT}")

if __name__ == "__main__":
    main()
