"""=========================================================================
 CORRIGÉ DU TP 3 — cryptanalyse de Vigenère (Kasiski, Friedman) et VIC
==========================================================================
Test :
    cd seance3_cryptanalyse
    TP_CORRIGE=1 python3 test_tp3_vigenere_vic.py
==========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.reference import (  # noqa: E402
    ALPHABET,
    PERMUTATION_VIC,
    chiffres_en_message,
    deviner_ligne_vic,
    lettre_vic,
    permutation_inverse,
    retirer_cle,
    transposition,
)
from outils.texte_francais import distance_au_francais, indice_de_coincidence  # noqa: E402


def colonnes(texte, periode):
    """Découpage en colonnes (repris du TP 2)."""
    morceaux = ["" for _ in range(periode)]
    for position, caractere in enumerate(texte):
        morceaux[position % periode] += caractere
    return morceaux


# ==========================================================================
# PARTIE A — la période par l'indice de coïncidence
# ==========================================================================

def indice_coincidence_moyen(texte, periode):
    """Solution A.1."""
    if not texte:
        return 0.0
    morceaux = colonnes(texte, periode)
    total = 0.0
    for morceau in morceaux:
        total += indice_de_coincidence(morceau)
    return total / len(morceaux)


def indices_par_periode(texte, maximum=15):
    """Solution A.2 — un dictionnaire {periode: indice de coïncidence moyen}."""
    return {periode: indice_coincidence_moyen(texte, periode)
            for periode in range(1, maximum + 1)}


def periode_probable(texte, maximum=15, proportion=0.9):
    """Solution A.3 — la plus petite période dont l'indice atteint 90 % du meilleur.

    Subtilité importante : un simple seuil fixe (par exemple 0,06) ne suffit
    pas.  Exemple vécu : pour un message dont la vraie période est 6, l'indice
    de la période 3 (qui mélange deux lettres de clef) peut monter à 0,067 et
    passer au-dessus d'un seuil de 0,06 !  Comparer les périodes au meilleur
    indice obtenu, et non à une valeur fixe, évite cet écueil.
    """
    indices = indices_par_periode(texte, maximum)
    if not indices:
        return None
    seuil = proportion * max(indices.values())
    for periode in range(1, maximum + 1):
        if indices[periode] >= seuil:
            return periode
    return None


# ==========================================================================
# PARTIE B — Kasiski
# ==========================================================================

def grammes_repetes(chiffre, taille):
    """Solution B.1."""
    comptes = {}
    for debut in range(0, len(chiffre) - taille + 1):
        morceau = chiffre[debut:debut + taille]
        comptes[morceau] = comptes.get(morceau, 0) + 1
    repetes = []
    for morceau in comptes:
        if comptes[morceau] >= 2:
            repetes.append(morceau)
    return sorted(repetes)


def _positions(chiffre, mot):
    """Positions (indices) où commence `mot` dans `chiffre` (fonction auxiliaire)."""
    positions = []
    for debut in range(0, len(chiffre) - len(mot) + 1):
        if chiffre[debut:debut + len(mot)] == mot:
            positions.append(debut)
    return positions


def kasiski_distances(chiffre, mot):
    """Solution B.2."""
    positions = _positions(chiffre, mot)
    distances = []
    for rang in range(len(positions) - 1):
        distance = positions[rang + 1] - positions[rang]
        if distance not in distances:
            distances.append(distance)
    return sorted(distances)


def diviseurs(nombre):
    """Solution B.3."""
    liste = []
    for candidat in range(1, nombre + 1):
        if nombre % candidat == 0:
            liste.append(candidat)
    return liste


def periodes_par_kasiski(chiffre, taille=4, maximum=15):
    """Fonction auxiliaire (non demandée aux étudiants) : compte, pour chaque
    période candidate, combien de distances elle divise.

    Renvoie un dictionnaire {periode: nombre de distances divisées}.
    """
    support = {periode: 0 for periode in range(2, maximum + 1)}
    for morceau in grammes_repetes(chiffre, taille):
        for distance in kasiski_distances(chiffre, morceau):
            for periode in range(2, maximum + 1):
                if distance % periode == 0:
                    support[periode] += 1
    return support


# ==========================================================================
# PARTIE C — casser les messages
# ==========================================================================

def forcer_cesar_sur_colonne(colonne):
    """Solution C.1."""
    meilleur_decalage = 0
    meilleure_distance = None
    for decalage in range(26):
        essai = "".join(
            ALPHABET[(ALPHABET.index(c) - decalage) % 26]
            for c in colonne.upper() if "A" <= c <= "Z"
        )
        distance = distance_au_francais(essai)
        if meilleure_distance is None or distance < meilleure_distance:
            meilleure_distance = distance
            meilleur_decalage = decalage
    return meilleur_decalage


def forcer_vigenere(chiffre, periode):
    """Solution C.2."""
    morceaux = colonnes(chiffre, periode)
    cle = ""
    morceaux_clairs = []
    for morceau in morceaux:
        decalage = forcer_cesar_sur_colonne(morceau)
        cle += ALPHABET[decalage]
        morceaux_clairs.append(
            "".join(ALPHABET[(ALPHABET.index(c) - decalage) % 26]
                    for c in morceau.upper() if "A" <= c <= "Z")
        )

    total = sum(len(morceau) for morceau in morceaux_clairs)
    clair = ""
    for position in range(total):
        clair += morceaux_clairs[position % periode][position // periode]
    return cle, clair


# ==========================================================================
# PARTIE D — VIC simplifié
# ==========================================================================

def caractere_vic(chiffre_message, chiffre_clef, position):
    """Solution D.1."""
    ligne = (chiffre_message + chiffre_clef) % 10
    return lettre_vic(ligne, position % 10)


def ligne_du_damier(lettre, position):
    """Solution D.2."""
    return deviner_ligne_vic(lettre, position % 10)


def chiffre_du_damier(lettre, chiffre_clef, position):
    """Solution D.3."""
    ligne = ligne_du_damier(lettre, position)
    return (ligne - chiffre_clef) % 10


def dechiffrer_message_vic(message_chiffre, cle, permutation=PERMUTATION_VIC):
    """Solution D.4 — les quatre étapes à l'envers."""
    # 1. du damier vers les chiffres
    chiffres = ""
    for position, caractere in enumerate(message_chiffre.upper()):
        chiffre_clef = int(cle[position % len(cle)])
        chiffres += str(chiffre_du_damier(caractere, chiffre_clef, position))
    # 2. transposition inverse
    chiffres = transposition(chiffres, permutation_inverse(list(permutation)))
    # 3. la clef retirée
    chiffres = retirer_cle(chiffres, cle)
    # 4. les chiffres redevenus des lettres
    return chiffres_en_message(chiffres)


