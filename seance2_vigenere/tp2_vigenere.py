"""==========================================================================
 TP 2 — CODES POLYALPHABÉTIQUES : VIGENÈRE ET SON ATTAQUE
 Chapitre 2 (fin) : « Codes polyalphabétiques » — Pascal Boyer,
 « Cryptographie 2013 ».

 Durée conseillée : 2 h.   À rendre : ce fichier complété.
==========================================================================

IDÉE DU COURS
-------------
Un code de substitution simple remplace toujours la même lettre par la même
autre lettre.  César est dans ce cas, et c'est pour cela qu'on le casse en
comparant les fréquences.  Vigenère fait autre chose : la lettre de clef qui
sert à décaler change à chaque lettre du message.  La même lettre du texte clair
devient donc des lettres différentes dans le texte chiffré, et l'analyse des
fréquences ne dit plus rien.

Mais le système garde une régularité : si la clef fait 5 lettres, la lettre de
clef utilisée revient tous les 5 caractères.  La position 1, la position 6, la
position 11... sont toutes décalées de la MÊME quantité.  Autrement dit, si
l'on découpe le texte en 5 colonnes (une par lettre de clef), chaque colonne est
un simple code de César — et l'on sait casser César !  C'est toute l'astuce de
l'attaque : trouver la longueur de la clef (la période), puis casser chaque
colonne séparément.

COMMENT TRAVAILLER
------------------
    python3 test_tp2_vigenere.py        (à relancer après chaque fonction)

FONCTIONS À ÉCRIRE (dans l'ordre)
---------------------------------
  A.1  indice_de_la_lettre        A.2  decaler_lettre        A.3  vider_les_espaces
  B.1  vigenere_chiffrer          B.2  vigenere_dechiffrer
  C.1  forcer_cesar_sur_colonne   C.2  colonnes              C.3  recoller
  C.4  forcer_vigenere
  D.1  cle_par_texte_connu
==========================================================================
"""

import os
import sys

# Permet de trouver le dossier « outils » du dépôt, quel que soit l'endroit
# d'où l'on lance la commande.
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.reference import (  # noqa: E402
    ALPHABET,
    nettoyer,
    rehabiller,
    vigenere_chiffrer as vigenere_chiffrer_reference,
    vigenere_dechiffrer as vigenere_dechiffrer_reference,
)
from outils.texte_francais import distance_au_francais  # noqa: E402


# ==========================================================================
# PARTIE A — PETITS OUTILS
# ==========================================================================

def indice_de_la_lettre(lettre):
    """A.1 — Renvoie le rang de la lettre dans l'alphabet : A -> 0, B -> 1, ..., Z -> 25.

    Arguments :
        lettre (str) : une lettre, majuscule ou minuscule.

    Renvoie :
        int : le rang entre 0 et 25.

    Exemples :
        indice_de_la_lettre("A")  ->  0
        indice_de_la_lettre("M")  ->  12
        indice_de_la_lettre("z")  ->  25

    Indication : `ALPHABET.index(lettre.upper())` fait tout le travail.
    """
    # ------------------------------------------------------------------
    # TODO A.1
    # ------------------------------------------------------------------
    raise NotImplementedError("A.1 indice_de_la_lettre n'est pas encore écrite")


def decaler_lettre(lettre, decalage):
    """A.2 — Décale une lettre de `decalage` rangs dans l'alphabet, en revenant
    au début après Z (donc modulo 26).

    Arguments :
        lettre (str) : une lettre, majuscule ou minuscule.
        decalage (int) : un entier, qui peut être négatif.

    Renvoie :
        str : la lettre obtenue, en majuscule.

    Exemples :
        decaler_lettre("A", 3)   ->  "D"
        decaler_lettre("Z", 1)   ->  "A"
        decaler_lettre("A", -1)  ->  "Z"
        decaler_lettre("B", -1)  ->  "A"
        decaler_lettre("B", 25)  ->  "A"

    Indication : `(indice + decalage) % 26` puis `ALPHABET[...]` ; pensez à
    utiliser votre fonction A.1.
    """
    # ------------------------------------------------------------------
    # TODO A.2
    # ------------------------------------------------------------------
    raise NotImplementedError("A.2 decaler_lettre n'est pas encore écrite")


