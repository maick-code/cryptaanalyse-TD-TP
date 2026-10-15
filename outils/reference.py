"""Implémentations de référence des primitives du cours (chapitres 1 et 2).

Ce fichier contient TOUT ce qui est « déjà écrit » et que les étudiants
utilisent sans le réécrire : la scytale, le code de Vigenère complet, le tableau
du VIC simplifié, la conversion lettres ↔ chiffres, etc.

Il sert à trois choses :
  1. aux étudiants, qui importent ces outils dans leurs TP ;
  2. aux corrigés (`corriges/`), qui ne recopient pas ces primitives ;
  3. à `preparer_donnees.py`, qui fabrique les messages chiffrés des TP.

Le code que les ÉTUDIANTS doivent écrire se trouve dans les fichiers
`seanceX_.../tpX_....py`.  Rien ici n'est à rendre.

Conventions générales de tout le TP :
  * les textes sont en MAJUSCULES, sans accents ;
  * une lettre est repérée par son rang : A = 0, B = 1, ..., Z = 25 ;
  * « décaler de k » signifie remplacer le rang n par le rang (n + k) mod 26.
"""

from __future__ import annotations

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
    "rehabiller",
    "PERMUTATION_VIC",
    "permutation_inverse",
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

#: Les 26 lettres dans l'ordre : ALPHABET[0] == "A", ALPHABET[25] == "Z".
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#: Accents les plus courants, remplacés par des lettres simples.
REMPLACEMENTS_ACCENTS = {
    "É": "E", "È": "E", "Ê": "E", "Ë": "E",
    "À": "A", "Â": "A", "Ä": "A",
    "Î": "I", "Ï": "I",
    "Ô": "O", "Ö": "O",
    "Ù": "U", "Û": "U", "Ü": "U",
    "Ç": "C", "Œ": "OE", "Æ": "AE",
}


# ===========================================================================
# 1. Préparer et observer le texte
# ===========================================================================

def nettoyer(texte: str) -> str:
    """Renvoie le texte en majuscules, sans accent, en ne gardant que A...Z.

        >>> nettoyer("César est un célèbre général !")
        'CESARESTUNCELEBREGENERAL'
    """
    resultat = ""
    for caractere in texte.upper():
        if caractere in REMPLACEMENTS_ACCENTS:
            resultat += REMPLACEMENTS_ACCENTS[caractere]
        elif "A" <= caractere <= "Z":
            resultat += caractere
    return resultat


def rehabiller(texte_modele: str, lettres: str) -> str:
    """Recopie `texte_modele` en remplaçant ses lettres, dans l'ordre, par celles
    de `lettres` ; les caractères qui ne sont pas des lettres sont conservés.

    Utile pour remettre un texte clair dans sa présentation d'origine (avec ses
    espaces et sa ponctuation) après l'avoir déchiffré lettre à lettre :

        >>> rehabiller("BO N??JOUR !", "ABCDEFG")
        'AB C??DEFG !'

    Les lettres de trop dans `lettres` sont ignorées.
    """
    resultat = ""
    position = 0
    for caractere in texte_modele:
        if "A" <= caractere.upper() <= "Z":
            if position >= len(lettres):
                raise ValueError("il n'y a pas assez de lettres à replacer")
            resultat += lettres[position]
            position += 1
        else:
            resultat += caractere
    if position != len(lettres):
        raise ValueError(
            f"{len(lettres) - position} lettre(s) de trop : le modèle "
            "n'a pas assez de lettres à remplacer"
        )
    return resultat


def comptage(texte: str) -> dict:
    """Compte les occurrences des 26 lettres.

    Renvoie un dictionnaire qui contient TOUJOURS les 26 clefs (les lettres
    absentes ont un compte de 0).

        >>> comptage("BONJOUR")["O"]
        2
        >>> comptage("BONJOUR")["Z"]
        0
    """
    comptes = {lettre: 0 for lettre in ALPHABET}
    for caractere in texte.upper():
        if caractere in comptes:
            comptes[caractere] += 1
    return comptes


def afficher_comptage(comptes: dict, largeur: int = 30) -> str:
    """Présente un dictionnaire de comptes sous forme d'histogramme lisible."""
    maximum = max(comptes.values()) or 1
    lignes = []
    for lettre in ALPHABET:
        valeur = comptes.get(lettre, 0)
        barre = "#" * int(round(largeur * valeur / maximum))
        lignes.append(f"{lettre} {valeur:>4} |{barre}")
    return "\n".join(lignes)


