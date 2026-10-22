"""==========================================================================
 OUTILS DE CRYPTANALYSE LINÉAIRE — le socle du TP
==========================================================================

Ce fichier est écrit par le professeur.  Tu peux (et tu devrais) le lire :
il contient la version de référence du mini-chiffre, les mesures statistiques
et l'affichage.  Tu n'as pas à le modifier.

Le mini-chiffre, appelé SPN-8, est un chiffrement par blocs jouet :

  * un bloc de 8 bits, vu comme deux quartets : A (poids fort) et B (faible) ;
  * une boîte S de 4 bits, celle de PRESENT (Bogdanov et al., 2007) ;
  * une couche linéaire P qui échange les deux quartets ;
  * trois tours, chacun terminé par l'addition XOR d'une clé de tour ;
  * une clé maître de 8 bits, diversifiée en quatre clés de tour.

Chiffrement :

      x0 = m ⊕ K0
      x1 = P(S(x0)) ⊕ K1
      x2 = P(S(x1)) ⊕ K2
      x3 = P(S(x2)) ⊕ K3 = C

où S s'applique quartet par quartet.

TROIS BIAIS À NE PAS CONFONDRE
------------------------------
Pour une relation linéaire donnée (une « approximation »), on rencontre trois
quantités différentes.  Le TP les distingue systématiquement :

  1. le BIAIS EXACT (`p_exact`, `delta_exact`, `rho_exact`)
     Il est calculé sur les 16 entrées possibles de la boîte S, ou sur les 256
     blocs possibles du chiffre, pour une clé FIXÉE.  C'est une propriété
     exacte du chiffre, il n'y a aucune fluctuation.
     Pour la boîte S :  p_exact = (8 + LAT[a][b]) / 16.
     Pour la trace et une clé fixée : on énumère les 256 clairs.

  2. le BIAIS ESTIMÉ PAR PILING-UP (`p_piling`, `delta_piling`)
     C'est une FORMULE, qui suppose les approximations indépendantes :
         rho_piling = ∏ rho_i        p_piling = 1/2 + rho_piling/2
     Ce n'est pas une valeur mesurée : c'est une prédiction.  Dans un
     mini-chiffre, les tours ne sont pas indépendants et plusieurs traces
     contribuent ; l'écart avec le biais exact peut être important.

  3. le BIAIS MESURÉ SUR UN ÉCHANTILLON (`p_mesure`, `delta_mesure`)
     C'est ce que l'attaquant calcule sur N couples clair-chiffré :
         p_mesure = compte / N
     Il fluctue autour du biais exact, avec un écart-type d'environ
     1/(2√N) quand il n'y a pas de biais.

Conventions (identiques dans tout le TP) :

      p      = probabilité que la relation soit vraie
      delta  = p - 1/2                (biais absolu)
      rho    = 2p - 1 = 2 delta       (corrélation, ou déséquilibre)

      LAT[a][b] = 16 * delta = 8 * rho      (pour la boîte S)
      z-score   = rho * sqrt(N)             (écart au hasard, en écarts-types)

LE JEU DE DONNÉES DU TP
-----------------------
La clé maître est M = 19 (0x13), et la diversification donne :

      K0 = 0x13    K1 = 0x40    K2 = 0xB1    K3 = 0xBA
      K3_haut = 0xB    K3_bas = 0xA

La trace utilisée est 9 -> 2 -> 13 sur deux tours.  Pour cette clé, le biais
EXACT de la trace vaut :

      orientation basse  : p = 0,250   (delta = -0,250, rho = -0,500)
      orientation haute  : p = 0,875   (delta = +0,375, rho = +0,750)

alors que le piling-up prédit p = 0,4375.  L'écart est le sujet de
l'expérience 2 : le piling-up est une estimation, pas une loi.

ATTENTION : sur un bloc de 8 bits, le biais exact dépend de la clé et peut
être NUL.  Le jeu de données a été calibré (choix de M) pour que ce ne soit
pas le cas ici ; ce n'est pas une propriété générale du chiffre.
==========================================================================
"""

