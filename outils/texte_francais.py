"""Outils « tout faits » sur le texte français (à utiliser, pas à réécrire).

Deux ensembles d'outils :

1. Le corpus de référence `TEXTE_REFERENCE` : un long texte en français écrit
   en toutes lettres (sans chiffres ni ponctuation).  Il sert de *modèle* du
   français pour la cryptanalyse statistique : en comptant les lettres de ce
   texte, on obtient les fréquences de la langue française, et on peut les
   comparer aux fréquences d'un message chiffré.

2. Des fonctions d'affichage : `tableau_lettres`, `barres`, `chi2`, `indice_de_coincidence`.

Toutes ces fonctions n'utilisent que la bibliothèque standard Python.
"""

from __future__ import annotations

import math

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


# ---------------------------------------------------------------------------
# 1. Le corpus de référence
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# 2. Fonctions d'affichage et de mesure
# ---------------------------------------------------------------------------

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def texte_reference() -> str:
    """Renvoie le corpus de référence, mis en majuscules et débarrassé de tout
    ce qui n'est pas une lettre de A à Z."""
    return "".join(c for c in TEXTE_REFERENCE.upper() if c in ALPHABET)


def frequences(texte: str) -> dict:
    """Fréquences des lettres de `texte`, en pourcentage.

    Renvoie un dictionnaire `{"A": 8.1, "B": 0.9, ...}` pour les 26 lettres,
    chaque valeur étant le pourcentage d'occurrence (0.0 si la lettre est
    absente).  Le texte est d'abord nettoyé : tout caractère qui n'est pas une
    lettre de A à Z est ignoré.
    """
    lettres = [c for c in texte.upper() if c in ALPHABET]
    total = len(lettres) or 1
    comptes = {lettre: 0 for lettre in ALPHABET}
    for lettre in lettres:
        comptes[lettre] += 1
    return {lettre: 100.0 * comptes[lettre] / total for lettre in ALPHABET}


def tableau_lettres(comptes: dict, en_pourcentage: bool = False) -> str:
    """Présente un dictionnaire de comptes sous forme de deux lignes alignées.

        A    B    C   ...
        12   1    3   ...

    `comptes` peut venir de `comptage` (nombres) ou de `frequences` (pourcentages).
    """
    entete = "".join(f"{lettre:>7}" for lettre in ALPHABET)
    if en_pourcentage:
        valeurs = "".join(f"{comptes.get(l, 0.0):>7.1f}" for l in ALPHABET)
    else:
        valeurs = "".join(f"{comptes.get(l, 0):>7}" for l in ALPHABET)
    return entete + "\n" + valeurs


def barres(comptes: dict, largeur: int = 40, maximum: int | float | None = None) -> str:
    """Histogramme horizontal, une ligne par lettre (de A à Z).

    Utile pour « voir » les fréquences d'un texte chiffré et les comparer à
    celles du français.  Exemple (à essayer dans l'interpréteur) :

        print(barres(frequences("BONJOUR")))
        A | 0
        B |#################### 14.2857
        ...
        O |######################################## 28.5714
    """
    maximum = maximum or (max(comptes.values()) if comptes else 1)
    maximum = maximum or 1
    lignes = []
    for lettre in ALPHABET:
        valeur = comptes.get(lettre, 0)
        longueur = int(round(largeur * valeur / maximum))
        lignes.append(f"{lettre} |{'#' * longueur} {valeur:g}")
    return "\n".join(lignes)


def chi2(observes: dict, attendus: dict) -> float:
    """« Distance » entre deux distributions de fréquences (test du khi-deux).

    Plus le résultat est petit, plus les deux distributions se ressemblent.
    Sert à comparer les fréquences d'un texte candidat avec celles du français.
    Ordres de grandeur mesurés avec le corpus de référence :

        * texte français                     : moins de 50 ;
        * texte chiffré par César mal décalé : plusieurs centaines.

    Pour un usage direct, préférez `distance_au_francais(candidat)`.
    """
    total = 0.0
    for lettre in ALPHABET:
        attendu = attendus.get(lettre, 0.0)
        if attendu <= 0:
            continue
        ecart = observes.get(lettre, 0.0) - attendu
        total += ecart * ecart / attendu
    return total


_TABLE_BIGRAMMES = None


