"""==========================================================================
 TP 1 — GÉNÉRALITÉS, CODES SIMPLES ET CRYPTANALYSE
 Chapitre 1 (définition d'un code) et chapitre 2 (codes de permutation,
 codes de substitution, cryptanalyse) — Pascal Boyer, « Cryptographie 2013 ».

 Durée conseillée : 2 h.   À rendre : ce fichier complété.
==========================================================================

 ██  MODE D'EMPLOI — À LIRE UNE FOIS, C'EST IMPORTANT  ██
==========================================================================

Tu ne connais pas Python ? Ce n'est pas grave : ce fichier t'explique tout, et
il te donne même la solution de chaque exercice. Voici comment il est construit.

LE PLAN DE CE FICHIER
---------------------
   1. Un mini-cours de Python (les 10 gestes dont tu as besoin) ...... § A
   2. Six exercices, à faire dans l'ordre ........................... § B et § C
        § B : le code à écrire (ce qui sert à CHIFFRER) .......... 3 fonctions
        § C : ★ LA CRYPTANALYSE ★ (ce qui sert à CASSER) ......... 3 fonctions
   3. Un supplément d'histoire (à lire) ............................. § D
   4. Des expériences à faire dans l'interpréteur Python ............. § E
   5. Des questions de rapport ....................................... § F

LA CRYPTANALYSE EST LA PARTIE PRINCIPALE DU TP
----------------------------------------------
Écrire un chiffre, c'est facile ; le casser, c'est là que se joue toute la
cryptographie du cours. La partie CRYPTANALYSE te fait attaquer de vrais
messages interceptés, dont tu ne connais PAS la clef, puis reconnaître tout seul
le chiffrement utilisé. Les outils de rangement dont tu aurais besoin sont déjà
écrits dans `outils/reference.py` : tu peux donc te concentrer sur l'attaque.

CHAQUE EXERCICE EST ÉCRIT TOUJOURS SUR LE MÊME MODÈLE
-----------------------------------------------------
   > OBJECTIF            : ce que la fonction doit faire.
   > POURQUOI (COURS)    : d'où cela vient dans le cours de cryptographie.
   > CE QUE TU DOIS FAIRE : la recette, étape par étape, en français.
   > RAPPELS PYTHON      : la (ou les) instruction(s) Python qu'il te faut.
   > À COMPLÉTER          : le squelette de la fonction. Les pointillés `...`
                            sont des trous : remplace-les par ce qui est demandé
                            dans le commentaire à côté.
   > ✅ SOLUTION          : le code complet, mis en commentaire. Tu peux le
                            lire à tout moment, mais essaie d'abord trente
                            secondes par toi-même : c'est ainsi qu'on apprend.

LA BOUCLE DE TRAVAIL (à répéter après chaque exercice)
-----------------------------------------------------
   1. ouvre ce fichier dans un éditeur (Thonny, VS Code, Idle... ou n'importe
      quel traitement de texte) ;
   2. écris le code demandé dans une fonction ;
   3. ouvre un terminal dans ce dossier et tape :

          python3 test_tp1_permutation.py

   4. lis le bilan : « [OK] » signifie que ton code est juste, « [ÉCHEC] »
      t'explique ce qui ne va pas (valeur attendue, valeur obtenue) ;
   5. recommence jusqu'à ce que les onze épreuves soient réussies.

RÈGLE D'OR : ne modifie jamais les fichiers `test_tp1_permutation.py` ni le
dossier `outils/` : ils appartiennent au professeur. Tu peux en revanche lire
`outils/reference.py` autant que tu veux, il est commenté ligne par ligne.

LES SIX FONCTIONS À ÉCRIRE
--------------------------
  § B — le code à écrire                     § C — ★ CRYPTANALYSE ★
   B.1  compter_lettres                       C.1  attaque_scytale
   B.2  cesar_chiffrer                        C.2  forcer_cesar
   B.3  cesar_dechiffrer                      C.3  identifier_et_dechiffrer

  Et, en jeu à la fin du TP, les cinq messages interceptés :
        MESSAGE_SCYTALE   MESSAGE_CESAR
        MESSAGE_MYSTERE_1   MESSAGE_MYSTERE_2   MESSAGE_MYSTERE_3
==========================================================================
"""

# ---------------------------------------------------------------------------
# LES IMPORTS (ne change rien ici, mais comprends ce que tu lis)
# ---------------------------------------------------------------------------
# Ces trois lignes techniques servent seulement à ce que Python trouve le
# dossier « outils » du dépôt, quel que soit l'endroit d'où tu lances la
# commande.  Tu n'as pas à y toucher.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Le fichier `common.py` du dossier te donne les outils de base écrits par le
# professeur :
#   * ALPHABET          : la chaîne "ABCDEFGHIJKLMNOPQRSTUVWXYZ" ;
#   * nettoyer(texte)   : met en majuscules et enlève accents et ponctuation ;
#   * comptage(texte)   : compte les 26 lettres d'un texte ;
#   * scytale_chiffrer / scytale_dechiffrer : le code de permutation, fourni.
from common import ALPHABET, comptage, nettoyer, scytale_chiffrer, scytale_dechiffrer

# Ces outils-là sont fournis pour que tu ne perdes pas ton temps sur du
# rangement : ils ne sont PAS de la cryptographie.
from outils.reference import cle_scytale_possibles, vider_les_espaces

