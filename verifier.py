"""==========================================================================
 LANCEUR — exécute les épreuves du TP de cryptanalyse linéaire
==========================================================================

    python3 verifier.py                  # vérifie le fichier des étudiants
    TP_CORRIGE=1 python3 verifier.py     # vérifie le corrigé du professeur

C'est un simple raccourci : le fichier d'épreuves peut aussi être lancé
directement depuis la racine du dépôt :

    python3 test_tp_cryptanalyse_lineaire.py
==========================================================================
"""

import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.abspath(__file__))
FICHIER_TESTS = "test_tp_cryptanalyse_lineaire.py"


def main() -> int:
    mode = "corrigé" if os.environ.get("TP_CORRIGE") == "1" else "fichier de l'étudiant"

    print("=" * 72)
    print(f"  VÉRIFICATION — CRYPTANALYSE LINÉAIRE ({mode})")
    print("=" * 72)

    resultat = subprocess.run(
        [sys.executable, FICHIER_TESTS],
        cwd=RACINE,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(resultat.stdout)
    if resultat.stderr:
        sys.stderr.write(resultat.stderr)
    return resultat.returncode


if __name__ == "__main__":
    sys.exit(main())
