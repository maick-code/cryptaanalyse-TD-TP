"""==========================================================================
 TP 3 — CRYPTANALYSE DE VIGENÈRE, PUIS LE CODE DE VIC
 Chapitre 2 (fin) : « Cryptanalyse » et « Code de VIC » — Pascal Boyer,
 « Cryptographie 2013 ».

 Durée conseillée : 2 h (2 h 30 avec le VIC).   À rendre : ce fichier complété.
==========================================================================

CE QUE L'ON SAIT ET CE QUE L'ON CHERCHE
---------------------------------------
Au TP 2, on cassait un message de Vigenère... à condition de connaître déjà la
longueur de la clef.  Ici, on ne connaît RIEN : on a juste le texte chiffré.
L'attaque se fait en deux temps :

    1. TROUVER LA PÉRIODE (la longueur de la clef).  Deux méthodes, que l'on
       met en œuvre toutes les deux et que l'on compare :
         * la méthode de Kasiski (1863) : on repère les petits groupes de
           lettres qui se répètent dans le texte chiffré, on mesure les
           distances entre deux répétitions, et l'on remarque que ces distances
           sont souvent multiples de la période ;
         * l'indice de coïncidence (Friedman, années 1920) : on découpe le texte
           en `p` colonnes pour chaque valeur possible de `p`, et l'on regarde si
           ces colonnes ressemblent à du français.  Elles y ressemblent
           exactement quand `p` est la période.

    2. CASSER CHAQUE COLONNE.  Une fois la période trouvée, chaque colonne est
       un simple code de César : on la casse par comparaison de fréquences,
       comme au TP 1.

Puis, en deuxième partie : le VIC, le chiffre utilisé par le service secret
britannique à partir de 1914 (version simplifiée, voir `outils/reference.py`).

COMMENT TRAVAILLER
------------------
    python3 test_tp3_vigenere_vic.py

FONCTIONS À ÉCRIRE (dans l'ordre)
---------------------------------
  A.1  indice_coincidence_moyen      A.2  indices_par_periode    A.3  periode_probable
  B.1  grammes_repetes               B.2  kasiski_distances      B.3  diviseurs
  C.1  forcer_cesar_sur_colonne      C.2  forcer_vigenere
  D.1  caractere_vic                 D.2  ligne_du_damier
  D.3  chiffre_du_damier             D.4  dechiffrer_message_vic
==========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.reference import (  # noqa: E402
    ALPHABET,
    ALPHABET_VIC,
    PERMUTATION_VIC,
    TABLEAU_VIC,
    ajouter_cle,
    chiffres_en_message,
    deviner_ligne_vic,
    lettre_vic,
    message_en_chiffres,
    nettoyer,
    permutation_inverse,
    retirer_cle,
    transposition,
)
from outils.texte_francais import distance_au_francais, indice_de_coincidence  # noqa: E402


# ==========================================================================
# OUTIL FOURNI (repris du TP 2) — découpage en colonnes
# ==========================================================================

def colonnes(texte, periode):
    """Découpe le texte en `periode` colonnes (fourni, ne pas modifier).

        >>> colonnes("ABCDEFGHIJ", 3)
        ['ADGJ', 'BEH', 'CFI']
    """
    morceaux = ["" for _ in range(periode)]
    for position, caractere in enumerate(texte):
        morceaux[position % periode] += caractere
    return morceaux


# ==========================================================================
# PARTIE A — TROUVER LA PÉRIODE PAR L'INDICE DE COÏNCIDENCE
# ==========================================================================
#
# Rappel de la séance 1 : dans un texte français, les lettres ne sont pas
# équiprobables, et la probabilité que deux lettres tirées au hasard soient
# égales vaut environ 0,075.  Dans un texte où les 26 lettres sont également
# probables (ce qui est le cas d'un texte bien chiffré), elle vaut 1/26, soit
# 0,038.  La fonction `indice_de_coincidence(texte)` fournie calcule ce nombre.
#
# L'idée de Friedman : si l'on découpe le texte chiffré en p colonnes et que p
# est la période, alors chaque colonne est un simple décalage du français, donc
# son indice de coïncidence vaut environ 0,075.  Sinon, les colonnes mélangent
# plusieurs décalages différents, et l'indice retombe vers 0,038.

def indice_coincidence_moyen(texte, periode):
    """A.1 — Renvoie la MOYENNE des indices de coïncidence des `periode` colonnes.

    Arguments :
        texte (str) : le texte chiffré, sans espaces (que des lettres).
        periode (int) : le nombre de colonnes à essayer.

    Renvoie :
        float : la moyenne des indices de coïncidence des colonnes.

    Indications :
        * découpez le texte : `morceaux = colonnes(texte, periode)` ;
        * pour chaque morceau, calculez `indice_de_coincidence(morceau)` et
          faites la moyenne (attention à ne pas diviser par 0 : si le texte est
          vide, renvoyez 0.0).
    """
    # ------------------------------------------------------------------
    # TODO A.1
    # ------------------------------------------------------------------
    raise NotImplementedError("A.1 indice_coincidence_moyen n'est pas encore écrite")


def indices_par_periode(texte, maximum=15):
    """A.2 — Calcule l'indice de coïncidence moyen pour chaque période possible.

    Arguments :
        texte (str) : le texte chiffré (que des lettres).
        maximum (int) : la plus grande période à essayer (15 par défaut).

    Renvoie :
        dict : {periode: indice moyen} pour toutes les périodes de 1 à
               `maximum`, par exemple {1: 0.045, 2: 0.041, 3: 0.038, 4: 0.072}

    C'est ce tableau qu'il faut regarder pour deviner la période : les valeurs
    nettement plus grandes que 0,038 trahissent les bons candidats.

    Remarque : la période 1 correspond au cas où le texte est un simple code de
    César (une clef d'une seule lettre répétée) : on garde donc 1 dans le
    tableau, même si l'on espère trouver plus grand.
    """
    # ------------------------------------------------------------------
    # TODO A.2
    # ------------------------------------------------------------------
    raise NotImplementedError("A.2 indices_par_periode n'est pas encore écrite")


def periode_probable(texte, maximum=15, proportion=0.9):
    """A.3 — Renvoie la période la plus probable du texte chiffré.

    Règle retenue :
        1. calculez l'indice de coïncidence moyen pour chaque période de 1 à
           `maximum` (fonction A.2) ;
        2. appelez `meilleur` le plus grand de ces indices ;
        3. renvoyez la PLUS PETITE période dont l'indice atteint au moins
           `proportion` fois le meilleur (0,9 par défaut, soit 90 %).

    Pourquoi 90 % du meilleur plutôt qu'un seuil fixe ?  Parce que la valeur des
    indices dépend de la longueur du texte : fixer un seuil fixe marche pour un
    texte de 600 lettres et échoue pour un texte de 120.  Comparer les périodes
    entre elles est plus solide.

    Pourquoi la plus petite ?  Parce que si la vraie période est 5, alors les
    périodes 10, 15, 20... donnent elles aussi des colonnes correctes (10 est un
    multiple de 5) : elles « marchent » aussi, mais ce n'est pas la vraie clef.

    Cas particulier de la période 1 : si le texte n'est pas brouillé du tout
    (simple code de César), l'indice dépasse déjà 90 % du meilleur dès p = 1, et
    la fonction renvoie 1.

    Arguments :
        texte (str) : le texte chiffré (que des lettres).
        maximum (int) : la plus grande période à essayer.
        proportion (float) : la fraction du meilleur indice à atteindre.

    Renvoie :
        int : la période trouvée (ou None si le texte est vide).

    Remarque pour ne pas se tromper d'interprétation : si tous les indices sont
    élevés (donc si le texte n'est pas brouillé du tout — c'est le cas d'un
    texte en clair, ou d'un simple code de César), la règle des 90 % renvoie une
    période quelconque. Ce n'est pas grave : dans ce cas, n'importe quelle clef
    de cette longueur déchiffre correctement le message, puisque le chiffrement
    n'était de toute façon qu'un seul décalage.

    Indication : `max(mon_dictionnaire.values())` donne le plus grand indice.
    """
    # ------------------------------------------------------------------
    # TODO A.3
    # ------------------------------------------------------------------
    raise NotImplementedError("A.3 periode_probable n'est pas encore écrite")


# ==========================================================================
# PARTIE B — LA MÉTHODE DE KASISKI
# ==========================================================================

def grammes_repetes(chiffre, taille):
    """B.1 — Repère les groupes de `taille` lettres qui se répètent.

    Arguments :
        chiffre (str) : le texte chiffré.
        taille (int) : la longueur des groupes cherchés (3 ou 4 en pratique).

    Renvoie :
        list : la liste des groupes (chaînes de `taille` caractères) qui
               apparaissent AU MOINS DEUX FOIS, chaque groupe une seule fois.

    Exemple :
        grammes_repetes("ABCIABCXABC", 3)  ->  ["ABC"]

    Indications :
        * parcourez les positions de 0 à len(chiffre) - taille et prenez à
          chaque fois le morceau `chiffre[debut:debut + taille]` ;
        * comptez-les : `comptes[morceau] = comptes.get(morceau, 0) + 1` ;
        * gardez ceux dont le compte est au moins 2 (écrivez-les une seule fois
          : parcourez les clefs du dictionnaire, puis triez la liste finale avec
          `sorted(...)` pour que le résultat soit toujours le même).
    """
    # ------------------------------------------------------------------
    # TODO B.1
    # ------------------------------------------------------------------
    raise NotImplementedError("B.1 grammes_repetes n'est pas encore écrite")


def kasiski_distances(chiffre, mot):
    """B.2 — Renvoie les distances entre les répétitions successives de `mot`.

    Arguments :
        chiffre (str) : le texte chiffré.
        mot (str) : le groupe de lettres dont on cherche les répétitions.

    Renvoie :
        list : la liste TRIÉE des distances, sans répétition.

    Exemple :
        Avec le texte "ABCXABCXXXABC", le mot "ABC" apparaît aux positions
        0, 4 et 11 ; les distances successives sont 4 (= 4 - 0) puis 7 (= 11 - 4),
        donc la fonction renvoie [4, 7].

    Indications :
        * trouvez toutes les positions où `mot` commence.  On peut les chercher
          avec une boucle et un test `chiffre[debut:debut + len(mot)] == mot` ;
        * calculez ensuite les différences entre positions consécutives ;
        * rangez-les dans une liste sans doublon (par exemple : si la distance
          n'est pas déjà dans la liste, ajoutez-la) et triez avec `sorted`.

    À quoi cela sert : si la clef a pour longueur p, alors deux répétitions du
    même groupe dans le texte clair se retrouvent décalées d'un nombre de
    lettres MULTIPLE de p (le même bout de texte clair est décalé par la même
    suite de lettres de clef).  Les distances sont donc, très souvent, des
    multiples de la période.
    """
    # ------------------------------------------------------------------
    # TODO B.2
    # ------------------------------------------------------------------
    raise NotImplementedError("B.2 kasiski_distances n'est pas encore écrite")


def diviseurs(nombre):
    """B.3 — Renvoie la liste triée des diviseurs de `nombre` (1 et lui-même compris).

    Exemples :
        diviseurs(12)  ->  [1, 2, 3, 4, 6, 12]
        diviseurs(7)   ->  [1, 7]
        diviseurs(1)   ->  [1]

    Indication : parcourez les entiers de 1 à `nombre` et gardez ceux qui
    divisent `nombre` (`nombre % d == 0`).

    À quoi cela sert : les diviseurs des distances trouvées en B.2 sont les
    périodes possibles.  On compte, pour chaque période possible, combien de
    fois elle divise une distance : la période qui revient le plus souvent est
    la bonne.
    """
    # ------------------------------------------------------------------
    # TODO B.3
    # ------------------------------------------------------------------
    raise NotImplementedError("B.3 diviseurs n'est pas encore écrite")


# ==========================================================================
# PARTIE C — CASSER LES DEUX MESSAGES INTERCEPTÉS
# ==========================================================================

def forcer_cesar_sur_colonne(colonne):
    """C.1 — Retrouve le décalage d'une colonne (comme au TP 2).

    Arguments :
        colonne (str) : les lettres d'une colonne.

    Renvoie :
        int : le décalage entre 0 et 25 (0 <=> lettre de clef A).

    Méthode : pour chaque décalage d de 0 à 25, déchiffrez la colonne (en
    reculant de d) et mesurez la distance de fréquences au français avec
    `distance_au_francais` ; gardez le décalage qui donne la plus petite
    distance.
    """
    # ------------------------------------------------------------------
    # TODO C.1
    # ------------------------------------------------------------------
    raise NotImplementedError("C.1 forcer_cesar_sur_colonne n'est pas encore écrite")


def forcer_vigenere(chiffre, periode):
    """C.2 — Casse le message complet, la période étant cette fois trouvée par vous.

    Arguments :
        chiffre (str) : le texte chiffré (que des lettres).
        periode (int) : la longueur de la clef.

    Renvoie :
        tuple : (cle, texte_clair)

    Étapes :
        1. morceaux = colonnes(chiffre, periode) ;
        2. pour chaque morceau, décalage = forcer_cesar_sur_colonne(morceau) ;
        3. la clef est la suite des lettres de clef correspondantes :
           décalage d -> ALPHABET[d] ;
        4. déchiffrez chaque colonne avec son décalage, puis recollez les
           colonnes dans l'ordre : à la position i du texte, on prend le
           caractère d'indice i // periode dans la colonne numéro i % periode.
    """
    # ------------------------------------------------------------------
    # TODO C.2
    # ------------------------------------------------------------------
    raise NotImplementedError("C.2 forcer_vigenere n'est pas encore écrite")


# ==========================================================================
# PARTIE D — LE CODE DE VIC (version simplifiée du cours)
# ==========================================================================
#
# Le VIC est décrit dans le cours ; voici la version simplifiée que nous
# étudions (tout est détaillé dans outils/reference.py) :
#
#   * le message est écrit avec les 10 lettres du damier : S E N A T R O I D L
#     (chacune vaut un chiffre : S = 0, E = 1, N = 2, A = 3, T = 4, R = 5,
#      O = 6, I = 7, D = 8, L = 9) ;
#   * on additionne la clef (une suite de chiffres), chiffre à chiffre, sans
#     retenue : c'est `ajouter_cle` ;
#   * on transposeles colonnes par blocs de 10 lettres : c'est `transposition` ;
#   * enfin, chaque chiffre devient une lettre grâce au damier `TABLEAU_VIC` :
#     on croise le chiffre (ligne) avec la POSITION du caractère dans son bloc
#     de 10 (colonne).
#
# Pour déchiffrer, on refait tout à l'envers.  C'est ce que vous allez écrire.

def caractere_vic(chiffre_message, chiffre_clef, position):
    """D.1 — Chiffre UN caractère : renvoie la lettre du damier.

    Arguments :
        chiffre_message (int) : le chiffre du message (0 à 9, après ajout de la
            clef et transposition).
        chiffre_clef (int) : le chiffre de la clef à cet endroit (0 à 9).
        position (int) : la position du caractère dans son bloc de 10 (0 à 9),
            qui donne la colonne du damier.

    Renvoie :
        str : la lettre du damier (une lettre de ALPHABET_VIC).

    Exemple :
        caractere_vic(0, 0, 0)  ->  "S"   (ligne (0+0) mod 10 = 0, colonne 0)

    Indications :
        * la ligne est `(chiffre_message + chiffre_clef) % 10` ;
        * la colonne est `position % 10` ;
        * la lettre est `TABLEAU_VIC[ligne][colonne]`, c'est-à-dire
          `lettre_vic(ligne, colonne)` (fonction fournie).
    """
    # ------------------------------------------------------------------
    # TODO D.1
    # ------------------------------------------------------------------
    raise NotImplementedError("D.1 caractere_vic n'est pas encore écrite")


def ligne_du_damier(lettre, position):
    """D.2 — Retrouve la LIGNE du damier à partir de la lettre et de la colonne.

    Arguments :
        lettre (str) : la lettre lue dans le message chiffré.
        position (int) : la position du caractère dans son bloc de 10 (la
            colonne du damier).

    Renvoie :
        int : le numéro de ligne (0 à 9).

    Pourquoi c'est possible : sur une même colonne du damier, les 10 lettres
    sont toutes différentes.  En regardant la colonne indiquée, il n'y a donc
    qu'une seule ligne possible.

    Indication : la fonction `deviner_ligne_vic(lettre, colonne)` fournie fait
    exactement ce travail (regardez son code dans outils/reference.py : c'est
    une simple boucle sur les 10 lignes).
    """
    # ------------------------------------------------------------------
    # TODO D.2
    # ------------------------------------------------------------------
    raise NotImplementedError("D.2 ligne_du_damier n'est pas encore écrite")


def chiffre_du_damier(lettre, chiffre_clef, position):
    """D.3 — Retrouve le chiffre du message (l'opération inverse de D.1).

    Arguments :
        lettre (str) : la lettre du message chiffré.
        chiffre_clef (int) : le chiffre de la clef à cet endroit.
        position (int) : la position du caractère dans son bloc de 10.

    Renvoie :
        int : le chiffre du message (0 à 9).

    Méthode :
        1. retrouvez la ligne du damier avec votre fonction D.2 ;
        2. le chiffre du message était `ligne - chiffre_clef`, modulo 10
           (car à l'aller, on avait ligne = message + clef, sans retenue).

    Exemple : si D.1 a transformé le chiffre 3 en lettre L avec le chiffre de
    clef 1 et la position 4, alors chiffre_du_damier("L", 1, 4) doit renvoyer 3.
    """
    # ------------------------------------------------------------------
    # TODO D.3
    # ------------------------------------------------------------------
    raise NotImplementedError("D.3 chiffre_du_damier n'est pas encore écrite")


def dechiffrer_message_vic(message_chiffre, cle, permutation=PERMUTATION_VIC):
    """D.4 — Déchiffre un message complet du VIC simplifié.

    Arguments :
        message_chiffre (str) : le message chiffré (lettres du damier).
        cle (str) : la clef, une suite de chiffres (ex. "5241").
        permutation (list) : la permutation des colonnes utilisée au chiffrement.

    Renvoie :
        str : le message en clair, en lettres du damier.

    Les quatre étapes À L'ENVERS (dans cet ordre) :
        1. pour chaque caractère, retrouvez le chiffre avec votre fonction D.3 :
           le chiffre de clef utilisé est celui de la position, en répétant la
           clef si elle est plus courte : `int(cle[position % len(cle)])` ;
        2. défaites la transposition : `transposition(chiffres,
           permutation_inverse(permutation))` ;
        3. retirez la clef : `retirer_cle(chiffres, cle)` ;
        4. convertissez les chiffres en lettres : `chiffres_en_message(chiffres)`.
    """
    # ------------------------------------------------------------------
    # TODO D.4
    # ------------------------------------------------------------------
    raise NotImplementedError("D.4 dechiffrer_message_vic n'est pas encore écrite")


# ==========================================================================
# PARTIE E — MESSAGES INTERCEPTÉS
# ==========================================================================
#
# MESSAGE_1 et MESSAGE_2 sont deux dépêches chiffrées par Vigenère.  Ici, la
# période est INCONNUE : utilisez votre travail des parties A, B et C.
#
# MESSAGE_VIC a été chiffré par le VIC simplifié, et l'on connaît sa clef
# (CLE_VIC) : il faut donc seulement votre fonction D.4 pour le lire.

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
    print("Damier du VIC :")
    from outils.reference import afficher_tableau_vic
    print(afficher_tableau_vic())
    print()
    print("Longueur du message 1 :", len(MESSAGE_1))
    print("Longueur du message 2 :", len(MESSAGE_2))
    print("Longueur du message VIC :", len(MESSAGE_VIC))
