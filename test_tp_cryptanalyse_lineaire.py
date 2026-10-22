"""==========================================================================
 ÉPREUVES AUTOMATIQUES — CRYPTANALYSE LINÉAIRE  (ne pas modifier ce fichier)
==========================================================================
Pour vérifier votre travail, tapez dans un terminal, dans ce dossier :

    python3 test_tp_cryptanalyse_lineaire.py

Chaque épreuve réussie s'affiche « [OK] », chaque épreuve ratée « [ÉCHEC] »
avec l'explication.

Les épreuves de la partie D sont celles de la CRYPTANALYSE : elles vérifient
que votre attaque retrouve bien la clé du jeu de données, puis RECHIFFRENT
les 2 000 couples avec la clé trouvée.  Le fichier ne contient que des
EMPREINTES (SHA-256) des réponses : vous ne pouvez pas tricher en le lisant.

Deux épreuves (D.7) vérifient les LIMITES de l'attaque : sur un très petit
échantillon, l'attaque doit signaler « elargie » ou « echec » — et surtout
ne pas inventer une clé.
==========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.verif import charger_module, empreinte, epreuve, lancer  # noqa: E402

tp = charger_module("tp_cryptanalyse_lineaire")

from donnees_lineaire import PAIRES  # noqa: E402
from outils.lineaire import (  # noqa: E402
    SBOX,
    MASQUE_A,
    MASQUE_C,
    attaquer_quartet as attaquer_quartet_reference,
    biais_exact,
    chiffrer as chiffrer_reference,
    cle_candidates as cle_candidates_reference,
    compter_relation as compter_relation_reference,
    diversifier as diversifier_reference,
    piling_up,
    table_approximations as table_approximations_reference,
)

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_donnees_lineaire.py) ---
EMPREINTES = {
    "cle_maitre": "9400f1b21cb527d7fa3d3eabba93557a18ebe7a2ca4e471cfe5e4c5b4ca7f767",
    "groupe_haut": "45054b927a8755f151e50b491b368c9a6bff3de53b63dc678de51f8fa593a3bb",
    "groupe_bas": "41164c427f4cf681cc1b50eaf1a175e3574a1d015c6c90fbdaf77aea39d24086",
    "candidats": "8c5efac17d5baf4424bbaa427b665fb4f4b5917c7e6bdb688eeace9b2332d8f4",
    "donnees": "e5cc56e44bfaf22087078d644e01effafd23c66f1836e862bdda2d1216d7ecfc",
}
# --- FIN DE LA ZONE GÉNÉRÉE ---


def _empreintes_disponibles():
    return bool(EMPREINTES)


def _verifier_empreinte(nom, valeur):
    """Compare `valeur` à l'empreinte du professeur, avec un message clair."""
    assert _empreintes_disponibles(), (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_donnees_lineaire.py » (réservé au professeur)"
    )
    obtenu = empreinte(valeur)
    assert obtenu == EMPREINTES[nom], (
        f"la valeur trouvée est fausse.\n"
        f"  vous proposez : {valeur!r}\n"
        f"  Vérifiez l'orientation : la trace BASSE (depart_haut=False) sert à "
        f"retrouver K3_HAUT, et la trace HAUTE (depart_haut=True) sert à "
        f"retrouver K3_BAS.\n"
        f"  Vérifiez aussi que vous n'avez pas inversé les quartets du chiffré."
    )


# ---------------------------------------------------------------------------
# § B — la boîte S et la LAT
# ---------------------------------------------------------------------------

@epreuve("B.1", "parite_masque")
def test_parite_masque():
    assert tp.parite_masque(0b1010, 0b1100) == 1, (
        "parite_masque(0b1010, 0b1100) doit valoir 1 : "
        "0b1010 & 0b1100 = 0b1000, qui a un seul bit à 1."
    )
    assert tp.parite_masque(0b1010, 0b0110) == 1, (
        "parite_masque(0b1010, 0b0110) doit valoir 1 : "
        "0b1010 & 0b0110 = 0b0010."
    )
    assert tp.parite_masque(0b1111, 0b1111) == 0, (
        "parite_masque(0b1111, 0b1111) doit valoir 0 : quatre bits à 1, "
        "donc une parité paire."
    )
    assert tp.parite_masque(0, 0b1011) == 0, (
        "parite_masque(0, ...) doit valoir 0 : aucun bit à 1."
    )
    # La parité masquée est bien le XOR des bits sélectionnés.
    for valeur in range(256):
        attendu = bin(valeur & 0b1001).count("1") % 2
        assert tp.parite_masque(valeur, 0b1001) == attendu, (
            f"parite_masque({valeur}, 0b1001) est faux : "
            f"attendu {attendu}, obtenu {tp.parite_masque(valeur, 0b1001)}."
        )


