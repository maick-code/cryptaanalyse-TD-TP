"""==========================================================================
 OUTIL DU PROFESSEUR — génère les données du TP de cryptanalyse linéaire
==========================================================================

Ce script fabrique le jeu de données du TP :

  1. il lit la clé maître dans `corriges/sources_lineaire.json` ;
  2. il chiffre 2 000 clairs tirés au hasard avec le mini-SPN ;
  3. il vérifie que l'attaque linéaire retrouve bien la clé, et que les
     quantités annoncées dans le TP sont exactes (biais, groupes, candidats) ;
  4. il écrit `donnees_lineaire.py` à la racine ;
  5. il écrit les empreintes SHA-256 dans la zone générée du fichier de tests.

Usage (depuis la racine du dépôt) :

    python3 outils/generer_donnees_lineaire.py              # génère
    python3 outils/generer_donnees_lineaire.py --verifier   # vérifie sans écrire
    python3 outils/generer_donnees_lineaire.py --calibrer   # cherche une clé

CALIBRAGE — À LIRE AVANT DE CHANGER LA CLÉ
------------------------------------------
Sur un bloc de 8 bits, le biais EXACT d'une trace dépend de la clé et peut
être exactement NUL.  Sur les 256 clés maîtres possibles, seules 13 remplissent
les conditions du TP :

  * biais exact >= 0,25 dans les DEUX orientations ;
  * le bon quartet est dans le groupe de tête (seuil 0,8) des deux côtés.

La clé retenue est M = 19 (K3 = 0xBA).  Ses biais exacts valent 0,25 et 0,875,
et ses groupes de tête sont [4, 7, 8, 11] et [10] : le quartet bas est unique,
le quartet haut est à égalité à quatre.  Cette égalité n'est pas un défaut du
programme, c'est une propriété de la relation linéaire (le score est une valeur
absolue, qui ne distingue pas p = 0,25 de p = 0,75) ; c'est la vérification sur
couples connus qui tranche.

Le mode `--calibrer` refait cette recherche et réécrit le JSON.
==========================================================================
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from outils.lineaire import (  # noqa: E402
    MASQUE_A,
    MASQUE_C,
    SEUILS,
    attaquer_cle,
    attaquer_quartet,
    biais_exact,
    chiffrer,
    cle_candidates,
    diversifier,
    groupe_de_tete,
    paires_pour_cle,
    verifier_cles,
)
from outils.verif import empreinte  # noqa: E402

DOSSIER_SEANCE = RACINE
CHEMIN_DONNEES = os.path.join(DOSSIER_SEANCE, "donnees_lineaire.py")
CHEMIN_TESTS = os.path.join(DOSSIER_SEANCE, "test_tp_cryptanalyse_lineaire.py")
CHEMIN_SOURCES = os.path.join(RACINE, "corriges", "sources_lineaire.json")

DEBUT = "# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_donnees_lineaire.py) ---"
FIN = "# --- FIN DE LA ZONE GÉNÉRÉE ---"

#: Conditions que doit remplir la clé pour que le TP soit confortable.
BIAIS_MINIMAL = 0.25


# ---------------------------------------------------------------------------
# 1. Sources
# ---------------------------------------------------------------------------

def charger_sources() -> dict:
    with open(CHEMIN_SOURCES, encoding="utf-8") as fichier:
        return json.load(fichier)


def ecrire_sources(sources: dict) -> None:
    with open(CHEMIN_SOURCES, "w", encoding="utf-8") as fichier:
        json.dump(sources, fichier, ensure_ascii=False, indent=2)
        fichier.write("\n")


# ---------------------------------------------------------------------------
# 2. Analyse du jeu de données
# ---------------------------------------------------------------------------

def analyser(cle_maitre: int, paires) -> dict:
    """Calcule les quantités que le TP annonce, et le résultat de l'attaque."""
    cles = diversifier(cle_maitre)
    k3 = cles[3]
    resultat = {"cle_maitre": cle_maitre, "cles": cles, "k3": k3}

    for nom, depart, cible, vrai in (
        ("trace_basse", False, "K3_haut", (k3 >> 4) & 0xF),
        ("trace_haute", True, "K3_bas", k3 & 0xF),
    ):
        scores = attaquer_quartet(paires, MASQUE_A, MASQUE_C, depart)
        groupe = groupe_de_tete(scores, SEUILS[0])
        compte = sum(
            1 for clair, chiffre in paires
            if _relation_vraie(clair, chiffre, depart, vrai)
        )
        resultat[nom] = {
            "cible": cible,
            "vrai": vrai,
            "p_exact": biais_exact(cles, depart_haut=depart, candidat=vrai),
            "p_mesure": compte / len(paires),
            "groupe": groupe,
            "taille": len(groupe),
            "dedans": vrai in groupe,
            "top": scores[:4],
        }

    candidats, groupe_haut, groupe_bas = cle_candidates(paires, SEUILS[0])
    resultat["candidats"] = candidats
    resultat["groupe_haut"] = groupe_haut
    resultat["groupe_bas"] = groupe_bas
    resultat["survivants"] = verifier_cles(candidats, paires, 3)
    resultat["cle_retrouvee"], resultat["statut"] = attaquer_cle(paires)
    return resultat


