"""==========================================================================
 CRYPTANALYSE LINÉAIRE EN PYTHON
 Cryptographie à clé secrète : chiffrement par blocs, boîte S, LAT,
 piling-up et attaque linéaire du dernier tour (Matsui, 1993).

 Durée conseillée : 3 h.   À rendre : ce fichier complété.
==========================================================================

 ██  MODE D'EMPLOI  ██
==========================================================================

Chaque exercice suit toujours le même plan :

    > OBJECTIF             : ce que la fonction doit faire ;
    > POURQUOI (COURS)     : ce que cela vient faire dans le cours ;
    > CE QUE TU DOIS FAIRE : la recette, étape par étape ;
    > RAPPELS PYTHON       : l'instruction dont tu as besoin ;
    > À COMPLÉTER          : le squelette ; remplace les `...` ;
    > ✅ SOLUTION          : le code complet, en commentaire, à recopier
                             après avoir essayé.

LE PLAN DE CE FICHIER
---------------------
   1. Cryptographie à clé secrète, XOR, masques et biais ............. § A
   2. La boîte S et sa table d'approximations (LAT) ................... § B
   3. Le mini-chiffre SPN-8 (substitution, diffusion, clés) ........... § C
   4. ★ CRYPTANALYSE LINÉAIRE : la trace et l'attaque ★ ............... § D
   5. Des expériences à faire dans l'interpréteur ..................... § E
   6. Des questions de rapport ....................................... § F
   7. Exercices papier et extensions ................................. § G

LA CRYPTANALYSE EST LA PARTIE PRINCIPALE DU TP
----------------------------------------------
Chiffrer, c'est de l'arithmétique.  Casser, c'est de la statistique.  La
cryptanalyse linéaire cherche une relation linéaire (un XOR de bits) entre
le clair, le chiffré et la clé qui est vraie *un peu plus souvent que le
hasard*, puis exploite ce déséquilibre pour retrouver la clé.

LA CRYPTANALYSE LINÉAIRE, EN UNE PHRASE
---------------------------------------
On cherche un XOR de bits du clair, du chiffré et de la clé qui est vrai plus
souvent que le hasard.  Ce déséquilibre minuscule, mesuré sur beaucoup de
couples, suffit à retrouver la clé — sans jamais l'essayer en entier.

LES DOUZE FONCTIONS À ÉCRIRE (+ 1 BONUS)
----------------------------------------
  § B — la brique non linéaire       § C — le chiffre
   B.1  parite_masque                 C.1  permuter
   B.2  appliquer_sbox                C.2  chiffrer
   B.3  sbox_inverse                  C.3  dechiffrer      (bonus)
   B.4  table_approximations

  § D — ★ CRYPTANALYSE ★
   D.1  compter_relation      D.4  cle_candidates
   D.2  attaquer_quartet      D.5  verifier_cles
   D.3  groupe_de_tete        D.6  attaquer_cle

LA BOUCLE DE TRAVAIL
   1. écris une fonction dans ce fichier ;
   2. dans un terminal, ici, tape :   python3 test_tp_cryptanalyse_lineaire.py
   3. lis le bilan : [OK] = c'est juste ; [ÉCHEC] = l'explication ;
   4. recommence, puis passe à la fonction suivante.

CE QUI EST FOURNI (et pourquoi)
-------------------------------
Tu n'as pas à écrire le « rangement » : il est dans `outils/lineaire.py`, que
tu peux lire.  Les éléments fournis sont :

  * la boîte S (`SBOX`) et les constantes du chiffre ;
  * la diversification de clé (`diversifier`), qui n'est pas le sujet ;
  * les mesures statistiques (`intervalle_confiance`, `z_score`, `phi`) ;
  * les affichages (`afficher_lat`, `afficher_scores`, `afficher_groupes`).

Tout ce qui fait la cryptanalyse (la LAT, le chiffrement, l'attaque) est à
toi : c'est l'objet de la séance.

UN POINT DE VOCABULAIRE IMPORTANT
---------------------------------
Le TP distingue TROIS biais, souvent confondus :

  * le biais EXACT   : calculé sur les 256 blocs, pour la clé du jeu de
                       données.  C'est une propriété exacte du chiffre.
  * le biais PILING-UP : prédit par une formule (produit des biais des
                       approximations).  C'est une ESTIMATION.
  * le biais MESURÉ  : calculé sur les N couples dont tu disposes.  Il
                       fluctue autour du biais exact.

Le § A explique les trois.  Aucun exercice ne te demande de les confondre.
==========================================================================
"""

# ---------------------------------------------------------------------------
# LES IMPORTS (n'y touche pas)
# ---------------------------------------------------------------------------
import os
import sys

# Ces deux lignes permettent de trouver `outils/` et `donnees_lineaire.py`
# quel que soit l'endroit d'où tu lances la commande.
DOSSIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DOSSIER)
sys.path.insert(0, os.path.dirname(DOSSIER))

# La boîte S, les constantes et les outils de mesure (écrits par le
# professeur).  Tu peux les utiliser librement.
from outils.lineaire import (
    SBOX,
    CONSTANTES_CLE,
    TAILLE_BLOC,
    NOMBRE_TOURS,
    MASQUE_A,
    MASQUE_B,
    MASQUE_C,
    SEUILS,
    diversifier,
    afficher_lat,
    afficher_scores,
    afficher_groupes,
    intervalle_confiance,
    z_score,
    phi,
)

# Les 2 000 couples (clair, chiffré) interceptés.
from donnees_lineaire import PAIRES


