"""==========================================================================
 TP 3 — CRYPTANALYSE DE VIGENÈRE (KASISKI, FRIEDMAN) ET CODE DE VIC
 Chapitre 2 (fin) : « Cryptanalyse » et « Code de VIC » — Pascal Boyer,
 « Cryptographie 2013 ».

 Durée conseillée : 2 h à 2 h 30.   À rendre : ce fichier complété.
==========================================================================

 ██  MODE D'EMPLOI  ██
==========================================================================

Au TP 2, tu cassais un message de Vigenère À CONDITION de connaître déjà la
longueur de la clef.  Ici, tu ne connais RIEN : tu as seulement le texte
intercepté.  L'attaque se fait en deux temps, et c'est tout le programme de
cette séance :

    1. TROUVER LA PÉRIODE (le nombre de lettres de la clef), sans aucune
       indication.  Deux méthodes, que tu vas écrire toutes les deux :
         * la méthode de KASISKI (1863) : on repère les groupes de lettres qui
           se répètent, on mesure les distances entre répétitions, et l'on
           remarque que ces distances sont souvent des multiples de la période ;
         * l'INDICE DE COÏNCIDENCE (Friedman, années 1920) : on découpe le texte
           en p colonnes pour chaque valeur de p, et l'on regarde si les
           colonnes ressemblent à du français.  Elles y ressemblent quand p est
           la période.
    2. CASSER CHAQUE COLONNE (comme au TP 2), une fois la période connue.

Puis la deuxième partie de la séance : le code de VIC.

Chaque exercice suit le même plan que dans les TP précédents :
    OBJECTIF / POURQUOI (COURS) / CE QUE TU DOIS FAIRE / RAPPELS PYTHON /
    À COMPLÉTER (avec les ... à remplacer) / ✅ SOLUTION.

LA BOUCLE DE TRAVAIL
   1. écris une fonction dans ce fichier ;
   2. tape, dans ce dossier :   python3 test_tp3_vigenere_vic.py
   3. lis le bilan, corrige, recommence.

LES DOUZE FONCTIONS À ÉCRIRE
----------------------------
   A.1  indice_coincidence_moyen    A.2  indices_par_periode    A.3  periode_probable
   B.1  grammes_repetes             B.2  kasiski_distances      B.3  diviseurs
   C.1  forcer_cesar_sur_colonne    C.2  forcer_vigenere
   D.1  caractere_vic               D.2  ligne_du_damier
   D.3  chiffre_du_damier           D.4  dechiffrer_message_vic
==========================================================================
"""

# ---------------------------------------------------------------------------
# LES IMPORTS (n'y touche pas)
# ---------------------------------------------------------------------------
# Ces trois lignes permettent à Python de trouver le dossier « outils ».
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Les outils du professeur.  Tu en reconnais déjà plusieurs (TP 1 et TP 2) :
#   * ALPHABET, nettoyer, comptage ......... les outils de base ;
#   * indice_de_coincidence(texte) ......... la fonction qui mesure si un texte
#     est resté « structuré » (0,075 pour du français, 0,038 pour du charabia) ;
#   * distance_au_francais(texte) .......... l'écart aux fréquences du français
#     (plus la valeur est PETITE, plus c'est du français) ;
#   * pour le VIC : ALPHABET_VIC, TABLEAU_VIC, PERMUTATION_VIC, lettre_vic,
#     deviner_ligne_vic, transposition, permutation_inverse, retirer_cle,
#     chiffres_en_message, message_en_chiffres, ajouter_cle...
from outils.reference import (
    ALPHABET,
    ALPHABET_VIC,
    PERMUTATION_VIC,
    TABLEAU_VIC,
    chiffres_en_message,
    deviner_ligne_vic,
    lettre_vic,
    nettoyer,
    permutation_inverse,
    retirer_cle,
    transposition,
)
from outils.texte_francais import distance_au_francais, indice_de_coincidence


# ###########################################################################
#
#  RAPPELS DU COURS — À LIRE AVANT DE COMMENCER
#
# ###########################################################################
#
# 1) POURQUOI LA PÉRIODE EST LA CLÉ DE TOUT
#    Si la clef fait p lettres, alors les caractères aux positions 0, p, 2p...
#    sont décalés de la MÊME quantité : en les séparant, on retrouve un simple
#    code de César par colonne.  Toute l'attaque consiste donc à deviner p.
#
# 2) LA MÉTHODE DE KASISKI (1853-1863)
#    Si un groupe de lettres apparaît deux fois dans le texte clair, il apparaît
#    deux fois dans le texte chiffré, décalé du même « coup de clef ».  La
#    distance entre les deux répétitions est donc un MULTIPLE DE LA PÉRIODE.
#    On repère les groupes répétés, on calcule les distances, on regarde quels
#    diviseurs reviennent le plus souvent : ce sont les périodes candidates.
#
# 3) L'INDICE DE COÏNCIDENCE (Friedman, années 1920)
#    Rappel du cours : l'indice de coïncidence d'un texte est la probabilité que
#    deux lettres tirées au hasard y soient identiques :
#        * texte français (structuré) : environ 0,075 ;
#        * texte bien mélangé          : environ 0,038 (= 1/26).
#    Si l'on découpe le texte chiffré en p colonnes et que p est la période,
#    chaque colonne est un César du français : son indice vaut 0,075 environ.
#    Sinon, la moyenne retombe vers 0,04.  ATTENTION : les MULTIPLES de la
#    période (2p, 3p...) donnent aussi un indice élevé ; il faut donc choisir la
#    plus PETITE période qui « fonctionne ».
#
# 4) LE CODE DE VIC (fin du chapitre 2)
#    Utilisé par le service secret britannique à partir de 1914, en quatre
#    étapes (cours) :
#       (1) la clef est écrite au-dessus du message ;
#       (2) on additionne la clef au message, chiffre à chiffre, sans retenue ;
#       (3) on brouille l'ordre des caractères (transposition) ;
#       (4) on convertit chaque chiffre en lettre grâce à un damier 10 x 10.
#    Nous étudions une version SIMPLIFIÉE, entièrement décrite dans
#    `outils/reference.py` (section 5) : le message est écrit avec les 10 lettres
#    du damier "SENATROIDL", la clef est une suite de chiffres, et le « chiffre
#    indicateur » (la colonne du damier) est la position du caractère dans son
#    bloc de 10.  Les différences avec le vrai VIC y sont expliquées honnêtement.
#
# ###########################################################################


