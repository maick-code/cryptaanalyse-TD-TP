"""=========================================================================
 CORRIGÉ DU TP 1 — généralités et codes simples (chapitres 1 et 2)
==========================================================================
Ce fichier est la solution complète du TP 1.  Il se teste exactement comme le
fichier des étudiants :

    cd seance1_permutation_substitution
    TP_CORRIGE=1 python3 test_tp1_permutation.py

Voir le guide de l'enseignant (`ENSEIGNANT.md`) pour les commentaires
pédagogiques et les erreurs les plus fréquentes des étudiants.
==========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.reference import (  # noqa: E402
    ALPHABET,
    comptage,
    nettoyer,
    scytale_chiffrer,
    scytale_dechiffrer,
)
from outils.texte_francais import distance_au_francais, vraisemblance  # noqa: E402


# ==========================================================================
# PARTIE A
# ==========================================================================

def nettoyer_simple(texte):
    """Solution A.1."""
    resultat = ""
    for caractere in texte.upper():
        if "A" <= caractere <= "Z":
            resultat += caractere
    return resultat


def compter_lettres(texte):
    """Solution A.2."""
    comptes = {}
    for lettre in ALPHABET:
        comptes[lettre] = 0
    for caractere in texte.upper():
        if "A" <= caractere <= "Z":
            comptes[caractere] += 1
    return comptes


# ==========================================================================
# PARTIE B
# ==========================================================================

def cle_scytale_possibles(longueur):
    """Solution B.1."""
    liste = []
    for t in range(2, longueur + 1):
        if longueur % t == 0 and longueur // t >= 5:
            liste.append(t)
    return liste


def decouper_en_morceaux(texte, taille):
    """Solution B.2."""
    morceaux = []
    for debut in range(0, len(texte), taille):
        morceaux.append(texte[debut:debut + taille])
    return morceaux


def attaque_scytale(chiffre):
    """Solution B.3 — on essaie chaque clef raisonnable et l'on garde le
    candidat qui ressemble le plus à du français, au sens de `vraisemblance`
    (score des paires de lettres consécutives).

    Remarque importante pour la correction : comparer les *fréquences des
    lettres* ne peut pas marcher ici, puisque la scytale ne change aucune
    lettre : tous les candidats ont exactement les mêmes comptes de lettres.
    Seul l'ORDRE des lettres change, et c'est ce que l'on exploite.  Compter
    les petits mots « DE », « LE »... fonctionne aussi, mais moins bien : un
    texte court en contient peu, et du charabia peut en contenir par hasard.
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

    return (meilleure_cle, meilleur_texte)


# ==========================================================================
# PARTIE C
# ==========================================================================

def cesar_chiffrer(texte, cle):
    """Solution C.1."""
    chiffre = ""
    for caractere in texte.upper():
        if "A" <= caractere <= "Z":
            rang = (ALPHABET.index(caractere) + cle) % 26
            chiffre += ALPHABET[rang]
        else:
            chiffre += caractere
    return chiffre


def cesar_dechiffrer(texte_chiffre, cle):
    """Solution C.2 — le déchiffrement, c'est le chiffrement avec -cle."""
    return cesar_chiffrer(texte_chiffre, (-cle) % 26)


def forcer_cesar(texte_chiffre):
    """Solution C.3 — on essaie les 26 clefs et l'on garde la plus petite
    distance aux fréquences du français."""
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

    return (meilleure_cle, meilleur_texte)


# ==========================================================================
# PARTIE D
# ==========================================================================

def message_compromis(message_clair, texte_chiffre_saisi):
    """Solution D.1."""
    return nettoyer(message_clair) in nettoyer(texte_chiffre_saisi)


# ==========================================================================
# PARTIE E — constantes des messages à décrypter
# (remplies automatiquement par outils/generer_messages.py)
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
# --- FIN DE LA ZONE GÉNÉRÉE ---


if __name__ == "__main__":
    # Vérification rapide des solutions, à la main.
    print("A.1", nettoyer_simple("Bonjour, le monde !"))
    print("A.2", compter_lettres("BONJOUR")["O"])
    print("B.1", cle_scytale_possibles(40))
    print("B.2", decouper_en_morceaux("ABCDEFGH", 3))
    chiffre = scytale_chiffrer("LEGRANDMESSAGERARRIVECETTEAPRESMIDI", 7)
    print("B.3", attaque_scytale(chiffre)[0], "->", attaque_scytale(chiffre)[1])
    print("C.1", cesar_chiffrer("BONJOUR, LE MONDE", 3))
    print("C.2", cesar_dechiffrer("ERQMRXU, OH PRQGH", 3))
    print("C.3", forcer_cesar(cesar_chiffrer("LE MESSAGE ARRIVE CE SOIR", 17)))
    print("D.1", message_compromis("ATTAQUE", "XWWD TXH, O'DSSURFKH !"))
    if MESSAGE_SCYTALE:
        print("E.1", attaque_scytale(MESSAGE_SCYTALE)[0])
        print("E.2", forcer_cesar(MESSAGE_CESAR)[0])
