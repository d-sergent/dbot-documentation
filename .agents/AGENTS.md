# D-Bot Project Rules

## Documentation and Knowledge Base Search (RAG)
- Whenever you need to search or verify details about the D-Bot project (such as mechanical specs, FEA results, electronics, motor choices, wiring, CAN bus, or software components), you MUST query the local LightRAG database first.
- To perform this query, run the following command using the shell:
  `/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode naive "<your search terms>"`
- **Search Modes**:
  - `--mode naive` (Vector similarity search): Optimal for retrieving exact dimensional tables, bolt torques, McMaster-Carr part numbers, and FEA Von Mises values.
  - `--mode hybrid` (Knowledge Graph + Vector search): Optimal for cross-subsystem architectural relationships and kinematic dependencies.
- **Primary Torso & Pelvis Reference Documents Indexed**:
  - `01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Torse_Complet_D-Bot_V2.md` (Architecture & CNC machining of Torso).
  - `01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Waist_et_Bassin_D-Bot_V2.md` (Pelvis PA12-CF, RB8016 bearing & RS-06 Waist).
  - `01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md` (Complete FEA synthesis, analytical derivations, boundary conditions & 1-click links).
  - `01_Mecanique_et_Chassis/Torse_et_Bassin/FINAL_BOM_Torse_et_Waist_D-Bot.md` (Consolidated BOM & McMaster-Carr hardware).
  - `01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin.json` (Exact 3D CAD coordinates, bounding boxes & mass properties).
- Always prioritize the retrieved context over general model knowledge for D-Bot specifications, measurements, and layouts.

## Interaction & Workflow Rules
- ALWAYS provide a detailed text explanation of the problem, diagnosis, and proposed code changes FIRST in your response message BEFORE invoking any `git push` or tool execution.
- NEVER run `git push` or execute modifying commands without explaining the rationale to the user beforehand in the text output.

## Ergonomie des Réponses & Copier-Coller en 1 Clic (Interface Antigravity)
- **Isolation Stricte dans des Blocs de Code Dédiés (` ```text ` ou ` ```bash `)** :
  - Dans l'interface Antigravity IDE, la sélection manuelle de texte à la souris dans les paragraphes, listes ou tableaux est sujette à des dysfonctionnements du presse-papiers ou à la capture involontaire d'espaces, de guillemets, de backticks et de descriptions parasites.
  - TOUT élément destiné à être copié et collé par l'utilisateur (référence de composant ou catalogue, commande shell, chemin de fichier absolu, paramètre de recherche, variable) DOIT ÊTRE SYSTÉMATIQUEMENT isolé dans son propre bloc de code dédié.
  - Ce bloc de code doit être rigoureusement épuré : il contient STRICTEMENT et UNIQUEMENT la valeur utile à copier (sur une seule ligne pour une référence ou un code), sans aucun mot descriptif, sans tiret, sans commentaire et sans espace superflu.
  - Cette disposition permet à l'utilisateur de cliquer directement sur l'icône native de copie (bouton "Copy" en haut à droite du bloc de code) pour charger instantanément le presse-papiers en 1 clic sans manipulation manuelle.
- **Règle Inviolable pour les Références McMaster-Carr (Insertion Fusion 360)** :
  - Dès qu'une référence McMaster-Carr (ex. `91292A118`, `93625A150`, `93475A230`) est transmise à l'utilisateur dans une réponse pour insertion dans Fusion 360 via `Insert > Insert McMaster-Carr Component`, elle DOIT OBLIGATOIREMENT être fournie dans un bloc ` ```text ` individuel contenant EXCLUSIVEMENT les 9 caractères alphanumériques.
  - Il est STRICTEMENT INTERDIT de concaténer la référence avec du texte descriptif dans le même bloc (ex: interdiction formelle d'écrire `91292A118 - Vis M4x16 inox`), car le moteur de recherche interne de McMaster dans Fusion 360 tente d'interpréter la chaîne complète et échoue systématiquement à trouver la pièce.

## Jetson Package Management & PyTorch GPU Protection
- **JetPack Python Package Protection**: When installing any Python package via `pip` or suggesting installation commands for the Jetson Orin Nano, ALWAYS append the `--no-deps` flag (e.g. `pip install <package> --no-deps`).
- **NEVER** run `pip install torch` or `pip install torchvision` without `--no-deps` or without using the official NVIDIA JetPack 6.1 wheel, to prevent overwriting the native CUDA 12.2 GPU bindings.

## Sécurité du Code Source & Audit Systématique (DevSecOps)
- **Validation Systématique de Sécurité (SAST & Secrets)** :
  - Tout code Python produit, modifié ou intégré dans le projet D-Bot (`Code/`) doit impérativement respecter les règles de sécurité défensive :
    1. *Zéro Injection Shell* : Interdiction formelle de `subprocess.run(..., shell=True)` ou `subprocess.Popen(..., shell=True)` avec des chaînes interpolées (f-strings). Utiliser systématiquement des listes d'arguments découpées (`shell=False`) ou des flux directs d'entrée standard `input=...`.
    2. *Zéro Secret Hardcodé* : Aucune clé d'API (Groq, Gemini, OpenAI), token ou mot de passe ne doit être écrit en dur dans le code. Utiliser systématiquement les variables d'environnement via `.env` (déjà exclu dans `.gitignore`).
    3. *Hachages Non Cryptographiques* : Toujours spécifier `usedforsecurity=False` lors de l'appel à `hashlib.md5()` pour les identifiants documentaires RAG.
- **Audit Automatique & Hook Git Pre-Commit** :
  - Le hook Git `.git/hooks/pre-commit` exécute automatiquement `audit_dbot_security.py --skip-sca` avant chaque commit pour bloquer toute régression de sécurité.
  - Avant de valider un lot de code Python ou lors de la clôture d'une session de développement, l'agent doit exécuter l'outil d'audit souverain :
    `/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/security/audit_dbot_security.py" --skip-sca`
  - Le code ne peut être validé que si l'audit SAST et le scan des secrets retournent un statut `PASSED` (code de sortie 0).