# ==========================================================================
# OUTIL FOURNI (repris du TP 2) — découpage en colonnes
# ==========================================================================

def colonnes(texte, periode):
    """Découpe le texte en `periode` colonnes (fourni : ne pas modifier).

        >>> colonnes("ABCDEFGHIJ", 3)
        ['ADGJ', 'BEH', 'CFI']

    Lecture du code : `position % periode` donne le numéro de colonne du
    caractère situé à la position `position` (0, 1, 2, 0, 1, 2...) ; on ajoute
    donc chaque caractère à la bonne colonne.
    """
    morceaux = ["" for _ in range(periode)]         # `periode` chaînes vides
    for position, caractere in enumerate(texte):    # position ET caractère
        morceaux[position % periode] += caractere   # on range dans la colonne
    return morceaux


# ==========================================================================
# PARTIE A — TROUVER LA PÉRIODE PAR L'INDICE DE COÏNCIDENCE
# ==========================================================================

def indice_coincidence_moyen(texte, periode):
    """A.1 — OBJECTIF : calculer la MOYENNE des indices de coïncidence des
    `periode` colonnes du texte.

    POURQUOI (COURS) : c'est le test de Friedman.  Si `periode` est la bonne
    longueur de clef, chaque colonne est un texte français décalé, donc
    l'indice de chaque colonne vaut environ 0,075, et la moyenne aussi.  Si la
    période est fausse, chaque colonne mélange plusieurs décalages différents :
    les lettres deviennent presque équiprobables et la moyenne retombe vers
    0,038.

    CE QUE TU DOIS FAIRE :
        étape 1 : range le texte en colonnes (fonction fournie) :
                      morceaux = colonnes(texte, periode)
        étape 2 : prépare un total à 0.0 ;
        étape 3 : parcours les morceaux et ajoute leur indice de coïncidence :
                      for morceau in morceaux:
                          total += indice_de_coincidence(morceau)
        étape 4 : renvoie la moyenne : total / len(morceaux).

    RAPPELS PYTHON :
        * `indice_de_coincidence(texte)` est fourni, il renvoie un nombre entre
          0 et 1 ;
        * une « moyenne » se calcule en additionnant puis en divisant par le
          nombre d'éléments ;
        * attention au texte vide : si le texte est vide, renvoie 0.0 pour
          éviter une division par zéro.

    EXEMPLES (ce que les tests vérifient) :
        indice_coincidence_moyen("ABAB", 2)  ->  1.0
            (les colonnes sont "AA" et "BB" : dans chacune, deux lettres tirées
             au hasard sont toujours égales, donc l'indice vaut 1)
        Sur un vrai message chiffré par une clef de 4 lettres :
            l'indice pour la période 4 est supérieur à 0,07 ;
            l'indice pour la période 3 est inférieur à 0,06.
    """
    # --- À COMPLÉTER ---
    if not texte:                                       # texte vide ?
        return 0.0
    morceaux = colonnes(..., periode)                   # les colonnes
    total = ...                                         # un total à 0.0
    for morceau in morceaux:                            # chaque colonne
        total += indice_de_coincidence(...)             # son indice
    return total / ...                                  # la moyenne

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     if not texte:
    #         return 0.0
    #     morceaux = colonnes(texte, periode)
    #     total = 0.0
    #     for morceau in morceaux:
    #         total += indice_de_coincidence(morceau)
    #     return total / len(morceaux)
    # ----------------------------------------------------------------------


def indices_par_periode(texte, maximum=15):
    """A.2 — OBJECTIF : construire le tableau des indices de coïncidence pour
    TOUTES les périodes de 1 à `maximum`.

    POURQUOI (COURS) : c'est le tableau que l'on regarde pour deviner la période.
    Les périodes « qui marchent » ressortent nettement : 0,075 contre 0,04 pour
    les autres.  En construisant le tableau d'un coup, on voit le contraste.

    CE QUE TU DOIS FAIRE :
        prépare un dictionnaire vide, puis, pour chaque période de 1 à maximum,
        range l'indice correspondant :
            resultat = {}
            for periode in range(1, maximum + 1):
                resultat[periode] = indice_coincidence_moyen(texte, periode)
            return resultat
        
        (Tu peux aussi écrire ce dictionnaire en une seule ligne, c'est une
        « compréhension » ; voir le GESTE 7 du TP 1.)

    RAPPELS PYTHON :
        * un dictionnaire s'écrit avec des accolades : `{periode: valeur}` ;
        * `range(1, maximum + 1)` donne 1, 2, ..., maximum (maximum compris).

    EXEMPLE (ce que les tests vérifient) :
        indices = indices_par_periode(chiffre, 10)   ->  {1: 0.047, 2: 0.041,
            3: 0.038, 4: 0.072, ..., 8: 0.075, ...}
        On y voit que 4 est la première période remarquable (puis 8, son
        multiple).
    """
    # --- À COMPLÉTER ---
    resultat = ...                                      # un dictionnaire vide
    for periode in range(1, ...):                       # de 1 à maximum inclus
        resultat[periode] = indice_coincidence_moyen(texte, ...)
    return ...                                          # renvoie le tableau

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     resultat = {}
    #     for periode in range(1, maximum + 1):
    #         resultat[periode] = indice_coincidence_moyen(texte, periode)
    #     return resultat
    # ----------------------------------------------------------------------


