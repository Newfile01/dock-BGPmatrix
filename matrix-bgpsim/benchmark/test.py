from matrix_bgpsim import RMatrix

# Charger une topologie
rmatrix = RMatrix.load("rmatrix-torch-core-20000.20250101.as-rel2.lz4")

# Lancer la simulation
rmatrix.run(max_iter=32, save_next_hop=True, backend="torch", device="cuda:0")

# Vérifier la présence d'un AS
print("AS 1234 est-il présent ?", rmatrix.has_asn("1234"))

# Obtenir le chemin entre deux AS
path = rmatrix.get_path("1234", "5678")
print("Chemin :", path)

# Obtenir l'état de la route
priority, length = rmatrix.get_state("1234", "5678")
print(f"Priorité : {priority}, Longueur : {length}")