# Et voici les deux instruments de mesure de la cryptanalyse :
#   * distance_au_francais(texte) : écart entre les fréquences des lettres du
#     texte et celles du français. PLUS LA VALEUR EST PETITE, plus le texte
#     ressemble à du français. C'est l'outil de C.2.
#   * vraisemblance(texte)        : note fondée sur l'ORDRE des lettres.
#     PLUS LA VALEUR EST GRANDE, plus le texte ressemble à du français. C'est
#     l'outil de C.1.
from outils.texte_francais import distance_au_francais, vraisemblance


# ###########################################################################
#
#  § A — MINI-COURS DE PYTHON : LES DIX GESTES DONT TU AS BESOIN
#
#  Ce n'est pas un cours complet : ce sont exactement les outils utilisés dans
#  les six exercices. Tu peux revenir ici à tout moment.
#
#  Avertissement : en Python, les espaces au début des lignes ont un sens !
#  On écrit les instructions « à l'intérieur » d'une boucle ou d'un `if` avec
#  4 espaces devant. Ce fichier te montre la bonne indentation partout.
#
# ###########################################################################

# --- GESTE 1 : les variables -------------------------------------------------
# Une variable est une boîte étiquetée dans laquelle on range une valeur.
#     taille = 5              -> dans la boîte « taille », il y a 5
#     nom = "CLE"             -> dans la boîte « nom », il y a le texte CLE
#     resultat = ""           -> une boîte qui contient une chaîne VIDE
# Le signe = veut dire « range dans la boîte », et non « est égal à ».
# Pour comparer, on utilise == (deux signes égaux) :
#     if cle == 3:            -> EST-CE QUE cle vaut 3 ?

# --- GESTE 2 : les chaînes de caractères (le texte) --------------------------
# Une chaîne s'écrit entre guillemets : "BONJOUR" ou 'BONJOUR'.
# Les opérations utiles :
#     texte.upper()          -> la même chose en MAJUSCULES
#     len(texte)             -> le nombre de caractères
#     texte[0]               -> le premier caractère (les positions partent de 0 !)
#     texte[2]               -> le TROISIÈME caractère
#     texte[debut:fin]       -> l'extrait, de `debut` à `fin` EXCLUE :
#                               "BONJOUR"[0:3] vaut "BON"
#     "A" in texte           -> True (vrai) si la lettre A est dans le texte
#     texte.count("DE")      -> combien de fois le groupe "DE" apparaît
#     resultat = ""          -> une chaîne vide, dans laquelle on va ajouter
#     resultat += "A"        -> ajoute "A" à la FIN de la chaîne
#                               après deux fois, resultat vaut "AA"

# --- GESTE 3 : les nombres, et les deux opérations spéciales -----------------
#     len("BONJOUR") // 3    -> 2   division ENTIÈRE (on jette le reste)
#     len("BONJOUR") % 3     -> 1   RESTE de la division (l'opérateur %)
# Ces deux opérations servent tout le temps en cryptographie : le % sert à
# « revenir au début » (après Z, par exemple), le // à compter des lignes.

# --- GESTE 4 : les comparaisons et les décisions -----------------------------
#     ==  égal à             !=  différent de
#     <   plus petit         >   plus grand
#     <=  plus petit ou égal >=  plus grand ou égal
# Une décision s'écrit :
#     if condition:
#         ...ce qu'on fait si c'est vrai...
#     elif autre_condition:
#         ...sinon, si l'autre condition est vraie...
#     else:
#         ...sinon...
# Exemple : tester si un caractère est une lettre majuscule non accentuée
#     if "A" <= caractere <= "Z":

# --- GESTE 5 : la boucle « pour chaque » ------------------------------------
#     for caractere in texte:
#         ...ce qu'on fait pour CHAQUE caractère...
# `caractere` est une variable : elle prend successivement la valeur du premier
# caractère, du deuxième, etc.
# Pour répéter 5 fois, avec un compteur qui vaut 0, 1, 2, 3, 4 :
#     for i in range(5):
# `range(a, b)` va de a à b-1 ; `range(a, b, pas)` avance du pas donné :
#     for debut in range(0, len(texte), 3):     -> 0, 3, 6, 9...
# Autre forme très utile, avec l'indice ET la valeur :
#     for position, caractere in enumerate(texte):

# --- GESTE 6 : les listes ----------------------------------------------------
# Une liste s'écrit entre crochets et peut contenir plusieurs valeurs :
#     nombres = [2, 4, 5, 8]
#     nombres[0]             -> 2       (premier élément)
#     nombres[-1]            -> 8       (dernier élément)
#     len(nombres)           -> 4
#     nombres.append(10)     -> ajoute 10 à la fin de la liste
#     for n in nombres:      -> parcourt les éléments

# --- GESTE 7 : les dictionnaires --------------------------------------------
# Un dictionnaire range des valeurs sous des noms (des « clefs ») :
#     comptes = {"A": 0, "B": 0, "C": 0}
#     comptes["A"] = 3       -> la case A vaut maintenant 3
#     comptes["A"]           -> 3
#     comptes["A"] += 1      -> on augmente la case A de 1 (compteur !)
#     comptes.get("Z", 0)    -> la valeur de Z, ou 0 si Z n'est pas dans le dict
#     for lettre in comptes: -> parcourt les clefs
# Attention : si la clef n'existe pas encore, `comptes["Z"] += 1` provoque une
# erreur. C'est pourquoi on initialise les 26 compteurs à zéro au départ.

