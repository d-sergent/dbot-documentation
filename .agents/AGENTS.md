# D-Bot Project Rules

## Documentation and Knowledge Base Search (RAG)
- Whenever you need to search or verify details about the D-Bot project (such as mechanical specs, electronics, motor choices, wiring, CAN bus, or software components), you MUST query the local RAG database first.
- To perform this query, run the following command using the shell:
  `/opt/homebrew/bin/python3.11 "/Users/Shared/Mon Google Drive Physique/Documentation/Code/rag/ask_rag.py" --search-only --mode naive "<your search terms>"`
- Always prioritize the retrieved context over general model knowledge for D-Bot specifications, measurements, and layouts.

## Interaction & Workflow Rules
- ALWAYS provide a detailed text explanation of the problem, diagnosis, and proposed code changes FIRST in your response message BEFORE invoking any `git push` or tool execution.
- NEVER run `git push` or execute modifying commands without explaining the rationale to the user beforehand in the text output.

## Jetson Package Management & PyTorch GPU Protection
- **JetPack Python Package Protection**: When installing any Python package via `pip` or suggesting installation commands for the Jetson Orin Nano, ALWAYS append the `--no-deps` flag (e.g. `pip install <package> --no-deps`).
- **NEVER** run `pip install torch` or `pip install torchvision` without `--no-deps` or without using the official NVIDIA JetPack 6.1 wheel, to prevent overwriting the native CUDA 12.2 GPU bindings.

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

## Cartographie des Usinages, Chanfreins, Fraisures & Ébavurages d'Atelier
- **Obligation de Spécification des Chanfreins & Cassages d'Arêtes** :
  - Aucun perçage, chambrage, fraisure conique ou chant débité ne doit être laissé sans spécification géométrique d'ébavurage dans les dossiers techniques d'usinage (C500 ou atelier).
  - Pour chaque opération de perçage ou de découpe, vous DEVEZ SYSTÉMATIQUEMENT mettre à jour la section et le **tableau récapitulatif des chanfreins et fraisures** du dossier technique concerné :
    - Chanfrein d'entrée et de sortie sur perçages lisses débouchants (typiquement `0,2 mm × 45°` à `0,3 mm × 45°`) pour éliminer le morfil de perçage et garantir une assise métal-métal parfaitement plane sous tête de vis, sous entretoise ou sous rondelle.
    - Fraisures coniques à 90° (vis FHC) : spécifier le diamètre de fraisure supérieur et la profondeur exacte pour un **noyage à fleur rigoureux à 0,0 mm** (zéro saillie de tête).
    - Chants débités et bords sciés : cassage d'arête systématique (typiquement `0,5 mm × 45°`).
    - Pliures et congés d'appui : chanfreinage adapté (`0,5 mm × 45°`) pour éviter le contact franc sur le congé intérieur naturel des profilés marchands.

