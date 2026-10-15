"""==========================================================================
 TP 1 — GÉNÉRALITÉS ET CODES SIMPLES
 Chapitre 1 (définition d'un code) et chapitre 2 (codes de permutation,
 codes de substitution, cryptanalyse) — Pascal Boyer, « Cryptographie 2013 ».

 Durée conseillée : 2 h.   À rendre : ce fichier complété.
==========================================================================

COMMENT TRAVAILLER
------------------
  1. Ouvrez un terminal dans le dossier du TP.
  2. Après avoir écrit une fonction (une seule à la fois), lancez :

         python3 test_tp1_permutation.py

     Les épreuves réussies s'affichent « [OK] », les autres « [ÉCHEC] » avec
     la raison exacte.  Vous pouvez relancer autant de fois que vous voulez.

  3. Vous pouvez toujours essayer votre code dans l'interpréteur :

         python3
         >>> from tp1_permutation import *
         >>> cesar_chiffrer("AVE", 3)

RAPPELS DU COURS UTILISÉS ICI
-----------------------------
  * Un code est la donnée de deux ensembles de mots (P les mots en clair, C les
    mots codés), d'un espace de clefs K, et de deux règles e_k (chiffrement) et
    d_k (déchiffrement) telles que d_k(e_k(x)) = x pour tout x de P.
  * Code de permutation : on ne change pas les lettres, on les déplace (scytale).
  * Code de substitution : on change chaque lettre en une autre (César).
  * Cryptanalyse : on ne connaît pas la clef ; on utilise les régularités de la
    langue (fréquences des lettres, par exemple) pour la retrouver.

CE QUE VOUS DEVEZ ÉCRIRE (neuf fonctions, dans l'ordre)
-------------------------------------------------------
  A.1  nettoyer_simple          A.2  compter_lettres
  B.1  cle_scytale_possibles    B.2  decouper_en_morceaux     B.3  attaque_scytale
  C.1  cesar_chiffrer           C.2  cesar_dechiffrer         C.3  forcer_cesar
  D.1  message_compromis
==========================================================================
"""

# On utilise le fichier common.py de ce dossier : il contient le code de la
# scytale (déjà écrit) et deux fonctions utilitaires.  NE LE MODIFIEZ PAS.
from common import ALPHABET, comptage, nettoyer, scytale_chiffrer, scytale_dechiffrer

# Pour l'épreuve finale de cryptanalyse du code de César.
# `distance_au_francais` compare les fréquences des lettres d'un texte à celles
# du français : plus le résultat est petit, plus le texte ressemble à du
# français.  C'est l'outil de la question C.3 ; vous pouvez lire son aide dans
# outils/texte_francais.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from outils.texte_francais import (  # noqa: E402
    distance_au_francais,
    frequences_du_francais,
    tableau_lettres,
    vraisemblance,
)


# ==========================================================================
# BOÎTE À OUTILS PYTHON (pour les débutants : ce sont des rappels de cours)
# ==========================================================================
#
#   Chaîne de caractères (str) : suite de caracteres entre guillemets.
#       "BONJOUR"        len("BONJOUR") -> 7      "BONJOUR"[0] -> "B"
#       majuscules = texte.upper()
#       boucle : for caractere in texte:
#
#   Comparer deux caractères :
#       "A" <= caractere <= "Z"     est vrai si caractere est une lettre simple
#
#   Ajouter à la fin d'une chaîne :
#       resultat = ""
#       resultat += "A"            # resultat vaut maintenant "A"
#
#   Trouver la position d'une lettre dans l'alphabet :
#       ALPHABET.index("C")    -> 2
#   Et l'inverse :
#       ALPHABET[2]            -> "C"
#
#   Le reste d'une division s'écrit avec le symbole % :
#       29 % 26  -> 3        (29 = 1 * 26 + 3)
#       -3 % 26  -> 23       (Python renvoie toujours un reste entre 0 et 25)
#
#   Listes :
#       liste = []             liste vide
#       liste.append(3)        ajoute 3 à la fin
#       liste[0]               premier élément
#       liste[-1]              dernier élément
#       for valeur in liste:   parcourt la liste
#
#   Dictionnaires (tableaux associatifs) :
#       d = {}                       dictionnaire vide
#       d["A"] = 3                   la case "A" vaut 3
#       d.get("B", 0)                valeur de la case "B", ou 0 si absente
#       for cle in d:                parcourt les clefs
#
# ==========================================================================