# --- GESTE 8 : les fonctions -------------------------------------------------
# Une fonction est une recette que l'on pourra appeler par son nom :
#     def doubler(x):
#         return x * 2
# `def` annonce la fonction, `x` est l'argument (la valeur donnée),
# `return` renvoie le résultat.  Sans `return`, la fonction ne renvoie rien
# (Python dit « None »), et les tests échoueront.
# Appeler la fonction : doubler(3) vaut 6.

# --- GESTE 9 : les erreurs à ne pas commettre -------------------------------
#   1. oublier les deux-points à la fin de `def`, `for`, `if` ;
#   2. oublier l'indentation (4 espaces) du bloc en dessous ;
#   3. oublier `return` (la fonction ne renvoie rien) ;
#   4. mettre `=` au lieu de `==` dans un test ;
#   5. mélanger majuscules et minuscules : "A" et "a" sont différents.

# --- GESTE 10 : voir ce que fait son code -----------------------------------
# Dans un terminal, tu peux dialoguer avec Python :
#     python3
#     >>> from tp1_permutation import *
#     >>> cesar_chiffrer("BONJOUR, LE MONDE", 3)
# Pour quitter : tape `exit()` puis Entrée.  C'est très utile pour essayer une
# instruction avant de l'écrire dans le fichier.


# ###########################################################################
#
#  § B — LE CODE À ÉCRIRE : CE QUI SERT À CHIFFRER
#
# ###########################################################################


def compter_lettres(texte):
    """B.1 — OBJECTIF : compter combien de fois chaque lettre apparaît.

    POURQUOI (COURS) : c'est LE geste de la cryptanalyse par analyse de
    fréquences.  Le cryptanalyste arabe du IXe siècle comptait les lettres du
    message intercepté ; c'est ce comptage qui révèle les régularités du
    français.  Ta fonction C.2 ne pourra pas se passer de ce genre de comptage.

    CE QUE TU DOIS FAIRE :
        étape 1 : crée un dictionnaire vide : `comptes = {}` ;
        étape 2 : remplis-le avec les 26 lettres, chacune à 0.  Sans cela,
                  l'instruction `comptes[caractere] += 1` provoquerait une
                  erreur pour une lettre qui n'existe pas encore dans le
                  dictionnaire.  Une boucle sur ALPHABET fait l'affaire :
                      for lettre in ALPHABET:
                          comptes[lettre] = 0
        étape 3 : parcours le texte mis en MAJUSCULES ;
        étape 4 : à chaque fois que le caractère est une lettre de "A" à "Z",
                  augmente son compteur de 1 : `comptes[caractere] += 1` ;
        étape 5 : renvoie le dictionnaire `comptes`.

    RAPPELS PYTHON :
        * `comptes = {}` crée un dictionnaire vide ;
        * `comptes[lettre] = 0` crée (ou remplace) la case `lettre` ;
        * `comptes[caractere] += 1` augmente le compteur de 1 ;
        * `len(comptes)` est le nombre de cases (il doit valoir 26 à la fin).

    EXEMPLES (ce que les tests vérifient) :
        compter_lettres("BONJOUR")["O"]  ->  2
        compter_lettres("BONJOUR")["A"]  ->  0
        len(compter_lettres("BONJOUR"))  ->  26
    """
    # --- À COMPLÉTER ---
    comptes = ...                                     # un dictionnaire vide : {}
    for lettre in ALPHABET:                           # pour les 26 lettres
        comptes[lettre] = ...                         # mets le compteur à 0
    for caractere in texte.upper():                   # parcours le texte en majuscules
        if ...:                                       # est-ce une lettre de A à Z ?
            comptes[caractere] += ...                 # augmente son compteur de 1
    return ...                                        # renvoie le dictionnaire

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     comptes = {}
    #     for lettre in ALPHABET:
    #         comptes[lettre] = 0
    #     for caractere in texte.upper():
    #         if "A" <= caractere <= "Z":
    #             comptes[caractere] += 1
    #     return comptes
    # ----------------------------------------------------------------------