from __future__ import annotations

import math
import random

__all__ = [
    "SBOX", "SBOX_INVERSE", "CONSTANTES_CLE",
    "TAILLE_BLOC", "NOMBRE_TOURS",
    "MASQUE_A", "MASQUE_B", "MASQUE_C",
    "SEUILS", "STATUTS",
    "parite_masque", "appliquer_sbox", "sbox_inverse", "permuter",
    "diversifier", "chiffrer", "dechiffrer",
    "table_approximations", "piling_up",
    "compter_relation", "attaquer_quartet", "groupe_de_tete",
    "cle_candidates", "verifier_cles", "attaquer_cle",
    "biais_exact", "biais_mesure",
    "afficher_lat", "afficher_scores", "afficher_groupes",
    "intervalle_confiance", "z_score", "phi", "paires_pour_cle",
]

# ---------------------------------------------------------------------------
# 1. Constantes
# ---------------------------------------------------------------------------

#: Boîte S de PRESENT : SBOX[x] est l'image du quartet x (0 à 15).
SBOX = (
    0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
    0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2,
)

#: Table inverse : SBOX_INVERSE[y] est l'unique x tel que SBOX[x] = y.
SBOX_INVERSE = tuple(SBOX.index(y) for y in range(16))

#: Constantes de la diversification de clé.
CONSTANTES_CLE = (0x1B, 0x2D, 0x3F)

TAILLE_BLOC = 8
NOMBRE_TOURS = 3

#: Masques de la trace : 9 -> 2 -> 13.
MASQUE_A = 9
MASQUE_B = 2
MASQUE_C = 13

#: Seuils d'élargissement du groupe de tête, du plus strict au plus large.
SEUILS = (0.8, 0.6, 0.4)

#: Les quatre statuts possibles de `attaquer_cle`.
STATUTS = {
    "certaine": "clé unique trouvée au seuil strict (0,8)",
    "elargie": "clé unique trouvée après élargissement du groupe",
    "incertaine": "plusieurs clés survivent : impossible de conclure",
    "echec": "aucune clé ne vérifie les couples connus",
}


# ---------------------------------------------------------------------------
# 2. Primitives du chiffrement
# ---------------------------------------------------------------------------

def parite_masque(valeur: int, masque: int) -> int:
    """Parité (0 ou 1) des bits de `valeur` sélectionnés par `masque`.

    C'est le XOR des bits indiqués par le masque :

        parite_masque(0b1010, 0b1100) = 1
        parite_masque(0b1010, 0b0110) = 1
        parite_masque(0b1111, 0b1111) = 0

    En Python : `bin(valeur & masque).count("1") & 1`.
    """
    return bin(valeur & masque).count("1") & 1


def appliquer_sbox(x: int) -> int:
    """Applique S aux deux quartets du bloc `x`.

    Le quartet fort est `(x >> 4) & 0xF`, le faible `x & 0xF`.
    On recolle : `(S[fort] << 4) | S[faible]`.

    Exemple : appliquer_sbox(0x5A) = 0x0F.
    """
    return (SBOX[(x >> 4) & 0xF] << 4) | SBOX[x & 0xF]


def sbox_inverse(y: int) -> int:
    """Antécédent du quartet `y` par S (y est un quartet, pas un bloc).

    Exemple : sbox_inverse(0x0) = 5, car S[5] = 0.
    """
    return SBOX_INVERSE[y & 0xF]


def permuter(x: int) -> int:
    """Échange les deux quartets (couche linéaire P). P est son propre inverse.

    Exemple : permuter(0xAB) = 0xBA.
    """
    return ((x & 0xF) << 4) | ((x >> 4) & 0xF)


