"""==========================================================================
 OUTIL DU PROFESSEUR — les blocs ✅ SOLUTION suffisent-ils ?
==========================================================================

Ce script vérifie, pour chaque séance, que les solutions imprimées dans le
fichier de TP des étudiants permettent bien d'obtenir un fichier qui passe
TOUTES les épreuves.  Concrètement :

   1. il ouvre le fichier de TP (par exemple `tp1_permutation.py`) ;
   2. il recopie le contenu des blocs « ✅ SOLUTION » à la place des squelettes
      « --- À COMPLÉTER --- » ;
   3. il lance les épreuves de la séance sur ce fichier reconstruit ;
   4. il remet le fichier de TP dans son état d'origine (rien n'est modifié).

Pourquoi cet outil ?  Parce qu'un squelette à trous n'est utile que si les trous
se comblent AVEC la solution imprimée : si l'on modifie une recette sans mettre
à jour la solution, les étudiants se retrouvent bloqués.  Ce script détecte ce
genre d'oubli en une seconde.

Usage (depuis la racine du dépôt) :

    python3 outils/verifier_solutions.py
==========================================================================
"""

from __future__ import annotations

import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEANCES = [
    ("seance1_permutation_substitution", "tp1_permutation.py", "test_tp1_permutation.py"),
    ("seance2_vigenere", "tp2_vigenere.py", "test_tp2_vigenere.py"),
    ("seance3_cryptanalyse", "tp3_vigenere_vic.py", "test_tp3_vigenere_vic.py"),
]

MARQUEUR_SQUELETTE = "# --- À COMPLÉTER"
MARQUEUR_SOLUTION = "✅ SOLUTION"


def _est_ligne_de_separation(ligne: str) -> bool:
    """Vrai pour les lignes du genre `# -------------` (les séparateurs)."""
    contenu = ligne.strip().lstrip("#").strip()
    return bool(contenu) and set(contenu) == {"-"}


def _code_de_la_solution(ligne: str) -> str:
    """Transforme une ligne de solution commentée en vraie ligne de code.

    `"    #     texte = texte.upper()"` devient `"    texte = texte.upper()"` :
    on enlève tout jusqu'au premier dièse, puis exactement un espace.
    """
    position = ligne.index("#")
    code = ligne[position + 1:]
    if code.startswith(" "):
        code = code[1:]
    return code.rstrip()


def reconstruire(chemin: str) -> str:
    """Renvoie le contenu du fichier où les squelettes sont remplacés par les
    solutions imprimées."""
    with open(chemin, encoding="utf-8") as fichier:
        lignes = fichier.read().splitlines()

    resultat = []
    index = 0
    while index < len(lignes):
        ligne = lignes[index]

        if not ligne.strip().startswith(MARQUEUR_SQUELETTE):
            resultat.append(ligne)
            index += 1
            continue

        # On garde la ligne « --- À COMPLÉTER --- » puis on cherche la solution.
        resultat.append(ligne)
        depart = index + 1

        fin_squelette = None
        debut_solution = None
        for position in range(depart, len(lignes)):
            if MARQUEUR_SOLUTION in lignes[position]:
                debut_solution = position
                break
        if debut_solution is None:
            raise ValueError(f"pas de bloc « ✅ SOLUTION » après la ligne {index + 1}")
        # La ligne juste avant l'en-tête de solution est un séparateur.
        fin_squelette = debut_solution - 1

        # Les lignes de code de la solution sont encadrées de deux séparateurs.
        position = debut_solution + 1
        if position >= len(lignes) or not _est_ligne_de_separation(lignes[position]):
            raise ValueError(f"en-tête de solution mal formé à la ligne {debut_solution + 1}")
        position += 1
        code = []
        while position < len(lignes) and not _est_ligne_de_separation(lignes[position]):
            code.append(_code_de_la_solution(lignes[position]))
            position += 1

        # On écrit le code, puis on reprend le fichier à la fin du bloc solution.
        resultat.extend(code)
        index = position + 1          # on saute le séparateur de fin

    return "\n".join(resultat) + "\n"


def main() -> int:
    tout_bon = True
    for dossier, fichier_tp, fichier_tests in SEANCES:
        chemin_tp = os.path.join(RACINE, dossier, fichier_tp)
        with open(chemin_tp, encoding="utf-8") as fichier:
            original = fichier.read()

        print(f"--- {fichier_tp} : reconstruction puis épreuves ---")
        try:
            reconstruit = reconstruire(chemin_tp)
        except Exception as erreur:  # noqa: BLE001
            print(f"  /!\\ reconstruction impossible : {erreur}")
            tout_bon = False
            continue

        # On écrit la version reconstruite, on teste, puis on restaure.
        with open(chemin_tp, "w", encoding="utf-8") as fichier:
            fichier.write(reconstruit)
        try:
            resultat = subprocess.run(
                [sys.executable, fichier_tests],
                cwd=os.path.join(RACINE, dossier),
                capture_output=True,
                text=True,
                env={cle: valeur for cle, valeur in os.environ.items() if cle != "TP_CORRIGE"},
            )
        finally:
            with open(chemin_tp, "w", encoding="utf-8") as fichier:
                fichier.write(original)

        bilan = [ligne.strip() for ligne in resultat.stdout.splitlines() if "Bilan" in ligne]
        print("  " + (bilan[0] if bilan else "aucun bilan (erreur de syntaxe ?)"))
        if "ÉCHEC" in resultat.stdout:
            tout_bon = False
            print("  /!\\ certaines épreuves échouent avec la solution imprimée :")
            for ligne in resultat.stdout.splitlines():
                if "ÉCHEC" in ligne:
                    print("     " + ligne.strip())

    print()
    if tout_bon:
        print("Tout est cohérent : recopier les solutions imprimées suffit à réussir le TP.")
    else:
        print("ATTENTION : au moins une séance pose problème (voir ci-dessus).")
    return 0 if tout_bon else 1


if __name__ == "__main__":
    sys.exit(main())
