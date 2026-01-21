"""
Module pour générer automatiquement le fichier references.txt
qui liste toutes les références à RMatrix/rmatrix dans les scripts Python.
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def scan_python_files(scripts_dir):
    """Scanne tous les fichiers .py dans le répertoire donné."""
    python_files = []
    for file_path in Path(scripts_dir).glob("*.py"):
        # Exclure le fichier references.py lui-même
        if file_path.name != "references.py":
            python_files.append(file_path)
    return sorted(python_files)


def find_references_in_file(file_path):
    """Trouve toutes les références à RMatrix/rmatrix dans un fichier."""
    references = defaultdict(list)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Erreur lors de la lecture de {file_path}: {e}")
        return references
    
    filename = file_path.name
    
    for line_num, line in enumerate(lines, start=1):
        # Pattern 1: rmatrix.method(...)
        pattern1 = r'\brmatrix\.(\w+)\s*\('
        matches = re.finditer(pattern1, line)
        for match in matches:
            method = match.group(1)
            references[f"rmatrix.{method}(...)"].append((filename, line_num, line.strip()))
        
        # Pattern 2: RMatrix.method(...)
        pattern2 = r'\bRMatrix\.(\w+)\s*\('
        matches = re.finditer(pattern2, line)
        for match in matches:
            method = match.group(1)
            references[f"RMatrix.{method}(...)"].append((filename, line_num, line.strip()))
        
        # Pattern 3: RMatrix.CONSTANT (attributs de classe)
        # Chercher RMatrix.CONSTANT qui n'est pas suivi de (
        pattern3 = r'\bRMatrix\.([A-Z][A-Z0-9_]+)(?!\s*\()'
        matches = re.finditer(pattern3, line)
        for match in matches:
            constant = match.group(1)
            references[f"RMatrix.{constant}"].append((filename, line_num, line.strip()))
        
        # Pattern 4: rmatrix comme paramètre de fonction
        # def function(rmatrix) ou def function(..., rmatrix, ...)
        pattern4 = r'\bdef\s+\w+\s*\([^)]*\brmatrix\b[^)]*\)'
        if re.search(pattern4, line):
            references["Paramètres de fonction rmatrix"].append((filename, line_num, line.strip()))
        
        # Pattern 5: rmatrix passé en argument (dans un appel de fonction)
        # function(rmatrix) ou function(..., rmatrix, ...)
        pattern5 = r'\w+\s*\([^)]*\brmatrix\b[^)]*\)'
        # Exclure les définitions de fonction (déjà capturées par pattern4)
        if not re.search(r'\bdef\s+', line):
            matches = re.finditer(pattern5, line)
            for match in matches:
                # Vérifier que ce n'est pas un appel de méthode sur rmatrix
                if not re.search(r'\brmatrix\.\w+\s*\(', line):
                    references["Passage de rmatrix en argument"].append((filename, line_num, line.strip()))
        
        # Pattern 6: _worker_rmatrix.method(...) ou autres variantes
        pattern6 = r'\b(_\w*rmatrix\w*)\.(\w+)\s*\('
        matches = re.finditer(pattern6, line)
        for match in matches:
            var_name = match.group(1)
            method = match.group(2)
            references[f"rmatrix.{method}(...)"].append((filename, line_num, f"via {var_name}.{method} - {line.strip()}"))
    
    return references


def generate_references_file(scripts_dir, output_file="references.txt"):
    """Génère le fichier references.txt avec toutes les références trouvées."""
    python_files = scan_python_files(scripts_dir)
    
    # Collecter toutes les références de tous les fichiers
    all_references = defaultdict(list)
    
    for file_path in python_files:
        file_refs = find_references_in_file(file_path)
        for key, values in file_refs.items():
            all_references[key].extend(values)
    
    # Trier les références par fichier puis par numéro de ligne
    for key in all_references:
        all_references[key].sort(key=lambda x: (x[0], x[1]))
    
    # Générer le contenu du fichier
    output_path = Path(scripts_dir) / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Références aux méthodes RMatrix/rmatrix dans les scripts Python\n")
        f.write("=" * 64 + "\n\n")
        
        # Collecter toutes les fonctions RMatrix (méthodes de classe et d'instance)
        rmatrix_class_methods = [k for k in all_references.keys() if k.startswith("RMatrix.") and k.endswith("(...)")]
        rmatrix_instance_methods = [k for k in all_references.keys() if k.startswith("rmatrix.") and k.endswith("(...)")]
        
        # Normaliser les noms de méthodes (enlever le préfixe pour avoir juste le nom)
        all_methods = set()
        method_to_key = {}
        
        for key in rmatrix_class_methods:
            method_name = key.replace("RMatrix.", "").replace("(...)", "")
            all_methods.add(method_name)
            method_to_key[method_name] = key
        
        for key in rmatrix_instance_methods:
            method_name = key.replace("rmatrix.", "").replace("(...)", "")
            all_methods.add(method_name)
            if method_name not in method_to_key:
                method_to_key[method_name] = key
        
        # SECTION 1: Liste de toutes les fonctions RMatrix utilisées (sans références)
        f.write("Fonctions RMatrix utilisées :\n")
        f.write("-" * 64 + "\n")
        for method in sorted(all_methods):
            f.write(f"{method}\n\n")
        
        f.write("\n")
        
        # SECTION 2: Références de chaque fonction RMatrix
        f.write("Références de chaque fonction RMatrix :\n")
        f.write("-" * 64 + "\n\n")
        
        for method in sorted(all_methods):
            # Chercher toutes les clés qui correspondent à cette méthode
            matching_keys = []
            for key in all_references.keys():
                if key.endswith("(...)") and method in key:
                    matching_keys.append(key)
            
            if matching_keys:
                f.write(f"{method}\n")
                for key in sorted(matching_keys):
                    for filename, line_num, context in all_references[key]:
                        # Vérifier si c'est une référence via une variable
                        if "via " in context:
                            note = context.split("via ")[1].split(" - ")[0]
                            f.write(f"  > {filename} - l. {line_num} (via {note})\n")
                        else:
                            f.write(f"  > {filename} - l. {line_num}\n")
                f.write("\n")
        
        # SECTION 3: Constantes RMatrix
        rmatrix_constants = [k for k in all_references.keys() if k.startswith("RMatrix.") and not k.endswith("(...)")]
        if rmatrix_constants:
            f.write("Constantes RMatrix :\n")
            f.write("-" * 64 + "\n\n")
            for constant in sorted(rmatrix_constants):
                f.write(f"{constant}\n")
                for filename, line_num, context in all_references[constant]:
                    f.write(f"  > {filename} - l. {line_num}\n")
                f.write("\n")
        
        # SECTION 4: Infos additionnelles
        f.write("Informations additionnelles :\n")
        f.write("-" * 64 + "\n\n")
        
        # Paramètres de fonction
        if "Paramètres de fonction rmatrix" in all_references:
            f.write("Paramètres de fonction rmatrix:\n")
            for filename, line_num, context in all_references["Paramètres de fonction rmatrix"]:
                # Extraire le nom de la fonction
                func_match = re.search(r'\bdef\s+(\w+)', context)
                func_name = func_match.group(1) if func_match else "?"
                f.write(f"  > {filename} - l. {line_num} ({func_name})\n")
            f.write("\n")
        
        # Passages en argument
        if "Passage de rmatrix en argument" in all_references:
            f.write("Passage de rmatrix en argument:\n")
            for filename, line_num, context in all_references["Passage de rmatrix en argument"]:
                f.write(f"  > {filename} - l. {line_num}\n")
            f.write("\n")
    
    print(f"✅ Fichier {output_path} mis à jour avec {len(all_references)} types de références trouvées.")


def update_references():
    """Fonction principale pour mettre à jour references.txt depuis le répertoire du script."""
    # Obtenir le répertoire du script actuel
    script_dir = Path(__file__).parent
    generate_references_file(script_dir)


if __name__ == "__main__":
    update_references()
