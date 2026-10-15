"""==========================================================================
 TP 2 — CODES POLYALPHABÉTIQUES : VIGENÈRE ET SON ATTAQUE
 Chapitre 2 (fin) : « Codes polyalphabétiques » — Pascal Boyer,
 « Cryptographie 2013 ».

 Durée conseillée : 2 h.   À rendre : ce fichier complété.
==========================================================================

 ██  MODE D'EMPLOI  ██
==========================================================================

Comme au TP 1, chaque exercice suit toujours le même plan :

    > OBJECTIF             : ce que la fonction doit faire ;
    > POURQUOI (COURS)     : ce que cela vient faire dans le cours ;
    > CE QUE TU DOIS FAIRE : la recette, étape par étape ;
    > RAPPELS PYTHON       : l'instruction dont tu as besoin ;
    > À COMPLÉTER          : le squelette ; remplace les `...` par ce qui est
                             demandé dans le commentaire à côté ;
    > ✅ SOLUTION          : le code complet, en commentaire, à recopier pour
                             corriger (essaie d'abord par toi-même).

LA BOUCLE DE TRAVAIL
   1. écris une fonction dans ce fichier ;
   2. dans un terminal, ici, tape :

          python3 test_tp2_vigenere.py

   3. lis le bilan : [OK] = c'est juste ; [ÉCHEC] = l'explication de l'erreur ;
   4. recommence, puis passe à la fonction suivante.

Si tu as besoin de revoir les bases de Python (variables, chaînes, boucles,
listes, dictionnaires, fonctions), tout est rappelé dans le § A du fichier du
TP 1 (`seance1_permutation_substitution/tp1_permutation.py`) : ouvre-le et lis
les « DIX GESTES ».  Un point nouveau ici, très utile :

    L'INDICE ET LA VALEUR EN MÊME TEMPS
        for position, caractere in enumerate(texte):
            ... position vaut 0, 1, 2... et caractere la lettre correspondante.

LES DIX FONCTIONS À ÉCRIRE
--------------------------
   A.1  indice_de_la_lettre      A.2  decaler_lettre      A.3  vider_les_espaces
   B.1  vigenere_chiffrer        B.2  vigenere_dechiffrer
   C.1  forcer_cesar_sur_colonne C.2  colonnes            C.3  recoller
   C.4  forcer_vigenere
   D.1  cle_par_texte_connu
==========================================================================
"""

# ---------------------------------------------------------------------------
# LES IMPORTS (n'y touche pas)
# ---------------------------------------------------------------------------
# Ces trois lignes permettent à Python de trouver le dossier « outils » du
# dépôt, quel que soit l'endroit d'où tu lances la commande.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Les outils du professeur utilisés ici :
#   * ALPHABET      : la chaîne "ABC...Z" ;
#   * rehabiller(texte_modele, lettres) : replace des lettres dans la
#     présentation d'un texte (pour remettre les espaces et la ponctuation
#     après un déchiffrement lettre à lettre) — voir son code commenté ;
#   * vigenere_chiffrer_reference / vigenere_dechiffrer_reference : la version
#     du professeur, pour comparer avec la tienne (utilise-la pour tester !) ;
#   * distance_au_francais(texte) : écart aux fréquences du français.  PLUS LA
#     VALEUR EST PETITE, plus le texte ressemble à du français (outil de C.1).
from outils.reference import (
    ALPHABET,
    nettoyer,
    rehabiller,
    vigenere_chiffrer as vigenere_chiffrer_reference,
    vigenere_dechiffrer as vigenere_dechiffrer_reference,
)
from outils.texte_francais import distance_au_francais


# ###########################################################################
#
#  RAPPELS DU COURS — À LIRE AVANT DE COMMENCER (c'est le cœur de la séance)
#
# ###########################################################################
#
# 1) POURQUOI CÉSAR NE SUFFIT PAS
#    Dans un code de substitution simple, la MÊME lettre du clair devient
#    TOUJOURS la même lettre du chiffré.  Les fréquences sont donc conservées :
#    le E français (15 % du texte) reste la lettre la plus fréquente après
#    chiffrement.  L'analyse de fréquences casse le code en quelques minutes.
#
# 2) L'IDÉE DE VIGENÈRE (XVIe siècle)
#    On n'utilise plus une seule substitution, mais PLUSIEURS : une par lettre
#    de la clef.  La lettre de clef employée change à chaque lettre du message :
#
#        message :  B  O  N  J  O  U  R         (on chiffre)
#        clef    :  C  L  E  C  L  E  C         (répétée autant que nécessaire)
#        rangs   :  1  2  3  1  2  3  1
#        décalage:  B+1=D, O+2=Q, N+3=Q, J+1=K, O+2=Q, U+3=X, R+1=S
#        chiffré :  D  Q  Q  K  Q  X  S
#
#    La même lettre du clair (ici le O, deux fois) peut donner deux lettres
#    différentes (Q et Q... ou autre chose selon la position) : les fréquences
#    globales deviennent inutilisables.  On a surnommé Vigenère « le chiffre
#    indéchiffrable ».  C'était excessif, et ton travail de la partie C le
#    montrera.
#
# 3) LA FAILLE, TOUJOURS LA MÊME
#    La clef se RÉPÈTE.  Si elle fait 5 lettres, alors les positions 0, 5, 10,
#    15... sont toutes décalées de la MÊME quantité.  En découpant le message en
#    5 colonnes, chaque colonne redevient un simple code de César... et l'on sait
#    casser César !
#
# 4) LA CONVENTION DES ESPACES (elle sert à tous les tests)
#    Les espaces et la ponctuation sont recopiés tels quels et NE CONSOMMENT PAS
#    de lettre de clef.  Autrement dit, dans la phrase « BONJOUR LE MONDE », le
#    J se chiffre avec la 4e lettre de la clef, et le L (après l'espace) avec la
#    5e : les espaces ne comptent pas.
#
# ###########################################################################


