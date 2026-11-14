# 🧠 Guide des Modèles IA & Stratégie OpenRouter (Architecture M1 Max 64Go)

L'intelligence du D-Bot repose sur une architecture hybride exploitant la puissance locale (Apple Silicon) et les ressources Cloud gratuites. Ce document recense les meilleurs modèles disponibles via OpenRouter (Cloud gratuit) et vMLX (Local), classés par cas d'usage.

## 1. Raisonnement Global & Analyse Mécanique (Le "Cerveau" général)

**Objectif :** Analyser des documents complexes, comparer des choix architecturaux (ex: Poignet DOF, moteurs), brainstorming mécanique.

*   🏆 **meta-llama/llama-3.3-70b-instruct:free (OpenRouter)**
    *   **Pourquoi :** C'est le meilleur modèle open-source polyvalent actuel. Il possède un raisonnement logique très solide, comparable à GPT-4.
*   🏋️ **nousresearch/hermes-3-llama-3.1-405b:free (OpenRouter)**
    *   **Pourquoi :** Un modèle titanesque (405 Milliards de paramètres). Lent, mais doté d'une compréhension chirurgicale pour les analyses profondes (manuels techniques, datasheets).
*   💻 **Local (vMLX) :** Mistral-Small-4-119B / Qwen 35B
    *   **Pourquoi :** Confidentialité totale, exploite la VRAM unifiée de 64Go du Mac M1 Max sans latence réseau.

## 2. Génération de Code (L'ingénieur Logiciel)

**Objectif :** Écrire des scripts Python (RAG), du firmware C++ (ESP32/Arduino), configurer des nœuds ROS.

*   🏆 **qwen/qwen3-coder-480b-a35b:free (OpenRouter)**
    *   **Pourquoi :** La série Qwen Coder d'Alibaba est la référence incontestée en open-source pour la programmation. Ce modèle massif excelle dans l'algorithmie complexe.
*   🥈 **qwen/qwen3-next-80b-a3b-instruct:free (OpenRouter)**
    *   **Pourquoi :** Excellente alternative plus rapide pour le code généraliste.

## 3. Tâches Rapides & Indexation RAG (Le "Travailleur à la chaîne")

**Objectif :** Indexation LightRAG (extraction d'entités/relations), formatage, micro-tâches, classification rapide.

*   🏆 **tencent/hy3-preview:free (OpenRouter)**
    *   **Pourquoi :** Le nouveau modèle phare de Tencent (Hunyuan 3) en phase preview. Actuellement doté d'un quota quasi illimité, il est **parfait pour les indexations massives** quand les autres modèles sont saturés. Très performant sur le respect des consignes.
*   🥇 **meta-llama/llama-3.2-3b-instruct:free (OpenRouter)**
    *   **Pourquoi :** Un modèle ultra-léger (3B) et donc **fulgurant**. Parfait pour le traitement de masse (ex: nettoyer un fichier de log) ou le routage de requêtes.
*   🥇 **meta-llama/llama-3.1-8b-instruct:free (OpenRouter)**
    *   **Pourquoi :** Plus équilibré que le 3B, c'est le standard de l'industrie pour les tâches rapides avec un bon niveau de raisonnement.
*   🧠 **liquid/lfm2.5-1.2b-thinking:free (OpenRouter)**
    *   **Pourquoi :** Un modèle innovant de LiquidAI conçu avec une chaîne de pensée ("Chain of Thought") malgré sa très petite taille. Idéal pour des petits puzzles logiques.
*   🔄 **Le Round-Robin Online (Gemini + OpenRouter) :**
    *   L'indexation du D-Bot s'appuie désormais sur un pool de modèles gratuits puissants exécutés en parallèle :
        1. `gemini-2.5-flash` (Très rapide, fort contexte)
        2. `gemini-3.1-flash-lite` (Vitesse extrême)
        3. `gemini-2.0-flash` (Repli Google)
        4. `meta-llama/llama-3.3-70b-instruct:free` (Filet de sécurité OpenRouter)

---

## 🚀 Pistes d'Amélioration & Nouvelles Options (Architecture Hybride)

Avec l'intégration d'OpenRouter et du parallélisme, voici les évolutions stratégiques possibles pour le D-Bot :

### A. Indexation Parallèle Haut-Débit (RAG)
Le script `index_docs.py` a été mis à jour (mode `--provider online`) pour utiliser `llm_model_max_async=4`. Au lieu d'attendre la réponse d'un LLM, l'extracteur envoie 4 requêtes simultanées au Round-Robin. Couplé au passage automatique des modèles épuisés, le temps d'indexation est divisé par 3.

### B. Le Routage Dynamique d'Intentions (Agentic Workflow)
Plutôt que d'utiliser un modèle "Moyen" pour tout faire :
1. Envoyer la question de l'utilisateur à `Llama 3.2 3B` (ultra rapide) pour qu'il identifie la **nature** de la tâche.
2. Si "Tâche = Coder", déléguer automatiquement via un outil (MCP) à `Qwen3 Coder`.
3. Si "Tâche = Mécanique", déléguer à `Llama 3.3 70B`.

### C. La Synthèse Asynchrone (Background Processing)
Pendant que vous modélisez des pièces sous Fusion 360, un script de fond peut utiliser le pool OpenRouter gratuit pour générer automatiquement les résumés `.md` de chaque nouveau plan CAO généré, sans jamais encombrer la VRAM de votre Mac.

*Dernière mise à jour : 2026-05-08*
