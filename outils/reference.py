"""==========================================================================
 OUTILS DU PROFESSEUR — primitives des chapitres 1 et 2 (NE PAS MODIFIER)
==========================================================================

Ce fichier contient tout ce qui est DÉJÀ ÉCRIT et que vous utilisez sans le
réécrire : la scytale, le code de Vigenère, le tableau du VIC simplifié, des
outils pour nettoyer un texte, etc.

Pourquoi le lire ?  Parce que :

  1. c'est un exemple de code Python simple, écrit pour être lu par des
     débutants : presque chaque ligne est commentée ;
  2. vous y trouverez la réponse à la question « comment fait-on pour... ? »
     (décaler une lettre, répéter une clef, remplir un tableau, etc.) ;
  3. le principe de Kerckhoffs dit que tout, sauf la clef, est public : ce
     fichier est donc public lui aussi, et c'est normal.

COMMENT LIRE LES COMMENTAIRES
-----------------------------
Un commentaire commence par un dièse (#) : Python l'ignore, il n'est là que
pour vous.  Les lignes qui commencent par >>> sont des exemples que l'on peut
taper dans l'interpréteur Python pour voir le résultat.

RAPPEL DES CONVENTIONS DE TOUT LE TP
------------------------------------
  * les textes sont en MAJUSCULES, sans accent ;
  * une lettre est repérée par son RANG : A = 0, B = 1, ..., Z = 25 ;
  * « décaler de k » veut dire : remplacer le rang n par le rang (n + k) mod 26.
    Le « mod 26 » (reste de la division par 26) est ce qui fait revenir au début
    de l'alphabet après Z : le rang 26 redevient 0, c'est-à-dire A.
==========================================================================
"""

from __future__ import annotations  # ligne technique, sans effet sur le TP

# __all__ est la liste de ce que l'on peut importer depuis ce fichier.
# Ce n'est pas obligatoire : c'est une carte de visite du fichier.
__all__ = [
    "ajouter_cle",
    "ALPHABET",
    "ALPHABET_VIC",
    "afficher_comptage",
    "afficher_tableau_vic",
    "cesar_chiffrer",
    "cesar_dechiffrer",
    "chiffrer_avec_damier",
    "chiffres_en_message",
    "comptage",
    "dechiffrer_avec_damier",
    "deviner_ligne_vic",
    "lettre_vic",
    "message_en_chiffres",
    "nettoyer",
    "PERMUTATION_VIC",
    "permutation_inverse",
    "rehabiller",
    "retirer_cle",
    "scytale_chiffrer",
    "scytale_dechiffrer",
    "TABLEAU_VIC",
    "transposition",
    "vic_chiffrer",
    "vic_dechiffrer",
    "vigenere_chiffrer",
    "vigenere_dechiffrer",
]

# ---------------------------------------------------------------------------
# Constantes de base
# ---------------------------------------------------------------------------

# ALPHABET est une CHAÎNE de 26 caractères : le A est à la position 0, le Z à
# la position 25.  Deux opérations très utiles :
#       ALPHABET.index("C")  ->  2      (quel est le rang de la lettre C ?)
#       ALPHABET[2]          ->  "C"    (quelle est la lettre de rang 2 ?)
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# REMPLACEMENTS_ACCENTS est un DICTIONNAIRE : à chaque lettre accentuée (la
# clef, à gauche) correspond la lettre simple à mettre à la place (la valeur, à
# droite).  Un dictionnaire sert à ranger des renseignements par nom :
#       REMPLACEMENTS_ACCENTS["É"]  ->  "E"
REMPLACEMENTS_ACCENTS = {
    "É": "E", "È": "E", "Ê": "E", "Ë": "E",
    "À": "A", "Â": "A", "Ä": "A",
    "Î": "I", "Ï": "I",
    "Ô": "O", "Ö": "O",
    "Ù": "U", "Û": "U", "Ü": "U",
    "Ç": "C", "Œ": "OE", "Æ": "AE",
}


# ===========================================================================
# 1. Préparer le texte
# ===========================================================================

