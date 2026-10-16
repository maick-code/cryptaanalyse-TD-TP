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

LE PLAN DE CE FICHIER
---------------------
   1. Rappels du cours sur Vigenère .................................. § A
   2. Le code à écrire (chiffrer et déchiffrer) ...................... § B
   3. ★ LA CRYPTANALYSE ★ : casser Vigenère .......................... § C
   4. Des expériences à faire dans l'interpréteur ..................... § D
   5. Des questions de rapport ....................................... § E

LA CRYPTANALYSE EST LA PARTIE PRINCIPALE DU TP
----------------------------------------------
Écrire Vigenère, c'est de l'arithmétique.  Le casser, c'est de la cryptanalyse,
et c'est LA leçon du chapitre 2 : un chiffre qui rend l'analyse de fréquences
inutilisable peut être ramené, colonne par colonne, à de simples décalages de
César — que l'on sait déjà casser depuis le TP 1.

Les outils de rangement dont tu aurais besoin (découper en colonnes, recoller,
décaler une lettre, vider un texte de ses espaces) sont DÉJÀ ÉCRITS dans
`outils/reference.py` : tu peux donc consacrer tout ton temps aux attaques.

LA BOUCLE DE TRAVAIL
   1. écris une fonction dans ce fichier ;
   2. dans un terminal, ici, tape :

          python3 test_tp2_vigenere.py

   3. lis le bilan : [OK] = c'est juste ; [ÉCHEC] = l'explication de l'erreur ;
   4. recommence, puis passe à la fonction suivante.

Si tu as besoin de revoir les bases de Python (variables, chaînes, boucles,
listes, dictionnaires, fonctions), tout est rappelé dans le § A du fichier du
TP 1 (`seance1_permutation_substitution/tp1_permutation.py`) : ouvre-le et lis
les « DIX GESTES ».

LES CINQ FONCTIONS À ÉCRIRE
---------------------------
  § B — le code à écrire                § C — ★ CRYPTANALYSE ★
   B.1  vigenere_chiffrer                C.1  decalage_probable
   B.2  vigenere_dechiffrer              C.2  forcer_vigenere
                                         C.3  cle_par_texte_connu

  Et, en jeu, les quatre messages interceptés :
        MESSAGE_VIGENERE_1 (période donnée)   MESSAGE_VIGENERE_2 (idem)
        MESSAGE_URGENT     (période donnée)   MESSAGE_INTERCEPTE (attaque D.3)
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

# Les outils fournis, que tu peux utiliser librement :
#   * ALPHABET            : la chaîne "ABC...Z" ;
#   * colonnes(texte, p)  : range le texte en p colonnes (voir C.2 du TP) ;
#   * decaler_lettre(l, d): décale une lettre en tournant dans l'alphabet ;
#   * indice_de_la_lettre : A -> 0, B -> 1, ... ;
#   * recoller(...)       : refait un texte à partir des colonnes ;
#   * rehabiller(texte_modele, lettres) : replace des lettres dans la
#     présentation d'un texte (pour remettre les espaces après déchiffrement) ;
#   * vider_les_espaces(texte) : ne garde que les lettres A...Z ;
#   * vigenere_chiffrer_reference / ..._dechiffrer_reference : la version du
#     professeur, pour vérifier la tienne.
from outils.reference import (
    ALPHABET,
    colonnes,
    decaler_lettre,
    indice_de_la_lettre,
    rehabiller,
    recoller,
    vider_les_espaces,
    vigenere_chiffrer as vigenere_chiffrer_reference,
    vigenere_dechiffrer as vigenere_dechiffrer_reference,
)

# L'instrument de mesure de la cryptanalyse :
#   distance_au_francais(texte) : écart entre les fréquences des lettres du
#   texte et celles du français.  PLUS LA VALEUR EST PETITE, plus le texte
#   ressemble à du français.  C'est l'outil de C.1, C.2 et C.3.
from outils.texte_francais import distance_au_francais


