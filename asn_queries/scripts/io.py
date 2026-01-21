import os
from pathlib import Path

# Chemin vers le dossier queries dans asn_queries/queries/
# Le script est dans asn_queries/scripts/, donc on remonte d'un niveau puis on va dans queries/
SCRIPT_DIR = Path(__file__).parent
ASN_QUERIES_DIR = SCRIPT_DIR.parent
QUERY_DIR = str(ASN_QUERIES_DIR / "queries")

FILES = [
    "asn_present.txt",
    "asn_core.txt",
    "asn_branch.txt",
    "asn_longest_path.txt",
]


def ensure_query_dir():
    os.makedirs(QUERY_DIR, exist_ok=True)


def query_path(filename):
    return os.path.join(QUERY_DIR, filename)


def move_legacy_files():
    """Déplace les fichiers présents à différents endroits vers queries/"""
    for f in FILES:
        # Chercher dans plusieurs emplacements possibles
        possible_locations = [
            f,  # Répertoire courant
            os.path.join(SCRIPT_DIR, f),  # Dans scripts/
            os.path.join(ASN_QUERIES_DIR, f),  # Dans asn_queries/
            os.path.join(SCRIPT_DIR.parent.parent, f),  # Dans benchmark/
        ]
        
        for location in possible_locations:
            if os.path.exists(location) and not os.path.exists(query_path(f)):
                try:
                    os.rename(location, query_path(f))
                    print(f"📦 Déplacé {location} -> {query_path(f)}")
                except Exception as e:
                    print(f"⚠️  Erreur lors du déplacement de {location}: {e}")
                break


def load_asn_file(path):
    with open(path, "r") as f:
        lines = f.readlines()
    return tuple(l.strip() for l in lines[:-1]), int(lines[-1][2:])


def save_asn_file(path, data):
    with open(path, "w") as f:
        for a in data:
            f.write(f"{a}\n")
        f.write(f"# {len(data)}\n")