def nettoyer(texte):
    """Renvoie le texte en majuscules, sans accent, en ne gardant que A...Z.

    Exemple :
        >>> nettoyer("César est un célèbre général !")
        'CESARESTUNCELEBREGENERAL'

    Lecture du code, ligne par ligne :
        * `texte.upper()` met le texte en majuscules ;
        * `for caractere in ...` fait le tour des caractères, un par un ;
        * `resultat += caractere` ajoute le caractère à la fin d'une chaîne :
          au début `resultat` est vide (""), et il s'allonge au fil de la boucle.
    """
    resultat = ""                      # on part d'une chaîne vide
    for caractere in texte.upper():    # on regarde chaque caractère du texte

        # `caractere in REMPLACEMENTS_ACCENTS` est VRAI si le caractère est une
        # des clefs du dictionnaire, par exemple "É".
        if caractere in REMPLACEMENTS_ACCENTS:
            resultat += REMPLACEMENTS_ACCENTS[caractere]   # on écrit la lettre simple

        # `"A" <= caractere <= "Z"` est VRAI si le caractère est une lettre
        # majuscule non accentuée.  La comparaison de caractères suit l'ordre
        # alphabétique.
        elif "A" <= caractere <= "Z":
            resultat += caractere      # on le garde tel quel

        # Sinon (espace, virgule, chiffre, apostrophe...), on ne fait rien :
        # le caractère est tout simplement oublié.
    return resultat                    # on renvoie la chaîne construite


def rehabiller(texte_modele, lettres):
    """Recopie `texte_modele` en remplaçant ses lettres, dans l'ordre, par
    celles de `lettres` ; les autres caractères (espaces, ponctuation) sont
    conservés tels quels.

    Utile pour remettre un texte clair dans sa présentation d'origine après
    l'avoir déchiffré lettre à lettre :

        >>> rehabiller("BO N??JOUR !", "ABCDEFG")
        'AB C??DEFG !'

    Lecture du code :
        * `position` est le numéro de la prochaine lettre de `lettres` à poser ;
        * à chaque fois qu'on rencontre une lettre du modèle (test
          `"A" <= caractere.upper() <= "Z"`), on pose la lettre suivante de
          `lettres` et on avance d'un cran (`position += 1`) ;
        * les autres caractères sont recopiés sans rien changer.
    """
    resultat = ""            # le texte que l'on construit
    position = 0             # combien de lettres de `lettres` ont déjà été posées

    for caractere in texte_modele:                      # on parcourt le modèle
        if "A" <= caractere.upper() <= "Z":             # le caractère est une lettre ?
            if position >= len(lettres):                # plus rien à poser ?
                raise ValueError("il n'y a pas assez de lettres à replacer")
            resultat += lettres[position]               # on pose la lettre suivante
            position += 1                               # et on avance d'un cran
        else:
            resultat += caractere                       # ponctuation : recopiée

    # Contrôle : a-t-on bien utilisé TOUTES les lettres fournies ?
    if position != len(lettres):
        raise ValueError(
            f"{len(lettres) - position} lettre(s) de trop : le modèle "
            "n'a pas assez de lettres à remplacer"
        )
    return resultat


def comptage(texte):
    """Compte les occurrences des 26 lettres du texte.

    Renvoie un dictionnaire qui contient TOUJOURS les 26 clefs, même pour les
    lettres absentes (leur compte vaut alors 0) :

        >>> comptage("BONJOUR")["O"]
        2
        >>> comptage("BONJOUR")["Z"]
        0

    Lecture du code :
        * `{lettre: 0 for lettre in ALPHABET}` construit en une fois un
          dictionnaire {"A": 0, "B": 0, ..., "Z": 0}.  C'est une « compréhension
          de dictionnaire » ; on peut aussi l'écrire avec une boucle ;
        * `if caractere in comptes` teste si le caractère est une des clefs du
          dictionnaire, donc une lettre de A à Z ;
        * `comptes[caractere] += 1` augmente de 1 le compteur de cette lettre.
    """
    comptes = {lettre: 0 for lettre in ALPHABET}   # les 26 compteurs à zéro
    for caractere in texte.upper():                # chaque caractère du texte
        if caractere in comptes:                   # est-ce une lettre de A à Z ?
            comptes[caractere] += 1                # alors on compte une fois de plus
    return comptes                                 # le dictionnaire des comptes


