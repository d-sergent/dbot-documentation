Lis le fichier d'audit `annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md`. 
J'ai analysé les incohérences. Voici mes décisions techniques officielles pour mettre à jour la documentation :

- Décision pour '1. Contradiction sur la Masse Totale du D-Bot' : 40.2 kg
- Décision pour '2. Contradiction sur le Nombre Total de Moteurs RobStride du D-Bot' : 26 car il y a 6 DOF par bras
- Décision pour '3. Contradiction sur le Nombre de Moteurs par Jambe' : oui, j'avoue en pas comprendre la question au sujet de la cheville et le F-A-R car il y a bien 6 moteurs par jambes : 3 au niveau de la hanche , 1 au genous et 2 au niveau de la cheville
- Décision pour 'Poignet (Wrist)' : RS-00 est bien le moteur qui gere le pitch au niveau du poignet
- Décision pour 'Incohérence supplémentaire : Attribution du RS-05 (Cou vs Poignet)' : Je pense qu'il y a une erreur car le RS-05 n'est pas mentionné dans les moteurs du poignet. Il n'est mentionné que pour le cou.
- Décision pour 'Anciens modèles encore présents' : RS-02 est bien le moteur qui gere la supination au niveau de l'avant-bras
- Décision pour '1. Alimentation (Tension Batterie)' : Oui, il faut corriger la synthèse pour indiquer une régulation 48V → 19V pour la Jetson car la carte mere est une Jetson Orin Nano
- Décision pour '2. Bus CAN (Nombre de moteurs par bus)' : Oui, il faut autoriser une exception de topologie en étoile pour les bus utilisant des moteurs à port CAN unique car c'est nécessaire pour le cou car les moteurs RS-05 ont tous un port CAN unique.
- Décision pour '2. Bus CAN (Nombre de moteurs par bus)' : Oui, il faut appliquer la règle de terminaison du guide électronique à l'ensemble du robot sauf pour le bus du cou car les câbles sont courts < 30 cm.
- Décision pour '2. Bus CAN (Nombre de moteurs par bus)' : Oui, il faut modifier le guide électronique pour préciser que les moteurs RS-05 utilisent un bus dédié distinct du bus centralisé des membres car c'est nécessaire pour le cou car les moteurs RS-05 ont tous un port CAN unique.
- Décision pour 'Divergence 1 : Version de l'OAK-D Pro' : Fixed Focus
- Décision pour 'Divergence 2 : IMU intégrée' : il est integré a l'OAK-D Pro
- Décision pour 'Divergence 1 : Modèle installé et capacité RAM' : C'est une Jetson Orin Nano Super 8 Go
- Décision pour 'Divergence 2 : Puissance de calcul (TOPS)' : Il dispose de 67 TOPS
- Décision pour 'Divergence 1 : Nombre de microphones et canaux audio' : il y a 4 micros sur le respeaker xvf-3800, mais 6 canaux si on compte la partie cancelation echo et le son produit par les moteurs
- Décision pour 'Divergence 2 : Problème de "Micro Muet"' : sur le port USB A , le bleu
- Décision pour 'Divergence 3 : Interface audio (ALSA vs PulseAudio)' : je ne sais pas repondre a cette question car je ne sais pas ce que c'est
- Décision pour 'Divergence 4 : Activation de l'amplificateur JST' : je ne sais pas repondre a cette question car je ne sais pas ce que c'est

Ta mission :
1. Scanne l'ensemble de la documentation (avec tes outils de recherche) pour localiser tous les fichiers qui contiennent les anciennes valeurs contradictoires.
2. RÈGLE D'OR : Ne touche jamais aux valeurs situées dans des études d'hypothèses, des alternatives ou des brouillons. Uniquement les spécifications de la version officielle.
3. PRÉPARE UN PLAN DOCUMENTÉ : Crée un fichier markdown `annexes/Outils_de_Travail/RAG/PLAN_CORRECTION.md`. 
   Dans ce fichier, tu dois :
   - Rappeler mes décisions techniques (pour assurer un suivi clair).
   - Lister précisément les fichiers que tu vas modifier, avec "Ancienne valeur -> Nouvelle valeur".
   - Lister les équations/calculs (levier, couple, etc.) que tu vas devoir recalculer.
4. ATTENDS MA VALIDATION : Ne modifie aucun autre fichier tant que je n'ai pas lu le plan et répondu "OK".
5. CRITIQUE : Une fois validé, modifie les fichiers de doc et mets à jour les résultats mathématiques.