# ==========================================================================
# PARTIE E — constantes (remplies par outils/generer_messages.py)
# ==========================================================================

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
MESSAGE_1 = (
    "NZVXSFIQGMEYGLYVWTXYCWIVWLMZPPJTWWISQXFWGFWJCEXJPOENVDYWNLVNXP"
    "TTWCZTKCTFUDIWNPWRCCGMCYHNUPWJVWIXXZCFIPYWUGISWDHJNZMSNPGTOXES"
    "FLRYULPZCWERCTWTPMPFPNLJFPWIQFESGDTZKDMQFZRSCWSWFCIIGAEWVTVQGQ"
    "PJWGIJVLMYNLVLGPXHCWQJEPQFVTRQCWIXGYJFPEWHQFVFKPRYNPPTPRHJNLFJ"
    "TRIJPLKNVLRYNPWRCTRXRPVXQYRJPPWFXLMYGYGTTPUZGWEHTFIFTCMAGCENVA"
    "PZUESYSFIUTPZZEPXYGLRSGPWZTWEWKGITRASXGPPJUAIHJPYWUCIUCCENGYXQ"
    "GFVXHTPJVDISRLVQCYXIWAVNZOYUQTWXQYEZOLVHJPHZNFRIKWIAKPYCRLXWQY"
    "VFEZRYCTXVWPHFPDWFLPYSGDWJKWEACTXIGDGJPOYQGQPJWGIOWDUZCWERGCEA"
    "GNYSGNLFTRIIGMSNUPXIGDIQKWWJUZYAGYENVOIXPFMYUDESUPXTKWIXQFPJEZ"
    "YWCYXUQFWXCTXQCMEWSFIAGCWQGDFFPNWIGDEGNPPJRTPTVPGTPYENUDENVNLF"
)