- **Gestion des Dépendances & Règle d'Isolation** :
  - Sur le Mac : ne jamais installer d'outils CLI ou d'applications tierces volumineuses directement dans le Python système Homebrew. Utiliser systématiquement `/Users/davidsergent/.local/bin/uvx <outil>`.
  - Sur la Jetson Orin Nano : appliquer impérativement le drapeau `--no-deps` pour toute commande `pip install` afin de préserver le PyTorch compilé GPU CUDA 12.2.

## Session Lifecycle & Context Persistence
- **Session Startup**: At the beginning of any work session, ALWAYS consult the latest entry in `05_Gestion_Projet/JOURNAL_DE_BORD.md` and review the current active level in `05_Gestion_Projet/ROADMAP_STRATEGIQUE_V1.md` to immediately get up to speed with current project status.
- **Periodic Journal Updates**: Do NOT update `JOURNAL_DE_BORD.md` after every minor interaction or routine fix. Instead, accumulate progress and only update `05_Gestion_Projet/JOURNAL_DE_BORD.md` periodically (at major milestones or when completing a full work session) with a clean, consolidated summary.
- **Session Closure & RAG Sync**: When concluding a full work session or when the user indicates the session is ending, ask the user if they wish to record the final session summary in `05_Gestion_Projet/JOURNAL_DE_BORD.md` and update checkmarks in `ROADMAP_STRATEGIQUE_V1.md` / `todo_court_terme.md`.
- **Interdiction Formelle d'Exécuter `index_docs.py` (Lancement Manuel Utilisateur)** : L'agent ne doit **JAMAIS** lancer de lui-même la commande de réindexation RAG (`index_docs.py`). L'utilisateur préfère systématiquement exécuter cette commande manuellement dans son terminal interactif pour suivre le déroulement et les flux en direct. L'agent peut uniquement rappeler la commande ou demander si l'utilisateur souhaite le faire, sans jamais l'exécuter.

## Text Formatting & Unit Representation
- **ABSOLUTE ZERO TOLERANCE FOR LATEX AND DOLLAR SIGNS ($ or $$)**: NEVER use LaTeX math syntax, dollar signs, or LaTeX symbols (such as `$0.5\text{ m}$`, `$\varnothing 80\text{ mm}$`, `$\pm 0,02^\circ$`, `$$...$$`, `\text{...}`, `\varnothing`, `\pm`, `\approx`, `\circ`, `\sqrt{...}`, `\mathbf{...}`) in text responses, chat messages, markdown documentation, artifacts (plans, walkthroughs), or code comments. ALWAYS write angles, ranges, diameters, tolerances, formulas, calculations, variables, and units in clean plain text (e.g. `0.5 m`, `500 mm`, `Ø 80 mm`, `+/- 0.02 deg`, `M_stat ~ 110 Nm`, `36.8 MPa`, `Delta_theta`, `Sigma_max`, `R_vis = sqrt(21^2 + 21^2) = 29.7 mm`). Every formula must be written in standard readable ASCII / plain text.

## Technical Diagrams & Schematics Generation
- **Systematic High-Quality SVG Vector Blueprints**: Whenever a technical, mechanical, electrical, or architectural diagram/schematic is needed in documentation or markdown files, NEVER use ASCII art or basic graph flowcharts (like Mermaid) which lack spatial proportions and native preview support.
- **SVG Generation Standard**: ALWAYS generate a dedicated, standalone SVG vector file in the local `./media/` directory (e.g. `./media/<diagram_name>.svg`) and embed it into markdown using `![Description](./media/<diagram_name>.svg)`.
- **Design Specifications for SVG Schematics**:
  - **Theme**: Dark technical blueprint aesthetic (`#0f172a` background canvas, `#1e293b` panel cards, subtle `#2a324b` grid background).
  - **Layout**: Multi-panel view layout (e.g., Vue de Face / Vue de Dessus / Vue de Profil) with clear titles.
  - **Visual Elements**: Color-coded material gradients (Aluminium, Tube Carbone, Moteurs QDD, Batteries), callout text, dimension lines, and a technical legend box.
- **Mandatory Markdown Image Embedding**: NEVER create, generate, or save any image file (PNG, JPG, SVG, WebP) in the workspace without IMMEDIATELY embedding and referencing it in a corresponding active Markdown document (e.g. `![Description](./media/<image_name>.png)`). No orphan media files are allowed in the repository.