# ###########################################################################
#
#  § A — CRYPTOGRAPHIE À CLÉ SECRÈTE : BITS, XOR, PARITÉ, MASQUES ET BIAIS
#
# ###########################################################################
#
# 0) LA CRYPTOGRAPHIE À CLÉ SECRÈTE (ou symétrique)
#    Alice veut envoyer un message à Bob.  Ils partagent une MÊME clé K, que
#    l'ennemi (Eve) ne connaît pas :
#
#        Alice : C = E(K, M)          Bob : M = D(K, C)
#        et l'on exige D(K, E(K, M)) = M pour tout message M.
#
#    « À clé secrète » signifie que la MÊME clé sert à chiffrer et à
#    déchiffrer.  C'est le contraire de la cryptographie à clé publique, où
#    tout le monde peut chiffrer avec la clé publique et où seule la clé
#    privée déchiffre.
#
#    Conséquence pratique : il faut d'abord se mettre d'accord sur K sans que
#    l'ennemi l'entende.  C'est le « problème de la distribution des clés », et
#    c'est une des raisons pour lesquelles la cryptographie à clé publique a
#    été inventée.
#
#    Ce TP se place entièrement dans ce cadre : une clé K secrète partagée,
#    un algorithme public.  C'est le principe de KERCKHOFFS : la sécurité doit
#    reposer sur le secret de la CLÉ, jamais sur le secret de l'algorithme.
#    Autrement dit, Eve connaît E et D (ici, tout le code de ce fichier) mais
#    pas K.
#
# 0 bis) LE CHIFFREMENT PAR BLOCS
#    Notre chiffre traite le message par BLOCS de taille fixe (ici 8 bits),
#    chacun indépendamment, avec la même clé.  C'est le modèle des chiffres
#    modernes : DES (64 bits), AES (128 bits).
#
#    Un tel chiffre est construit en alternant deux opérations :
#      * de la CONFUSION, non linéaire : la boîte S, qui brouille les bits
#        à l'intérieur d'un quartet ;
#      * de la DIFFUSION, linéaire : la couche P, qui mélange les quartets
#        entre eux.
#    Répétées sur plusieurs TOURS, ces deux opérations rendent le lien entre
#    clair, clé et chiffré très complexe.
#
#    La cryptanalyse linéaire exploite le fait que ce lien n'est pas
#    parfaitement complexe : la boîte S, seule brique non linéaire, possède
#    des approximations linéaires biaisées, et ces biais se combinent d'un
#    tour à l'autre.
#
# 0 ter) CE QUE L'ATTAQUANT POSSÈDE
#    Modèle de la boîte noire, attaque à CLAIR CONNU :
#      * l'algorithme E et la taille des blocs et des clés ;
#      * un grand nombre de couples (M, C = E(K, M)) chiffrés avec la MÊME
#        clé K inconnue ;
#      * pas la clé, et pas le droit de choisir les messages.
#
#    Objectif : retrouver K (ou une partie de K), ou au moins de
#    l'information sur K.  On parle de cryptanalyse dès que l'on fait mieux
#    que la recherche exhaustive de toutes les clés.
#
# 1) LE XOR
#    Le OU exclusif, noté ⊕, vaut 0 si les deux bits sont égaux, 1 sinon :
#
#        0 ⊕ 0 = 0     0 ⊕ 1 = 1     1 ⊕ 0 = 1     1 ⊕ 1 = 0
#
#    Trois propriétés suffisent pour tout ce TP :
#        a ⊕ a = 0          (un bit s'annule avec lui-même)
#        a ⊕ 0 = a          (0 est neutre)
#        a ⊕ b ⊕ a = b      (donc le XOR est son propre inverse)
#    En Python :  a ^ b.
#
#    C'est pour cela qu'en chiffrement on ajoute la clé par XOR : pour
#    déchiffrer, on refait le même XOR avec la même clé.
#
# 2) LA PARITÉ D'UN MOT
#    La parité d'un mot de bits est le XOR de tous ses bits.  Elle vaut 0
#    si le nombre de 1 est pair, 1 sinon :
#
#        parité(1011) = 1 ⊕ 0 ⊕ 1 ⊕ 1 = 1
#
#    En Python, le plus simple :  bin(x).count("1") % 2
#
# 3) UN MASQUE SÉLECTIONNE DES BITS
#    Un masque est un mot de même taille, où les 1 indiquent les bits qui
#    nous intéressent.  La parité masquée est le XOR de ces bits :
#
#        parité(1010 masqué par 0110) = bit2 ⊕ bit1 = 0 ⊕ 1 = 1
#
#    C'est exactement ce que fait la fonction `parite_masque` (B.1).
#    Un masque de quartet va de 0 à 15 : 9 = 1001, 2 = 0010, 13 = 1101.
#
# 4) LA FORME LINÉAIRE
#    Une relation linéaire entre une entrée x et une sortie y s'écrit
#
#        parité(x, a) ⊕ parité(y, b) = 0
#
#    où a et b sont deux masques.  En cryptographie, on la note souvent
#    « a -> b ».  Pour une boîte S, il y a 16 × 16 = 256 couples (a, b)
#    possibles, et l'on peut TOUS les essayer : c'est la table des
#    approximations linéaires, la LAT (§ B).
#
# 5) TROIS QUANTITÉS À NE PAS CONFONDRE
#    Pour une relation donnée, on note p la probabilité qu'elle soit vraie.
#
#        delta = p - 1/2          le BIAIS ABSOLU
#        rho   = 2p - 1           la CORRÉLATION (ou déséquilibre)
#
#    On a rho = 2 delta.  Une relation sans intérêt a p = 1/2, donc
#    delta = rho = 0.  Plus |rho| est grand, plus la relation est utile.
#
#    Pour une boîte S de 4 bits, il n'y a que 16 entrées possibles, donc p
#    est un multiple de 1/16, et l'on peut calculer le biais EXACTEMENT :
#
#        LAT[a][b] = 16 * delta = 8 * rho
#
#    Exemple : LAT[9][2] = -2, donc delta = -2/16 = -1/8, rho = -1/4,
#    et p = 1/2 - 1/8 = 3/8 = 6/16 : la relation est vraie 6 fois sur 16.
#
# 6) LE BIAIS EXACT D'UNE TRACE (pour le chiffre complet)
#    Une trace est une chaîne d'approximations qui traverse les tours.  Son
#    biais dépend de la clé.  Sur notre bloc de 8 bits, on peut le calculer
#    exactement en essayant les 256 clairs possibles :
#
#        p_exact = (nombre de clairs qui satisfont la relation) / 256
#
#    C'est une propriété du chiffre, pas une mesure : il n'y a aucune
#    fluctuation.
#
# 7) LE BIAIS ESTIMÉ PAR LE LEMME DU PILING-UP
#    Pour CHAÎNER des approximations, on utilise le lemme du piling-up.
#    Si les approximations sont indépendantes et ont pour corrélations
#    rho_1, rho_2, ... :
#
#        rho_piling = rho_1 × rho_2 × ...
#        p_piling   = 1/2 + rho_piling / 2
#
#    Équivaut, avec les biais absolus : p = 1/2 + 2^(m-1) × delta_1 × ... × delta_m.
#
#    ATTENTION : c'est une ESTIMATION.  Elle suppose l'indépendance des
#    tours, ce qui est FAUX dans un petit chiffre.  Le TP compare les trois
#    valeurs à l'expérience 2, et l'écart est instructif.
#
# 8) LE BIAIS MESURÉ SUR UN ÉCHANTILLON
#    Un attaquant ne connaît pas la clé, donc il ne peut pas calculer le
#    biais exact.  Il compte sur les N couples dont il dispose :
#
#        p_mesure = (nombre de couples qui satisfont la relation) / N
#
#    Ce n'est qu'une estimation : elle fluctue.  Sous l'hypothèse « pas de
#    biais », l'écart-type de p_mesure vaut 1/(2 sqrt(N)).  On mesure
#    l'écart au hasard par le z-score :
#
#        z = (2 p_mesure - 1) × sqrt(N) = rho × sqrt(N)
#
#    Ordre de grandeur : avec rho = 1/2 et N = 2 000, z ≈ 22.  Le hasard
#    ne produit pas cela.
#
# 9) LE MODÈLE D'ATTAQUE : CLAIR CONNU
#    La cryptanalyse linéaire est une attaque à CLAIR CONNU : l'attaquant
#    dispose de couples (clair, chiffré) chiffrés avec la même clé, mais il
#    ne choisit pas les clairs.  C'est plus faible que le modèle à clairs
#    CHOISIS de la cryptanalyse différentielle, et c'est plus réaliste.
#
# ###########################################################################


