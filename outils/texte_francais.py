"""==========================================================================
 OUTILS DU PROFESSEUR — le « modèle du français » pour la cryptanalyse
==========================================================================

Pour casser un chiffre, il faut savoir reconnaître du français.  C'est le rôle
de ce fichier : il mesure à quel point un texte ressemble à du français.

Il fournit :

  * un CORPUS de référence : un long texte français (environ 2 400 lettres) ;
  * `frequences(texte)`        : la part de chaque lettre, en pourcentage ;
  * `tableau_lettres(...)`     : présentation en tableau aligné ;
  * `barres(...)`              : histogramme en caractères # ;
  * `indice_de_coincidence(texte)` : probabilité que deux lettres tirées au
    hasard dans le texte soient égales (≈ 0,075 en français, ≈ 0,038 pour un
    texte bien mélangé) ;
  * `vraisemblance(texte)`     : note de « françaisité » fondée sur les paires
    de lettres (bigrammes) ; plus la note est GRANDE, plus le texte ressemble à
    du français.  C'est l'outil de l'attaque de la scytale ;
  * `distance_au_francais(texte)` : écart entre les fréquences du texte et
    celles du français ; plus la distance est PETITE, plus le texte ressemble à
    du français.  C'est l'outil de l'attaque de César.

COMMENT LIRE LES COMMENTAIRES
-----------------------------
Un commentaire commence par # et Python l'ignore : il est là pour vous.  Les
lignes qui commencent par >>> sont des exemples à taper dans l'interpréteur.

Ce fichier est un peu plus technique que `reference.py` : vous n'avez pas besoin
d'en comprendre chaque ligne pour faire les TP.  Lisez surtout les docstrings
(les textes entre triple guillemets), qui expliquent à quoi sert chaque
fonction.
==========================================================================
"""

from __future__ import annotations  # ligne technique, sans effet sur le TP

import math                         # pour la fonction math.log (logarithme)
from typing import Optional         # pour écrire « peut valoir None » dans les types

__all__ = [
    "ALPHABET",
    "TEXTE_REFERENCE",
    "barres",
    "chi2",
    "distance_au_francais",
    "frequences",
    "frequences_du_francais",
    "indice_de_coincidence",
    "tableau_lettres",
    "texte_reference",
    "vraisemblance",
]

# La même chaîne alphabétique que dans reference.py (le A est au rang 0).
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ---------------------------------------------------------------------------
# 1. Le corpus de référence
# ---------------------------------------------------------------------------
# C'est un texte français ordinaire, écrit ici « en dur » dans le fichier.
# En le comptant, on obtient les fréquences du français : beaucoup de E, de S,
# de A, et très peu de K, W, Z.

TEXTE_REFERENCE = """
L'art de cacher le sens d'un message est presque aussi ancien que l'ecriture.
En Grèce, les Spartiates enroulaient une lanière de cuir autour d'un bâton, la
scytale, et n'écrivaient que dans le sens de la longueur : pour lire le message
il fallait un bâton de même diamètre. C'est déjà l'idée d'une clef secrète.
Les Romains, dit-on, utilisaient un décalage fixe de l'alphabet que nous
appelons aujourd'hui le chiffre de César, et les militaires en ont gardé
longtemps le souvenir sous le nom d'alphabet trois.

Pendant des siècles, on a cru que le secret du chiffre reposait sur le secret de
son fonctionnement. Il fallait donc changer tout le système dès qu'un espion
perçait le mystère. Auguste Kerckhoffs, à la fin du dix neuvième siècle, a
renversé ce point de vue : la sécurité d'un cryptosystème ne doit pas reposer
sur le secret de la méthode mais seulement sur le secret de la clef. Ce principe
porte son nom et il est encore enseigné aujourd'hui ; il explique pourquoi les
algorithmes modernes sont publiés et étudiés par tous.

La première grande faiblesse des chiffres anciens vient des statistiques. Dans
une langue donnée, certaines lettres sont beaucoup plus fréquentes que d'autres.
En français, la lettre e arrive largement en tête, suivie du s, du a, du i, du t
et du n. Si le chiffrement remplace toujours une lettre donnée par la même autre
lettre, alors les fréquences du texte chiffré gardent celles du texte clair,
simplement déplacées. Un cryptanalyste patient peut donc retrouver la clef sans
aucune information secrète : il compare les deux histogrammes, il devine, il
vérifie, il recommence. Les Arabes du neuvième siècle pratiquaient déjà cette
analyse de fréquences, et c'est elle qui a fait tomber bien des codes.

Pour résister à cette attaque, il faut brouiller les fréquences. L'idée du
chiffre de Vigenère, publiée au seizième siècle, consiste à utiliser non pas une
mais plusieurs substitutions, une par lettre de la clef. La même lettre du texte
clair peut alors devenir vingt lettres différentes dans le texte chiffré : les
comptes ne veulent plus rien dire. On a longtemps surnommé ce chiffre la
méthode indéchiffrable. Le surnom était excessif, comme souvent, mais il a fallu
deux siècles pour montrer comment le casser : on cherche d'abord la longueur de
la clef, puis on traite séparément chacune des substitutions, ce qui ramène le
problème à une simple analyse de fréquences.

Un chiffre n'est jamais un objet isolé. Il faut aussi se demander contre qui on
se protège, avec quels moyens, pendant combien de temps et à quel prix. Un
message dont la lecture demande trois cents ans de calculs est parfaitement sûr
pour la durée d'une guerre. Un mot de passe qui tient une semaine peut suffire
pour un examen, mais pas pour une banque. Enfin, un système se juge sur ses
points faibles : la clef est elle transmise par un canal sûr, le messager
est il fiable, le poste de travail est il protégé, les opérateurs font ils tous
exactement ce qu'ils doivent faire ? L'histoire des codes montre que ce sont
presque toujours ces questions, et non les mathématiques, qui ont livré les
secrets.
"""


