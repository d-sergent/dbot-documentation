# AUDIT - Santé de la timeline Torse-123 v49

> **Statut** : audit en lecture seule réalisé le 2026-11-20 via le serveur MCP Fusion (voir [GUIDE_COMPLET_MCP_Fusion360.md](./GUIDE_COMPLET_MCP_Fusion360.md)). Aucune modification n'a été apportée à la CAO.
> **Document audité** : `Torse-123 v49` (projet `d-bot - Torse`), 1478 éléments de timeline, marqueur en fin de timeline.

## 📑 Sommaire

- [1. Synthèse](#1-synthèse)
- [2. Inventaire des 28 éléments en défaut](#2-inventaire-des-28-éléments-en-défaut)
- [3. Les 51 groupes signalés](#3-les-51-groupes-signalés)
- [4. Classement par priorité](#4-classement-par-priorité)
- [5. Protocole de correction proposé](#5-protocole-de-correction-proposé)
- [6. Limites de l'audit](#6-limites-de-laudit)

---

## 1. Synthèse

Le décompte précédent de **79 éléments non sains** se décompose en réalité ainsi :

| Catégorie | Nombre |
|---|---|
| Éléments réellement en défaut (esquisses, plans, fonctions, contraintes) | **28** |
| Groupes de timeline signalés (sans message, aucun membre défaillant détecté au premier niveau) | **51** |
| **Total initialement compté** | **79** |

Sur les 28 éléments en défaut :

- **27 sont des avertissements** (`Warning`) : Fusion utilise la géométrie en cache. La CAO reste calculable et les masses lues sont cohérentes avec la documentation (voir section 7.2 du guide).
- **1 est une erreur** (`Error`) : `DeleteFace6` dans `Capot_Verrouillage_Batterie`.
- **1 est à l'état `RolledBack`** (code 4) : `Extrusion19` dans `Bride Epaule`. Ce n'est pas une erreur de calcul, mais l'état est inattendu avec un marqueur en fin de timeline (à vérifier).

> [!IMPORTANT]
> Aucun de ces défauts ne modifie à ce jour la masse ni l'encombrement de la CAO (les valeurs lues correspondent à la documentation). Le risque est **futur** : toute modification en amont ou recalcul peut faire dériver la géométrie qui repose sur le cache.

## 2. Inventaire des 28 éléments en défaut

Légende état : `W` = avertissement (cache utilisé), `E` = erreur, `RB` = RolledBack.

| # | Élément | Index | Type | Composant propriétaire | État | Défaut signalé |
|---|---|---|---|---|---|---|
| 1 | Plan18 | 247 | Plan de construction | Racine | W | 2 faces de référence manquantes |
| 2 | Axe17 | 248 | Axe de construction | Racine | W | 1 face de référence manquante |
| 3 | Esquisse21 | 251 | Esquisse (25 profils) | Racine | W | Plan d'esquisse perdu, source de projection perdue, échec de transformation d'occurrence |
| 4 | Plan19 | 255 | Plan de construction | Racine | W | 2 faces de référence manquantes |
| 5 | Esquisse22 | 258 | Esquisse (2 profils) | Racine | W | Plan d'esquisse perdu, source de projection perdue |
| 6 | Plan20 | 260 | Plan de construction | Racine | W | 1 face de référence manquante |
| 7 | Esquisse24 | 261 | Esquisse (20 profils) | Racine | W | Source de projection perdue (2 projections) |
| 8 | Chanfrein16 | 303 | Chanfrein | **Bride Epaule** | W | 1 arête de référence perdue |
| 9 | Chanfrein17 | 304 | Chanfrein | **Bride Epaule** | W | 2 arêtes de référence perdues |
| 10 | Jeu de contraintes 47 | 308 | Contrainte d'assemblage | Racine | W | 2 faces de référence manquantes |
| 11 | Réseau C6 | 316 | Réseau circulaire | Racine | W | 1 face (axe) manquante |
| 12 | Réseau C7 | 317 | Réseau circulaire | Racine | W | 1 face (axe) manquante |
| 13 | Réseau C8 | 322 | Réseau circulaire | Racine | W | 1 face (axe) manquante |
| 14 | Réseau C9 | 323 | Réseau circulaire | Racine | W | 1 face (axe) manquante |
| 15 | Esquisse32 | 324 | Esquisse (2 profils) | Racine | W | Plan d'esquisse perdu, faces manquantes |
| 16 | Jeu de contraintes 52 | 335 | Contrainte d'assemblage | Racine | W | 1 face de référence manquante |
| 17 | Jeu de contraintes 53 | 337 | Contrainte d'assemblage | Racine | W | 1 face de référence manquante |
| 18 | Plan2 | 346 | Plan de construction | Racine | W | 2 faces de référence manquantes |
| 19 | Plan3 | 347 | Plan de construction | Racine | W | 2 faces de référence manquantes |
| 20 | Extrusion19 | 362 | Extrusion | **Bride Epaule** | RB | Aucun message (état RolledBack) |
| 21 | Esquisse55 | 810 | Esquisse (13 profils, 1021 courbes) | Racine | W | Source de projection perdue (10 projections) |
| 22 | DeleteFace4 | 826 | Suppression de face | **Capot_Verrouillage_Batterie** | W | 10 faces manquantes |
| 23 | DeleteFace5 | 827 | Suppression de face | **Capot_Verrouillage_Batterie** | W | 6 faces manquantes |
| 24 | DeleteFace6 | 828 | Suppression de face | **Capot_Verrouillage_Batterie** | **E** | 3 faces manquantes (référence perdue) |
| 25 | Plan1 | 1141 | Plan de construction | (contexte occurrence) | W | Échec de transformation de l'occurrence cible (3 échecs) |
| 26 | Esquisse1 | 1142 | Esquisse (2 profils) | **Tube transverse Epaules good** | W | Échec de transformation de l'occurrence cible |
| 27 | Epaissir1 | 1276 | Épaississement | Racine | W | Calcul incomplet : résultat partiel renvoyé |
| 28 | Extrusion10 | 1397 | Extrusion | **Tube transverse Epaules good** | W | Échec de transformation de l'occurrence propriétaire |

*Note : le composant propriétaire "Racine" signifie le composant `Torse-123 v49`. Les plans et axes de construction n'exposent pas leur composant via l'API (affiché "?" à la lecture), ils sont rattachés à la racine par défaut dans ce tableau, à confirmer.*

## 3. Les 51 groupes signalés

51 groupes (`Groupe10`, `Groupe12`, `Groupe25` à `Groupe82`) sont signalés en avertissement **sans message**. L'examen de leurs membres de premier niveau ne trouve aucun élément défaillant. L'hypothèse la plus probable est une propagation d'état (élément enfant en défaut dans un sous-niveau, ou état hérité d'une référence externe). Les 51 groupes ne représentent donc pas 51 défauts distincts : ils sont à revérifier après correction des 28 éléments (les signalements devraient disparaître).

## 4. Classement par priorité

| Priorité | Éléments | Pourquoi |
|---|---|---|
| **P1 - Erreur réelle** | DeleteFace6 (et DeleteFace4/5 qui sont du même lot) | Seule erreur franche de la timeline, sur `Capot_Verrouillage_Batterie` (pièce de verrouillage des batteries hot-swap) |
| **P2 - Pièces certifiées ou critiques** | Chanfrein16, Chanfrein17, Extrusion19 (Bride Epaule) ; Esquisse1, Extrusion10 (Tube transverse Epaules) ; Epaissir1 (résultat partiel) | `Bride Epaule` est la pièce certifiée en FEA (`STUDY_Calculs_FEA_Bride_Epaule_RS04.md`) et utilisée aux épaules et aux hanches (4 occurrences). Epaissir1 est le seul cas où la géométrie peut être incomplète |
| **P3 - Géométrie de référence et assemblage** | Plans, axes, esquisses, réseaux circulaires, contraintes d'assemblage | Références de construction perdues mais cache stable pour l'instant |
| **P4 - Groupes** | 51 groupes | À revérifier après P1 à P3 |

## 5. Protocole de correction proposé

> [!CAUTION]
> Toute correction modifie la CAO. Elle ne doit être faite que sur une copie dédiée, jamais sur le document de référence.

1. **Copie de travail (par vous)** : dans Fusion, enregistrer sous un nouveau nom, par exemple `Torse-123 v50_test`. Je ne peux pas créer cette copie via le MCP.
2. **Point de référence mesuré** : masse racine `18 390,33 g`, encombrement `525,96 x 487,10 x 859,07 mm`, centre de masse `[61,104 ; 8,034 ; 1128,306] mm`, 28 éléments en défaut.
3. **Correction par lot, avec reprise automatique** : après chaque correction, relecture de la santé de l'élément, de la masse racine et de l'encombrement. Écart de masse supérieur à 0,05 g ou apparition d'un nouvel élément en défaut : retour arrière immédiat (rollback du marqueur ou annulation).
4. **Méthode de rattachement** : pour chaque plan, axe ou arête perdu, lecture de la géométrie en cache (position, normale), recherche de la face ou de l'arête existante qui lui correspond à la tolérance près, puis proposition. Pour les cas ambigus, la décision vous revient.
5. **Ordre** : P1 (DeleteFace4/5/6), puis P2, puis P3, puis revérification des groupes (P4).
6. **Validation finale par vous** avant toute sauvegarde ou promotion de la copie en version de référence. Aucune sauvegarde n'est faite sans votre demande explicite.

### 5.1 Premier test conseillé

`DeleteFace6` (seule erreur franche) sur la copie `v50_test` : cas isolé, dans une pièce de faible masse (`Capot_Verrouillage_Batterie`, 115 g pour le lot), avec un risque de dérive très limité et une vérification de masse immédiate.

## 6. Limites de l'audit

- La lecture ne couvre que la **timeline racine** de `Torse-123 v49`. Les timelines internes des composants éventuellement indépendants ne sont pas auditées.
- Le composant propriétaire des plans et axes de construction n'est pas exposé par l'API (marqué "?" à la lecture).
- Les références exactes (quelle face, quelle arête) n'ont pas été extraites : elles seront lues au moment de la correction.
- L'état `RolledBack` de `Extrusion19` n'a pas été expliqué.