# ###########################################################################
#
#  § B — LA BOÎTE S ET SA TABLE D'APPROXIMATIONS (LAT)
#
# ###########################################################################

def parite_masque(valeur, masque):
    """B.1 — OBJECTIF : renvoyer la parité (0 ou 1) des bits de `valeur`
    sélectionnés par `masque`.

    POURQUOI (COURS) : c'est la brique de base de toute la cryptanalyse
    linéaire.  Une forme linéaire n'est rien d'autre qu'une parité masquée,
    et une relation linéaire compare deux parités masquées.

    CE QUE TU DOIS FAIRE :
        étape 1 : garder seulement les bits indiqués par le masque, avec un
                  ET bit à bit :            valeur & masque
        étape 2 : compter les bits à 1 du résultat :
                                                bin(...).count("1")
        étape 3 : renvoyer ce compte modulo 2 :  ... % 2

    RAPPELS PYTHON :
        * `&` est le ET bit à bit, `^` le OU exclusif, `%` le reste ;
        * `bin(13)` vaut `'0b1101'` ; `bin(13).count("1")` vaut 3.

    EXEMPLES (vérifiés par les épreuves) :
        parite_masque(0b1010, 0b1100) -> 1
        parite_masque(0b1010, 0b0110) -> 1
        parite_masque(0b1111, 0b1111) -> 0
    """
    # --- À COMPLÉTER ---
    return bin(... & ...).count("1") % ...

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     return bin(valeur & masque).count("1") % 2
    # ----------------------------------------------------------------------


def appliquer_sbox(x):
    """B.2 — OBJECTIF : appliquer la boîte S aux deux quartets du bloc `x`.

    POURQUOI (COURS) : la boîte S est la seule brique NON LINÉAIRE du
    chiffre.  C'est elle qui empêche une résolution linéaire exacte... mais
    c'est aussi elle qui possède des approximations biaisées, donc elle est
    la source de l'attaque.

    CE QUE TU DOIS FAIRE :
        étape 1 : extraire le quartet fort :  (x >> 4) & 0xF
        étape 2 : extraire le quartet faible : x & 0xF
        étape 3 : remplacer chacun par son image dans `SBOX` ;
        étape 4 : recoller les deux quartets :  (fort << 4) | faible.

    RAPPELS PYTHON :
        * `x >> 4` décale de 4 bits vers la droite (garde le quartet fort) ;
        * `x & 0xF` garde les 4 bits de droite (le quartet faible) ;
        * `<< 4` décale vers la gauche ; `|` recolle deux quartets.

    EXEMPLE : appliquer_sbox(0x5A) = (S[5] << 4) | S[0xA] = 0x0F.
    """
    # --- À COMPLÉTER ---
    fort = SBOX[(x >> 4) & 0xF]
    faible = SBOX[...]
    return (fort << 4) | ...

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     fort = SBOX[(x >> 4) & 0xF]
    #     faible = SBOX[x & 0xF]
    #     return (fort << 4) | faible
    # ----------------------------------------------------------------------


def sbox_inverse(y):
    """B.3 — OBJECTIF : renvoyer l'antécédent du quartet `y` par la boîte S.

    POURQUOI (COURS) : l'attaque déchiffre PARTIELLEMENT le dernier tour :
    elle doit donc appliquer S⁻¹ à un quartet du chiffré.  Sans S⁻¹, pas
    d'attaque du dernier tour.

    `y` est un quartet (0 à 15), pas un bloc de 8 bits.  Comme S est une
    bijection, il existe un unique x tel que S[x] = y.

    CE QUE TU DOIS FAIRE :
        étape 1 : masquer y pour être sûr d'avoir un quartet : y & 0xF ;
        étape 2 : chercher sa position dans `SBOX` avec `.index(...)`.

    RAPPELS PYTHON :
        * `SBOX` est un tuple ; `SBOX.index(valeur)` renvoie l'indice de la
          première occurrence (ici, la seule, puisque SBOX est une
          permutation).

    EXEMPLE : sbox_inverse(0x0) = 5, car SBOX[5] = 0.
    """
    # --- À COMPLÉTER ---
    return SBOX.index(...)

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     return SBOX.index(y & 0xF)
    # ----------------------------------------------------------------------


def table_approximations():
    """B.4 — OBJECTIF : construire la LAT (16 × 16) de la boîte S.

    POURQUOI (COURS) : la LAT est le catalogue de toutes les approximations
    linéaires possibles de la boîte S.  On y lit directement le biais de
    chaque couple de masques, et donc on peut choisir la meilleure.

    Pour chaque couple (a, b), on compte les quartets x tels que

        parite_masque(x, a) == parite_masque(SBOX[x], b)

    puis on retranche 8 (la moitié de 16) pour centrer la table :

        LAT[a][b] = nombre_de_solutions - 8

    CE QUE TU DOIS FAIRE :
        étape 1 : préparer une liste vide `lat` ;
        étape 2 : pour a de 0 à 15, préparer une ligne vide ;
        étape 3 : pour b de 0 à 15, compter les x (de 0 à 15) qui
                  satisfont l'égalité ci-dessus ;
        étape 4 : ajouter `compte - 8` à la ligne ;
        étape 5 : renvoyer `lat`.

    RAPPELS PYTHON :
        * `sum(1 for x in range(16) if condition)` compte les x qui
          satisfont la condition ;
        * `ligne.append(valeur)` ajoute à la fin d'une liste.

    CE QUE TU DOIS OBSERVER (expérience 1) :
        * LAT[0][0] = 8 ; LAT[0][b] = 0 et LAT[a][0] = 0 sinon ;
        * toutes les valeurs sont paires, entre -8 et +8 ;
        * le maximum en valeur absolue, hors (0,0), est 4 : aucune
          approximation de 4 bits ne fait mieux que p = 12/16.
    """
    # --- À COMPLÉTER ---
    lat = []
    for a in range(16):
        ligne = []
        for b in range(16):
            compte = sum(
                1 for x in range(16)
                if parite_masque(x, a) == parite_masque(...)
            )
            ligne.append(compte - ...)
        lat.append(ligne)
    return lat

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     lat = []
    #     for a in range(16):
    #         ligne = []
    #         for b in range(16):
    #             compte = sum(
    #                 1 for x in range(16)
    #                 if parite_masque(x, a) == parite_masque(SBOX[x], b)
    #             )
    #             ligne.append(compte - 8)
    #         lat.append(ligne)
    #     return lat
    # ----------------------------------------------------------------------


