"""=========================================================================
 CORRIGÉ — CRYPTANALYSE LINÉAIRE
=========================================================================
Version corrigée du fichier des étudiants ; mêmes noms, mêmes épreuves :

    TP_CORRIGE=1 python3 test_tp_cryptanalyse_lineaire.py

PARTIE B — la boîte S et sa LAT :
    parite_masque, appliquer_sbox, sbox_inverse, table_approximations
PARTIE C — le mini-chiffre :
    permuter, chiffrer, dechiffrer (bonus)
PARTIE D — ★ l'attaque linéaire ★ :
    compter_relation, attaquer_quartet, groupe_de_tete,
    cle_candidates, verifier_cles, attaquer_cle

Les mesures statistiques et l'affichage sont fournis par `outils/lineaire.py`.
Rappel des trois biais :
    exact    : p = 0,25 (trace basse) et 0,875 (trace haute), pour M = 19 ;
    piling-up: p = 0,4375 (estimation) ;
    mesuré   : p ≈ 0,258 et 0,873 sur les 2 000 couples.
=========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = RACINE
for chemin in (DOSSIER, RACINE):
    if chemin not in sys.path:
        sys.path.insert(0, chemin)

from outils.lineaire import (  # noqa: E402
    SEUILS,
    SBOX,
    diversifier,
    groupe_de_tete as _groupe_de_tete_reference,
)


# ---------------------------------------------------------------------------
# § B — la boîte S et sa LAT
# ---------------------------------------------------------------------------

def parite_masque(valeur, masque):
    """Parité (0 ou 1) des bits de `valeur` sélectionnés par `masque`."""
    return bin(valeur & masque).count("1") % 2


def appliquer_sbox(x):
    """Applique la boîte S aux deux quartets du bloc `x`."""
    fort = SBOX[(x >> 4) & 0xF]
    faible = SBOX[x & 0xF]
    return (fort << 4) | faible


def sbox_inverse(y):
    """Antécédent du quartet `y` par la boîte S."""
    return SBOX.index(y & 0xF)


def table_approximations():
    """LAT 16 × 16 : LAT[a][b] = #solutions - 8."""
    lat = []
    for a in range(16):
        ligne = []
        for b in range(16):
            compte = sum(
                1 for x in range(16)
                if parite_masque(x, a) == parite_masque(SBOX[x], b)
            )
            ligne.append(compte - 8)
        lat.append(ligne)
    return lat


# ---------------------------------------------------------------------------
# § C — le mini-chiffre
# ---------------------------------------------------------------------------

def permuter(x):
    """Échange les deux quartets (couche linéaire P)."""
    return ((x & 0xF) << 4) | ((x >> 4) & 0xF)


def chiffrer(bloc, cles):
    """Chiffre un bloc de 8 bits avec (K0, K1, K2, K3)."""
    x = bloc ^ cles[0]
    for tour in range(1, len(cles)):
        x = permuter(appliquer_sbox(x)) ^ cles[tour]
    return x & 0xFF


def dechiffrer(bloc, cles):
    """Déchiffre un bloc de 8 bits (bonus)."""
    x = bloc & 0xFF
    for tour in range(len(cles) - 1, 0, -1):
        x = permuter(x ^ cles[tour])
        x = (sbox_inverse((x >> 4) & 0xF) << 4) | sbox_inverse(x & 0xF)
    return (x ^ cles[0]) & 0xFF


# ---------------------------------------------------------------------------
# § D — ★ l'attaque linéaire ★
# ---------------------------------------------------------------------------

def compter_relation(paires, masque_entree, masque_sortie, depart_haut, candidat):
    """Compte les couples qui satisfont la relation de trace.

    `depart_haut = False` : trace basse, candidat pour K3_HAUT, quartet haut
    du chiffré.  `depart_haut = True` : trace haute, candidat pour K3_BAS,
    quartet bas du chiffré.
    """
    total = 0
    for clair, chiffre in paires:
        if depart_haut:
            quartet_clair = (clair >> 4) & 0xF
            y = (chiffre & 0xF) ^ candidat
        else:
            quartet_clair = clair & 0xF
            y = ((chiffre >> 4) & 0xF) ^ candidat
        entree_sbox = sbox_inverse(y)
        if parite_masque(quartet_clair, masque_entree) == parite_masque(entree_sbox, masque_sortie):
            total += 1
    return total


def attaquer_quartet(paires, masque_entree, masque_sortie, depart_haut):
    """Classe les 16 candidats d'un quartet de K3 par |2 × compte − N|."""
    n = len(paires)
    scores = []
    for candidat in range(16):
        compte = compter_relation(paires, masque_entree, masque_sortie, depart_haut, candidat)
        scores.append((abs(2 * compte - n), candidat))
    scores.sort(reverse=True)
    return scores


def groupe_de_tete(scores, proportion=0.8):
    """Candidats dont le score atteint `proportion` fois le meilleur."""
    if not scores:
        return []
    meilleur = scores[0][0]
    if meilleur == 0:
        return sorted(candidat for _, candidat in scores)
    return sorted(
        candidat for score, candidat in scores
        if score >= proportion * meilleur
    )


def cle_candidates(paires, proportion=0.8):
    """Clés maîtres compatibles avec les groupes de tête des deux traces."""
    scores_haut = attaquer_quartet(paires, 9, 13, False)
    scores_bas = attaquer_quartet(paires, 9, 13, True)
    groupe_haut = groupe_de_tete(scores_haut, proportion)
    groupe_bas = groupe_de_tete(scores_bas, proportion)

    candidats = []
    for cle_maitre in range(256):
        k3 = diversifier(cle_maitre)[3]
        if ((k3 >> 4) & 0xF) in groupe_haut and (k3 & 0xF) in groupe_bas:
            candidats.append(cle_maitre)
    return candidats, groupe_haut, groupe_bas


def verifier_cles(candidats, paires, nombre=3):
    """Ne garde que les clés qui rechiffrent correctement les premiers couples."""
    survivantes = []
    temoins = paires[:nombre]
    for cle_maitre in candidats:
        cles = diversifier(cle_maitre)
        if all(chiffrer(clair, cles) == chiffre for clair, chiffre in temoins):
            survivantes.append(cle_maitre)
    return survivantes


def attaquer_cle(paires, nombre_verifications=3, seuils=SEUILS):
    """Attaque complète, avec élargissement progressif et statut explicite.

    Aucune recherche exhaustive de secours : si les groupes élargis ne
    laissent pas une clé unique, on renvoie None avec « incertaine » ou
    « echec ».
    """
    derniers = []
    for indice, seuil in enumerate(seuils):
        candidats, _, _ = cle_candidates(paires, seuil)
        survivantes = verifier_cles(candidats, paires, nombre_verifications)
        derniers = survivantes
        if len(survivantes) == 1:
            statut = "certaine" if indice == 0 else "elargie"
            return survivantes[0], statut
    if len(derniers) > 1:
        return None, "incertaine"
    return None, "echec"