def diversifier(cle_maitre: int) -> tuple[int, int, int, int]:
    """Dérive (K0, K1, K2, K3) de la clé maître de 8 bits.

        K0 = M
        K1 = S(M)  ⊕ 0x1B
        K2 = S(K1) ⊕ 0x2D
        K3 = S(K2) ⊕ 0x3F

    Chaque étape est bijective, donc M -> K3 est une bijection : à une clé de
    dernier tour correspond exactement une clé maître.

    Exemple : diversifier(19) = (0x13, 0x40, 0xB1, 0xBA).
    """
    k0 = cle_maitre & 0xFF
    k1 = appliquer_sbox(k0) ^ CONSTANTES_CLE[0]
    k2 = appliquer_sbox(k1) ^ CONSTANTES_CLE[1]
    k3 = appliquer_sbox(k2) ^ CONSTANTES_CLE[2]
    return (k0, k1, k2, k3)


def chiffrer(bloc: int, cles: tuple[int, int, int, int]) -> int:
    """Chiffre un bloc de 8 bits avec (K0, K1, K2, K3).

        x = bloc ⊕ K0 ;  puis 3 fois : x = P(S(x)) ⊕ K_tour
    """
    x = bloc ^ cles[0]
    for tour in range(1, len(cles)):
        x = permuter(appliquer_sbox(x)) ^ cles[tour]
    return x & 0xFF


def dechiffrer(bloc: int, cles: tuple[int, int, int, int]) -> int:
    """Déchiffre un bloc (inverse de `chiffrer`)."""
    x = bloc & 0xFF
    for tour in range(len(cles) - 1, 0, -1):
        x = permuter(x ^ cles[tour])
        x = (SBOX_INVERSE[(x >> 4) & 0xF] << 4) | SBOX_INVERSE[x & 0xF]
    return (x ^ cles[0]) & 0xFF


# ---------------------------------------------------------------------------
# 3. LAT et piling-up
# ---------------------------------------------------------------------------

def table_approximations() -> list[list[int]]:
    """LAT de la boîte S : matrice 16 × 16.

        LAT[a][b] = #{x : parite(x,a) == parite(S[x],b)} - 8

    Donc `LAT[a][b] = 16 * delta = 8 * rho`.

    Propriétés : LAT[0][0] = 8 ; LAT[0][b] = LAT[a][0] = 0 sinon ; les
    valeurs sont paires, entre -8 et 8.

    Exemple : LAT[9][2] = -2, donc p = 6/16, delta = -1/8, rho = -1/4.
    """
    lat = []
    for a in range(16):
        ligne = []
        for b in range(16):
            solutions = sum(
                1 for x in range(16)
                if parite_masque(x, a) == parite_masque(SBOX[x], b)
            )
            ligne.append(solutions - 8)
        lat.append(ligne)
    return lat


def piling_up(lat1: int, lat2: int) -> float:
    """Probabilité prédite par le piling-up pour deux approximations.

        rho_piling = (lat1/8) * (lat2/8)
        p_piling   = 1/2 + rho_piling / 2

    Exemple : piling_up(-2, 4) = 0,4375.
    """
    rho = (lat1 / 8.0) * (lat2 / 8.0)
    return 0.5 + rho / 2.0


# ---------------------------------------------------------------------------
# 4. Attaque
# ---------------------------------------------------------------------------

