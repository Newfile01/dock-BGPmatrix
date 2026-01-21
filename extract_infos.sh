#!/bin/bash
set -euo pipefail

OUT_DIR="container_infos"
DOCKER_ARGS=(
  -q
  --rm
  -v "$(pwd)/${OUT_DIR}:/export"
  --entrypoint cp
  extract_image
  -r /workspace/container_struct/. /export/
)

mkdir -p "${OUT_DIR}"
# Construit l'image jusqu'à la couche extract
docker build -q -f dock-nct-py/Dockerfile --target extract -t extract_image .

# Extraction via entrypoint cp
docker run "${DOCKER_ARGS[@]}"

echo "💾 ✅ Les fichiers ont été copiés dans ${OUT_DIR}/"

