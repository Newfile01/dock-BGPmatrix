FROM quay.io/jupyter/base-notebook:latest

USER root

# Libs Python pour modélisation BGP
RUN pip install --no-cache-dir \
    networkx \
    plotly \
    ipywidgets \
    pyvis \
    matplotlib \
    pandas

WORKDIR /home/jovyan/work/matrix-bgpsim/matrix_bgpsim
RUN pip install matrix-bgpsim[torch]


# Activation widgets JupyterLab
WORKDIR /home/jovyan/work
RUN jupyter labextension enable @jupyter-widgets/jupyterlab-manager

USER root
