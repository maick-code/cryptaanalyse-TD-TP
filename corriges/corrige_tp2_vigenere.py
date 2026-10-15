"""=========================================================================
 CORRIGÉ DU TP 2 — codes polyalphabétiques (Vigenère) et son attaque
==========================================================================
Test :
    cd seance2_vigenere
    TP_CORRIGE=1 python3 test_tp2_vigenere.py
==========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.reference import ALPHABET, rehabiller  # noqa: E402
from outils.texte_francais import distance_au_francais  # noqa: E402


# ==========================================================================
# PARTIE A
# ==========================================================================

def indice_de_la_lettre(lettre):
    """Solution A.1."""
    return ALPHABET.index(lettre.upper())


def decaler_lettre(lettre, decalage):
    """Solution A.2."""
    return ALPHABET[(indice_de_la_lettre(lettre) + decalage) % 26]


def vider_les_espaces(texte):
    """Solution A.3."""
    resultat = ""
    for caractere in texte.upper():
        if "A" <= caractere <= "Z":
            resultat += caractere
    return resultat


# ==========================================================================
# PARTIE B
# ==========================================================================

def vigenere_chiffrer(texte, cle):
    """Solution B.1.

    Le point délicat est le compteur `rang_clef` : il ne s'incrémente QUE
    lorsqu'on rencontre une lettre, car les espaces et la ponctuation ne
    consomment pas de lettre de clef (convention des exercices de ce TP).
    """
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    chiffre = ""
    rang_clef = 0
    for caractere in texte.upper():
        if "A" <= caractere <= "Z":
            decalage = indice_de_la_lettre(cle[rang_clef % len(cle)])
            chiffre += decaler_lettre(caractere, decalage)
            rang_clef += 1
        else:
            chiffre += caractere
    return chiffre


def vigenere_dechiffrer(texte_chiffre, cle):
    """Solution B.2 — le même parcours, avec le décalage opposé."""
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    clair = ""
    rang_clef = 0
    for caractere in texte_chiffre.upper():
        if "A" <= caractere <= "Z":
            decalage = indice_de_la_lettre(cle[rang_clef % len(cle)])
            clair += decaler_lettre(caractere, -decalage)
            rang_clef += 1
        else:
            clair += caractere
    return clair


# ==========================================================================
# PARTIE C
# ==========================================================================

def forcer_cesar_sur_colonne(colonne):
    """Solution C.1 — on essaie les 26 décalages et l'on garde celui qui donne
    le texte le plus proche des fréquences du français."""
    meilleur_decalage = 0
    meilleure_distance = None
    for decalage in range(26):
        essai = ""
        for lettre in colonne:
            if "A" <= lettre.upper() <= "Z":
                essai += decaler_lettre(lettre, -decalage)
        distance = distance_au_francais(essai)
        if meilleure_distance is None or distance < meilleure_distance:
            meilleure_distance = distance
            meilleur_decalage = decalage
    return meilleur_decalage


def colonnes(texte, periode):
    """Solution C.2."""
    morceaux = ["" for _ in range(periode)]
    for position, caractere in enumerate(texte):
        morceaux[position % periode] += caractere
    return morceaux


def recoller(morceaux, periode):
    """Solution C.3."""
    total = sum(len(morceau) for morceau in morceaux)
    texte = ""
    for position in range(total):
        colonne = position % periode
        rang_dans_la_colonne = position // periode
        texte += morceaux[colonne][rang_dans_la_colonne]
    return texte


def forcer_vigenere(texte_chiffre, periode):
    """Solution C.4 — l'attaque complète, période connue.

    Les colonnes sont calculées sur le texte SANS espaces (puisque les espaces
    ne consomment pas de lettre de clef), puis les lettres déchiffrées sont
    replacées dans la présentation du message chiffré.
    """
    lettres_chiffrees = vider_les_espaces(texte_chiffre)
    morceaux = colonnes(lettres_chiffrees, periode)

    cle = ""
    morceaux_clairs = []
    for morceau in morceaux:
        decalage = forcer_cesar_sur_colonne(morceau)
        cle += ALPHABET[decalage]
        morceaux_clairs.append("".join(decaler_lettre(c, -decalage) for c in morceau))

    lettres_claires = recoller(morceaux_clairs, periode)
    return cle, rehabiller(texte_chiffre, lettres_claires)


# ==========================================================================
# PARTIE D
# ==========================================================================

def cle_par_texte_connu(message_clair, message_chiffre):
    """Solution D.1."""
    clair = vider_les_espaces(message_clair)
    chiffre = vider_les_espaces(message_chiffre)
    if len(clair) != len(chiffre):
        raise ValueError(
            "les deux messages doivent avoir le même nombre de lettres "
            f"({len(clair)} lettres en clair, {len(chiffre)} lettres chiffrées)"
        )

    lettres_clef = ""
    for position in range(len(clair)):
        decalage = (indice_de_la_lettre(chiffre[position])
                    - indice_de_la_lettre(clair[position])) % 26
        lettres_clef += ALPHABET[decalage]

    for periode in range(1, len(lettres_clef) + 1):
        repetee = all(
            lettres_clef[position] == lettres_clef[position + periode]
            for position in range(len(lettres_clef) - periode)
        )
        if repetee:
            return lettres_clef[:periode]
    return lettres_clef


# ==========================================================================
# PARTIE E — constantes (remplies par outils/generer_messages.py)
# ==========================================================================

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
MESSAGE_VIGENERE_1 = (
    "XS PRRESVO HQ ZN QEFWBQ WQ FRXRUH QHQMWA PEFWA D LGWG KIGFRV. "
    "MX GRUE CIRVXUCA GIE HEDZMIK GY BCEW, HQ ZN USGHR QEFWBQEXS RW"
    " HG BBXZQOH PEDQUH. PQG QHPQUHHW PSF YMXZNJIE JBLWUBF RRF OAQS"
    "ZQR OIGF NUVUJRH TAIE OE ZIVW. PQ DEHWURRQX PI PRRESVO TDSFHRF"
    "SED WAB EDTBCEW HQJNQX XSF QSFOOOIE RR OE DSTLSZ. HBXX XS ZRRP"
    "S NWXQBQ FIFHR UIGBVRR MJRF MYDNWMQBPH GMF YHW PSPLWUCAV TDWFH"
    "W OVNQKQFBQX XO ILI PS ARW CINUXUSEV TAIE GI XCAJYQG NQRQSF."
)

MESSAGE_VIGENERE_2 = (
    "XE WQEIGFENZ QY TARM I EIGG NHBEI PQTMZR. MP DEIWAH UGE EMF XV"
    "MVTCK HI PRTONKI OOFURRGQRHVG EY PEUCG HY YOBA CVSOHTQA IX CUX"
    " TRW FMTXIHB HQVKWAX VQSMME EY YONQYPESE IMAHEZT WQK NSGRL. TR"
    "W TMTKWAW HQS IMPLIDIXA QIQMNWMAX YZE BVQIQZIMM CSYD LT XRVXQ "
    "DX TRYV BEVPR. RSGS TDBRW BRHXBWI GNX ZRRGANMZR EZQC EMF VIEPH"
    "VFEFXEL LH QMZILBRVI."
)

PERIODE_1 = 5

PERIODE_2 = 7
# --- FIN DE LA ZONE GÉNÉRÉE ---


if __name__ == "__main__":
    print("A.1", indice_de_la_lettre("M"), "| A.2", decaler_lettre("A", -1),
          "| A.3", vider_les_espaces("Bonjour, l'ami !"))
    print("B.1", vigenere_chiffrer("BONJOUR LE MONDE", "CLE"))
    print("B.2", vigenere_dechiffrer("DZRLZYT WI OZRFP", "CLE"))
    print("D.1", cle_par_texte_connu("BONJOUR", "DZRLZYT"))
    if MESSAGE_VIGENERE_1:
        cle, clair = forcer_vigenere(MESSAGE_VIGENERE_1, PERIODE_1)
        print("E.1 clef", cle, "->", clair[:70], "...")
        cle, clair = forcer_vigenere(MESSAGE_VIGENERE_2, PERIODE_2)
        print("E.2 clef", cle, "->", clair[:70], "...")