def vider_les_espaces(texte):
    """A.3 — Renvoie le texte en majuscules, sans aucun caractère autre que A...Z.

    C'est la fonction `nettoyer` de `outils/reference.py`, que vous connaissez
    déjà ; réécrivez-la ici pour l'avoir sous la main (et parce que c'est un bon
    exercice).

    Exemples :
        vider_les_espaces("Bonjour, l'ami !")  ->  "BONJOURLAMI"
        vider_les_espaces("DEJA PROPRE")       ->  "DEJAPROPRE"
    """
    # ------------------------------------------------------------------
    # TODO A.3
    # ------------------------------------------------------------------
    raise NotImplementedError("A.3 vider_les_espaces n'est pas encore écrite")


# ==========================================================================
# PARTIE B — LE CODE DE VIGENÈRE
# ==========================================================================
#
# Convention du cours (et de tous les exercices de ce TP) :
#   * la clef est une suite de lettres, par exemple "CLE" ;
#   * la lettre de clef de rang 0 décale de 0, celle de rang 1 de 1, etc. ;
#   * la clef se répète si le message est plus long qu'elle ;
#   * les caractères qui ne sont pas des lettres (espaces, ponctuation) sont
#     recopiés tels quels ET NE CONSOMMENT PAS de lettre de clef.
#
# Ce dernier point est une convention : on pourrait imaginer que les espaces
# consomment aussi une lettre de clef.  Vous étudierez les deux à la question
# D.2 ; pour l'instant, on suit la convention habituelle.

def vigenere_chiffrer(texte, cle):
    """B.1 — Chiffre `texte` par le code de Vigenère de clef `cle`.

    Arguments :
        texte (str) : le message en clair.
        cle (str) : la clef, uniquement des lettres (ex. "CLE", "SECRET").

    Renvoie :
        str : le message chiffré, de même longueur que le message en clair.

    Exemples (vérifiez-les une fois votre fonction écrite !) :
        vigenere_chiffrer("BONJOUR", "CLE")                ->  "DZRLZYT"
        vigenere_chiffrer("BONJOUR LE MONDE", "CLE")       ->  "DZRLZYT WI OZRFP"

    Indications :
        * conservez une variable `rang_clef` qui compte combien de LETTRES ont
          déjà été chiffrées ; la lettre de clef utilisée est
          `cle[rang_clef % len(cle)]` (le % fait tourner la clef en boucle) ;
        * parcourez le texte mis en majuscules ;
        * si le caractère est une lettre : décalez-la avec votre fonction A.2,
          puis augmentez `rang_clef` de 1 ;
        * sinon : recopiez le caractère SANS toucher à `rang_clef`.
    """
    # ------------------------------------------------------------------
    # TODO B.1
    # ------------------------------------------------------------------
    raise NotImplementedError("B.1 vigenere_chiffrer n'est pas encore écrite")


def vigenere_dechiffrer(texte_chiffre, cle):
    """B.2 — Déchiffre un message chiffré par votre fonction B.1.

    Arguments :
        texte_chiffre (str) : le message chiffré.
        cle (str) : la clef utilisée au chiffrement.

    Renvoie :
        str : le message en clair (en majuscules, espaces et ponctuation
              conservés).

    Exemple :
        vigenere_dechiffrer("DZRLZYT WI OZRFP", "CLE")  ->  "BONJOUR LE MONDE"

    Indication : c'est exactement la même chose que B.1, mais en décalant de
    l'opposé (`-decalage`).  Vous pouvez recopier votre fonction B.1 et changer
    un signe... ou écrire une seule ligne maligne : le décalage du déchiffrement
    de la lettre i est l'opposé de celui du chiffrement de la lettre i.
    """
    # ------------------------------------------------------------------
    # TODO B.2
    # ------------------------------------------------------------------
    raise NotImplementedError("B.2 vigenere_dechiffrer n'est pas encore écrite")


