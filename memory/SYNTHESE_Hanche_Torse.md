# Synthèse : Hanche & Torse - État de l'Art

Ce document résume la configuration finale et aboutie du torse, du bassin et des hanches du D-Bot.

## 1. Hanches (Pelvis)
L'architecture retenue est la **Configuration Hybride B** pour optimiser le poids tout en conservant un couple frontal élevé.
- **Hanche Pitch (Flexion)** : **RS-04** (120 N.m pic) — ✅ Marge +43% dynamique.
- **Hanche Roll (Latéral)** : **RS-03** (60 N.m pic) — ✅ Marge +200% dynamique.
- **Massif Pelvien** : Structure hybride aluminium CNC et **PA12-CF avec allégement Isogrid** (remplissage gyroid adaptatif).

## 2. Torse & Dimensions
La structure centrale est une **cage en aluminium 6061/7075-T6** usinée sur NestWorks C500.
- **Hauteur (Épaule -> Hanche)** : 420 mm.
- **Largeur** : 300 mm.
- **Profondeur** : 220 mm.
- **Centre de Masse (CoM)** : Centralisé au niveau du tiers inférieur du torse (batterie 12S).

## 3. Épaules & Bras (Membres Supérieurs)
- **Épaule Pitch** : **RS-04** (120 N.m).
- **Épaule Roll** : **RS-03** (60 N.m).
- **Coude** : **RS-06** (36 N.m).
- **Mains** : **D-Hand Hybrid (8 DOF)** — ~785 g par main.

## 4. Cou & Tête
- **Actionneurs Cou** : **2× RS-05** (Pan/Tilt). Montage superposé dans une enveloppe de 250 mm.
- **Visserie** : Généralisation du Titane et Alu 7075 pour les brackets mobiles.

## 5. Liens et Archives
- **Dimensions de Synthèse** : [28_Dimensions_Physiques_Synthese.md](../28_Dimensions_Physiques_Synthese.md)
- **Étude Bloc Pelvien** : [26_Etude_Bloc_Pelvien_Hanche.md](../26_Etude_Bloc_Pelvien_Hanche.md)
- **Architecture de Masse** : [16_Conclusions_Architecture_DBot.md](../16_Conclusions_Architecture_DBot.md)
- **Archives** : [Archives/ETUDE_Hanche_Double_RS04.md](../Archives/ETUDE_Hanche_Double_RS04.md) (Option A abandonnée pour gain de masse)