def texte_reference():
    """Renvoie le corpus en majuscules, sans accent, sans ponctuation.

    Lecture du code : `c for c in ... if c in ALPHABET` s'appelle une
    « compréhension ».  Elle construit la liste des caractères gardés, et
    `"".join(...)` colle ensuite tous ces caractères en une seule chaîne.
    """
    return "".join(c for c in TEXTE_REFERENCE.upper() if c in ALPHABET)


# ---------------------------------------------------------------------------
# 2. Compter et représenter les lettres
# ---------------------------------------------------------------------------

def frequences(texte):
    """Fréquences des lettres du texte, en POURCENTAGE.

    Renvoie un dictionnaire du genre {"A": 6.5, "B": 0.9, ..., "Z": 0.04} où
    chaque valeur est la part de la lettre dans le texte, en pour cent.
    Les lettres absentes ont une fréquence de 0.0.

        >>> round(frequences("AAB")["A"], 1)
        66.7

    Lecture du code :
        * `total = len(lettres) or 1` : on compte les lettres.  Si le texte est
          vide, la longueur vaut 0, et le `or 1` évite de diviser par zéro ;
        * `100.0 * comptes[lettre] / total` calcule la part, en pourcentage.
          On multiplie par 100.0 (et non 100) pour obtenir un nombre à virgule.
    """
    lettres = [c for c in texte.upper() if c in ALPHABET]   # les lettres seulement
    total = len(lettres) or 1                               # on ne divise pas par 0
    comptes = {lettre: 0 for lettre in ALPHABET}            # 26 compteurs à zéro
    for lettre in lettres:                                  # on compte
        comptes[lettre] += 1
    # On renvoie un pourcentage pour chaque lettre, dans l'ordre A, B, ..., Z.
    return {lettre: 100.0 * comptes[lettre] / total for lettre in ALPHABET}


def tableau_lettres(comptes, en_pourcentage=False):
    """Présente un dictionnaire de comptes sous forme de deux lignes alignées :

        A      B      C    ...
        12     1      3    ...

    Lecture du code :
        * `f"{lettre:>7}"` écrit la lettre alignée à droite sur 7 caractères ;
        * `"".join(...)` colle tous ces petits morceaux pour former une ligne ;
        * `f"{valeur:>7.1f}"` écrit un nombre à virgule avec 1 chiffre après la
          virgule, aligné sur 7 caractères.
    """
    entete = "".join(f"{lettre:>7}" for lettre in ALPHABET)
    if en_pourcentage:
        valeurs = "".join(f"{comptes.get(l, 0.0):>7.1f}" for l in ALPHABET)
    else:
        valeurs = "".join(f"{comptes.get(l, 0):>7}" for l in ALPHABET)
    return entete + "\n" + valeurs


def barres(comptes, largeur=40, maximum=None):
    """Histogramme horizontal : une ligne par lettre, de A à Z.

        A | 0
        B |#################### 14.2857
        ...

    Lecture du code :
        * `maximum or (max(comptes.values()) if comptes else 1)` choisit la plus
          grande valeur : c'est elle qui donnera la plus longue barre ;
        * `"#" * longueur` répète le caractère # ; une barre deux fois plus
          longue signifie un compte deux fois plus grand ;
        * `int(round(...))` transforme en nombre entier de caractères.
    """
    maximum = maximum or (max(comptes.values()) if comptes else 1)
    maximum = maximum or 1                                  # encore une fois 0 ?
    lignes = []
    for lettre in ALPHABET:                                 # une ligne par lettre
        valeur = comptes.get(lettre, 0)
        longueur = int(round(largeur * valeur / maximum))    # barre proportionnelle
        lignes.append(f"{lettre} |{'#' * longueur} {valeur:g}")
    return "\n".join(lignes)                                # les lignes collées