def compter_relation(paires, masque_entree, masque_sortie, depart_haut, candidat):
    """Compte les couples où la relation de trace est vraie.

    `paires` : liste de (clair, chiffré).
    `depart_haut` : True si la trace part du quartet HAUT du clair.

    La trace couvre deux tours et s'arrête à l'ENTRÉE de la boîte S du
    troisième tour.  Ce quartet se calcule depuis le chiffré et un candidat
    pour un quartet de K3 :

      * depart_haut = False : quartet bas de x2, candidat = K3_haut
            x2_bas = S⁻¹( (C >> 4) & 0xF  ⊕  candidat )
      * depart_haut = True  : quartet haut de x2, candidat = K3_bas
            x2_haut = S⁻¹( (C & 0xF) ⊕  candidat )

    On compte alors :
        parite(quartet_du_clair, masque_entree)
            == parite(x2_quartet, masque_sortie)
    """
    total = 0
    for clair, chiffre in paires:
        if depart_haut:
            quartet_clair = (clair >> 4) & 0xF
            y = (chiffre & 0xF) ^ candidat
        else:
            quartet_clair = clair & 0xF
            y = ((chiffre >> 4) & 0xF) ^ candidat
        entree_sbox = SBOX_INVERSE[y & 0xF]
        if parite_masque(quartet_clair, masque_entree) == parite_masque(entree_sbox, masque_sortie):
            total += 1
    return total


def attaquer_quartet(paires, masque_entree, masque_sortie, depart_haut):
    """Classe les 16 candidats d'un quartet de K3.

    score = |2 * compte - N| ; 0 si le compte vaut N/2, N s'il vaut 0 ou N.

    ATTENTION : le score est une valeur ABSOLUE.  Il ne distingue pas un
    candidat à p = 0,25 d'un candidat à p = 0,75, et plusieurs candidats
    peuvent avoir exactement le même score.  Le premier n'est donc pas
    forcément le bon : c'est pourquoi on garde un GROUPE de tête.

    Renvoie la liste des (score, candidat) triée du meilleur au moins bon.
    """
    n = len(paires)
    scores = []
    for candidat in range(16):
        compte = compter_relation(paires, masque_entree, masque_sortie, depart_haut, candidat)
        scores.append((abs(2 * compte - n), candidat))
    scores.sort(reverse=True)
    return scores


def groupe_de_tete(scores, proportion: float = 0.8):
    """Candidats dont le score atteint `proportion` fois le meilleur score.

    Renvoie une liste triée.  Si tous les scores sont nuls, renvoie les 16
    candidats (on ne peut rien conclure).
    """
    if not scores:
        return []
    meilleur = scores[0][0]
    if meilleur == 0:
        return sorted(candidat for _, candidat in scores)
    return sorted(candidat for score, candidat in scores if score >= proportion * meilleur)


def cle_candidates(paires, proportion: float = 0.8):
    """Clés maîtres compatibles avec les groupes de tête des deux orientations.

    Renvoie `(candidats, groupe_haut, groupe_bas)`, où `candidats` est la
    liste triée des clés maîtres M telles que K3 = diversifier(M)[3] ait son
    quartet haut dans `groupe_haut` et son quartet bas dans `groupe_bas`.

    La diversification étant bijective, chaque couple de quartets compatibles
    correspond à une clé maître au plus : on ne teste que 256 clés.
    """
    scores_haut = attaquer_quartet(paires, MASQUE_A, MASQUE_C, False)
    scores_bas = attaquer_quartet(paires, MASQUE_A, MASQUE_C, True)
    groupe_haut = groupe_de_tete(scores_haut, proportion)
    groupe_bas = groupe_de_tete(scores_bas, proportion)

    candidats = []
    for cle_maitre in range(256):
        k3 = diversifier(cle_maitre)[3]
        if ((k3 >> 4) & 0xF) in groupe_haut and (k3 & 0xF) in groupe_bas:
            candidats.append(cle_maitre)
    return candidats, groupe_haut, groupe_bas


def verifier_cles(candidats, paires, nombre: int = 3):
    """Ne garde que les clés qui chiffrent correctement les `nombre` premiers clairs.

    C'est la vérification sur couples connus : elle ne coûte presque rien et
    élimine les clés compatibles avec les groupes mais fausses.
    """
    survivantes = []
    temoins = paires[:nombre]
    for cle_maitre in candidats:
        cles = diversifier(cle_maitre)
        if all(chiffrer(clair, cles) == chiffre for clair, chiffre in temoins):
            survivantes.append(cle_maitre)
    return survivantes


