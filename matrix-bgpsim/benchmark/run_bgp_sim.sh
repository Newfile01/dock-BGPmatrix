#!/bin/bash
set -e

echo "⚙️  Configuration des paramètres de simulation BGP"

# ---------- 1️⃣ Paramètres utilisateur ----------
read -p "Nombre maximum d'AS à générer (max_asn_num) [ex: 10000]: " max_asn_num
read -p "Nombre de vagues de propagation BGP (max_iter) [ex: 32]: " max_iter
read -p "Nombre de processus CPU (n_jobs) [ex: 20]: " n_jobs
read -p "Nombre d'AS à vérifier pour la correction (n_sample) [ex: 20]: " n_sample

# ---------- Déterminer les backends ----------
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

# ---------- Fichier récap ----------
recap_file="simulation_recap.txt"
echo "Simulation BGP - Récapitulatif" > "$recap_file"
echo "Paramètres choisis :" >> "$recap_file"
echo "max_asn_num = $max_asn_num" >> "$recap_file"
echo "max_iter = $max_iter" >> "$recap_file"
echo "n_jobs = $n_jobs" >> "$recap_file"
echo "n_sample = $n_sample" >> "$recap_file"
echo "backends = ${backends[@]}" >> "$recap_file"
echo "" >> "$recap_file"

# ---------- 2️⃣ Génération topologies ----------
echo "🧩 Génération des topologies ..."
python3 sample_topology.py --max_asn_num "$max_asn_num"

topologies=("core-$max_asn_num.20250101.as-rel2.txt" "random-$max_asn_num.20250101.as-rel2.txt")

# ---------- 3️⃣ Lancer benchmark par backend et topologie ----------
for backend in "${backends[@]}"; do
    echo "📊 Benchmark backend: $backend" 
    echo "Backend: $backend" >> "$recap_file"

    for topo in "${topologies[@]}"; do
        echo "  ▶ Topologie: $topo"
        echo "Topologie: $topo" >> "$recap_file"

        # ---------- Mesure ressources ----------
        start_time=$(date +%s)

        # Exécution benchmark avec time (sortie du temps CPU réel)
        { /usr/bin/time -f "Temps réel: %e sec, CPU user: %U sec, CPU sys: %S sec" \
          python3 benchmark.py \
            --as_rels "$topo" \
            --max_iter "$max_iter" \
            --n_jobs "$n_jobs" \
            --n_sample "$n_sample" \
            --backend "$backend"; } 2>> "$recap_file"

        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo "Durée totale (wall clock) : ${duration} sec" >> "$recap_file"

        # ---------- RAM / swap ----------
        mem_info=$(ps -o pid,rss,vsz,comm -p $$ --no-headers)
        echo "RAM / VSZ (kB) : $mem_info" >> "$recap_file"

        # ---------- GPU usage (si nvidia-smi disponible) ----------
        if command -v nvidia-smi &> /dev/null; then
            echo "GPU status :" >> "$recap_file"
            nvidia-smi --query-gpu=index,name,utilization.gpu,utilization.memory,memory.total,memory.used --format=csv >> "$recap_file"
        fi

        echo "--------------------------------------" >> "$recap_file"
    done
done

echo
echo "✅ Simulation terminée. Récapitulatif disponible dans $recap_file"