def afficher_comptage(comptes, largeur=30):
    """Présente un dictionnaire de comptes sous forme d'histogramme, une ligne
    par lettre.  (Fonction d'affichage : elle ne sert pas à chiffrer.)

    Lecture du code :
        * `max(comptes.values())` est la plus grande valeur du dictionnaire ;
          le `or 1` évite la division par zéro quand tous les comptes sont nuls ;
        * `"#" * nombre` répète le caractère # autant de fois que `nombre` ;
        * `f"{lettre} {valeur:>4} |{barre}"` fabrique une ligne de texte où
          `{valeur:>4}` signifie « la valeur, alignée à droite sur 4 caractères ».
    """
    maximum = max(comptes.values()) or 1       # pour ne pas diviser par zéro
    lignes = []                                # on va ranger les lignes ici
    for lettre in ALPHABET:                    # pour chaque lettre, de A à Z
        valeur = comptes.get(lettre, 0)        # son compte (0 si absente)
        longueur = int(round(largeur * valeur / maximum))   # longueur de la barre
        barre = "#" * longueur                 # la barre elle-même
        lignes.append(f"{lettre} {valeur:>4} |{barre}")     # la ligne complète
    return "\n".join(lignes)                   # on colle les lignes avec un retour


# ===========================================================================
# 2. Codes de substitution : César
# ===========================================================================
#
# Principe : chaque lettre est remplacée par celle qui se trouve `cle` rangs
# plus loin dans l'alphabet.  Avec la clef 3 : A -> D, B -> E, ..., Z -> C.

def cesar_chiffrer(texte, cle):
    """Code de César : décale chaque lettre de `cle` rangs.

        >>> cesar_chiffrer("BONJOUR, LE MONDE", 3)
        'ERQMRXU, OH PRQGH'
        >>> cesar_chiffrer("XYZ", 3)
        'ABC'

    Lecture du code :
        * on parcourt le texte en majuscules ;
        * si le caractère est une lettre : on calcule son rang avec
          `ALPHABET.index(caractere)`, on ajoute `cle`, on prend le reste de la
          division par 26 (l'opérateur %), et on reprend la lettre à ce rang ;
        * sinon, on recopie le caractère sans le modifier (l'espace, la virgule,
          l'apostrophe restent en place).
    """
    resultat = ""                                        # la chaîne construite
    for caractere in texte.upper():                      # chaque caractère
        if "A" <= caractere <= "Z":                      # est-ce une lettre ?
            rang = (ALPHABET.index(caractere) + cle) % 26  # nouveau rang (modulo 26)
            resultat += ALPHABET[rang]                   # la lettre correspondante
        else:
            resultat += caractere                        # sinon : recopié tel quel
    return resultat


def cesar_dechiffrer(texte_chiffre, cle):
    """Opération inverse de `cesar_chiffrer` : on décale de -cle.

        >>> cesar_dechiffrer("ERQMRXU, OH PRQGH", 3)
        'BONJOUR, LE MONDE'

    Remarque importante : `(-cle) % 26` est le décalage inverse.  Par exemple
    pour cle = 3, cela vaut 23 : décaler de 23 revient à reculer de 3, car
    23 + 3 = 26 ≡ 0 (mod 26).  C'est pour cette raison que l'on réutilise la
    fonction précédente au lieu d'écrire une seconde boucle.
    """
    return cesar_chiffrer(texte_chiffre, (-cle) % 26)


# ===========================================================================
# 3. Codes de permutation : la scytale
# ===========================================================================
#
# Principe (cours, chapitre 2) : on écrit le texte en lignes de t lettres, puis
# on relit le tableau en colonnes.  Exemple avec t = 5 :
#
#       J E V O U          lecture en colonnes :
#       S A T T E          JSNH + EADE + VTST + OTAE + UECR
#       N D S A C
#       H E T E R
#
# Aucune lettre n'est remplacée : elles sont déplacées.  C'est pour cela que les
# fréquences du texte chiffré sont exactement celles du texte clair.

