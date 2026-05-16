# FINAL - Distribution de Puissance (Arbre Hiérarchique)

L'architecture de distribution du D-Bot suit un modèle hiérarchique "en arbre" pour minimiser le poids des câbles et isoler les pannes.

## 1. Topologie de Distribution
Un **busbar central** (torse) alimente des lignes "tronc" protégées par fusibles vers chaque membre. Chaque membre possède ensuite un **splitter local** (WAGO ou mini-busbar).

### Découpage des Zones de Puissance
| Zone | Fusible | AWG Tronc | Connecteur | Répartiteur Local |
| :--- | :---: | :---: | :---: | :--- |
| **Bras G** | 30A | 14 AWG | XT60 | WAGO 221-415 |
| **Bras D** | 30A | 14 AWG | XT60 | WAGO 221-415 |
| **Jambe G** | 50A | 12 AWG | XT60 | Mini-Busbar 6 bornes |
| **Jambe D** | 50A | 12 AWG | XT60 | Mini-Busbar 6 bornes |
| **Cou / Tête**| 5A | 18 AWG | XT30 | WAGO 221-413 |
| **Logique** | 5A | 18 AWG | Bornier | Direct |

## 2. Spécifications des Câbles (Silicone Souple)
Deux calibres rationalisés pour l'ensemble du robot :

*   **14 AWG (Sertissage/Soudure)** : 
    *   *Usage* : Troncs d'alimentation et gros moteurs RS-04 (Pitch Épaule, Genou).
    *   *Capacité* : 45A continu.
*   **18 AWG (Silicone)** :
    *   *Usage* : Tous les autres moteurs (RS-03, 02, 06, 05, 00) et électronique logique.
    *   *Capacité* : 16A continu.

## 3. Méthodes de Connexion
*   **INTERDICTION de souder/étamer** les fils allant dans les WAGO ou sous les vis du busbar (le cuivre doit rester nu et souple).
*   **WAGO 221** : Utilisation exclusive pour les bras et le cou (courant < 30A).
*   **Busbar / Bornier** : Utilisation de **cosses rondes à sertir (Ring Terminals)** pour les connexions vissées.
*   **XT60 / XT30** : Utilisés uniquement pour les connecteurs détachables (troncs et pigtails moteurs RS-04).

## 4. Composants de Distribution
*   **Busbar Central** : Double rail 12 bornes M4, certifié Marine (150A).
*   **E-Stop** : Bouton coup de poing NC inséré sur la ligne (+) entre le fusible principal et le busbar. Coupe la puissance moteurs uniquement.