@epreuve("B.2", "appliquer_sbox")
def test_appliquer_sbox():
    assert tp.appliquer_sbox(0x00) == 0xCC, (
        "appliquer_sbox(0x00) doit valoir 0xCC : S[0] = 0xC pour les deux "
        "quartets."
    )
    assert tp.appliquer_sbox(0x5A) == 0x0F, (
        "appliquer_sbox(0x5A) doit valoir 0x0F : S[5] = 0x0 et S[0xA] = 0xF.\n"
        "  Le quartet FORT se traite avec (x >> 4) & 0xF, le faible avec x & 0xF."
    )
    for bloc in range(256):
        attendu = (SBOX[(bloc >> 4) & 0xF] << 4) | SBOX[bloc & 0xF]
        assert tp.appliquer_sbox(bloc) == attendu, (
            f"appliquer_sbox(0x{bloc:02X}) est faux : attendu 0x{attendu:02X}, "
            f"obtenu {tp.appliquer_sbox(bloc)!r}."
        )


@epreuve("B.3", "sbox_inverse")
def test_sbox_inverse():
    assert tp.sbox_inverse(0x0) == 5, (
        "sbox_inverse(0x0) doit valoir 5 : SBOX[5] = 0."
    )
    for y in range(16):
        x = tp.sbox_inverse(y)
        assert 0 <= x < 16, f"sbox_inverse({y}) doit renvoyer un quartet, pas {x!r}."
        assert SBOX[x] == y, (
            f"sbox_inverse({y}) a renvoyé {x}, mais SBOX[{x}] = {SBOX[x]} ≠ {y}.\n"
            f"  Utilise SBOX.index(y) : S est une permutation, donc l'antécédent "
            f"est unique."
        )


@epreuve("B.4", "table_approximations")
def test_table_approximations():
    lat = tp.table_approximations()
    assert isinstance(lat, list) and len(lat) == 16, (
        "la LAT doit être une liste de 16 lignes."
    )
    assert all(len(ligne) == 16 for ligne in lat), (
        "chaque ligne de la LAT doit avoir 16 cases."
    )
    assert lat[0][0] == 8, (
        "LAT[0][0] doit valoir 8 : le masque nul est toujours satisfait "
        "(16 solutions, moins 8)."
    )
    assert all(lat[0][b] == 0 for b in range(1, 16)), (
        "LAT[0][b] doit valoir 0 pour b ≠ 0 : un masque de sortie non nul "
        "sur une entrée non contrainte est équilibré."
    )
    assert all(lat[a][0] == 0 for a in range(1, 16)), (
        "LAT[a][0] doit valoir 0 pour a ≠ 0."
    )
    reference = table_approximations_reference()
    assert lat == reference, (
        "la LAT ne correspond pas à celle de la boîte S.\n"
        "  Vérifie que tu compares bien parite_masque(x, a) avec "
        "parite_masque(SBOX[x], b), puis que tu retranches 8."
    )


@epreuve("B.5", "les approximations de la trace")
def test_lat_trace():
    lat = tp.table_approximations()
    assert lat[9][2] == -2, (
        f"LAT[9][2] doit valoir -2 (6 solutions sur 16), obtenu {lat[9][2]}.\n"
        f"  p = 6/16, delta = -1/8, rho = -1/4."
    )
    assert lat[2][13] == 4, (
        f"LAT[2][13] doit valoir +4 (12 solutions sur 16), obtenu {lat[2][13]}.\n"
        f"  p = 12/16, delta = +1/4, rho = +1/2."
    )
    maximum = max(abs(lat[a][b]) for a in range(16) for b in range(16) if (a, b) != (0, 0))
    assert maximum == 4, (
        f"le plus grand biais hors (0,0) doit valoir 4 en valeur absolue, "
        f"obtenu {maximum}."
    )
    assert all(lat[a][b] % 2 == 0 for a in range(16) for b in range(16)), (
        "toutes les cases de la LAT doivent être paires : le nombre de "
        "solutions est 8 + LAT[a][b], et 8 est pair."
    )