def scytale_chiffrer(texte, t):
    """Scytale de clef `t` : découpage en lignes de t lettres, puis lecture en
    colonnes.  La dernière ligne est complétée par des X si nécessaire.

        >>> scytale_chiffrer("JEVOUSATTENDSACHETER", 5)
        'JSNHEADEVTSTOTAEUECR'

    Lecture du code :
        * `complement = (t - len(texte) % t) % t` calcule combien de X il faut
          ajouter pour que la longueur devienne un multiple de t.  Si la
          longueur est déjà bonne, le calcul donne 0 ;
        * `tableau = texte + "X" * complement` ajoute ces X à la fin ;
        * `len(tableau) // t` est le NOMBRE DE LIGNES (division entière) ;
        * la double boucle parcourt les colonnes (de 0 à t-1) puis, dans chaque
          colonne, les lignes (de 0 à lignes-1) ; l'indice de la case est
          `ligne * t + colonne`, ce qui correspond à la position de la lettre
          dans un tableau lu ligne après ligne.
    """
    if t < 1:                                    # contrôle de la clef
        raise ValueError("la clef t doit être un entier supérieur ou égal à 1")

    texte = texte.upper()                        # on travaille en majuscules
    complement = (t - len(texte) % t) % t        # nombre de X à ajouter
    tableau = texte + "X" * complement           # le tableau complet

    chiffre = ""                                 # la chaîne construite
    for colonne in range(t):                     # pour chaque colonne (0 à t-1)
        for ligne in range(len(tableau) // t):   # pour chaque ligne
            chiffre += tableau[ligne * t + colonne]   # la case (ligne, colonne)
    return chiffre                               # la lecture en colonnes


def scytale_dechiffrer(chiffre, t):
    """Opération inverse de `scytale_chiffrer` : on remplit les colonnes, puis
    on relit les lignes.

        >>> scytale_dechiffrer("JSNHEADEVTSTOTAEUECX", 5)
        'JEVOUSATTENDSACHETEX'

    Le X de complément ajouté au chiffrement reste dans le texte déchiffré :
    c'est à l'utilisateur de le retirer s'il sait que le message est complet.

    Lecture du code :
        * `lignes = len(chiffre) // t` : combien de lignes avait le tableau ;
        * la double boucle fait l'opération inverse de la précédente : on
          parcourt les lignes, et dans chaque ligne les colonnes, en lisant la
          case `colonne * lignes + ligne` du texte chiffré ;
        * `%` (reste) et `//` (division entière) sont les deux opérations à bien
          distinguer : `9 % 2` vaut 1 et `9 // 2` vaut 4.
    """
    if t < 1:                                    # contrôle de la clef
        raise ValueError("la clef t doit être un entier supérieur ou égal à 1")
    if len(chiffre) % t != 0:                    # la longueur doit convenir
        raise ValueError(
            "la longueur du texte chiffré doit être un multiple de t "
            f"({len(chiffre)} n'est pas un multiple de {t})"
        )

    lignes = len(chiffre) // t                   # nombre de lignes du tableau
    clair = ""                                   # la chaîne construite
    for ligne in range(lignes):                  # pour chaque ligne
        for colonne in range(t):                 # pour chaque colonne
            clair += chiffre[colonne * lignes + ligne]   # la case correspondante
    return clair


# ===========================================================================
# 4. Codes polyalphabétiques : Vigenère
# ===========================================================================
#
# Principe : la lettre de clef qui sert à décaler change à chaque lettre du
# message.  La clef est répétée autant de fois que nécessaire.  Convention
# choisie ici (et dans tout le TP) : les espaces et la ponctuation sont recopiés
# tels quels et NE CONSOMMENT PAS de lettre de clef.

def vigenere_chiffrer(texte, cle):
    """Chiffre avec la clef `cle` (une suite de lettres, par exemple "CLE").

        >>> vigenere_chiffrer("BONJOUR", "CLE")
        'DZRLZYT'
        >>> vigenere_chiffrer("BONJOUR LE MONDE", "CLE")
        'DZRLZYT WI OZRFP'

    Lecture du code — c'est LE passage à comprendre :
        * `rang_clef` compte combien de LETTRES ont déjà été chiffrées.  Il ne
          change pas quand on rencontre un espace : c'est ce qui met les lettres
          de la clef « en face » des lettres du message ;
        * l'opérateur % sert à faire tourner la clef en boucle :
          `cle[rang_clef % len(cle)]` prend la lettre 0, 1, 2, ..., puis revient
          à la 0.  Exemple avec la clef "CLE" (3 lettres) : les rangs de clef
          suivis sont 0, 1, 2, 0, 1, 2, ...
        * `ALPHABET.index(...)` donne le décalage demandé par cette lettre
          (A = 0, B = 1, ..., Z = 25).
    """
    if not cle:                                  # clef vide : erreur
        raise ValueError("la clef ne peut pas être vide")

    cle = cle.upper()                            # on travaille en majuscules
    for lettre in cle:                           # on vérifie la clef
        if lettre not in ALPHABET:
            raise ValueError("la clef ne doit contenir que des lettres A...Z")

    resultat = ""                                # la chaîne construite
    rang_clef = 0                                # état : où en est-on dans la clef ?

    for caractere in texte.upper():              # chaque caractère du message
        if "A" <= caractere <= "Z":              # est-ce une lettre ?
            decalage = ALPHABET.index(cle[rang_clef % len(cle)])   # lettre de clef
            rang = (ALPHABET.index(caractere) + decalage) % 26     # nouvelle lettre
            resultat += ALPHABET[rang]           # on l'ajoute au résultat
            rang_clef += 1                       # une lettre de plus consommée
        else:
            resultat += caractere                # ponctuation : recopiée...
                                                 # ...et rang_clef NE CHANGE PAS
    return resultat


def vigenere_dechiffrer(texte_chiffre, cle):
    """Opération inverse de `vigenere_chiffrer` : le décalage est retiré.

        >>> vigenere_dechiffrer("DZRLZYT WI OZRFP", "CLE")
        'BONJOUR LE MONDE'

    Lecture du code : c'est exactement la même boucle que ci-dessus, à un signe
    près : on SOUSTRAIT le décalage au lieu de l'ajouter, et le modulo 26 est là
    encore pour rester entre 0 et 25 (sans lui, on obtiendrait des rangs
    négatifs, et `ALPHABET[-1]` ne donnerait pas la lettre attendue).
    """
    if not cle:
        raise ValueError("la clef ne peut pas être vide")

    cle = cle.upper()
    rang_clef = 0                                # même compteur que ci-dessus
    resultat = ""

    for caractere in texte_chiffre.upper():
        if "A" <= caractere <= "Z":
            decalage = ALPHABET.index(cle[rang_clef % len(cle)])
            rang = (ALPHABET.index(caractere) - decalage) % 26   # la soustraction !
            resultat += ALPHABET[rang]
            rang_clef += 1
        else:
            resultat += caractere
    return resultat


# ===========================================================================
# 5. Le VIC simplifié (fin du chapitre 2)
# ===========================================================================
#
# Le vrai code de VIC, utilisé par le service secret britannique à partir de
# 1914, comporte quatre étapes :
#
#   (1) on écrit la clef au-dessus du message (elle est écrite deux fois, ce qui
#       permet au destinataire de la retrouver sans avoir à la transmettre) ;
#   (2) on additionne la clef au message, chiffre à chiffre, sans retenue ;
#   (3) on brouille l'ordre des caractères par une transposition ;
#   (4) on transforme chaque caractère en lettre, grâce à un damier de 10 lignes
#       et 10 colonnes.
#
# CE QUE NOUS SIMPLIFIONS (et qu'il faut savoir pour en parler honnêtement) :
#
#   * le vrai VIC travaille sur les 10 lettres d'un alphabet mixte (c'est ce même
#     alphabet qui sert à convertir une lettre en chiffre) ; nous faisons comme
#     lui, avec ALPHABET_VIC ;
#   * dans le vrai VIC, le « chiffre indicateur » qui choisit la colonne du
#     damier est tiré au hasard et transmis avec le message ; chez nous, c'est
#     simplement la POSITION du caractère dans son bloc de 10 ;
#   * la clef est fournie directement au déchiffreur.
#
# Le reste du principe (addition modulo 10, transposition, damier, carré latin)
# est fidèle.  Les TDs de l'enseignement d'origine contiennent le vrai tableau
# du VIC : il suffit de le recopier à la place du nôtre.

# Les 10 lettres du damier, dans l'ordre.  Chaque lettre vaut aussi un chiffre :
# S = 0, E = 1, ..., L = 9.
ALPHABET_VIC = "SENATROIDL"

# Comment construire le DAMIER (un « carré latin ») :
#     TABLEAU_VIC[ligne][colonne] = ALPHABET_VIC[(ligne + 3 * colonne) % 10]
#
# La double boucle ci-dessous remplit les 10 lignes ; chaque ligne est une
# chaîne de 10 lettres.  Propriété ESSENTIELLE : sur chaque ligne et dans chaque
# colonne, les 10 lettres apparaissent une fois et une seule.  C'est ce qui
# permet, en lecture, de retrouver la colonne (donc le chiffre) sans ambiguïté.
# Le tableau est public (principe de Kerckhoffs) : tout le secret est dans la
# clef.
TABLEAU_VIC = [
    "".join(ALPHABET_VIC[(ligne + 3 * colonne) % 10] for colonne in range(10))
    for ligne in range(10)
]

# Permutation des 10 colonnes pour l'étape de transposition : on relit d'abord
# la colonne 3, puis la 0, puis la 7, etc.
PERMUTATION_VIC = [3, 0, 7, 1, 9, 2, 5, 8, 4, 6]


def afficher_tableau_vic():
    """Renvoie le damier présenté sous forme de grille lisible.

    Lecture du code :
        * `"".join(...)` colle bout à bout les morceaux d'une liste ;
        * `f"{colonne:>3}"` écrit un numéro aligné sur 3 caractères ;
        * les deux boucles imbriquées parcourent les 10 lignes et les
          10 colonnes, exactement comme un tableau de la classe.
    """
    lignes = ["       " + "".join(f"{colonne:>3}" for colonne in range(10))]   # entête
    for ligne in range(10):                          # pour chacune des 10 lignes
        contenu = "".join(f"{TABLEAU_VIC[ligne][colonne]:>3}" for colonne in range(10))
        lignes.append(f"  {ligne} |  " + contenu)    # la ligne, avec son numéro
    return "\n".join(lignes)                         # une ligne par ligne


def message_en_chiffres(message):
    """Convertit un message en chiffres, avec le damier.

        >>> message_en_chiffres("LION")
        '9762'

    Lecture du code : `ALPHABET_VIC.index(caractere)` donne le chiffre de la
    lettre (par exemple 7 pour I).  `str(...)` transforme un nombre en texte pour
    pouvoir l'ajouter à une chaîne ; sans cela, Python refuserait d'écrire
    "chiffres += 7".
    """
    chiffres = ""
    for caractere in message.upper():
        if caractere in ALPHABET_VIC:
            chiffres += str(ALPHABET_VIC.index(caractere))    # lettre -> chiffre
        else:
            raise ValueError(
                f"le caractère {caractere!r} n'appartient pas au damier "
                f"{ALPHABET_VIC!r}"
            )
    return chiffres


def chiffres_en_message(chiffres):
    """Opération inverse de `message_en_chiffres`.

        >>> chiffres_en_message("9762")
        'LION'

    Lecture du code : pour chaque caractère (qui est ici un chiffre, par exemple
    "7"), on prend la lettre de même rang dans ALPHABET_VIC.
    `int(chiffre)` transforme le texte "7" en nombre 7, ce qui est nécessaire
    pour s'en servir comme indice.
    """
    message = ""
    for chiffre in chiffres:
        if chiffre not in "0123456789":
            raise ValueError(f"{chiffre!r} n'est pas un chiffre")
        message += ALPHABET_VIC[int(chiffre)]      # chiffre -> lettre
    return message


def ajouter_cle(chiffres, cle):
    """Additionne chiffre à chiffre le message et la clef, modulo 10 (sans
    retenue : c'est l'arithmétique du VIC).

        >>> ajouter_cle("01895", "12")
        '13916'

    Lecture du code :
        * `enumerate(chiffres)` fournit à la fois la POSITION et le CARACTÈRE ;
        * la clef se répète : `cle[position % len(cle)]`, comme pour Vigenère ;
        * `(a + b) % 10` : si la somme dépasse 9, on recommence à 0 (9 + 1 = 0).
    """
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    for chiffre in cle:
        if chiffre not in "0123456789":
            raise ValueError("la clef ne doit contenir que des chiffres")

    resultat = ""
    for position, chiffre in enumerate(chiffres):
        somme = (int(chiffre) + int(cle[position % len(cle)])) % 10
        resultat += str(somme)                     # nombre -> texte
    return resultat


def retirer_cle(chiffres, cle):
    """Opération inverse de `ajouter_cle` (soustraction modulo 10).

        >>> retirer_cle("13916", "12")
        '01895'
    """
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    resultat = ""
    for position, chiffre in enumerate(chiffres):
        difference = (int(chiffre) - int(cle[position % len(cle)])) % 10
        resultat += str(difference)
    return resultat


def permutation_inverse(permutation):
    """Renvoie la permutation réciproque, c'est-à-dire celle qui défait l'autre.

        >>> permutation_inverse([1, 0, 2])
        [1, 0, 2]
        >>> permutation_inverse([2, 0, 1])
        [1, 2, 0]

    Lecture du code : `inverse` est une liste de 10 zéros au départ ;
    `enumerate` donne le rang et la valeur ; on range chaque rang à la place
    indiquée par sa valeur, ce qui échange les rôles.
    """
    inverse = [0] * len(permutation)               # autant de cases que nécessaire
    for rang, valeur in enumerate(permutation):
        inverse[valeur] = rang                     # value <-> rang
    return inverse


def transposition(texte, permutation=PERMUTATION_VIC):
    """Transposition : le texte est écrit en lignes de 10 caractères, puis les
    colonnes sont relues dans l'ordre donné par `permutation`.

        >>> transposition("0123456789ABCDEFGHIJ", [1, 0, 2, 3, 4, 5, 6, 7, 8, 9])
        '1023456789BACDEFGHIJ'

    Lecture du code :
        * `sorted(permutation) != list(range(10))` vérifie que `permutation`
          contient bien les nombres 0, 1, ..., 9, chacun une fois : sinon ce
          n'est pas une permutation, et la transposition serait irréversible ;
        * `range(0, len(texte), 10)` parcourt les positions de début des blocs ;
        * `ligne = texte[debut:debut + 10]` extrait l'extrait « de debut à
          debut+10 exclu » (le découpage se fait avec les crochets) ;
        * `for colonne in permutation` relit les colonnes dans l'ordre demandé.
    """
    if sorted(permutation) != list(range(10)):
        raise ValueError("permutation doit être une permutation de 0 à 9")
    if len(texte) % 10 != 0:
        raise ValueError("la longueur du texte doit être un multiple de 10")

    resultat = ""
    for debut in range(0, len(texte), 10):         # un bloc de 10 à la fois
        ligne = texte[debut:debut + 10]            # le bloc
        for colonne in permutation:                # les colonnes dans l'ordre voulu
            resultat += ligne[colonne]             # on en prend le caractère
    return resultat


def lettre_vic(chiffre_ligne, chiffre_colonne):
    """Renvoie la lettre du damier à l'intersection de la ligne et de la colonne.

        >>> lettre_vic(0, 0)
        'S'

    Lecture du code : `% 10` garantit que l'indice reste entre 0 et 9 ; puis on
    lit la case [ligne][colonne] du tableau.
    """
    return TABLEAU_VIC[chiffre_ligne % 10][chiffre_colonne % 10]


def deviner_ligne_vic(lettre, chiffre_colonne):
    """Retrouve le numéro de la ligne à partir de la lettre et de la colonne.

        >>> deviner_ligne_vic("S", 0)
        0

    Lecture du code : on essaie les 10 lignes l'une après l'autre et l'on
    s'arrête sur celle dont la case contient la lettre cherchée.  Comme aucune
    lettre n'est répétée dans une colonne (carré latin), il y a exactement une
    solution — c'est toute la force de ce tableau.
    """
    colonne = chiffre_colonne % 10
    for ligne in range(10):                        # on essaie les 10 lignes
        if TABLEAU_VIC[ligne][colonne] == lettre.upper():
            return ligne                           # trouvée : on renvoie le numéro
    raise ValueError(f"la lettre {lettre!r} n'apparaît pas dans la colonne {colonne}")


def chiffrer_avec_damier(chiffres, cle):
    """Dernière étape du VIC simplifié : chaque chiffre devient une lettre.

    Pour chaque position `p` (0 à 9 dans son bloc : c'est le « chiffre
    indicateur », donc la colonne du damier) et chaque chiffre `m` du message :

        lettre = TABLEAU_VIC[(m + chiffre_de_clef) mod 10][p]

    Lecture du code : `enumerate` donne la position, `int(...)` convertit les
    caractères en nombres, et `lettre_vic` lit le damier.
    """
    resultat = ""
    for position, chiffre in enumerate(chiffres):
        chiffre_clef = int(cle[position % len(cle)])          # clef répétée
        ligne = (int(chiffre) + chiffre_clef) % 10            # ligne du damier
        resultat += lettre_vic(ligne, position % 10)          # colonne = position
    return resultat


def dechiffrer_avec_damier(message, cle):
    """Opération inverse de `chiffrer_avec_damier` : de la lettre au chiffre."""
    chiffres = ""
    for position, caractere in enumerate(message.upper()):
        chiffre_clef = int(cle[position % len(cle)])
        ligne = deviner_ligne_vic(caractere, position % 10)   # on remonte à la ligne
        chiffres += str((ligne - chiffre_clef) % 10)          # ligne - clef, modulo 10
    return chiffres


def vic_chiffrer(message, cle, permutation=PERMUTATION_VIC):
    """Le VIC simplifié complet, dans l'ordre du cours :

        1. convertir le message en chiffres (damier lettres -> chiffres) ;
        2. additionner la clef, chiffre à chiffre, modulo 10 ;
        3. transposer les colonnes, bloc de 10 par bloc de 10 ;
        4. transformer chaque chiffre en lettre avec le damier.

    Le message doit être écrit avec les 10 lettres du damier et sa longueur doit
    être un multiple de 10 : ce sont les contraintes du VIC.
    """
    chiffres = message_en_chiffres(message)                  # étape 1
    if len(chiffres) % 10 != 0:
        raise ValueError("la longueur du message doit être un multiple de 10")
    chiffres = ajouter_cle(chiffres, cle)                    # étape 2
    chiffres = transposition(chiffres, permutation)          # étape 3
    return chiffrer_avec_damier(chiffres, cle)               # étape 4


def vic_dechiffrer(message, cle, permutation=PERMUTATION_VIC):
    """Opération inverse de `vic_chiffrer` : les quatre étapes à l'envers, dans
    l'ordre (4), (3), (2), (1).

    Lecture du code : `permutation_inverse(list(permutation))` construit la
    permutation qui défait la transposition ; `list(...)` n'est là que pour
    travailler sur une copie.
    """
    chiffres = dechiffrer_avec_damier(message, cle)                          # (4)
    chiffres = transposition(chiffres, permutation_inverse(list(permutation)))  # (3)
    chiffres = retirer_cle(chiffres, cle)                                    # (2)
    return chiffres_en_message(chiffres)                                     # (1)


# ---------------------------------------------------------------------------
# VÉRIFICATION AUTOMATIQUE
# ---------------------------------------------------------------------------
# Cette partie s'exécute seulement quand on lance ce fichier directement :
#     python3 outils/reference.py
# Elle vérifie la propriété fondamentale d'un code, celle du cours :
#     d_k(e_k(x)) = x  pour tout message x.
# Si vous modifiez une fonction de ce fichier, pensez à relancer cette
# vérification : elle doit toujours afficher « OK ».
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # César : on chiffre puis on déchiffre avec les 26 clefs possibles.
    messages_cesar = ["BONJOUR", "LE MESSAGE ARRIVE CE SOIR"]
    for cle in range(26):                          # cle = 0, 1, 2, ..., 25
        for message in messages_cesar:
            assert cesar_dechiffrer(cesar_chiffrer(message, cle), cle) == message
    print("César : d_k(e_k(x)) = x pour les 26 clefs. OK")

    # Scytale : idem, pour toutes les clefs de 2 à 10.
    base = "JEVOUSATTENDSACHETERDEMAINMATINAVANTMIDI"
    for t in range(2, 11):
        # Attention : d_t(e_t(x)) = x seulement si la longueur est un multiple
        # de t ; sinon le X de complément reste dans le texte déchiffré.
        clair = base[: len(base) - len(base) % t]
        assert scytale_dechiffrer(scytale_chiffrer(clair, t), t) == clair
    clair = base[: len(base) - len(base) % 5 + 3]
    attendu = clair + "X" * (-len(clair) % 5)
    assert scytale_dechiffrer(scytale_chiffrer(clair, 5), 5) == attendu
    print("Scytale : d_t(e_t(x)) = x (+ X de complément) pour t de 2 à 10. OK")

    # Vigenère.
    for cle in ["CLE", "SECRET", "MATHEMATIQUES"]:
        clair = "LE MESSAGE ARRIVE CE SOIR, A DIX HEURES"
        assert vigenere_dechiffrer(vigenere_chiffrer(clair, cle), cle) == clair
    print("Vigenère : d_k(e_k(x)) = x. OK")

    # Damier du VIC : on vérifie la propriété de carré latin.
    for ligne in range(10):
        assert sorted(TABLEAU_VIC[ligne]) == sorted(ALPHABET_VIC)
    for colonne in range(10):
        assert sorted(TABLEAU_VIC[ligne][colonne] for ligne in range(10)) == sorted(ALPHABET_VIC)
    print("Damier VIC : carré latin (10 lettres par ligne et par colonne). OK")

    # VIC simplifié : aller-retour complet.
    message_vic = "LIONSENATO"                     # 10 lettres du damier
    for cle in ["12345", "5241730219", "7"]:
        chiffre = vic_chiffrer(message_vic, cle)
        assert vic_dechiffrer(chiffre, cle) == message_vic, (cle, chiffre)
    for permutation in ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]):
        chiffre = vic_chiffrer(message_vic, "12345", permutation)
        assert vic_dechiffrer(chiffre, "12345", permutation) == message_vic
    print("VIC simplifié : d_k(e_k(x)) = x. OK")