def cesar_chiffrer(texte, cle):
    """B.2 — OBJECTIF : chiffrer un texte avec le code de César de clef `cle`.

    RAPPEL DU COURS : on REMPLACE chaque lettre par une autre : la lettre de
    rang n devient la lettre de rang (n + cle) mod 26.  Avec la clef 3 :
    A devient D, B devient E, ..., Z revient à C.  C'est le plus ancien code de
    substitution connu (les militaires l'appelaient « alphabet trois »).

    CONVENTIONS DU TP (elles servent à tous les tests) :
        * le texte est mis en MAJUSCULES ;
        * seules les lettres de A à Z sont décalées ;
        * les autres caractères (espace, virgule, point, apostrophe) sont
          RECOPIÉS SANS MODIFICATION, à leur place.

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare une chaîne vide : `chiffre = ""` ;
        étape 2 : parcours le texte mis en majuscules ;
        étape 3 : pour chaque caractère :
                    - s'il est entre "A" et "Z" :
                        * trouve son rang dans l'alphabet :
                          `ALPHABET.index(caractere)`
                        * ajoute la clef, puis « reviens au début » avec le
                          reste de la division par 26 :
                          `nouveau_rang = (rang + cle) % 26`
                        * la nouvelle lettre est `ALPHABET[nouveau_rang]` ;
                    - sinon (espace, ponctuation...) : garde le caractère tel
                      quel ;
        étape 4 : renvoie la chaîne `chiffre`.

    RAPPELS PYTHON :
        * `ALPHABET.index("C")` vaut 2, `ALPHABET[2]` vaut "C" ;
        * `(rang + cle) % 26` reste toujours entre 0 et 25 : c'est ce qui fait
          que Z + 1 donne A, et non une lettre qui n'existe pas ;
        * `chiffre += ALPHABET[nouveau_rang]` ajoute la lettre au résultat.

    EXEMPLES (ce que les tests vérifient) :
        cesar_chiffrer("AVE", 3)                ->  "DYH"
        cesar_chiffrer("XYZ", 3)                ->  "ABC"    (retour au début)
        cesar_chiffrer("BONJOUR, LE MONDE", 3)  ->  "ERQMRXU, OH PRQGH"
    """
    # --- À COMPLÉTER ---
    chiffre = ...                                      # une chaîne vide
    for caractere in texte.upper():                    # parcours le texte
        if "A" <= caractere <= "Z":                    # est-ce une lettre ?
            rang = ALPHABET.index(...)                 # son rang (0 à 25)
            nouveau_rang = (rang + ...) % ...          # on décale, modulo 26
            chiffre += ALPHABET[...]                   # la nouvelle lettre
        else:
            chiffre += ...                             # recopie le caractère tel quel
    return ...                                         # renvoie le texte chiffré

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     chiffre = ""
    #     for caractere in texte.upper():
    #         if "A" <= caractere <= "Z":
    #             rang = ALPHABET.index(caractere)
    #             nouveau_rang = (rang + cle) % 26
    #             chiffre += ALPHABET[nouveau_rang]
    #         else:
    #             chiffre += caractere
    #     return chiffre
    # ----------------------------------------------------------------------


def cesar_dechiffrer(texte_chiffre, cle):
    """B.3 — OBJECTIF : déchiffrer un message chiffré par César.

    POURQUOI C'EST FACILE (et important) : déchiffrer, c'est décaler dans
    l'autre sens, donc de -cle.  Et comme « reculer de 3 » revient au même que
    « avancer de 23 » (3 + 23 = 26), on peut réutiliser exactement la fonction
    précédente avec le décalage `(-cle) % 26`.

    CE QUE TU DOIS FAIRE :
        écris UNE SEULE ligne, qui appelle la fonction B.2 :
            return cesar_chiffrer(texte_chiffre, (-cle) % 26)
        C'est tout !  Et c'est une leçon de programmation : quand on a écrit une
        fonction juste, on la réutilise au lieu de recopier du code (moins de
        code, moins de fautes).

    RAPPELS PYTHON :
        * `(-cle) % 26` calcule le décalage inverse.  Pour cle = 3, cela vaut
          23 : compter 23 cases en avant, c'est comme reculer de 3.

    EXEMPLE (ce que les tests vérifient) :
        cesar_dechiffrer("ERQMRXU, OH PRQGH", 3)  ->  "BONJOUR, LE MONDE"
        Et bien sûr, pour toutes les clefs : déchiffrer(chiffrer(x)) = x.
    """
    # --- À COMPLÉTER : une seule ligne suffit ! ---
    return ...                                         # appelle cesar_chiffrer

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     return cesar_chiffrer(texte_chiffre, (-cle) % 26)
    # ----------------------------------------------------------------------


# ###########################################################################
#
#  § C — ★ CRYPTANALYSE ★
#
#  LA PARTIE PRINCIPALE DU TP.  Tu es maintenant un cryptanalyste : tu as
#  intercepté un message, tu ne connais NI le texte, NI la clef, NI même (pour
#  les messages mystères) la méthode de chiffrement utilisée.  Ton travail est
#  de retrouver le texte clair.
#
#  ## LA MÉTHODE GÉNÉRALE, EN TROIS TEMPS ###############################
#
#   1. COMPTER LES CLEFS POSSIBLES.  Si elles sont peu nombreuses (26 pour
#      César, une poignée pour la scytale), on les essaie toutes : c'est la
#      RECHERCHE EXHAUSTIVE.  C'est laid, mais ça marche toujours.
#
#   2. POUR CHAQUE CANDIDAT, SE DEMANDER « EST-CE DU FRANÇAIS ? ».  Un candidat
#      a intérêt à ressembler au français : cela s'appelle une HYPOTHÈSE DE
#      TRAVAIL, et il faut savoir la mesurer.  Deux instruments sont fournis :
#
#        * `distance_au_francais(texte)` : écart entre les FRÉQUENCES des
#          lettres du candidat et celles du français.
#              PLUS PETIT = PLUS FRANÇAIS.
#          Il sert quand les lettres ont été REMPLACÉES (César) : le E du
#          français reste la lettre la plus fréquente du message, simplement
#          décalée.
#
#        * `vraisemblance(texte)` : note fondée sur l'ORDRE des lettres, donc
#          sur la fréquence des PAIRES (« ES », « LE », « DE », « NT » sont
#          partout en français ; « XZ », « QK » nulle part).
#              PLUS GRAND = PLUS FRANÇAIS.
#          Il sert quand les lettres ont été DÉPLACÉES sans être remplacées
#          (scytale) : là, toutes les fréquences sont identiques d'un candidat à
#          l'autre, et seul l'ordre peut les départager.
#
#   3. GARDER LE MEILLEUR CANDIDAT, et vérifier qu'il se lit vraiment.
#
#  ## L'ERREUR À NE PAS COMMETTRE ######################################
#
#   C'est l'erreur classique du débutant : comparer les FRÉQUENCES pour casser
#   une scytale (aucun résultat, puisque la scytale ne change aucune lettre) ou
#   comparer l'ORDRE des lettres pour casser un César (le meilleur score est
#   souvent obtenu avec un texte qui n'est pas encore tout à fait décalé comme
#   il faut).  Choisis ton instrument d'après ce que le chiffrement a fait aux
#   lettres : REMPLACÉES ou DÉPLACÉES.
#
#  ## LES OUTILS QUE TU AS LE DROIT D'UTILISER (ils sont fournis) ######
#
#     cle_scytale_possibles(longueur)  ->  les clefs t à essayer ;
#     scytale_dechiffrer(chiffre, t)   ->  le déchiffrement de la scytale ;
#     vider_les_espaces(texte)         ->  ne garde que les lettres A...Z ;
#     distance_au_francais(texte)      ->  voir ci-dessus ;
#     vraisemblance(texte)             ->  voir ci-dessus.
#
# ###########################################################################