# ==========================================================================
# PARTIE A — PETITS OUTILS
# ==========================================================================

def indice_de_la_lettre(lettre):
    """A.1 — OBJECTIF : donner le rang d'une lettre dans l'alphabet.

    POURQUOI (COURS) : toute la cryptographie de ce chapitre s'écrit avec des
    nombres : A vaut 0, B vaut 1, ..., Z vaut 25.  Chiffrer, c'est additionner
    des rangs ; déchiffrer, c'est en soustraire.  Cette fonction fait la
    conversion lettre -> nombre.

    CE QUE TU DOIS FAIRE :
        utilise la méthode `.index()` de la chaîne ALPHABET :
            ALPHABET.index("C")  vaut 2
        Pense à mettre la lettre en majuscules d'abord : on veut accepter
        aussi bien "m" que "M".

    RAPPELS PYTHON :
        * `ALPHABET.index(quelque_chose)` cherche la position de cette chose
          dans la chaîne : le A est en position 0, le B en position 1, etc. ;
        * `lettre.upper()` met une lettre en majuscule.

    EXEMPLES (ce que les tests vérifient) :
        indice_de_la_lettre("A")  ->  0
        indice_de_la_lettre("M")  ->  12
        indice_de_la_lettre("z")  ->  25
    """
    # --- À COMPLÉTER ---
    return ALPHABET.index(...)                          # cherche le rang de la lettre

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     return ALPHABET.index(lettre.upper())
    # ----------------------------------------------------------------------


def decaler_lettre(lettre, decalage):
    """A.2 — OBJECTIF : décaler une lettre de `decalage` rangs dans l'alphabet,
    en revenant au début après Z (et en reculant correctement si le décalage est
    négatif).

    POURQUOI (COURS) : c'est LE geste du chiffrement par décalage.  Décaler de
    3 : A devient D ; décaler de -3 : D redevient A.  Pour que Z + 1 donne bien
    A, on utilise le reste de la division par 26 : c'est le « modulo 26 » du
    cours (n devient (n + k) mod 26).

    CE QUE TU DOIS FAIRE :
        étape 1 : trouve le rang de la lettre avec ta fonction A.1 ;
        étape 2 : ajoute le décalage puis prends le reste de la division par 26 :
                      (rang + decalage) % 26
        étape 3 : renvoie la lettre de ce nouveau rang : ALPHABET[nouveau rang].

    RAPPELS PYTHON :
        * `%` donne le reste : `(3 + 1) % 26` vaut 4 ; `(25 + 1) % 26` vaut 0
          (le Z décalé d'un cran devient donc le A) ;
        * avec un décalage négatif, le % de Python donne toujours un résultat
          entre 0 et 25 : `(0 - 1) % 26` vaut 25, donc le A reculé d'un cran
          devient le Z.  C'est exactement ce qu'on veut.

    EXEMPLES (ce que les tests vérifient) :
        decaler_lettre("A", 3)   ->  "D"
        decaler_lettre("Z", 1)   ->  "A"
        decaler_lettre("A", -1)  ->  "Z"
        decaler_lettre("B", -1)  ->  "A"
        decaler_lettre("a", 1)   ->  "B"    (les minuscules sont acceptées)
    """
    # --- À COMPLÉTER ---
    rang = indice_de_la_lettre(...)                     # le rang de la lettre
    nouveau_rang = (rang + ...) % 26                    # on décale, modulo 26
    return ALPHABET[...]                                # la lettre du nouveau rang

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     rang = indice_de_la_lettre(lettre)
    #     nouveau_rang = (rang + decalage) % 26
    #     return ALPHABET[nouveau_rang]
    # ----------------------------------------------------------------------


def vider_les_espaces(texte):
    """A.3 — OBJECTIF : ne garder que les lettres de A à Z, en majuscules.

    POURQUOI (COURS) : pour attaquer un message, il faut le manipuler « en
    colonnes ».  Or les espaces et la ponctuation ne font pas partie du
    chiffrement (ils ne consomment pas de lettre de clef) : on les met donc de
    côté le temps des calculs.  On les remettra à la fin avec `rehabiller`.

    CE QUE TU DOIS FAIRE :
        c'est exactement la fonction `nettoyer_simple` du TP 1 !  Si tu l'as
        déjà écrite, recopie-la ici (c'est normal : on réutilise son travail) ;
        sinon, la recette est la même :
            étape 1 : prépare une chaîne vide ;
            étape 2 : parcours le texte en majuscules ;
            étape 3 : si le caractère est entre "A" et "Z", ajoute-le ;
            étape 4 : renvoie le résultat.

    RAPPELS PYTHON : voir le TP 1, geste 2.
        * `texte.upper()` ; `for caractere in ...:` ; `resultat += caractere` ;
        * `if "A" <= caractere <= "Z":` (mais attention : cette comparaison
          n'accepte que les majuscules non accentuées, d'où le `.upper()`).

    EXEMPLES (ce que les tests vérifient) :
        vider_les_espaces("Bonjour, l'ami !")  ->  "BONJOURLAMI"
        vider_les_espaces("DEJA PROPRE")       ->  "DEJAPROPRE"
    """
    # --- À COMPLÉTER ---
    resultat = ...                                      # une chaîne vide
    for caractere in ...:                               # parcours texte.upper()
        if ...:                                         # teste "A" <= c <= "Z"
            resultat += ...                             # ajoute la lettre
    return ...                                          # renvoie le résultat

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     resultat = ""
    #     for caractere in texte.upper():
    #         if "A" <= caractere <= "Z":
    #             resultat += caractere
    #     return resultat
    # ----------------------------------------------------------------------


