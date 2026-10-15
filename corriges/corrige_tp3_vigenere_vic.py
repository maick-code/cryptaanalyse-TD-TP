"""=========================================================================
 CORRIGÉ DU TP 3 — cryptanalyse de Vigenère (Kasiski, Friedman) et VIC
==========================================================================
Version corrigée du fichier des étudiants ; mêmes noms, mêmes épreuves :

    cd seance3_cryptanalyse
    TP_CORRIGE=1 python3 test_tp3_vigenere_vic.py

PARTIE B — outils d'analyse à écrire :
    indice_coincidence_moyen, periode_probable
PARTIE C — CRYPTANALYSE DE VIGENÈRE (période inconnue) :
    kasiski_distances, support_kasiski, forcer_vigenere
PARTIE D — CODE DE VIC :
    chiffre_du_damier, dechiffrer_message_vic
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
    colonnes,              # outil fourni
    deviner_ligne_vic,     # outil fourni
    diviseurs,             # outil fourni
    grammes_repetes,       # outil fourni
    permutation_inverse,
    recoller,              # outil fourni
    retirer_cle,
    transposition,
    vider_les_espaces,     # outil fourni
)
from outils.texte_francais import (  # noqa: E402
    decalage_probable,     # outil fourni
    indice_de_coincidence,
    indices_par_periode,   # outil fourni
)


# ==========================================================================
# PARTIE B — outils d'analyse
# ==========================================================================

def indice_coincidence_moyen(texte, periode):
    """Solution B.1 — moyenne des indices de coïncidence des colonnes.

    Si `periode` est la bonne, chaque colonne est un César du français : son
    indice vaut environ 0,075.  Sinon les colonnes mélangent les décalages et
    l'indice retombe vers 0,038.
    """
    if not texte:
        return 0.0
    morceaux = colonnes(texte, periode)
    total = 0.0
    for morceau in morceaux:
        total += indice_de_coincidence(morceau)
    return total / len(morceaux)


def periode_probable(texte, maximum=15, proportion=0.9):
    """Solution B.2 — la plus petite période qui atteint 90 % du meilleur indice.

    On prend la PLUS PETITE parce que les multiples de la vraie période (2p, 3p)
    donnent eux aussi des colonnes cohérentes : ils « marchent » aussi, mais ce
    n'est pas la vraie longueur de clef.
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
# PARTIE C — CRYPTANALYSE DE VIGENÈRE (période inconnue)
# ==========================================================================

def kasiski_distances(chiffre, mot):
    """Solution C.1 — distances entre les répétitions successives d'un groupe."""
    positions = []
    for debut in range(len(chiffre) - len(mot) + 1):
        if chiffre[debut:debut + len(mot)] == mot:
            positions.append(debut)

    distances = []
    for rang in range(len(positions) - 1):
        distance = positions[rang + 1] - positions[rang]
        if distance not in distances:
            distances.append(distance)
    return sorted(distances)


def support_kasiski(chiffre, taille=4, maximum=15):
    """Solution C.2 — combien de répétitions de Kasiski « votent » pour chaque
    période possible.

    Pour chaque groupe répété, on mesure les distances, et pour chaque distance
    on compte un point à chacun de ses diviseurs compris entre 2 et `maximum`.
    """
    support = {}
    for groupe in grammes_repetes(chiffre, taille):
        for distance in kasiski_distances(chiffre, groupe):
            for periode in diviseurs(distance):
                if 2 <= periode <= maximum:
                    support[periode] = support.get(periode, 0) + 1
    return support


def forcer_vigenere(chiffre, periode):
    """Solution C.3 — l'attaque complète : période trouvée, puis colonne par
    colonne, puis on recolle."""
    morceaux = colonnes(vider_les_espaces(chiffre), periode)

    decalages = []
    cle = ""
    for morceau in morceaux:
        decalage = decalage_probable(morceau)
        decalages.append(decalage)
        cle += ALPHABET[decalage]

    morceaux_clairs = []
    for rang in range(periode):
        colonne_claire = ""
        for lettre in morceaux[rang]:
            colonne_claire += ALPHABET[(ALPHABET.index(lettre) - decalages[rang]) % 26]
        morceaux_clairs.append(colonne_claire)

    return cle, recoller(morceaux_clairs, periode)