# ==========================================================================
# PARTIE C — L'ATTAQUE DE VIGENÈRE
# ==========================================================================

def forcer_cesar_sur_colonne(colonne):
    """C.1 — Retrouve le décalage d'une colonne de Vigenère.

    Une colonne, c'est l'ensemble des caractères qui ont été décalés par la MÊME
    lettre de clef.  C'est donc un texte français chiffré par un simple code de
    César : pour la casser, on essaie les 26 décalages possibles et l'on garde
    celui qui donne le texte le plus proche du français.

    Arguments :
        colonne (str) : les lettres d'une colonne (une chaîne de lettres).

    Renvoie :
        int : le décalage (entre 0 et 25) qui a servi à chiffrer cette colonne.
              Rappel : décalage 0 <=> lettre de clef A, décalage 3 <=> D, etc.

    Comment faire :
        * pour chaque décalage `d` de 0 à 25 :
              essai = "" puis, pour chaque lettre de la colonne, ajoutez
              `decaler_lettre(lettre, -d)`   (on essaie de DÉCHIFFRER)
              distance = distance_au_francais(essai)
        * gardez le décalage qui donne la plus PETITE distance.

    Exemple : si la colonne a été chiffrée avec la lettre de clef D (décalage 3),
    la fonction doit renvoyer 3.
    """
    # ------------------------------------------------------------------
    # TODO C.1
    # ------------------------------------------------------------------
    raise NotImplementedError("C.1 forcer_cesar_sur_colonne n'est pas encore écrite")


def colonnes(texte, periode):
    """C.2 — Découpe le texte en `periode` colonnes.

    On met dans la colonne 0 tous les caractères de rang 0, période, 2*période...
    dans la colonne 1 les caractères de rang 1, 1+période, ... etc.

    Arguments :
        texte (str) : le texte à découper.
        periode (int) : le nombre de colonnes (la longueur de la clef).

    Renvoie :
        list : la liste des colonnes (chaînes de caractères).

    Exemples :
        colonnes("ABCDEFGHIJ", 3)  ->  ["ADGJ", "BEH", "CFI"]
        colonnes("ABCDEF", 2)      ->  ["ACE", "BDF"]

    Indications :
        * créez une liste de `periode` chaînes vides : `[ "" for _ in range(periode) ]`
          (ou construisez-la avec une boucle) ;
        * parcourez les caractères avec `for position, caractere in enumerate(texte)`
          (`enumerate` donne à la fois la position et le caractère) ;
        * ajoutez le caractère à la colonne numéro `position % periode`.
    """
    # ------------------------------------------------------------------
    # TODO C.2
    # ------------------------------------------------------------------
    raise NotImplementedError("C.2 colonnes n'est pas encore écrite")


def recoller(morceaux, periode):
    """C.3 — Opération inverse de `colonnes` : on remet les colonnes dans l'ordre.

    Arguments :
        morceaux (list) : la liste des colonnes, par exemple ["ADGJ", "BEH", "CFI"].
        periode (int) : le nombre de colonnes.

    Renvoie :
        str : le texte entrelacé.

    Exemple :
        recoller(["ADGJ", "BEH", "CFI"], 3)  ->  "ABCDEFGHIJ"

    Indications :
        * parcourez les positions 0, 1, 2, ... du texte à reconstruire ;
        * à la position `i`, le caractère vient de la colonne numéro `i % periode` ;
        * pour savoir lequel prendre dans cette colonne, comptez combien de
          caractères de cette colonne ont déjà été utilisés : c'est `i // periode`
          (la division entière).
    """
    # ------------------------------------------------------------------
    # TODO C.3
    # ------------------------------------------------------------------
    raise NotImplementedError("C.3 recoller n'est pas encore écrite")