## Documentation Structure & Navigation
- **Systematic Table of Contents (Sommaire Cliquable Obligatoire)** : In every active technical Markdown document of Level 1 (`FINAL_`, `GUIDE_COMPLET_`, `DOSSIER_TECHNIQUE_`) and Level 2 (`STUDY_`, `AUDIT_`), you MUST include a structured `## 📑 Sommaire` / `## 📑 Sommaire Général` at the beginning of the file (immediately after the header / intro callout) with functional markdown anchor links (`[Titre](#slug-ancre)`) pointing directly to all major sections (`##`) and sub-sections (`###`).
- **Fonctionnalité & Validité Stricte des Liens de Sommaire (Zéro Lien Mort)** :
  - TOUS les liens d'ancre d'un sommaire doivent être rigoureusement fonctionnels et vérifiés : le slug d'ancre (`#nom-de-section`) doit correspondre exactement aux règles de slugification Markdown (conversion en minuscules, suppression des caractères spéciaux/ponctuations, remplacement des espaces par des tirets `-`).
  - Lors de tout ajout, renommage, déplacement ou suppression d'une section (`##` ou `###`), vous DEVEZ SYSTÉMATIQUEMENT inspecter et mettre à jour le sommaire du document pour réaligner immédiatement le texte et le slug de l'ancre. Aucun lien brisé ou ancre orpheline n'est toléré dans la documentation active.
  - Vérifier également que les liens de référence inter-fichiers (`[Doc](file:///...)` ou relatifs) pointent toujours vers des chemins de fichiers réels et existants.

## Actionneurs RobStride — Règle Matérielle Inviolable (Arbres Pleins / Zéro Arbre Creux)
- **Architecture Pleine & Fermée** : TOUS les moteurs de la gamme RobStride (RS-00, RS-02, RS-03, RS-04, RS-05, RS-06) possèdent un arbre de sortie plein, un centre borgne/obstrué et un carter arrière totalement fermé.
- **Interdiction Formelle d'Arbre Creux** : AUCUN moteur RobStride n'a d'arbre creux traversant (ZÉRO hollow shaft / ZÉRO through-bore).
- **Routage Obligatoire Déporté** : Tout passage de faisceau électrique (lignes de puissance 48V, paires CAN-FD, câblage capteurs) ou de transmission par câble/tendon (mains D-Hand) doit IMPÉRATIVEMENT contourner le moteur via un corridor latéral ou postérieur déporté (lumière oblongue avec passe-fil et boucle de service). Il est STRICTEMENT INTERDIT de concevoir ou de suggérer un passage de câbles ou de tendons à travers l'axe d'un moteur RobStride.

## Rigueur d'Ingénierie Système & Prévention des Biais de Cadrage
- **Interdiction Formelle d'Affirmation de Mémoire (Zéro Raccourci)** :
  - Dès qu'une réponse cite, compare, dimensionne ou prend en exemple un sous-ensemble, un composant, une référence de pièce ou un inventaire, il est STRICTEMENT INTERDIT de se baser sur une restitution intuitive ou un souvenir de conversation.
  - Tout état des lieux ou exemple illustratif DOIT être formellement recoupé avec la source de vérité consolidée active (dossiers `00_Architecture_Centrale/` ou `05_Gestion_Projet/`) AVANT de formuler la réponse.
- **Principe de Complétude & Non-Fragmentation (Vue Système Holistique)** :
  - Lorsqu'une question porte sur un composant ou une articulation isolée, l'analyse ne doit JAMAIS fragmenter ou simplifier arbitrairement le sous-ensemble auquel il se rattache.
  - Tout sous-ensemble mentionné (ex. chaîne cinématique, organe terminal, alimentation, bus de données) doit être décrit dans son **intégralité fonctionnelle exacte**, sans omettre les éléments complémentaires qui le constituent.
