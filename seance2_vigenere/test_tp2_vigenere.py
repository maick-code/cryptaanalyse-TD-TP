"""==========================================================================
 ÉPREUVES AUTOMATIQUES DU TP 2  (ne pas modifier ce fichier)
==========================================================================
    python3 test_tp2_vigenere.py
==========================================================================
"""

import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.verif import charger_module, empreinte, epreuve, lancer  # noqa: E402

tp = charger_module("tp2_vigenere")

from outils.reference import (  # noqa: E402
    vigenere_chiffrer as chiffrer_reference,
    vigenere_dechiffrer as dechiffrer_reference,
)

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
EMPREINTES = {
    "vigenere1": {
        "longueur": 432,
        "texte": "c9078c0a096bc892154ac7707284e229719ee172ae028a74fe4ef047e53886b8",
        "cle": "1149799f024164d3724b1312e8d659d5309108927e9360f94e2958830ab2912b",
        "periode": "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",
    },
    "vigenere2": {
        "longueur": 331,
        "texte": "c42bbbd81058db3d28e33b9b448de06c0f4fcc1a751db461a8609be9a54f2b03",
        "cle": "bac81eaa51df1f49b24f74b5795061585734f78c52a1ffe51ce280472b211f4b",
        "periode": "7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451",
    },
}
# --- FIN DE LA ZONE GÉNÉRÉE ---

# Texte français long, utilisé pour fabriquer des colonnes de Vigenère.
TEXTE_LONG = (
    "LE MESSAGE ARRIVE CE SOIR A DIX HEURES DEVANT LA PORTE DU JARDIN PRES DE "
    "LA FONTAINE. LES ENFANTS JOUENT DANS LA COUR DE L ECOLE ET LE MAITRE "
    "FERME LES VOLETS. DEMAIN MATIN NOUS PARTIRONS AVANT LE LEVER DU SOLEIL "
    "POUR ARRIVER A LA RIVIERE AU MILIEU DE LA JOURNEE. LE BATEAU ATTENDRA "
    "SUR LA BERGE AVEC LES PECHEURS ET LEURS FILETS. CHACUN A PREPARE SON "
    "BAGAGE ET SES PROVISIONS POUR LE VOYAGE."
)


def _colonnes_de_reference(texte, periode):
    """Découpage en colonnes, écrit ici pour ne pas dépendre de la fonction
    de l'étudiant (les tests ne doivent pas s'appuyer sur ce qu'ils testent)."""
    morceaux = ["" for _ in range(periode)]
    for position, caractere in enumerate(texte):
        morceaux[position % periode] += caractere
    return morceaux


# ==========================================================================
# PARTIE A — petits outils
# ==========================================================================

@epreuve("A.1", "indice_de_la_lettre()")
def test_indice_de_la_lettre():
    for lettre, attendu in [("A", 0), ("B", 1), ("M", 12), ("Z", 25),
                            ("a", 0), ("z", 25)]:
        resultat = tp.indice_de_la_lettre(lettre)
        assert resultat == attendu, (
            f"indice_de_la_lettre({lettre!r}) : attendu {attendu}, obtenu {resultat}"
        )


@epreuve("A.2", "decaler_lettre()")
def test_decaler_lettre():
    for lettre, decalage, attendu in [
        ("A", 3, "D"), ("Z", 1, "A"), ("A", -1, "Z"), ("B", -1, "A"),
        ("B", 25, "A"), ("Z", 26, "Z"), ("a", 1, "B"), ("M", 0, "M"),
    ]:
        resultat = tp.decaler_lettre(lettre, decalage)
        assert resultat == attendu, (
            f"decaler_lettre({lettre!r}, {decalage}) : attendu {attendu!r}, "
            f"obtenu {resultat!r}"
        )


@epreuve("A.3", "vider_les_espaces()")
def test_vider_les_espaces():
    for texte, attendu in [
        ("Bonjour, l'ami !", "BONJOURLAMI"),
        ("DEJA PROPRE", "DEJAPROPRE"),
        ("  avec des     espaces  ", "AVECDESESPACES"),
        ("a-b.c", "ABC"),
    ]:
        resultat = tp.vider_les_espaces(texte)
        assert resultat == attendu, (
            f"vider_les_espaces({texte!r}) : attendu {attendu!r}, obtenu {resultat!r}"
        )


# ==========================================================================
# PARTIE B — Vigenère
# ==========================================================================