# ###########################################################################
#
#  § C — LE MINI-CHIFFRE SPN-8
#
# ###########################################################################
#
# Le chiffre fait 3 tours sur des blocs de 8 bits.  Un bloc, c'est DEUX
# quartets : le quartet fort (poids 16) et le quartet faible (poids 1).
#
#     x0 = m ⊕ K0
#     x1 = P(S(x0)) ⊕ K1
#     x2 = P(S(x1)) ⊕ K2
#     x3 = P(S(x2)) ⊕ K3 = C
#
# S s'applique aux DEUX quartets en même temps.  P échange les quartets.
# La diversification de clé (fournie) donne K0..K3 à partir de M.
#
# ###########################################################################

def permuter(x):
    """C.1 — OBJECTIF : échanger les deux quartets du bloc `x` (couche P).

    POURQUOI (COURS) : la couche linéaire P assure la DIFFUSION : elle
    mélange l'information entre les quartets.  C'est elle qui rend
    l'approximation d'un tour insuffisante, et qui oblige à chaîner les
    approximations (la trace).  Sans P, le chiffre serait deux chiffres
    indépendants de 4 bits !

    CE QUE TU DOIS FAIRE :
        étape 1 : le quartet faible devient le fort : (x & 0xF) << 4 ;
        étape 2 : le quartet fort devient le faible : (x >> 4) & 0xF ;
        étape 3 : recoller les deux avec `|`.

    RAPPEL PYTHON : P est une INVOLUTION : permuter(permuter(x)) == x.

    EXEMPLE : permuter(0xAB) = 0xBA.
    """
    # --- À COMPLÉTER ---
    return ((x & 0xF) << ...) | ((x >> ...) & 0xF)

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     return ((x & 0xF) << 4) | ((x >> 4) & 0xF)
    # ----------------------------------------------------------------------


def chiffrer(bloc, cles):
    """C.2 — OBJECTIF : chiffrer un bloc de 8 bits avec (K0, K1, K2, K3).

    POURQUOI (COURS) : c'est le chiffre attaqué.  Tu dois pouvoir le
    construire pour vérifier tes hypothèses et, à la fin, VÉRIFIER une clé
    candidate : si elle rechiffre correctement les couples connus, c'est la
    bonne.

    CE QUE TU DOIS FAIRE :
        étape 1 : ajouter la clé initiale :  x = bloc ^ cles[0]
        étape 2 : pour chaque tour de 1 à 3 :
                      x = permuter(appliquer_sbox(x)) ^ cles[tour]
        étape 3 : renvoyer x & 0xFF (on reste sur 8 bits).

    RAPPELS PYTHON :
        * `for tour in range(1, len(cles))` parcourt 1, 2, 3 ;
        * `cles` est un tuple de 4 entiers, par exemple diversifier(19).

    VECTEURS DE TEST (publics, vérifiés par les épreuves) :
        chiffrer(0x00, (0, 0, 0, 0))                  -> 0x99
        chiffrer(0xAB, (0x12, 0x34, 0x56, 0x78))       -> 0x2D
    """
    # --- À COMPLÉTER ---
    x = bloc ^ ...
    for tour in range(1, len(cles)):
        x = permuter(...) ^ cles[...]
    return x & 0xFF

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     x = bloc ^ cles[0]
    #     for tour in range(1, len(cles)):
    #         x = permuter(appliquer_sbox(x)) ^ cles[tour]
    #     return x & 0xFF
    # ----------------------------------------------------------------------


def dechiffrer(bloc, cles):
    """C.3 — BONUS : déchiffrer un bloc (inverse de `chiffrer`).

    POURQUOI (COURS) : un chiffrement doit être réversible.  Écrire
    l'inverse oblige à comprendre l'ordre des opérations, et sert aux
    extensions du § G (retrouver K2, K1, K0 en remontant les tours).

    CE QUE TU DOIS FAIRE :
        étape 1 : x = bloc & 0xFF ;
        étape 2 : pour tour de 3 à 1 (ordre INVERSE) :
                      a. retirer la clé :       x ^ cles[tour]
                      b. refaire P :            permuter(...)
                      c. appliquer S⁻¹ :        sbox_inverse sur les deux
                                                quartets, puis recoller ;
        étape 3 : retirer la clé initiale : x ^ cles[0].

    ATTENTION À L'ORDRE : au chiffrement, on fait S puis P puis XOR.
    Au déchiffrement, on défait donc XOR, puis P, puis S⁻¹.

    RAPPEL PYTHON : `for tour in range(len(cles) - 1, 0, -1)` parcourt
    3, 2, 1.
    """
    # --- À COMPLÉTER (bonus) ---
    x = bloc & 0xFF
    for tour in range(len(cles) - 1, 0, -1):
        x = permuter(x ^ cles[tour])
        x = (sbox_inverse((x >> 4) & 0xF) << 4) | sbox_inverse(...)
    return (x ^ cles[0]) & 0xFF

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     x = bloc & 0xFF
    #     for tour in range(len(cles) - 1, 0, -1):
    #         x = permuter(x ^ cles[tour])
    #         x = (sbox_inverse((x >> 4) & 0xF) << 4) | sbox_inverse(x & 0xF)
    #     return (x ^ cles[0]) & 0xFF
    # ----------------------------------------------------------------------


# ###########################################################################
#
#  § D — ★ CRYPTANALYSE LINÉAIRE ★
#
# ###########################################################################
#
# LA TRACE UTILISÉE :  9 -> 2 -> 13, sur DEUX tours.
#
#   tour 1, quartet BAS   :  9 -> 2    LAT[9][2]  = -2   rho = -1/4
#   tour 2, quartet HAUT  :  2 -> 13   LAT[2][13] = +4   rho = +1/2
#
# Pourquoi le quartet change : c'est P !  Le quartet bas du tour 1 devient
# le quartet haut du tour 2.  Le masque suit la même permutation.
#
# POURQUOI DEUX TOURS ET PAS TROIS :
#   La trace s'arrête à l'ENTRÉE de la boîte S du troisième tour.  Il reste
#   donc UN tour à attaquer : on teste les 16 valeurs d'un quartet de K3.
#   Si la trace traversait les trois tours, elle se terminerait sur la
#   SORTIE de la S du troisième tour, qui dépend des 8 bits de K3 : il
#   faudrait 256 candidats, et l'on ne gagnerait plus rien.
#
# LE PILING-UP PRÉDIT :
#   rho_piling = (-1/4) × (+1/2) = -1/8
#   p_piling   = 1/2 + (-1/8)/2 = 7/16 = 0,4375
#   C'est une ESTIMATION.  Le biais EXACT de ce jeu de données est
#   différent (voir l'expérience 2).
#
# CE QUE L'ON COMPTE :
#   trace basse (départ quartet bas)  -> quartet bas de x2, masque 13
#        x2_bas = S⁻¹( quartet HAUT du chiffré ⊕ candidat )
#        candidat = K3_HAUT
#   trace haute (départ quartet haut) -> quartet haut de x2, masque 13
#        x2_haut = S⁻¹( quartet BAS du chiffré ⊕ candidat )
#        candidat = K3_BAS
#
# ###########################################################################

