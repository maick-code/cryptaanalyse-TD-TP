"""==========================================================================
 ÉPREUVES AUTOMATIQUES DU TP 3  (ne pas modifier ce fichier)
==========================================================================
    python3 test_tp3_vigenere_vic.py
==========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.verif import charger_module, empreinte, epreuve, lancer  # noqa: E402

tp = charger_module("tp3_vigenere_vic")

from outils.reference import (  # noqa: E402
    PERMUTATION_VIC,
    TABLEAU_VIC,
    vic_chiffrer,
    vigenere_chiffrer as chiffrer_reference,
)

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
EMPREINTES = {
    "vigenere1": {
        "longueur": 620,
        "texte": "6e9788b7a06f5e9f4947c322ab403797265efe913369e7f07edeca2c33778ac3",
        "cle": "9122217c16ac79733338b07428c95b67ee7240a4d69f6580d14a7c6505fef172",
        "periode": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
    },
    "vigenere2": {
        "longueur": 700,
        "texte": "8e2c8c45afaa1e3f869a4bb33e5d9e1a850a959aad0e5bb145710e7ab961597a",
        "cle": "269dc135897f427830329acc2c45b49557050472c6d4e7246ec6d90e51ad301f",
        "periode": "7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451",
    },
    "vic": {
        "longueur": 80,
        "texte": "46c49bb04aba374ed308c86c531c2ade68d6f1b40c58a16d87808067ed8d9f3d",
        "cle": "b2a2f01fd91682e4f012509566bc45c88c6cfa43171b6d7d16cff44572ebf57b",
    },
}
# --- FIN DE LA ZONE GÉNÉRÉE ---

# Long texte français (595 lettres) servant à fabriquer des messages chiffrés
# d'essai dont on connaît la période.
TEXTE_LONG = (
    "LE MESSAGE ARRIVE CE SOIR A DIX HEURES DEVANT LA PORTE DU JARDIN PRES DE "
    "LA FONTAINE. LES ENFANTS JOUENT DANS LA COUR DE L ECOLE ET LE MAITRE "
    "FERME LES VOLETS. DEMAIN MATIN NOUS PARTIRONS AVANT LE LEVER DU SOLEIL "
    "POUR ARRIVER A LA RIVIERE AU MILIEU DE LA JOURNEE. LE BATEAU ATTENDRA "
    "SUR LA BERGE AVEC LES PECHEURS ET LEURS FILETS. CHACUN A PREPARE SON "
    "BAGAGE ET SES PROVISIONS POUR LE VOYAGE."
    "LE COURRIER ARRIVE DEUX FOIS PAR SEMAINE PAR LE BATEAU DE LA POSTE IL "
    "APPORTAIT LES LETTRES DE LA FAMILLE ET LES JOURNAUX DE LA CAPITALE. LE "
    "FACTEUR DU QUARTIER CONNAISSAIT TOUT LE MONDE ET LISAIT LES ADRESSES A "
    "VOIX HAUTE DEVANT LA PORTE. LES ENFANTS SE RASSEMBLENT AUTOUR DE LUI "
    "POUR ENTENDRE LES NOUVELLES DU PAYS ET LES HISTOIRES ANCIENNES."
)
TEXTE_LONG = "".join(c for c in TEXTE_LONG.upper() if "A" <= c <= "Z")


def _colonnes_de_reference(texte, periode):
    """Découpage en colonnes, écrit ici pour ne pas dépendre du code testé."""
    morceaux = ["" for _ in range(periode)]
    for position, caractere in enumerate(texte):
        morceaux[position % periode] += caractere
    return morceaux


def _retrouver_message(message, empreintes):
    """Essaie toutes les périodes de 2 à 15 (les épreuves C.3 et C.4)."""
    for periode in range(2, 16):
        try:
            cle, clair = tp.forcer_vigenere(message, periode)
        except Exception:  # noqa: BLE001 - on essaie simplement la suivante
            continue
        if empreinte(cle) == empreintes["cle"]:
            return periode, cle, clair
    return None, None, None


# ==========================================================================
# PARTIE A — la période
# ==========================================================================

@epreuve("A.1", "indice_coincidence_moyen()")
def test_indice_coincidence_moyen():
    # Cas simples et exacts
    assert tp.indice_coincidence_moyen("ABAB", 2) == 1.0, (
        'dans "ABAB" avec 2 colonnes, chaque colonne ne contient qu\'une seule '
        'lettre répétée ("AA" et "BB"), donc l\'indice vaut 1 pour chacune et '
        "la moyenne vaut 1 ; votre fonction renvoie "
        f"{tp.indice_coincidence_moyen('ABAB', 2)}"
    )
    assert tp.indice_coincidence_moyen("ABCD", 1) == 0.0, (
        "une colonne d'une seule lettre a un indice nul"
    )

    # Cas réel : message chiffré par Vigenère avec la clef CLEF (période 4)
    chiffre = chiffrer_reference(TEXTE_LONG, "CLEF")
    indice_4 = tp.indice_coincidence_moyen(chiffre, 4)
    indice_3 = tp.indice_coincidence_moyen(chiffre, 3)
    assert indice_4 > 0.07, (
        "avec la bonne période (4) l'indice moyen doit être proche de celui du "
        f"français (environ 0,075) ; votre fonction trouve {indice_4:.4f}"
    )
    assert indice_3 < 0.06, (
        "avec une mauvaise période, l'indice moyen retombe vers 0,04 ; pour la "
        f"période 3 votre fonction trouve {indice_3:.4f}"
    )


@epreuve("A.2", "indices_par_periode()")
def test_indices_par_periode():
    chiffre = chiffrer_reference(TEXTE_LONG, "CLEF")
    resultat = tp.indices_par_periode(chiffre, 10)
    assert set(resultat) == set(range(1, 11)), (
        "le dictionnaire doit contenir une entrée pour chaque période de 1 à "
        f"maximum ; on obtient les clefs {sorted(resultat)}"
    )
    assert resultat[4] > resultat[3] and resultat[4] > resultat[5], (
        "la période 4 doit avoir un indice nettement plus grand que ses "
        f"voisines : 3 -> {resultat[3]:.4f}, 4 -> {resultat[4]:.4f}, "
        f"5 -> {resultat[5]:.4f}"
    )
    assert resultat[8] > resultat[7] and resultat[8] > resultat[9], (
        "les multiples de la période (8 est un multiple de 4) donnent eux aussi "
        f"un indice élevé : 8 -> {resultat[8]:.4f}"
    )


@epreuve("A.3", "periode_probable()")
def test_periode_probable():
    for cle in ("CLEF", "MONDE", "SECRET", "MYSTERE"):
        chiffre = chiffrer_reference(TEXTE_LONG, cle)
        resultat = tp.periode_probable(chiffre)
        assert resultat == len(cle), (
            f"ce message a été chiffré avec la clef {cle!r}, de période "
            f"{len(cle)} ; votre fonction propose {resultat}.\n"
            "  Pensez à prendre la plus PETITE période qui atteint 90 % du "
            "meilleur indice (les multiples marchent aussi : 8 et 12 pour une "
            "vraie période de 4)."
        )

    # Les deux messages interceptés : on vérifie la période par son empreinte.
    for nom in ("vigenere1", "vigenere2"):
        attendu = EMPREINTES[nom]
        assert attendu["periode"], (
            "les empreintes n'ont pas été générées : lancez "
            "« python3 outils/generer_messages.py » (réservé au professeur)"
        )
        message = getattr(tp, "MESSAGE_1" if nom == "vigenere1" else "MESSAGE_2")
        resultat = tp.periode_probable(message)
        assert empreinte(resultat) == attendu["periode"], (
            f"la période trouvée pour {message[:25]}... est {resultat}, ce n'est "
            "pas la bonne.\n  Regardez le tableau des indices (A.2) : les "
            "bonnes périodes ressortent très nettement (autour de 0,075), les "
            "mauvaises restent vers 0,045 (et les multiples de la bonne période "
            "ressortent aussi)."
        )


# ==========================================================================
# PARTIE B — Kasiski
# ==========================================================================

@epreuve("B.1", "grammes_repetes()")
def test_grammes_repetes():
    for chiffre, taille, attendu in [
        ("ABCIABCXABC", 3, ["ABC"]),
        ("XABCXABCXABC", 3, ["ABC", "BCX", "CXA", "XAB"]),
        ("ABCDEF", 3, []),
        ("ABCDABCD", 4, ["ABCD"]),
    ]:
        resultat = tp.grammes_repetes(chiffre, taille)
        assert list(resultat) == attendu, (
            f"grammes_repetes({chiffre!r}, {taille}) : attendu {attendu}, "
            f"obtenu {list(resultat)}"
        )


@epreuve("B.2", "kasiski_distances()")
def test_kasiski_distances():
    for chiffre, mot, attendu in [
        ("ABCXABCXXXABC", "ABC", [4, 6]),
        ("ABABAB", "AB", [2]),
        ("AAAA", "AA", [1]),
        ("ABCDE", "ZZ", []),
        ("ABCDEF", "ABC", []),
    ]:
        resultat = tp.kasiski_distances(chiffre, mot)
        assert list(resultat) == attendu, (
            f"kasiski_distances({chiffre!r}, {mot!r}) : attendu {attendu}, "
            f"obtenu {list(resultat)}"
        )


@epreuve("B.3", "diviseurs()")
def test_diviseurs():
    for nombre, attendu in [
        (12, [1, 2, 3, 4, 6, 12]),
        (7, [1, 7]),
        (1, [1]),
        (36, [1, 2, 3, 4, 6, 9, 12, 18, 36]),
    ]:
        resultat = tp.diviseurs(nombre)
        assert list(resultat) == attendu, (
            f"diviseurs({nombre}) : attendu {attendu}, obtenu {list(resultat)}"
        )


# ==========================================================================
# PARTIE C — casser les messages
# ==========================================================================

@epreuve("C.1", "forcer_cesar_sur_colonne()")
def test_forcer_cesar_sur_colonne():
    cle = "SECRET"
    chiffre = chiffrer_reference(TEXTE_LONG, cle)
    morceaux = _colonnes_de_reference(chiffre, len(cle))
    for numero, morceau in enumerate(morceaux):
        attendu = ord(cle[numero]) - ord("A")
        resultat = tp.forcer_cesar_sur_colonne(morceau)
        assert resultat == attendu, (
            f"la colonne {numero} a été décalée de {attendu} (lettre de clef "
            f"{cle[numero]!r}) ; votre fonction propose {resultat}.\n"
            f"  colonne : {morceau[:50]}..."
        )


@epreuve("C.2", "forcer_vigenere()")
def test_forcer_vigenere():
    for cle in ("CLEF", "MONDE", "SECRET"):
        chiffre = chiffrer_reference(TEXTE_LONG, cle)
        resultat = tp.forcer_vigenere(chiffre, len(cle))
        cle_trouvee, clair_trouve = resultat
        assert cle_trouvee == cle, (
            f"message chiffré avec {cle!r} : votre fonction propose "
            f"{cle_trouvee!r}.\n  texte chiffré : {chiffre[:70]}..."
        )
        assert clair_trouve[:len(TEXTE_LONG)] == TEXTE_LONG, (
            f"la clef {cle} est trouvée, mais le texte déchiffré ne convient "
            f"pas :\n  attendu : {TEXTE_LONG[:70]}...\n"
            f"  obtenu  : {clair_trouve[:70]}..."
        )


@epreuve("C.3", "le premier message intercepté est déchiffré")
def test_message_1():
    attendu = EMPREINTES["vigenere1"]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )
    periode, cle, clair = _retrouver_message(tp.MESSAGE_1, attendu)
    assert periode is not None, (
        "aucune période essayée (de 2 à 15) ne donne la bonne clef pour "
        "MESSAGE_1.\n  Vérifiez d'abord forcer_cesar_sur_colonne (C.1) et "
        "forcer_vigenere (C.2) sur les messages d'essai."
    )
    assert empreinte(clair[:attendu["longueur"]]) == attendu["texte"], (
        f"la clef {cle!r} (période {periode}) est la bonne, mais le texte "
        f"déchiffré ne correspond pas :\n  votre déchiffrement commence par : "
        f"{clair[:70]}..."
    )


@epreuve("C.4", "le second message intercepté est déchiffré")
def test_message_2():
    attendu = EMPREINTES["vigenere2"]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )
    periode, cle, clair = _retrouver_message(tp.MESSAGE_2, attendu)
    assert periode is not None, (
        "aucune période essayée (de 2 à 15) ne donne la bonne clef pour "
        "MESSAGE_2."
    )
    assert empreinte(clair[:attendu["longueur"]]) == attendu["texte"], (
        f"la clef {cle!r} (période {periode}) est la bonne, mais le texte "
        f"déchiffré ne correspond pas :\n  votre déchiffrement commence par : "
        f"{clair[:70]}..."
    )


# ==========================================================================
# PARTIE D — VIC simplifié
# ==========================================================================

@epreuve("D.1", "caractere_vic()")
def test_caractere_vic():
    for chiffre_message in range(10):
        for chiffre_clef in range(10):
            for position in range(10):
                attendu = TABLEAU_VIC[(chiffre_message + chiffre_clef) % 10][position]
                resultat = tp.caractere_vic(chiffre_message, chiffre_clef, position)
                assert resultat == attendu, (
                    f"caractere_vic({chiffre_message}, {chiffre_clef}, {position}) : "
                    f"attendu {attendu!r}, obtenu {resultat!r}\n"
                    "  Rappel : ligne = (chiffre du message + chiffre de clef) "
                    "modulo 10, colonne = position dans le bloc de 10."
                )


@epreuve("D.2", "ligne_du_damier()")
def test_ligne_du_damier():
    for position in range(10):
        for ligne in range(10):
            lettre = TABLEAU_VIC[ligne][position]
            resultat = tp.ligne_du_damier(lettre, position)
            assert resultat == ligne, (
                f"la lettre {lettre!r} se trouve à la ligne {ligne} de la "
                f"colonne {position}, votre fonction propose {resultat}"
            )


@epreuve("D.3", "chiffre_du_damier()")
def test_chiffre_du_damier():
    for chiffre_message in range(10):
        for chiffre_clef in range(10):
            for position in range(10):
                lettre = TABLEAU_VIC[(chiffre_message + chiffre_clef) % 10][position]
                resultat = tp.chiffre_du_damier(lettre, chiffre_clef, position)
                assert resultat == chiffre_message, (
                    f"la lettre {lettre!r} avec le chiffre de clef "
                    f"{chiffre_clef} et la position {position} devait redonner "
                    f"le chiffre {chiffre_message} ; votre fonction propose "
                    f"{resultat}"
                )


@epreuve("D.4", "dechiffrer_message_vic()")
def test_dechiffrer_message_vic():
    essais = [
        ("LETRAINEST", "12345", PERMUTATION_VIC),
        ("SENATROIDLSENATROIDL", "9", PERMUTATION_VIC),
        ("LIONSENATOLIONSENATO", "5241730219", [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]),
    ]
    for clair, cle, permutation in essais:
        chiffre = vic_chiffrer(clair, cle, permutation)
        resultat = tp.dechiffrer_message_vic(chiffre, cle, permutation)
        assert resultat == clair, (
            f"message chiffré : {chiffre}\n  avec la clef {cle!r} et la "
            f"permutation {permutation}, le message en clair est {clair!r} ; "
            f"votre fonction propose {resultat!r}"
        )

    # Le vrai message intercepté
    attendu = EMPREINTES["vic"]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )
    resultat = tp.dechiffrer_message_vic(tp.MESSAGE_VIC, tp.CLE_VIC)
    assert empreinte(resultat[:attendu["longueur"]]) == attendu["texte"], (
        "le message VIC n'est pas déchiffré correctement.\n"
        f"  votre déchiffrement commence par : {resultat[:40]}...\n"
        "  Rappel de l'ordre des opérations à l'envers : (1) retrouver les "
        "chiffres avec le damier, (2) défaire la transposition, (3) retirer la "
        "clef, (4) reconvertir les chiffres en lettres."
    )


if __name__ == "__main__":
    sys.exit(lancer())
