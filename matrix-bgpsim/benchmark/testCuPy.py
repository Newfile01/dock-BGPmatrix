from matrix_bgpsim import RMatrix
import cupy as cp

# 1. Charger la topologie depuis un fichier .lz4
rmatrix = RMatrix.load("rmatrix-cupy-core-20000.20250101.as-rel2.lz4")

# 2. Vérifier la présence de CuPy et du GPU
try:
    cp.cuda.Device(0).compute_capability  # Teste si CuPy et le GPU sont disponibles
    print("CuPy et GPU sont disponibles. Utilisation du backend CuPy.")
except Exception as e:
    raise RuntimeError("CuPy ou le GPU n'est pas disponible. Vérifiez votre installation.") from e

# 3. Lancer la simulation avec le backend CuPy
# print("Lancement de la simulation BGP avec CuPy...")
# rmatrix.run(
#     n_jobs=1,
#     max_iter=32,
#     save_next_hop=True,
#     backend="cupy",
#     device=0  # Utilise le premier GPU disponible
# )

# 4. Tester la présence d'un AS
asn1 = "36555"
asn2 = "286"
if rmatrix.has_asn(asn1):
    print(f"\n✅ {asn1} est présent dans la topologie")
else:
    print(f"\n❌ ASN {asn1} n'existe pas dans la topologie")

# 5. Vérifier si un AS est Core ou Branch
if rmatrix.is_core_asn(asn1):
    print(f"\n 🤍{asn1} est un Core AS ")
elif rmatrix.is_branch_asn(asn1):
    print(f"\n 🌿 {asn1} est un Branch AS")



# 6. Obtenir un chemin entre deux AS existants
asn1, asn2 = "286", "36555"
if rmatrix.has_asn(asn1) and rmatrix.has_asn(asn2):
    path = rmatrix.get_path(asn1, asn2)
    print(f"\nChemin BGP entre {asn1} et {asn2} : {path}")

    # Afficher la priorité et la longueur du chemin
    priority, length = rmatrix.get_state(asn1, asn2)
    print(f"Priorité : {priority}, Longueur : {length}")
else:
    print(f"\nL'un des AS ({asn1}, {asn2}) n'est pas présent dans la topologie.")

# # 7. Afficher des statistiques sur la topologie
# print(f"\nNombre total d'AS dans la topologie : {rmatrix.num_asns}")