def compter_relation(paires, masque_entree, masque_sortie, depart_haut, candidat):
    """D.1 — OBJECTIF : compter combien de couples satisfont la relation.

    POURQUOI (COURS) : c'est le cœur de l'attaque.  Pour un candidat donné,
    on déchiffre PARTIELLEMENT le dernier tour, puis on compte combien de
    fois la relation linéaire est vraie.  Le bon candidat donne un compte
    anormalement éloigné de N/2.

    CE QUE TU DOIS FAIRE, pour chaque couple (clair, chiffre) :
        étape 1 : choisir le quartet du clair et calculer y, le quartet du
                  chiffré après XOR avec le candidat :

                  si depart_haut est FAUX (trace basse) :
                      quartet_clair = clair & 0xF
                      y = ((chiffre >> 4) & 0xF) ^ candidat
                  si depart_haut est VRAI (trace haute) :
                      quartet_clair = (clair >> 4) & 0xF
                      y = (chiffre & 0xF) ^ candidat

        étape 2 : déchiffrer la boîte S du dernier tour :
                      entree_sbox = sbox_inverse(y)
        étape 3 : tester l'égalité des deux parités :
                      parite_masque(quartet_clair, masque_entree)
                          == parite_masque(entree_sbox, masque_sortie)
                  et incrémenter le total si elle est vraie.
        étape 4 : renvoyer le total.

    RAPPELS PYTHON :
        * `for clair, chiffre in paires:` déballe chaque couple ;
        * une variable `total = 0` que l'on incrémente avec `total += 1`.

    CE QUE TU DOIS OBSERVER : pour le vrai candidat, le compte s'écarte
    nettement de N/2 ; pour les autres, il en est proche... mais pas
    toujours exactement (expérience 3).
    """
    # --- À COMPLÉTER ---
    total = 0
    for clair, chiffre in paires:
        if depart_haut:
            quartet_clair = (clair >> 4) & 0xF
            y = (chiffre & 0xF) ^ ...
        else:
            quartet_clair = clair & 0xF
            y = ((chiffre >> ...) & 0xF) ^ candidat
        entree_sbox = sbox_inverse(...)
        if parite_masque(quartet_clair, masque_entree) == parite_masque(entree_sbox, ...):
            total += 1
    return total

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     total = 0
    #     for clair, chiffre in paires:
    #         if depart_haut:
    #             quartet_clair = (clair >> 4) & 0xF
    #             y = (chiffre & 0xF) ^ candidat
    #         else:
    #             quartet_clair = clair & 0xF
    #             y = ((chiffre >> 4) & 0xF) ^ candidat
    #         entree_sbox = sbox_inverse(y)
    #         if parite_masque(quartet_clair, masque_entree) == parite_masque(entree_sbox, masque_sortie):
    #             total += 1
    #     return total
    # ----------------------------------------------------------------------


def attaquer_quartet(paires, masque_entree, masque_sortie, depart_haut):
    """D.2 — OBJECTIF : classer les 16 candidats d'un quartet de K3.

    POURQUOI (COURS) : on ne peut pas « lire » la clé dans un comptage.  On
    classe les candidats par écart au hasard, et l'on garde les meilleurs.

    Pour chaque candidat k de 0 à 15, on calcule son compte avec
    `compter_relation`, puis son score :

        score = |2 × compte - N|

    Ce score vaut 0 si le compte vaut exactement N/2 (aucun biais) et N si
    le compte vaut 0 ou N (biais maximal).

    CE QUE TU DOIS FAIRE :
        étape 1 : n = len(paires) ;
        étape 2 : pour candidat de 0 à 15, calculer le compte et le score,
                  et ranger le couple (score, candidat) dans une liste ;
        étape 3 : trier la liste du plus grand score au plus petit
                  (`liste.sort(reverse=True)`) ;
        étape 4 : renvoyer la liste triée.

    ATTENTION — LE PIÈGE DU TP : le score est une valeur ABSOLUE.  Il ne
    distingue pas un candidat à p = 0,25 d'un candidat à p = 0,75, et
    plusieurs candidats peuvent avoir EXACTEMENT le même score.  Le premier
    de la liste n'est donc pas forcément le bon : c'est pour cela que D.3
    garde un GROUPE de tête.

    RAPPEL PYTHON : `abs(...)` donne la valeur absolue.
    """
    # --- À COMPLÉTER ---
    n = len(paires)
    scores = []
    for candidat in range(16):
        compte = compter_relation(paires, ..., ..., depart_haut, ...)
        scores.append((abs(2 * compte - n), ...))
    scores.sort(reverse=True)
    return scores

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     n = len(paires)
    #     scores = []
    #     for candidat in range(16):
    #         compte = compter_relation(paires, masque_entree, masque_sortie, depart_haut, candidat)
    #         scores.append((abs(2 * compte - n), candidat))
    #     scores.sort(reverse=True)
    #     return scores
    # ----------------------------------------------------------------------


def groupe_de_tete(scores, proportion=0.8):
    """D.3 — OBJECTIF : garder les candidats dont le score atteint
    `proportion` fois le meilleur score.

    POURQUOI (COURS) : une seule relation linéaire ne donne qu'une PARTIE
    de l'information sur la clé.  Plusieurs quartets peuvent produire un
    biais important, et le score absolu ne permet pas de les distinguer.
    On garde donc un petit groupe, que l'on départagera ensuite avec des
    couples connus.

    CE QUE TU DOIS FAIRE :
        étape 1 : si la liste est vide, renvoyer [] ;
        étape 2 : prendre le meilleur score : scores[0][0] ;
        étape 3 : si ce meilleur score vaut 0, tous les candidats se valent :
                  renvoyer les 16 candidats triés ;
        étape 4 : sinon, garder les candidats dont le score est supérieur ou
                  égal à `proportion * meilleur`, et renvoyer la liste triée.

    RAPPELS PYTHON :
        * `sorted(iterable)` renvoie une liste triée ;
        * une compréhension de liste :
              [candidat for score, candidat in scores if condition]

    RÉSULTAT ATTENDU ICI (avec les 2 000 couples) :
        trace basse -> [4, 7, 8, 11]   (quatre candidats à égalité)
        trace haute -> [10]            (un seul)
    """
    # --- À COMPLÉTER ---
    if not scores:
        return []
    meilleur = scores[...][0]
    if meilleur == 0:
        return sorted(candidat for _, candidat in scores)
    return sorted(
        candidat for score, candidat in scores
        if score >= ... * meilleur
    )

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     if not scores:
    #         return []
    #     meilleur = scores[0][0]
    #     if meilleur == 0:
    #         return sorted(candidat for _, candidat in scores)
    #     return sorted(
    #         candidat for score, candidat in scores
    #         if score >= proportion * meilleur
    #     )
    # ----------------------------------------------------------------------