def attaque_scytale(chiffre):
    """C.1 — ★ CRYPTANALYSE ★ retrouver le message clair sans connaître la clef.

    POURQUOI (COURS) : c'est le cœur de la cryptanalyse.  On ne connaît ni le
    message, ni la clef : on a seulement le texte intercepté.  On essaie donc
    toutes les clefs possibles et l'on garde le candidat le plus français.

    QUEL INSTRUMENT CHOISIR ?  La scytale est un code de PERMUTATION : elle
    déplace les lettres sans en remplacer aucune.  Tous les candidats ont donc
    exactement les mêmes fréquences de lettres, et comparer les fréquences ne
    peut pas les départager.  Ce qui les distingue, c'est l'ORDRE : on utilise
    `vraisemblance`, dont la valeur est d'autant plus GRANDE que le texte
    ressemble à du français.

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare trois « boîtes » pour mémoriser le meilleur candidat
                  trouvé jusqu'ici :
                      meilleure_cle = 0
                      meilleur_texte = ""
                      meilleur_score = None     (None = « rien pour l'instant »)
        étape 2 : parcours les clefs possibles :
                      for t in cle_scytale_possibles(len(chiffre)):
        étape 3 : dans la boucle, déchiffre le message avec cette clef :
                      candidat = scytale_dechiffrer(chiffre, t)
                  et calcule sa note :
                      score = vraisemblance(candidat)
        étape 4 : si aucune note n'a encore été retenue, OU si cette note est
                  meilleure que la précédente, mets à jour les trois boîtes :
                      if meilleur_score is None or score > meilleur_score:
                          meilleure_cle = t
                          meilleur_texte = candidat
                          meilleur_score = score
        étape 5 : après la boucle, renvoie les deux informations :
                      return (meilleure_cle, meilleur_texte)
                  Attention à la virgule : `return (a, b)` renvoie DEUX valeurs
                  à la fois ; c'est ce que le test attend.

    RAPPELS PYTHON :
        * `None` est la valeur « rien du tout » ; on la teste avec `is None` ;
        * `or` se dit `or`, `>` compare deux nombres ;
        * `return (a, b)` renvoie un couple ; on le relira ainsi plus tard :
              cle, texte = attaque_scytale(message)

    EXEMPLE (essai que tu peux faire dans l'interpréteur) :
        chiffre = scytale_chiffrer("LEGRANDMESSAGERARRIVECETTEAPRESMIDI", 7)
        attaque_scytale(chiffre)   ->  (7, "LEGRANDMESSAGERARRIVECETTEAPRESMIDI")

    ASTUCE DE MISE AU POINT : si ton résultat est faux, ajoute dans la boucle
        print(t, round(score, 3), candidat[:40])
    et regarde : la bonne clef est celle dont la note est la plus grande.
    """
    # --- À COMPLÉTER ---
    meilleure_cle = 0
    meilleur_texte = ...
    meilleur_score = None
    for t in cle_scytale_possibles(len(chiffre)):
        candidat = scytale_dechiffrer(chiffre, ...)   # déchiffre avec la clef t
        score = vraisemblance(...)                    # note le candidat
        if meilleur_score is None or score > ...:     # est-ce mieux que le meilleur ?
            meilleure_cle = ...
            meilleur_texte = ...
            meilleur_score = ...
    return (... , ...)                                # renvoie la clef ET le texte

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     meilleure_cle = 0
    #     meilleur_texte = ""
    #     meilleur_score = None
    #     for t in cle_scytale_possibles(len(chiffre)):
    #         candidat = scytale_dechiffrer(chiffre, t)
    #         score = vraisemblance(candidat)
    #         if meilleur_score is None or score > meilleur_score:
    #             meilleure_cle = t
    #             meilleur_texte = candidat
    #             meilleur_score = score
    #     return (meilleure_cle, meilleur_texte)
    # ----------------------------------------------------------------------