def periode_probable(texte, maximum=15, proportion=0.9):
    """A.3 — OBJECTIF : renvoyer la période la plus probable du texte chiffré.

    LA RÈGLE (et pourquoi celle-là) :
        1. calcule tous les indices (ta fonction A.2) ;
        2. appelle `meilleur` le plus grand de ces indices ;
        3. renvoie la PLUS PETITE période dont l'indice atteint au moins
           `proportion` fois le meilleur (0,9 par défaut, soit 90 %).

    POURQUOI 90 % DU MEILLEUR PLUTÔT QU'UN SEUIL FIXE ?  Parce que la valeur des
    indices dépend de la longueur du texte : un seuil fixe (0,06 par exemple)
    marche pour un texte de 600 lettres et échoue pour un texte de 120 lettres.
    Comparer les périodes entre elles est beaucoup plus solide.
    (Attention : un simple seuil fixe peut aussi se tromper d'une autre manière.
    Exemple vécu : pour une vraie période de 6, l'indice de la période 3 monte
    parfois à 0,067, au-dessus du seuil de 0,06 !)

    POURQUOI LA PLUS PETITE ?  Parce que si la vraie période est 5, les périodes
    10, 15, 20... donnent aussi des colonnes correctes (multiples de 5) : elles
    « marchent » aussi, mais ce n'est pas la vraie clef.

    CE QUE TU DOIS FAIRE :
        étape 1 : indices = indices_par_periode(texte, maximum) ;
        étape 2 : calcule le seuil : `seuil = proportion * max(indices.values())`
                  (la méthode `.values()` donne toutes les valeurs du
                  dictionnaire ; `max(...)` prend la plus grande) ;
        étape 3 : parcours les périodes de 1 à maximum, dans l'ordre croissant,
                  et renvoie la première dont l'indice est supérieur ou égal au
                  seuil :
                      for periode in range(1, maximum + 1):
                          if indices[periode] >= seuil:
                              return periode
        étape 4 : si aucune période ne convient (cela arrive rarement), renvoie
                  None.

    RAPPELS PYTHON :
        * `max(indices.values())` : la plus grande valeur du dictionnaire ;
        * `!=`, `>=` : comparaisons (différent, supérieur ou égal) ;
        * `None` est la valeur « rien du tout ».

    RESPONSABILITÉ D'INTERPRÉTATION (à écrire dans ton rapport) : si TOUS les
    indices sont élevés (par exemple si le texte n'est pas brouillé du tout),
    la règle renvoie une période quelconque.  Ce n'est pas grave : dans ce cas,
    n'importe quelle clef de cette longueur déchiffre correctement le message,
    puisque le chiffrement n'était qu'un seul décalage.

    EXEMPLE (ce que les tests vérifient) : pour des messages chiffrés avec des
    clefs de 4, 5, 6 et 7 lettres, la fonction doit renvoyer 4, 5, 6 et 7.
    """
    # --- À COMPLÉTER ---
    indices = indices_par_periode(texte, ...)           # le tableau des indices
    if not indices:                                     # sécurité
        return None
    seuil = proportion * max(indices.values())          # 90 % du meilleur indice
    for periode in range(1, maximum + 1):               # de la plus petite à la plus grande
        if indices[periode] >= ...:                     # atteint-on le seuil ?
            return ...                                  # trouvé !
    return ...                                          # aucune période ne convient

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     indices = indices_par_periode(texte, maximum)
    #     if not indices:
    #         return None
    #     seuil = proportion * max(indices.values())
    #     for periode in range(1, maximum + 1):
    #         if indices[periode] >= seuil:
    #             return periode
    #     return None
    # ----------------------------------------------------------------------


# ==========================================================================
# PARTIE B — LA MÉTHODE DE KASISKI
# ==========================================================================
#
# Principe (rappel du cours) : deux occurrences du même groupe de lettres dans
# le texte clair sont chiffrées par le même « coup de clef » ; dans le texte
# chiffré, elles sont donc séparées par une distance multiple de la période.
# On repère les groupes répétés, on mesure les distances, et l'on regarde leurs
# diviseurs.  À la fin, on croise ce résultat avec l'indice de coïncidence :
# c'est ainsi que travaille vraiment un cryptanalyste — deux indices faibles
# valent mieux qu'un.


def grammes_repetes(chiffre, taille):
    """B.1 — OBJECTIF : trouver les groupes de `taille` lettres qui apparaissent
    AU MOINS DEUX FOIS dans le texte chiffré.

    POURQUOI (COURS) : ce sont les répétitions de Kasiski.  Pour une taille de
    3 lettres (« ABC »), on les appelle des trigrammes, pour 4 des
    quadrigrammes.  Plus un groupe est long, plus il indique une vraie
    répétition du texte clair (et non un hasard).

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare un dictionnaire vide `comptes = {}` ;
        étape 2 : parcours les positions de 0 à len(chiffre) - taille :
                      for debut in range(len(chiffre) - taille + 1):
        étape 3 : prends le groupe qui commence à cette position :
                      morceau = chiffre[debut:debut + taille]
                  et compte-le :
                      comptes[morceau] = comptes.get(morceau, 0) + 1
        étape 4 : prépare une liste vide `repetes = []` ;
        étape 5 : parcours les clefs du dictionnaire :
                      for morceau in comptes:
                  et ajoute à la liste ceux dont le compte est >= 2 :
                      if comptes[morceau] >= 2:
                          repetes.append(morceau)
        étape 6 : renvoie la liste TRIÉE : `return sorted(repetes)`.

    RAPPELS PYTHON :
        * `comptes.get(morceau, 0)` : la valeur déjà comptée, ou 0 si le groupe
          n'a pas encore été vu (cela évite l'erreur « clef inconnue ») ;
        * `sorted(liste)` range la liste par ordre alphabétique : le résultat
          des tests est ainsi toujours le même, quel que soit l'ordre interne du
          dictionnaire ;
        * deux boucles séparées (une pour compter, une pour garder) : c'est plus
          clair que tout faire dans une seule boucle.

    EXEMPLES (ce que les tests vérifient) :
        grammes_repetes("ABCIABCXABC", 3)  ->  ["ABC"]
        grammes_repetes("ABCDEF", 3)       ->  []      (aucune répétition)
        grammes_repetes("ABCDABCD", 4)     ->  ["ABCD"]
    """
    # --- À COMPLÉTER ---
    comptes = ...                                       # un dictionnaire vide
    for debut in range(len(chiffre) - taille + 1):      # chaque position de départ
        morceau = chiffre[debut:debut + ...]            # les `taille` caractères
        comptes[morceau] = comptes.get(morceau, ...) + 1   # on compte ce groupe

    repetes = []                                        # les groupes vus 2 fois ou plus
    for morceau in comptes:                             # parcours des clefs
        if comptes[morceau] >= ...:
            repetes.append(...)                         # on garde le groupe
    return sorted(...)                                  # renvoie la liste triée

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     comptes = {}
    #     for debut in range(len(chiffre) - taille + 1):
    #         morceau = chiffre[debut:debut + taille]
    #         comptes[morceau] = comptes.get(morceau, 0) + 1
    #
    #     repetes = []
    #     for morceau in comptes:
    #         if comptes[morceau] >= 2:
    #             repetes.append(morceau)
    #     return sorted(repetes)
    # ----------------------------------------------------------------------