def attaquer_cle(paires, nombre_verifications: int = 3, seuils=SEUILS):
    """Attaque complète.  Renvoie `(cle, statut)`.

    Déroulé :

      1. pour chaque seuil, du plus strict (0,8) au plus large (0,4) :
           a. construire les groupes de tête des deux orientations ;
           b. en déduire les clés maîtres candidates ;
           c. les vérifier sur `nombre_verifications` couples connus ;
           d. si UNE seule clé survit, la renvoyer ;
      2. si le seuil strict a suffi : statut « certaine » ;
      3. si un seuil plus large a été nécessaire : statut « elargie » ;
      4. si plusieurs clés survivent au dernier seuil : « incertaine »
         (on renvoie None : l'attaque ne conclut pas) ;
      5. si aucune clé ne survit : « echec ».

    L'attaque ne bascule JAMAIS sur une recherche exhaustive des 256 clés :
    un échec est signalé comme un échec.  C'est une limite statistique
    assumée : sur un petit nombre de couples, le bruit peut faire sortir le
    bon quartet du groupe de tête, et aucune conclusion n'est alors possible.
    """
    derniers_survivants = []
    for indice, seuil in enumerate(seuils):
        candidats, _, _ = cle_candidates(paires, seuil)
        survivantes = verifier_cles(candidats, paires, nombre_verifications)
        derniers_survivants = survivantes
        if len(survivantes) == 1:
            statut = "certaine" if indice == 0 else "elargie"
            return survivantes[0], statut
    if len(derniers_survivants) > 1:
        return None, "incertaine"
    return None, "echec"


# ---------------------------------------------------------------------------
# 5. Les trois biais, mesurés explicitement
# ---------------------------------------------------------------------------

def biais_exact(cles, masque_entree=MASQUE_A, masque_sortie=MASQUE_C,
                depart_haut=False, candidat=None) -> float:
    """Biais EXACT de la trace pour une clé fixée, par énumération des 256 blocs.

    On ne peut faire cela que parce que le bloc fait 8 bits.  Sur un vrai
    chiffrement, on ne connaît jamais ce nombre : c'est précisément ce que
    l'attaquant cherche à estimer.

    `candidat` vaut par défaut le vrai quartet de K3.
    """
    k3 = cles[-1]
    if candidat is None:
        # depart_haut=False : la trace part du quartet bas et arrive sur le
        # quartet bas de x2, qui se calcule avec K3_HAUT.
        candidat = (k3 & 0xF) if depart_haut else ((k3 >> 4) & 0xF)
    paires = [(m, chiffrer(m, cles)) for m in range(256)]
    return compter_relation(paires, masque_entree, masque_sortie, depart_haut, candidat) / 256.0


def biais_mesure(paires, masque_entree=MASQUE_A, masque_sortie=MASQUE_C,
                 depart_haut=False, candidat=None) -> float:
    """Biais MESURÉ sur un échantillon de couples.

    Si `candidat` est None, on prend le candidat de tête de l'orientation
    demandée : c'est ce que fait un attaquant qui ne connaît pas la clé.
    """
    if candidat is None:
        candidat = attaquer_quartet(paires, masque_entree, masque_sortie, depart_haut)[0][1]
    return compter_relation(paires, masque_entree, masque_sortie, depart_haut, candidat) / len(paires)


# ---------------------------------------------------------------------------
# 6. Statistiques
# ---------------------------------------------------------------------------

def intervalle_confiance(p: float, n: int, z: float = 1.96):
    """Intervalle de confiance approché à 95 % pour une proportion."""
    if n <= 0:
        return (0.0, 1.0)
    marge = z * math.sqrt(max(p * (1.0 - p), 0.0) / n)
    return (max(0.0, p - marge), min(1.0, p + marge))


def z_score(p: float, n: int) -> float:
    """Écart au hasard, en écarts-types : rho * sqrt(N) = (2p - 1) * sqrt(N)."""
    if n <= 0:
        return 0.0
    return (2.0 * p - 1.0) * math.sqrt(n)