# ###########################################################################
#
#  § A — RAPPELS DU COURS (c'est le cœur de la séance)
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
#    différentes : les fréquences globales deviennent inutilisables.  On a
#    surnommé Vigenère « le chiffre indéchiffrable ».  C'était excessif, et ton
#    travail de la partie C le montrera.
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


# ###########################################################################
#
#  § B — LE CODE À ÉCRIRE : CE QUI SERT À CHIFFRER
#
# ###########################################################################

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
                    * son décalage est `indice_de_la_lettre(lettre_de_clef)` ;
                    * décale le caractère avec l'outil fourni :
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
        * tu peux appeler les fonctions fournies : `decaler_lettre(...)`.

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
            decalage = indice_de_la_lettre(...)         # son décalage
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
    #             decalage = indice_de_la_lettre(lettre_de_clef)
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
          de 3.  L'outil `decaler_lettre` gère déjà les décalages négatifs.

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
            decalage = indice_de_la_lettre(...)         # son décalage
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
    #             decalage = indice_de_la_lettre(lettre_de_clef)
    #             clair += decaler_lettre(caractere, -decalage)
    #             rang_clef += 1
    #         else:
    #             clair += caractere
    #     return clair
    # ----------------------------------------------------------------------


# ###########################################################################
#
#  § C — ★ CRYPTANALYSE ★ : CASSER VIGENÈRE
#
#  LA PARTIE PRINCIPALE DU TP.  Voici l'idée complète, à comprendre avant
#  d'écrire une seule ligne :
#
#      La clef se RÉPÈTE.  Si elle fait 4 lettres, les caractères aux positions
#      0, 4, 8, 12... sont décalés de la MÊME quantité.  En rangeant le message
#      chiffré en 4 colonnes, CHAQUE COLONNE EST UN SIMPLE CODE DE CÉSAR.
#
#  Et casser César, tu sais faire depuis le TP 1 : on essaie les 26 décalages
#  possibles et l'on garde celui dont le résultat ressemble le plus au français
#  (ici : `distance_au_francais`, appliquée à la colonne).
#
#  Il ne reste alors qu'à recoller les colonnes déchiffrées : le message
#  apparaît.  C'est exactement ce que fait la fonction `forcer_vigenere`.
#
#  ## DEUX DÉTAILS QUI COMPTENT ########################################
#
#   * LES ESPACES NE COMPTENT PAS.  Comme ils ne consomment pas de lettre de
#     clef, il faut les retirer AVANT de découper en colonnes (outil fourni :
#     `vider_les_espaces`), puis les remettre à la fin (outil fourni :
#     `rehabiller`).
#
#   * TROUVER LA PÉRIODE est un problème à part entière : c'est tout le
#     programme du TP 3 (méthode de Kasiski et indice de coïncidence).  Aujourd'
#     hui, la période vous est DONNÉE : c'est ce qui permet de se concentrer sur
#     l'attaque elle-même.
#
#  ## LES OUTILS FOURNIS POUR CETTE PARTIE #####################
#     vider_les_espaces(texte)      colonnes(texte, periode)
#     recoller(morceaux, periode)   decaler_lettre(lettre, d)
#     distance_au_francais(texte)   rehabiller(modele, lettres)
#
# ###########################################################################


