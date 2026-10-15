"""==========================================================================
 TP 1 — GÉNÉRALITÉS ET CODES SIMPLES
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
   2. Neuf exercices, à faire dans l'ordre .......................... § B
   3. Des expériences à faire dans l'interpréteur Python ............. § C
   4. Des questions de rapport ....................................... § D

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
   5. recommence jusqu'à ce que les neuf fonctions soient [OK].

RÈGLE D'OR : ne modifie jamais les fichiers `test_tp1_permutation.py` ni le
dossier `outils/` : ils appartiennent au professeur. Tu peux en revanche lire
`outils/reference.py` autant que tu veux, il est commenté ligne par ligne.

LES SEPT FONCTIONS À ÉCRIRE
---------------------------
   A.1  nettoyer_simple            A.2  compter_lettres
   B.1  cle_scytale_possibles      B.2  decouper_en_morceaux    B.3  attaque_scytale
   C.1  cesar_chiffrer             C.2  cesar_dechiffrer        C.3  forcer_cesar
   D.1  message_compromis
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

# Cette ligne va chercher, dans le dossier du TP, les outils DÉJÀ ÉCRITS par le
# professeur.  On utilisera surtout :
#   * ALPHABET          : la chaîne "ABCDEFGHIJKLMNOPQRSTUVWXYZ" ;
#   * nettoyer(texte)   : met en majuscules et enlève accents et ponctuation ;
#   * comptage(texte)   : compte les 26 lettres d'un texte ;
#   * scytale_chiffrer / scytale_dechiffrer : le code de permutation, fourni.
from common import ALPHABET, comptage, nettoyer, scytale_chiffrer, scytale_dechiffrer

# Et voici les trois outils de cryptanalyse que le professeur t'offre :
#   * distance_au_francais(texte) : écart entre les fréquences du texte et
#     celles du français. PLUS LA VALEUR EST PETITE, plus le texte ressemble à
#     du français. Sert à l'exercice C.3.
#   * vraisemblance(texte)        : note fondée sur l'ORDRE des lettres.
#     PLUS LA VALEUR EST GRANDE, plus le texte ressemble à du français. Sert à
#     l'exercice B.3.
#   * frequences_du_francais()    : le modèle du français (pour information).
from outils.texte_francais import (
    distance_au_francais,
    frequences_du_francais,
    tableau_lettres,
    vraisemblance,
)


# ###########################################################################
#
#  § A — MINI-COURS DE PYTHON : LES DIX GESTES DONT TU AS BESOIN
#
#  Ce n'est pas un cours complet : ce sont exactement les outils utilisés dans
#  les neuf exercices. Tu peux revenir ici à tout moment.
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
#  § B — LES NEUF EXERCICES
#
# ###########################################################################


# ==========================================================================
# PARTIE A — PRÉPARER LE TEXTE
# ==========================================================================

def nettoyer_simple(texte):
    """A.1 — OBJECTIF : mettre le texte en MAJUSCULES et ne garder que les
    lettres de A à Z (les espaces, la ponctuation, les chiffres et les accents
    compliqués sont enlevés).

    POURQUOI (COURS) : tous les codes anciens du cours travaillent sur les
    mêmes 26 lettres.  Avant de chiffrer, il faut donc « ranger » le message :
    plus d'espaces, plus d'accents, tout en majuscules.  C'est ce que faisaient
    les opérateurs avec leurs tableaux de chiffrement.

    CE QUE TU DOIS FAIRE :
        étape 1 : mets le texte en majuscules ;
        étape 2 : prépare une chaîne vide qui recevra le résultat ;
        étape 3 : parcours le texte caractère par caractère ;
        étape 4 : si le caractère est une lettre de "A" à "Z", ajoute-le à la
                  fin du résultat ; sinon, ne fais rien (le caractère disparaît) ;
        étape 5 : renvoie le résultat.

    RAPPELS PYTHON :
        * `texte.upper()` met en majuscules ;
        * `for caractere in texte:` parcourt les caractères ;
        * `if "A" <= caractere <= "Z":` teste si c'est une lettre ;
        * `resultat += caractere` ajoute le caractère à la fin du résultat ;
        * `return resultat` renvoie le résultat.

    EXEMPLES (ce que les tests vérifient) :
        nettoyer_simple("Bonjour, le monde !")      ->  "BONJOURLEMONDE"
        nettoyer_simple("Le chat mange, en 2026.")  ->  "LECHATMANGEEN"
    """
    # --- À COMPLÉTER : remplace les ... en suivant les commentaires ---
    texte = ...                                       # utilise la méthode .upper()
    resultat = ...                                    # une chaîne vide : ""
    for caractere in ...:                             # parcours le texte
        if ...:                                       # teste "A" <= caractere <= "Z"
            resultat += ...                           # ajoute le caractère
    return ...                                        # renvoie le résultat

    # ----------------------------------------------------------------------
    # ✅ SOLUTION (recopie ces lignes dans la fonction pour corriger)
    # ----------------------------------------------------------------------
    #     texte = texte.upper()
    #     resultat = ""
    #     for caractere in texte:
    #         if "A" <= caractere <= "Z":
    #             resultat += caractere
    #     return resultat
    # ----------------------------------------------------------------------


def compter_lettres(texte):
    """A.2 — OBJECTIF : compter combien de fois chaque lettre apparaît.

    POURQUOI (COURS) : c'est LE geste de la cryptanalyse par analyse de
    fréquences.  Le cryptanalyste arabe du IXe siècle comptait les lettres du
    message intercepté ; c'est ce comptage qui révèle les régularités du
    français.

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


