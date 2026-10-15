"""==========================================================================
 TP 3 — CRYPTANALYSE DE VIGENÈRE (KASISKI, FRIEDMAN) ET CODE DE VIC
 Chapitre 2 (fin) : « Cryptanalyse » et « Code de VIC » — Pascal Boyer,
 « Cryptographie 2013 ».

 Durée conseillée : 2 h à 2 h 30.   À rendre : ce fichier complété.
==========================================================================

 ██  MODE D'EMPLOI  ██
==========================================================================

Au TP 2, tu cassais un message de Vigenère À CONDITION de connaître la longueur
de la clef.  Ici, tu ne connais RIEN : tu as seulement le texte intercepté.
C'est LA situation du cryptanalyste.

LE PLAN DE CE FICHIER
---------------------
   1. Rappels du cours ............................................... § A
   2. Les outils d'analyse à écrire (indice de coïncidence) .......... § B
   3. ★ CRYPTANALYSE DE VIGENÈRE : trouver la période, puis la clef ★ . § C
   4. Le code de VIC (fin du chapitre 2) ............................. § D
   5. Des expériences à faire dans l'interpréteur ..................... § E
   6. Des questions de rapport ....................................... § F

L'ATTAQUE COMPLÈTE, EN DEUX TEMPS
---------------------------------
   1. TROUVER LA PÉRIODE (le nombre de lettres de la clef), sans aucune
      indication.  Deux méthodes, que tu vas écrire toutes les deux :
        * la méthode de KASISKI (1863) : on repère les groupes de lettres qui
          se répètent, on mesure les distances entre répétitions, et l'on
          remarque que ces distances sont des multiples de la période ;
        * l'INDICE DE COÏNCIDENCE (Friedman, années 1920) : on découpe le texte
          en p colonnes pour chaque valeur de p, et l'on regarde si les colonnes
          ressemblent à du français.  Elles y ressemblent quand p est la période.
      ★ Aucune des deux ne suffit seule : c'est en les CROISANT que l'on est sûr.
   2. CASSER CHAQUE COLONNE, une fois la période connue (comme au TP 2).

LES OUTILS FOURNIS (pour te concentrer sur la cryptanalyse)
----------------------------------------------------------
    colonnes(texte, p)        recoller(...)        decalage_probable(colonne)
    indice_de_coincidence(t)  indices_par_periode(texte, maximum)
    grammes_repetes(t, n)     diviseurs(n)         vider_les_espaces(t)
    et, pour le VIC : TABLEAU_VIC, lettre_vic, deviner_ligne_vic, transposition,
    permutation_inverse, retirer_cle, chiffres_en_message...

LES SEPT FONCTIONS À ÉCRIRE
---------------------------
  § B — analyse                        § C — ★ CRYPTANALYSE ★ (le cœur)
   B.1  indice_coincidence_moyen        C.1  kasiski_distances
   B.2  periode_probable                C.2  support_kasiski
                                        C.3  forcer_vigenere
  § D — code de VIC
   D.1  chiffre_du_damier               D.2  dechiffrer_message_vic

  Et, en jeu, les SIX messages interceptés de la séance (voir la fin du § D).
==========================================================================
"""

# ---------------------------------------------------------------------------
# LES IMPORTS (n'y touche pas)
# ---------------------------------------------------------------------------
# Ces trois lignes permettent à Python de trouver le dossier « outils ».
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Les outils fournis.  Tu en reconnais plusieurs (TP 1 et TP 2) :
#   * ALPHABET, colonnes, recoller, decalage_probable, vider_les_espaces,
#     grammes_repetes, diviseurs, indice_de_la_lettre ;
#   * pour le VIC : ALPHABET_VIC, TABLEAU_VIC, PERMUTATION_VIC, lettre_vic,
#     deviner_ligne_vic, transposition, permutation_inverse, retirer_cle,
#     chiffres_en_message, ajouter_cle.
from outils.reference import (
    ALPHABET,
    ALPHABET_VIC,
    PERMUTATION_VIC,
    TABLEAU_VIC,
    chiffres_en_message,
    colonnes,
    deviner_ligne_vic,
    diviseurs,
    grammes_repetes,
    lettre_vic,
    permutation_inverse,
    recoller,
    retirer_cle,
    transposition,
    vider_les_espaces,
)
from outils.texte_francais import (
    decalage_probable,
    indice_de_coincidence,
    indices_par_periode,
)