def cle_candidates(paires, proportion=0.8):
    """D.4 — OBJECTIF : en déduire les clés maîtres compatibles.

    POURQUOI (COURS) : l'attaque récupère les quartets de K3 par groupes.
    Comme la diversification M -> K3 est une BIJECTION, chaque couple de
    quartets compatibles correspond à une clé maître au plus : on n'essaie
    donc jamais plus de 256 clés, et souvent beaucoup moins.

    CE QUE TU DOIS FAIRE :
        étape 1 : classer les 16 candidats pour K3_HAUT (trace basse,
                  `depart_haut=False`) et garder le groupe de tête ;
        étape 2 : idem pour K3_BAS (trace haute, `depart_haut=True`) ;
        étape 3 : pour chaque clé maître M de 0 à 255 :
                      a. calculer K3 = diversifier(M)[3] ;
                      b. garder le quartet haut (K3 >> 4) & 0xF et le
                         quartet bas K3 & 0xF ;
                      c. si les deux sont dans les groupes, retenir M ;
        étape 4 : renvoyer (liste triée des candidats, groupe_haut, groupe_bas).

    RAPPELS PYTHON :
        * `for cle_maitre in range(256)` ;
        * `diversifier(M)` est fourni et renvoie (K0, K1, K2, K3).

    ATTENTION : `depart_haut=False` correspond à K3_HAUT, et non à K3_BAS.
    C'est un piège classique : la trace PART du quartet bas, donc elle
    ARRIVE sur le quartet bas de x2, qui se calcule avec K3_HAUT.

    RÉSULTAT ATTENDU : ([19, 51, 163, 179], [4, 7, 8, 11], [10]).
    """
    # --- À COMPLÉTER ---
    scores_haut = attaquer_quartet(paires, MASQUE_A, MASQUE_C, ...)
    scores_bas = attaquer_quartet(paires, MASQUE_A, MASQUE_C, ...)
    groupe_haut = groupe_de_tete(scores_haut, proportion)
    groupe_bas = groupe_de_tete(scores_bas, ...)

    candidats = []
    for cle_maitre in range(256):
        k3 = diversifier(cle_maitre)[...]
        if ((k3 >> 4) & 0xF) in groupe_haut and (k3 & 0xF) in ...:
            candidats.append(...)
    return candidats, groupe_haut, groupe_bas

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     scores_haut = attaquer_quartet(paires, MASQUE_A, MASQUE_C, False)
    #     scores_bas = attaquer_quartet(paires, MASQUE_A, MASQUE_C, True)
    #     groupe_haut = groupe_de_tete(scores_haut, proportion)
    #     groupe_bas = groupe_de_tete(scores_bas, proportion)
    #
    #     candidats = []
    #     for cle_maitre in range(256):
    #         k3 = diversifier(cle_maitre)[3]
    #         if ((k3 >> 4) & 0xF) in groupe_haut and (k3 & 0xF) in groupe_bas:
    #             candidats.append(cle_maitre)
    #     return candidats, groupe_haut, groupe_bas
    # ----------------------------------------------------------------------


def verifier_cles(candidats, paires, nombre=3):
    """D.5 — OBJECTIF : ne garder que les clés qui rechiffrent correctement
    les `nombre` premiers couples connus.

    POURQUOI (COURS) : c'est la vérification finale, celle qui transforme
    une présomption statistique en certitude.  Elle coûte presque rien :
    quelques chiffrements.  Un attaquant réel fait toujours cette étape.

    CE QUE TU DOIS FAIRE :
        étape 1 : préparer une liste vide `survivantes` ;
        étape 2 : pour chaque clé candidate :
                      a. calculer ses clés de tour : diversifier(cle) ;
                      b. chiffrer le clair de chacun des `nombre` premiers
                         couples et comparer au chiffré ;
                      c. si tout correspond, ajouter la clé à `survivantes` ;
        étape 3 : renvoyer `survivantes`.

    RAPPELS PYTHON :
        * `paires[:nombre]` prend les `nombre` premiers couples ;
        * `all(condition for ...)` vaut True si toutes les conditions sont
          vraies.

    RÉSULTAT ATTENDU : [19].
    """
    # --- À COMPLÉTER ---
    survivantes = []
    temoins = paires[:...]
    for cle_maitre in candidats:
        cles = diversifier(...)
        if all(chiffrer(clair, cles) == chiffre for clair, chiffre in ...):
            survivantes.append(...)
    return survivantes

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     survivantes = []
    #     temoins = paires[:nombre]
    #     for cle_maitre in candidats:
    #         cles = diversifier(cle_maitre)
    #         if all(chiffrer(clair, cles) == chiffre for clair, chiffre in temoins):
    #             survivantes.append(cle_maitre)
    #     return survivantes
    # ----------------------------------------------------------------------


def attaquer_cle(paires, nombre_verifications=3, seuils=SEUILS):
    """D.6 — OBJECTIF : l'attaque complète, avec élargissement progressif.

    POURQUOI (COURS) : sur un échantillon, le bruit peut faire sortir le bon
    quartet du groupe de tête.  Une attaque honnête ne le cache pas : elle
    ÉLARGIT le groupe, et si elle ne peut toujours pas conclure, elle
    renvoie un statut explicite.

    Les quatre statuts possibles :
        "certaine"  : une seule clé survit, au seuil strict (0,8) ;
        "elargie"   : une seule clé survit, mais il a fallu élargir ;
        "incertaine": plusieurs clés survivent -> on ne conclut pas ;
        "echec"     : aucune clé ne vérifie les couples connus.

    CE QUE TU DOIS FAIRE :
        étape 1 : préparer `derniers = []` ;
        étape 2 : pour chaque seuil, du plus strict au plus large :
                      a. candidats, _, _ = cle_candidates(paires, seuil) ;
                      b. survivantes = verifier_cles(candidats, paires,
                                                     nombre_verifications) ;
                      c. retenir `survivantes` dans `derniers` ;
                      d. si UNE seule clé survit, la renvoyer avec
                         "certaine" (premier seuil) ou "elargie" ;
        étape 3 : après la boucle, s'il reste PLUSIEURS survivantes au
                  dernier seuil, renvoyer (None, "incertaine") ;
        étape 4 : sinon, renvoyer (None, "echec").

    RAPPELS PYTHON :
        * `for indice, seuil in enumerate(seuils)` donne l'indice et la
          valeur ;
        * `len(liste) == 1` teste s'il y a exactement un élément.

    IMPORTANT : on ne bascule JAMAIS sur une recherche exhaustive des 256
    clés pour « sauver » l'attaque.  Un échec est un échec, et il est
    instructif : il signifie que l'échantillon est trop petit.

    RÉSULTATS ATTENDUS :
        avec les 2 000 couples      -> (19, "certaine")
        avec 20 couples (graine 2)  -> (19, "elargie")
        avec 20 couples (graine 5)  -> (None, "echec")
    """
    # --- À COMPLÉTER ---
    derniers = []
    for indice, seuil in enumerate(seuils):
        candidats, _, _ = cle_candidates(paires, ...)
        survivantes = verifier_cles(candidats, paires, ...)
        derniers = survivantes
        if len(survivantes) == 1:
            statut = "certaine" if indice == ... else "elargie"
            return survivantes[0], statut
    if len(derniers) > 1:
        return None, "..."
    return None, "..."

    # ----------------------------------------------------------------------
    # ✅ SOLUTION
    # ----------------------------------------------------------------------
    #     derniers = []
    #     for indice, seuil in enumerate(seuils):
    #         candidats, _, _ = cle_candidates(paires, seuil)
    #         survivantes = verifier_cles(candidats, paires, nombre_verifications)
    #         derniers = survivantes
    #         if len(survivantes) == 1:
    #             statut = "certaine" if indice == 0 else "elargie"
    #             return survivantes[0], statut
    #     if len(derniers) > 1:
    #         return None, "incertaine"
    #     return None, "echec"
    # ----------------------------------------------------------------------


