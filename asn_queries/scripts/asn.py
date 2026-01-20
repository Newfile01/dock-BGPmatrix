from .io import load_asn_file, save_asn_file, query_path


def build_or_load_asn(rmatrix):
    present_path = query_path("asn_present.txt")
    core_path = query_path("asn_core.txt")
    branch_path = query_path("asn_branch.txt")

    if all(map(lambda p: p and __import__("os").path.exists(p),
               [present_path, core_path, branch_path])):

        asn_present, present_count = load_asn_file(present_path)
        asn_core, core_count = load_asn_file(core_path)
        asn_branch, branch_count = load_asn_file(branch_path)

        print(f"✅ Nombre d'ASN présents : {present_count}")
        print(f"♥️  Nombre total de Core AS : {core_count}")
        print(f"🌿 Nombre total de Branch AS : {branch_count}")

        return asn_present, asn_core, asn_branch

    # Construction
    asn_set = set()
    with open("core-20000.20250101.as-rel2.txt", "r") as f:
        for line in f:
            if line.strip():
                asn_set.add(line.split("|")[0].strip())

    asn_list = sorted(asn_set, key=int)
    asn_present = [a for a in asn_list if rmatrix.has_asn(a)]

    asn_core = [a for a in asn_present if rmatrix.is_core_asn(a)]
    asn_branch = [a for a in asn_present if rmatrix.is_branch_asn(a)]

    save_asn_file(present_path, asn_present)
    save_asn_file(core_path, asn_core)
    save_asn_file(branch_path, asn_branch)

    print(f"✅ Nombre d'ASN présents : {len(asn_present)}")
    print(f"🤍 Nombre total de Core AS : {len(asn_core)}")
    print(f"🌿 Nombre total de Branch AS : {len(asn_branch)}")

    return tuple(asn_present), tuple(asn_core), tuple(asn_branch)
