FROM pytorch/pytorch:latest AS base
# 🐳 Base Ubuntu 22.04.3 LTS

WORKDIR /workspace

# 📦 Installe les dépendances système nécessaires
RUN apt update -y && \
    apt upgrade -y && \
    apt install -y tree nano && \
    apt clean

# 🤖 Installe CuPy
# RUN pip install cupy-cuda13x
RUN conda install -c conda-forge cupy-core

# 📦 Installation de matrix-bgpsim
COPY matrix-bgpsim/ /workspace/matrix-bgpsim/
WORKDIR /workspace/matrix-bgpsim/matrix-bgpsim
# RUN pip install matrix-bgpsim[torch]
RUN pip install matrix-bgpsim[torch,cupy]


FROM base AS extract

ENV STRUCT_PATH=/workspace/container_struct

RUN mkdir -p ${STRUCT_PATH}

WORKDIR ${STRUCT_PATH}

# 📝 Récupération des infos de compatibilité avec matrix-bgpsim
RUN STRUCT_PATH="/workspace/container_struct" && \
    cat /etc/os-release | grep "PRETTY" > mx-bgp_compatibility.txt && \
    nvidia-smi -L | awk '{print $3 " "  $4 " "  $5 " " $6 " " $7 " " $8}' >> mx-bgp_compatibility.txt && \
    python --version >> mx-bgp_compatibility.txt && \
    pip list | grep -E '^(pip|lz4|numpy|cupy|setuptools|torch[[:space:]]+)' >> mx-bgp_compatibility.txt

# 📋 Extractions de l'ensemble des composants Python installés
RUN STRUCT_PATH="/workspace/container_struct" && \
    pip freeze > requirements.txt && \
    grep -E '^([^=]+)==[^=]+$' requirements.txt > requirements_clean.txt && \
    grep -E '^([^ ]+) @ ' requirements.txt >> requirements_clean.txt && \
    rm -f requirements.txt && \
    mv requirements_clean.txt requirements.txt

# 🌳 Arborescence du système de fichiers
RUN tree -L 2 / > fs_tree.log 2>&1


FROM base AS prod
WORKDIR /workspace/matrix-bgpsim/matrix-bgpsim

# 🚀 Commande par défaut
CMD [ "/bin/bash" ]
