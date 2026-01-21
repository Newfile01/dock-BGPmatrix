"""
Module pour analyser les statistiques de la topologie AS.
"""

from collections import defaultdict, Counter
from typing import List, Tuple, Optional, Any
from pathlib import Path
from matrix_bgpsim import RMatrix


def get_top_connected_as(rmatrix, top_n: int = 10) -> List[Tuple[str, int]]:
    """
    Trouve les AS les plus connectés (avec le plus de relations).
    
    Args:
        rmatrix: Instance RMatrix chargée
        top_n: Nombre d'AS à retourner (défaut: 10)
    
    Returns:
        Liste de tuples (ASN, nombre_de_relations) triée par nombre de relations décroissant
    """
    # Dictionnaire pour compter les relations par AS
    asn_connections = defaultdict(int)
    
    # Parcourir tous les AS core et compter leurs relations
    # idx2ngbrs est une liste où chaque élément est un RelMap contenant les voisins
    # RelMap est un NamedTuple avec P2P, C2P, P2C qui sont des sets
    try:
        # Accéder à l'attribut privé __idx2asn__ qui est une liste
        if hasattr(rmatrix, '__idx2asn__'):
            idx2asn_list = rmatrix.__idx2asn__
            idx2ngbrs_list = rmatrix.__idx2ngbrs__
            num_asn = len(idx2asn_list)
        else:
            # Fallback : essayer d'utiliser idx2asn comme méthode et trouver le nombre d'AS
            # en testant jusqu'à obtenir une erreur
            num_asn = 0
            idx = 0
            while True:
                try:
                    rmatrix.idx2asn(idx)
                    idx += 1
                except (IndexError, AttributeError, TypeError, KeyError):
                    num_asn = idx
                    break
            idx2asn_list = None
            idx2ngbrs_list = None
        
        for idx in range(num_asn):
            if idx2asn_list is not None:
                asn = idx2asn_list[idx]
                ngbrs = idx2ngbrs_list[idx]
            else:
                asn = rmatrix.idx2asn(idx)
                ngbrs = rmatrix.idx2ngbrs(idx)
            
            # RelMap contient P2P, C2P, P2C qui sont des sets
            total_connections = len(ngbrs.P2P) + len(ngbrs.C2P) + len(ngbrs.P2C)
            asn_connections[asn] = total_connections
    except Exception as e:
        print(f"⚠️  Erreur lors du calcul des connexions : {e}")
        import traceback
        traceback.print_exc()
        return []
    
    # Trier par nombre de connexions décroissant
    sorted_asn = sorted(asn_connections.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_asn[:top_n]


def find_intersection_as(rmatrix, asn_core: List[str], min_paths: int = 5) -> Optional[Tuple[str, int, List[Tuple[str, str, List[str]]]]]:
    """
    Trouve un AS qui apparaît dans au moins min_paths chemins différents.
    
    Args:
        rmatrix: Instance RMatrix chargée (doit avoir été simulée avec save_next_hop=True)
        asn_core: Liste des AS core à analyser
        min_paths: Nombre minimum de chemins requis (défaut: 5)
    
    Returns:
        Tuple (ASN, nombre_de_chemins, liste_des_chemins_complets) ou None si aucun AS trouvé
        Chaque chemin est un tuple (src, dst, path) où path est la liste des AS intermédiaires
    """
    # Vérifier que la simulation a été exécutée
    if rmatrix.__state__ is None or rmatrix.__next_hop__ is None:
        print("⚠️  La simulation doit être exécutée avec save_next_hop=True pour utiliser get_path")
        return None
    
    # Compteur pour chaque AS : nombre de chemins où il apparaît
    asn_path_count = defaultdict(int)
    # Dictionnaire pour stocker les chemins complets pour chaque AS
    asn_paths = defaultdict(list)
    
    # Échantillonner des paires d'AS pour analyser les chemins
    # Augmenter la taille de l'échantillon pour avoir plus de chances de trouver un AS avec plusieurs chemins
    sample_size = min(200, len(asn_core))
    import random
    sampled_asn = random.sample(asn_core, sample_size) if len(asn_core) > sample_size else asn_core
    
    paths_analyzed = 0
    for i, src in enumerate(sampled_asn):
        for j, dst in enumerate(sampled_asn):
            if i >= j:  # Éviter les doublons et les chemins vers soi-même
                continue
            
            try:
                path = rmatrix.get_path(src, dst)
                if path is not None and len(path) > 0:
                    paths_analyzed += 1
                    # Compter chaque AS dans le chemin et stocker le chemin complet
                    for asn_in_path in path:
                        asn_path_count[asn_in_path] += 1
                        # Stocker le chemin complet (src, dst, path)
                        asn_paths[asn_in_path].append((src, dst, path))
                    
                    # Vérifier si on a trouvé un AS avec assez de chemins
                    for asn, count in asn_path_count.items():
                        if count >= min_paths:
                            # Limiter à 10 chemins pour l'affichage
                            return (asn, count, asn_paths[asn][:10])
            except Exception as e:
                # Ignorer les erreurs (AS non accessibles, etc.)
                continue
    
    # Si aucun AS n'a été trouvé avec min_paths, retourner celui avec le plus de chemins
    if asn_path_count:
        max_asn = max(asn_path_count.items(), key=lambda x: x[1])
        if max_asn[1] > 0:
            return (max_asn[0], max_asn[1], asn_paths[max_asn[0]][:10])
    
    return None


def get_path_stats_range(rmatrix, asn_core: List[str], sample_size: int = 200):
    """
    Trouve le minimum et maximum de chemins interceptés par un AS.
    
    Args:
        rmatrix: Instance RMatrix chargée (doit avoir été simulée avec save_next_hop=True)
        asn_core: Liste des AS core à analyser
        sample_size: Taille de l'échantillon pour l'analyse
    
    Returns:
        Tuple (min_paths, max_paths, path_count_dict) ou (None, None, None) si erreur
    """
    if rmatrix.__state__ is None or rmatrix.__next_hop__ is None:
        return None, None, None
    
    from collections import defaultdict
    import random
    
    asn_path_count = defaultdict(int)
    sample_size = min(sample_size, len(asn_core))
    sampled_asn = random.sample(asn_core, sample_size) if len(asn_core) > sample_size else asn_core
    
    for i, src in enumerate(sampled_asn):
        for j, dst in enumerate(sampled_asn):
            if i >= j:
                continue
            try:
                path = rmatrix.get_path(src, dst)
                if path is not None and len(path) > 0:
                    for asn_in_path in path:
                        asn_path_count[asn_in_path] += 1
            except Exception:
                continue
    
    if not asn_path_count:
        return None, None, None
    
    min_paths = min(asn_path_count.values())
    max_paths = max(asn_path_count.values())
    return min_paths, max_paths, asn_path_count


def display_path(rmatrix, src: str, dst: str, path: List[str]):
    """
    Affiche un chemin dans le même format que dans main.py.
    
    Args:
        rmatrix: Instance RMatrix
        src: AS source
        dst: AS destination
        path: Liste des AS intermédiaires
    """
    full = [src] + path + [dst]
    relations = []
    
    # Récupérer les relations entre chaque paire d'AS consécutifs
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
        
        # Espaces pour passer l'AS actuel
        relation_line += " " * len(asn)
        
        # Centrer la relation sous "___" (3 caractères)
        padding_left = (3 - len(rel)) // 2
        padding_right = 3 - len(rel) - padding_left
        relation_line += " " * padding_left + rel + " " * padding_right
    
    print(relation_line)
    print()


def analyze_topology_stats(rmatrix, asn_core: List[str], asn_present: List[str]):
    """
    Analyse les statistiques de la topologie et affiche les résultats.
    
    Args:
        rmatrix: Instance RMatrix chargée
        asn_core: Liste des AS core
        asn_present: Liste des AS présents dans la topologie
    """
    print("📊 Statistiques de la topologie\n")
    
    # 1. Top 10 AS les plus connectés
    print("🔗 Top 10 AS les plus connectés :\n")
    top_connected = get_top_connected_as(rmatrix, top_n=10)
    
    for rank, (asn, connections) in enumerate(top_connected, 1):
        # Obtenir les détails des relations pour cet AS
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
    
    print()
    
    # 2. AS à l'intersection de plusieurs chemins
    print("🔀 AS à l'intersection de plusieurs chemins :\n")
    intersection_as = find_intersection_as(rmatrix, list(asn_core), min_paths=5)
    
    if intersection_as:
        asn, path_count, paths = intersection_as
        print(f"  AS{asn} apparaît dans {path_count} chemins différents\n")
        if paths:
            print(f"  Chemins contenant AS{asn} :\n")
            for idx, (src, dst, path) in enumerate(paths, 1):
                print(f"  Chemin {idx} (AS{src} -> AS{dst}) :")
                display_path(rmatrix, src, dst, path)
    else:
        print("  Aucun AS trouvé dans au moins 5 chemins différents")
        print("  (La simulation doit être exécutée avec save_next_hop=True)")
    
    print()


def compute_topology_stats(rmatrix=None, asn_core: List[str] = None, asn_present: List[str] = None, lz4_file: str = None):
    """
    Fonction principale pour calculer et afficher les statistiques.
    Cette fonction est appelée depuis main.py.
    
    Args:
        rmatrix: Instance RMatrix (optionnel, sera chargée depuis lz4_file si non fournie)
        asn_core: Liste des AS core (optionnel, sera calculée si non fournie)
        asn_present: Liste des AS présents (optionnel, sera calculée si non fournie)
        lz4_file: Chemin vers le fichier .lz4 (optionnel, utilise le fichier par défaut si non fourni)
    """
    # Si rmatrix n'est pas fournie, charger depuis le fichier .lz4
    if rmatrix is None:
        if lz4_file is None:
            # Utiliser le même chemin que dans main.py
            from pathlib import Path
            script_dir = Path(__file__).parent
            lz4_file = script_dir / "rmatrix-cupy-core-20000.20250101.as-rel2.lz4"
        
        if not Path(lz4_file).exists():
            print(f"❌ Fichier {lz4_file} introuvable")
            return
        
        print(f"📂 Chargement du fichier : {lz4_file}\n")
        rmatrix = RMatrix.load(lz4_file)
    
    # Si asn_core ou asn_present ne sont pas fournis, les calculer
    if asn_core is None or asn_present is None:
        asn_present = [rmatrix.idx2asn(i) for i in range(len(rmatrix.idx2asn))]
        asn_core = [asn for asn in asn_present if rmatrix.is_core_asn(asn)]
    
    analyze_topology_stats(rmatrix, asn_core, asn_present)


if __name__ == "__main__":
    # Pour tester le script indépendamment
    from pathlib import Path
    import sys
    
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    sys.path.insert(0, str(parent_dir))
    
    from matrix_bgpsim import RMatrix
    
    # Charger la matrice
    rmatrix_path = script_dir / "rmatrix-cupy-core-20000.20250101.as-rel2.lz4"
    if rmatrix_path.exists():
        rmatrix = RMatrix.load(rmatrix_path)
        
        # Obtenir les AS core et présents
        asn_present = [rmatrix.idx2asn(i) for i in range(len(rmatrix.idx2asn))]
        asn_core = [asn for asn in asn_present if rmatrix.is_core_asn(asn)]
        
        analyze_topology_stats(rmatrix, asn_core, asn_present)
    else:
        print(f"❌ Fichier {rmatrix_path} introuvable")