def forcer_cesar(texte_chiffre):
    """C.2 — ★ CRYPTANALYSE ★ retrouver la clef et le message sans la connaître.

    POURQUOI (COURS) : il n'y a que 26 clefs possibles ; on les essaie toutes.
    Ici les lettres ont été REMPLACÉES : le E du français (environ 15 % du
    texte) reste la lettre la plus fréquente du message chiffré, simplement
    décalée.  On compare donc les FRÉQUENCES avec celles du français.

    ATTENTION À UN PIÈGE CLASSIQUE : l'indice de coïncidence (que tu verras au
    TP 3) est LE MÊME pour les 26 décalages : il est inutile ici.  Ce qui permet
    de trancher, c'est la comparaison des fréquences lettre par lettre, que fait
    `distance_au_francais`.

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare trois boîtes :
                      meilleure_cle = 0
                      meilleur_texte = ""
                      meilleure_distance = None
        étape 2 : essaie les 26 clefs :  `for cle in range(26):`
        étape 3 : dans la boucle :
                      candidat = cesar_dechiffrer(texte_chiffre, cle)
                      distance = distance_au_francais(candidat)
        étape 4 : si `meilleure_distance is None` ou si cette distance est
                  MEILLEURE (donc plus PETITE) que la précédente, mets à jour
                  les trois boîtes ;
        étape 5 : renvoie `(meilleure_cle, meilleur_texte)`.

    RAPPELS PYTHON :
        * `range(26)` donne 0, 1, 2, ..., 25 : les 26 clefs possibles ;
        * `distance < meilleure_distance` : « strictement plus petit » ;
        * `is None` sert à tester « rien pour l'instant ».

    EXEMPLE (ce que les tests vérifient) :
        chiffre = cesar_chiffrer("LE MESSAGE ARRIVE CE SOIR", 17)
        forcer_cesar(chiffre)  ->  (17, "LE MESSAGE ARRIVE CE SOIR")

    ASTUCE DE MISE AU POINT : ajoute `print(cle, distance)` dans la boucle et
    regarde les 26 distances : la plus petite est la bonne clef (les autres sont
    dix à cent fois plus grandes).
    """
    # --- À COMPLÉTER ---
    meilleure_cle = 0
    meilleur_texte = ...
    meilleure_distance = None
    for cle in range(...):                             # les 26 clefs : 0 à 25
        candidat = cesar_dechiffrer(..., cle)          # déchiffre avec cette clef
        distance = distance_au_francais(...)           # mesure l'écart au français
        if meilleure_distance is None or distance < ...:
            meilleure_cle = cle
            meilleur_texte = ...
            meilleure_distance = ...
    return (... , ...)                                 # renvoie la clef ET le message

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     meilleure_cle = 0
    #     meilleur_texte = ""
    #     meilleure_distance = None
    #     for cle in range(26):
    #         candidat = cesar_dechiffrer(texte_chiffre, cle)
    #         distance = distance_au_francais(candidat)
    #         if meilleure_distance is None or distance < meilleure_distance:
    #             meilleure_cle = cle
    #             meilleur_texte = candidat
    #             meilleure_distance = distance
    #     return (meilleure_cle, meilleur_texte)
    # ----------------------------------------------------------------------


def identifier_et_dechiffrer(message):
    """C.3 — ★ CRYPTANALYSE ★ reconnaître le chiffrement, puis le casser.

    POURQUOI (COURS) : dans la réalité, un cryptanalyste reçoit un texte et ne
    sait même pas COMMENT il a été chiffré.  Sa première question est donc :
    « à quoi ai-je affaire ? ».  C'est l'exercice que te proposent les trois
    messages MYSTÈRE : ils ont été chiffrés par une scytale ou par un César, on
    ne te dit pas lequel.

    COMMENT RECONNAÎTRE LE CHIFFREMENT ?  En essayant les DEUX attaques que tu
    viens d'écrire, puis en comparant les deux meilleurs candidats.  Celui des
    deux qui ressemble le plus à du français a été obtenu par la bonne méthode.
    Tu n'as donc besoin d'aucune formule magique : tu as besoin de tes deux
    fonctions et d'un instrument de mesure.  (On mesure ici avec
    `vraisemblance`, qui compare les deux candidats sur le même critère.)

    CE QUE TU DOIS FAIRE :
        étape 1 : mets le message en lettres seules :
                      lettres = vider_les_espaces(message)
                  (ni espaces ni ponctuation : on veut comparer des lettres) ;
        étape 2 : attaque-le par les deux méthodes :
                      cle_scytale, texte_scytale = attaque_scytale(lettres)
                      cle_cesar, texte_cesar = forcer_cesar(lettres)
        étape 3 : compare les deux candidats :
                      if vraisemblance(texte_scytale) > vraisemblance(texte_cesar):
                          return ("SCYTALE", cle_scytale, texte_scytale)
                      return ("CESAR", cle_cesar, texte_cesar)
        étape 4 : c'est fini !  Trois valeurs sont renvoyées : la méthode
                  (« SCYTALE » ou « CESAR »), la clef et le texte clair.

    RAPPELS PYTHON :
        * tu appelles tes propres fonctions : c'est fait pour ;
        * une fonction peut renvoyer trois valeurs : `return (a, b, c)` ;
        * on les relira ainsi : `methode, cle, texte = identifier_et_dechiffrer(m)`.

    EXEMPLES (ce que les tests vérifient) :
        m = scytale_chiffrer("LERENDEZVOUSESTFIXEAMIDI", 4)
        identifier_et_dechiffrer(m)  ->  ("SCYTALE", 4, "LERENDEZVOUSEST...")
        m = cesar_chiffrer("LE MESSAGE ARRIVE CE SOIR", 17)
        identifier_et_dechiffrer(m)  ->  ("CESAR", 17, "LE MESSAGE ARRIVE...")

    CE QUE TU VAS EN FAIRE : les trois messages MYSTÈRE de ce TP.  Pour chacun,
    cette seule fonction doit te dire la méthode, la clef ET le texte.
    """
    # --- À COMPLÉTER ---
    lettres = vider_les_espaces(...)                   # lettres seulement

    cle_scytale, texte_scytale = attaque_scytale(...)  # hypothèse 1
    cle_cesar, texte_cesar = forcer_cesar(...)         # hypothèse 2

    if vraisemblance(...) > vraisemblance(...):        # lequel est le plus français ?
        return ("SCYTALE", ..., ...)
    return ("CESAR", ..., ...)

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     lettres = vider_les_espaces(message)
    #
    #     cle_scytale, texte_scytale = attaque_scytale(lettres)
    #     cle_cesar, texte_cesar = forcer_cesar(lettres)
    #
    #     if vraisemblance(texte_scytale) > vraisemblance(texte_cesar):
    #         return ("SCYTALE", cle_scytale, texte_scytale)
    #     return ("CESAR", cle_cesar, texte_cesar)
    # ----------------------------------------------------------------------


