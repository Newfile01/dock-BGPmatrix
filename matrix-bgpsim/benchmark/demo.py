from matrix_bgpsim import RMatrix

rmatrix = RMatrix.load("rmatrix-torch-core-20000.20250101.as-rel2.lz4")

# rmatrix_loaded = RMatrix(input_rels="subset_15000_as.txt")
# rmatrix_loaded.load("rmatrix-torch-core-10000.20250101.as-rel2.lz4")
# print("Topologie chargé?e depuis rmatrix_demo.lz4")

# ---- Simulation BGP CPU-safe ----
#rmatrix.run(
 #   max_iter=32,        # maximum route propagation iterations
  #  save_next_hop=True, # store next-hop information
   # backend="torch",    # use PyTorch CPU/GPU backend
   # device="cuda:0"     # specify CPU/GPU device (defaults to "cuda:0" if available)
#)
#print("Simulation BGP terminee.")

# ---- Exemple : é?tat de la simulation pour un chemin ----


priority, length = rmatrix.get_state("286","36555")
print("Route prerentielle 286->36555 : priorite ? =", priority, ", longueur =", length)

# ---- Exemple : chemin BGP complet ----
as_path = rmatrix.get_path("286", "36555")
print("Chemin BGP 286->36555 :", as_path)

# ---- Vé?rifier la pré?sence d'un ASN ----
print("ASN 36555 pré?sent ?", rmatrix.has_asn(36555))
print("ASN 26577 pré?sent ?", rmatrix.has_asn(26577))

# ---- Convertir ASN <-> index ----
idx_36555 = rmatrix.asn2idx(36555)
asn_from_idx = rmatrix.idx2asn(idx_36555)
print("Index interne de 36555 :", idx_36555)
print("ASN depuis index :", asn_from_idx)

# ---- Voisins et relations ----
neighbors = rmatrix.idx2ngbrs(idx_36555)
print("Voisins de 36555 (limité? à? 5) :", [rmatrix.idx2asn(n) for n in neighbors[:5]])

for n in neighbors[:5]:
    tags = []
    if rmatrix.C2P(idx_36555, n): tags.append("C2P")
    if rmatrix.P2C(idx_36555, n): tags.append("P2C")
    if rmatrix.P2P(idx_36555, n): tags.append("P2P")
    if rmatrix.BranchRoute(idx_36555, n): tags.append("BranchRoute")
    print(f"36555 -> {rmatrix.idx2asn(n)} : {' | '.join(tags)}")

# ---- BRts ----
print("BRts de 36555 :", rmatrix.asn2brts(36555)[:5])

# ---- Vé?rifier Core / Branch ----
print("36555 est Core ?", rmatrix.is_core_asn(36555))
print("26577 est Branch ?", rmatrix.is_branch_asn(26577))

# ---- Sauvegarde et chargement ----
rmatrix.dump("rmatrix_demo.lz4")
print("Topologie sauvegardé?e dans rmatrix_demo.lz4")



# ---- RelMap (relations internes) ----s
# Affiche un petit extrait de la matrice des relations
print("Extrait RelMap (5 premiers indices de 36555) :")
for n in neighbors[:5]:
    print(f"36555 -> {rmatrix.idx2asn(n)} :", rmatrix.RelMap[idx_36555][n])
root@43373507c6ca:/workspace/matrix-bgpsim/benchmark# cat demo.py 
from matrix_bgpsim import RMatrix

rmatrix = RMatrix.load("rmatrix-torch-core-20000.20250101.as-rel2.lz4")

# rmatrix_loaded = RMatrix(input_rels="subset_15000_as.txt")
# rmatrix_loaded.load("rmatrix-torch-core-10000.20250101.as-rel2.lz4")
# print("Topologie chargé?e depuis rmatrix_demo.lz4")

# ---- Simulation BGP CPU-safe ----
#rmatrix.run(
 #   max_iter=32,        # maximum route propagation iterations
  #  save_next_hop=True, # store next-hop information
   # backend="torch",    # use PyTorch CPU/GPU backend
   # device="cuda:0"     # specify CPU/GPU device (defaults to "cuda:0" if available)
#)
#print("Simulation BGP terminee.")

# ---- Exemple : é?tat de la simulation pour un chemin ----


priority, length = rmatrix.get_state("286","36555")
print("Route prerentielle 286->36555 : priorite ? =", priority, ", longueur =", length)

# ---- Exemple : chemin BGP complet ----
as_path = rmatrix.get_path("286", "36555")
print("Chemin BGP 286->36555 :", as_path)

# ---- Vé?rifier la pré?sence d'un ASN ----
print("ASN 36555 pré?sent ?", rmatrix.has_asn(36555))
print("ASN 26577 pré?sent ?", rmatrix.has_asn(26577))

# ---- Convertir ASN <-> index ----
idx_36555 = rmatrix.asn2idx(36555)
asn_from_idx = rmatrix.idx2asn(idx_36555)
print("Index interne de 36555 :", idx_36555)
print("ASN depuis index :", asn_from_idx)

# ---- Voisins et relations ----
neighbors = rmatrix.idx2ngbrs(idx_36555)
print("Voisins de 36555 (limité? à? 5) :", [rmatrix.idx2asn(n) for n in neighbors[:5]])

for n in neighbors[:5]:
    tags = []
    if rmatrix.C2P(idx_36555, n): tags.append("C2P")
    if rmatrix.P2C(idx_36555, n): tags.append("P2C")
    if rmatrix.P2P(idx_36555, n): tags.append("P2P")
    if rmatrix.BranchRoute(idx_36555, n): tags.append("BranchRoute")
    print(f"36555 -> {rmatrix.idx2asn(n)} : {' | '.join(tags)}")

# ---- BRts ----
print("BRts de 36555 :", rmatrix.asn2brts(36555)[:5])

# ---- Vé?rifier Core / Branch ----
print("36555 est Core ?", rmatrix.is_core_asn(36555))
print("26577 est Branch ?", rmatrix.is_branch_asn(26577))

# ---- Sauvegarde et chargement ----
rmatrix.dump("rmatrix_demo.lz4")
print("Topologie sauvegardé?e dans rmatrix_demo.lz4")



# ---- RelMap (relations internes) ----s
# Affiche un petit extrait de la matrice des relations
print("Extrait RelMap (5 premiers indices de 36555) :")
for n in neighbors[:5]:
    print(f"36555 -> {rmatrix.idx2asn(n)} :", rmatrix.RelMap[idx_36555][n])
