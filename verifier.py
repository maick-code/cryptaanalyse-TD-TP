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
            if "Bilan" in ligne or ligne.strip().startswith("[ÉCHEC]"):
                print("   " + ligne.strip())
        bilans[numero] = "Bilan" in resultat.stdout and "0 épreuve" not in resultat.stdout

    print()
    print("=" * 72)
    if all(bilans.values()):
        print("  Chaque séance a au moins une épreuve réussie.")
    else:
        print("  Certaines séances ne sont pas commencées (aucune épreuve réussie).")
    print("  Détail complet : lancez le fichier test_tpX_*.py de la séance concernée.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