# ###########################################################################
#
#  § E — EXPÉRIENCES À FAIRE DANS L'INTERPRÉTEUR
#
# ###########################################################################
#
# Lance Python dans ce dossier :   python3
# puis :                          from tp_cryptanalyse_lineaire import *
#
# EXPÉRIENCE 1 — la LAT et le biais exact d'une boîte S
#     >>> lat = table_approximations()
#     >>> afficher_lat(lat)
#     >>> lat[9][2], lat[2][13]
#     >>> lat[9]                                      # la ligne du masque 9
#     Vérifie à la main : LAT[9][2] = -2 signifie 6 solutions sur 16, donc
#     p = 6/16 = 0,375, delta = -0,125, rho = -0,25.
#     Question : pourquoi toutes les valeurs sont-elles paires ?
#
# EXPÉRIENCE 2 — les TROIS biais de la trace
#     >>> from outils.lineaire import biais_exact, piling_up
#     >>> cles_vraies = diversifier(19)        # clé du jeu de données
#     >>> print(biais_exact(cles_vraies, depart_haut=False))   # trace basse
#     >>> print(biais_exact(cles_vraies, depart_haut=True))    # trace haute
#     >>> print(piling_up(lat[9][2], lat[2][13]))
#     >>> p_mesure = compter_relation(PAIRES, 9, 13, False, 0xB) / len(PAIRES)
#     >>> print(p_mesure)
#     Tu obtiens trois valeurs différentes :
#         piling-up : 0,4375          (estimation)
#         p_exact   : 0,25 et 0,875   (propriété du chiffre et de la clé)
#         p_mesuré  : environ 0,258 et 0,873
#     Écris dans ton rapport POURQUOI le piling-up se trompe ici.
#
# EXPÉRIENCE 3 — les mauvais candidats n'ont pas tous un biais nul
#     >>> scores = attaquer_quartet(PAIRES, 9, 13, False)
#     >>> afficher_scores(scores)
#     >>> groupe_de_tete(scores)
#     Observe : plusieurs candidats atteignent le même score que le bon.
#     Calcule leur biais mesuré : certains valent 0,75, d'autres 0,375.
#     CONCLUSION : « un mauvais candidat donne N/2 » est FAUX en général.
#     C'est le score ABSOLU qui les met à égalité.
#
# EXPÉRIENCE 4 — l'attaque complète, et sa vérification
#     >>> cle, statut = attaquer_cle(PAIRES)
#     >>> print(cle, statut)
#     >>> candidats, gh, gb = cle_candidates(PAIRES)
#     >>> print(candidats)
#     >>> print(verifier_cles(candidats, PAIRES, 3))
#     La clé est-elle bien 19 ? Vérifie en rechiffrant :
#     >>> cles = diversifier(cle)
#     >>> all(chiffrer(m, cles) == c for m, c in PAIRES)
#
# EXPÉRIENCE 5 — combien de couples faut-il ? (la limite statistique)
#     >>> import random
#     >>> for N in (20, 50, 100, 200, 400, 800, 2000):
#     ...     echantillon = PAIRES[:N]
#     ...     cle, statut = attaquer_cle(echantillon)
#     ...     print(N, cle, statut)
#     Recommence avec des échantillons tirés au hasard :
#     >>> for essai in range(10):
#     ...     echantillon = random.sample(PAIRES, 100)
#     ...     print(attaquer_cle(echantillon))
#     Tu dois voir apparaître des "echec" et des "elargie" sur les petits N.
#     C'est NORMAL et c'est le sujet de la question 5.
#
# EXPÉRIENCE 6 — le biais exact dépend de la clé
#     >>> from outils.lineaire import biais_exact
#     >>> for M in (16, 19, 26, 35, 227):
#     ...     c = diversifier(M)
#     ...     print(M, biais_exact(c, depart_haut=False), biais_exact(c, depart_haut=True))
#     Certaines clés donnent un biais NUL dans une orientation.  Sur les 256
#     clés possibles, 80 ont un biais exact nul dans une orientation donnée.
#     C'est pourquoi le jeu de données a été CALIBRÉ (choix de M = 19).
#
# ###########################################################################