# ==========================================================================
# PARTIE B — LE CODE DE VIGENÈRE
# ==========================================================================

def vigenere_chiffrer(texte, cle):
    """B.1 — OBJECTIF : chiffrer un texte avec la clef `cle` (par exemple "CLE").

    POURQUOI (COURS) : c'est la mise en œuvre du chiffre de Vigenère : la
    lettre de clef qui décale le message change à chaque lettre, et la clef se
    répète si elle est plus courte que le message.

    LE POINT DÉLICAT (lis bien, c'est l'erreur numéro 1 des TP) :
        il faut COMPTER LES LETTRES.  La variable `rang_clef` retient combien de
        lettres ont déjà été chiffrées :
            * quand on rencontre une LETTRE du message, on utilise la lettre de
              clef numéro `rang_clef` puis on fait `rang_clef += 1` ;
            * quand on rencontre un ESPACE ou une virgule, on recopie le
              caractère et `rang_clef` NE CHANGE PAS.
        Utilise le modulo pour faire tourner la clef en boucle :
            cle[rang_clef % len(cle)]
        Avec la clef "CLE" (3 lettres) et rang_clef = 0,1,2,3,4,5..., cela donne
        les lettres C, L, E, C, L, E...

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare `chiffre = ""` (le résultat) et `rang_clef = 0` ;
        étape 2 : parcours le texte mis en majuscules ;
        étape 3 : si le caractère est une lettre :
                    * prends la lettre de clef : `cle[rang_clef % len(cle)]` ;
                    * son décalage est `ALPHABET.index(lettre_de_clef)` ;
                    * décale le caractère avec ta fonction A.2 : c'est
                      `decaler_lettre(caractere, decalage)` ;
                    * ajoute la lettre obtenue à `chiffre` ;
                    * fais `rang_clef += 1` (une lettre de plus consommée) ;
                  sinon : recopie le caractère tel quel, SANS toucher à
                  `rang_clef` ;
        étape 4 : renvoie `chiffre`.

    RAPPELS PYTHON :
        * `cle[rang_clef % len(cle)]` : le % ramène l'indice dans les limites de
          la clef (0, 1, 2, 0, 1, 2...) ;
        * `+= 1` augmente une variable de 1 ;
        * tu peux appeler tes fonctions : `decaler_lettre(...)`.

    EXEMPLES (ce que les tests vérifient — compare avec la version du
    professeur, `vigenere_chiffrer_reference`, en cas de doute) :
        vigenere_chiffrer("BONJOUR", "CLE")           ->  "DZRLZYT"
        vigenere_chiffrer("BONJOUR LE MONDE", "CLE")  ->  "DZRLZYT WI OZRFP"
    """
    # --- À COMPLÉTER ---
    chiffre = ...                                       # une chaîne vide
    rang_clef = ...                                     # au départ, 0 lettres consommées
    for caractere in texte.upper():                     # parcours le message
        if "A" <= caractere <= "Z":                     # est-ce une lettre ?
            lettre_de_clef = cle[rang_clef % len(...)]  # la lettre de clef du moment
            decalage = ALPHABET.index(...)              # son décalage
            chiffre += decaler_lettre(...)              # on décale la lettre
            rang_clef += ...                            # une lettre de plus
        else:
            chiffre += ...                              # recopie sans consommer de clef
    return ...                                          # renvoie le texte chiffré

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     chiffre = ""
    #     rang_clef = 0
    #     for caractere in texte.upper():
    #         if "A" <= caractere <= "Z":
    #             lettre_de_clef = cle[rang_clef % len(cle)]
    #             decalage = ALPHABET.index(lettre_de_clef)
    #             chiffre += decaler_lettre(caractere, decalage)
    #             rang_clef += 1
    #         else:
    #             chiffre += caractere
    #     return chiffre
    # ----------------------------------------------------------------------


