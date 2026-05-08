# 05 — Audit & Intégrité (Système RAG)

## 1. Présentation
L'outil **RAG Audit** est un système d'assurance qualité automatique pour la documentation du D-Bot. Il utilise les capacités de raisonnement du **Graph-RAG** pour comparer les informations dispersées dans plus de 100 fichiers et détecter les contradictions techniques (poids, moteurs, bus CAN, capteurs).

## 2. Fonctionnement Technique
Contrairement à une recherche classique, l'audit utilise le **Mode Global** du RAG :
- Il analyse les entités (ex: "Masse totale") à travers tout le graphe de connaissances.
- Il corrèle les relations entre les documents (ex: "La Liste d'achats dit X, mais la Synthèse dit Y").
- Il synthétise les divergences sous forme de rapport Markdown.

## 3. Utilisation

### Lancement de l'Audit
Pour générer un nouveau rapport d'intégrité, exécutez la commande suivante dans le terminal :
```bash
python3 code/rag/check_integrity.py
```

### Emplacement du Rapport
Le rapport est généré et écrasé à chaque passage dans :
`annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md`

## 4. Processus de Correction (Boucle Humaine)
Chaque section du rapport d'audit se termine par une série de **Questions de Validation**.

**Procédure recommandée :**
1. **Lecture** : Parcourez le fichier `AUDIT_INTEGRITE.md`.
2. **Arbitrage** : Pour chaque incohérence, décidez quelle source est la vérité (généralement le document le plus récent ou la synthèse).
3. **Correction Assistée** : Vous pouvez copier-coller la question proposée par l'audit directement dans votre interface de chat avec l'IA (Antigravity) pour qu'elle réalise la correction à votre place.
   - *Exemple* : "L'audit propose : 'Voulez-vous que je mette à jour le poids à 40.2kg dans le fichier 01_Synthese ?'. Répondez : 'Oui, fais-le'."

## 5. Maintenance de l'outil
Les thématiques d'audit (Masse, Cinématique, Électronique, IA) sont définies dans le dictionnaire `AUDITS` au début du script `code/rag/check_integrity.py`. Vous pouvez y ajouter de nouveaux axes d'analyse (ex: budget, matériaux, conformité logicielle) selon l'évolution du projet.

---
*Dernière mise à jour : Mai 2026*