# ===========================================================================
# 2. Codes de substitution : César
# ===========================================================================

def cesar_chiffrer(texte: str, cle: int) -> str:
    """Code de César : décale chaque lettre de `cle` rangs.

    Les caractères qui ne sont pas des lettres (espaces, ponctuation) sont
    recopiés tels quels ; le texte est d'abord mis en majuscules.

        >>> cesar_chiffrer("BONJOUR, LE MONDE", 3)
        'ERQMRXU, OH PRQGH'
        >>> cesar_chiffrer("XYZ", 3)
        'ABC'
    """
    resultat = ""
    for caractere in texte.upper():
        if "A" <= caractere <= "Z":
            rang = (ALPHABET.index(caractere) + cle) % 26
            resultat += ALPHABET[rang]
        else:
            resultat += caractere
    return resultat


def cesar_dechiffrer(texte_chiffre: str, cle: int) -> str:
    """Opération inverse de `cesar_chiffrer` (décalage de -cle).

        >>> cesar_dechiffrer("ERQMRXU, OH PRQGH", 3)
        'BONJOUR, LE MONDE'
    """
    return cesar_chiffrer(texte_chiffre, (-cle) % 26)


# ===========================================================================
# 3. Codes de permutation : la scytale
# ===========================================================================

def scytale_chiffrer(texte: str, t: int) -> str:
    """Scytale de clef `t` : on écrit le texte en lignes de t lettres (la
    dernière ligne est complétée par des X), puis on lit les colonnes.

        >>> scytale_chiffrer("JEVOUSATTENDSACHETER", 5)
        'JSNHEADEVTSTOTAEUECR'

    Le texte chiffré a toujours une longueur multiple de `t`.
    """
    if t < 1:
        raise ValueError("la clef t doit être un entier supérieur ou égal à 1")
    texte = texte.upper()
    complement = (t - len(texte) % t) % t
    tableau = texte + "X" * complement

    chiffre = ""
    for colonne in range(t):
        for ligne in range(len(tableau) // t):
            chiffre += tableau[ligne * t + colonne]
    return chiffre


def scytale_dechiffrer(chiffre: str, t: int) -> str:
    """Opération inverse de `scytale_chiffrer`.

        >>> scytale_dechiffrer("JSNHEADEVTSTOTAEUECX", 5)
        'JEVOUSATTENDSACHETEX'

    Le X de complément éventuel reste dans le texte déchiffré.
    """
    if t < 1:
        raise ValueError("la clef t doit être un entier supérieur ou égal à 1")
    if len(chiffre) % t != 0:
        raise ValueError(
            "la longueur du texte chiffré doit être un multiple de t "
            f"({len(chiffre)} n'est pas un multiple de {t})"
        )
    lignes = len(chiffre) // t
    clair = ""
    for ligne in range(lignes):
        for colonne in range(t):
            clair += chiffre[colonne * lignes + ligne]
    return clair


# ===========================================================================
# 4. Codes polyalphabétiques : Vigenère
# ===========================================================================

def vigenere_chiffrer(texte: str, cle: str) -> str:
    """Code de Vigenère : chaque lettre est décalée du rang de la lettre de
    clef correspondante (A = 0, B = 1, ...).

    La clef se répète si elle est plus courte que le texte.  Les caractères qui
    ne sont pas des lettres sont recopiés tels quels ET NE CONSOMMENT PAS de
    lettre de clef (c'est la convention classique, et celle utilisée dans tous
    les exercices) :

        >>> vigenere_chiffrer("BONJOUR", "CLE")
        'DZRLZYT'
        >>> vigenere_chiffrer("BONJOUR LE MONDE", "CLE")
        'DZRLZYT WI OZRFP'
    """
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    cle = cle.upper()
    for lettre in cle:
        if lettre not in ALPHABET:
            raise ValueError("la clef ne doit contenir que des lettres A...Z")

    resultat = ""
    rang_clef = 0
    for caractere in texte.upper():
        if "A" <= caractere <= "Z":
            decalage = ALPHABET.index(cle[rang_clef % len(cle)])
            rang = (ALPHABET.index(caractere) + decalage) % 26
            resultat += ALPHABET[rang]
            rang_clef += 1
        else:
            resultat += caractere
    return resultat


def vigenere_dechiffrer(texte_chiffre: str, cle: str) -> str:
    """Opération inverse de `vigenere_chiffrer`.

        >>> vigenere_dechiffrer("DZRLZYT WI OZRFP", "CLE")
        'BONJOUR LE MONDE'
    """
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    cle = cle.upper()
    rang_clef = 0
    resultat = ""
    for caractere in texte_chiffre.upper():
        if "A" <= caractere <= "Z":
            decalage = ALPHABET.index(cle[rang_clef % len(cle)])
            rang = (ALPHABET.index(caractere) - decalage) % 26
            resultat += ALPHABET[rang]
            rang_clef += 1
        else:
            resultat += caractere
    return resultat


# ===========================================================================
# 5. Le VIC simplifié (chapitre 2, fin)
# ===========================================================================
#
# Le vrai code de VIC, utilisé par le service secret britannique à partir de
# 1914, comporte quatre étapes :

#   (1) on écrit la clef au-dessus du message ; le reste de la clef (car elle
#       est écrite deux fois) sert de « clef de transposition » ;
#   (2) on additionne la clef au message, chiffre à chiffre, sans retenue
#       (c'est-à-dire modulo 10) ;
#   (3) on brouille l'ordre des caractères par une transposition ;
#   (4) on transforme chaque caractère en une lettre, à l'aide d'un damier de
#       10 lignes et 10 colonnes (le « tableau indicateur »).
#
# Ce que nous simplifions ici, et qu'il faut savoir pour pouvoir en parler
# honnêtement :
#
#   * le vrai VIC ne travaille pas sur les 26 lettres mais sur un alphabet
#     mixte de 10 lettres : c'est ce même alphabet qui sert à convertir chaque
#     lettre en chiffre.  Nous faisons la même chose avec `ALPHABET_VIC` ;
#   * dans le vrai VIC, le « chiffre indicateur » qui choisit la colonne du
#     damier est tiré au hasard et transmis avec le message.  Ici nous le
#     remplaçons par un choix déterministe : la position du caractère dans son
#     bloc de 10.  Tout devient ainsi calculable et vérifiable ;
#   * la clef est fournie directement au déchiffreur (dans le vrai VIC, elle
#     est écrite dans le message, ce qui est sa grande faiblesse et sa grande
#     force à la fois).
#
# Voir les TDs de l'enseignement de P. Boyer pour le vrai tableau du VIC : il
# suffit de le recopier ici à la place du nôtre, le reste du code ne change pas.

#: Alphabet mixte du damier : les 10 lettres du VIC simplifié.
#: Chaque lettre est aussi un chiffre : S = 0, E = 1, N = 2, A = 3, T = 4,
#: R = 5, O = 6, I = 7, D = 8, L = 9.
ALPHABET_VIC = "SENATROIDL"

#: Le damier : TABLEAU_VIC[ligne][colonne] est une lettre de ALPHABET_VIC.
#:
#: C'est un carré latin, construit par la formule
#: TABLEAU_VIC[ligne][colonne] = ALPHABET_VIC[(ligne + 3 * colonne) % 10].
#: Conséquence, sur chaque ligne et dans chaque colonne, les 10 lettres
#: apparaissent une fois et une seule.  Cette double propriété est essentielle :
#: connaissant la ligne, on retrouve la colonne sans ambiguïté, et réciproquement.
#: Le tableau est public (principe de Kerckhoffs) : toute la sécurité est dans
#: la clef.  Pour l'afficher :
#:
#:     >>> print(afficher_tableau_vic())
TABLEAU_VIC = [
    "".join(ALPHABET_VIC[(ligne + 3 * colonne) % 10] for colonne in range(10))
    for ligne in range(10)
]

#: Permutation des 10 colonnes utilisée pour l'étape de transposition :
#: on relit la colonne 3, puis la 0, puis la 7, etc.
PERMUTATION_VIC = [3, 0, 7, 1, 9, 2, 5, 8, 4, 6]


def afficher_tableau_vic() -> str:
    """Renvoie le damier présenté sous forme de grille lisible.

        >>> print(afficher_tableau_vic())  # doctest: +SKIP
    """
    lignes = ["       " + "".join(f"{colonne:>3}" for colonne in range(10))]
    for ligne in range(10):
        contenu = "".join(f"{TABLEAU_VIC[ligne][colonne]:>3}" for colonne in range(10))
        lignes.append(f"  {ligne} |  " + contenu)
    return "\n".join(lignes)


def message_en_chiffres(message: str) -> str:
    """Convertit un message écrit avec les lettres de `ALPHABET_VIC` en chiffres.

        >>> message_en_chiffres("LION")
        '9762'
    """
    chiffres = ""
    for caractere in message.upper():
        if caractere in ALPHABET_VIC:
            chiffres += str(ALPHABET_VIC.index(caractere))
        else:
            raise ValueError(
                f"le caractère {caractere!r} n'appartient pas au damier "
                f"{ALPHABET_VIC!r}"
            )
    return chiffres


def chiffres_en_message(chiffres: str) -> str:
    """Convertit une suite de chiffres en lettres du damier.

        >>> chiffres_en_message("9762")
        'LION'
    """
    message = ""
    for chiffre in chiffres:
        if chiffre not in "0123456789":
            raise ValueError(f"{chiffre!r} n'est pas un chiffre")
        message += ALPHABET_VIC[int(chiffre)]
    return message


def ajouter_cle(chiffres: str, cle: str) -> str:
    """Additionne chiffre à chiffre le message et la clef, modulo 10 (sans retenue).

    La clef se répète si elle est plus courte que le message.

        >>> ajouter_cle("01895", "12")
        '13916'
    """
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    for chiffre in cle:
        if chiffre not in "0123456789":
            raise ValueError("la clef ne doit contenir que des chiffres")
    resultat = ""
    for position, chiffre in enumerate(chiffres):
        resultat += str((int(chiffre) + int(cle[position % len(cle)])) % 10)
    return resultat


def retirer_cle(chiffres: str, cle: str) -> str:
    """Opération inverse de `ajouter_cle` (soustraction modulo 10).

        >>> retirer_cle("13916", "12")
        '01895'
    """
    if not cle:
        raise ValueError("la clef ne peut pas être vide")
    resultat = ""
    for position, chiffre in enumerate(chiffres):
        resultat += str((int(chiffre) - int(cle[position % len(cle)])) % 10)
    return resultat


def permutation_inverse(permutation) -> list:
    """Renvoie la permutation réciproque.

        >>> permutation_inverse([1, 0, 2])
        [1, 0, 2]
        >>> permutation_inverse([2, 0, 1])
        [1, 2, 0]
    """
    inverse = [0] * len(permutation)
    for rang, valeur in enumerate(permutation):
        inverse[valeur] = rang
    return inverse


def transposition(texte: str, permutation=PERMUTATION_VIC) -> str:
    """Transposition par colonnes : le texte est écrit en lignes de 10, puis les
    colonnes sont relues dans l'ordre donné par `permutation`.

        >>> transposition("0123456789ABCDEFGHIJ", [1, 0, 2, 3, 4, 5, 6, 7, 8, 9])
        '1023456789BACDEFGHIJ'

    `permutation` doit être une permutation de 0..9 : c'est la clef.
    """
    if sorted(permutation) != list(range(10)):
        raise ValueError("permutation doit être une permutation de 0 à 9")
    if len(texte) % 10 != 0:
        raise ValueError("la longueur du texte doit être un multiple de 10")
    resultat = ""
    for debut in range(0, len(texte), 10):
        ligne = texte[debut:debut + 10]
        for colonne in permutation:
            resultat += ligne[colonne]
    return resultat


def lettre_vic(chiffre_ligne: int, chiffre_colonne: int) -> str:
    """Renvoie la lettre du damier à l'intersection de la ligne et de la colonne.

        >>> lettre_vic(0, 0)
        'S'
    """
    return TABLEAU_VIC[chiffre_ligne % 10][chiffre_colonne % 10]


def deviner_ligne_vic(lettre: str, chiffre_colonne: int) -> int:
    """Retrouve le numéro de la ligne à partir de la lettre et de la colonne.

    Comme aucune lettre n'est répétée dans une colonne du damier, il y a
    exactement une solution.

        >>> deviner_ligne_vic("S", 0)
        0
    """
    colonne = chiffre_colonne % 10
    for ligne in range(10):
        if TABLEAU_VIC[ligne][colonne] == lettre.upper():
            return ligne
    raise ValueError(f"la lettre {lettre!r} n'apparaît pas dans la colonne {colonne}")


def chiffrer_avec_damier(chiffres: str, cle: str) -> str:
    """Étape finale du VIC simplifié.

    Pour chaque position p (0 à 9 dans son bloc : c'est le chiffre indicateur,
    donc la colonne du damier) et chaque chiffre m du message :

        lettre = TABLEAU_VIC[(m + chiffre_de_clef) mod 10][p]
    """
    resultat = ""
    for position, chiffre in enumerate(chiffres):
        chiffre_clef = int(cle[position % len(cle)])
        ligne = (int(chiffre) + chiffre_clef) % 10
        resultat += lettre_vic(ligne, position % 10)
    return resultat


def dechiffrer_avec_damier(message: str, cle: str) -> str:
    """Opération inverse de `chiffrer_avec_damier`."""
    chiffres = ""
    for position, caractere in enumerate(message.upper()):
        chiffre_clef = int(cle[position % len(cle)])
        ligne = deviner_ligne_vic(caractere, position % 10)
        chiffres += str((ligne - chiffre_clef) % 10)
    return chiffres


def vic_chiffrer(message: str, cle: str, permutation=PERMUTATION_VIC) -> str:
    """Le VIC simplifié complet, dans l'ordre du cours :

        1. on convertit le message en chiffres (damier lettres -> chiffres) ;
        2. on additionne la clef, chiffre à chiffre, modulo 10 ;
        3. on transpose les colonnes, bloc de 10 par bloc de 10 ;
        4. on transforme chaque chiffre en lettre avec le damier.

    Le message doit être écrit avec les 10 lettres du damier et sa longueur
    doit être un multiple de 10.
    """
    chiffres = message_en_chiffres(message)
    if len(chiffres) % 10 != 0:
        raise ValueError("la longueur du message doit être un multiple de 10")
    chiffres = ajouter_cle(chiffres, cle)
    chiffres = transposition(chiffres, permutation)
    return chiffrer_avec_damier(chiffres, cle)


def vic_dechiffrer(message: str, cle: str, permutation=PERMUTATION_VIC) -> str:
    """Opération inverse de `vic_chiffrer` (les quatre étapes à l'envers)."""
    chiffres = dechiffrer_avec_damier(message, cle)
    chiffres = transposition(chiffres, permutation_inverse(list(permutation)))
    chiffres = retirer_cle(chiffres, cle)
    return chiffres_en_message(chiffres)


# ---------------------------------------------------------------------------
# Vérification interne : chaque fois que l'on exécute ce fichier, on teste que
# les opérations sont bien inverses l'une de l'autre.  C'est la définition même
# d'un code : d_k(e_k(x)) = x.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    messages_cesar = ["BONJOUR", "LE MESSAGE ARRIVE CE SOIR"]
    for cle in range(26):
        for message in messages_cesar:
            assert cesar_dechiffrer(cesar_chiffrer(message, cle), cle) == message
    print("César : d_k(e_k(x)) = x pour les 26 clefs. OK")

    base = "JEVOUSATTENDSACHETERDEMAINMATINAVANTMIDI"
    for t in range(2, 11):
        # d_t(e_t(x)) = x lorsque la longueur du message est un multiple de t.
        clair = base[: len(base) - len(base) % t]
        assert scytale_dechiffrer(scytale_chiffrer(clair, t), t) == clair
    # Sinon, la dernière ligne est complétée par des X, qui restent au déchiffrement.
    clair = base[: len(base) - len(base) % 5 + 3]
    attendu = clair + "X" * (-len(clair) % 5)
    assert scytale_dechiffrer(scytale_chiffrer(clair, 5), 5) == attendu
    print("Scytale : d_t(e_t(x)) = x (+ X de complément) pour t de 2 à 10. OK")

    for cle in ["CLE", "SECRET", "MATHEMATIQUES"]:
        clair = "LE MESSAGE ARRIVE CE SOIR, A DIX HEURES"
        assert vigenere_dechiffrer(vigenere_chiffrer(clair, cle), cle) == clair
    print("Vigenère : d_k(e_k(x)) = x. OK")

    # Vérification du damier : chaque ligne et chaque colonne contient bien les
    # 10 lettres du damier, une fois et une seule.
    for ligne in range(10):
        assert sorted(TABLEAU_VIC[ligne]) == sorted(ALPHABET_VIC)
    for colonne in range(10):
        assert sorted(TABLEAU_VIC[ligne][colonne] for ligne in range(10)) == sorted(ALPHABET_VIC)
    print("Damier VIC : carré latin (10 lettres par ligne et par colonne). OK")

    message_vic = "LIONSENATO"  # 10 lettres du damier
    for cle in ["12345", "5241730219", "7"]:
        chiffre = vic_chiffrer(message_vic, cle)
        assert vic_dechiffrer(chiffre, cle) == message_vic, (cle, chiffre)
    for permutation in ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]):
        chiffre = vic_chiffrer(message_vic, "12345", permutation)
        assert vic_dechiffrer(chiffre, "12345", permutation) == message_vic
    print("VIC simplifié : d_k(e_k(x)) = x. OK")