def vigenere_dechiffrer(texte_chiffre, cle):
    """B.2 — OBJECTIF : déchiffrer un message chiffré par ta fonction B.1.

    POURQUOI (COURS) : le déchiffrement, c'est la même opération avec le
    décalage opposé.  Le cours insiste sur la propriété fondamentale :
        d_k(e_k(x)) = x
    (si l'on chiffre puis déchiffre avec la même clef, on retrouve le message).

    CE QUE TU DOIS FAIRE :
        c'est exactement la recette de B.1, avec UN SEUL changement : au lieu de
        `decaler_lettre(caractere, decalage)`, on écrit
        `decaler_lettre(caractere, -decalage)` (le signe moins !).
        Tu peux recopier ta fonction B.1 et changer ce signe : c'est autorisé,
        et c'est même la façon la plus sûre de ne pas se tromper.

    RAPPELS PYTHON :
        * `-decalage` est l'opposé du décalage : si decalage vaut 3, on recule
          de 3 ;
        * `decaler_lettre` gère déjà les décalages négatifs grâce au modulo
          (revoir l'exercice A.2).

    EXEMPLE (ce que les tests vérifient) :
        vigenere_dechiffrer("DZRLZYT WI OZRFP", "CLE")  ->  "BONJOUR LE MONDE"
        Et pour toute clef : vigenere_dechiffrer(vigenere_chiffrer(x, k), k) = x
    """
    # --- À COMPLÉTER ---
    clair = ...                                         # une chaîne vide
    rang_clef = ...                                     # au départ, 0
    for caractere in texte_chiffre.upper():             # parcours le texte chiffré
        if "A" <= caractere <= "Z":
            lettre_de_clef = cle[rang_clef % len(...)]  # la lettre de clef du moment
            decalage = ALPHABET.index(...)              # son décalage
            clair += decaler_lettre(caractere, ...)     # ATTENTION AU SIGNE !
            rang_clef += ...                            # une lettre de plus
        else:
            clair += ...                                # recopie sans consommer de clef
    return ...                                          # renvoie le texte clair

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     clair = ""
    #     rang_clef = 0
    #     for caractere in texte_chiffre.upper():
    #         if "A" <= caractere <= "Z":
    #             lettre_de_clef = cle[rang_clef % len(cle)]
    #             decalage = ALPHABET.index(lettre_de_clef)
    #             clair += decaler_lettre(caractere, -decalage)
    #             rang_clef += 1
    #         else:
    #             clair += caractere
    #     return clair
    # ----------------------------------------------------------------------


# ==========================================================================
# PARTIE C — L'ATTAQUE DE VIGENÈRE, ÉTAPE PAR ÉTAPE
# ==========================================================================
#
# RAPPEL DE L'IDÉE (c'est toute la cryptanalyse de Vigenère) :
#
#   La clef se répète.  Si elle fait 4 lettres, alors les caractères aux
#   positions 0, 4, 8, 12... sont décalés de la MÊME quantité.  En rangeant le
#   message en 4 colonnes, chaque colonne est un simple code de César, et l'on
#   sait casser César depuis le TP 1 (en comparant les fréquences au français).
#
#   Trouver la période (le nombre de colonnes) est l'objet du TP 3.  Ici, la
#   période vous est DONNÉE : c'est ce que vous faites en classe pour comprendre
#   l'attaque sans se battre avec la partie difficile.


def forcer_cesar_sur_colonne(colonne):
    """C.1 — OBJECTIF : retrouver le décalage d'UNE colonne (donc UNE lettre de
    la clef).

    POURQUOI (COURS) : chaque colonne est un texte français chiffré par un
    décalage constant.  On essaie donc les 26 décalages possibles, on déchiffre
    chaque fois, et l'on garde celui qui donne le texte le plus proche du
    français.  C'est l'attaque par analyse de fréquences du TP 1, appliquée à
    une colonne.

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare deux boîtes :
                      meilleur_decalage = 0
                      meilleure_distance = None
        étape 2 : essaie les 26 décalages : `for decalage in range(26):`
        étape 3 : dans la boucle, construis la version déchiffrée de la colonne :
                      essai = ""
                      for lettre in colonne:
                          essai += decaler_lettre(lettre, -decalage)
        étape 4 : mesure l'écart au français :
                      distance = distance_au_francais(essai)
        étape 5 : garde le décalage qui donne la plus PETITE distance (comme
                  dans l'exercice C.3 du TP 1) ;
        étape 6 : renvoie `meilleur_decalage` (un nombre entre 0 et 25).

    COMMENT LIRE LE RÉSULTAT : le décalage 0 correspond à la lettre de clef A,
        1 à B, 2 à C, ..., 25 à Z.  On convertira en lettre dans C.4.

    RAPPELS PYTHON :
        * deux boucles imbriquées : la petite (les lettres de la colonne)
          s'exécute entièrement à chaque tour de la grande (les 26 décalages) ;
        * construire `essai` avec `+=` comme d'habitude ;
        * `distance < meilleure_distance` : on cherche la PLUS PETITE distance.

    EXEMPLE : si la colonne a été chiffrée avec la lettre de clef D (décalage 3),
        forcer_cesar_sur_colonne(colonne)  ->  3
    """
    # --- À COMPLÉTER ---
    meilleur_decalage = 0
    meilleure_distance = ...
    for decalage in range(...):                         # les 26 décalages : 0 à 25
        essai = ...                                     # une chaîne vide
        for lettre in colonne:                          # parcours la colonne
            essai += decaler_lettre(lettre, ...)        # recule de `decalage`
        distance = distance_au_francais(...)            # l'écart au français
        if meilleure_distance is None or distance < ...:
            meilleur_decalage = ...
            meilleure_distance = ...
    return ...                                          # renvoie le décalage trouvé

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     meilleur_decalage = 0
    #     meilleure_distance = None
    #     for decalage in range(26):
    #         essai = ""
    #         for lettre in colonne:
    #             essai += decaler_lettre(lettre, -decalage)
    #         distance = distance_au_francais(essai)
    #         if meilleure_distance is None or distance < meilleure_distance:
    #             meilleur_decalage = decalage
    #             meilleure_distance = distance
    #     return meilleur_decalage
    # ----------------------------------------------------------------------


