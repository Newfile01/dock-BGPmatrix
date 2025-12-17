from matrix_bgpsim import RMatrix
import cupy as cp
import os

# 1. Charger la topologie depuis un fichier .lz4
rmatrix = RMatrix.load("rmatrix-cupy-core-20000.20250101.as-rel2.lz4")

# 2. Vérifier la présence de CuPy et du GPU
try:
    cp.cuda.Device(0).compute_capability
    print("CuPy et GPU sont disponibles.")
except Exception as e:
    raise RuntimeError("CuPy ou le GPU n'est pas disponible. Vérifiez votre installation.") from e

print("\n" + "=" * 60 + "\n")

# 3. Vérifier si les fichiers existent déjà
files_to_check = ["asn_present.txt", "asn_core.txt", "asn_branch.txt"]
files_exist = all(os.path.exists(f) for f in files_to_check)

if not files_exist:
    # 4. Initialiser une liste pour stocker les ASN présents
    asn_list = []

    # 5. Boucle pour tester les ASN de 1 à 20000
    print("Début de la vérification des ASN de 1 à 20000...")
    for asn in range(1, 20001):
        asn_str = str(asn)
        if rmatrix.has_asn(asn_str):
            asn_list.append(asn_str)

    # 6. Convertir la liste en tuple pour un accès rapide
    asn_tuple = tuple(asn_list)
    print(f"\n✅ Nombre d'ASN présents dans la topologie : {len(asn_tuple)}")

    print("\nasn_tuple = ", end="")
    print(', '.join(f'"{asn}"' for asn in asn_tuple[:10]))  # Affiche les 10 premiers ASN
    if len(asn_tuple) > 10:
        print(", ...")

    # 7. Sauvegarder le tuple dans un fichier
    with open("asn_present.txt", "w") as f:
        for asn in asn_tuple:
            f.write(f"{asn}\n")
    print("\nListe des ASN présents sauvegardée dans 'asn_present.txt'.")

    # 8. Lire les ASN présents depuis le fichier
    with open("asn_present.txt", "r") as f:
        asn_present = [line.strip() for line in f.readlines()]

    # 9. Initialiser les listes pour Core AS et Branch AS
    asn_core = []
    asn_branch = []

    # 10. Vérifier chaque ASN pour déterminer s'il est Core ou Branch
    for asn in asn_present:
        if rmatrix.is_core_asn(asn):
            asn_core.append(asn)
        elif rmatrix.is_branch_asn(asn):
            asn_branch.append(asn)

    # 11. Convertir les listes en tuples
    asn_core_tuple = tuple(asn_core)
    asn_branch_tuple = tuple(asn_branch)

    # 12. Sauvegarder les résultats dans des fichiers
    with open("asn_core.txt", "w") as f:
        for asn in asn_core_tuple:
            f.write(f"{asn}\n")

    with open("asn_branch.txt", "w") as f:
        for asn in asn_branch_tuple:
            f.write(f"{asn}\n")

    print(f"\n 🤍 Nombre total de Core AS : {len(asn_core_tuple)}")
    print(f" 🌿 Nombre total de Branch AS : {len(asn_branch_tuple)}")

else:
    # 13. Charger les données depuis les fichiers existants
    print("Chargement des données depuis les fichiers existants...")

    with open("asn_present.txt", "r") as f:
        asn_present = [line.strip() for line in f.readlines()]
    asn_tuple = tuple(asn_present)

    with open("asn_core.txt", "r") as f:
        asn_core = [line.strip() for line in f.readlines()]
    asn_core_tuple = tuple(asn_core)

    with open("asn_branch.txt", "r") as f:
        asn_branch = [line.strip() for line in f.readlines()]
    asn_branch_tuple = tuple(asn_branch)

    print(f"\n✅ Nombre d'ASN présents dans la topologie : {len(asn_tuple)}")
    print(f" 🤍 Nombre total de Core AS : {len(asn_core_tuple)}")
    print(f" 🌿 Nombre total de Branch AS : {len(asn_branch_tuple)}")

print("\n" + "=" * 60 + "\n")

# 14. Tester les chemins entre chaque AS Core et les autres AS présents
max_path_length = 0
max_path = None
max_asn1 = None
max_asn2 = None

print("Début des tests de chemins entre AS Core et les autres AS...\n")

for asn1 in asn_core_tuple:
    for asn2 in asn_present:
        if asn1 == asn2:
            continue  # Éviter de tester un AS avec lui-même

        path = rmatrix.get_path(asn1, asn2)
        if path is not None and len(path) > max_path_length:
            max_path_length = len(path)
            max_path = path
            max_asn1 = asn1
            max_asn2 = asn2

# 15. Afficher et sauvegarder le chemin le plus long
if max_path is not None:
    result = (
        f"🔍 Chemin le plus long trouvé :\n"
        f"   - AS source : {max_asn1}\n"
        f"   - AS destination : {max_asn2}\n"
        f"   - Longueur du chemin : {max_path_length} AS intermédiaires\n"
        f"   - Chemin : {max_asn1} -> " + " -> ".join(max_path)
    )
    print(result)

    with open("asn_longest_path.txt", "w") as f:
        f.write(result)
else:
    print("\n❌ Aucun chemin valide trouvé.")

print("\n" + "=" * 60 + "\n")