# ---------------------------------------------------------------------------
# § C — le mini-chiffre
# ---------------------------------------------------------------------------

@epreuve("C.1", "permuter")
def test_permuter():
    assert tp.permuter(0xAB) == 0xBA, (
        "permuter(0xAB) doit valoir 0xBA : les deux quartets s'échangent."
    )
    for bloc in range(256):
        attendu = ((bloc & 0xF) << 4) | ((bloc >> 4) & 0xF)
        assert tp.permuter(bloc) == attendu, (
            f"permuter(0x{bloc:02X}) est faux : attendu 0x{attendu:02X}."
        )
        assert tp.permuter(tp.permuter(bloc)) == bloc, (
            "P doit être son propre inverse : permuter(permuter(x)) == x."
        )


@epreuve("C.2", "chiffrer (vecteurs de test)")
def test_chiffrer_vecteurs():
    assert tp.chiffrer(0x00, (0, 0, 0, 0)) == 0x99, (
        "chiffrer(0x00, (0, 0, 0, 0)) doit valoir 0x99.\n"
        "  Déroulé : S(00) = CC, P(CC) = CC, S(CC) = 44, P(44) = 44, "
        "S(44) = 99, P(99) = 99."
    )
    assert tp.chiffrer(0xAB, (0x12, 0x34, 0x56, 0x78)) == 0x2D, (
        "chiffrer(0xAB, (0x12, 0x34, 0x56, 0x78)) doit valoir 0x2D."
    )
    for cles in ((0, 0, 0, 0), (0x12, 0x34, 0x56, 0x78), diversifier_reference(19)):
        for bloc in range(256):
            attendu = chiffrer_reference(bloc, cles)
            assert tp.chiffrer(bloc, cles) == attendu, (
                f"chiffrer(0x{bloc:02X}, {tuple(hex(k) for k in cles)}) est faux : "
                f"attendu 0x{attendu:02X}, obtenu {tp.chiffrer(bloc, cles)!r}.\n"
                f"  Vérifie l'ordre : XOR de K0, puis (S, P, XOR) trois fois."
            )


@epreuve("C.3", "chiffrer (déterminisme et sensibilité à la clé)")
def test_chiffrer_sensibilite():
    cles = diversifier_reference(19)
    assert tp.chiffrer(0x5A, cles) == tp.chiffrer(0x5A, cles), (
        "le chiffrement doit être déterministe."
    )
    k3_modifiee = cles[3] ^ 0x01
    cles_modifiees = (cles[0], cles[1], cles[2], k3_modifiee)
    differents = sum(
        1 for bloc in range(256)
        if tp.chiffrer(bloc, cles) != tp.chiffrer(bloc, cles_modifiees)
    )
    assert differents == 256, (
        f"changer un bit de K3 doit changer les 256 chiffrés, "
        f"obtenu {differents}/256 : la clé du dernier tour est-elle bien "
        f"utilisée ?"
    )


# ---------------------------------------------------------------------------
# § D — l'attaque
# ---------------------------------------------------------------------------