# ==========================================================================
# PARTIE A — PRÉPARER LE TEXTE
# ==========================================================================

def nettoyer_simple(texte):
    """A.1 — Renvoie la version « propre » du texte : tout en MAJUSCULES, et
    seuls les caractères de "A" à "Z" sont conservés (les espaces, la
    ponctuation, les chiffres et les accents simples disparaissent).

    Arguments :
        texte (str) : le texte à nettoyer.

    Renvoie :
        str : le texte en majuscules, sans aucun autre caractère que A...Z.

    Exemples :
        nettoyer_simple("Bonjour, le monde !")      ->  "BONJOURLEMONDE"
        nettoyer_simple("Le chat mange, en 2026.")  ->  "LECHATMANGEEN"

    Indications :
        * commencez par `texte = texte.upper()`;
        * partez d'une chaîne vide `resultat = ""`;
        * parcourez le texte caractère par caractère avec une boucle `for`;
        * gardez le caractère seulement si le test `"A" <= caractere <= "Z"`
          est vrai, en faisant `resultat += caractere`.
    """
    # ------------------------------------------------------------------
    # TODO A.1 — écrivez ici les 5 lignes de la fonction.
    # ------------------------------------------------------------------
    raise NotImplementedError("A.1 nettoyer_simple n'est pas encore écrite")


def compter_lettres(texte):
    """A.2 — Compte combien de fois chaque lettre apparaît dans le texte.

    Arguments :
        texte (str) : un texte quelconque (pas forcément nettoyé).

    Renvoie :
        dict : un dictionnaire à 26 cases, {"A": 12, "B": 0, ..., "Z": 3}.
               Les lettres absentes du texte ont un compte nul (0), comme dans
               la fonction `comptage` de common.py dont vous pouvez vous
               inspirer — mais recopiez-la de mémoire, cela vous entraîne.

    Exemple :
        compter_lettres("BONJOUR")["O"]   ->  2
        compter_lettres("BONJOUR")["A"]   ->  0

    Indications :
        * créez d'abord le dictionnaire vide, puis remplissez-le à zéro pour
          les 26 lettres (sans cela, `comptes["A"] += 1` échouerait) ;
        * parcourez `texte.upper()` et testez si le caractère est bien une
          lettre avant d'incrémenter son compte.
    """
    # ------------------------------------------------------------------
    # TODO A.2
    # ------------------------------------------------------------------
    raise NotImplementedError("A.2 compter_lettres n'est pas encore écrite")


# ==========================================================================
# PARTIE B — LE CODE DE PERMUTATION (SCYTALE) ET SON ATTAQUE
# ==========================================================================
#
# Rappel du cours : dans un code de permutation, on ne remplace aucune lettre,
# on les déplace.  Les fréquences du texte chiffré sont donc EXACTEMENT celles
# du texte clair : c'est un point faible énorme.  Ici, on attaque la scytale en
# essayant toutes les clefs possibles : c'est une attaque par recherche
# exhaustive (« force brute »), celle qui, appliquée à Enigma, exigeait bien
# autre chose qu'un crayon.

def cle_scytale_possibles(longueur):
    """B.1 — Renvoie la liste des clefs t de scytale qu'il est raisonnable
    d'essayer pour un texte chiffré de longueur `longueur`.

    On convient qu'une clef t est « raisonnable » si :
        * t divise la longueur du texte chiffré (sinon le déchiffrement est
          impossible : la scytale n'accepte que des longueurs multiples de t) ;
        * t est au moins 2 (t = 1 ne mélange rien du tout) ;
        * le tableau obtenu a au moins 5 lignes (donc t <= longueur // 5).

    Arguments :
        longueur (int) : nombre de caractères du texte chiffré.

    Renvoie :
        list : la liste des clefs à essayer, dans l'ordre croissant.

    Exemple :
        cle_scytale_possibles(40)  ->  [2, 4, 5, 8]

    Indications :
        * créez une liste vide, puis parcourez les entiers t de 2 à longueur
          avec une boucle `for` ;
        * gardez t si `longueur % t == 0` et si `longueur // t >= 5` ;
        * il ne reste plus qu'à faire `liste.append(t)`.
    """
    # ------------------------------------------------------------------
    # TODO B.1
    # ------------------------------------------------------------------
    raise NotImplementedError("B.1 cle_scytale_possibles n'est pas encore écrite")


