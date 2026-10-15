"""=========================================================================
 CORRIGÉ DU TP 1 — généralités, permutation (scytale), substitution (César)
==========================================================================
Ce fichier est la version corrigée du fichier des étudiants, et il définit
EXACTEMENT les mêmes noms : les épreuves tournent à l'identique :

    cd seance1_permutation_substitution
    TP_CORRIGE=1 python3 test_tp1_permutation.py

Il sert aussi de référence à `outils/generer_messages.py`, qui vérifie que
chaque message intercepté peut effectivement être cassé.

PARTIE B — code à écrire par les étudiants :
    compter_lettres, cesar_chiffrer, cesar_dechiffrer
PARTIE C — CRYPTANALYSE (le cœur du TP) :
    attaque_scytale, forcer_cesar, identifier_et_dechiffrer
==========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.reference import (  # noqa: E402
    ALPHABET,
    cle_scytale_possibles,      # outil fourni
    comptage,                   # outil fourni
    scytale_dechiffrer,         # outil fourni
    vider_les_espaces,          # outil fourni
)
from outils.texte_francais import distance_au_francais, vraisemblance  # noqa: E402


# ==========================================================================
# PARTIE B — le code à écrire
# ==========================================================================

def compter_lettres(texte):
    """Solution B.1 — on initialise les 26 compteurs avant de compter."""
    comptes = {}
    for lettre in ALPHABET:
        comptes[lettre] = 0
    for caractere in texte.upper():
        if "A" <= caractere <= "Z":
            comptes[caractere] += 1
    return comptes


def cesar_chiffrer(texte, cle):
    """Solution B.2 — le décalage se fait modulo 26 : après Z on revient à A."""
    chiffre = ""
    for caractere in texte.upper():
        if "A" <= caractere <= "Z":
            chiffre += ALPHABET[(ALPHABET.index(caractere) + cle) % 26]
        else:
            chiffre += caractere
    return chiffre


def cesar_dechiffrer(texte_chiffre, cle):
    """Solution B.3 — déchiffrer, c'est décaler de l'opposé : (-cle) % 26."""
    return cesar_chiffrer(texte_chiffre, (-cle) % 26)


# ==========================================================================
# PARTIE C — CRYPTANALYSE
# ==========================================================================

def attaque_scytale(chiffre):
    """Solution C.1 — recherche exhaustive sur les clefs possibles.

    La scytale ne change aucune lettre : tous les candidats ont donc les mêmes
    fréquences.  Ce qui les distingue est l'ORDRE des lettres : c'est la
    vraisemblance (fréquence des paires de lettres) qui tranche.
    """
    meilleure_cle = 0
    meilleur_texte = ""
    meilleur_score = None
    for t in cle_scytale_possibles(len(chiffre)):
        candidat = scytale_dechiffrer(chiffre, t)
        score = vraisemblance(candidat)
        if meilleur_score is None or score > meilleur_score:
            meilleure_cle = t
            meilleur_texte = candidat
            meilleur_score = score
    return meilleure_cle, meilleur_texte


def forcer_cesar(texte_chiffre):
    """Solution C.2 — les 26 décalages, celui dont les fréquences collent le
    mieux à celles du français est le bon."""
    meilleure_cle = 0
    meilleur_texte = ""
    meilleure_distance = None
    for cle in range(26):
        candidat = cesar_dechiffrer(texte_chiffre, cle)
        distance = distance_au_francais(candidat)
        if meilleure_distance is None or distance < meilleure_distance:
            meilleure_cle = cle
            meilleur_texte = candidat
            meilleure_distance = distance
    return meilleure_cle, meilleur_texte


def identifier_et_dechiffrer(message):
    """Solution C.5 — reconnaissance du chiffrement, puis attaque.

    On essaie les DEUX méthodes d'attaque et l'on garde le candidat qui
    ressemble le plus à du français.  Avantage de cette méthode : elle ne
    suppose rien sur le chiffrement utilisé.
    """
    lettres = vider_les_espaces(message)
    cle_scytale, texte_scytale = attaque_scytale(lettres)
    cle_cesar, texte_cesar = forcer_cesar(lettres)
    if vraisemblance(texte_scytale) > vraisemblance(texte_cesar):
        return "SCYTALE", cle_scytale, texte_scytale
    return "CESAR", cle_cesar, texte_cesar


# ==========================================================================
# MESSAGES INTERCEPTÉS (remplis par outils/generer_messages.py)
# ==========================================================================

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
MESSAGE_SCYTALE = (
    "LNEDIPEERASSEXRULERETMHEXAXECFAESPRXURIIUDOIXNEXNRUNVXITEAEVTI"
    "XOEEDSIDEX"
)

MESSAGE_CESAR = (
    "CV TFEMFZ GRIK UVDRZE DRKZE R C'RLSV VK RIIZMV R CR WIFEKZVIV "
    "RMREK DZUZ"
)

MESSAGE_MYSTERE_1 = (
    "LSETETTILREAPRNRANEICRAAUEUACEORRIIPMVORLILNTAAEUXIVEDERTCRX"
)

MESSAGE_MYSTERE_2 = (
    "WPMLETXPYEPDECPDEPQPCXPEZFEWSTGPCPEWPDECLGLFIZYECPACTDLFACTYEP"
    "XAD"
)

MESSAGE_MYSTERE_3 = (
    "LSADNOUIUEEEEATDTRJNIHERMGTELTADSENEEEEVAEREUUTXSRNAPDDPNRIX"
)
# --- FIN DE LA ZONE GÉNÉRÉE ---