def forcer_vigenere(texte_chiffre, periode):
    """C.4 — Casse un message de Vigenère dont on connaît la période.

    Méthode (c'est l'attaque du cours) :
        1. découpez le message chiffré en `periode` colonnes (fonction C.2) ;
        2. pour chaque colonne, trouvez le décalage (fonction C.1) ;
        3. pour chaque colonne, déchiffrez-la avec son décalage ;
        4. recollez les colonnes déchiffrées (fonction C.3) ;
        5. remettez les espaces et la ponctuation du message chiffré :
           utilisez la fonction `rehabiller(texte_chiffre, lettres_dechiffrees)`
           fournie en haut de ce fichier ;
        6. la clef est la suite des lettres de clef : décalage 0 -> A, 1 -> B...

    Arguments :
        texte_chiffre (str) : le message chiffré (avec ou sans espaces).
        periode (int) : la longueur de la clef, déjà connue.

    Renvoie :
        tuple : (cle, texte_clair) — la clef (chaîne de lettres) et le message
                en clair, avec les espaces et la ponctuation du message chiffré.

    Exemple d'utilisation (essayez avec vos deux messages à décrypter) :
        cle, clair = forcer_vigenere(MESSAGE_VIGENERE_1, PERIODE_1)
        print(cle, clair)
    """
    # ------------------------------------------------------------------
    # TODO C.4
    # ------------------------------------------------------------------
    raise NotImplementedError("C.4 forcer_vigenere n'est pas encore écrite")


# ==========================================================================
# PARTIE D — QUI VA AVEC QUOI (texte connu, et la question des espaces)
# ==========================================================================

def cle_par_texte_connu(message_clair, message_chiffre):
    """D.1 — Retrouve la clef quand on connaît le texte clair ET le texte chiffré.

    C'est l'attaque la plus simple de toutes, et la plus ancienne : si l'on met
    la main sur le message en clair (un rapport, un communiqué, un télégramme),
    on compare les deux textes lettre par lettre et l'on retrouve la clef.

    Méthode :
        1. supprimez la ponctuation et les espaces des deux textes (A.3) ;
        2. pour chaque position, le décalage appliqué est
               (indice de la lettre chiffrée - indice de la lettre claire) mod 26
        3. ce décalage se traduit en lettre de clef (0 -> A, 1 -> B, ...) et vous
           obtenez ainsi la clef répétée autant de fois que nécessaire, par
           exemple "CLECLECLECLE" ;
        4. trouvez la plus PETITE période p telle que
               cle_repete[i] == cle_repete[i + p]  pour toutes les positions i,
           et renvoyez les p premières lettres : c'est la clef.

    Arguments :
        message_clair (str) : le message en clair connu.
        message_chiffre (str) : le message chiffré correspondant.

    Renvoie :
        str : la clef, sans répétition (par exemple "CLE").

    Exemples :
        clair   = "BONJOUR"
        chiffre = "DZRLZYT"        (chiffré avec la clef "CLE")
        cle_par_texte_connu(clair, chiffre)  ->  "CLE"

    Indication : pour trouver la plus petite période, essayez p = 1, puis p = 2,
    etc., et testez toutes les positions i pour ce p ; arrêtez-vous au premier
    p qui convient.
    """
    # ------------------------------------------------------------------
    # TODO D.1
    # ------------------------------------------------------------------
    raise NotImplementedError("D.1 cle_par_texte_connu n'est pas encore écrite")


# ==========================================================================
# PARTIE E — DEUX MESSAGES INTERCEPTÉS À DÉCRYPTER
# ==========================================================================
#
# Voici deux dépêches chiffrées par Vigenère.  Bonne nouvelle : on connaît la
# période de chacune (elle a été obtenue par des agents restés anonymes).
# À vous de retrouver la clef et le texte !

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
    print("Rappel : le corrigé du professeur utilise ces mêmes fonctions.")
    print("Un exemple de chiffrement, une fois B.1 écrite :")
    print("  vigenere_chiffrer('BONJOUR LE MONDE', 'CLE') doit donner",
          repr(vigenere_chiffrer_reference("BONJOUR LE MONDE", "CLE")))
    print()
    print("Longueur du premier message intercepté :", len(MESSAGE_VIGENERE_1))
    print("Longueur du second  message intercepté :", len(MESSAGE_VIGENERE_2))
