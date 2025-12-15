#!/bin/bash
set -e

echo "⚙️  Configuration des paramètres de simulation BGP"

# --- Interactions utilisateur ---
read -p "Nombre maximum d'AS à générer (max_asn_num) [ex: 10000]: " max_asn_num
read -p "Nombre de vagues de propagation BGP (max_iter) [ex: 32]: " max_iter
read -p "Nombre de processus CPU (n_jobs) [ex: 20]: " n_jobs
read -p "Nombre d'AS à vérifier pour la correction (n_sample) [ex: 20]: " n_sample

# Backend logique
if [ "$max_iter" -gt 1 ]; then
    echo "⚠️ max_iter > 1, CuPy sera désactivé pour éviter les problèmes GPU"
    backends=("cpu" "torch")
else
    read -p "Inclure CuPy pour le GPU ? (y/N): " use_cupy
    if [[ "$use_cupy" =~ ^[Yy]$ ]]; then
        backends=("cpu" "torch" "cupy")
    else
        backends=("cpu" "torch")
    fi
fi

echo
echo "📝 Paramètres choisis :"
echo "max_asn_num = $max_asn_num"
echo "max_iter = $max_iter"
echo "n_jobs = $n_jobs"
echo "n_sample = $n_sample"
echo "backends = ${backends[@]}"
echo

# --- Étape 1 : Générer les topologies ---
echo "🧩 Génération des topologies avec sample_topology.py ..."
python3 sample_topology.py --max_asn_num "$max_asn_num"

# Les fichiers générés : core-xxxx, random-xxxx
topologies=("core-$max_asn_num.20250101.as-rel2.txt" "random-$max_asn_num.20250101.as-rel2.txt")

# --- Étape 2 : Lancer benchmark.py ---
for topo in "${topologies[@]}"; do
    echo "📊 Benchmark pour $topo"
    for backend in "${backends[@]}"; do
        echo "  ▶ Backend : $backend"
        python3 benchmark.py \
            --as_rels "$topo" \
            --max_iter "$max_iter" \
            --n_jobs "$n_jobs" \
            --n_sample "$n_sample" \
            --backend "$backend"
    done
done

echo
echo "✅ Simulation terminée. Les fichiers .lz4 et results.json ont été générés."