def colonnes(texte, periode):
    """C.2 — OBJECTIF : ranger le texte en `periode` colonnes.

    POURQUOI (COURS) : c'est la manipulation qui transforme le problème
    « Vigenère » (difficile) en `periode` problèmes « César » (faciles).  Voici
    ce qui se passe, avec la période 3 et le texte ABCDEFGHIJ :

        colonne 0 : A, D, G, J   (positions 0, 3, 6, 9)
        colonne 1 : B, E, H      (positions 1, 4, 7)
        colonne 2 : C, F, I      (positions 2, 5, 8)
        résultat  : ["ADGJ", "BEH", "CFI"]

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare une liste de `periode` chaînes vides :
                      morceaux = []
                      for i in range(periode):
                          morceaux.append("")
        étape 2 : parcours le texte avec les positions :
                      for position, caractere in enumerate(texte):
        étape 3 : range le caractère dans la bonne colonne :
                      colonne = position % periode
                      morceaux[colonne] += caractere
        étape 4 : renvoie `morceaux`.

    RAPPELS PYTHON :
        * `enumerate(texte)` fournit DEUX choses à chaque tour : la position
          (0, 1, 2...) et le caractère ;
        * `position % periode` donne le numéro de colonne : 0, 1, 2, 0, 1, 2...
        * `morceaux[colonne] += caractere` ajoute le caractère à LA colonne
          voulue (on modifie un élément de la liste, pas la liste entière).

    EXEMPLES (ce que les tests vérifient) :
        colonnes("ABCDEFGHIJ", 3)  ->  ["ADGJ", "BEH", "CFI"]
        colonnes("ABCDEF", 2)      ->  ["ACE", "BDF"]
    """
    # --- À COMPLÉTER ---
    morceaux = []                                       # la liste des colonnes
    for rang in range(...):                             # autant que la période
        morceaux.append(...)                            # une colonne vide : ""
    for position, caractere in enumerate(...):          # position ET caractère
        colonne = position % ...                        # numéro de la colonne
        morceaux[colonne] += ...                        # range le caractère
    return ...                                          # renvoie les colonnes

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     morceaux = []
    #     for rang in range(periode):
    #         morceaux.append("")
    #     for position, caractere in enumerate(texte):
    #         colonne = position % periode
    #         morceaux[colonne] += caractere
    #     return morceaux
    # ----------------------------------------------------------------------


def recoller(morceaux, periode):
    """C.3 — OBJECTIF : faire l'opération inverse de C.2 : reconstruire le texte
    en entrelaçant les colonnes.

    POURQUOI (COURS) : après avoir déchiffré chaque colonne séparément, il faut
    remettre les lettres dans le bon ordre pour lire le message.  C'est le geste
    « on relit le tableau ligne par ligne » (au lieu de colonne par colonne).

    COMMENT FAIRE (l'idée à comprendre) :
        on veut reconstruire la position 0, 1, 2, 3, ... du texte.
        La position `i` vient de la colonne numéro `i % periode`, et c'est le
        `i // periode`-ième caractère de cette colonne.  Exemple avec 3 colonnes
        ["ADGJ", "BEH", "CFI"] :

            i = 0  -> colonne 0 % 3 = 0, rang 0 // 3 = 0  -> morceaux[0][0] = "A"
            i = 1  -> colonne 1,      rang 0              -> morceaux[1][0] = "B"
            i = 2  -> colonne 2,      rang 0              -> morceaux[2][0] = "C"
            i = 3  -> colonne 0,      rang 1              -> morceaux[0][1] = "D"

    CE QUE TU DOIS FAIRE :
        étape 1 : calcule la longueur totale : la somme des longueurs des
                  morceaux.  Tu peux faire :
                      total = 0
                      for morceau in morceaux:
                          total += len(morceau)
        étape 2 : prépare une chaîne vide `texte = ""` ;
        étape 3 : parcours les positions de 0 à total - 1 :
                      for position in range(total):
        étape 4 : ajoute le bon caractère :
                      colonne = position % periode
                      rang_dans_la_colonne = position // periode
                      texte += morceaux[colonne][rang_dans_la_colonne]
        étape 5 : renvoie `texte`.

    RAPPELS PYTHON :
        * `//` (division entière) : 7 // 3 vaut 2 ; `%` (reste) : 7 % 3 vaut 1 ;
        * `morceaux[colonne][rang]` : deux crochets, on prend un caractère DANS
          une chaîne QUI EST DANS une liste.

    EXEMPLES (ce que les tests vérifient) :
        recoller(["ADGJ", "BEH", "CFI"], 3)  ->  "ABCDEFGHIJ"
        Et pour tout texte : recoller(colonnes(texte, p), p) = texte.
    """
    # --- À COMPLÉTER ---
    total = 0                                           # longueur totale
    for morceau in morceaux:
        total += ...                                    # ajoute sa longueur
    texte = ...                                         # une chaîne vide
    for position in range(...):                         # de 0 à total - 1
        colonne = position % ...                        # numéro de la colonne
        rang_dans_la_colonne = position // ...          # combien de lettres déjà prises
        texte += morceaux[colonne][...]                 # le bon caractère
    return ...                                          # renvoie le texte recollé

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     total = 0
    #     for morceau in morceaux:
    #         total += len(morceau)
    #     texte = ""
    #     for position in range(total):
    #         colonne = position % periode
    #         rang_dans_la_colonne = position // periode
    #         texte += morceaux[colonne][rang_dans_la_colonne]
    #     return texte
    # ----------------------------------------------------------------------