def _relation_vraie(clair: int, chiffre: int, depart_haut: bool, candidat: int) -> bool:
    """Réplique locale du test de relation (pour mesurer le biais sans détour)."""
    from outils.lineaire import parite_masque, sbox_inverse

    if depart_haut:
        quartet = (clair >> 4) & 0xF
        y = (chiffre & 0xF) ^ candidat
    else:
        quartet = clair & 0xF
        y = ((chiffre >> 4) & 0xF) ^ candidat
    return parite_masque(quartet, MASQUE_A) == parite_masque(sbox_inverse(y), MASQUE_C)


# ---------------------------------------------------------------------------
# 3. Calibrage
# ---------------------------------------------------------------------------

def calibrer(graine: int, nombre: int) -> int:
    """Cherche une clé remplissant les conditions du TP.

    On parcourt les 256 clés maîtres et on garde celles dont :
      * le biais exact atteint BIAIS_MINIMAL dans les deux orientations ;
      * le bon quartet est dans le groupe de tête des deux orientations ;
      * aucune clé de tour n'est triviale (0x00 ou 0xFF), pour la lisibilité.
    """
    admissibles = []
    for cle_maitre in range(256):
        cles = diversifier(cle_maitre)
        k3 = cles[3]
        if any(cle in (0x00, 0xFF) for cle in cles):
            continue
        paires = [(m, chiffrer(m, cles)) for m in range(256)]
        ok = True
        for depart, vrai in ((False, (k3 >> 4) & 0xF), (True, k3 & 0xF)):
            if biais_exact(cles, depart_haut=depart, candidat=vrai) - 0.5 < BIAIS_MINIMAL - 1e-9:
                ok = False
                break
            scores = attaquer_quartet(paires, MASQUE_A, MASQUE_C, depart)
            if vrai not in groupe_de_tete(scores, SEUILS[0]):
                ok = False
                break
        if ok:
            admissibles.append((cle_maitre, cles))

    if not admissibles:
        raise RuntimeError("aucune clé ne remplit les conditions du TP")

    # On préfère une clé dont les groupes sont petits, puis on vérifie
    # l'attaque réelle sur le tirage demandé.
    meilleures = []
    for cle_maitre, _ in admissibles:
        paires = paires_pour_cle(cle_maitre, nombre, graine)
        candidats, groupe_haut, groupe_bas = cle_candidates(paires, SEUILS[0])
        if attaquer_cle(paires)[0] == cle_maitre:
            meilleures.append((len(groupe_haut) + len(groupe_bas), cle_maitre))

    if not meilleures:
        return admissibles[0][0]
    meilleures.sort()
    return meilleures[0][1]


# ---------------------------------------------------------------------------
# 4. Écriture des fichiers
# ---------------------------------------------------------------------------

def litteral_chaine(texte: str, largeur: int = 64) -> str:
    lignes = []
    for debut in range(0, len(texte), largeur):
        lignes.append('    "' + texte[debut:debut + largeur] + '"')
    return "\n".join(lignes)