# ###########################################################################
#
#  § C (suite) — LES MESSAGES INTERCEPTÉS
#
#  Voici les cinq messages que tu dois casser.  AUCUNE CLEF N'EST DONNÉE.
#
#    MESSAGE_SCYTALE   chiffré par scytale       -> attaque_scytale
#    MESSAGE_CESAR     chiffré par César         -> forcer_cesar
#    MESSAGE_MYSTERE_1 méthode INCONNUE          -> identifier_et_dechiffrer
#    MESSAGE_MYSTERE_2 méthode INCONNUE          -> identifier_et_dechiffrer
#    MESSAGE_MYSTERE_3 méthode INCONNUE          -> identifier_et_dechiffrer
#
#  Comment s'en servir ?  Dans l'interpréteur Python (commande `python3`) :
#
#      >>> from tp1_permutation import *
#      >>> attaque_scytale(MESSAGE_SCYTALE)
#      >>> forcer_cesar(MESSAGE_CESAR)
#      >>> methode, cle, texte = identifier_et_dechiffrer(MESSAGE_MYSTERE_1)
#      >>> print(methode, cle)
#      >>> print(texte)
#
#  Les épreuves vérifient automatiquement que tu as trouvé la bonne méthode, la
#  bonne clef et le bon texte : tu n'as donc pas besoin de recopier les réponses
#  dans un coin, il suffit que tes fonctions soient justes.
#
#  (Ces constantes sont remplies par le professeur : ne les modifie pas, c'est
#  le message intercepté.)

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


# ###########################################################################
#
#  § D — SUPPLÉMENT : LA LEÇON DE MARIE STUART (à lire, pas de code)
#
#  En 1586, Marie Stuart, prisonnière d'Élisabeth d'Angleterre, correspond avec
#  ses partisans par un chiffre de substitution que les services de la reine
#  savent déjà décoder — les mathématiques du chiffre sont donc percées, mais
#  Marie l'ignore.  Les espions obtiennent bien plus que le texte : en 1587, ils
#  glissent dans un courrier une phrase que Marie reprend presque mot pour mot,
#  ce qui donne la « preuve » de sa participation au complot.  Elle est
#  condamnée et exécutée.
#
#  Trois leçons, qui sont exactement celles du cours :
#
#   1. LA MÉTHODE FINIT TOUJOURS PAR ÊTRE CONNUE.  C'est le principe de
#      Kerckhoffs : toute la sécurité doit tenir dans la CLEF, jamais dans le
#      secret du système.  C'est pourquoi, dans ce TP, tu connais entièrement le
#      code (scytale, César) et que tu dois quand même retrouver la clef.
#
#   2. LE POINT FAIBLE EST SOUVENT HUMAIN.  Un code qui ne transmet aucun
#      message compromettant, mais qui sert à en fabriquer — c'est le principe
#      des « lettres de la fourche ».
#
#   3. ON VÉRIFIE TOUJOURS QUI A PARLÉ.  Vérifier qu'une phrase donnée figure
#      bien dans un document, sans se laisser tromper par les espaces, les
#      majuscules ou la ponctuation, est une brique de ce qu'on appelle
#      aujourd'hui un code d'authentification (MAC, chapitre 6 du cours).
#
#  Question de rapport n° 5 : à ton avis, pourquoi la sécurité d'un système
#  cryptographique ne doit-elle JAMAIS reposer sur le secret de son
#  fonctionnement ?  Réponds en t'appuyant sur ce que tu viens de faire dans ce
#  TP (tu connaissais le code, et cela ne t'a pas empêché de casser les
#  messages).
#
# ###########################################################################


