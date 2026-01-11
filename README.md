# dock-BGPmatrix
Conteneurisation de l'application Python matrix-BGPsim simulant les interconnexion BGP à l'échelle d'internet. L'objectif est d'aboutir à une image déployable rapidement et simplement permettant facilement la mise en place de l'accélération matérielle possible avec cette application.

# 🧭 ASN Queries

[[Accueil]|#accueil] | [**Arborescence**](#arborescence) | [**Modules**](#modules) | [**Exécution**](#exécution) | [**Résultats**](#résultats)

---

## Accueil {#accueil}
Description générale du projet.

---

## Arborescence {#arborescence}
```
asn_queries/
├── scripts/
│   ├── __init__.py
│   ├── io.py
│   ├── asn.py
│   ├── paths.py
│   └── main.py
└── queries/
    ├── asn_present.txt
    ├── asn_core.txt
    ├── asn_branch.txt
    └── asn_longest_path.txt
```
---

## Modules {#modules}
### `io.py`
- Gestion des entrées/sorties.
- Création du dossier `queries/`.

### `asn.py`
- Analyse des ASN (Core/Branch).

---

## Exécution {#exécution}
```bash
python3 asn_queries/scripts/main.py
```

---

## Résultats {#résultats}
- Fichiers générés : `asn_present.txt`, `asn_core.txt`, etc.
- Affichage des métriques en sortie standard.
