import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour permettre les imports
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(script_dir))  # Pour permettre l'import de references.py

from matrix_bgpsim import RMatrix
from scripts.io import ensure_query_dir, move_legacy_files
from scripts.asn import build_or_load_asn
from scripts.paths import load_or_compute_longest_path
from scripts.paths import max_path
from stats import compute_topology_stats
from references import update_references

##################################################
# 🚀 INITIALISATION                              #
##################################################

ensure_query_dir()
move_legacy_files()

# Charger le fichier .lz4 depuis le répertoire scripts/
rmatrix_file = script_dir / "rmatrix-cupy-core-20000.20250101.as-rel2.lz4"
if not rmatrix_file.exists():
    # Essayer depuis le répertoire parent (benchmark/)
    rmatrix_file = parent_dir / "rmatrix-cupy-core-20000.20250101.as-rel2.lz4"

rmatrix = RMatrix.load(rmatrix_file)

##################################################
# 📊 ASN                                         #
##################################################
print("\n" + "=" * 60 + "\n")
asn_present, asn_core, asn_branch = build_or_load_asn(rmatrix)

##################################################
# 🧮 CHEMIN LE PLUS LONG                          #
##################################################

src, dst, path, length = load_or_compute_longest_path(
    rmatrix, asn_core, list(asn_present)
)

##################################################
# 📊 AFFICHAGE COMPACT DU CHEMIN                  #
##################################################

if path:
    full = [src] + path + [dst]
    relations = []
    
    # Récupérer les relations entre chaque paire d'AS consécutifs
    for i in range(len(full) - 1):
        p, _ = rmatrix.get_state(full[i], full[i + 1])
        rel = "P2C" if p == RMatrix.P2C else "P2P" if p == RMatrix.P2P else "C2P"
        relations.append(rel)
    
    # Afficher le chemin compact
    print("\n" + "=" * 60 + "\n")
    print("🗺️  Chemin le plus long :\n")
    
    # Ligne 1 : AS séparés par ___
    path_line = "___".join(full)
    print(path_line)
    
    # Ligne 2 : Relations alignées sous les "___"
    # Chaque relation doit être centrée sous son "___" (3 caractères)
    relation_line = ""
    
    for i in range(len(full) - 1):
        asn = full[i]
        rel = relations[i]
        
        # Espaces pour passer l'AS actuel
        relation_line += " " * len(asn)
        
        # Centrer la relation sous "___" (3 caractères)
        padding_left = (3 - len(rel)) // 2
        padding_right = 3 - len(rel) - padding_left
        relation_line += " " * padding_left + rel + " " * padding_right
    
    print(relation_line)

##################################################
# 📊 STATISTIQUES DE LA TOPOLOGIE                #
##################################################
print("\n" + "=" * 60 + "\n")
compute_topology_stats(rmatrix, list(asn_core), list(asn_present))

##################################################
# 📝 MISE À JOUR DES RÉFÉRENCES                  #
##################################################
print("\n" + "=" * 60 + "\n")
# Mettre à jour le fichier references.txt en dernier
update_references()
print("\n" + "=" * 60 + "\n")