# ###########################################################################
#
#  § A — RAPPELS DU COURS (à lire avant de commencer)
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
#    ATTENTION : cette méthode ne donne pas une réponse unique.  Un diviseur
#    comme 2 ou 3 « explique » énormément de distances par hasard ; la vraie
#    période est souvent noyée parmi quelques candidates.  D'où l'étape 3.
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


# ###########################################################################
#
#  § B — LES OUTILS D'ANALYSE À ÉCRIRE
#
# ###########################################################################

def indice_coincidence_moyen(texte, periode):
    """B.1 — OBJECTIF : calculer la MOYENNE des indices de coïncidence des
    `periode` colonnes du texte.

    POURQUOI (COURS) : c'est le test de Friedman.  Si `periode` est la bonne
    longueur de clef, chaque colonne est un texte français décalé, donc
    l'indice de chaque colonne vaut environ 0,075, et la moyenne aussi.  Si la
    période est fausse, chaque colonne mélange plusieurs décalages différents :
    les lettres deviennent presque équiprobables et la moyenne retombe vers
    0,038.

    CE QUE TU DOIS FAIRE :
        étape 1 : range le texte en colonnes (outil fourni) :
                      morceaux = colonnes(texte, periode)
        étape 2 : prépare un total à 0.0 ;
        étape 3 : parcours les morceaux et ajoute leur indice de coïncidence
                  (outil fourni `indice_de_coincidence`) :
                      for morceau in morceaux:
                          total += indice_de_coincidence(morceau)
        étape 4 : renvoie la moyenne : total / len(morceaux).

    RAPPELS PYTHON :
        * `if not texte:` teste si le texte est vide ; dans ce cas, renvoie 0.0
          pour éviter une division par zéro ;
        * une moyenne se calcule en additionnant, puis en divisant par le
          nombre d'éléments.

    EXEMPLES (ce que les tests vérifient) :
        indice_coincidence_moyen("ABAB", 2)  ->  1.0
            (les colonnes sont "AA" et "BB" : dans chacune, deux lettres tirées
             au hasard sont toujours égales, donc l'indice vaut 1)
        Sur un vrai message chiffré : l'indice de la vraie période dépasse
        0,07 ; celui d'une période fausse reste sous 0,06.
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


def periode_probable(texte, maximum=15, proportion=0.9):
    """B.2 — OBJECTIF : renvoyer la période la plus probable du texte chiffré.

    LA RÈGLE (et pourquoi celle-là) :
        1. calcule tous les indices, pour les périodes de 1 à `maximum`
           (outil fourni : `indices_par_periode`) ;
        2. appelle `meilleur` le plus grand de ces indices ;
        3. renvoie la PLUS PETITE période dont l'indice atteint au moins
           `proportion` fois le meilleur (0,9 par défaut, soit 90 %).

    POURQUOI 90 % DU MEILLEUR PLUTÔT QU'UN SEUIL FIXE ?  Parce que la valeur des
    indices dépend de la longueur du texte : un seuil fixe (0,06 par exemple)
    marche pour un texte de 600 lettres et échoue pour un texte de 120 lettres.
    Comparer les périodes entre elles est beaucoup plus solide.  (Un seuil fixe
    peut aussi se tromper d'une autre manière : pour une vraie période de 6,
    l'indice de la période 3 monte parfois à 0,067, au-dessus du seuil !)

    POURQUOI LA PLUS PETITE ?  Parce que si la vraie période est 5, les périodes
    10, 15, 20... donnent aussi des colonnes correctes (ce sont des multiples de
    5) : elles « marchent » aussi, mais ce n'est pas la vraie clef.

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
        * `>=` : « supérieur ou égal » ; `None` : la valeur « rien du tout ».

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


# ###########################################################################
#
#  § C — ★ CRYPTANALYSE DE VIGENÈRE ★ (période inconnue)
#
#  C'est le cœur du TP, et l'aboutissement du chapitre 2.  La démarche complète,
#  dans l'ordre où un vrai cryptanalyste travaille :
#
#     1. REPÉRER LES RÉPÉTITIONS (Kasiski) : quels groupes de lettres se
#        répètent, et à quelles distances ?
#     2. COMPTER LES VOIX : chaque distance fait « voter » ses diviseurs.  On
#        obtient une liste de périodes candidates, classées par nombre de voix.
#     3. DÉPARTAGER PAR L'INDICE DE COÏNCIDENCE (Friedman) : parmi ces
#        candidates, laquelle donne des colonnes qui ressemblent à du français ?
#     4. CASSER CHAQUE COLONNE, puis recoller.
#
#  La leçon de méthode, à retenir : AUCUN INDICE PRIS SEUL NE SUFFIT.  Kasiski
#  donne plusieurs candidates (parfois fausses), l'indice de coïncidence peut
#  être bruité sur un texte court ; croisés, ils sont fiables.
#
# ###########################################################################


def kasiski_distances(chiffre, mot):
    """C.1 — ★ CRYPTANALYSE ★ distances entre les répétitions successives d'un
    groupe de lettres.

    POURQUOI (COURS) : c'est le cœur de la méthode de Kasiski.  Si « ABC »
    apparaît aux positions 4 et 13, la distance est 13 - 4 = 9.  Un tel écart
    est un multiple de la période : c'est ce que l'on cherche.

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
        * `chiffre[debut:debut + len(mot)] == mot` : on compare deux extraits
          avec == (deux signes égaux !) ;
        * `positions[rang + 1] - positions[rang]` : l'écart entre deux positions
          consécutives ;
        * `if distance not in distances:` : évite de mettre deux fois la même
          distance.

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


def support_kasiski(chiffre, taille=4, maximum=15):
    """C.2 — ★ CRYPTANALYSE ★ combien de répétitions « votent » pour chaque
    période possible.

    POURQUOI (COURS) : une seule répétition ne prouve rien (elle peut être un
    hasard du texte).  Mais si l'on mesure les distances de TOUTES les
    répétitions d'un texte, la vraie période est un diviseur de la plupart
    d'entre elles : elle va donc recevoir beaucoup de voix.  C'est un vote.

    CE QUE TU DOIS FAIRE :
        étape 1 : prépare un dictionnaire vide `support = {}` ;
        étape 2 : parcours les groupes répétés (outil fourni :
                  `grammes_repetes(chiffre, taille)`) :
                      for groupe in grammes_repetes(chiffre, taille):
        étape 3 : pour chaque groupe, parcours ses distances (ta fonction C.1) :
                      for distance in kasiski_distances(chiffre, groupe):
        étape 4 : pour chaque distance, ajoute une voix à chacun de ses
                  diviseurs (outil fourni `diviseurs`) compris entre 2 et
                  `maximum` :
                      for periode in diviseurs(distance):
                          if 2 <= periode <= maximum:
                              support[periode] = support.get(periode, 0) + 1
        étape 5 : renvoie le dictionnaire `support`.

    RAPPELS PYTHON :
        * `support.get(periode, 0) + 1` : la façon habituelle de compter dans un
          dictionnaire sans provoquer d'erreur sur une clef inconnue ;
        * on ignore le diviseur 1 (il divise tout, il ne veut rien dire) ;
        * trois boucles imbriquées, c'est normal : groupes -> distances ->
          diviseurs.

    EXEMPLES (ce que les tests vérifient) :
        support_kasiski("ABCXABCXXXABC", taille=3, maximum=10)  ->  {2: 1, 3: 1, 4: 1, 6: 1}
            (les groupes de 3 lettres ne se répètent pas ici ; avec "ABC" répété,
             la distance 4 a pour diviseurs 2 et 4, la distance 6 a pour
             diviseurs 2, 3 et 6 : on recompte les voix.)
        Sur un vrai message, la vraie période doit être bien classée, mais elle
        n'est PAS forcément première : c'est pour cela qu'on croise avec B.2.
    """
    # --- À COMPLÉTER ---
    support = ...                                       # un dictionnaire vide
    for groupe in grammes_repetes(..., taille):         # chaque groupe répété
        for distance in kasiski_distances(..., groupe):  # ses distances
            for periode in diviseurs(distance):          # les diviseurs de la distance
                if 2 <= periode <= maximum:
                    support[periode] = support.get(periode, 0) + ...
    return ...                                          # renvoie le dictionnaire des voix

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     support = {}
    #     for groupe in grammes_repetes(chiffre, taille):
    #         for distance in kasiski_distances(chiffre, groupe):
    #             for periode in diviseurs(distance):
    #                 if 2 <= periode <= maximum:
    #                     support[periode] = support.get(periode, 0) + 1
    #     return support
    # ----------------------------------------------------------------------


def forcer_vigenere(chiffre, periode):
    """C.3 — ★ CRYPTANALYSE ★ casser le message complet, la période étant
    maintenant trouvée par toi (partie B).

    POURQUOI (COURS) : c'est l'aboutissement du chapitre 2 : la recherche de la
    période (Kasiski, Friedman), puis la cassure colonne par colonne.

    CE QUE TU DOIS FAIRE :
        étape 1 : découpe le texte en colonnes (outil fourni) :
                      morceaux = colonnes(chiffre, periode)
        étape 2 : pour chaque colonne, trouve son décalage (outil fourni
                  `decalage_probable`, c'est la fonction que tu as écrite au TP 2)
                  et note la lettre de clef : décalage 0 -> A, 1 -> B... :
                      decalages = []
                      cle = ""
                      for morceau in morceaux:
                          decalage = decalage_probable(morceau)
                          decalages.append(decalage)
                          cle += ALPHABET[decalage]
        étape 3 : déchiffre chaque colonne avec son décalage et garde le
                  résultat :
                      for rang in range(periode):
                          colonne_claire = ""
                          for lettre in morceaux[rang]:
                              colonne_claire += ALPHABET[(ALPHABET.index(lettre)
                                                          - decalages[rang]) % 26]
        étape 4 : recolle les colonnes dans l'ordre (outil fourni `recoller`) ;
        étape 5 : renvoie `(cle, clair)`.

    RAPPELS PYTHON :
        * `decalages[rang]` : le décalage de la colonne numéro `rang` ;
        * `recoller(morceaux_clairs, periode)` recolle les colonnes claires et
          redonne le texte, sans espaces ;
        * `return (cle, clair)` renvoie deux valeurs.

    EXEMPLE D'UTILISATION (avec les messages interceptés de la fin du § D) :
        periode = periode_probable(MESSAGE_3)      # ta fonction B.2
        cle, clair = forcer_vigenere(MESSAGE_3, periode)
        print(periode, cle)
        print(clair[:80])
    """
    # --- À COMPLÉTER ---
    morceaux = colonnes(... , periode)                  # étape 1

    decalages = []                                      # un décalage par colonne
    cle = ""                                            # la clef reconstruite
    for morceau in morceaux:                            # étape 2
        decalage = decalage_probable(...)               # le décalage de cette colonne
        decalages.append(...)                           # on le garde
        cle += ALPHABET[...]                            # sa lettre de clef

    morceaux_clairs = []                                # les colonnes déchiffrées
    for rang in range(periode):                         # étape 3
        colonne_claire = ""                             # une chaîne vide
        for lettre in morceaux[rang]:                   # chaque lettre de la colonne
            colonne_claire += ALPHABET[(ALPHABET.index(lettre) - ...) % 26]
        morceaux_clairs.append(...)                     # on garde la colonne claire

    return (... , recoller(morceaux_clairs, periode))   # étape 4 et 5

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     morceaux = colonnes(chiffre, periode)
    #
    #     decalages = []
    #     cle = ""
    #     for morceau in morceaux:
    #         decalage = decalage_probable(morceau)
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
    #     return (cle, recoller(morceaux_clairs, periode))
    # ----------------------------------------------------------------------


# ###########################################################################
#
#  § D — LE CODE DE VIC (version simplifiée du cours)
#
#  RAPPEL DE NOTRE VERSION SIMPLIFIÉE (tout est détaillé dans
#  `outils/reference.py`, section 5 — va lire son code commenté) :
#
#    * le message est écrit avec les 10 lettres du damier :
#          S = 0, E = 1, N = 2, A = 3, T = 4, R = 5, O = 6, I = 7, D = 8, L = 9
#      (la chaîne ALPHABET_VIC = "SENATROIDL") ;
#    * on additionne la clef (une suite de chiffres), chiffre à chiffre, sans
#      retenue (modulo 10) ;
#    * on transpose les colonnes, bloc de 10 par bloc de 10 ;
#    * enfin, chaque chiffre devient une lettre grâce au damier TABLEAU_VIC :
#      on croise le CHIFFRE (la ligne) avec la POSITION du caractère dans son
#      bloc de 10 (la colonne).
#
#  POUR DÉCHIFFRER, ON FAIT TOUT À L'ENVERS.  C'est ce que tu écris ici.
#
#  Le damier, pour mémoire :
#      >>> from outils.reference import afficher_tableau_vic
#      >>> print(afficher_tableau_vic())
#
# ###########################################################################

def chiffre_du_damier(lettre, chiffre_clef, position):
    """D.1 — OBJECTIF : retrouver le chiffre du message (le déchiffrement d'UN
    caractère).

    COMMENT C'EST POSSIBLE : sur une même colonne du damier, les 10 lettres sont
    toutes différentes (le tableau est un « carré latin »).  En regardant la
    colonne indiquée par la position, il n'y a donc qu'une seule ligne possible
    pour la lettre lue.

    CE QUE TU DOIS FAIRE :
        étape 1 : retrouve la ligne du damier avec l'outil fourni (il essaie les
                  10 lignes et renvoie celle qui contient la lettre) :
                      ligne = deviner_ligne_vic(lettre, position % 10)
        étape 2 : à l'aller, on avait `ligne = (message + clef) % 10`.
                  Donc le message est :
                      (ligne - chiffre_clef) % 10
                  (le modulo ramène la soustraction dans les 0 à 9, même si le
                  résultat est négatif) ;
        étape 3 : renvoie ce nombre (entre 0 et 9).

    RAPPELS PYTHON :
        * `position % 10` : la position dans le bloc de 10 caractères ;
        * un nombre négatif, dans `% 10`, donne toujours un résultat entre 0
          et 9 : (-1) % 10 vaut 9 (le Z du damier).

    EXEMPLE (ce que les tests vérifient) : si l'on chiffre le chiffre 3 avec le
    chiffre de clef 1 et la position 4, alors
    chiffre_du_damier(lettre obtenue, 1, 4) doit redonner 3.
    """
    # --- À COMPLÉTER ---
    ligne = deviner_ligne_vic(... , position % 10)      # l'outil fourni
    return (ligne - ...) % ...                          # on retire la clef

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     ligne = deviner_ligne_vic(lettre, position % 10)
    #     return (ligne - chiffre_clef) % 10
    # ----------------------------------------------------------------------


def dechiffrer_message_vic(message_chiffre, cle, permutation=PERMUTATION_VIC):
    """D.2 — OBJECTIF : déchiffrer un message complet du VIC simplifié.

    POURQUOI (COURS) : c'est l'exercice final du chapitre 2.  Le chiffrement
    s'est fait en quatre étapes ; on les refait donc À L'ENVERS, dans l'ordre
    (4), (3), (2), (1) :

        (4) transformer les lettres en chiffres avec le damier -> ta fonction D.1
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
                  l'inverse pour pouvoir ajouter à une chaîne de texte.
        étape 3 : défais la transposition :
                      chiffres = transposition(chiffres, permutation_inverse(list(permutation)))
                  (`permutation_inverse` construit la permutation qui défait ;
                   `list(permutation)` en fait une copie manipulable)
        étape 2 : retire la clef : `chiffres = retirer_cle(chiffres, cle)`
        étape 1 : reconvertis en lettres : `chiffres_en_message(chiffres)`
        renvoie le résultat.

    RAPPELS PYTHON :
        * `enumerate(message)` donne la position ET le caractère ;
        * `int("5")` vaut 5 ; `str(5)` vaut "5" ;
        * `transposition`, `permutation_inverse` et `retirer_cle` sont fournis :
          regarde leur code commenté dans `outils/reference.py`.

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


# ###########################################################################
#
#  § D (suite) — LES SIX MESSAGES INTERCEPTÉS
#
#  LES QUATRE DÉPÊCHES VIGENÈRE — la période est INCONNUE pour toutes :
#
#    MESSAGE_1   la plus ancienne, période 4      -> periode_probable + forcer_vigenere
#    MESSAGE_2   période 7                        -> idem
#    MESSAGE_3   dépêche inédite, jamais vue      -> idem
#    MESSAGE_4   dépêche courte : plus difficile  -> idem
#
#  La marche à suivre, dans l'interpréteur Python :
#
#      >>> from tp3_vigenere_vic import *
#      >>> indices = indices_par_periode(MESSAGE_3, 15)
#      >>> for periode in sorted(indices):        # le tableau des indices
#      ...     print(periode, round(indices[periode], 4))
#      >>> periode = periode_probable(MESSAGE_3)
#      >>> cle, clair = forcer_vigenere(MESSAGE_3, periode)
#      >>> print(periode, cle)
#      >>> print(clair[:200])
#
#  Et pour croiser avec la méthode de Kasiski (l'expérience 3 du § E) :
#
#      >>> support = support_kasiski(MESSAGE_3)
#      >>> for periode in sorted(support, key=lambda p: -support[p])[:6]:
#      ...     print(periode, support[periode])
#
#  LE MESSAGE VIC — la clef est connue (CLE_VIC), c'est le déchiffrement seul :
#
#      >>> print(dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC))
#
#  (Ces constantes sont remplies par le professeur : ne les modifie pas.)

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

MESSAGE_3 = (
    "RIUFVZLRVWNLGAMITILDSJTPMSFWKZLQQSMKSZWYNSHLMBPEVBYDWZZRHRYKII"
    "LMTSNDWDZVUQBSFUPHFJCKSUPPFGAJMSDMNAITAZPWESMKABPRURYKGAMVFGFG"
    "FUFITGOJDSDIOHLWHCEWFHFGFSYXFBXKWIWINSHLDSNPBDILAGOIMSUMUCYXSS"
    "FWKQZUVSMMFJTIJZBGEAPTBGMWSJPGVBWZASYWBFLWLSFRJBMLSBETPILJWULV"
    "ESLDWGQIVLXWKPLXFOOPSIWESUYHMWDGPBNAFIPWPBWZWATRTOHKJWPREWLWVO"
    "YWMSMTMFPEVLXMHCCXVBYDSAAICFODWSYGPFYMFSXTMCSWUZLWTSXWKDLTJSLK"
    "UCEIQOLUGHPGPAGWGBLPJUHWVSDPFHNJWGDYSIHWHORIJZHGLSOEOGOFUOSMFF"
    "FWKOCVJJYWKRFNPILDWGOIQOLLKRFPFBXWEOTRMSHGERPWCONWSIIIUZUFSHFV"
    "FRYKEOCGIOHVAGPWQZOKLOCHRIUFVHZYUGYJSGTPFBWA"
)

MESSAGE_4 = (
    "ZVTXEWEEYXSETXISEGGVSRVKGIEENIIIEJIFVTGVRJUXPSHUGMZVSBSMRGKYFJ"
    "SOQDRTOIBKETXZVSVSFKEAVGTHKVQYETXZVUXWQCIKRHJEZYBVMVPCPEGRBFNI"
    "IRLNKZCZXREGJEWYSCEJIDRRZEIIARMSLDGRGMITKHDITYHVSVIFJOTRSEEYIA"
    "SLKPSTOAXSIDGRGCEHYFVAAHITHKJRVGGVSFNIPOJSKHSJTKPSXRGQAVSVEFFR"
    "JVSUAXVWMEKGSCUOHSTESEHZNBMSETJIZRCUXSZLVEFCEJIARRIL"
)

MESSAGE_VIC = (
    "ELAANODTRDIESTIITEOESEANIOODRTRESNSDDSARLNAANSETTRIENINISRNIIO"
    "ILLEEDNNENROOOELAS"
)

CLE_VIC = "5241730219"
# --- FIN DE LA ZONE GÉNÉRÉE ---


# ###########################################################################
#
#  § E — EXPÉRIENCES À FAIRE DANS L'INTERPRÉTEUR (méthode scientifique)
#
# ###########################################################################
#
# EXPÉRIENCE 1 — le damier est bien un carré latin
#     >>> from outils.reference import afficher_tableau_vic
#     >>> print(afficher_tableau_vic())
#     >>> for ligne in range(10):
#     ...     assert sorted(TABLEAU_VIC[ligne]) == sorted(ALPHABET_VIC)
#     Chaque ligne contient les 10 lettres une fois.  Vérifie la même chose pour
#     une colonne : c'est cette propriété qui rend le déchiffrement possible.
#
# EXPÉRIENCE 2 — le tableau des indices, et l'effet des multiples
#     >>> indices = indices_par_periode(MESSAGE_1, 15)
#     >>> for periode in sorted(indices):
#     ...     print(periode, round(indices[periode], 4),
#     ...           "#" * int(200 * indices[periode]))
#     Repère les pics : la vraie période et ses MULTIPLES sortent du lot.  C'est
#     pour cela que periode_probable prend la plus PETITE qui atteint 90 % du
#     meilleur indice.
#
# EXPÉRIENCE 3 — croiser Kasiski et Friedman (la méthode du cryptanalyste)
#     >>> support = support_kasiski(MESSAGE_1)
#     >>> for periode in sorted(support, key=lambda p: -support[p])[:6]:
#     ...     print(periode, support[periode], "voix")
#     >>> print(indices_par_periode(MESSAGE_1, 15)[2], indices_par_periode(MESSAGE_1, 15)[4])
#     Observe : les petits diviseurs (2, 3, 4) reçoivent beaucoup de voix par
#     hasard — Kasiski seul est ambigu.  L'indice de coïncidence, lui, tranche.
#     C'est cette comparaison que tu dois commenter dans la question 3.
#
# EXPÉRIENCE 4 — VIC : et si l'on se trompait de permutation ?
#     >>> dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC,
#     ...                        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
#     Compare avec le résultat correct : cela montre le rôle de la transposition.
#
# EXPÉRIENCE 5 — les quatre dépêches, en une boucle
#     >>> for nom, message in (("1", MESSAGE_1), ("2", MESSAGE_2),
#     ...                      ("3", MESSAGE_3), ("4", MESSAGE_4)):
#     ...     periode = periode_probable(message)
#     ...     cle, clair = forcer_vigenere(message, periode)
#     ...     print(nom, periode, cle, clair[:60])
#
# ###########################################################################
#
#  § F — QUESTIONS DE RAPPORT (à rédiger et à rendre avec le fichier)
#
# ###########################################################################
#
# QUESTION 1. Démontre la propriété de Kasiski : si le même groupe de lettres
# apparaît deux fois dans le texte CLAIR, pourquoi la distance entre les deux
# occurrences est-elle un multiple de la période dans le texte CHIFFRÉ ?
#
# QUESTION 2. Pourquoi les multiples de la vraie période donnent-ils aussi un
# indice de coïncidence élevé ?  Comment ta fonction periode_probable (B.2)
# résout-elle ce problème ?
#
# QUESTION 3. Compare Kasiski et l'indice de coïncidence (expérience 3) :
# lequel donne le plus de faux candidats ?  Lequel est le plus fiable sur une
# dépêche courte ?  Que gagne-t-on à utiliser les deux ?  (C'est la question de
# MÉTHODE de la séance.)
#
# QUESTION 4. Pour chacune des quatre dépêches : période trouvée, clef trouvée,
# et les quinze premières lettres du texte clair.  Laquelle a été la plus
# difficile à casser, et pourquoi ?  (Compare le nombre de lettres par colonne
# pour chaque dépêche : c'est cela qui fait la difficulté.)
#
# QUESTION 5. VIC : explique le rôle des quatre étapes du cours.  Que se
# passerait-il si l'on supprimait l'étape de transposition ?  Et l'addition de
# clef ?  (Tu peux le tester : essaie de déchiffrer MESSAGE_VIC en sautant une
# étape dans ta fonction D.2 et regarde le résultat.)
#
# QUESTION 6. Le damier du VIC est public, et sa clef est ici une suite de
# chiffres écrite en clair dans le fichier.  En quoi cela illustre-t-il le
# principe de Kerckhoffs ?  Et pourquoi le VIC historique a-t-il tout de même
# été cassé ?
#


if __name__ == "__main__":
    # Cette partie s'exécute quand on lance :   python3 tp3_vigenere_vic.py

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

    print("Voici où tu en es dans tes sept fonctions :")
    print("  --- § B : les outils d'analyse ---")
    _essai("B.1 indice_coincidence_moyen('ABAB', 2)",
           lambda: indice_coincidence_moyen("ABAB", 2))
    _essai("B.2 periode_probable(MESSAGE_3)",
           lambda: periode_probable(MESSAGE_3))
    print("  --- § C : ★ cryptanalyse de Vigenère ★ ---")
    _essai("C.1 kasiski_distances('ABCXABCXXXABC', 'ABC')",
           lambda: kasiski_distances("ABCXABCXXXABC", "ABC"))
    _essai("C.2 support_kasiski(MESSAGE_3)",
           lambda: support_kasiski(MESSAGE_3))
    _essai("C.3 forcer_vigenere(MESSAGE_3, periode_probable(MESSAGE_3))",
           lambda: forcer_vigenere(MESSAGE_3, periode_probable(MESSAGE_3)))
    print("  --- § D : code de VIC ---")
    _essai("D.1 chiffre_du_damier (doit redonner le chiffre de départ)",
           lambda: chiffre_du_damier(
               lettre_vic((3 + 1) % 10, 4), 1, 4))
    _essai("D.2 dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC)",
           lambda: dechiffrer_message_vic(MESSAGE_VIC, CLE_VIC))

    print()
    print("Le damier du VIC (utile pour comprendre D.1 et D.2) :")
    from outils.reference import afficher_tableau_vic
    print(afficher_tableau_vic())
    print()
    print("Quand tout est écrit, lance les épreuves :")
    print("    python3 test_tp3_vigenere_vic.py")
