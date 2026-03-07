# Sécurité et Procédures de Mise en Marche

> [!DANGER]
> **RISQUE ÉLECTRIQUE ET MÉCANIQUE MAJEUR**
> Les moteurs Robstride sont puissants et peuvent causer des blessures physiques ou brûler l'électronique s'ils sont mal utilisés.

## 1. Configuration de l'Alimentation (Laboratoire)
Pour les premiers tests (Banc d'essai ou Bras seul), utilisez une alimentation de labo réglable (ex: Wanptek).

### Paramètres "Safe Start"
1.  **Tension (Voltage)** : **24.00V** (Vérifier au multimètre à vide avant de brancher quoi que ce soit).
2.  **Courant (Current Limit)** : **1.000A** (1 Ampère).
    *   *Méthode* : Faites un court-circuit des sondes (si l'alim le supporte) ou réglez via le menu OCP.
3.  **Protection** : Activez le mode **OCP** (Over Current Protection). Si le moteur tire trop (blocage), l'alim coupe tout.

## 2. Séquence d'Allumage (Power-Up Sequence)
Respectez **toujours** cet ordre pour éviter de griller la carte de contrôle du moteur ou l'USB2CAN.

1.  **ALLUMER** l'alimentation (Câble moteur DÉBRANCHÉ).
2.  **VÉRIFIER** que la tension affiche bien 24V.
3.  **BRANCHER** le connecteur XT60 du moteur (ou du robot).
4.  **CONNECTER** l'USB (Data) à l'ordinateur/Jetson.
5.  **LOGICIEL** : Lancer le script de contrôle ou le "Enable" moteur.

> **INTERDIT** : Ne jamais modifier la tension (Voltage d'alim) alors que le moteur est branché et activé (Enabled). Les fluctuations peuvent détruire les MOSFETs internes.

## 3. Arrêt d'Urgence (E-Stop)
*   En phase de développement (Phase 2), ayez toujours la main sur l'interrupteur de l'alimentation.
*   Si le robot fait un mouvement violent ou un bruit strident ("singing"), **COUPEZ L'ALIM DIRECTEMENT**. Ne cherchez pas à l'arrêter par logiciel.

## 4. Sécurité Mécanique
*   **Zone d'évolution** : Lors des tests de bras, assurez-vous que le rayon d'action est vide.
*   **Pincement** : Ne pas mettre les doigts dans les articulations (Coude/Poignet) lorsque les moteurs sont sous tension, même à l'arrêt (Holding Torque actif).