def _table_bigrammes():
    """Table (une fois pour toutes) de la probabilité de chaque paire de lettres,
    estimée sur le corpus de référence, avec un petit lissage pour qu'aucune
    paire n'ait une probabilité nulle."""
    global _TABLE_BIGRAMMES
    if _TABLE_BIGRAMMES is None:
        texte = texte_reference()
        comptes = {}
        for position in range(len(texte) - 1):
            paire = texte[position:position + 2]
            comptes[paire] = comptes.get(paire, 0) + 1
        total = sum(comptes.values())
        lissage = 0.5
        _TABLE_BIGRAMMES = {
            a + b: (comptes.get(a + b, 0) + lissage) / (total + 676 * lissage)
            for a in ALPHABET
            for b in ALPHABET
        }
    return _TABLE_BIGRAMMES


def vraisemblance(texte: str) -> float:
    """Mesure à quel point `texte` ressemble à du français, en tenant compte de
    l'ORDRE des lettres (et non seulement de leur fréquence).

    On calcule la vraisemblance moyenne des paires de lettres consécutives :
    dans un texte français, les paires « ES », « LE », « EN », « DE », « NT »
    sont fréquentes, tandis que « XZ », « QK » ou « BN » sont presque
    impossibles.  Un texte français obtient ainsi un score nettement plus
    élevé qu'un charabia.

    PLUS LE SCORE EST GRAND (donc, comme c'est un logarithme, moins négatif),
    PLUS LE TEXTE RESSEMBLE À DU FRANÇAIS.  Ordres de grandeur mesurés avec
    cette fonction :

        * corpus de référence (texte français suivi) : environ -5,2 ;
        * phrase française normale                   : environ -5,3 à -5,8 ;
        * texte brouillé (permutation, charabia)     : environ -5,9 et moins.

    C'est l'outil qui permet de classer les candidats d'un code de
    permutation : on garde celui dont la vraisemblance est la plus grande.
    """
    texte = "".join(c for c in texte.upper() if c in ALPHABET)
    if len(texte) < 2:
        return -99.0
    table = _table_bigrammes()
    total = 0.0
    for position in range(len(texte) - 1):
        total += math.log(table[texte[position:position + 2]])
    return total / (len(texte) - 1)


_FREQUENCES_DU_FRANCAIS = None


def frequences_du_francais() -> dict:
    """Fréquences des lettres du français (en pourcentage), calculées une fois
    pour toutes sur le corpus de référence `TEXTE_REFERENCE`.

    Renvoie un dictionnaire du type `{"A": 6.5, "B": 0.9, ..., "Z": 0.04}`.
    C'est le « modèle » auquel on compare un texte candidat.
    """
    global _FREQUENCES_DU_FRANCAIS
    if _FREQUENCES_DU_FRANCAIS is None:
        _FREQUENCES_DU_FRANCAIS = frequences(texte_reference())
    return _FREQUENCES_DU_FRANCAIS


def distance_au_francais(texte: str) -> float:
    """Mesure à quel point `texte` ressemble à du français du point de vue des
    fréquences de lettres.  PLUS LA DISTANCE EST PETITE, PLUS LE TEXTE
    RESSEMBLE À DU FRANÇAIS (0 serait un texte aux fréquences exactement
    françaises).

    Utilisation typique — retrouver la clef d'un code de César en essayant les
    26 clefs possibles :

        for cle in range(26):
            candidat = cesar_dechiffrer(chiffre, cle)
            print(cle, distance_au_francais(candidat))

    Attention : deux textes qui ne diffèrent que par un décalage de l'alphabet
    (donc deux candidats d'un code de César) ont EXACTEMENT le même indice de
    coïncidence : c'est pour cela qu'on n'utilise pas l'indice de coïncidence
    ici, mais la comparaison des fréquences lettre par lettre, que réalise
    cette fonction.
    """
    return chi2(frequences(texte), frequences_du_francais())


def indice_de_coincidence(texte: str) -> float:
    """Indice de coïncidence : probabilité que deux lettres tirées au hasard
    dans le texte soient identiques.

    Repères utiles, pour un alphabet de 26 lettres :

        * texte écrit dans une langue (structures répétées) : environ 0,07 ;
        * texte chiffré « bien mélangé » (lettres presque équiprobables) : environ 0,038.

    C'est l'outil de base pour deviner si un chiffrement a conservé les
    structures du français.
    """
    lettres = [c for c in texte.upper() if c in ALPHABET]
    n = len(lettres)
    if n < 2:
        return 0.0
    comptes = {lettre: 0 for lettre in ALPHABET}
    for lettre in lettres:
        comptes[lettre] += 1
    numerateur = sum(compte * (compte - 1) for compte in comptes.values())
    return numerateur / (n * (n - 1))


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