def forcer_vigenere(texte_chiffre, periode):
    """C.4 — OBJECTIF : casser un message de Vigenère dont on connaît la période.

    C'EST L'ATTAQUE COMPLÈTE DU COURS.  Elle s'enchaîne en six étapes, et tu as
    déjà écrit toutes les briques :

        étape 1 : enlève les espaces et la ponctuation (fonction A.3), car ils
                  ne font pas partie du chiffrement ;
        étape 2 : range les lettres en `periode` colonnes (fonction C.2) ;
        étape 3 : pour chaque colonne, trouve son décalage (fonction C.1) ;
        étape 4 : la clef est la suite des lettres correspondantes : décalage 0
                  -> A, 1 -> B, ... On la construit avec :
                      cle = ""
                      for decalage in decalages:
                          cle += ALPHABET[decalage]
        étape 5 : déchiffre chaque colonne avec son décalage (avec
                  `decaler_lettre(lettre, -decalage)`), puis recolle les
                  colonnes avec la fonction C.3 : tu obtiens les lettres du
                  message clair, sans espaces ;
        étape 6 : remets la présentation d'origine (espaces, ponctuation) avec
                  l'outil du professeur :
                      clair = rehabiller(texte_chiffre, lettres_claires)
        étape 7 : renvoie les DEUX résultats : `return (cle, clair)`.

    RAPPELS PYTHON :
        * une liste peut contenir des listes ou des chaînes : construis une
          liste `decalages` avec `decalages.append(...)` ;
        * pour parcourir des colonnes ET leurs décalages en même temps :
              for rang in range(periode):
                  morceau = morceaux[rang]
                  decalage = decalages[rang]
        * `return (cle, clair)` renvoie un couple ; on le lira ensuite :
              cle, clair = forcer_vigenere(message, periode)

    EXEMPLE D'UTILISATION (ta récompense, avec les messages interceptés plus bas) :
        cle, clair = forcer_vigenere(MESSAGE_VIGENERE_1, PERIODE_1)
        print(cle, clair[:80])

    CONSEIL DE MISE AU POINT : les tests de C.1, C.2 et C.3 doivent passer AVANT
    d'attaquer C.4.  Si C.4 échoue, ajoute :
        print(cle)          juste avant le return
    et regarde la clef trouvée : si elle ressemble à la vraie clef sans être
    exactement elle, c'est qu'une colonne a été mal reconnue (message trop court
    ou colonne trop pauvre en lettres) — recommence avec un message plus long.
    """
    # --- À COMPLÉTER ---
    lettres_chiffrees = vider_les_espaces(...)          # étape 1
    morceaux = colonnes(lettres_chiffrees, ...)         # étape 2

    decalages = []                                      # un décalage par colonne
    cle = ""                                            # la clef reconstruite
    for rang in range(periode):
        decalage = forcer_cesar_sur_colonne(...)        # étape 3 : le décalage
        decalages.append(...)                           # on le garde
        cle += ALPHABET[...]                            # étape 4 : en lettre de clef

    morceaux_clairs = []                                # les colonnes déchiffrées
    for rang in range(periode):
        colonne_claire = ""                             # une chaîne vide
        for lettre in morceaux[rang]:                   # chaque lettre de la colonne
            colonne_claire += decaler_lettre(lettre, -...)   # étape 5
        morceaux_clairs.append(...)                     # on garde la colonne claire

    lettres_claires = recoller(..., periode)            # étape 5 (suite)
    clair = rehabiller(...)                             # étape 6 : espaces d'origine
    return (... , ...)                                  # étape 7 : la clef ET le texte

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     lettres_chiffrees = vider_les_espaces(texte_chiffre)
    #     morceaux = colonnes(lettres_chiffrees, periode)
    #
    #     decalages = []
    #     cle = ""
    #     for rang in range(periode):
    #         decalage = forcer_cesar_sur_colonne(morceaux[rang])
    #         decalages.append(decalage)
    #         cle += ALPHABET[decalage]
    #
    #     morceaux_clairs = []
    #     for rang in range(periode):
    #         colonne_claire = ""
    #         for lettre in morceaux[rang]:
    #             colonne_claire += decaler_lettre(lettre, -decalages[rang])
    #         morceaux_clairs.append(colonne_claire)
    #
    #     lettres_claires = recoller(morceaux_clairs, periode)
    #     clair = rehabiller(texte_chiffre, lettres_claires)
    #     return (cle, clair)
    # ----------------------------------------------------------------------


# ==========================================================================
# PARTIE D — L'ATTAQUE PAR TEXTE CONNU
# ==========================================================================
#
# Si l'on met la main sur le message en clair (un rapport, un communiqué, un
# télégramme intercepté deux fois), l'affaire est entendue : on compare les deux
# textes lettre à lettre et l'on retrouve la clef.  C'est ainsi que Kasiski,
# officier prussien, a commencé à casser Vigenère au XIXe siècle ; c'est
# aujourd'hui encore la base des attaques « à texte clair connu ».