def decouper_en_morceaux(texte, taille):
    """B.2 — Découpe le texte en morceaux de `taille` caractères.

    Arguments :
        texte (str) : le texte à découper.
        taille (int) : le nombre de caractères par morceau.

    Renvoie :
        list : la liste des morceaux (chaînes de caractères).

    Exemples :
        decouper_en_morceaux("ABCDEFGH", 3)  ->  ["ABC", "DEF", "GH"]
        decouper_en_morceaux("ABCDEF", 3)    ->  ["ABC", "DEF"]

    Indications :
        * parcourez les positions de départ : `for debut in range(0, len(texte), taille)`
          (le troisième argument de range est le pas) ;
        * l'extrait qui commence à la position `debut` et qui fait `taille`
          caractères s'écrit `texte[debut:debut + taille]`.
    """
    # ------------------------------------------------------------------
    # TODO B.2
    # ------------------------------------------------------------------
    raise NotImplementedError("B.2 decouper_en_morceaux n'est pas encore écrite")


def attaque_scytale(chiffre):
    """B.3 — Retrouve le message clair et la clef d'un texte chiffré par la
    scytale, sans connaître la clef.

    Méthode : on essaie toutes les clefs raisonnables (fonction B.1), on
    déchiffre le message avec chacune, et on choisit le candidat qui
    « ressemble le plus à du français ».

    Comment mesurer cette ressemblance ?  Réfléchissez d'abord à une fausse
    piste : comparer les FRÉQUENCES DES LETTRES ne sert à rien ici, car la
    scytale ne change aucune lettre : tous les candidats ont exactement les
    mêmes comptes de lettres.  Ce qui distingue le bon candidat, c'est l'ORDRE
    des lettres.  On utilise donc la fonction `vraisemblance` (importée en haut
    de ce fichier) : elle regarde les paires de lettres consécutives et donne
    un score d'autant plus grand que le texte ressemble à du français.

        * pour chaque clef t de B.1 :
              candidat = scytale_dechiffrer(chiffre, t)
              score = vraisemblance(candidat)
        * gardez la plus GRANDE vraisemblance rencontrée (rappel : -5,3 est
          plus grand que -6,1) ;
        * à la fin, renvoyez la clef gagnante et son texte.

    (Autre idée possible, plus simple mais moins fiable : compter les
    occurrences des petits mots fréquents « DE », « LE », « ES », « EN » grâce
    à `candidat.count("DE")`.  Vous pouvez essayer, comparer les deux méthodes
    et garder la meilleure.)

    Arguments :
        chiffre (str) : le texte chiffré par la scytale.

    Renvoie :
        tuple : (cle, texte_clair) — la clef t trouvée et le message déchiffré
                (le X de complément éventuel peut rester, ce n'est pas grave).

    Exemple (à tester à la fin) :
        attaque_scytale(scytale_chiffrer("LEGRANDMESSAGERARRIVECETTEAPRESMIDI", 7))
        ->  (7, "LEGRANDMESSAGERARRIVECETTEAPRESMIDI")

    Indications :
        * inspirez-vous de la structure : `for t in cle_scytale_possibles(len(chiffre)):`
        * gardez en mémoire trois variables mises à jour au fil de la boucle :
          la meilleure clef, le meilleur texte et le meilleur score (0 au
          départ) ;
        * testez plusieurs petits mots plutôt qu'un seul : cela évite de se
          tromper quand le message n'utilise pas « DE ».
    """
    # ------------------------------------------------------------------
    # TODO B.3
    # ------------------------------------------------------------------
    raise NotImplementedError("B.3 attaque_scytale n'est pas encore écrite")


# ==========================================================================
# PARTIE C — LE CODE DE SUBSTITUTION : CÉSAR
# ==========================================================================
#
# Le code de César est une substitution : on remplace chaque lettre par celle
# qui se trouve `cle` rangs plus loin dans l'alphabet, en revenant au début
# après Z (arithmétique modulo 26, comme dans le cours : n -> n + k mod 26).