@epreuve("D.1", "compter_relation")
def test_compter_relation():
    echantillon = PAIRES[:100]
    for depart_haut in (False, True):
        for candidat in range(16):
            attendu = compter_relation_reference(
                echantillon, MASQUE_A, MASQUE_C, depart_haut, candidat)
            obtenu = tp.compter_relation(
                echantillon, MASQUE_A, MASQUE_C, depart_haut, candidat)
            assert obtenu == attendu, (
                f"compter_relation(..., depart_haut={depart_haut}, "
                f"candidat={candidat}) vaut {obtenu}, attendu {attendu}.\n"
                f"  Rappel : depart_haut=False -> quartet bas du clair et "
                f"quartet HAUT du chiffré (candidat = K3_HAUT).\n"
                f"  depart_haut=True -> quartet haut du clair et quartet BAS "
                f"du chiffre (candidat = K3_BAS)."
            )
    # Le vrai candidat de la trace basse produit bien un biais net.
    compte = tp.compter_relation(PAIRES, MASQUE_A, MASQUE_C, False, 0xB)
    p = compte / len(PAIRES)
    assert abs(p - 0.5) > 0.2, (
        f"avec le vrai candidat (0xB), le biais mesuré devrait être fort "
        f"(environ 0,25) ; obtenu p = {p:.4f}."
    )


@epreuve("D.2", "attaquer_quartet")
def test_attaquer_quartet():
    for depart_haut in (False, True):
        scores = tp.attaquer_quartet(PAIRES, MASQUE_A, MASQUE_C, depart_haut)
        assert isinstance(scores, list) and len(scores) == 16, (
            "attaquer_quartet doit renvoyer une liste de 16 couples "
            "(score, candidat)."
        )
        assert sorted(candidat for _, candidat in scores) == list(range(16)), (
            "les 16 candidats doivent apparaître une fois chacun."
        )
        assert all(scores[i][0] >= scores[i + 1][0] for i in range(15)), (
            "la liste doit être triée du plus grand score au plus petit."
        )
        attendu = attaquer_quartet_reference(PAIRES, MASQUE_A, MASQUE_C, depart_haut)
        assert scores == attendu, (
            "les scores ne correspondent pas.\n"
            "  score = |2 × compte − N|, et N = len(paires).\n"
            f"  Pour depart_haut={depart_haut}, les 3 premiers attendus sont "
            f"{attendu[:3]}."
        )


@epreuve("D.3", "groupe_de_tete")
def test_groupe_de_tete():
    # depart_haut=False -> trace basse -> candidats pour K3_HAUT
    # depart_haut=True  -> trace haute -> candidats pour K3_BAS
    scores_pour_k3_haut = attaquer_quartet_reference(PAIRES, MASQUE_A, MASQUE_C, False)
    scores_pour_k3_bas = attaquer_quartet_reference(PAIRES, MASQUE_A, MASQUE_C, True)

    groupe_haut = tp.groupe_de_tete(scores_pour_k3_haut)
    groupe_bas = tp.groupe_de_tete(scores_pour_k3_bas)
    assert isinstance(groupe_bas, list), (
        "groupe_de_tete doit renvoyer une liste triée, pas un ensemble."
    )
    _verifier_empreinte("groupe_haut", groupe_haut)
    _verifier_empreinte("groupe_bas", groupe_bas)

    assert tp.groupe_de_tete([]) == [], (
        "une liste de scores vide doit donner une liste vide."
    )
    scores_nuls = [(0, candidat) for candidat in range(16)]
    assert tp.groupe_de_tete(scores_nuls) == list(range(16)), (
        "si tous les scores sont nuls, aucun candidat ne se détache : il faut "
        "renvoyer les 16."
    )


@epreuve("D.4", "cle_candidates")
def test_cle_candidates():
    candidats, groupe_haut, groupe_bas = tp.cle_candidates(PAIRES)
    attendus, gh_ref, gb_ref = cle_candidates_reference(PAIRES)
    assert groupe_haut == gh_ref and groupe_bas == gb_ref, (
        "les groupes de tête ne correspondent pas à ceux de D.3.\n"
        f"  attendu : groupe_haut={gh_ref}, groupe_bas={gb_ref}\n"
        f"  obtenu  : groupe_haut={groupe_haut}, groupe_bas={groupe_bas}"
    )
    assert candidats == attendus, (
        f"les clés candidates sont fausses : attendu {attendus}, "
        f"obtenu {candidats}.\n"
        f"  La diversification M -> K3 est une bijection : pour chaque M de "
        f"0 à 255, compare les deux quartets de K3 aux groupes."
    )
    _verifier_empreinte("candidats", candidats)