def kasiski_distances(chiffre, mot):
    """B.2 — OBJECTIF : calculer les distances entre les répétitions successives
    du groupe `mot` dans le texte chiffré.

    POURQUOI (COURS) : c'est le cœur de la méthode de Kasiski.  Exemple : si
    « ABC » apparaît aux positions 4 et 13, la distance est 13 - 4 = 9.  Un tel
    écart est presque toujours un multiple de la période : c'est ce que l'on
    cherche.

    CE QUE TU DOIS FAIRE :
        étape 1 : trouve toutes les positions où `mot` commence :
                      positions = []
                      for debut in range(len(chiffre) - len(mot) + 1):
                          if chiffre[debut:debut + len(mot)] == mot:
                              positions.append(debut)
        étape 2 : calcule les distances entre positions voisines :
                      distances = []
                      for rang in range(len(positions) - 1):
                          distance = positions[rang + 1] - positions[rang]
                          if distance not in distances:      # sans doublon
                              distances.append(distance)
        étape 3 : renvoie les distances TRIÉES : `return sorted(distances)`.

    RAPPELS PYTHON :
        * `chiffre[debut:debut + len(mot)] == mot` : compare deux extraits de
          texte avec == (deux signes égaux !) ;
        * `positions[rang + 1] - positions[rang]` : la distance entre deux
          positions consécutives ;
        * `if distance not in distances:` : teste si la distance est déjà dans
          la liste (pour ne pas la mettre deux fois).

    EXEMPLES (ce que les tests vérifient) :
        kasiski_distances("ABCXABCXXXABC", "ABC")  ->  [4, 6]
            (positions 0, 4 et 10 : distances 4 - 0 = 4, puis 10 - 4 = 6)
        kasiski_distances("ABABAB", "AB")          ->  [2]
        kasiski_distances("ABCDE", "ZZ")           ->  []   (aucune répétition)
    """
    # --- À COMPLÉTER ---
    positions = []                                      # les positions de départ
    for debut in range(len(chiffre) - len(mot) + 1):    # chaque position possible
        if chiffre[debut:debut + ...] == ...:           # est-ce notre mot ?
            positions.append(...)                       # on note la position

    distances = []                                      # les écarts entre répétitions
    for rang in range(len(positions) - 1):              # positions voisines
        distance = positions[rang + 1] - ...            # l'écart
        if distance not in ...:                         # pas déjà dans la liste ?
            distances.append(distance)
    return sorted(...)                                  # distances triées

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     positions = []
    #     for debut in range(len(chiffre) - len(mot) + 1):
    #         if chiffre[debut:debut + len(mot)] == mot:
    #             positions.append(debut)
    #
    #     distances = []
    #     for rang in range(len(positions) - 1):
    #         distance = positions[rang + 1] - positions[rang]
    #         if distance not in distances:
    #             distances.append(distance)
    #     return sorted(distances)
    # ----------------------------------------------------------------------


def diviseurs(nombre):
    """B.3 — OBJECTIF : donner la liste des diviseurs de `nombre`, dans l'ordre.

    POURQUOI (COURS) : une distance entre deux répétitions est un multiple de la
    période, donc la période est un DIVISEUR de cette distance.  Pour chaque
    distance trouvée, on liste donc ses diviseurs : ce sont les périodes
    possibles.

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare une liste vide ;
        étape 2 : parcours les entiers de 1 à `nombre` :
                      for candidat in range(1, nombre + 1):
        étape 3 : si `nombre % candidat == 0` (le reste est nul), c'est un
                  diviseur : ajoute-le à la liste ;
        étape 4 : renvoie la liste.

    RAPPELS PYTHON :
        * `%` donne le reste : `12 % 4` vaut 0 (donc 4 divise 12), `12 % 5` vaut
          2 (donc 5 ne divise pas 12) ;
        * une boucle de 1 à nombre + 1 : n'oublie pas le + 1, sinon tu omets le
          nombre lui-même.

    EXEMPLES (ce que les tests vérifient) :
        diviseurs(12)  ->  [1, 2, 3, 4, 6, 12]
        diviseurs(7)   ->  [1, 7]
        diviseurs(1)   ->  [1]
    """
    # --- À COMPLÉTER ---
    liste = ...                                         # une liste vide
    for candidat in range(1, ...):                      # de 1 à nombre inclus
        if nombre % candidat == ...:
            liste.append(...)                           # c'est un diviseur
    return ...                                          # renvoie la liste

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     liste = []
    #     for candidat in range(1, nombre + 1):
    #         if nombre % candidat == 0:
    #             liste.append(candidat)
    #     return liste
    # ----------------------------------------------------------------------


# ==========================================================================
# PARTIE C — CASSER LES DEUX MESSAGES INTERCEPTÉS
# ==========================================================================