# ==========================================================================
# PARTIE B — LE CODE DE PERMUTATION (SCYTALE) ET SON ATTAQUE
# ==========================================================================
#
# RAPPEL DU COURS.  Dans un code de PERMUTATION, on ne remplace aucune lettre :
# on les DÉPLACE.  La scytale des Spartiates fait cela : on enroule une lanière
# de cuir autour d'un bâton de t colonnes, on écrit le message dans le sens de
# la longueur, et on le lit en colonnes.  Les fonctions `scytale_chiffrer` et
# `scytale_dechiffrer` sont déjà écrites dans `common.py` : regarde-les, elles
# sont commentées.
#
# CONSÉQUENCE FONDAMENTALE (à comprendre, c'est tout l'exercice) :
#     les fréquences des lettres du texte chiffré sont EXACTEMENT celles du
#     texte clair, puisque aucune lettre n'a changé !
#
# Donc, pour casser une scytale, il est INUTILE de comparer les fréquences :
# tous les candidats ont les mêmes comptes de lettres.  Ce qui change d'un
# candidat à l'autre, c'est l'ORDRE des lettres.  Or, en français, certains
# enchaînements sont fréquents (« ES », « LE », « DE », « NT »...) et d'autres
# presque impossibles (« XZ », « QK »...).  C'est ce que mesure la fonction
# `vraisemblance` : plus sa valeur est GRANDE, plus l'enchaînement des lettres
# ressemble à du français.  Un vrai texte français tourne autour de -5, un
# charabia descend vers -6.