def cle_par_texte_connu(message_clair, message_chiffre):
    """D.1 — OBJECTIF : retrouver la clef quand on connaît à la fois le texte
    clair et le texte chiffré correspondant.

    POURQUOI (COURS) : c'est l'attaque la plus simple et la plus ancienne.
    Comme on sait que chiffré = clair + clef (position par position), on a :
        clef = chiffré - clair   (modulo 26)

    CE QUE TU DOIS FAIRE :
        étape 1 : enlève espaces et ponctuation des DEUX textes (fonction A.3) :
                      clair = vider_les_espaces(message_clair)
                      chiffre = vider_les_espaces(message_chiffre)
        étape 2 : pour chaque position, calcule le décalage :
                      decalage = (indice_de_la_lettre(chiffre[position])
                                  - indice_de_la_lettre(clair[position])) % 26
                  et transforme-le en lettre de clef : ALPHABET[decalage].
                  Tu obtiens une suite longue, par exemple "CLECLECLECLE".
        étape 3 : cette suite répète la clef.  Cherche la plus PETITE période p
                  telle que `suite[position] == suite[position + p]` pour toutes
                  les positions.  Renvoie les p premières lettres.
                  (C'est le même problème que l'exercice B.1 du TP 1 : une
                  boucle `for p in range(1, len(suite) + 1)` et un test pour
                  toutes les positions.)

    RAPPELS PYTHON :
        * `len(suite)` : la longueur de la suite de lettres ;
        * pour tester si TOUTES les positions conviennent, on peut utiliser :
              tout_bon = True
              for position in range(len(suite) - p):
                  if suite[position] != suite[position + p]:
                      tout_bon = False
          puis `if tout_bon: return suite[:p]` ;
        * `suite[:p]` prend les p premières lettres.

    EXEMPLES (ce que les tests vérifient) :
        clair_chiffre_dans_le_code_de_la_fonction :
        cle_par_texte_connu("BONJOUR", "DZRLZYT")       ->  "CLE"
        cle_par_texte_connu("LE MESSAGE, ARRIVE !", chiffre_avec_la_clef_CLE)
                                                        ->  "CLE"

    LIMITE À CONNAÎTRE : on ne retrouve que les lettres de clef qui ont
    réellement servi.  Si la clef est plus longue que le texte connu, on ne peut
    pas la retrouver en entier — c'est une limite de l'attaque, pas de ton code.
    """
    # --- À COMPLÉTER ---
    clair = vider_les_espaces(...)                      # étape 1
    chiffre = vider_les_espaces(...)                    # étape 1 (suite)

    suite = ""                                          # la clef répétée
    for position in range(len(clair)):                  # étape 2
        decalage = (indice_de_la_lettre(chiffre[position])
                    - indice_de_la_lettre(clair[position])) % 26
        suite += ALPHABET[...]                          # la lettre de clef

    for periode in range(1, len(suite) + ...):          # étape 3 : la plus petite période
        tout_bon = ...                                  # au départ, True
        for position in range(len(suite) - periode):
            if suite[position] != suite[position + ...]:
                tout_bon = ...                          # ce n'est pas la bonne période
        if tout_bon:
            return suite[...]                           # les `periode` premières lettres
    return ...                                          # cas de secours : renvoie la suite

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     clair = vider_les_espaces(message_clair)
    #     chiffre = vider_les_espaces(message_chiffre)
    #
    #     suite = ""
    #     for position in range(len(clair)):
    #         decalage = (indice_de_la_lettre(chiffre[position])
    #                     - indice_de_la_lettre(clair[position])) % 26
    #         suite += ALPHABET[decalage]
    #
    #     for periode in range(1, len(suite) + 1):
    #         tout_bon = True
    #         for position in range(len(suite) - periode):
    #             if suite[position] != suite[position + periode]:
    #                 tout_bon = False
    #         if tout_bon:
    #             return suite[:periode]
    #     return suite
    # ----------------------------------------------------------------------


# ==========================================================================
# PARTIE E — DEUX MESSAGES INTERCEPTÉS À DÉCRYPTER
# ==========================================================================
#
# Voici deux dépêches chiffrées par Vigenère.  Bonne nouvelle : on connaît la
# période de chacune (elle a été obtenue par des agents restés anonymes).
# À toi de retrouver la clef et le texte, avec ta fonction C.4.
#
# Dans l'interpréteur Python :
#     >>> from tp2_vigenere import *
#     >>> cle, clair = forcer_vigenere(MESSAGE_VIGENERE_1, PERIODE_1)
#     >>> print(cle)
#     >>> print(clair)
#
# Ensuite, essaie ton attaque D.1 : tu connais maintenant le texte clair de la
# dépêche 1 !  Vérifie que cle_par_texte_connu(texte_connu, MESSAGE_VIGENERE_1)
# redonne la même clef.

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