def chi2(observes, attendus):
    """Écart entre deux distributions de fréquences (test du khi-deux).

    Plus le résultat est PETIT, plus les deux distributions se ressemblent.

    Ordres de grandeur mesurés avec le corpus de référence :
        * texte français                     : moins de 50 ;
        * texte français mal décalé (César)  : plusieurs centaines.

    Lecture du code :
        * pour chaque lettre, on calcule l'écart `observes - attendus` ;
        * on l'élève au carré (pour que les écarts négatifs comptent aussi) ;
        * on le divise par la valeur attendue (les grosses valeurs pardonnent) ;
        * on additionne le tout : c'est la « distance » totale.
    """
    total = 0.0
    for lettre in ALPHABET:
        attendu = attendus.get(lettre, 0.0)
        if attendu <= 0:                     # on ne divise pas par zéro
            continue
        ecart = observes.get(lettre, 0.0) - attendu
        total += ecart * ecart / attendu     # le carré de l'écart, pondéré
    return total


# ---------------------------------------------------------------------------
# 3. Le modèle : les fréquences du français, et les bigrammes
# ---------------------------------------------------------------------------

# _FREQUENCES_DU_FRANCAIS est une variable « mémoire » : la première fois qu'on
# demande les fréquences du français, on les calcule et on les range ici ; les
# fois suivantes, on les relit directement (cela évite de recompter 2 400
# lettres à chaque appel).
_FREQUENCES_DU_FRANCAIS = None


def frequences_du_francais():
    """Fréquences des lettres du français (en pourcentage), calculées une fois
    pour toutes sur le corpus de référence."""
    global _FREQUENCES_DU_FRANCAIS          # on modifie la variable du dessus
    if _FREQUENCES_DU_FRANCAIS is None:     # pas encore calculée ?
        _FREQUENCES_DU_FRANCAIS = frequences(texte_reference())
    return _FREQUENCES_DU_FRANCAIS


def distance_au_francais(texte):
    """Mesure à quel point `texte` ressemble à du français du point de vue des
    FRÉQUENCES DES LETTRES.

        PLUS LA DISTANCE EST PETITE, PLUS LE TEXTE RESSEMBLE À DU FRANÇAIS.
        (0 serait un texte aux fréquences exactement françaises.)

    Usage typique — casser un code de César :

        for cle in range(26):                       # les 26 clefs possibles
            candidat = cesar_dechiffrer(chiffre, cle)
            print(cle, distance_au_francais(candidat))

    ATTENTION (piège classique) : deux textes qui ne diffèrent que par un
    décalage de l'alphabet ont exactement le même indice de coïncidence.  C'est
    pourquoi l'indice de coïncidence ne sert PAS à casser César : il faut
    comparer les fréquences lettre par lettre, ce que fait cette fonction.
    """
    return chi2(frequences(texte), frequences_du_francais())


# _TABLE_BIGRAMMES garde en mémoire la probabilité de chaque paire de lettres
# (« bigramme »), estimée sur le corpus.
_TABLE_BIGRAMMES = None


def _table_bigrammes():
    """Table des probabilités de toutes les paires de lettres (AA, AB, ..., ZZ),
    estimées sur le corpus de référence, avec un petit « lissage » pour qu'aucune
    paire n'ait une probabilité nulle.

    Lecture du code :
        * on compte chaque paire de lettres consécutives : `texte[i:i+2]` prend
          deux caractères côte à côte ;
        * `comptes.get(paire, 0) + 1` augmente le compteur de cette paire ;
        * on divise par le nombre total de paires pour obtenir une probabilité ;
        * le « lissage » (0.5) ajoute une petite quantité à chaque paire, ce qui
          évite les probabilités nulles que le logarithme n'aime pas.
    """
    global _TABLE_BIGRAMMES
    if _TABLE_BIGRAMMES is None:                    # calculé une seule fois
        texte = texte_reference()
        comptes = {}
        for position in range(len(texte) - 1):      # toutes les paires voisines
            paire = texte[position:position + 2]
            comptes[paire] = comptes.get(paire, 0) + 1
        total = sum(comptes.values())
        lissage = 0.5
        _TABLE_BIGRAMMES = {
            a + b: (comptes.get(a + b, 0) + lissage) / (total + 676 * lissage)
            for a in ALPHABET
            for b in ALPHABET                        # les 26 x 26 paires possibles
        }
    return _TABLE_BIGRAMMES