def forcer_cesar_sur_colonne(colonne):
    """C.1 — OBJECTIF : retrouver le décalage d'UNE colonne (comme au TP 2 C.1).

    POURQUOI (COURS) : une fois la période trouvée, chaque colonne est un simple
    code de César, que l'on casse par comparaison de fréquences.

    CE QUE TU DOIS FAIRE (c'est la recette du TP 2, refais-la de mémoire) :
        étape 1 : prépare `meilleur_decalage = 0` et `meilleure_distance = None` ;
        étape 2 : essaie les 26 décalages : `for decalage in range(26):`
        étape 3 : construis la version déchiffrée de la colonne :
                      essai = ""
                      for lettre in colonne:
                          essai += ALPHABET[(ALPHABET.index(lettre) - decalage) % 26]
                  (c'est le déchiffrement de César : on recule de `decalage`)
        étape 4 : mesure l'écart au français : `distance_au_francais(essai)` ;
        étape 5 : garde le décalage qui donne la plus PETITE distance ;
        étape 6 : renvoie ce décalage (entre 0 et 25).

    RAPPELS PYTHON :
        * `(ALPHABET.index(lettre) - decalage) % 26` : le modulo ramène toujours
          entre 0 et 25, même quand le résultat serait négatif ;
        * on cherche la plus petite distance, comme au TP 1 C.3.

    EXEMPLE (ce que les tests vérifient) : si la colonne a été chiffrée avec la
    lettre de clef S (décalage 18), la fonction renvoie 18.
    """
    # --- À COMPLÉTER ---
    meilleur_decalage = 0
    meilleure_distance = ...
    for decalage in range(...):                         # les 26 décalages
        essai = ...                                     # une chaîne vide
        for lettre in colonne:                          # chaque lettre de la colonne
            essai += ALPHABET[(ALPHABET.index(lettre) - ...) % 26]
        distance = distance_au_francais(...)            # l'écart au français
        if meilleure_distance is None or distance < ...:
            meilleur_decalage = ...
            meilleure_distance = ...
    return ...                                          # le décalage trouvé

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     meilleur_decalage = 0
    #     meilleure_distance = None
    #     for decalage in range(26):
    #         essai = ""
    #         for lettre in colonne:
    #             essai += ALPHABET[(ALPHABET.index(lettre) - decalage) % 26]
    #         distance = distance_au_francais(essai)
    #         if meilleure_distance is None or distance < meilleure_distance:
    #             meilleur_decalage = decalage
    #             meilleure_distance = distance
    #     return meilleur_decalage
    # ----------------------------------------------------------------------


