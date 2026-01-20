"""
Menu interactif pour analyser la topologie AS.
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour permettre les imports
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(script_dir))

from matrix_bgpsim import RMatrix
from scripts.io import ensure_query_dir, move_legacy_files
from scripts.asn import build_or_load_asn
from scripts.paths import load_or_compute_longest_path
from stats import get_top_connected_as, find_intersection_as, display_path, get_path_stats_range


def load_rmatrix():
    """Charge la matrice RMatrix."""
    ensure_query_dir()
    move_legacy_files()
    
    # Charger le fichier .lz4 depuis le répertoire scripts/
    rmatrix_file = script_dir / "rmatrix-cupy-core-20000.20250101.as-rel2.lz4"
    if not rmatrix_file.exists():
        # Essayer depuis le répertoire parent (benchmark/)
        rmatrix_file = parent_dir / "rmatrix-cupy-core-20000.20250101.as-rel2.lz4"
    
    if not rmatrix_file.exists():
        print(f"❌ Fichier {rmatrix_file} introuvable")
        return None
    
    print(f"📂 Chargement de la matrice...")
    return RMatrix.load(rmatrix_file)


def display_asn_stats(rmatrix, asn_present, asn_core, asn_branch):
    """Affiche les statistiques AS (présents, core, branch)."""
    print("\n" + "=" * 60)
    print("📊 Statistiques AS\n")
    print(f"✅ Nombre d'ASN présents : {len(asn_present)}")
    print(f"🤍 Nombre total de Core AS : {len(asn_core)}")
    print(f"🌿 Nombre total de Branch AS : {len(asn_branch)}")
    print("=" * 60 + "\n")


def display_longest_path(rmatrix, asn_core, asn_present):
    """Affiche le chemin le plus long avec le nombre d'AS traversé."""
    print("\n" + "=" * 60)
    print("🧮 Calcul du chemin le plus long...\n")
    
    src, dst, path, length = load_or_compute_longest_path(
        rmatrix, asn_core, list(asn_present)
    )
    
    if path:
        full = [src] + path + [dst]
        # Le nombre d'AS traversé = nombre d'AS intermédiaires + 2 (src et dst)
        num_as_traversed = len(full)
        
        print("🗺️  Chemin le plus long :")
        print(f"   Nombre d'AS traversé : {num_as_traversed}\n")
        
        relations = []
        for i in range(len(full) - 1):
            p, _ = rmatrix.get_state(full[i], full[i + 1])
            rel = "P2C" if p == RMatrix.P2C else "P2P" if p == RMatrix.P2P else "C2P"
            relations.append(rel)
        
        # Ligne 1 : AS séparés par ___
        path_line = "___".join(full)
        print(path_line)
        
        # Ligne 2 : Relations alignées sous les "___"
        relation_line = ""
        for i in range(len(full) - 1):
            asn = full[i]
            rel = relations[i]
            relation_line += " " * len(asn)
            padding_left = (3 - len(rel)) // 2
            padding_right = 3 - len(rel) - padding_left
            relation_line += " " * padding_left + rel + " " * padding_right
        
        print(relation_line)
    else:
        print("❌ Aucun chemin trouvé")
    
    print("=" * 60 + "\n")


def display_top_connected(rmatrix):
    """Affiche les 10 AS les plus connectés."""
    print("\n" + "=" * 60)
    print("🔗 Top 10 AS les plus connectés :\n")
    
    top_connected = get_top_connected_as(rmatrix, top_n=10)
    
    for rank, (asn, connections) in enumerate(top_connected, 1):
        try:
            if rmatrix.has_asn(asn):
                idx = rmatrix.asn2idx(asn)
                ngbrs = rmatrix.idx2ngbrs(idx)
                p2c = len(ngbrs.P2C)
                p2p = len(ngbrs.P2P)
                c2p = len(ngbrs.C2P)
                print(f"  {rank:2d}. AS{asn:>8s} : {connections:4d} relations totales "
                      f"(P2C: {p2c:3d}, P2P: {p2p:3d}, C2P: {c2p:3d})")
            else:
                print(f"  {rank:2d}. AS{asn:>8s} : {connections:4d} relations")
        except Exception as e:
            print(f"  {rank:2d}. AS{asn:>8s} : {connections:4d} relations (erreur détails: {e})")
    
    print("=" * 60 + "\n")


