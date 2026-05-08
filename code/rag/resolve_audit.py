import os
import re

# Chemins
AUDIT_FILE = "/Users/Shared/Mon Google Drive Physique/Documentation/annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md"
OUTPUT_PROMPT = "/Users/Shared/Mon Google Drive Physique/Documentation/annexes/Outils_de_Travail/RAG/PROMPT_CORRECTION.md"

def extract_questions(filepath):
    if not os.path.exists(filepath):
        print(f"❌ Fichier non trouvé : {filepath}")
        return []
    
    questions = []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            # Cherche les lignes qui commencent par "**Question"
            if line.strip().startswith("**Question"):
                # Essaie de capter le contexte (le titre h4 juste au-dessus)
                context = "Contexte inconnu"
                for j in range(i-1, max(-1, i-10), -1):
                    if lines[j].strip().startswith("####"):
                        context = lines[j].strip().replace("#### ", "")
                        break
                
                # Nettoie la question
                q_text = line.strip().replace("**Question :**", "").replace("**Question:**", "").strip()
                questions.append({"context": context, "question": q_text})
                
    return questions

def main():
    print("======================================================")
    print("🤖 ASSISTANT DE RÉSOLUTION D'AUDIT D-BOT")
    print("======================================================\n")
    
    questions = extract_questions(AUDIT_FILE)
    
    if not questions:
        print("✅ Aucune question trouvée dans l'audit. Tout semble parfait !")
        return

    print(f"🔍 {len(questions)} question(s) d'intégrité détectée(s).\n")
    
    answers = []
    for i, q in enumerate(questions, 1):
        print(f"--- Question {i} / {len(questions)} ---")
        print(f"📌 Thème : {q['context']}")
        print(f"❓ {q['question']}\n")
        
        print("Votre décision (Laissez vide pour ignorer cette question) :")
        ans = input("> ")
        
        if ans.strip():
            answers.append(f"- Décision pour '{q['context']}' : {ans.strip()}")
        print("")
        
    if not answers:
        print("❌ Aucune réponse fournie. Annulation.")
        return

    # Génération du prompt agentique
    prompt = f"""Lis le fichier d'audit `annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md`. 
J'ai analysé les incohérences. Voici mes décisions techniques officielles pour mettre à jour la documentation :

{chr(10).join(answers)}

Ta mission :
1. Fais un scan (grep_search) pour trouver tous les fichiers qui contiennent les anciennes valeurs.
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
