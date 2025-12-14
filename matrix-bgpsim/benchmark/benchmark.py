#!/usr/bin/env python
from pathlib import Path
from matrix_bgpsim import RMatrix
from correctness_test import check_correctness
import hashlib
import json
import time
import argparse

# ---------- Arguments CLI ----------
parser = argparse.ArgumentParser(description="Benchmark BGP avec RMatrix")
parser.add_argument("--as_rels", type=str, required=True,
                    help="Fichier AS relationships")
parser.add_argument("--max_iter", type=int, default=32,
                    help="Nombre de vagues de propagation BGP")
parser.add_argument("--n_jobs", type=int, default=20,
                    help="Nombre de processus CPU")
parser.add_argument("--n_sample", type=int, default=20,
                    help="Nombre d'AS à vérifier pour la correction")
parser.add_argument("--backend", type=str, choices=["cpu", "torch", "cupy"], default="cpu")
parser.add_argument("--repeat", type=int, default=1,
                    help="Nombre de répétitions du benchmark")
args = parser.parse_args()

script_dir = Path(__file__).resolve().parent
as_rels = Path(args.as_rels)

# ---------- Load checksums ----------
checksums = {}
checksum_file = script_dir/"md5-checksum.txt"
if checksum_file.exists():
    for line in open(checksum_file, "r"):
        checksum, filename = line.strip().split()
        checksums[filename] = checksum

# ---------- Vérification intégrité ----------
if as_rels.name in checksums:
    assert hashlib.md5(as_rels.read_bytes()).hexdigest() == checksums[as_rels.name], \
        "Checksum mismatch !"

# ---------- Benchmark ----------
rmatrix = RMatrix(as_rels)
elapse_times = []

for _ in range(args.repeat):
    t0 = time.perf_counter()
    rmatrix.run(
        n_jobs=args.n_jobs,
        max_iter=args.max_iter,
        save_next_hop=True,
        backend=args.backend
    )
    t1 = time.perf_counter()
    elapse_times.append(t1 - t0)

# ---------- Save & load ----------
rmatrix.dump(script_dir/f"rmatrix-{args.backend}-{as_rels.stem}.lz4")
rmatrix = RMatrix.load(script_dir/f"rmatrix-{args.backend}-{as_rels.stem}.lz4")

# ---------- Correction ----------
check_correctness(as_rels, rmatrix, n_sample=args.n_sample)

# ---------- Enregistrer résultats ----------
results = {as_rels.name: {args.backend: elapse_times}}
json.dump(results, open(script_dir/"results.json", "w"), indent=2)

print(f"✅ Benchmark terminé pour {as_rels.name} avec backend {args.backend}")
print(f"Temps : {elapse_times}")
