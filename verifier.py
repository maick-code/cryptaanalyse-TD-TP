"""==========================================================================
 LANCEUR GLOBAL — exécute les épreuves des trois séances
==========================================================================

    python3 verifier.py                  # vérifie les fichiers des étudiants
    TP_CORRIGE=1 python3 verifier.py     # vérifie les corrigés du professeur

On peut aussi ne vérifier qu'une séance :

    python3 verifier.py 1
    python3 verifier.py 2
    python3 verifier.py 3
==========================================================================
"""

import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.abspath(__file__))

SEANCES = {
    "1": ("seance1_permutation_substitution", "test_tp1_permutation.py",
          "TP 1 — généralités, permutation (scytale), substitution (César)"),
    "2": ("seance2_vigenere", "test_tp2_vigenere.py",
          "TP 2 — codes polyalphabétiques (Vigenère) et son attaque"),
    "3": ("seance3_cryptanalyse", "test_tp3_vigenere_vic.py",
          "TP 3 — cryptanalyse de Vigenère (Kasiski, Friedman) et VIC"),
}


def main() -> int:
    demandees = [a for a in sys.argv[1:] if a in SEANCES] or list(SEANCES)
    mode = "corrigés" if os.environ.get("TP_CORRIGE") == "1" else "fichiers des étudiants"

    print("=" * 72)
    print(f"  VÉRIFICATION GLOBALE ({mode})")
    print("=" * 72)

    bilans = {}
    for numero in demandees:
        dossier, fichier, titre = SEANCES[numero]
        print()
        print(f"### {titre}")
        resultat = subprocess.run(
            [sys.executable, fichier],
            cwd=os.path.join(RACINE, dossier),
            capture_output=True,
            text=True,
        )
        for ligne in resultat.stdout.splitlines():
            if ligne.strip().startswith("[ÉCHEC]"):
                print("   " + ligne.strip())
        bilans[numero] = lire_bilan(resultat.stdout)
        reussies, total = bilans[numero]
        if total == 0:
            print("   (les épreuves n'ont pas pu être lancées : erreur de syntaxe ?)")
        else:
            print(f"   Bilan de la séance : {reussies}/{total} épreuves réussies")

    print()
    print("=" * 72)
    total_reussies = sum(reussies for reussies, _ in bilans.values())
    total_epreuves = sum(total for _, total in bilans.values())
    print(f"  ENSEMBLE : {total_reussies}/{total_epreuves} épreuves réussies")
    if total_epreuves and total_reussies == total_epreuves:
        print("  Bravo, les trois séances sont terminées !")
    else:
        for numero in demandees:
            reussies, total = bilans[numero]
            if reussies < total:
                print(f"  séance {numero} : encore {total - reussies} épreuve(s) à réussir  "
                      f"-> cd {SEANCES[numero][0]} && python3 {SEANCES[numero][1]}")
    print("=" * 72)
    return 0


def lire_bilan(sortie: str):
    """Retrouve « Bilan : 5/11 épreuves réussies » dans la sortie des épreuves."""
    for ligne in sortie.splitlines():
        if "Bilan :" in ligne:
            nombres = ligne.split("Bilan :")[1].split("épreuve")[0].strip()
            if "/" in nombres:
                reussies, total = nombres.split("/")
                try:
                    return int(reussies.strip()), int(total.strip())
                except ValueError:
                    return 0, 0
    return 0, 0


if __name__ == "__main__":
    sys.exit(main())
