"""Séance 1 — les outils déjà écrits (NE MODIFIEZ PAS CE FICHIER).

Ce fichier ne fait qu'une chose : il rend disponibles, depuis le dossier de la
séance 1, les outils écrits par votre professeur dans `outils/reference.py`.
Vous pouvez donc écrire dans votre TP :

    from common import ALPHABET, comptage, nettoyer, scytale_chiffrer, scytale_dechiffrer

Les outils disponibles ici :

  * `ALPHABET`          : la chaîne "ABC...Z" (26 lettres) ;
  * `nettoyer(texte)`   : met en majuscules et ne garde que les lettres A...Z ;
  * `comptage(texte)`   : compte les 26 lettres du texte (dictionnaire) ;
  * `afficher_comptage(comptes)` : histogramme lisible d'un dictionnaire de comptes ;
  * `scytale_chiffrer(texte, t)` et `scytale_dechiffrer(chiffre, t)` : le code de
    permutation des Spartiates, entièrement écrit.

Prenez l'habitude d'aller lire les docstrings et le code de
`outils/reference.py` : c'est un bon exemple de code Python, et cela vous
montrera comment ces fonctions sont écrites.
"""

from outils.reference import (  # noqa: F401
    ALPHABET,
    afficher_comptage,
    comptage,
    nettoyer,
    scytale_chiffrer,
    scytale_dechiffrer,
)

__all__ = [
    "ALPHABET",
    "afficher_comptage",
    "comptage",
    "nettoyer",
    "scytale_chiffrer",
    "scytale_dechiffrer",
]
