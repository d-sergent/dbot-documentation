# 15 — Analyse Biomécanique D-Bot (Hub)

Cette section a été restructurée pour plus de clarté. Le contenu est désormais réparti en **4 documents spécialisés** et un **document de conclusions**.

---

## Navigation

| # | Document | Contenu | Lignes |
| :---: | :--- | :--- | :---: |
| **15a** | [Locomotion & Portage (Baseline K-Bot)](./15a_Analyse_Locomotion_Baseline.md) | Paramètres physiques, couples requis marche/course/portage, faiblesses initiales | ~200 |
| **15b** | [Configurations Moteurs & Évolutions](./15b_Configurations_Moteurs.md) | Options A/B/C/D, comparatifs, DOF Roll, stabilité, capteurs FSR, algorithmes | ~900 |
| **15c** | [Révision Cardan 40.2 kg](./15c_Revision_Cardan_40_2kg.md) | Recalcul complet avec masse 40.2 kg et architecture cheville cardan 2×RS-03 | ~200 |
| **15d** | [Genou — Analyse & Solution GT3](./15d_Genou_et_Course.md) | **Document principal genou (fusionné 15d+15g)** — S1 à S5 explorées, S6 (GT3 2.5:1, 300 N.m) retenue, compatibilité F-A-R hanche validée | ~300 |
| **15e** | [Alternatives Moteurs Genou](./15e_Alternatives_Moteurs_Genou.md) | Comparatif RS-02, RS-03, RS-06 pour upgrades | ~150 |
| **15g** | [→ Redirection vers 15d](./15g_Solution_S6_Courroie_GT3_Genou.md) | Contenu fusionné dans 15d (Avril 2026) | — |
| **15h** | [Alternatives Transmission Genou](./15h_Alternatives_Transmission_Genou.md) | Archive des débats Vérins Linéaires vs Chaîne vs Courroie vs Pivots Variables | ~70 |
| **16** | [**Conclusions & Architecture Finale D-Bot**](./16_Conclusions_Architecture_DBot.md) | **Décisions finales par articulation. Lire en premier.** | ~100 |

---

## Logique de Lecture Recommandée

```
Nouveau lecteur :
  → 16_Conclusions  (résumé décisions)
  → 15c (recalcul définitif 40.2 kg)
  → 15d (course et genou)

Analyse historique :
  → 15a (baseline K-Bot)
  → 15b (toutes les options étudiées)

Ingénierie détaillée :
  → 15b §7-10 (configurations finales, capteurs)
  → 15d §12.3.1 (cinématique tirant genou)
```

---

*Document restructuré en Mars 2026 — contenu complet dans les 4 sous-documents ci-dessus.*