# ==========================================================================
# PARTIE D — code de VIC (version simplifiée)
# ==========================================================================

def chiffre_du_damier(lettre, chiffre_clef, position):
    """Solution D.1 — on retrouve la ligne du damier, puis on retire la clef."""
    ligne = deviner_ligne_vic(lettre, position % 10)
    return (ligne - chiffre_clef) % 10


def dechiffrer_message_vic(message_chiffre, cle, permutation=PERMUTATION_VIC):
    """Solution D.2 — les quatre étapes du chiffrement, à l'envers."""
    chiffres = ""
    for position, caractere in enumerate(message_chiffre.upper()):
        chiffre_clef = int(cle[position % len(cle)])
        chiffres += str(chiffre_du_damier(caractere, chiffre_clef, position))

    chiffres = transposition(chiffres, permutation_inverse(list(permutation)))
    chiffres = retirer_cle(chiffres, cle)
    return chiffres_en_message(chiffres)


# ==========================================================================
# MESSAGES INTERCEPTÉS (remplis par outils/generer_messages.py)
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

MESSAGE_3 = (
    "RIUFVZLRVWNLGAMITILDSJTPMSFWKZLQQSMKSZWYNSHLMBPEVBYDWZZRHRYKII"
    "LMTSNDWDZVUQBSFUPHFJCKSUPPFGAJMSDMNAITAZPWESMKABPRURYKGAMVFGFG"
    "FUFITGOJDSDIOHLWHCEWFHFGFSYXFBXKWIWINSHLDSNPBDILAGOIMSUMUCYXSS"
    "FWKQZUVSMMFJTIJZBGEAPTBGMWSJPGVBWZASYWBFLWLSFRJBMLSBETPILJWULV"
    "ESLDWGQIVLXWKPLXFOOPSIWESUYHMWDGPBNAFIPWPBWZWATRTOHKJWPREWLWVO"
    "YWMSMTMFPEVLXMHCCXVBYDSAAICFODWSYGPFYMFSXTMCSWUZLWTSXWKDLTJSLK"
    "UCEIQOLUGHPGPAGWGBLPJUHWVSDPFHNJWGDYSIHWHORIJZHGLSOEOGOFUOSMFF"
    "FWKOCVJJYWKRFNPILDWGOIQOLLKRFPFBXWEOTRMSHGERPWCONWSIIIUZUFSHFV"
    "FRYKEOCGIOHVAGPWQZOKLOCHRIUFVHZYUGYJSGTPFBWA"
)

MESSAGE_4 = (
    "ZVTXEWEEYXSETXISEGGVSRVKGIEENIIIEJIFVTGVRJUXPSHUGMZVSBSMRGKYFJ"
    "SOQDRTOIBKETXZVSVSFKEAVGTHKVQYETXZVUXWQCIKRHJEZYBVMVPCPEGRBFNI"
    "IRLNKZCZXREGJEWYSCEJIDRRZEIIARMSLDGRGMITKHDITYHVSVIFJOTRSEEYIA"
    "SLKPSTOAXSIDGRGCEHYFVAAHITHKJRVGGVSFNIPOJSKHSJTKPSXRGQAVSVEFFR"
    "JVSUAXVWMEKGSCUOHSTESEHZNBMSETJIZRCUXSZLVEFCEJIARRIL"
)

MESSAGE_VIC = (
    "ELAANODTRDIESTIITEOESEANIOODRTRESNSDDSARLNAANSETTRIENINISRNIIO"
    "ILLEEDNNENROOOELAS"
)

CLE_VIC = "5241730219"
# --- FIN DE LA ZONE GÉNÉRÉE ---