# ###########################################################################
#
#  § F — QUESTIONS DE RAPPORT (à rédiger et à rendre avec ce fichier)
#
# ###########################################################################
#
# QUESTION 1. Démontre que a ⊕ b ⊕ a = b, puis que la parité d'un mot est
#     un XOR de ses bits.  Explique pourquoi l'addition de clé par XOR est
#     réversible.
#
# QUESTION 2. Pour LAT[9][2] = -2 : calcule p, delta et rho.  Le signe
#     négatif a-t-il une importance pour l'attaque ?  Justifie.
#
# QUESTION 3. Énonce le lemme du piling-up avec les corrélations (rho), puis
#     avec les biais absolus (delta).  Vérifie que les deux formules donnent
#     le même résultat pour notre trace (7/16).
#
# QUESTION 4. Compare les trois biais de l'expérience 2.  Pourquoi le
#     piling-up se trompe-t-il ?  Que faudrait-il pour qu'il soit exact ?
#
# QUESTION 5. À partir de quelle valeur de N l'attaque devient-elle fiable ?
#     Utilise l'expérience 5 et l'ordre de grandeur N ≈ 1/(delta1 - delta2)²
#     où delta2 est le biais du meilleur candidat concurrent.  Compare avec
#     le nombre de couples réellement utilisés (2 000).
#
# QUESTION 6. Pourquoi le score |2c - N| ne permet-il pas de désigner un
#     unique candidat ?  Explique l'égalité à quatre de la trace basse, et
#     comment la vérification D.5 la lève.
#
# QUESTION 7. L'attaque renvoie parfois "echec" (expérience 5).  Est-ce un
#     bug ?  Que peut faire un cryptanalyste dans ce cas ?
#
# QUESTION 8. En quoi la cryptanalyse linéaire est-elle une attaque à clairs
#     CONNUS, et non à clairs CHOISIS ?  Quelle différence cela fait-il pour
#     l'attaquant ?
#
# QUESTION 9. Sur le DES, Matsui utilise environ 2^47 couples clair-chiffré.
#     Calcule l'ordre de grandeur du nombre de couples nécessaires si le
#     biais valait 10^-6, puis 10^-8.  Conclus sur la difficulté.
#
# QUESTION 10. Pourquoi un chiffrement réel utilise-t-il beaucoup plus de
#     tours ?  Que devient le biais d'une trace quand on ajoute des tours ?
#
# ###########################################################################


# ###########################################################################
#
#  § G — EXERCICES PAPIER ET EXTENSIONS
#
# ###########################################################################
#
# EXERCICE 1 (papier).  Calcule à la main LAT[9][2] :
#     pour chacun des 16 quartets x, calcule parité(x, 9), puis parité(S[x], 2),
#     et compte les égalités.  Tu dois trouver 6, donc LAT[9][2] = -2.
#
# EXERCICE 2 (papier).  Si p = 0,5625, que valent delta et rho ?  Si
#     rho = -0,25, que valent p et delta ?  Lequel est le meilleur pour
#     l'attaquant : p = 0,75 ou p = 0,25 ?  (Attention au piège.)
#
# EXERCICE 3 (papier).  Applique le piling-up à 2, 3 et 4 approximations de
#     corrélation 1/4.  Que constate-t-on quand le nombre de tours augmente ?
#
# EXERCICE 4 (machine).  Écris `dechiffrer` (C.3) et vérifie :
#         all(dechiffrer(chiffrer(m, c), c) == m for m in range(256))
#     avec c = diversifier(19).
#
# EXERCICE 5 (machine, diagnostic).  Une fois K3 connu, on peut calculer
#     x2 = S⁻¹(P(C ⊕ K3)) pour chaque couple : on obtient un chiffre réduit à
#     deux tours, de clé (K0, K1, K2).  Applique alors la MÊME méthode pour
#     retrouver K2, avec la trace à UNE approximation 9 -> 2.
#
#     Résultat attendu : le groupe de tête ne contient PAS le bon quartet.
#     Mesure les biais exacts et explique pourquoi.  C'est un résultat
#     important : une seule approximation de 4 bits a un biais faible, et un
#     mauvais candidat peut avoir un biais comparable ou supérieur.  La
#     remontée des tours demande des traces plus longues et plus de données.
#     (Corrigé détaillé : corriges/corrige_exercices_lineaire.md.)
#
# EXERCICE 6 (machine).  Change la trace : choisis un autre couple (a, b) de
#     la LAT, recalcule le piling-up, et refais l'attaque.  Compare les
#     biais exacts et le taux de succès.
#
# EXERCICE 7 (machine).  Implémente la diversification de clé complète du TD
#     d'origine (sélection de bits de la clé maître) et retrouve la clé
#     maître de 32 bits à partir de K3.
#
# EXERCICE 8 (réflexion).  Le score |2c - N| vaut 0 quand c = N/2.  Que se
#     passe-t-il si N est impair ?  Et si le biais exact est nul pour la clé
#     utilisée ?  Que doit faire l'attaque ?
#
# ###########################################################################


if __name__ == "__main__":
    # Cette partie s'exécute quand on lance :  python3 tp_cryptanalyse_lineaire.py

    def _inacheve(valeur):
        """Vrai si la fonction n'est pas finie : il reste des « ... » ou rien."""
        if valeur is Ellipsis or valeur is None:
            return True
        if isinstance(valeur, (tuple, list)):
            return any(_inacheve(element) for element in valeur)
        return False

    def _essai(nom, appel):
        try:
            resultat = appel()
        except Exception as erreur:                     # fonction incomplète ?
            print(f"  {nom} : pas encore terminée ({type(erreur).__name__})")
            return
        if _inacheve(resultat):
            print(f"  {nom} : pas encore terminée (les ... du squelette sont encore là)")
        else:
            print(f"  {nom} -> {resultat}")

    print("Voici où tu en es dans tes fonctions :")
    print("  --- § B : la boîte S et la LAT ---")
    _essai("B.1 parite_masque(0b1010, 0b1100)", lambda: parite_masque(0b1010, 0b1100))
    _essai("B.2 appliquer_sbox(0x5A)", lambda: hex(appliquer_sbox(0x5A)))
    _essai("B.3 sbox_inverse(0x0)", lambda: sbox_inverse(0x0))
    _essai("B.4 LAT[9][2]", lambda: table_approximations()[9][2])
    print("  --- § C : le chiffre ---")
    _essai("C.1 permuter(0xAB)", lambda: hex(permuter(0xAB)))
    _essai("C.2 chiffrer(0x00, clés nulles)",
           lambda: hex(chiffrer(0x00, (0, 0, 0, 0))))
    _essai("C.3 dechiffrer(chiffrer(0xAB)) (bonus)",
           lambda: hex(dechiffrer(chiffrer(0xAB, (0x12, 0x34, 0x56, 0x78)),
                                  (0x12, 0x34, 0x56, 0x78))))
    print("  --- § D : ★ la cryptanalyse ★ ---")
    _essai("D.1 compter_relation (trace basse, candidat 0xB)",
           lambda: compter_relation(PAIRES, MASQUE_A, MASQUE_C, False, 0xB))
    _essai("D.2 attaquer_quartet (trace basse, 3 premiers)",
           lambda: attaquer_quartet(PAIRES, MASQUE_A, MASQUE_C, False)[:3])
    _essai("D.3 groupe_de_tete (trace basse)",
           lambda: groupe_de_tete(attaquer_quartet(PAIRES, MASQUE_A, MASQUE_C, False)))
    _essai("D.4 cle_candidates",
           lambda: cle_candidates(PAIRES))
    _essai("D.5 verifier_cles",
           lambda: verifier_cles(cle_candidates(PAIRES)[0], PAIRES, 3))
    _essai("D.6 attaquer_cle", lambda: attaquer_cle(PAIRES))

    print()
    print("Quand tout est écrit, lance les épreuves :")
    print("    python3 test_tp_cryptanalyse_lineaire.py")