def texte_donnees(cle_maitre: int, graine: int, nombre: int, paires) -> str:
    clairs = "".join(f"{clair:02x}" for clair, _ in paires)
    chiffres = "".join(f"{chiffre:02x}" for _, chiffre in paires)
    return f'''"""==========================================================================
 DONNÉES DU TP — {nombre} couples clair-chiffré du mini-SPN
==========================================================================

Fichier GÉNÉRÉ par `outils/generer_donnees_lineaire.py`.  Ne le modifie pas à
la main : relance le générateur si tu veux d'autres données.

Chaque couple est un clair (0..255) et le chiffré correspondant, obtenus avec
la MÊME clé maître, que tu ne connais pas : c'est l'objet de l'attaque.

Les couples sont rangés dans deux chaînes hexadécimales, pour que le fichier
reste lisible.  `PAIRES` reconstruit la liste de tuples.

    >>> from donnees_lineaire import PAIRES
    >>> len(PAIRES)
    {nombre}
    >>> PAIRES[0]
    ({paires[0][0]}, {paires[0][1]})

Remarque : un bloc ne fait que 8 bits, donc il n'existe que 256 clairs
possibles.  Sur {nombre} couples, les clairs se répètent forcément.  C'est
normal : dans une attaque à clair connu, on utilise tous les couples dont on
dispose.
==========================================================================
"""

{DEBUT}
GRAINE = {graine}
NOMBRE_PAIRES = {nombre}

CLAIRS_HEX = (
{litteral_chaine(clairs)}
)

CHIFFRES_HEX = (
{litteral_chaine(chiffres)}
)
{FIN}


def paires():
    """Reconstruit la liste des couples (clair, chiffré)."""
    return [
        (int(CLAIRS_HEX[i:i + 2], 16), int(CHIFFRES_HEX[i:i + 2], 16))
        for i in range(0, 2 * NOMBRE_PAIRES, 2)
    ]


PAIRES = paires()
'''


def texte_empreintes(resultat: dict, paires) -> str:
    """Empreintes des réponses, pour que le fichier de tests ne les révèle pas."""
    clairs = "".join(f"{clair:02x}" for clair, _ in paires)
    chiffres = "".join(f"{chiffre:02x}" for _, chiffre in paires)
    return "\n".join([
        DEBUT,
        "EMPREINTES = {",
        f'    "cle_maitre": "{empreinte(resultat["cle_maitre"])}",',
        f'    "groupe_haut": "{empreinte(str(resultat["groupe_haut"]))}",',
        f'    "groupe_bas": "{empreinte(str(resultat["groupe_bas"]))}",',
        f'    "candidats": "{empreinte(str(resultat["candidats"]))}",',
        f'    "donnees": "{empreinte(clairs + chiffres)}",',
        "}",
        FIN,
    ])


def remplacer_zone(chemin: str, contenu: str) -> None:
    with open(chemin, encoding="utf-8") as fichier:
        lignes = fichier.read().splitlines()

    debut = fin = None
    for index, ligne in enumerate(lignes):
        if ligne.strip() == DEBUT:
            debut = index
        elif ligne.strip() == FIN:
            fin = index
            break
    if debut is None or fin is None:
        raise ValueError(f"marqueurs de zone introuvables dans {chemin}")

    nouvelles = lignes[:debut] + contenu.splitlines() + lignes[fin + 1:]
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write("\n".join(nouvelles) + "\n")


# ---------------------------------------------------------------------------
# 5. Vérification des données déjà écrites
# ---------------------------------------------------------------------------

def charger_donnees():
    spec = importlib.util.spec_from_file_location("donnees_lineaire_verif", CHEMIN_DONNEES)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verifier_donnees(cle_maitre: int, nombre: int, graine: int) -> bool:
    if not os.path.exists(CHEMIN_DONNEES):
        print("  /!\\ aucune donnée écrite : lance d'abord la génération.")
        return False
    module = charger_donnees()
    paires = module.PAIRES
    coherent = True

    print("  données relues : %d couples" % len(paires))
    if len(paires) != nombre:
        print("  /!\\ NOMBRE_PAIRES attendu %d, trouvé %d" % (nombre, len(paires)))
        coherent = False
    attendues = paires_pour_cle(cle_maitre, nombre, graine)
    if paires != attendues:
        print("  /!\\ les couples ne correspondent pas au tirage (graine, clé)")
        coherent = False
    else:
        print("  tirage conforme (graine %d, clé %d)" % (graine, cle_maitre))

    resultat = analyser(cle_maitre, paires)
    print("  biais mesurés  : trace basse %.4f, trace haute %.4f"
          % (resultat["trace_basse"]["p_mesure"], resultat["trace_haute"]["p_mesure"]))
    print("  groupes        : haut %s, bas %s"
          % (resultat["groupe_haut"], resultat["groupe_bas"]))
    print("  candidats      : %s" % (resultat["candidats"],))
    print("  survivants     : %s" % (resultat["survivants"],))
    print("  attaque        : clé = %s, statut = %s"
          % (resultat["cle_retrouvee"], resultat["statut"]))
    if resultat["cle_retrouvee"] != cle_maitre or resultat["statut"] != "certaine":
        coherent = False
    return coherent


# ---------------------------------------------------------------------------
# 6. Programme principal
# ---------------------------------------------------------------------------