# ###########################################################################
#
#  EXPÉRIENCES À FAIRE DANS L'INTERPRÉTEUR (la partie « cryptanalyse »)
#
# ###########################################################################
#
# EXPÉRIENCE 1 — Vigenère fait-il vraiment disparaître les fréquences ?
#     >>> from tp2_vigenere import *
#     >>> from common import scytale_chiffrer          (ou outils.reference)
#     >>> from outils.reference import cesar_chiffrer
#     >>> from outils.texte_francais import barres, frequences
#     >>> clair = "LE MESSAGE ARRIVE CE SOIR A DIX HEURES DEVANT LA PORTE"
#     >>> print(barres(frequences(clair)))                 (français : E en tête)
#     >>> print(barres(frequences(cesar_chiffrer(clair, 7))))   (même forme, décalée)
#     >>> print(barres(frequences(vigenere_chiffrer(clair, "SECRET"))))
#     Observe : avec Vigenère, plus de E dominant !  Les lettres se ressemblent.
#     C'est pour cela que l'analyse de fréquences globale échoue.
#
# EXPÉRIENCE 2 — mais chaque colonne, elle, reste du français !
#     >>> lettres = vider_les_espaces(chiffre)
#     >>> for rang in range(6):
#     ...     print(rang, barres(frequences(lettres[rang::6]))[:60])
#     (lettres[rang::6] prend un caractère sur six, à partir du rang : c'est la
#     colonne du rang.  Le découpage [a:b:c] s'écrit a=début, b=fin, c=pas.)
#     Chaque colonne retrouve l'allure du français : c'est toute l'astuce de C.1.
#
# EXPÉRIENCE 3 — la clef est très courte à trouver
#     >>> for decalage in range(26):
#     ...     essai = "".join(decaler_lettre(c, -decalage) for c in colonnes(...)[0])
#     ...     print(decalage, round(distance_au_francais(essai), 1))
#     La plus petite distance donne le décalage de la première lettre de clef.
#
# ###########################################################################
#
#  QUESTIONS DE RAPPORT (à rédiger et à rendre avec le fichier)
#
# ###########################################################################
#
# QUESTION 1. Pourquoi l'analyse de fréquences globale échoue-t-elle sur
# Vigenère ?  Cite l'expérience 1.
#
# QUESTION 2. Pourquoi fonctionne-t-elle « par colonne » ?  Cite l'expérience 2.
#
# QUESTION 3. Combien y a-t-il de clefs de 5 lettres ?  Et de 8 lettres ?
# (Indice : 26 possibilités par lettre.)  Compare ce nombre au coût de l'attaque
# par colonnes : 26 essais par colonne, donc 26 x période essais au total.
#
# QUESTION 4. Deux messages sont chiffrés avec la même clef.  Que peut-on en
# déduire ?  (Indice : compare les positions où les deux textes chiffrés ont la
# même lettre ; c'est l'attaque « de deux messages », celle qui a fait tomber
# Enigma par la répétition de la clef de message.)
#
# QUESTION 5. Quelle est la faiblesse structurelle de Vigenère ?  Que faudrait-il
# changer pour la corriger, et pourquoi est-ce encore insuffisant ?
#
# QUESTION 6. Ton attaque D.1 (texte connu) a-t-elle besoin de la période ?
# Explique pourquoi, et dans quel cas cette attaque est la plus efficace.
#


if __name__ == "__main__":
    # Cette partie s'exécute quand on lance :   python3 tp2_vigenere.py

    def _essai(nom, appel):
        """Exécute un essai et affiche soit le résultat, soit un rappel gentil."""
        try:
            resultat = appel()
        except Exception as erreur:                     # fonction incomplète ?
            print(f"  {nom} : pas encore terminée ({type(erreur).__name__})")
            return
        if resultat is Ellipsis or resultat is None:    # il reste des ...
            print(f"  {nom} : pas encore terminée (les ... du squelette sont encore là)")
        else:
            print(f"  {nom} -> {resultat}")

    print("Voici où tu en es dans tes dix fonctions :")
    _essai("A.1 indice_de_la_lettre('M')", lambda: indice_de_la_lettre("M"))
    _essai("A.2 decaler_lettre('A', -1)", lambda: decaler_lettre("A", -1))
    _essai("A.3 vider_les_espaces(\"Bonjour, l'ami !\")",
           lambda: vider_les_espaces("Bonjour, l'ami !"))
    _essai("B.1 vigenere_chiffrer('BONJOUR LE MONDE', 'CLE')",
           lambda: vigenere_chiffrer("BONJOUR LE MONDE", "CLE"))
    _essai("B.2 vigenere_dechiffrer('DZRLZYT WI OZRFP', 'CLE')",
           lambda: vigenere_dechiffrer("DZRLZYT WI OZRFP", "CLE"))
    # Pour tester C.1, on fabrique une « colonne » de toutes pièces : un texte
    # français chiffré avec la lettre de clef D (donc un décalage de 3).
    # La fonction doit retrouver le décalage 3.
    _essai("C.1 forcer_cesar_sur_colonne (doit donner le décalage 3)",
           lambda: forcer_cesar_sur_colonne(
               vigenere_chiffrer_reference(
                   nettoyer("LE MESSAGE ARRIVE CE SOIR A DIX HEURES DEVANT LA PORTE DU JARDIN"),
                   "D")))
    _essai("C.2 colonnes('ABCDEFGHIJ', 3)",
           lambda: colonnes("ABCDEFGHIJ", 3))
    _essai("C.3 recoller(['ADGJ', 'BEH', 'CFI'], 3)",
           lambda: recoller(["ADGJ", "BEH", "CFI"], 3))
    _essai("C.4 forcer_vigenere(MESSAGE_VIGENERE_1, PERIODE_1)",
           lambda: forcer_vigenere(MESSAGE_VIGENERE_1, PERIODE_1))
    _essai("D.1 cle_par_texte_connu('BONJOUR', 'DZRLZYT')",
           lambda: cle_par_texte_connu("BONJOUR", "DZRLZYT"))

    print()
    print("Pour comparer avec la version du professeur (utile en cas de doute) :")
    print("  vigenere_chiffrer_reference('BONJOUR LE MONDE', 'CLE') =",
          repr(vigenere_chiffrer_reference("BONJOUR LE MONDE", "CLE")))
    print()
    print("Quand tout est écrit, lance les épreuves :")
    print("    python3 test_tp2_vigenere.py")