def vraisemblance(texte):
    """Note de « françaisité » fondée sur l'ORDRE des lettres (les paires).

        PLUS LA NOTE EST GRANDE, PLUS LE TEXTE RESSEMBLE À DU FRANÇAIS.

    Ordres de grandeur mesurés avec cette fonction :
        * corpus de référence (texte français suivi)  : environ -5,2 ;
        * phrase française normale                    : environ -5,3 à -5,8 ;
        * texte brouillé (permutation, charabia)      : environ -5,9 et moins.

    Pourquoi c'est indispensable pour la scytale : une permutation ne change
    AUCUNE lettre, donc tous les candidats ont les mêmes fréquences.  Ce qui les
    distingue, c'est l'ordre des lettres : « ES », « LE », « DE », « NT » sont
    fréquents en français, « XZ » ou « QK » ne le sont pas.

    Lecture du code :
        * `math.log(...)` calcule le logarithme (négatif, car les probabilités
          sont inférieures à 1) ; on fait la moyenne des logarithmes, ce qui
          évite que les longs textes soient pénalisés ;
        * on divise par `len(texte) - 1` (le nombre de paires) pour obtenir une
          note comparable d'un texte à l'autre.
    """
    texte = "".join(c for c in texte.upper() if c in ALPHABET)   # lettres seules
    if len(texte) < 2:                                           # pas de paire ?
        return -99.0                                             # note très mauvaise
    table = _table_bigrammes()
    total = 0.0
    for position in range(len(texte) - 1):                       # chaque paire
        total += math.log(table[texte[position:position + 2]])   # son logarithme
    return total / (len(texte) - 1)                              # la moyenne


# ---------------------------------------------------------------------------
# 4. L'indice de coïncidence (outil des séances 1 et 3)
# ---------------------------------------------------------------------------

def indice_de_coincidence(texte):
    """Indice de coïncidence : probabilité que deux lettres tirées au hasard
    dans le texte soient identiques.

    Repères, pour un alphabet de 26 lettres :
        * texte écrit dans une langue (structuré)   : environ 0,07 ;
        * texte bien mélangé (lettres équiprobables) : environ 0,038 (= 1/26).

    Utilisation : c'est l'outil qui permet de deviner si un texte est resté
    « structuré » comme le français.  Il sert en séance 3 à trouver la période de
    Vigenère.  Il NE sert PAS à casser César : il est le même pour les 26
    décalages (voir `distance_au_francais`).

    Lecture du code :
        * `n = len(lettres)` : le nombre de lettres ;
        * `compte * (compte - 1)` : c'est le nombre de paires ordonnées que l'on
          peut former avec les `compte` exemplaires de cette lettre ;
        * on divise par `n * (n - 1)`, le nombre total de paires possibles : le
          résultat est bien une probabilité.
    """
    lettres = [c for c in texte.upper() if c in ALPHABET]     # les lettres du texte
    n = len(lettres)
    if n < 2:                                                 # besoin de 2 lettres
        return 0.0
    comptes = {lettre: 0 for lettre in ALPHABET}              # 26 compteurs à zéro
    for lettre in lettres:
        comptes[lettre] += 1
    numerateur = sum(compte * (compte - 1) for compte in comptes.values())
    return numerateur / (n * (n - 1))                         # une probabilité


# ---------------------------------------------------------------------------
# Test rapide : quand on lance ce fichier directement, on affiche le modèle.
#     python3 outils/texte_francais.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    reference = texte_reference()
    print("Longueur du corpus de référence :", len(reference), "lettres")
    print()
    print("Fréquences des lettres dans ce corpus (en pourcentage) :")
    print(tableau_lettres(frequences(reference), en_pourcentage=True))
    print()
    print("Histogramme :")
    print(barres(frequences(reference)))
    print()
    print("Indice de coïncidence du corpus :", round(indice_de_coincidence(reference), 4))
    print("Vraisemblance du corpus        :", round(vraisemblance(reference), 3))
    print()
    print("Pour comparaison, la vraisemblance d'un texte brouillé :")
    # On importe la scytale ici, et l'on s'assure que le dossier « outils » est
    # accessible, quel que soit l'endroit d'où l'on lance la commande.
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from outils.reference import scytale_chiffrer
    bouilli = scytale_chiffrer("LEGRANDMESSAGERARRIVECETTEAPRESMIDI", 7)
    print("  scytale à clef 7 :", round(vraisemblance(bouilli), 3))
