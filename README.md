    # 🧭 ASN Queries — Analyse BGP modulaire pour matrix-bgpsim

    Ce projet fournit un script **modulaire, lisible et performant** permettant d’analyser une topologie BGP issue de **matrix-bgpsim**.

    Il conserve les performances du script initial (multiprocessing) tout en améliorant la lisibilité, la maintenabilité et l’exportabilité.

    ---

    ## 📁 Arborescence attendue

    ```
    asn_queries/
    ├── 📂 scripts/
    │   ├── __init__.py
    │   ├── io.py
    │   ├── asn.py
    │   ├── paths.py
    │   └── main.py
    |   └── stats.py
    |   └── menu.py
    |   └── references.py
    │
    └── 📂 queries/
        ├── asn_present.txt
        ├── asn_core.txt
        ├── asn_branch.txt
        └── asn_longest_path.txt
    ```
    ---

    ## 🧩 Détails des modules

    ---

    ### 🔹 io.py — Gestion des entrées / sorties

    - Création et vérification du dossier queries/

    - Test d’existence des fichiers de résultats

    - Lecture / écriture centralisée des fichiers

    - Déplacement d’anciens fichiers si nécessaire

    ➡️ Garantit une exécution propre, reproductible et sans doublons.

    ---

    ### 🔹 asn.py — Analyse des systèmes autonomes

    - Extraction des ASN présents dans la topologie

    - Classification des ASN en Core et Branch

    - Comptage et affichage des résultats

    - Calculs parallélisés via multiprocessing

    ➡️ Cœur logique de l’analyse BGP.

    ---

    ### 🔹 paths.py — Chemins et relations AS

    - Calcul du chemin AS le plus long

    - Analyse des relations AS le long de ce chemin :

        - Customer → Provider

        - Peer → Peer

        - Provider → Customer

    - Génération du tableau récapitulatif affiché en sortie

    ➡️ Partie analytique avancée du script.

    ---

    ### 🔹 main.py — Point d’entrée

    - Orchestration de l’ensemble des modules

    - Vérification de l’existence des résultats avant recalcul

    - Affichage final des métriques et tableaux

    ➡️ Interface principale du script.

    🛠️ Mise en place dans matrix-bgpsim

    Depuis la racine du projet matrix-bgpsim : `mv asn_queries matrix-bgpsim/benchmark/`

    ```
    matrix-bgpsim/
    └── benchmark/
        └── asn_queries/
            ├── scripts/
            └── queries/
    ```

    ▶️ Mode opératoire d’exécution

    Se placer dans le dossier benchmark/ puis lancer :

    ```
    python3 asn_queries/scripts/main.py
    ```

    📌 Le script peut être relancé plusieurs fois sans effet de bord.

    📊 Résultats attendus

    À l’exécution :

    - 📁 Création automatique du dossier queries/ si absent

    - 📄 Création ou réutilisation des fichiers :

        - `asn_present.txt`
        - `asn_core.txt`
        - `asn_branch.txt`
        - `asn_longest_path.txt`

    - 🔁 Aucun doublon de fichiers entre deux exécutions

    Affichage en sortie standard :

    - 🔢 Nombre total d’ASN présents

    - 🧠 Nombre d’ASN Core

    - 🌿 Nombre d’ASN Branch

    - 🧮 Longueur du chemin AS le plus long

    - 📊 Tableau récapitulatif des relations AS sur ce chemin