def cesar_chiffrer(texte, cle):
    """C.1 — Chiffre `texte` par le code de César de clef `cle`.

    Conventions choisies pour tout le TP :
        * le texte est d'abord mis en MAJUSCULES ;
        * seules les lettres de A à Z sont décalées ;
        * tous les autres caractères (espaces, virgules, points...) sont
          recopiés sans modification.

    Arguments :
        texte (str) : le message en clair.
        cle (int) : le décalage, entre 0 et 25.

    Renvoie :
        str : le message chiffré, de même longueur que le message clair.

    Exemples :
        cesar_chiffrer("AVE", 3)                ->  "DYH"
        cesar_chiffrer("BONJOUR, LE MONDE", 3)  ->  "ERQMRXU, OH PRQGH"
        cesar_chiffrer("XYZ", 3)                ->  "ABC"      (retour au début)

    Indications :
        * pour une lettre, sa position est `ALPHABET.index(lettre)` ;
        * la nouvelle position est `(position + cle) % 26` ;
        * la nouvelle lettre est `ALPHABET[nouvelle_position]`;
        * attention à copier les autres caractères sans les décaler.
    """
    # ------------------------------------------------------------------
    # TODO C.1
    # ------------------------------------------------------------------
    raise NotImplementedError("C.1 cesar_chiffrer n'est pas encore écrite")


def cesar_dechiffrer(texte_chiffre, cle):
    """C.2 — Déchiffre un texte chiffré par `cesar_chiffrer` avec la même clef.

    Arguments :
        texte_chiffre (str) : le message chiffré.
        cle (int) : la clef utilisée au chiffrement.

    Renvoie :
        str : le message clair (en majuscules).

    Exemple :
        cesar_dechiffrer("ERQMRXU, OH PRQGH", 3)  ->  "BONJOUR, LE MONDE"

    Indication : pour retrouver le décalage inverse, décalez de -cle, c'est-à-dire
    de `(-cle) % 26`.  Vous pouvez réutiliser votre fonction C.1 en trois lignes
    (c'est même recommandé : moins de code, moins de fautes).
    """
    # ------------------------------------------------------------------
    # TODO C.2
    # ------------------------------------------------------------------
    raise NotImplementedError("C.2 cesar_dechiffrer n'est pas encore écrite")


def forcer_cesar(texte_chiffre):
    """C.3 — Retrouve le message clair SANS CONNAÎTRE LA CLEF.

    C'est le cœur de la cryptanalyse : il y a seulement 26 clefs possibles, on
    les essaie donc toutes, et on garde la meilleure.  Mais « la meilleure »
    veut dire quoi ?  Il faut un critère automatique.  Ici, vous le ferez avec
    les fréquences des lettres :

        * dans un texte français, les lettres ne sont pas équiprobables : il y
          a beaucoup de E (environ 15 %), peu de K, W, Z (moins de 0,5 %) ;
        * on compare donc l'histogramme du candidat à celui du français.  La
          fonction `distance_au_francais` (importée en haut de ce fichier) fait
          ce calcul : elle renvoie un nombre, et PLUS CE NOMBRE EST PETIT, PLUS
          LE TEXTE RESSEMBLE À DU FRANÇAIS.  Le bon candidat est donc celui
          dont la distance est la plus PETITE ;
        * attention au piège : l'indice de coïncidence, lui, est identique pour
          les 26 candidats (décaler l'alphabet ne change pas la répartition des
          lettres entre elles) — il ne sert donc à rien ici.  On le réutilisera
          en revanche pour le code de Vigenère, en séance 3.

    Arguments :
        texte_chiffre (str) : le message chiffré, clef inconnue.

    Renvoie :
        tuple : (cle, texte_clair) — la clef trouvée et le message déchiffré.

    Exemple :
        forcer_cesar(cesar_chiffrer("LE MESSAGE ARRIVE CE SOIR", 17)) -> (17, ...)

    Indications :
        * pour chaque clef possible `cle` de 0 à 25 :
              candidat = cesar_dechiffrer(texte_chiffre, cle)
              distance = distance_au_francais(candidat)
          et mémorisez la plus petite distance rencontrée, ainsi que la clef et
          le texte qui vont avec ;
        * `for cle in range(26):` parcourt bien 0, 1, 2, ..., 25 ;
        * pour mémoriser « la plus petite vue jusqu'ici », utilisez une
          variable `meilleure_distance` initialisée à `None`, et le test :
              if meilleure_distance is None or distance < meilleure_distance:
        * le critère a besoin d'un peu de matière : à partir d'environ 50
          lettres, il est fiable.  Sur un texte de 5 lettres, personne ne peut
          deviner la clef, et ce n'est pas votre faute.  Le TP ne piègera pas
          ce cas.
    """
    # ------------------------------------------------------------------
    # TODO C.3
    # ------------------------------------------------------------------
    raise NotImplementedError("C.3 forcer_cesar n'est pas encore écrite")