def cle_scytale_possibles(longueur):
    """B.1 — OBJECTIF : donner la liste des clefs t qu'il est raisonnable
    d'essayer pour un texte chiffré de `longueur` caractères.

    POURQUOI (COURS) : attaquer un code, c'est d'abord savoir combien de clefs
    existent.  Ici, la clef est le nombre de lettres par ligne, t.  Une clef
    n'est possible que si :
        * t divise la longueur du texte (sinon on ne peut pas remplir le
          tableau : la scytale exige un nombre entier de lignes) ;
        * t vaut au moins 2 (t = 1 ne mélange rien du tout) ;
        * le tableau a au moins 5 lignes, donc t <= longueur // 5 (en dessous,
          le tableau est trop écrasé pour que le message soit vraiment brouillé).

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare une liste vide : `possibles = []` ;
        étape 2 : parcours tous les entiers t de 2 à longueur :
                      for t in range(2, longueur + 1):
        étape 3 : si `longueur % t == 0` ET si `longueur // t >= 5`, alors
                  ajoute t à la liste : `possibles.append(t)` ;
        étape 4 : renvoie la liste.

    RAPPELS PYTHON :
        * `%` donne le reste : `40 % 4` vaut 0, donc 4 divise 40 ;
        * `//` donne la division entière : `40 // 4` vaut 10 (il y a 10 lignes) ;
        * `et` se dit `and` en Python : `if longueur % t == 0 and longueur // t >= 5:` ;
        * `liste.append(t)` ajoute t à la fin de la liste.

    EXEMPLES (ce que les tests vérifient) :
        cle_scytale_possibles(40)  ->  [2, 4, 5, 8]
        cle_scytale_possibles(35)  ->  [5, 7]
        cle_scytale_possibles(9)   ->  []
    """
    # --- À COMPLÉTER ---
    possibles = ...                                   # une liste vide : []
    for t in range(2, ...):                           # de 2 à longueur inclus
        if longueur % t == ... and longueur // t >= ...:
            possibles.append(...)                     # ajoute t à la liste
    return ...                                        # renvoie la liste

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     possibles = []
    #     for t in range(2, longueur + 1):
    #         if longueur % t == 0 and longueur // t >= 5:
    #             possibles.append(t)
    #     return possibles
    # ----------------------------------------------------------------------


def decouper_en_morceaux(texte, taille):
    """B.2 — OBJECTIF : découper un texte en morceaux de `taille` caractères.

    POURQUOI (COURS) : cette petite fonction servira à lire un texte chiffré
    « en lignes de t lettres », exactement comme l'opérateur qui enroule sa
    lanière autour du bâton.  On la retrouvera aussi au TP 2 pour compter des
    fréquences par colonnes.

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare une liste vide : `morceaux = []` ;
        étape 2 : parcours les positions de début, de 3 en 3 si la taille vaut 3 :
                  `for debut in range(0, len(texte), taille):`
        étape 3 : prends l'extrait qui commence en `debut` et qui fait `taille`
                  caractères : `texte[debut:debut + taille]`
                  (le découpage par crochets s'arrête AVANT la fin donnée) ;
        étape 4 : ajoute cet extrait à la liste ;
        étape 5 : renvoie la liste.

    RAPPELS PYTHON :
        * `range(0, len(texte), taille)` donne 0, taille, 2*taille... : ce sont
          les positions de départ de chaque morceau ;
        * `texte[debut:debut + taille]` extrait les `taille` caractères ;
        * le dernier morceau peut être plus court : c'est normal (il sera
          complété par des X au moment du chiffrement).

    EXEMPLES (ce que les tests vérifient) :
        decouper_en_morceaux("ABCDEFGH", 3)  ->  ["ABC", "DEF", "GH"]
        decouper_en_morceaux("ABCDEF", 3)    ->  ["ABC", "DEF"]
    """
    # --- À COMPLÉTER ---
    morceaux = ...                                    # une liste vide
    for debut in range(0, ..., taille):               # les positions de départ
        extrait = texte[debut:...]                    # les `taille` caractères
        morceaux.append(...)                          # ajoute l'extrait
    return ...                                        # renvoie la liste

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     morceaux = []
    #     for debut in range(0, len(texte), taille):
    #         extrait = texte[debut:debut + taille]
    #         morceaux.append(extrait)
    #     return morceaux
    # ----------------------------------------------------------------------