# ###########################################################################
#
#  § E — EXPÉRIENCES À FAIRE DANS L'INTERPRÉTEUR PYTHON
#
#  Lance `python3`, puis tape les instructions ci-dessous (recopie-les, et
#  observe).  Ces expériences sont la partie « méthode scientifique » du TP :
#  c'est ainsi que l'on choisit son instrument de mesure.
#
# ###########################################################################
#
# EXPÉRIENCE 1 — vérifier que la scytale ne change pas les fréquences
#     >>> from tp1_permutation import *
#     >>> clair = "LEGRANDMESSAGERARRIVECETTEAPRESMIDI"
#     >>> chiffre = scytale_chiffrer(clair, 7)
#     >>> comptage(clair)["E"], comptage(chiffre)["E"]
#     Réponse : les deux comptent le même nombre de E.
#     Conclusion à écrire dans ton rapport : comparer les fréquences ne peut
#     pas départager les candidats d'une scytale.  Il faut autre chose.
#
# EXPÉRIENCE 2 — et cet autre chose, c'est l'ordre des lettres
#     >>> vraisemblance(clair)
#     >>> vraisemblance(chiffre)
#     La note du texte clair est plus grande (moins négative) que celle du texte
#     chiffré : c'est le critère utilisé dans C.1.
#
# EXPÉRIENCE 3 — l'analyse de fréquences « à la main » sur MESSAGE_CESAR
#     >>> from outils.texte_francais import tableau_lettres, frequences_du_francais
#     >>> print(tableau_lettres(compter_lettres(MESSAGE_CESAR)))
#     >>> print(tableau_lettres(frequences_du_francais(), en_pourcentage=True))
#     Compare les deux tableaux : la lettre la plus fréquente du message chiffré
#     est le « E du français » décalé.  De combien de cases ?  C'est la clef !
#     Compare ensuite avec ce que te donne forcer_cesar.
#
# EXPÉRIENCE 4 — voir les 26 distances du message César
#     >>> for cle in range(26):
#     ...     candidat = cesar_dechiffrer(MESSAGE_CESAR, cle)
#     ...     print(cle, round(distance_au_francais(candidat), 1), candidat[:30])
#     La ligne dont la distance est la plus PETITE est la bonne clef.
#
# EXPÉRIENCE 5 — les messages mystères, en une ligne
#     >>> for message in (MESSAGE_MYSTERE_1, MESSAGE_MYSTERE_2, MESSAGE_MYSTERE_3):
#     ...     methode, cle, texte = identifier_et_dechiffrer(message)
#     ...     print(methode, cle, texte[:50])
#
# ###########################################################################
#
#  § F — QUESTIONS DE RAPPORT (à rédiger et à rendre avec le fichier)
#
#  Réponds en trois ou quatre phrases par question, en t'appuyant sur ce que tu
#  as observé.  Écris tes réponses dans un fichier texte à part, ou à la main.
#
# ###########################################################################
#
# QUESTION 1. Pourquoi les fréquences des lettres d'un texte chiffré par la
# scytale sont-elles exactement celles du texte clair ?  Quelle conséquence
# pour la cryptanalyse ?  (Expérience 1.)
#
# QUESTION 2. Explique, avec tes mots, la différence entre les deux instruments
# de mesure `vraisemblance` et `distance_au_francais`, et pourquoi l'un ne peut
# pas remplacer l'autre.  (Expériences 1, 2 et 4.)
#
# QUESTION 3. Combien y a-t-il de clefs possibles pour un message de 40 lettres
# chiffré par la scytale ?  (Utilise ton programme :
# len(cle_scytale_possibles(40)).)  Compare avec les 26 clefs de César : lequel
# des deux chiffres est le plus solide du point de vue du nombre de clefs ?
#
# QUESTION 4. Pour chacun des trois messages MYSTÈRE, indique la méthode, la
# clef et les dix premières lettres du texte clair.  Comment ton programme a-t-il
# décidé ?  (Réponse attendue : en comparant les deux candidats avec
# `vraisemblance`, et non au hasard.)
#
# QUESTION 5. Dans l'expérience 3, de combien de cases fallait-il décaler la
# lettre la plus fréquente pour la faire coïncider avec le E du français ?
# Retrouves-tu la clef donnée par forcer_cesar ?  Que se passerait-il si le
# message était très court (par exemple vingt lettres) ?
#
# QUESTION 6. Marie Stuart (supplément § D) : pourquoi le fait que ses ennemis
# connaissaient son code n'était-il pas, à lui seul, un désastre ?  Et pourquoi
# cela serait-il inacceptable aujourd'hui, où l'on publie les algorithmes ?
#


if __name__ == "__main__":
    # Cette partie s'exécute quand on lance :   python3 tp1_permutation.py
    # Elle sert à vérifier d'un coup d'œil où tu en es.

    def _inacheve(valeur):
        """Vrai si la fonction n'est pas finie : il reste des « ... » ou rien.

        On regarde aussi à l'intérieur des couples renvoyés, car certaines
        fonctions renvoient plusieurs valeurs à la fois (la clef ET le texte).
        """
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

    print("Voici où tu en es dans tes six fonctions :")
    print("  --- § B : le code à écrire ---")
    _essai("B.1 compter_lettres('BONJOUR')['O']",
           lambda: compter_lettres("BONJOUR")["O"])
    _essai("B.2 cesar_chiffrer('AVE', 3)",
           lambda: cesar_chiffrer("AVE", 3))
    _essai("B.3 cesar_dechiffrer('ERQMRXU, OH PRQGH', 3)",
           lambda: cesar_dechiffrer("ERQMRXU, OH PRQGH", 3))
    print("  --- § C : ★ cryptanalyse ★ ---")
    _essai("C.1 attaque_scytale(MESSAGE_SCYTALE)",
           lambda: attaque_scytale(MESSAGE_SCYTALE))
    _essai("C.2 forcer_cesar(MESSAGE_CESAR)",
           lambda: forcer_cesar(MESSAGE_CESAR))
    _essai("C.3 identifier_et_dechiffrer(MESSAGE_MYSTERE_1)",
           lambda: identifier_et_dechiffrer(MESSAGE_MYSTERE_1))
    print()
    print("Quand tout est écrit, lance les épreuves :")
    print("    python3 test_tp1_permutation.py")