@epreuve("D.5", "verifier_cles")
def test_verifier_cles():
    candidats = cle_candidates_reference(PAIRES)[0]
    survivantes = tp.verifier_cles(candidats, PAIRES, 3)
    assert survivantes == [19], (
        f"après vérification sur 3 couples, il doit rester exactement la clé "
        f"19 ; obtenu {survivantes}.\n"
        f"  Vérifie que tu rechiffres bien le CLAIR de chaque couple, et que "
        f"tu le compares au CHIFFRÉ."
    )
    # Vérifier avec un couple suffit déjà sur ce jeu de données.
    assert tp.verifier_cles(candidats, PAIRES, 1) == [19], (
        "même avec un seul couple de vérification, la clé 19 doit rester "
        "seule : les autres candidates ne rechiffrent pas ce clair."
    )


@epreuve("D.6", "attaquer_cle")
def test_attaquer_cle():
    cle, statut = tp.attaquer_cle(PAIRES)
    assert statut == "certaine", (
        f"avec 2 000 couples, l'attaque doit être certaine (seuil 0,8 "
        f"suffit) ; statut obtenu : {statut!r}.\n"
        f"  Statuts possibles : 'certaine', 'elargie', 'incertaine', 'echec'."
    )
    assert cle is not None, "une attaque certaine doit renvoyer une clé."
    _verifier_empreinte("cle_maitre", cle)
    # Critère du cryptanalyste : la clé doit rechiffrer TOUS les couples.
    cles = diversifier_reference(cle)
    faux = [
        (clair, chiffre) for clair, chiffre in PAIRES
        if chiffrer_reference(clair, cles) != chiffre
    ]
    assert not faux, (
        f"la clé {cle} ne rechiffre pas les 2 000 couples : "
        f"{len(faux)} échec(s), par exemple {faux[:3]}."
    )


@epreuve("D.7", "limites de l'attaque (échantillon trop petit)")
def test_limites():
    cle, statut = tp.attaquer_cle(PAIRES[:10])
    assert statut == "elargie", (
        f"sur les 10 premiers couples, le seuil 0,8 ne suffit pas : "
        f"l'attaque doit élargir et signaler 'elargie' ; statut obtenu "
        f"{statut!r}."
    )
    assert cle == 19, "après élargissement, la clé trouvée doit être 19."
    cle, statut = tp.attaquer_cle(PAIRES[60:70])
    assert statut == "echec", (
        f"sur les couples 60 à 70, aucune clé ne peut être vérifiée : "
        f"l'attaque doit signaler 'echec' ; statut obtenu {statut!r}.\n"
        f"  Un échec n'est PAS un bug : c'est la limite statistique de "
        f"l'attaque sur un échantillon trop petit."
    )
    assert cle is None, (
        "en cas d'échec, l'attaque ne doit renvoyer AUCUNE clé : il ne faut "
        "pas masquer l'échec par une recherche exhaustive."
    )


@epreuve("D.8", "biais mesuré, biais exact et piling-up")
def test_biais():
    cles = diversifier_reference(19)
    for depart_haut in (False, True):
        p_exact = biais_exact(cles, depart_haut=depart_haut)
        candidat = (cles[3] & 0xF) if depart_haut else ((cles[3] >> 4) & 0xF)
        p_mesure = tp.compter_relation(
            PAIRES, MASQUE_A, MASQUE_C, depart_haut, candidat) / len(PAIRES)
        bas, haut = (p_exact - 0.03, p_exact + 0.03)
        assert bas <= p_mesure <= haut, (
            f"le biais mesuré ({p_mesure:.4f}) devrait être proche du biais "
            f"exact ({p_exact:.4f}) : l'échantillon de 2 000 couples est "
            f"largement suffisant pour cet écart de 0,03."
        )
    p_exact_bas = biais_exact(cles, depart_haut=False)
    p_piling = piling_up(-2, 4)
    assert abs(p_exact_bas - p_piling) > 0.1, (
        "le biais exact et le piling-up doivent être nettement différents "
        "sur ce chiffre : c'est le sujet de l'expérience 2.\n"
        "  piling-up : 0,4375 ; biais exact de la trace basse : 0,25."
    )


if __name__ == "__main__":
    lancer()