def attaque_scytale(chiffre):
    """B.3 — OBJECTIF : retrouver le message clair SANS CONNAÎTRE LA CLEF.

    POURQUOI (COURS) : c'est le cœur de la cryptanalyse.  On ne connaît ni le
    message, ni la clef : on a seulement le texte intercepté.  La méthode est
    la « recherche exhaustive » : on essaie toutes les clefs possibles, et l'on
    garde le candidat qui ressemble le plus à du français.

    COMMENT RECONNAÎTRE LE BON CANDIDAT ? (réfléchis, c'est le point clé)
        * comparer les FRÉQUENCES ne marche pas : la scytale n'a changé aucune
          lettre, donc tous les candidats ont les mêmes comptes de lettres ;
        * ce qui change, c'est l'ORDRE des lettres.  On utilise donc la fonction
          `vraisemblance`, qui note l'enchaînement des lettres.  Dans un vrai
          texte français, on trouve partout « ES », « LE », « DE », « NT » ;
          dans un charabia, non.  PLUS LA VALEUR EST GRANDE (donc moins
          négative), PLUS LE TEXTE RESSEMBLE À DU FRANÇAIS.

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


# ==========================================================================
# PARTIE C — LE CODE DE SUBSTITUTION : CÉSAR
# ==========================================================================
#
# RAPPEL DU COURS.  Cette fois, on REMPLACE chaque lettre par une autre : la
# lettre de rang n devient la lettre de rang (n + cle) mod 26.  Avec la clef 3 :
# A devient D, B devient E, ..., Z revient à C.
#
# POURQUOI L'ANALYSE DE FRÉQUENCES MARCHE ICI (et pas avec la scytale) : chaque
# lettre du clair est toujours remplacée par LA MÊME lettre du chiffré.  Le E du
# français (environ 15 % du texte) reste donc la lettre la plus fréquente du
# message chiffré, simplement décalée.  En comparant les deux histogrammes, on
# devine le décalage.
#
# ATTENTION À UN PIÈGE CLASSIQUE : l'indice de coïncidence (que tu verras au
# TP 2 et au TP 3) est LE MÊME pour les 26 décalages : inutile pour César.  Ce
# qui permet de trancher, c'est de comparer les fréquences lettre par lettre
# avec celles du français : c'est ce que fait `distance_au_francais`.


def cesar_chiffrer(texte, cle):
    """C.1 — OBJECTIF : chiffrer un texte avec le code de César de clef `cle`.

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
    """C.2 — OBJECTIF : déchiffrer un message chiffré par César.

    POURQUOI C'EST FACILE (et important) : déchiffrer, c'est décaler dans
    l'autre sens, donc de -cle.  Et comme « reculer de 3 » revient au même que
    « avancer de 23 » (3 + 23 = 26), on peut réutiliser exactement la fonction
    précédente avec le décalage `(-cle) % 26`.

    CE QUE TU DOIS FAIRE :
        écris UNE SEULE ligne, qui appelle la fonction C.1 :
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


def forcer_cesar(texte_chiffre):
    """C.3 — OBJECTIF : retrouver la clef et le message SANS CONNAÎTRE LA CLEF.

    POURQUOI (COURS) : il n'y a que 26 clefs possibles.  On les essaie donc
    toutes, et l'on garde celle qui donne le texte le plus proche du français.
    Mais « le plus proche » doit se mesurer : c'est le rôle de la fonction
    `distance_au_francais`, qui compare les fréquences du candidat à celles du
    français.  PLUS LA DISTANCE EST PETITE, plus le texte ressemble à du
    français.

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
                  MEILLEURE (donc plus petite) que la précédente, mets à jour
                  les trois boîtes (comme pour la scytale, mais dans l'autre
                  sens : ici on cherche la plus PETITE valeur) ;
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


# ==========================================================================
# PARTIE D — HISTOIRE, KERCKHOFFS ET MESSAGES TRUQUÉS
# ==========================================================================

