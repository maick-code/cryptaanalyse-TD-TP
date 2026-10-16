"""=========================================================================
 CORRIGÉ DU TP 2 — codes polyalphabétiques (Vigenère) et son attaque
==========================================================================
Version corrigée du fichier des étudiants ; mêmes noms, mêmes épreuves :

    cd seance2_vigenere
    TP_CORRIGE=1 python3 test_tp2_vigenere.py

PARTIE B — code à écrire par les étudiants :
    vigenere_chiffrer, vigenere_dechiffrer
PARTIE C — CRYPTANALYSE (le cœur du TP) :
    decalage_probable, forcer_vigenere, cle_par_texte_connu
==========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.reference import (  # noqa: E402
    ALPHABET,
    colonnes,             # outil fourni
    decaler_lettre,       # outil fourni
    indice_de_la_lettre,  # outil fourni
    rehabiller,           # outil fourni
    recoller,             # outil fourni
    vider_les_espaces,    # outil fourni
)
from outils.texte_francais import distance_au_francais  # noqa: E402


# ==========================================================================
# PARTIE B — le code à écrire
# ==========================================================================

def vigenere_chiffrer(texte, cle):
    """Solution B.1.

    Le point délicat est le compteur `rang_clef` : il ne s'incrémente QUE
    lorsqu'on rencontre une lettre, car les espaces et la ponctuation ne
    consomment pas de lettre de clef (convention de tout le TP).
    """
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    cle = cle.upper()
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
    """Solution B.2 — la même boucle, avec le décalage opposé."""
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    cle = cle.upper()
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
# PARTIE C — CRYPTANALYSE
# ==========================================================================

def decalage_probable(colonne):
    """Solution C.1 — les 26 décalages possibles d'une colonne, et l'on garde
    celui dont le texte déchiffré est le plus proche du français."""
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


def forcer_vigenere(texte_chiffre, periode):
    """Solution C.2 — l'attaque complète, période connue.

    Les colonnes sont calculées sur le texte SANS espaces (puisque les espaces
    ne consomment pas de lettre de clef), puis les lettres déchiffrées sont
    replacées dans la présentation du message chiffré avec `rehabiller`.
    """
    lettres_chiffrees = vider_les_espaces(texte_chiffre)
    morceaux = colonnes(lettres_chiffrees, periode)

    cle = ""
    morceaux_clairs = []
    for morceau in morceaux:
        decalage = decalage_probable(morceau)
        cle += ALPHABET[decalage]
        morceaux_clairs.append(
            "".join(decaler_lettre(lettre, -decalage) for lettre in morceau)
        )

    lettres_claires = recoller(morceaux_clairs, periode)
    return cle, rehabiller(texte_chiffre, lettres_claires)


def cle_par_texte_connu(message_clair, message_chiffre):
    """Solution C.3 — clef = chiffré - clair, position par position.

    Si les deux textes n'ont pas la même longueur (l'agent n'a photographié
    qu'un fragment), on compare seulement le début commun : c'est la longueur
    du plus court qui commande.
    """
    clair = vider_les_espaces(message_clair)
    chiffre = vider_les_espaces(message_chiffre)
    longueur = min(len(clair), len(chiffre))

    suite = ""
    for position in range(longueur):
        decalage = (indice_de_la_lettre(chiffre[position])
                    - indice_de_la_lettre(clair[position])) % 26
        suite += ALPHABET[decalage]

    for periode in range(1, len(suite) + 1):
        tout_bon = True
        for position in range(len(suite) - periode):
            if suite[position] != suite[position + periode]:
                tout_bon = False
                break
        if tout_bon:
            return suite[:periode]
    return suite


# ==========================================================================
# MESSAGES INTERCEPTÉS (remplis par outils/generer_messages.py)
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

PERIODE_1 = 5

MESSAGE_VIGENERE_2 = (
    "XE WQEIGFENZ QY TARM I EIGG NHBEI PQTMZR. MP DEIWAH UGE EMF XV"
    "MVTCK HI PRTONKI OOFURRGQRHVG EY PEUCG HY YOBA CVSOHTQA IX CUX"
    " TRW FMTXIHB HQVKWAX VQSMME EY YONQYPESE IMAHEZT WQK NSGRL. TR"
    "W TMTKWAW HQS IMPLIDIXA QIQMNWMAX YZE BVQIQZIMM CSYD LT XRVXQ "
    "DX TRYV BEVPR. RSGS TDBRW BRHXBWI GNX ZRRGANMZR EZQC EMF VIEPH"
    "VFEFXEL LH QMZILBRVI."
)

PERIODE_2 = 7

MESSAGE_URGENT = (
    "DI RIIYWX C IIVM RQKVX VIRVGAW. MN FVWGRPV UNW PG TSGNSK GEKLI"
    " EVXMW RWZX ISV NR VHMXG UI ES GQKI, XF IXZXTFX NVW OAPNRKXK. "
    "PGJ GAWZCLB LWVQEX VZEPXIL S PC WIKEI FL QHMPKE. P TDITKI LWVC"
    " USGFIG RY IGWVV HX YETUI TNEPK QBVM, GK GX HERZIK KITR FKMPG "
    "RYLKMVFX ES PGTXNJI VVVFARGV. WB DE TFYMW IUK GHMTGV, ME XEWK "
    "TTKWGI TTJ PG TLXEMP UI ES ZCCPXJMG VX TLXGEHKW PC EYBL TQLV M"
    "JEXVVLWV NV THFX FV TBWVTV. PXK LQDQXK HW IIESMU FRM VIU DSGLY"
    "TVW YJEKTLXK IV UY ISMP GSNJ PC ISNLI. KC RX XEWK TTJPGI E IWV"
    "UFRGW EXRRM DE RFVMW HG CE OAPNV, IM JIOVXMJI NV TEA EW TLXX H"
    "W GSLLI, SLM LWYN TSGFEKK PX ESV UI ISWUV."
)

PERIODE_URGENT = 6

MESSAGE_INTERCEPTE = (
    "GIJLEIVYYFTXOITPASMXIWLQVVMPSEPXMLGIXYVNSEMKMXPROHMMZMNIBOPJZV"
    "TPNEKMBLTRZEZPNYGSZOCIYIXLDWZVIFWEMKMOPWDPMDPXYIVPAENVMAZRYVML"
    "FBNMOYLYSHMWLGJXMWLQZVMDEGVPUPWIQIVEGMZRBOFRJVLPDXGIDZJEBILFCI"
    "MELPFBESCCDIOHMFIRPMBDLPVVZTGIZPMATPJXMLEXZRLCLPZFIEPEPHIYDPVT"
    "IDDIYYAFOIOJMCLQJRBPCEWSZOOIPBPZXQZWLPNSIJQLYGZEDPNHZWXLAMZVAP"
    "EHZWKLCXZW"
)

TEXTE_CONNU = (
    "LEBATEAUQUITTELEPORTALAMAREEHAUTEAVECUNCHARGEMENTDEBOISETDEFER"
    "LECAPITAIN"
)
# --- FIN DE LA ZONE GÉNÉRÉE ---