def display_intersection_as(rmatrix, asn_core):
    """Affiche un AS à l'intersection de plusieurs chemins avec demande interactive."""
    print("\n" + "=" * 60)
    print("🔀 AS à l'intersection de plusieurs chemins\n")
    
    if rmatrix.__state__ is None or rmatrix.__next_hop__ is None:
        print("⚠️  La simulation doit être exécutée avec save_next_hop=True pour utiliser get_path")
        print("=" * 60 + "\n")
        return
    
    print("📊 Analyse des chemins...\n")
    min_paths, max_paths, path_count = get_path_stats_range(rmatrix, list(asn_core))
    
    if min_paths is None:
        print("❌ Aucun chemin analysé")
        print("=" * 60 + "\n")
        return
    
    print(f"   Minimum de chemins interceptés par un AS : {min_paths}")
    print(f"   Maximum de chemins interceptés par un AS : {max_paths}\n")
    
    while True:
        try:
            user_input = input(f"   Entrez le nombre minimum de chemins requis [{min_paths}-{max_paths}] (ou 'q' pour quitter) : ")
            if user_input.lower() == 'q':
                print("=" * 60 + "\n")
                return
            
            min_paths_req = int(user_input)
            if min_paths_req < min_paths or min_paths_req > max_paths:
                print(f"⚠️  Veuillez entrer un nombre entre {min_paths} et {max_paths}")
                continue
            
            break
        except ValueError:
            print("⚠️  Veuillez entrer un nombre valide")
        except KeyboardInterrupt:
            print("\n" + "=" * 60 + "\n")
            return
    
    print(f"\n🔍 Recherche d'un AS dans au moins {min_paths_req} chemins...\n")
    
    intersection_as = find_intersection_as(rmatrix, list(asn_core), min_paths=min_paths_req)
    
    if intersection_as:
        asn, path_count_val, paths = intersection_as
        print(f"✅ AS{asn} apparaît dans {path_count_val} chemins différents\n")
        if paths:
            print(f"   Chemins contenant AS{asn} :\n")
            for idx, (src, dst, path) in enumerate(paths, 1):
                print(f"   Chemin {idx} (AS{src} -> AS{dst}) :")
                display_path(rmatrix, src, dst, path)
    else:
        print(f"❌ Aucun AS trouvé dans au moins {min_paths_req} chemins différents")
    
    print("=" * 60 + "\n")


def display_menu():
    """Affiche le menu principal."""
    print("\n" + "=" * 60)
    print("📋 MENU PRINCIPAL")
    print("=" * 60)
    print("1. 📊 Afficher les statistiques AS (présents, core, branch)")
    print("2. 🗺️  Afficher le chemin le plus long")
    print("3. 🔗 Afficher les 10 AS les plus connectés")
    print("4. 🔀 Afficher un AS à l'intersection de plusieurs chemins")
    print("5. 🚪 Quitter")
    print("=" * 60 + "\n")


def main():
    """Fonction principale du menu interactif."""
    print("🚀 Initialisation...\n")
    
    rmatrix = load_rmatrix()
    if rmatrix is None:
        return
    
    print("✅ Matrice chargée avec succès\n")
    
    # Charger les données AS
    asn_present, asn_core, asn_branch = build_or_load_asn(rmatrix)
    
    while True:
        display_menu()
        
        try:
            choice = input("👉 Votre choix : ").strip()
            
            if choice == "1":
                display_asn_stats(rmatrix, asn_present, asn_core, asn_branch)
            elif choice == "2":
                display_longest_path(rmatrix, asn_core, asn_present)
            elif choice == "3":
                display_top_connected(rmatrix)
            elif choice == "4":
                display_intersection_as(rmatrix, asn_core)
            elif choice == "5":
                print("\n👋 Au revoir !\n")
                break
            else:
                print("\n⚠️  Choix invalide. Veuillez entrer un nombre entre 1 et 5.\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !\n")
            break
        except Exception as e:
            print(f"\n❌ Erreur : {e}\n")


if __name__ == "__main__":
    main()