@epreuve("B.1", "vigenere_chiffrer()")
def test_vigenere_chiffrer():
    essais = [
        ("BONJOUR", "CLE"),
        ("BONJOUR LE MONDE", "CLE"),
        ("Bonjour le monde, a dix heures !", "SECRET"),
        ("MATHEMATIQUES", "ABC"),
        ("MOT", "TRESLONGUECLEF"),
        ("LE MESSAGE ARRIVE CE SOIR", "Z"),
    ]
    for texte, cle in essais:
        resultat = tp.vigenere_chiffrer(texte, cle)
        attendu = chiffrer_reference(texte, cle)
        assert resultat == attendu, (
            f"vigenere_chiffrer({texte!r}, {cle!r}) :\n"
            f"  attendu {attendu!r}\n  obtenu  {resultat!r}\n"
            "  (rappel : les espaces et la ponctuation sont conservés et ne "
            "consomment PAS de lettre de clef)"
        )


@epreuve("B.2", "vigenere_dechiffrer()")
def test_vigenere_dechiffrer():
    for texte, cle in [
        ("BONJOUR LE MONDE", "CLE"),
        ("LE MESSAGE ARRIVE CE SOIR, A DIX HEURES !", "SECRET"),
        ("UN AUTRE ESSAI DE TEXTE", "VIGENERE"),
    ]:
        chiffre = chiffrer_reference(texte, cle)
        resultat = tp.vigenere_dechiffrer(chiffre, cle)
        attendu = dechiffrer_reference(chiffre, cle)
        assert resultat == attendu, (
            f"vigenere_dechiffrer({chiffre!r}, {cle!r}):\n"
            f"  attendu {attendu!r}\n  obtenu  {resultat!r}"
        )
        assert resultat == texte.upper(), (
            "le déchiffrement doit redonner exactement le message de départ "
            f"(en majuscules) : attendu {texte.upper()!r}, obtenu {resultat!r}"
        )

    # Le déchiffrement doit être l'inverse du chiffrement, y compris pour la
    # version écrite par l'étudiant.
    chiffre = tp.vigenere_chiffrer("LE MESSAGE ARRIVE CE SOIR", "SECRET")
    resultat = tp.vigenere_dechiffrer(chiffre, "SECRET")
    assert resultat == "LE MESSAGE ARRIVE CE SOIR", (
        "chiffrer puis déchiffrer avec vos deux fonctions doit redonner le "
        f"message de départ : obtenu {resultat!r}"
    )


# ==========================================================================
# PARTIE C — l'attaque
# ==========================================================================

@epreuve("C.1", "forcer_cesar_sur_colonne()")
def test_forcer_cesar_sur_colonne():
    cle = "SECRET"
    texte = "".join(c for c in TEXTE_LONG.upper() if "A" <= c <= "Z")
    chiffre = chiffrer_reference(texte, cle)
    morceaux = _colonnes_de_reference(chiffre, len(cle))

    for numero, morceau in enumerate(morceaux):
        attendu = ord(cle[numero]) - ord("A")
        resultat = tp.forcer_cesar_sur_colonne(morceau)
        assert resultat == attendu, (
            f"la colonne numéro {numero} (longue de {len(morceau)} lettres) a été "
            f"chiffrée avec la lettre de clef {cle[numero]!r}, donc le décalage "
            f"{attendu} ; votre fonction propose {resultat}.\n"
            f"  colonne : {morceau[:50]}...\n"
            "  Astuce : regardez les distances obtenues pour les 26 décalages."
        )


@epreuve("C.2", "colonnes()")
def test_colonnes():
    for texte, periode, attendu in [
        ("ABCDEFGHIJ", 3, ["ADGJ", "BEH", "CFI"]),
        ("ABCDEF", 2, ["ACE", "BDF"]),
        ("ABCD", 4, ["A", "B", "C", "D"]),
        ("ABCDE", 5, ["A", "B", "C", "D", "E"]),
    ]:
        resultat = list(tp.colonnes(texte, periode))
        assert resultat == attendu, (
            f"colonnes({texte!r}, {periode}) : attendu {attendu}, obtenu {resultat}"
        )
    assert len(tp.colonnes("ABCDEFGHIJ", 7)) == 7, (
        "colonnes() doit renvoyer exactement `periode` morceaux (même vides)"
    )


@epreuve("C.3", "recoller()")
def test_recoller():
    for morceaux, periode, attendu in [
        (["ADGJ", "BEH", "CFI"], 3, "ABCDEFGHIJ"),
        (["ACE", "BDF"], 2, "ABCDEF"),
        (["A", "B", "C", "D"], 4, "ABCD"),
    ]:
        resultat = tp.recoller(morceaux, periode)
        assert resultat == attendu, (
            f"recoller({morceaux}, {periode}) : attendu {attendu!r}, "
            f"obtenu {resultat!r}"
        )

    # recoller doit défaire exactement ce que fait colonnes.
    texte = "".join(c for c in TEXTE_LONG.upper() if "A" <= c <= "Z")
    for periode in (3, 5, 7):
        resultat = tp.recoller(tp.colonnes(texte, periode), periode)
        assert resultat == texte, (
            f"recoller(colonnes(texte, {periode}), {periode}) doit redonner le "
            "texte de départ"
        )