def main() -> int:
    os.makedirs(DOSSIER_SEANCE, exist_ok=True)
    analyseur = argparse.ArgumentParser(description="Génère les données du TP de cryptanalyse linéaire.")
    analyseur.add_argument("--verifier", action="store_true",
                           help="vérifie les données existantes, sans écrire")
    analyseur.add_argument("--calibrer", action="store_true",
                           help="cherche une clé remplissant les conditions")
    analyseur.add_argument("--graine", type=int, default=None)
    analyseur.add_argument("--nombre", type=int, default=None)
    arguments = analyseur.parse_args()

    sources = charger_sources()
    graine = arguments.graine if arguments.graine is not None else sources["graine"]
    nombre = arguments.nombre if arguments.nombre is not None else sources["nombre_paires"]

    print("=" * 72)
    print("  DONNÉES DU TP — CRYPTANALYSE LINÉAIRE")
    print("=" * 72)

    if arguments.calibrer:
        print("\nCalibrage : recherche d'une clé parmi les 256 possibles...")
        cle_maitre = calibrer(graine, nombre)
        sources.update({"cle_maitre": cle_maitre, "graine": graine, "nombre_paires": nombre})
        ecrire_sources(sources)
        print("  clé retenue : %d (0x%02X)" % (cle_maitre, cle_maitre))
    else:
        cle_maitre = sources["cle_maitre"]

    cles = diversifier(cle_maitre)
    print("\nClé maître (professeur) : %d (0x%02X)" % (cle_maitre, cle_maitre))
    print("Clés de tour            : " + ", ".join("0x%02X" % cle for cle in cles))
    print("K3 (dernier tour)       : 0x%02X  (haut 0x%X, bas 0x%X)"
          % (cles[3], (cles[3] >> 4) & 0xF, cles[3] & 0xF))

    paires = paires_pour_cle(cle_maitre, nombre, graine)
    resultat = analyser(cle_maitre, paires)

    print("\nBiais EXACT (énumération des 256 blocs) :")
    for nom, libelle in (("trace_basse", "trace basse (départ bas) "),
                         ("trace_haute", "trace haute (départ haut)")):
        info = resultat[nom]
        print("  %s -> %-7s : p_exact = %.4f, delta = %+.4f, rho = %+.4f"
              % (libelle, info["cible"], info["p_exact"],
                 info["p_exact"] - 0.5, 2 * info["p_exact"] - 1))
    print("  piling-up (prédiction) : p = %.4f  (indépendant de la clé)"
          % (0.5 + 0.5 * (-2 / 8.0) * (4 / 8.0)))

    print("\nBiais MESURÉ sur %d couples :" % nombre)
    for nom, libelle in (("trace_basse", "trace basse"), ("trace_haute", "trace haute")):
        info = resultat[nom]
        print("  %s -> %-7s : p = %.4f  (groupe %s, taille %d)"
              % (libelle, info["cible"], info["p_mesure"], info["groupe"], info["taille"]))

    print("\nAttaque :")
    print("  groupes        : haut %s, bas %s"
          % (resultat["groupe_haut"], resultat["groupe_bas"]))
    print("  candidats      : %s" % (resultat["candidats"],))
    print("  après 3 paires : %s" % (resultat["survivants"],))
    print("  résultat       : clé = %s, statut = %s"
          % (resultat["cle_retrouvee"], resultat["statut"]))

    if resultat["cle_retrouvee"] != cle_maitre or resultat["statut"] != "certaine":
        print("\n/!\\ L'attaque ne retrouve pas la clé : rien n'est écrit.")
        return 1

    if arguments.verifier:
        print("\nMode --verifier : aucune écriture.")
        return 0 if verifier_donnees(cle_maitre, nombre, graine) else 1

    with open(CHEMIN_DONNEES, "w", encoding="utf-8") as fichier:
        fichier.write(texte_donnees(cle_maitre, graine, nombre, paires))
    print("\nDonnées écrites   : %s" % os.path.relpath(CHEMIN_DONNEES, RACINE))

    empreintes = texte_empreintes(resultat, paires)
    if os.path.exists(CHEMIN_TESTS):
        remplacer_zone(CHEMIN_TESTS, empreintes)
        print("Empreintes écrites : %s" % os.path.relpath(CHEMIN_TESTS, RACINE))
    else:
        print("Empreintes        : (fichier de tests absent, non écrites)")
        print(empreintes)

    return 0


if __name__ == "__main__":
    sys.exit(main())