MESSAGE_2 = (
    "XCUHYIVUCJTVIMHCVXYOJAGKIEIWQKSBRVTMPDXFRXQYMWICEBMKMIZPMNHHVK"
    "EURDXWCIFRJXWUIXYXTQZPXCDXWASGPFTYOHQJSVEGMFYDXIKTMPXHMJYZKSGH"
    "RXMRLXRUYPCHNMJHQQEHMJPQDSVXVYDBMJYRVFGWKGFRZYALWRMFRGNXCIYMFW"
    "IVXXGKTMKPQQSWVVWECKTZFMJFSNXVHQTSGXCEBMJMICIECFYEEXEQWKEJWQKT"
    "EEZIZRSNXFYDBWEYZTASJXRKIZBJXPVWZMMOICPQQVNTRCEJWFEZXDCVXGFPQM"
    "MOVRMFJWLNFYDLSNBVXOMEFIEXMGLEIJHQAALMFREBMZSLZQPFXQVRFGDIEIPM"
    "GLWIJVASLXWUIENGGXJHQQAFTFXECLWIJIOMDXWESGTWEPVWXCKTRTMQLKXGFY"
    "FYAXRKIZQAEIEGQCLVSDTMPSBIEXMTWVPVXQKHLTRWECDXQRVOFWWYJEYCVBVV"
    "WFYAMPVKDYFWIMIZCEXRKHQJSLIDEULWHRPZQLSBXUIFPWLPFMZNGNVMIZBJXH"
    "VWMLAFELBPCKIEEMQPKWIJXUQKNWVXPCKHYKMXQDXWGVUVKXHZWOSLTMVRFYNH"
    "MOFMQKXWFYEJWLEIFDCKEEGPGGWTZRMFCLXVRVQAWMXVEZLWXIKPQQUAEDTEQG"
    "NJWVMGWGXTLMAMGQVW"
)

MESSAGE_VIC = (
    "ELAANODTRDIESTIITEOESEANIOODRTRESNSDDSARLNAANSETTRIENINISRNIIO"
    "ILLEEDNNENROOOELAS"
)

CLE_VIC = "5241730219"
# --- FIN DE LA ZONE GÉNÉRÉE ---


if __name__ == "__main__":
    for nom, message in (("MESSAGE_1", MESSAGE_1), ("MESSAGE_2", MESSAGE_2)):
        if not message:
            continue
        indices = indices_par_periode(message, 15)
        print(f"{nom} : indices de coïncidence par période")
        for periode in sorted(indices, key=lambda p: -indices[p])[:4]:
            print(f"    période {periode:2d} : {indices[periode]:.4f}")
        periode = periode_probable(message)
        print(f"  période retenue : {periode}  (indice {indices.get(periode, 0):.4f}, "
              f"meilleur indice {max(indices.values()):.4f})")
        print(f"  Kasiski (support des distances) : "
              f"{sorted(periodes_par_kasiski(message, 4, 15).items(), key=lambda e: -e[1])[:4]}")
        cle, clair = forcer_vigenere(message, periode)
        print(f"  clef : {cle}")
        print(f"  clair : {clair[:80]}...")
    if MESSAGE_VIC:
        print("VIC :", dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC))
