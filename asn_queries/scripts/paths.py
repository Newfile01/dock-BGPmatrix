import os
from multiprocessing import Pool
from functools import lru_cache
from .io import query_path

max_path = None
max_asn1 = None
max_asn2 = None
max_path_length = 0

# Cache global pour chaque worker (initialisé dans init_worker)
_worker_rmatrix = None
_worker_cache = None


def init_worker(rmatrix):
    """Initialise le cache pour chaque worker"""
    global _worker_rmatrix, _worker_cache
    _worker_rmatrix = rmatrix
    
    @lru_cache(maxsize=None)
    def cached_get_path(a, b):
        return _worker_rmatrix.get_path(a, b)
    _worker_cache = cached_get_path


def get_path_cached(a, b):
    """Utilise le cache du worker pour obtenir un chemin"""
    if _worker_cache is None:
        raise RuntimeError("Worker not initialized")
    return _worker_cache(a, b)


def process_chunk(args):
    core_chunk, present_chunk = args
    results = {}
    for a1 in core_chunk:
        for a2 in present_chunk:
            if a1 != a2:
                path = get_path_cached(a1, a2)
                if path:
                    results[(a1, a2)] = (len(path), path)
    return results


def find_longest_path(rmatrix, asn_core, asn_present):
    global max_path, max_asn1, max_asn2, max_path_length

    max_path = None
    max_path_length = 0
    max_asn1 = None
    max_asn2 = None

    csize = max(1, int(len(asn_core) * 0.1))
    psize = max(1, int(len(asn_present) * 0.1))

    args = [
        (asn_core[i:i + csize], asn_present[j:j + psize])
        for i in range(0, len(asn_core), csize)
        for j in range(0, len(asn_present), psize)
    ]

    with Pool(8, initializer=init_worker, initargs=(rmatrix,)) as pool:
        for result in pool.imap_unordered(process_chunk, args):
            for (a1, a2), (length, path) in result.items():
                if length > max_path_length:
                    max_path_length = length
                    max_path = path
                    max_asn1 = a1
                    max_asn2 = a2

    return max_asn1, max_asn2, max_path, max_path_length


def load_or_compute_longest_path(rmatrix, asn_core, asn_present):
    path_file = query_path("asn_longest_path.txt")

    if os.path.exists(path_file):
        with open(path_file) as f:
            content = f.read()

        src = dst = None
        path = []
        length = 0

        for line in content.splitlines():
            if "AS source" in line:
                src = line.split(": ")[1]
            elif "AS destination" in line:
                dst = line.split(": ")[1]
            elif "Longueur du chemin" in line:
                length = int(line.split(": ")[1].split()[0])
            elif "Chemin :" in line:
                parts = line.split(" -> ")
                path = parts[1:-1]

        return src, dst, path, length

    src, dst, path, length = find_longest_path(rmatrix, asn_core, asn_present)

    if path:
        with open(path_file, "w") as f:
            f.write(
                f"🔍 Chemin le plus long trouvé :\n"
                f"   - AS source : {src}\n"
                f"   - AS destination : {dst}\n"
                f"   - Longueur du chemin : {length} AS intermédiaires\n"
                f"   - Chemin : {src} -> " + " -> ".join(path) + f" -> {dst}\n"
            )

    return src, dst, path, length