@epreuve("C.4", "forcer_vigenere()")
def test_forcer_vigenere():
    """L'attaque complète sur un message dont on connaît la période.

    Remarque : l'attaque a besoin de matière !  Chaque colonne doit contenir
    assez de lettres (une bonne cinquantaine) pour que la comparaison des
    fréquences soit fiable.  C'est pour cela que les essais ci-dessous portent
    sur un texte long : sur un message de vingt lettres, personne ne peut
    deviner la clef, et ce n'est pas un défaut de votre programme.
    """
    for texte, cle in [
        (TEXTE_LONG, "SECRET"),
        (TEXTE_LONG, "MATIN"),
        (TEXTE_LONG, "CLEF"),
        (TEXTE_LONG, "VIGENERE"),
    ]:
        chiffre = chiffrer_reference(texte, cle)
        resultat = tp.forcer_vigenere(chiffre, len(cle))
        cle_trouvee, clair_trouve = resultat
        assert cle_trouvee == cle, (
            f"pour ce message chiffré avec la clef {cle!r}, votre attaque "
            f"propose {cle_trouvee!r}\n  message chiffré : {chiffre[:80]}..."
        )
        assert clair_trouve[:len(texte)] == texte.upper(), (
            f"la clef {cle} est trouvée, mais le texte déchiffré ne convient pas :\n"
            f"  attendu : {texte.upper()[:80]}...\n"
            f"  obtenu  : {clair_trouve[:80]}..."
        )


@epreuve("C.5", "le premier message intercepté est déchiffré")
def test_message_1():
    attendu = EMPREINTES["vigenere1"]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )
    cle, clair = tp.forcer_vigenere(tp.MESSAGE_VIGENERE_1, tp.PERIODE_1)
    assert empreinte(cle) == attendu["cle"], (
        f"la clef trouvée est {cle!r}, elle n'est pas la bonne. "
        "Vérifiez le découpage en colonnes (les espaces ne doivent pas être "
        "comptés) et le décalage retenu pour chaque colonne."
    )
    assert empreinte(clair[:attendu["longueur"]]) == attendu["texte"], (
        "la clef est la bonne, mais le message déchiffré ne correspond pas.\n"
        f"  votre déchiffrement commence par : {clair[:70]}..."
    )


@epreuve("C.6", "le second message intercepté est déchiffré")
def test_message_2():
    attendu = EMPREINTES["vigenere2"]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )
    cle, clair = tp.forcer_vigenere(tp.MESSAGE_VIGENERE_2, tp.PERIODE_2)
    assert empreinte(cle) == attendu["cle"], (
        f"la clef trouvée est {cle!r}, elle n'est pas la bonne."
    )
    assert empreinte(clair[:attendu["longueur"]]) == attendu["texte"], (
        "la clef est la bonne, mais le message déchiffré ne correspond pas.\n"
        f"  votre déchiffrement commence par : {clair[:70]}..."
    )


# ==========================================================================
# PARTIE D — texte connu
# ==========================================================================

@epreuve("D.1", "cle_par_texte_connu()")
def test_cle_par_texte_connu():
    for clair, cle in [
        ("BONJOUR", "CLE"),
        ("LE MESSAGE ARRIVE CE SOIR A DIX HEURES", "SECRET"),
        ("LE MESSAGE ARRIVE CE SOIR A DIX HEURES", "MATHEMATIQUES"),
        ("PAS DE CHANCE", "A"),
    ]:
        chiffre = chiffrer_reference(clair, cle)
        resultat = tp.cle_par_texte_connu(clair, chiffre)
        # La clef « A » ne décale rien : la plus petite clef possible est "A",
        # ce que l'on accepte pour ce cas particulier.
        attendu = cle if set(cle) != {"A"} else "A"
        assert resultat == attendu, (
            f"avec le texte connu {clair!r} chiffré en {chiffre!r}, la clef "
            f"attendue est {attendu!r}, votre fonction propose {resultat!r}"
        )

    # Remarque importante : on ne peut retrouver que les lettres de clef qui
    # ont réellement servi !  Si la clef est plus longue que le texte connu,
    # on ne la retrouve pas en entier.  C'est une limite de l'attaque, pas de
    # votre programme.

    # Fonctionne aussi avec un texte clair présenté avec sa ponctuation.
    clair = "LE MESSAGE ARRIVE, CE SOIR !"
    chiffre = chiffrer_reference(clair, "CLE")
    resultat = tp.cle_par_texte_connu(clair, chiffre)
    assert resultat == "CLE", (
        "la ponctuation ne doit pas gêner : attendu 'CLE', "
        f"obtenu {resultat!r}"
    )


if __name__ == "__main__":
    sys.exit(lancer())