def phi(x: float) -> float:
    """Fonction de répartition de la loi normale centrée réduite."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# ---------------------------------------------------------------------------
# 7. Affichage
# ---------------------------------------------------------------------------

def afficher_lat(lat) -> None:
    """Affiche une LAT 16 × 16 (zéros en points, hexadécimal en en-tête)."""
    entete = "       " + " ".join(f"{b:X}" for b in range(16))
    print(entete)
    print("      " + "-" * (len(entete) - 6))
    for a in range(16):
        cases = []
        for b in range(16):
            valeur = lat[a][b]
            if valeur == 0:
                cases.append(" .")
            elif valeur > 0:
                cases.append(f"+{valeur}")
            else:
                cases.append(f"{valeur}")
        print(f"  {a:X} | " + " ".join(f"{case:>2}" for case in cases))


def afficher_scores(scores, n: int | None = None) -> None:
    """Affiche une liste (score, candidat) en barres.

    `n` est le nombre de couples ; s'il est fourni, on rappelle que le score
    vaut |2 × compte − n|, donc qu'il ne donne pas le SIGNE du biais.
    """
    maximum = max((score for score, _ in scores), default=0) or 1
    for score, candidat in scores:
        longueur = int(40 * score / maximum)
        print(f"  candidat {candidat:2d} (0x{candidat:X}) : {score:5d}  " + "#" * longueur)


def afficher_groupes(nom, scores, groupes, n: int | None = None) -> None:
    """Affiche un classement et met les candidats du groupe entre crochets."""
    print(f"  {nom} : groupe de tête = {groupes}")
    for score, candidat in scores[:6]:
        marque = "<<" if candidat in groupes else "  "
        longueur = int(30 * score / (scores[0][0] or 1))
        print(f"    {marque} 0x{candidat:X} : {score:5d}  " + "#" * longueur)


# ---------------------------------------------------------------------------
# 8. Utilitaire (générateur et expériences)
# ---------------------------------------------------------------------------

def paires_pour_cle(cle_maitre: int, nombre: int, graine: int):
    """`nombre` couples (clair, chiffré) pour une clé maître, tirage reproductible.

    ATTENTION : un bloc ne fait que 8 bits, donc il n'existe que 256 clairs
    possibles.  Un tirage de 2000 couples contient forcément des répétitions :
    c'est normal, et c'est le cas dans une vraie attaque à clair connu, où
    l'attaquant collecte ce qu'il peut.
    """
    generateur = random.Random(graine)
    cles = diversifier(cle_maitre)
    return [(clair, chiffrer(clair, cles))
            for clair in (generateur.randrange(256) for _ in range(nombre))]


# ---------------------------------------------------------------------------
# 9. Autocontrôle (professeur) : python3 outils/lineaire.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Autocontrôle du module outils/lineaire.py")
    print("----------------------------------------")
    cles = diversifier(19)
    print("diversifier(19) =", tuple(f"0x{c:02X}" for c in cles))
    lat = table_approximations()
    print(f"LAT[9][2] = {lat[9][2]}   LAT[2][13] = {lat[2][13]}")
    print(f"piling-up     : p = {piling_up(lat[9][2], lat[2][13]):.4f}")
    print(f"biais exact   : bas {biais_exact(cles, depart_haut=False):.4f}, "
          f"haut {biais_exact(cles, depart_haut=True):.4f}")
    paires = paires_pour_cle(19, 2000, 20261022)
    cle, statut = attaquer_cle(paires)
    print(f"attaque       : clé = {cle}, statut = {statut}")
    k3 = cles[3]
    for depart, vrai in ((False, (k3 >> 4) & 0xF), (True, k3 & 0xF)):
        p = biais_mesure(paires, depart_haut=depart, candidat=vrai)
        print(f"biais mesuré  : depart_haut={depart} p = {p:.4f}")