def message_compromis(message_clair, texte_chiffre_saisi):
    """D.1 — OBJECTIF : vérifier qu'un message chiffré contient bien la phrase
    que l'on croit y voir, en ignorant majuscules, espaces et ponctuation.

    POURQUOI (COURS ET HISTOIRE) : en 1587, Marie Stuart correspondait avec ses
    partisans par un chiffre qu'Élisabeth d'Angleterre connaissait.  Les
    services de la reine glissèrent dans un message une phrase que Marie ne
    pouvait que reprendre, presque mot pour mot : une « lettre de la fourche »
    qui servit de preuve à son procès.  Pour que le piège fonctionne, il faut
    pouvoir vérifier automatiquement qu'une phrase donnée se retrouve dans un
    document, quelles que soient la casse et la ponctuation.  C'est exactement
    le principe des codes d'authentification (MAC) vus en fin de cours.

    CE QUE TU DOIS FAIRE :
        étape 1 : nettoie les deux textes avec ta fonction A.1, appelée ici
                  `nettoyer_simple` (elle enlève espaces, accents et
                  ponctuation, et met en majuscules) ;
        étape 2 : teste si le message nettoyé se trouve DANS le document
                  nettoyé, avec l'opérateur `in` :
                      "DE" in "ABDE"   ->  True   (vrai)
                      "FUITE" in "ATTAQUE"  ->  False  (faux)
        étape 3 : renvoie le résultat (True ou False).

    RAPPELS PYTHON (le squelette est écrit juste en dessous, complète les trous) :
        * `nettoyer_simple(message_clair)` : appel de ta fonction A.1 ;
        * `in` teste l'appartenance ; `True` et `False` sont les deux booléens.

    EXEMPLES (ce que les tests vérifient) — le document intercepté est un
    mélange de texte chiffré et d'une phrase restée en clair, comme dans le
    piège historique :

        document = "XWWD TXH, O'DSSURFKH. ATTAQUE A L'AUBE, PREVENEZ LE BATELIER."
        message_compromis("ATTAQUE A L AUBE", document)  ->  True
        message_compromis("FUITE", document)             ->  False
    """
    # --- À COMPLÉTER ---
    message_propre = ...                               # nettoie le message clair
    document_propre = ...                              # nettoie le document saisi
    reponse = ...                                      # teste l'appartenance avec `in`
    return reponse                                     # renvoie True ou False

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     message_propre = nettoyer_simple(message_clair)
    #     document_propre = nettoyer_simple(texte_chiffre_saisi)
    #     return message_propre in document_propre
    # ----------------------------------------------------------------------


# ==========================================================================
# PARTIE E — DEUX MESSAGES À DÉCRYPTER POUR DE VRAI
# ==========================================================================
#
# Ces deux messages ont été chiffrés par ton professeur : l'un avec la scytale,
# l'autre avec César.  LES CLEFS SONT INCONNUES !  C'est ton travail des parties
# B et C qui va les retrouver.
#
# Pour les déchiffrer, écris dans l'interpréteur Python (commande `python3`) :
#
#     >>> from tp1_permutation import *
#     >>> attaque_scytale(MESSAGE_SCYTALE)
#     >>> forcer_cesar(MESSAGE_CESAR)
#
# (Les deux constantes ci-dessous sont remplies par le professeur : ne les
# modifie pas, c'est le message intercepté.)

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