- **Hiérarchie Stricte des Sources Documentaires** :
  - **Niveau 1 (Vérité Terrain Active)** : Les documents préfixés `FINAL_`, `GUIDE_COMPLET_`, `DOSSIER_TECHNIQUE_`, ainsi que `05_Gestion_Projet/FINAL_Liste_Achats_BOM.md`, `05_Gestion_Projet/JOURNAL_DE_BORD.md` et `05_Gestion_Projet/ROADMAP_STRATEGIQUE_V1.md` font foi absolue.
  - **Niveau 2 (Études & R&D en cours)** : Les documents préfixés `STUDY_` ou `AUDIT_` fournissent le contexte technique et les calculs justificatifs.
  - **Niveau 3 (Interdit d'affirmation)** : Les documents historiques, brouillons ou archives (ex. dossiers `Archives`, `00_Archives_Recherche`) ne doivent JAMAIS être utilisés pour énoncer l'état actuel du robot, sauf si l'utilisateur demande explicitement l'historique d'une décision.
- **Auto-Vérification Pré-Génération (Sanity Check)** :
  - Avant de valider le message final, vérifier la cohérence interne entre tous les composants cités dans le message et les inventaires validés de la session. En cas de doute ou d'information manquante, expliciter la nuance plutôt que d'extrapoler.
- **Détection et Signalement Systématique des Désynchronisations CAO / Documentation** :
  - Dès qu'une divergence, un déphasage ou une contradiction apparaît entre la documentation technique écrite (dossiers, feuilles de route) et l'état réel de la CAO (audit métrologique JSON, captures d'écran Fusion 360, cotes effectives), vous avez l'OBLIGATION STRICTE de le signaler immédiatement et explicitement à l'utilisateur au lieu de poursuivre aveuglément sur le texte théorique.
  - Exposer clairement l'écart (État Documenté vs État CAO Réel) afin de trancher ensemble l'arbitrage et de réaligner immédiatement la documentation et les schémas vectoriels SVG sur la réalité validée en conception 3D.

## Posture d'Ingénierie Système & Décisions d'Expertise en Robotique Humanoïde
- **Exigence d'Excellence & Alignement Strict sur l'État de l'Art Mondial** :
  - Dans toutes ses analyses, diagnostics et propositions de conception (mécanique, cinématique, dynamique, câblage, thermique, asservissement), l'agent DOIT systématiquement adopter la posture d'un **architecte système senior en robotique humanoïde avancée**, calibré sur les standards des leaders mondiaux (Boston Dynamics Atlas, Tesla Optimus Gen 2, Unitree H1/G1, Figure 02).
- **Formulation Systématique de la Meilleure Hypothèse dès le Premier Jet (Zéro Rétropédalage par Simplisme)** :
  - L'agent ne doit JAMAIS proposer de compromis au rabais, de géométries hâtives ou d'impasses techniques sous-estimant la physique d'un humanoïde dynamique (ex: passages de câbles trop étroits provoquant un cisaillement, rayons de courbure trop faibles détruisant le cuivre par fatigue cyclique, connecteurs indémontables obligeant à dessouder en atelier, oubli des masses, inerties ou contraintes thermiques).
  - L'agent DOIT formuler d'emblée la **meilleure proposition argumentée**, étayée par les calculs physiques réels (RDM, cinématique, dynamique, thermique, électrotechnique) et les retours d'expérience industriels.
  - Une fois une solution techniquement démontrée et validée, l'agent **assume et maintient fermement sa décision** : il est formellement interdit de revenir sur une décision solide, de changer d'avis sans justification physique nouvelle ou de rétropédaler vers une solution bancale au moindre questionnement. L'agent doit au contraire expliciter la démonstration avec rigueur, chiffres et pédagogie pour dissiper les doutes.
- **Anticipation Holistique Systématique des Contraintes Réelles** :
  - **Cinématique & Torsion Dynamique du Harnais Électrique** :
    - Toujours analyser le comportement dynamique du faisceau sur toute la plage angulaire réelle (ex: lacet de taille +/- 90° à +/- 95°).
    - Respect absolu de la règle de torsion linéique admissible (`<= 0,6° / mm` à `1,0° / mm` max) et prédisposition d'une boucle de service libre (`L = 150 à 200 mm`).
    - Respect des rayons de courbure minimaux : `R >= 6 * Ø_câble` en statique, `R >= 10 * Ø_câble` en flexion/torsion cyclique continue.
    - Proscription absolue du cisaillement relatif ("effet guillotine") : deux cloisons en mouvement relatif ne doivent JAMAIS enserrer un faisceau dans deux orifices fermés superposés. Tout passage tournant doit s'ouvrir en encoche dégagée ou passer par un corridor axial ouvert avec boucle de service dédiée.
  - **Démontabilité & Maintenance Atelier (Zéro Dessoudage)** :
    - Tout passage de faisceau (lumière, passe-fil, tunnel de cloison) doit impérativement être dimensionné pour laisser passer les connecteurs complets pré-câblés (XT30, XT60, XT90, JST, Micro-Fit) sans jamais obliger à couper ou dessouder les lignes de puissance ou de communication lors de la maintenance en atelier.
    - Les passe-fils souples en élastomère (TPU) doivent être systématiquement conçus avec une fente latérale pour être amovibles sans déconnecter le faisceau.
  - **Cohérence Métrologique & Intégrité Matière (Usinage & Impression 3D)** :
    - Avant de poser une cote ou une lumière, recouper systématiquement les encombrements réels (bounding boxes, axes de rotation, bagues de roulements) dans le modèle CAO validé (ex: `AUDIT_METROLOGIQUE_Torse_et_Bassin.json`).
    - Toujours vérifier que les ponts de matière résiduels en alliage d'aluminium (7075-T6) ou polymère composite (PA12-CF) respectent les épaisseurs minimales d'usinabilité et de tenue mécanique (typiquement `> 2,5 à 3,0 mm` en 7075-T6 pour éviter toute déformation lors du fraisage CNC).

## Modélisation CAO Fusion 360 & Quincaillerie Normalisée (McMaster-Carr)
- **Références McMaster-Carr Systématiques (3D STEP)** :
  - Dès qu'un nouveau composant de visserie, fixation ou quincaillerie (vis CHC/FHC/BHC, écrous Nylstop, rondelles plates DIN 125A, rondelles Nord-Lock, entretoises nylon, inserts filetés, goupilles) est introduit, dimensionné ou modifié dans la documentation technique active, vous DEVEZ SYSTÉMATIQUEMENT :
    1. Renseigner sa **référence catalogue McMaster-Carr exacte** (à 9 caractères alphanumériques, ex. `92290A038`, `90631A105`) pour permettre le téléchargement direct du modèle 3D STEP dans Autodesk Fusion 360 via le menu `Insert > Insert McMaster-Carr Component`.
    2. Documenter la **procédure pas-à-pas d'assemblage dans Fusion 360** : type de liaison `Joint` (raccourci `J`, généralement `Rigid`), sélection des arêtes et faces d'appui planes, orientation du composant (ex. dôme polyamide vers l'extérieur pour un écrou Nylstop) et méthode de répétition (Pattern ou copie liée).
    3. Mettre à jour le **tableau synthétique des couples dynamométriques** de serrage recommandés (en N.m) et l'outillage d'atelier associé (taille de clé Allen, clé plate ou douille).
    4. Fournir SYSTÉMATIQUEMENT chaque référence catalogue dans le dialogue sous forme de **bloc de code isolé monoligne** (` ```text\n91292A118\n``` `) pour permettre à l'utilisateur de la copier en un seul clic sans aucun texte parasite.
- **Protocole de Vérification Stricte des Références Fournisseur & McMaster-Carr (Zéro Hallucination de Référence)** :
  - **Interdiction Formelle d'Extrapolation ou d'Invention Numérique** :
    - Il est formellement interdit de deviner, d'interpoler ou de restituer "de mémoire" un code catalogue alphanumérique (les séries McMaster-Carr ne sont pas linéaires et varient selon la matière, le pas métrique, le filetage total ou partiel et la longueur).
  - **Étape 1 — Recoupement Prioritaire avec l'Historique CAO et la BOM Active** :
    - Avant de chercher une référence, TOUJOURS inspecter si le composant exact existe déjà dans l'assemblage CAO du robot (ex. fichiers `AUDIT_METROLOGIQUE_Torse_et_Bassin.json`, noms d'occurrences CAO contenant un tag de pièce comme `[93625A150]`) ou dans [FINAL_Liste_Achats_BOM.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/FINAL_Liste_Achats_BOM.md).
    - Si une référence est déjà certifiée et implantée dans la CAO pour une taille donnée (ex: écrou Nylstop M4 = `93625A150`), elle DOIT être reprise à l'identique pour assurer la cohérence des approvisionnements.
  - **Étape 2 — Validation Multi-Critères Obligatoire sur le Catalogue Réel** :
    - Pour tout nouveau composant de fixation, vous DEVEZ formellement vérifier les 6 critères physiques sur le catalogue McMaster-Carr (via recherche web ou documentation technique officielle) avant de délivrer le code :
      1. *Système d'unités* : Métrique obligatoire (System of Measurement = Metric). Zéro visserie impériale en pouces.
      2. *Diamètre nominal & Pas* : Pas métrique standard (Coarse) ou fin (Fine) clairement identifié (ex. M4 × 0,7 mm).
      3. *Longueur exacte* : Longueur sous tête pour les vis à tête cylindrique CHC / bombée BHC, ou longueur totale pour les vis à tête fraisée FHC.
      4. *Nuance de matériau & Traitement* : Inox 18-8 standard (A2 / 304), Inox 316 marine (A4), Acier allié haute résistance classe 12.9 (Black-Oxide ou zingué).
      5. *Type de filetage* : Filetage total (Fully Threaded) ou partiel avec longueur non filetée.
      6. *Norme géométrique* : DIN 912 / ISO 4762 (CHC), DIN 7991 / ISO 10642 (FHC), ISO 7380 (BHC), DIN 985 (Nylstop), DIN 125A (Rondelle).
  - **Étape 3 — Contrôle de Compatibilité CAO 3D STEP** :
    - Vérifier que la référence sélectionnée dispose bien d'un modèle CAO 3D téléchargeable (icône CAD / 3D STEP disponible dans le catalogue McMaster).
  - **Étape 4 — Isolement Monoligne pour Copier-Coller en 1 Clic** :
    - Comme stipulé dans la règle d'ergonomie, chaque code final validé doit être délivré dans son bloc ` ```text ` isolé, sans nom de pièce ni texte dans le bloc, pour garantir un copier-coller immédiat dans le moteur de recherche de Fusion 360.

## Cartographie des Usinages, Chanfreins, Fraisures & Ébavurages d'Atelier
- **Obligation de Spécification des Chanfreins & Cassages d'Arêtes** :
  - Aucun perçage, chambrage, fraisure conique ou chant débité ne doit être laissé sans spécification géométrique d'ébavurage dans les dossiers techniques d'usinage (C500 ou atelier).
  - Pour chaque opération de perçage ou de découpe, vous DEVEZ SYSTÉMATIQUEMENT mettre à jour la section et le **tableau récapitulatif des chanfreins et fraisures** du dossier technique concerné :
    - Chanfrein d'entrée et de sortie sur perçages lisses débouchants (typiquement `0,2 mm × 45°` à `0,3 mm × 45°`) pour éliminer le morfil de perçage et garantir une assise métal-métal parfaitement plane sous tête de vis, sous entretoise ou sous rondelle.
    - Fraisures coniques à 90° (vis FHC) : spécifier le diamètre de fraisure supérieur et la profondeur exacte pour un **noyage à fleur rigoureux à 0,0 mm** (zéro saillie de tête).
    - Chants débités et bords sciés : cassage d'arête systématique (typiquement `0,5 mm × 45°`).
    - Pliures et congés d'appui : chanfreinage adapté (`0,5 mm × 45°`) pour éviter le contact franc sur le congé intérieur naturel des profilés marchands.

## Inspection Visuelle Multimodale de la CAO & Bibliothèque Hors-Git
- **Localisation des Snapshots CAO Haute Définition** :
  - Les rendus et captures d'écran de l'assemblage complet et de chaque pièce isolée sont générés dans le dossier souverain externe (hors-Git) :
    `/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/`
    - `Vues_Ensemble/` : 7 vues globales de l'assemblage CAO (Face, Arrière, Dessus, Dessous, Profil Droit, Profil Gauche, Isométrique).
    - `Pieces_Isolees/<nom_piece>/` : Tétraptyque d'ingénierie systématique à 4 vues (`_iso.png`, `_face.png`, `_dessus.png`, `_dessous.png`) + pack FEA complet pour les pièces structurelles.
    - `Assemblages/<nom_assemblage>/` : Modèles `.FCStd` multi-composants résolus par CalculiX, cartographies spectrales `_VonMises.png` et lanceurs 1-clic `.command`.
- **Interdiction Stricte de Pollution du Répertoire Git (`media/`)** :
  - Il est FORMELLEMENT INTERDIT de copier, dupliquer ou commiter ces captures de pièces brutes ou modèles `.FCStd` volumineux dans le sous-dossier `media/` de la documentation Git (`Documentation/.../media`).
- **Protocole d'Inspection Visuelle Réelle à la Volée (Dépassement des Bounding Boxes)** :
  - Pour toute analyse géométrique, étude d'encombrement, vérification d'interférence ou dimensionnement de renfort/nervure, l'agent ne doit JAMAIS se contenter de la boîte englobante rectangulaire aveugle (`bounding_box_mm` du JSON).
  - L'agent DOIT inspecter la morphologie réelle de la pièce en ouvrant directement l'image avec `read_file` (ou en la copiant dans `<conversation_artifact_dir>/scratch/`) pour analyser ses congés, lamages, nervures et étagements 3D réels.
- **Protocole d'Auto-Vérification Visuelle Obligatoire après Génération d'Images** :
  - Dès qu'une image (snapshot CAO, cartographie FEA `_VonMises.png`, ou schéma vectoriel SVG) est générée par script, l'agent a l'**OBLIGATION STRICTE** de l'ouvrir et de l'inspecter visuellement une par une avec l'outil `read_file` avant de formuler sa réponse.
  - L'agent doit contrôler de manière autonome :
    1. *Intégrité et Cadrage* : L'image n'est ni vide, ni blanche, ni minuscule ; la pièce ou le maillage occupe 80 à 90% de la hauteur utile (via `view.fitAll()` + ajustement `OrthographicCamera height`).
    2. *Spectre Chromatique FEA Réel* : Le maillage 3D affiche bien les couleurs spectrales de contraintes Von Mises (bleu -> cyan -> vert -> jaune -> rouge) issues de `CCX_Results`, et non un simple ombrage CAO gris.
    3. *Échelle et Bandeau d'Ingénierie* : La barre d'échelle verticale (`Von Mises (MPa)`) est graduée avec les bornes exactes `[min, max]` du calcul, et toutes les lignes de métriques s'inscrivent dans la carte supérieure gauche avec une marge suffisante sans débordement.
  - Si un défaut visuel est détecté à l'ouverture, l'agent DOIT corriger le script et régénérer l'image de manière autonome avant de présenter le livrable à l'utilisateur.

## Standardisation du Pack Technique Autonome : Pièces Isolées & Assemblages (Exports_CAO_DBot)
- **1. Règle d'Organisation par Pièce Isolée (`Pieces_Isolees/<nom_piece>/`)** :
  - Tout composant isolé du robot D-Bot dispose d'un **pack technique complet et autonome** regroupé dans :
    `/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Pieces_Isolees/<nom_piece>/`
  - Contenu standardisé :
    1. *Tétraptyque Visuel Orthogonal & 3D* : `<nom_piece>_iso.png`, `<nom_piece>_face.png`, `<nom_piece>_dessus.png`, `<nom_piece>_dessous.png`.
    2. *Modèle de Simulation FEM FreeCAD* (pour les pièces structurelles calculées) : `<nom_piece>_FEA_Results.FCStd` ou `<nom_piece>_FEA_Tangage.FCStd` contenant l'arbre complet CalculiX (`CCX_Results`), le maillage Gmsh C3D10 et les conditions aux limites.
    3. *Cartographie Chromatique FEA* : `<nom_piece>_VonMises.png` (rendu HD du maillage 3D coloré par les scalaires Von Mises CalculiX avec colorbar MPa et carte de synthèse).
    4. *Lanceur 1-Clic macOS* : `Ouvrir_Simulation_FreeCAD.command` ou `Ouvrir_Simulation_Tangage.command`.
  - **Répertoires de pièces structurelles avec FEA certifiée** :
    - `Pieces_Isolees/Corniere_haute/` : `Corniere_haute_FEA_Results.FCStd` (27 478 nœuds, crête 84,7 MPa, Sf P95 = 11,2) + `Corniere_haute_VonMises.png`.
    - `Pieces_Isolees/Corniere_basse/` : `Corniere_basse_FEA_Results.FCStd` (47 126 nœuds, crête 67,9 MPa, Sf P95 = 13,1) + `Corniere_basse_VonMises.png`.
    - `Pieces_Isolees/colonne_vertébrale/` : `colonne_basse_FEA_Tangage.FCStd` (53 958 nœuds, crête 106,8 MPa, Sf P95 = 4,7) + `colonne_basse_Tangage_VonMises.png`.
- **2. Règle d'Organisation par Assemblage Structurel (`Assemblages/<nom_assemblage>/`)** :
  - Les simulations multi-composants sont centralisées dans :
    `/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Assemblages/`
  - **Répertoires d'assemblages actifs avec FEA CalculiX certifiée** :
    1. *Colonne Vertébrale Complète Sandwich 15 mm* (`Assemblages/colonne_vertébrale_complete/`) :
       - `colonne_complete_FEA_Tangage.FCStd` (Plaque basse + Plaque haute + 2 Éclisses 5 mm, 125 490 nœuds C3D10, crête 81,1 MPa, flèche 0,384 mm).
       - `colonne_complete_Tangage_VonMises.png` & `Ouvrir_Simulation_Tangage.command`.
    2. *Ossature Primaire Globale du Torse — Spaceframe 3D* (`Assemblages/torse_complet_global/`) :
       - `Torse_Global_Assembly_FEA_Results.FCStd` : Assemblage structurel complet intégrant les **15 solides CAO réels** (Waist Plate, 2 Équerres Waist, Colonne Sandwich 15 mm, Équerre de Cou, Plaque de Cou, 2 Tubes d'épaules, 2 Brides d'épaules, 2 Cornières Hautes, Ceinture Ventrale 7075-T6 et 2 Cornières Basses — *sans le support batterie PA12-CF non-porteur*), maillé à **156 846 nœuds** (82 003 éléments C3D10) et résolu par CalculiX sous flexion sagittale d'arrêt d'urgence (`F_x = 328 N`, `M_pitch = 140 N.m` : `CCX_Results`, crête `62,11 MPa` soit `-23,4 %` par rapport à la colonne seule grâce au partage d'effort des cornières, P95 zone basse `15,25 MPa`, flèche totale au cou `0,622 mm`, `Sf = 8,13` crête / `33,1` P95).
       - `Torse_Global_Assembly_VonMises.png` & `Ouvrir_Simulation_Torse_Global.command`.
- **Zéro Fichier Volant à la Racine (`Exports_CAO_DBot/`)** :
  - Aucun fichier temporaire de simulation (`.FCStd`, `.FCBak`, scripts ou logs) ne doit être abandonné à la racine de `Exports_CAO_DBot/`. Tout livrable doit être classé dans `Pieces_Isolees/<nom_piece>/` ou `Assemblages/<nom_assemblage>/`.

## Export CAO Souverain & Hygiène de la Bibliothèque STEP (Zéro Fichier Orphelin)
- **Principe d'Intégrité Stricte de la Bibliothèque B-Rep (`Bibliotheque_Composants_STEP`)** :
  - Le dossier souverain `/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP/` centralise les solides B-Rep uniques du robot pour reconstruction dans FreeCAD.
  - La bibliothèque doit être en TOUT TEMPS rigoureusement synchronisée avec le manifeste actif `dbot_cad_manifest.json` : chaque fichier `.step` présent sur disque doit obligatoirement correspondre à un composant actif de la maquette numérique.
- **Purge Automatique des Pièces Renommées ou Supprimées** :
  - Lors de chaque export via le script Fusion 360 `ExportSovereignCAD.py`, le script compare systématiquement les fichiers sur disque avec les composants actifs de l'assemblage.
  - Tout fichier STEP orphelin (pièce renommée, ancienne dénomination de visserie avant standardisation, ou pièce supprimée du modèle) est **automatiquement purgé du disque** et consigné dans `manifest["metadata"]["purged_orphans"]`.
- **Maintenance et Audit CLI Hors-Fusion (`clean_sovereign_library.py`)** :
  - Pour auditer ou purger manuellement les fichiers orphelins sans ouvrir Fusion 360, utiliser le script :
    `/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/scripts/cad_tools/clean_sovereign_library.py" --purge`

## Calculs RDM & Analyses par Éléments Finis (FEA) — Auditabilité, Cartographies & Répertoire des Résultats
- **Consultation Immédiate des Spécifications et Résultats FEA** :
  - Toute question ou vérification portant sur les calculs RDM, les hypothèses de charge ou les résultats d'éléments finis du Torse et du Bassin doit systématiquement s'appuyer sur le dossier de référence central :
    `01_Mecanique_et_Chassis/Torse_et_Bassin/DOSSIER_TECHNIQUE_Calculs_FEA_Torse_et_Bassin.md`
  - Les scripts Python souverains de simulation et de post-traitement associés sont stockés dans :
    - `Code/scripts/freecad/simulate_torse_global_assembly.py` (Simulation FEA globale des 15 corps de l'ossature primaire du torse).
    - `Code/scripts/freecad/simulate_colonne_complete_assembly.py` (Simulation FEA de l'assemblage sandwich 15 mm de la colonne).
    - `Code/scripts/freecad/simulate_colonne_vertebrale.py` (Simulation FEA des segments bas et haut isolés).
    - `Code/scripts/freecad/simulate_corniere_haute.py` & `Code/scripts/freecad/simulate_corniere_basse.py` (Simulations FEA des cornières en lacet).
    - `Code/scripts/cad_tools/export_all_fea_snapshots.py` (Générateur automatique des cartographies HD `_VonMises.png` via FreeCAD GUI OpenGL).
- **Règle Inviolable d'Exécution FEA Souveraine (Option B Exclusivement — Source Unique de Vérité)** :
  - Il est **FORMELLEMENT INTERDIT** de produire de fausses images FEA (ex: simple rendu CAO gris ombré avec texte superposé) ou de restituer des valeurs estimées sans résolution effective du solveur.
  - Toute cartographie `_VonMises.png` DOIT provenir d'une véritable résolution CalculiX (`ccx`) + Gmsh dont l'objet `CCX_Results` (`Fem::FemResultObjectPython`) est sauvegardé dans le fichier `.FCStd` correspondant, et dont le maillage 3D est coloré nœud par nœud via `mesh_vo.setNodeColorByScalars(res_obj.NodeNumbers, mapped_scalars)`.
  - **Étalonnage Chromatique `[-1.0, +1.0]` & Direction de Force (`con_force.Direction`) dans FreeCAD FEM** :
    1. *Vecteur directionnel de force* : Dans FreeCAD FEM, `con_force.DirectionVector` est en lecture seule et recalculé depuis `con_force.Direction`. Ne jamais écrire uniquement `con_force.DirectionVector = FreeCAD.Vector(1,0,0)` sans assigner une arête géométrique rectiligne `con_force.Direction = (part_obj, ["Edge..."])` (faute de quoi FreeCAD applique l'effort selon la normale à la face sélectionnée).
    2. *Spectre complet Bleu-Cyan-Vert-Jaune-Rouge* : La méthode C++ `ViewProviderFemMesh::setNodeColorByScalars` de FreeCAD utilise une palette signée `[-max, +max]` où `0.0` correspond au **Vert** (`(0, 255, 0)`), `-max` au **Bleu** (`(0, 0, 255)`) et `+max` au **Rouge** (`(255, 0, 0)`). Pour les grandeurs positives comme `vonMises`, il est obligatoire de projeter `[vm_min, vm_scale_max]` sur `[-1.0, +1.0]` avant d'appeler `setNodeColorByScalars` afin que `0 MPa` soit rendu en **Bleu profond** et que le maillage concorde à 100% avec l'échelle latérale.
  - **Modélisation des Assemblages Fermés (Prévention des Boucles MPC `*TIE`)** : Sur les structures fermées hyperstatiques (comme le caisson spatial du torse), ne jamais chaîner des contraintes `ConstraintTie` (`*TIE`) en boucle fermée, ce qui fait boucler indéfiniment la routine `cascade.c` de CalculiX. Toujours unifier les sous-ensembles en contact franc et modéliser les cales de serrage boulonné aux interfaces pour obtenir un solide B-Rep continu (`Solids = 1`) avant maillage Gmsh.
  - **Exécution Non-Bloquante de FreeCAD GUI sur macOS** : Pour exécuter un script de rendu OpenGL avec `/Applications/FreeCAD.app/Contents/Resources/bin/FreeCAD <script.py>`, toujours préfixer par `PYTHONIOENCODING=utf-8`, appeler la fonction d'export au niveau top-level du fichier (ne jamais la bloquer derrière `if __name__ == "__main__":` qui n'est pas déclenché par l'interpréteur macro de FreeCAD) et fermer explicitement la fenêtre en fin de script via `FreeCADGui.getMainWindow().close()`.
- **Interdiction Formelle d'Efforts Arbitraires (Zéro Force « Magique »)** :
  - Aucun effort ponctuel, pression, couple ou condition de Neumann ne doit être injecté arbitrairement ou « de mémoire » dans un script ou deck de simulation FEA (FreeCAD / CalculiX / ccx).
  - Tout chargement mécanique DOIT être formellement et explicitement dérivé de la physique réelle du robot D-Bot :
    1. *Masse et Répartition Inertielles* : Masse effective du sous-ensemble et position métrologique exacte de son centre de gravité (CoG) extraite de la maquette numérique CAO.
    2. *Accélérations et Décélérations Réelles* : Prise en compte des cas de freinage d'urgence (E-Stop avec décélération typique `gamma = 1,5 g = 14,7 m/s^2` à pleine vitesse de marche `1,2 m/s`) ou butée dynamique brutale.
    3. *Couples Moteurs Certifiés* : Utilisation stricte des couples de calage crête et nominaux des actionneurs RobStride issus des fiches constructeur certifiées (sous 48 V).
    4. *Coefficients Dynamiques Normatifs* : Application des facteurs de choc et de transfert d'inertie de marche bipède (`k_dyn = 1,8 à 2,1` selon Eurocode 9 et l'état de l'art en robotique humanoïde).
- **Dérivation Analytique Explicite & Formulation Mathématique en Texte Clair** :
  - Pour chaque cas de charge modélisé, le dossier technique (`DOSSIER_TECHNIQUE_Calculs_FEA_...md`) doit obligatoirement expliciter la chaîne de calcul analytique complète :
    - Équations mécaniques explicites en texte clair ASCII (rappel : zéro dollar, zéro LaTeX) : `F = M / d`, `F = m * a * k_dyn`, `Sigma = M * y / I_z`, etc.
    - Bras de levier métrologiques extraits des cotes B-Rep CAO certifiées (`d`, `L`, coordonnées X, Y, Z).
    - Démonstration de l'équivalence statique en cas de déport du point d'application (garantie que le moment de renversement résultant à l'encastrement `M_base = F * L` demeure rigoureusement identique entre le calcul de pièce isolée et l'assemblage complet).
- **Tableau Systématique de Traçabilité des Hypothèses FEA** :
  - Tout dossier technique comportant des simulations numériques doit inclure dès sa section méthodologique un **tableau de traçabilité d'auditabilité** détaillant :
    - *Colonnes obligatoires* : Cas de charge | Axe/Plan cinématique | Sollicitation principale | Source motrice ou inertielle | Grandeur physique source | Bras de levier CAO (mm) | Formule analytique | Effort appliqué FEA (N) | Moment équivalent à l'encastrement (N.m) | Critère normatif d'acceptation.
- **Distinction Stricte entre Contrainte Crête et Percentile 95 (P95)** :
  - Tout compte-rendu ou script d'exploitation FEA doit obligatoirement distinguer :
    1. `Sigma_peak` (capturant les singularités numériques de maillage sur les arêtes d'encastrement) avec son facteur de sécurité associé `Sf_peak = Re / Sigma_peak`.
    2. `Sigma_P95` (reflétant la contrainte volumique nominale réelle subie par 95% de la matière de la pièce) avec son facteur de sécurité `Sf_P95 = Re / Sigma_P95`.
  - Seul `Sigma_P95` fait foi pour la résistance en fatigue cyclique (marche à 1,5 Hz, limite d'endurance Wöhler à 10^7 cycles).
- **Standards de Maillage et Intégrité Numérique (Gmsh / Netgen)** :
  - Utilisation systématique d'éléments volumiques tétraédriques quadratiques de second ordre (**C3D10** à 10 nœuds).
  - Contrôle du Jacobien strictement positif (`Jacobien min > 0,35`) sur 100% des éléments du maillage, avec zéro élément retourné ou dégénéré.