# ==========================================================================
# PARTIE D — HISTOIRE, KERCKHOFFS ET MESSAGES TRUQUÉS
# ==========================================================================

def message_compromis(message_clair, texte_chiffre_saisi):
    """D.1 — Vérifie qu'un message chiffré correspond bien au message annoncé.

    Situation historique (cours) : Marie Stuart faisait passer des messages
    chiffrés.  Les services de la reine Élisabeth, qui connaissaient le système,
    y glissaient des phrases qu'elle ne pouvait que reprendre mot pour mot afin
    de la faire tomber dans un piège.  Pour cela, il faut pouvoir vérifier
    automatiquement qu'un message chiffré donné correspond bien à un message
    clair donné — c'est exactement le principe des codes d'authentification
    (MAC) que vous verrez en fin d'année.

    Arguments :
        message_clair (str) : le message que l'on croit avoir été envoyé.
        texte_chiffre_saisi (str) : le texte chiffré réellement intercepté,
            qui peut contenir des espaces, des majuscules et des minuscules,
            de la ponctuation... (une saisie « à la main », donc).

    Renvoie :
        bool : True si, une fois les deux textes nettoyés et mis en majuscules,
               tout le message clair se retrouve dans le texte chiffré ;
               False sinon.

    Exemples (le deuxième argument est le document intercepté, qui mêle du
    texte chiffré et, hélas pour son auteur, une phrase restée en clair !) :

        document = "XWWD TXH, O'DSSURFKH. ATTAQUE A L'AUBE, PREVENEZ LE BATELIER."
        message_compromis("ATTAQUE A L AUBE", document)  ->  True
        message_compromis("ATTAQUER A L AUBE", document) ->  True  (même nettoyé)
        message_compromis("FUITE", document)             ->  False

    Indications :
        * nettoyez les deux textes avec votre fonction A.1 ;
        * pour tester si une chaîne `a` est contenue dans une chaîne `b`,
          Python offre l'opérateur `in` : "DE" in "ABDE" vaut True ;
        * attention : le texte chiffré intercepté peut être plus long que le
          message que l'on veut vérifier ; c'est bien le message clair que l'on
          cherche DANS le document, et non l'inverse.
    """
    # ------------------------------------------------------------------
    # TODO D.1
    # ------------------------------------------------------------------
    raise NotImplementedError("D.1 message_compromis n'est pas encore écrite")


# ==========================================================================
# PARTIE E — DEUX MESSAGES À DÉCRYPTER POUR DE VRAI
# ==========================================================================
#
# Ces deux messages ont été chiffrés par votre professeur : l'un avec la
# scytale, l'autre avec César.  Les clefs sont inconnues !  Utilisez vos
# fonctions B.3 et C.3 pour les retrouver.

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


if __name__ == "__main__":
    # Petit test « à la main » : exécutez ce fichier avec
    #     python3 tp1_permutation.py
    # quand vos fonctions sont écrites, pour voir le résultat du travail.
    print("Scytale (fournie) :", scytale_dechiffrer(scytale_chiffrer("BONJOUR", 3), 3))
    print()
    print("À vous de jouer : écrivez vos fonctions, puis lancez")
    print("    python3 test_tp1_permutation.py")
    print()
    print("Nettoyage du texte de référence :")
    print(nettoyer("Bonjour, c'est un test !"))
    print("Comptage :", comptage("BONJOUR")["O"], "lettre O dans BONJOUR")