# ###########################################################################
#
#  § C — EXPÉRIENCES À FAIRE DANS L'INTERPRÉTEUR PYTHON
#
#  Lance `python3`, puis tape les instructions ci-dessous (recopie-les, et
#  observe).  Ces expériences sont la partie « cryptanalyse » du programme.
#
# ###########################################################################
#
# EXPÉRIENCE 1 — la scytale ne change pas les fréquences
#     >>> from tp1_permutation import *
#     >>> clair = "LEGRANDMESSAGERARRIVECETTEAPRESMIDI"
#     >>> chiffre = scytale_chiffrer(clair, 7)
#     >>> comptage(clair)["E"], comptage(chiffre)["E"]
#     Réponse : les deux comptent le même nombre de E.  Conclusion : comparer
#     les fréquences ne peut pas départager les candidats d'une scytale.
#
# EXPÉRIENCE 2 — ce qui distingue le bon candidat, c'est l'ordre
#     >>> vraisemblance(clair)
#     >>> vraisemblance(chiffre)
#     La note du texte clair est plus grande (moins négative) : c'est le critère
#     utilisé dans B.3.
#
# EXPÉRIENCE 3 — voir les fréquences du message César intercepté
#     >>> print(tableau_lettres(comptage(MESSAGE_CESAR)))
#     >>> print(tableau_lettres(frequences_du_francais(), en_pourcentage=True))
#     Compare les deux tableaux : la lettre la plus fréquente du message
#     chiffré est le « E du français » décalé.  De combien de cases ?  C'est la
#     clef !  (C'est l'analyse de fréquences historique ; la fonction C.3 le fait
#     automatiquement.)
#
# EXPÉRIENCE 4 — voir les 26 distances du message César
#     >>> for cle in range(26):
#     ...     candidat = cesar_dechiffrer(MESSAGE_CESAR, cle)
#     ...     print(cle, round(distance_au_francais(candidat), 1), candidat[:30])
#     La ligne dont la distance est la plus PETITE est la bonne clef.
#
# ###########################################################################
#
#  § D — QUESTIONS DE RAPPORT (à rédiger et à rendre avec le fichier)
#
#  Réponds en trois ou quatre phrases par question, en t'appuyant sur ce que tu
#  as observé.  Écris tes réponses dans un fichier texte à part, ou à la main.
#
# ###########################################################################
#
# QUESTION 1. Pourquoi les fréquences des lettres d'un texte chiffré par la
# scytale sont-elles exactement celles du texte clair ?  Quelle conséquence
# pour la cryptanalyse ?
#
# QUESTION 2. Combien y a-t-il de clefs possibles pour un message de 40 lettres
# chiffré par la scytale ?  (Utilise ton programme : len(cle_scytale_possibles(40)).)
# Que peut-on en conclure sur le coût de l'attaque ?
#
# QUESTION 3. Dans l'expérience 3, de combien de cases fallait-il décaler la
# lettre la plus fréquente pour la faire coïncider avec le E du français ?
# Retrouve-t-on la clef trouvée par forcer_cesar ?
#
# QUESTION 4. Deux méthodes pour reconnaître du français ont été utilisées :
# la vraisemblance (B.3) et la distance au français (C.3).  Pourquoi ne peut-on
# pas les échanger ?  (Relis les rappels du cours au début des parties B et C.)
#
# QUESTION 5. Qu'est-ce que le principe de Kerckhoffs, et en quoi ce TP le
# respecte-t-il ?  (Indice : tu connais le fonctionnement de la scytale et de
# César, et pourtant tu dois retrouver la clef.)
#
# QUESTION 6. Le code de César a 26 clefs, la scytale en a une poignée : ces
# chiffres sont-ils solides ?  Explique en une phrase ce qui rend un chiffre
# « solide » du point de vue du nombre de clefs.
#


if __name__ == "__main__":
    # Cette partie s'exécute quand on lance :   python3 tp1_permutation.py
    # Elle sert à vérifier d'un coup d'œil où tu en es.

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

    print("Voici où tu en es dans tes neuf fonctions :")
    _essai("A.1 nettoyer_simple('Bonjour, le monde !')",
           lambda: nettoyer_simple("Bonjour, le monde !"))
    _essai("A.2 compter_lettres('BONJOUR')['O']",
           lambda: compter_lettres("BONJOUR")["O"])
    _essai("B.1 cle_scytale_possibles(40)",
           lambda: cle_scytale_possibles(40))
    _essai("B.2 decouper_en_morceaux('ABCDEFGH', 3)",
           lambda: decouper_en_morceaux("ABCDEFGH", 3))
    _essai("B.3 attaque_scytale(MESSAGE_SCYTALE)",
           lambda: attaque_scytale(MESSAGE_SCYTALE))
    _essai("C.1 cesar_chiffrer('AVE', 3)",
           lambda: cesar_chiffrer("AVE", 3))
    _essai("C.2 cesar_dechiffrer('ERQMRXU, OH PRQGH', 3)",
           lambda: cesar_dechiffrer("ERQMRXU, OH PRQGH", 3))
    _essai("C.3 forcer_cesar(MESSAGE_CESAR)",
           lambda: forcer_cesar(MESSAGE_CESAR))
    _essai("D.1 message_compromis('ATTAQUE A L AUBE', document)",
           lambda: message_compromis(
               "ATTAQUE A L AUBE",
               "XWWD TXH, O'DSSURFKH. ATTAQUE A L'AUBE, PREVENEZ LE BATELIER."))

    print()
    print("Quand tout est écrit, lance les épreuves :")
    print("    python3 test_tp1_permutation.py")
