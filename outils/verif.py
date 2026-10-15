"""Mini-harnais de tests, uniquement avec la bibliothèque standard Python.

Pourquoi ce fichier ?
---------------------
Les machines de TP n'ont pas forcément `pytest` d'installé, et il n'y a pas
toujours d'accès Internet pour l'installer.  Ce module fournit donc :

  * `epreuve(...)` : un décorateur qui donne un numéro et un titre à un test ;
  * `lancer()`    : un lanceur qui affiche un bilan lisible en français ;
  * `charger_module(...)` : pour que les mêmes tests valident le fichier de
    l'étudiant (`tp1_permutation.py`) ou le corrigé (`corrige_tp1_permutation.py`).

Les tests sont des fonctions Python ordinaires dont le nom commence par
`test_`.  Si `pytest` est installé, il peut aussi les exécuter
(`python3 -m pytest`), sans rien changer : le décorateur ne modifie pas la
fonction.

Exemple d'utilisation dans un fichier de tests
---------------------------------------------
    from outils.verif import charger_module, epreuve, lancer

    tp = charger_module("tp1_permutation")

    @epreuve("1.1", "nettoyer_simple()")
    def test_nettoyer_simple():
        assert tp.nettoyer_simple("Bonjour, le monde !") == "BONJOURLEMONDE"

    if __name__ == "__main__":
        lancer()
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
import traceback

__all__ = ["charger_module", "empreinte", "epreuve", "lancer", "RACINE"]


def empreinte(valeur) -> str:
    """Empreinte SHA-256 d'une valeur (nombre ou texte).

    Les fichiers d'épreuves rangent les réponses du professeur sous cette forme
    plutôt qu'en clair : les tests peuvent ainsi vérifier une réponse sans
    l'écrire noir sur blanc dans un fichier que les étudiants ont sous les yeux.
    """
    return hashlib.sha256(str(valeur).encode("utf-8")).hexdigest()

#: Racine du dépôt (le dossier qui contient `outils/`, `seance1_.../`, etc.).
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (numero, titre, fonction) dans l'ordre d'apparition dans le fichier de tests.
_EPREUVES: list[tuple[str, str, object]] = []


def epreuve(numero: str, titre: str):
    """Décorateur : associe un numéro et un titre à une fonction de test."""

    def decorateur(fonction):
        _EPREUVES.append((numero, titre, fonction))
        return fonction

    return decorateur


def charger_module(nom: str, dossier: str | None = None):
    """Charge le fichier `nom + ".py"` du dossier `dossier` (par défaut celui du
    script de tests en cours).

    Si la variable d'environnement ``TP_CORRIGE=1`` est définie, on charge à la
    place la version corrigée ``corriges/corrige_<nom>.py``.  C'est ce qui
    permet au professeur de tester le corrigé avec exactement les mêmes
    épreuves que les étudiants :

        python3 test_tp1_permutation.py                # version étudiant
        TP_CORRIGE=1 python3 test_tp1_permutation.py   # version corrigée
    """
    if os.environ.get("TP_CORRIGE") == "1":
        chemin = os.path.join(RACINE, "corriges", "corrige_" + nom + ".py")
    else:
        dossier = dossier or os.path.dirname(os.path.abspath(sys.argv[0]))
        chemin = os.path.join(dossier, nom + ".py")

    chemin = os.path.abspath(chemin)
    if not os.path.exists(chemin):
        raise FileNotFoundError(
            chemin + "\n(le fichier de TP est introuvable : êtes-vous bien dans son dossier ?)"
        )

    # Permet aux fichiers de TP d'écrire « from outils.texte_francais import ... »
    # quel que soit le dossier depuis lequel on lance la commande.
    for dossier_utile in (os.path.dirname(os.path.abspath(sys.argv[0])), RACINE):
        if dossier_utile not in sys.path:
            sys.path.insert(0, dossier_utile)

    nom_module = "tp_en_cours_" + os.path.basename(chemin)[:-3]
    spec = importlib.util.spec_from_file_location(nom_module, chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom_module] = module
    try:
        spec.loader.exec_module(module)
    except Exception:  # erreur de syntaxe, import impossible, division par zéro...
        print()
        print("=" * 72)
        print("Impossible de lire votre fichier :", os.path.relpath(chemin, RACINE))
        print("=" * 72)
        traceback.print_exc()
        print()
        print("Corrigez d'abord cette erreur, puis relancez les tests.")
        sys.exit(2)
    return module


def lancer() -> int:
    """Exécute toutes les épreuves enregistrées et affiche un bilan."""
    reussies = 0
    resultats = []

    print()
    print("=" * 72)
    print("  VÉRIFICATION DU TRAVAIL")
    print("=" * 72)

    for numero, titre, fonction in _EPREUVES:
        try:
            fonction()
        except AssertionError as erreur:
            message = str(erreur) or "la valeur obtenue ne correspond pas à la valeur attendue"
            resultats.append((numero, titre, False, "assertion fausse : " + message))
        except NotImplementedError as erreur:
            message = str(erreur) or "fonction pas encore écrite"
            resultats.append((numero, titre, False, "TODO non fait : " + message))
        except Exception as erreur:  # noqa: BLE001 - on veut tout attraper pour l'étudiant
            detail = traceback.format_exception_only(type(erreur), erreur)[-1].strip()
            resultats.append((numero, titre, False, "erreur Python : " + detail))
        else:
            reussies += 1
            resultats.append((numero, titre, True, ""))

    for numero, titre, ok, detail in resultats:
        marque = "OK " if ok else "ÉCHEC"
        print(f"  [{marque}] {numero} {titre}")
        if detail:
            for ligne in _decouper(detail):
                print("          " + ligne)

    total = len(resultats)
    print("-" * 72)
    print(f"  Bilan : {reussies}/{total} épreuves réussies")
    if reussies == total:
        print("  Bravo, tout est bon !")
    else:
        print("  Reprenez les épreuves marquées ÉCHEC, puis relancez ce fichier.")
    print("=" * 72)
    print()
    return 0 if reussies == total else 1


def _decouper(texte: str, largeur: int = 100):
    """Découpe un long message en lignes lisibles."""
    mots = texte.split()
    ligne = ""
    for mot in mots:
        if len(ligne) + len(mot) + 1 > largeur:
            yield ligne
            ligne = mot
        else:
            ligne = (ligne + " " + mot).strip()
    if ligne:
        yield ligne


if __name__ == "__main__":
    print(__doc__)