def forcer_vigenere(chiffre, periode):
    """C.2 — OBJECTIF : casser le message complet, la période étant cette fois
    trouvée par toi (partie A).

    POURQUOI (COURS) : c'est l'aboutissement du chapitre 2 : la recherche de la
    période (Kasiski, Friedman) puis la cassure colonne par colonne.

    CE QUE TU DOIS FAIRE :
        étape 1 : découpe le texte en colonnes (fonction fournie) :
                      morceaux = colonnes(chiffre, periode)
        étape 2 : pour chaque colonne, trouve son décalage (C.1) et note la
                  lettre de clef : décalage 0 -> A, 1 -> B... :
                      decalages = []
                      cle = ""
                      for morceau in morceaux:
                          decalage = forcer_cesar_sur_colonne(morceau)
                          decalages.append(decalage)
                          cle += ALPHABET[decalage]
        étape 3 : déchiffre chaque colonne avec son décalage et garde le résultat :
                      morceaux_clairs = []
                      for rang in range(periode):
                          colonne_claire = ""
                          for lettre in morceaux[rang]:
                              colonne_claire += ALPHABET[(ALPHABET.index(lettre)
                                                          - decalages[rang]) % 26]
                          morceaux_clairs.append(colonne_claire)
        étape 4 : recolle les colonnes dans l'ordre.  La position `i` du texte
                  vient de la colonne `i % periode`, et c'est le
                  `i // periode`-ième caractère de cette colonne :
                      total = 0
                      for morceau in morceaux_clairs:
                          total += len(morceau)
                      clair = ""
                      for position in range(total):
                          clair += morceaux_clairs[position % periode][position // periode]
        étape 5 : renvoie `(cle, clair)`.

    RAPPELS PYTHON :
        * `decalages[rang]` : le décalage de la colonne numéro `rang` ;
        * `morceaux_clairs[position % periode][position // periode]` : deux
          crochets : on prend une chaîne dans la liste, puis un caractère dans
          cette chaîne ;
        * `return (cle, clair)` renvoie deux valeurs.

    EXEMPLE D'UTILISATION (avec les messages interceptés de la partie E) :
        periode = periode_probable(MESSAGE_1)      # ta fonction A.3
        cle, clair = forcer_vigenere(MESSAGE_1, periode)
        print(periode, cle, clair[:80])
    """
    # --- À COMPLÉTER ---
    morceaux = colonnes(..., periode)                   # étape 1

    decalages = []                                      # un décalage par colonne
    cle = ""                                            # la clef reconstruite
    for morceau in morceaux:                            # étape 2
        decalage = forcer_cesar_sur_colonne(...)        # le décalage de cette colonne
        decalages.append(...)                           # on le garde
        cle += ALPHABET[...]                            # sa lettre de clef

    morceaux_clairs = []                                # les colonnes déchiffrées
    for rang in range(periode):                         # étape 3
        colonne_claire = ""                             # une chaîne vide
        for lettre in morceaux[rang]:                   # chaque lettre de la colonne
            colonne_claire += ALPHABET[(ALPHABET.index(lettre) - ...) % 26]
        morceaux_clairs.append(...)                     # on garde la colonne claire

    total = 0                                           # étape 4 : recoller
    for morceau in morceaux_clairs:
        total += ...                                    # la longueur totale
    clair = ...                                         # une chaîne vide
    for position in range(total):
        clair += morceaux_clairs[position % ...][position // ...]
    return (... , ...)                                  # la clef ET le texte clair

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     morceaux = colonnes(chiffre, periode)
    #
    #     decalages = []
    #     cle = ""
    #     for morceau in morceaux:
    #         decalage = forcer_cesar_sur_colonne(morceau)
    #         decalages.append(decalage)
    #         cle += ALPHABET[decalage]
    #
    #     morceaux_clairs = []
    #     for rang in range(periode):
    #         colonne_claire = ""
    #         for lettre in morceaux[rang]:
    #             colonne_claire += ALPHABET[(ALPHABET.index(lettre) - decalages[rang]) % 26]
    #         morceaux_clairs.append(colonne_claire)
    #
    #     total = 0
    #     for morceau in morceaux_clairs:
    #         total += len(morceau)
    #     clair = ""
    #     for position in range(total):
    #         clair += morceaux_clairs[position % periode][position // periode]
    #     return (cle, clair)
    # ----------------------------------------------------------------------


# ==========================================================================
# PARTIE D — LE CODE DE VIC (version simplifiée du cours)
# ==========================================================================
#
# RAPPEL DE NOTRE VERSION SIMPLIFIÉE (tout est détaillé dans
# `outils/reference.py`, section 5 — va lire son code commenté) :
#
#   * le message est écrit avec les 10 lettres du damier :
#         S = 0, E = 1, N = 2, A = 3, T = 4, R = 5, O = 6, I = 7, D = 8, L = 9
#     (la chaîne ALPHABET_VIC = "SENATROIDL") ;
#   * on additionne la clef (une suite de chiffres), chiffre à chiffre, sans
#     retenue (modulo 10) ;
#   * on transpose les colonnes, bloc de 10 par bloc de 10 ;
#   * enfin, chaque chiffre devient une lettre grâce au damier TABLEAU_VIC :
#     on croise le CHIFFRE (la ligne) avec la POSITION du caractère dans son
#     bloc de 10 (la colonne).
#
# POUR DÉCHIFFRER, ON FAIT TOUT À L'ENVERS.  C'est ce que tu écris ici.
#
# Le damier, pour mémoire (chaque ligne contient les 10 lettres) :
#      >>> from outils.reference import afficher_tableau_vic
#      >>> print(afficher_tableau_vic())

def caractere_vic(chiffre_message, chiffre_clef, position):
    """D.1 — OBJECTIF : chiffrer UN caractère : donner la lettre du damier.

    CE QUE TU DOIS FAIRE :
        étape 1 : calcule la LIGNE du damier :
                      ligne = (chiffre_message + chiffre_clef) % 10
                  (c'est l'« addition de clef » du cours, sans retenue) ;
        étape 2 : la COLONNE est simplement la position dans le bloc :
                      colonne = position % 10
        étape 3 : renvoie la lettre de la case [ligne][colonne], avec la
                  fonction fournie `lettre_vic(ligne, colonne)`.

    RAPPELS PYTHON :
        * `% 10` garde le résultat entre 0 et 9 (comme le % 26 pour les lettres) ;
        * `lettre_vic(ligne, colonne)` lit le damier pour toi.

    EXEMPLES (ce que les tests vérifient) :
        caractere_vic(0, 0, 0)  ->  "S"    (ligne 0, colonne 0)
        caractere_vic(4, 3, 7)  ->  TABLEAU_VIC[7][7]  (vérifie la formule)
    """
    # --- À COMPLÉTER ---
    ligne = (chiffre_message + ...) % ...               # l'addition de clef
    colonne = position % ...                            # la position dans le bloc
    return lettre_vic(... , ...)                        # la lettre du damier

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     ligne = (chiffre_message + chiffre_clef) % 10
    #     colonne = position % 10
    #     return lettre_vic(ligne, colonne)
    # ----------------------------------------------------------------------


def ligne_du_damier(lettre, position):
    """D.2 — OBJECTIF : retrouver la LIGNE du damier à partir de la lettre lue
    dans le message chiffré et de la position (colonne).

    POURQUOI C'EST POSSIBLE : sur une même colonne du damier, les 10 lettres
    sont toutes différentes (le tableau est un « carré latin »).  En regardant
    la colonne indiquée, il n'y a donc qu'une seule ligne possible.

    CE QUE TU DOIS FAIRE :
        utilise la fonction fournie `deviner_ligne_vic(lettre, colonne)`, qui
        fait exactement ce travail (elle essaie les 10 lignes l'une après
        l'autre et renvoie celle qui contient la lettre dans cette colonne).
        Attention à la colonne : c'est `position % 10`.

    RAPPELS PYTHON :
        * `position % 10` : la position dans le bloc (0 à 9) ;
        * `deviner_ligne_vic` renvoie un nombre (la ligne).

    EXEMPLE (ce que les tests vérifient) : pour la lettre au bon endroit,
        ligne_du_damier("S", 0)  ->  0
    """
    # --- À COMPLÉTER ---
    return deviner_ligne_vic(lettre, ...)               # la colonne est position % 10

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     return deviner_ligne_vic(lettre, position % 10)
    # ----------------------------------------------------------------------


def chiffre_du_damier(lettre, chiffre_clef, position):
    """D.3 — OBJECTIF : retrouver le chiffre du message (opération inverse de D.1).

    CE QUE TU DOIS FAIRE :
        étape 1 : retrouve la ligne du damier avec ta fonction D.2 ;
        étape 2 : à l'aller, on avait `ligne = (message + clef) % 10`.
                  Donc le message est :
                      (ligne - chiffre_clef) % 10
                  (le modulo ramène la soustraction dans les 0 à 9) ;
        étape 3 : renvoie ce nombre.

    RAPPELS PYTHON :
        * `(ligne - chiffre_clef) % 10` reste toujours entre 0 et 9, même si la
          soustraction donne un nombre négatif.

    EXEMPLE : si D.1 a transformé le chiffre 3 en lettre avec le chiffre de clef
    1 et la position 4, alors chiffre_du_damier(lettre_obtenue, 1, 4) doit
    renvoyer 3.
    """
    # --- À COMPLÉTER ---
    ligne = ligne_du_damier(... , position)             # ta fonction D.2
    return (ligne - ...) % ...                          # on retire la clef

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     ligne = ligne_du_damier(lettre, position)
    #     return (ligne - chiffre_clef) % 10
    # ----------------------------------------------------------------------


def dechiffrer_message_vic(message_chiffre, cle, permutation=PERMUTATION_VIC):
    """D.4 — OBJECTIF : déchiffrer un message complet du VIC simplifié.

    POURQUOI (COURS) : c'est l'exercice final du chapitre 2.  Le chiffrement
    s'est fait en quatre étapes ; on les refait donc À L'ENVERS, dans l'ordre
    (4), (3), (2), (1) :

        (4) transformer les lettres en chiffres avec le damier  ->  ta fonction D.3
        (3) défaire la transposition des colonnes
        (2) retirer la clef (soustraction modulo 10)
        (1) reconvertir les chiffres en lettres du damier

    CE QUE TU DOIS FAIRE :
        étape 4 : pour chaque caractère, retrouve son chiffre :
                      chiffres = ""
                      for position, caractere in enumerate(message_chiffre.upper()):
                          chiffre_clef = int(cle[position % len(cle)])
                          chiffres += str(chiffre_du_damier(caractere, chiffre_clef, position))
                  Attention : `int(cle[...])` transforme le caractère chiffre de la
                  clef (par exemple "5") en nombre (5), et `str(...)` fait
                  l'inverse pour pouvoir ajouter à la chaîne.
        étape 3 : défais la transposition :
                      chiffres = transposition(chiffres, permutation_inverse(list(permutation)))
                  (`permutation_inverse` construit la permutation qui défait ;
                   `list(permutation)` en fait une copie modifiable)
        étape 2 : retire la clef : `chiffres = retirer_cle(chiffres, cle)`
        étape 1 : reconvertis en lettres : `chiffres_en_message(chiffres)`
        renvoie le résultat.

    RAPPELS PYTHON :
        * `enumerate(message)` donne position et caractère ;
        * `int("5")` vaut 5 ; `str(5)` vaut "5" ;
        * les trois fonctions `transposition`, `permutation_inverse` et
          `retirer_cle` sont fournies : regarde leur code commenté.

    EXEMPLE (ce que les tests vérifient, notamment avec le vrai message) :
        dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC)  ->  un vrai message français
    """
    # --- À COMPLÉTER (dans cet ordre : 4, 3, 2, 1) ---
    chiffres = ""                                       # étape 4
    for position, caractere in enumerate(message_chiffre.upper()):
        chiffre_clef = int(cle[position % len(...)])    # le chiffre de la clef
        chiffres += str(chiffre_du_damier(caractere, ... , position))
    chiffres = transposition(chiffres, ...)             # étape 3 : détransposer
    chiffres = ...                                      # étape 2 : retirer la clef
    return ...                                          # étape 1 : reconvertir en lettres

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     chiffres = ""
    #     for position, caractere in enumerate(message_chiffre.upper()):
    #         chiffre_clef = int(cle[position % len(cle)])
    #         chiffres += str(chiffre_du_damier(caractere, chiffre_clef, position))
    #     chiffres = transposition(chiffres, permutation_inverse(list(permutation)))
    #     chiffres = retirer_cle(chiffres, cle)
    #     return chiffres_en_message(chiffres)
    # ----------------------------------------------------------------------


# ==========================================================================
# PARTIE E — MESSAGES INTERCEPTÉS
# ==========================================================================
#
# MESSAGE_1 et MESSAGE_2 sont deux dépêches chiffrées par Vigenère.  Ici, la
# PÉRIODE EST INCONNUE : c'est ton travail des parties A, B et C.
#
# MESSAGE_VIC a été chiffré par le VIC simplifié, et l'on connaît sa clef
# (CLE_VIC) : il te faut seulement ta fonction D.4.
#
# Dans l'interpréteur Python :
#     >>> from tp3_vigenere_vic import *
#     >>> indices = indices_par_periode(MESSAGE_1, 15)
#     >>> for periode in sorted(indices):        # le tableau des indices
#     ...     print(periode, round(indices[periode], 4))
#     >>> periode = periode_probable(MESSAGE_1)
#     >>> cle, clair = forcer_vigenere(MESSAGE_1, periode)
#     >>> print(periode, cle)
#     >>> print(clair[:200])
#     >>> print(dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC))

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
MESSAGE_1 = (
    "NZVXSFIQGMEYGLYVWTXYCWIVWLMZPPJTWWISQXFWGFWJCEXJPOENVDYWNLVNXP"
    "TTWCZTKCTFUDIWNPWRCCGMCYHNUPWJVWIXXZCFIPYWUGISWDHJNZMSNPGTOXES"
    "FLRYULPZCWERCTWTPMPFPNLJFPWIQFESGDTZKDMQFZRSCWSWFCIIGAEWVTVQGQ"
    "PJWGIJVLMYNLVLGPXHCWQJEPQFVTRQCWIXGYJFPEWHQFVFKPRYNPPTPRHJNLFJ"
    "TRIJPLKNVLRYNPWRCTRXRPVXQYRJPPWFXLMYGYGTTPUZGWEHTFIFTCMAGCENVA"
    "PZUESYSFIUTPZZEPXYGLRSGPWZTWEWKGITRASXGPPJUAIHJPYWUCIUCCENGYXQ"
    "GFVXHTPJVDISRLVQCYXIWAVNZOYUQTWXQYEZOLVHJPHZNFRIKWIAKPYCRLXWQY"
    "VFEZRYCTXVWPHFPDWFLPYSGDWJKWEACTXIGDGJPOYQGQPJWGIOWDUZCWERGCEA"
    "GNYSGNLFTRIIGMSNUPXIGDIQKWWJUZYAGYENVOIXPFMYUDESUPXTKWIXQFPJEZ"
    "YWCYXUQFWXCTXQCMEWSFIAGCWQGDFFPNWIGDEGNPPJRTPTVPGTPYENUDENVNLF"
)

MESSAGE_2 = (
    "XCUHYIVUCJTVIMHCVXYOJAGKIEIWQKSBRVTMPDXFRXQYMWICEBMKMIZPMNHHVK"
    "EURDXWCIFRJXWUIXYXTQZPXCDXWASGPFTYOHQJSVEGMFYDXIKTMPXHMJYZKSGH"
    "RXMRLXRUYPCHNMJHQQEHMJPQDSVXVYDBMJYRVFGWKGFRZYALWRMFRGNXCIYMFW"
    "IVXXGKTMKPQQSWVVWECKTZFMJFSNXVHQTSGXCEBMJMICIECFYEEXEQWKEJWQKT"
    "EEZIZRSNXFYDBWEYZTASJXRKIZBJXPVWZMMOICPQQVNTRCEJWFEZXDCVXGFPQM"
    "MOVRMFJWLNFYDLSNBVXOMEFIEXMGLEIJHQAALMFREBMZSLZQPFXQVRFGDIEIPM"
    "GLWIJVASLXWUIENGGXJHQQAFTFXECLWIJIOMDXWESGTWEPVWXCKTRTMQLKXGFY"
    "FYAXRKIZQAEIEGQCLVSDTMPSBIEXMTWVPVXQKHLTRWECDXQRVOFWWYJEYCVBVV"
    "WFYAMPVKDYFWIMIZCEXRKHQJSLIDEULWHRPZQLSBXUIFPWLPFMZNGNVMIZBJXH"
    "VWMLAFELBPCKIEEMQPKWIJXUQKNWVXPCKHYKMXQDXWGVUVKXHZWOSLTMVRFYNH"
    "MOFMQKXWFYEJWLEIFDCKEEGPGGWTZRMFCLXVRVQAWMXVEZLWXIKPQQUAEDTEQG"
    "NJWVMGWGXTLMAMGQVW"
)

MESSAGE_VIC = (
    "ELAANODTRDIESTIITEOESEANIOODRTRESNSDDSARLNAANSETTRIENINISRNIIO"
    "ILLEEDNNENROOOELAS"
)

CLE_VIC = "5241730219"
# --- FIN DE LA ZONE GÉNÉRÉE ---


# ###########################################################################
#
#  EXPÉRIENCES À FAIRE DANS L'INTERPRÉTEUR (méthode scientifique)
#
# ###########################################################################
#
# EXPÉRIENCE 1 — le damier est bien un carré latin
#     >>> from outils.reference import afficher_tableau_vic, TABLEAU_VIC, ALPHABET_VIC
#     >>> print(afficher_tableau_vic())
#     >>> for ligne in range(10):
#     ...     assert sorted(TABLEAU_VIC[ligne]) == sorted(ALPHABET_VIC)
#     Chaque ligne contient les 10 lettres une fois.  Vérifie la même chose
#     pour une colonne : c'est cette propriété qui rend le déchiffrement possible.
#
# EXPÉRIENCE 2 — le tableau des indices, et l'effet des multiples
#     >>> indices = indices_par_periode(MESSAGE_1, 15)
#     >>> for periode in sorted(indices):
#     ...     print(periode, round(indices[periode], 4), "#" * int(200 * indices[periode]))
#     Repère les pics : la vraie période et ses multiples sortent du lot.  C'est
#     pour cela que periode_probable prend la PLUS PETITE qui atteint 90 % du
#     meilleur indice.
#
# EXPÉRIENCE 3 — croiser Kasiski et Friedman (la méthode du cryptanalyste)
#     >>> support = {}
#     >>> for groupe in grammes_repetes(MESSAGE_1, 4):
#     ...     for distance in kasiski_distances(MESSAGE_1, groupe):
#     ...         for periode in diviseurs(distance):
#     ...             if 2 <= periode <= 15:
#     ...                 support[periode] = support.get(periode, 0) + 1
#     >>> for periode in sorted(support, key=lambda p: -support[p])[:6]:
#     ...     print(periode, support[periode])
#     Compare cette liste avec celle des indices : les petits diviseurs (2, 3, 4)
#     apparaissent souvent par hasard.  Les deux méthodes se complètent.
#
# EXPÉRIENCE 4 — VIC : et si l'on se trompait de permutation ?
#     >>> dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
#     Compare avec le résultat correct : cela montre le rôle de la transposition.
#
# ###########################################################################
#
#  QUESTIONS DE RAPPORT (à rédiger et à rendre avec le fichier)
#
# ###########################################################################
#
# QUESTION 1. Démontre la propriété de Kasiski : si le même groupe de lettres
# apparaît deux fois dans le texte CLAIR, pourquoi la distance entre les deux
# occurrences est-elle un multiple de la période dans le texte CHIFFRÉ ?
#
# QUESTION 2. Pourquoi les multiples de la vraie période donnent-ils aussi un
# indice de coïncidence élevé ?  Comment ta fonction periode_probable (A.3)
# résout-elle ce problème ?
#
# QUESTION 3. Compare Kasiski et l'indice de coïncidence : lequel donne le plus
# de faux candidats (voir l'expérience 3) ?  Lequel est le plus fiable sur un
# message de 200 lettres ?  Que gagne-t-on à utiliser les deux ?
#
# QUESTION 4. VIC : explique le rôle des quatre étapes du cours.  Que se
# passerait-il si l'on supprimait l'étape de transposition ?  Et l'addition de
# clef ?  (Tu peux le tester : essaie de déchiffrer MESSAGE_VIC en sautant une
# étape dans ta fonction D.4 et regarde le résultat.)
#
# QUESTION 5. Le damier du VIC est public.  En quoi cela illustre-t-il le
# principe de Kerckhoffs ?
#
# QUESTION 6. Le VIC a été cassé parce que la même clef de message servait deux
# fois, ce qui produisait des répétitions exploitables.  Rapproche cela de la
# méthode de Kasiski : quelle leçon générale en tire-t-on pour les systèmes de
# chiffrement (voir aussi la question 4 du TP 2) ?
#


if __name__ == "__main__":
    # Cette partie s'exécute quand on lance :   python3 tp3_vigenere_vic.py

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

    print("Voici où tu en es dans tes douze fonctions :")
    _essai("A.1 indice_coincidence_moyen('ABAB', 2)",
           lambda: indice_coincidence_moyen("ABAB", 2))
    _essai("A.2 indices_par_periode(MESSAGE_1, 6)",
           lambda: indices_par_periode(MESSAGE_1, 6))
    _essai("A.3 periode_probable(MESSAGE_1)",
           lambda: periode_probable(MESSAGE_1))
    _essai("B.1 grammes_repetes('ABCIABCXABC', 3)",
           lambda: grammes_repetes("ABCIABCXABC", 3))
    _essai("B.2 kasiski_distances('ABCXABCXXXABC', 'ABC')",
           lambda: kasiski_distances("ABCXABCXXXABC", "ABC"))
    _essai("B.3 diviseurs(12)", lambda: diviseurs(12))
    _essai("C.1 forcer_cesar_sur_colonne (doit donner le décalage 3)",
           lambda: forcer_cesar_sur_colonne(
               "".join(ALPHABET[(ALPHABET.index(c) + 3) % 26]
                       for c in nettoyer("LE MESSAGE ARRIVE CE SOIR A DIX HEURES DEVANT LA PORTE DU JARDIN"))))
    _essai("C.2 forcer_vigenere(MESSAGE_1, periode_probable(MESSAGE_1))",
           lambda: forcer_vigenere(MESSAGE_1, periode_probable(MESSAGE_1)))
    _essai("D.1 caractere_vic(0, 0, 0)", lambda: caractere_vic(0, 0, 0))
    _essai("D.2 ligne_du_damier('S', 0)", lambda: ligne_du_damier("S", 0))
    _essai("D.3 chiffre_du_damier (doit redonner le chiffre de départ)",
           lambda: chiffre_du_damier(caractere_vic(3, 1, 4), 1, 4))
    _essai("D.4 dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC)",
           lambda: dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC))

    print()
    print("Le damier du VIC (utile pour comprendre D.1 à D.4) :")
    from outils.reference import afficher_tableau_vic
    print(afficher_tableau_vic())
    print()
    print("Quand tout est écrit, lance les épreuves :")
    print("    python3 test_tp3_vigenere_vic.py")