def decalage_probable(colonne):
    """C.1 — ★ CRYPTANALYSE ★ retrouver le décalage d'UNE colonne.

    POURQUOI (COURS) : chaque colonne est un texte français chiffré par un
    décalage constant (un César).  On essaie donc les 26 décalages, on déchiffre
    chaque fois la colonne, et l'on garde celui qui donne le texte le plus proche
    du français : c'est l'attaque par analyse de fréquences du TP 1, appliquée à
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
                  dans l'exercice C.2 du TP 1) ;
        étape 6 : renvoie `meilleur_decalage` (un nombre entre 0 et 25).

    COMMENT LIRE LE RÉSULTAT : le décalage 0 correspond à la lettre de clef A,
        1 à B, 2 à C, ..., 25 à Z.  On convertit en lettre dans C.2.

    RAPPELS PYTHON :
        * deux boucles imbriquées : la petite (les lettres de la colonne)
          s'exécute entièrement à chaque tour de la grande (les 26 décalages) ;
        * `distance < meilleure_distance` : on cherche la PLUS PETITE distance.

    EXEMPLE (ce que les tests vérifient) : si la colonne a été chiffrée avec la
    lettre de clef D (décalage 3), la fonction renvoie 3.
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


def forcer_vigenere(texte_chiffre, periode):
    """C.2 — ★ CRYPTANALYSE ★ casser un message dont on connaît la période.

    C'EST L'ATTAQUE COMPLÈTE DU COURS.  Elle s'enchaîne en six étapes, et tu as
    déjà écrit la brique principale (C.1) :

        étape 1 : enlève les espaces et la ponctuation (outil fourni), car ils
                  ne font pas partie du chiffrement ;
        étape 2 : range les lettres en `periode` colonnes (outil fourni) ;
        étape 3 : pour chaque colonne, trouve son décalage avec ta fonction C.1 ;
        étape 4 : la clef est la suite des lettres correspondantes : décalage 0
                  -> A, 1 -> B, ... On la construit avec :
                      cle = ""
                      for decalage in decalages:
                          cle += ALPHABET[decalage]
        étape 5 : déchiffre chaque colonne avec son décalage (avec
                  `decaler_lettre(lettre, -decalage)`), puis recolle les
                  colonnes avec l'outil fourni `recoller` : tu obtiens les
                  lettres du message clair, sans espaces ;
        étape 6 : remets la présentation d'origine (espaces, ponctuation) avec
                  l'outil fourni :
                      clair = rehabiller(texte_chiffre, lettres_claires)
        étape 7 : renvoie les DEUX résultats : `return (cle, clair)`.

    RAPPELS PYTHON :
        * construis une liste `decalages` avec `decalages.append(...)` ;
        * pour parcourir les colonnes ET leurs décalages :
              for rang in range(periode):
                  decalage = decalages[rang]
                  morceau = morceaux[rang]
        * `return (cle, clair)` renvoie un couple ; on le lira ensuite :
              cle, clair = forcer_vigenere(message, periode)

    EXEMPLE D'UTILISATION (ta récompense, avec les messages interceptés plus bas) :
        cle, clair = forcer_vigenere(MESSAGE_VIGENERE_1, PERIODE_1)
        print(cle)
        print(clair[:80])

    CONSEIL DE MISE AU POINT : les tests de C.1 doivent passer AVANT d'attaquer
    C.2.  Si C.2 échoue, ajoute `print(cle)` juste avant le return et regarde la
    clef trouvée : si elle ressemble à la vraie clef sans être exactement elle,
    c'est qu'une colonne a été mal reconnue (colonne trop pauvre en lettres : le
    message est trop court pour cette période).
    """
    # --- À COMPLÉTER ---
    lettres_chiffrees = vider_les_espaces(...)          # étape 1
    morceaux = colonnes(lettres_chiffrees, ...)         # étape 2

    decalages = []                                      # un décalage par colonne
    cle = ""                                            # la clef reconstruite
    for rang in range(periode):
        decalage = decalage_probable(...)               # étape 3 : le décalage
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
    #         decalage = decalage_probable(morceaux[rang])
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


def cle_par_texte_connu(message_clair, message_chiffre):
    """C.3 — ★ CRYPTANALYSE ★ retrouver la clef quand on connaît un morceau du
    texte clair.

    POURQUOI (COURS) : c'est l'attaque la plus simple et la plus ancienne, et
    elle est redoutable.  Si l'on met la main sur le texte en clair (un rapport,
    un communiqué, un télégramme intercepté deux fois), l'affaire est entendue :
    on compare les deux textes lettre à lettre, et l'on retrouve la clef.  C'est
    la base des attaques dites « à texte clair connu », utilisées pour casser
    Enigma : les Allemands terminaient leurs messages par des formules
    stéréotypées.

    COMMENT ÇA MARCHE : on sait que, position par position,
        chiffré = clair + clef        donc        clef = chiffré - clair
    et l'on travaille modulo 26 comme toujours.

    CE QUE TU DOIS FAIRE :
        étape 1 : enlève espaces et ponctuation des DEUX textes (outil fourni
                  `vider_les_espaces`) ;
        étape 2 : ATTENTION, ICI L'AGENT N'A PHOTOGRAPHIÉ QU'UN FRAGMENT : les
                  deux textes n'ont pas forcément la même longueur.  On compare
                  donc lettre à lettre jusqu'à la fin du PLUS COURT :
                      longueur = min(len(clair), len(chiffre))
                      for position in range(longueur):
                          decalage = (indice_de_la_lettre(chiffre[position])
                                      - indice_de_la_lettre(clair[position])) % 26
                          suite += ALPHABET[decalage]
                  Tu obtiens une longue suite de lettres, par exemple
                  « EDFHEDFHEDFH... » (une suite qui se répète).
        étape 3 : cette suite ne fait que répéter la clef.  Cherche la plus
                  PETITE période p telle que `suite[position] == suite[position + p]`
                  pour toutes les positions, et renvoie les p premières lettres.
                  (Même problème qu'au TP 1 : une boucle `for p in range(1, ...)`
                  et un test pour toutes les positions.)
        étape 4 : renvoie la clef.

    RAPPELS PYTHON :
        * `min(a, b)` donne le plus petit des deux nombres ;
        * pour tester TOUTES les positions et sortir dès qu'une seule échoue :
              tout_bon = True
              for position in range(len(suite) - periode):
                  if suite[position] != suite[position + periode]:
                      tout_bon = False
                      break
          (`break` interrompt la boucle : plus la peine de continuer) ;
        * `suite[:periode]` prend les `periode` premières lettres.

    EXEMPLES (ce que les tests vérifient) :
        cle_par_texte_connu("BONJOUR", "DZRLZYT")  ->  "CLE"
        Et avec un simple fragment : cle_par_texte_connu("BONJ", "DZRLZ") -> "CLE"

    LIMITE À CONNAÎTRE : on ne retrouve que les lettres de clef qui ont
    réellement servi.  Si le fragment connu est plus court que la clef, on ne
    peut pas la retrouver en entier — c'est une limite de l'attaque, pas de ton
    code.
    """
    # --- À COMPLÉTER ---
    clair = vider_les_espaces(...)                      # étape 1
    chiffre = vider_les_espaces(...)                    # étape 1 (suite)
    longueur = min(len(clair), len(...))                # étape 2 : le plus court

    suite = ""                                          # la clef répétée
    for position in range(longueur):                    # étape 2
        decalage = (indice_de_la_lettre(chiffre[position])
                    - indice_de_la_lettre(clair[position])) % ...
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
    #     longueur = min(len(clair), len(chiffre))
    #
    #     suite = ""
    #     for position in range(longueur):
    #         decalage = (indice_de_la_lettre(chiffre[position])
    #                     - indice_de_la_lettre(clair[position])) % 26
    #         suite += ALPHABET[decalage]
    #
    #     for periode in range(1, len(suite) + 1):
    #         tout_bon = True
    #         for position in range(len(suite) - periode):
    #             if suite[position] != suite[position + periode]:
    #                 tout_bon = False
    #                 break
    #         if tout_bon:
    #             return suite[:periode]
    #     return suite
    # ----------------------------------------------------------------------


# ###########################################################################
#
#  § C (suite) — LES MESSAGES INTERCEPTÉS
#
#  Quatre messages t'attendent.  Pour les trois premiers, on connaît la PÉRIODE
#  (un indicateur obtenu par ailleurs : c'est le TP 3 qui apprendra à la trouver
#  tout seul), mais PAS la clef : à toi de jouer.
#
#    MESSAGE_VIGENERE_1  période donnée (PERIODE_1)   -> forcer_vigenere
#    MESSAGE_VIGENERE_2  période donnée (PERIODE_2)   -> forcer_vigenere
#    MESSAGE_URGENT      période donnée (PERIODE_URGENT) -> forcer_vigenere
#
#    MESSAGE_INTERCEPTE  : la clef est inconnue, la période aussi ; mais un agent
#                          a photographié le DÉBUT DU TEXTE CLAIR, qui est dans
#                          la constante TEXTE_CONNU.  C'est l'attaque C.3 :
#
#        >>> cle = cle_par_texte_connu(TEXTE_CONNU, MESSAGE_INTERCEPTE)
#        >>> cle, clair = forcer_vigenere(MESSAGE_INTERCEPTE, len(cle))
#
#  Dans l'interpréteur Python :
#      >>> from tp2_vigenere import *
#      >>> cle, clair = forcer_vigenere(MESSAGE_URGENT, PERIODE_URGENT)
#      >>> print(cle)
#      >>> print(clair)
#
#  (Ces constantes sont remplies par le professeur : ne les modifie pas, ce sont
#  les messages interceptés.)

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


# ###########################################################################
#
#  § D — EXPÉRIENCES À FAIRE DANS L'INTERPRÉTEUR (la méthode scientifique)
#
# ###########################################################################
#
# EXPÉRIENCE 1 — Vigenère fait-il vraiment disparaître les fréquences ?
#     >>> from tp2_vigenere import *
#     >>> from outils.texte_francais import barres, frequences
#     >>> from outils.reference import cesar_chiffrer
#     >>> clair = "LE MESSAGE ARRIVE CE SOIR A DIX HEURES DEVANT LA PORTE"
#     >>> print(barres(frequences(clair)))                       (E en tête)
#     >>> print(barres(frequences(cesar_chiffrer(clair, 7))))    (même forme,
#                                                                  décalée)
#     >>> print(barres(frequences(vigenere_chiffrer(clair, "PILOTE"))))
#     Observe : avec Vigenère, plus de E dominant, les lettres se ressemblent.
#     C'est pour cela que l'analyse de fréquences GLOBALE échoue.
#
# EXPÉRIENCE 2 — mais chaque colonne, elle, redevient du français !
#     >>> lettres = vider_les_espaces(vigenere_chiffrer(clair, "PILOTE"))
#     >>> for rang in range(6):
#     ...     print("colonne", rang, barres(frequences(lettres[rang::6]))[:60])
#     (lettres[rang::6] prend un caractère sur six : le découpage [a:b:c]
#     s'écrit début, fin, pas.)  Chaque colonne retrouve l'allure du français :
#     c'est toute l'astuce de C.1 et C.2.
#
# EXPÉRIENCE 3 — voir les 26 distances d'une colonne
#     >>> for decalage in range(26):
#     ...     essai = "".join(decaler_lettre(c, -decalage)
#     ...                     for c in colonnes(lettres, 6)[0])
#     ...     print(decalage, round(distance_au_francais(essai), 1))
#     La plus petite distance donne le décalage de la première lettre de clef.
#
# EXPÉRIENCE 4 — la clef est bien plus longue que le texte connu
#     >>> cle_par_texte_connu("BONJ", "DZRLZ")     -> "CLE" (3 lettres retrouvées)
#     >>> cle_par_texte_connu("BO", "DZ")          -> que se passe-t-il ?
#     Réfléchis : avec deux lettres connues, peut-on vraiment retrouver une clef
#     de trois lettres ?  Note la réponse pour la question 5 du rapport.
#
# ###########################################################################
#
#  § E — QUESTIONS DE RAPPORT (à rédiger et à rendre avec le fichier)
#
# ###########################################################################
#
# QUESTION 1. Pourquoi l'analyse de fréquences globale échoue-t-elle sur
# Vigenère ?  Cite l'expérience 1.
#
# QUESTION 2. Pourquoi fonctionne-t-elle « par colonne » ?  Cite l'expérience 2,
# et explique le rôle de la PÉRIODE dans l'attaque.
#
# QUESTION 3. Combien y a-t-il de clefs de 5 lettres ?  Et de 8 lettres ?
# (Indice : 26 possibilités par lettre.)  Compare ce nombre au coût réel de
# l'attaque par colonnes : 26 essais par colonne, donc 26 x période essais.
# Que peut-on en conclure sur ce qui fait la solidité d'un chiffre ?
#
# QUESTION 4. Pour la dépêche MESSAGE_URGENT : quelle est la clef trouvée ?
# Quelles sont les dix premières lettres du texte clair ?  Que signifie le
# message ?
#
# QUESTION 5. L'attaque C.3 a-t-elle besoin de la période ?  Explique pourquoi,
# et ce qui se passe si le fragment connu est plus court que la clef (voir
# l'expérience 4).  Dans quel cas cette attaque est-elle la plus efficace ?
#
# QUESTION 6. Deux messages sont chiffrés avec la même clef.  Que peut-on en
# déduire ?  (Indice : compare les positions où les deux textes chiffrés ont la
# même lettre ; c'est l'attaque « de deux messages », celle qui a fait tomber
# Enigma par la répétition de la clef de message.)
#


if __name__ == "__main__":
    # Cette partie s'exécute quand on lance :   python3 tp2_vigenere.py
    # Elle sert à vérifier d'un coup d'œil où tu en es.

    def _inacheve(valeur):
        """Vrai si la fonction n'est pas finie : il reste des « ... » ou rien."""
        if valeur is Ellipsis or valeur is None:
            return True
        if isinstance(valeur, (tuple, list)):
            return any(_inacheve(element) for element in valeur)
        return False

    def _essai(nom, appel):
        """Exécute un essai et affiche soit le résultat, soit un rappel gentil."""
        try:
            resultat = appel()
        except Exception as erreur:                     # fonction incomplète ?
            print(f"  {nom} : pas encore terminée ({type(erreur).__name__})")
            return
        if _inacheve(resultat):                         # il reste des ...
            print(f"  {nom} : pas encore terminée (les ... du squelette sont encore là)")
        else:
            print(f"  {nom} -> {resultat}")

    print("Voici où tu en es dans tes cinq fonctions :")
    print("  --- § B : le code à écrire ---")
    _essai("B.1 vigenere_chiffrer('BONJOUR LE MONDE', 'CLE')",
           lambda: vigenere_chiffrer("BONJOUR LE MONDE", "CLE"))
    _essai("B.2 vigenere_dechiffrer('DZRLZYT WI OZRFP', 'CLE')",
           lambda: vigenere_dechiffrer("DZRLZYT WI OZRFP", "CLE"))
    print("  --- § C : ★ cryptanalyse ★ ---")
    # Pour tester C.1, on fabrique une « colonne » de toutes pièces : un texte
    # français chiffré avec la lettre de clef D (donc un décalage de 3).
    _essai("C.1 decalage_probable (doit donner le décalage 3)",
           lambda: decalage_probable(
               vider_les_espaces(
                   vigenere_chiffrer_reference(
                       "LE MESSAGE ARRIVE CE SOIR A DIX HEURES DEVANT LA PORTE DU JARDIN",
                       "D"))))
    _essai("C.2 forcer_vigenere(MESSAGE_URGENT, PERIODE_URGENT)",
           lambda: forcer_vigenere(MESSAGE_URGENT, PERIODE_URGENT))
    _essai("C.3 cle_par_texte_connu('BONJOUR', 'DZRLZYT')",
           lambda: cle_par_texte_connu("BONJOUR", "DZRLZYT"))

    print()
    print("Pour comparer avec la version du professeur (utile en cas de doute) :")
    print("  vigenere_chiffrer_reference('BONJOUR LE MONDE', 'CLE') =",
          repr(vigenere_chiffrer_reference("BONJOUR LE MONDE", "CLE")))
    print()
    print("Quand tout est écrit, lance les épreuves :")
    print("    python3 test_tp2_vigenere.py")
