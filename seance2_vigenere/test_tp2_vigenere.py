"""==========================================================================
 ÉPREUVES AUTOMATIQUES DU TP 2  (ne pas modifier ce fichier)
==========================================================================
Pour vérifier votre travail, tapez dans un terminal, dans ce dossier :

    python3 test_tp2_vigenere.py

Chaque épreuve réussie s'affiche « [OK] », chaque épreuve ratée « [ÉCHEC] »
avec l'explication.

Les épreuves de la partie C sont celles de la CRYPTANALYSE : quatre messages
interceptés dont vous devez retrouver la clef et le texte.  Le fichier ne
contient que des EMPREINTES (SHA-256) de ces réponses : vous ne pouvez pas
tricher en le lisant, et c'est tant mieux.
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
    colonnes,
    decaler_lettre,
    vider_les_espaces,
    vigenere_chiffrer as vigenere_chiffrer_reference,
)

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
EMPREINTES = {
    "vigenere1": {
        "longueur": 432,
        "texte": "c9078c0a096bc892154ac7707284e229719ee172ae028a74fe4ef047e53886b8",
        "cle": "1149799f024164d3724b1312e8d659d5309108927e9360f94e2958830ab2912b",
        "methode": "59634baee12f7567c95b1aee0b104300aad5be4073d5e363b257c50346019b05",
        "periode": "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",
    },
    "vigenere2": {
        "longueur": 331,
        "texte": "c42bbbd81058db3d28e33b9b448de06c0f4fcc1a751db461a8609be9a54f2b03",
        "cle": "bac81eaa51df1f49b24f74b5795061585734f78c52a1ffe51ce280472b211f4b",
        "methode": "59634baee12f7567c95b1aee0b104300aad5be4073d5e363b257c50346019b05",
        "periode": "7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451",
    },
    "urgent": {
        "longueur": 600,
        "texte": "b528bd062fe5107805adcb40cb561e2f8d3554279da0be2da01af1d323325afa",
        "cle": "0917b13a9091915d54b6336f45909539cce452b3661b21f386418a257883b30a",
        "methode": "59634baee12f7567c95b1aee0b104300aad5be4073d5e363b257c50346019b05",
        "periode": "e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683",
    },
    "connu": {
        "longueur": 320,
        "texte": "7bef8babed9b25f95d706fbd2abec7f331513aeb36a74271e943f7c32b3cd823",
        "cle": "c07222d65fd8d5a882617f53dbe943864459af662d9c20b67224aa5b9a88708b",
        "methode": "59634baee12f7567c95b1aee0b104300aad5be4073d5e363b257c50346019b05",
        "periode": "e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683",
        "fragment": 72,
    },
}
# --- FIN DE LA ZONE GÉNÉRÉE ---


def _verifier_message(nom, cle, texte):
    """Compare une attaque aux empreintes du professeur, avec des messages clairs."""
    attendu = EMPREINTES[nom]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )

    assert empreinte(cle) == attendu["cle"], (
        f"la clef trouvée est fausse (vous proposez {cle!r}).\n"
        "  Deux causes possibles :\n"
        "   1. une colonne a été mal reconnue (vérifiez C.1 sur une colonne "
        "isolée) ;\n"
        "   2. les espaces ou la ponctuation ont été comptés comme des lettres "
        "(ils ne consomment PAS de lettre de clef).\n"
        "  Astuce : ajoutez `print(cle)` dans forcer_vigenere et comparez avec "
        "la vraie clef... que vous ne connaissez pas !  Regardez plutôt si la "
        "clef trouvée est presque la bonne : c'est le signe d'une colonne "
        "fautive."
    )

    texte = texte[: attendu["longueur"]]
    assert empreinte(texte) == attendu["texte"], (
        "la clef est la bonne, mais le texte déchiffré ne correspond pas.\n"
        f"  votre déchiffrement commence par : {texte[:60]}...\n"
        "  Rappel : les espaces et la ponctuation du message chiffré doivent se "
        "retrouver à leur place (outil `rehabiller`)."
    )


# ==========================================================================
# § B — le code à écrire
# ==========================================================================

@epreuve("B.1", "vigenere_chiffrer()")
def test_vigenere_chiffrer():
    """La clef tourne, et les caractères non alphabétiques ne la consomment pas."""
    essais = [
        ("BONJOUR", "CLE", "DZRLZYT"),
        ("BONJOUR LE MONDE", "CLE", "DZRLZYT WI OZRFP"),
        ("AAAA", "A", "AAAA"),
        ("ABC", "ABC", "ACE"),
        ("LE MESSAGE ARRIVE", "SIGNAL", "DM SRSDSOK NRCADK"),
    ]
    for texte, cle, attendu in essais:
        resultat = tp.vigenere_chiffrer(texte, cle)
        assert resultat == attendu, (
            f"pour {texte!r} avec la clef {cle!r}, on attendait {attendu!r}, "
            f"on obtient {resultat!r}\n"
            "  Vérifiez le compteur `rang_clef` : il ne s'incrémente QUE devant "
            "une lettre."
        )
        reference = vigenere_chiffrer_reference(texte, cle)
        assert resultat == reference, (
            "la version du professeur donne un autre résultat :\n"
            f"  la vôtre    : {resultat!r}\n  la référence : {reference!r}"
        )


@epreuve("B.2", "vigenere_dechiffrer()")
def test_vigenere_dechiffrer():
    """Chiffrer puis déchiffrer doit redonner le message d'origine."""
    for texte in ["BONJOUR, LE MONDE !", "LE CONVOI PART A L AUBE", "AVE CESAR"]:
        for cle in ["CLE", "PILOTE", "SIGNAL", "A"]:
            chiffre = vigenere_chiffrer_reference(texte, cle)
            resultat = tp.vigenere_dechiffrer(chiffre, cle)
            assert resultat == texte, (
                f"avec la clef {cle!r} et le message {texte!r}, on attendait "
                f"{texte!r}, on obtient {resultat!r}\n"
                "  N'oubliez pas le signe : vigenere_dechiffrer retire le "
                "décalage (-decalage)."
            )


# ==========================================================================
# § C — ★ CRYPTANALYSE ★
# ==========================================================================

@epreuve("C.1", "decalage_probable()")
def test_decalage_probable():
    """Chaque colonne doit révéler le décalage qui l'a chiffrée."""
    message = vider_les_espaces(
        "LE MESSAGE ARRIVE CE SOIR A DIX HEURES DEVANT LA PORTE DU JARDIN"
    )
    for decalage_attendu in (0, 3, 11, 20):
        colonne = "".join(
            decaler_lettre(lettre, decalage_attendu) for lettre in message
        )
        trouve = tp.decalage_probable(colonne)
        assert trouve == decalage_attendu, (
            f"la colonne avait été chiffrée avec le décalage {decalage_attendu} "
            f"(lettre de clef {chr(65 + decalage_attendu)}), votre fonction "
            f"propose {trouve}\n  colonne chiffrée : {colonne[:40]}...\n"
            "  Rappel : on garde le décalage dont la distance au français est "
            "la PLUS PETITE."
        )


@epreuve("C.2", "forcer_vigenere()")
def test_forcer_vigenere():
    """L'attaque complète doit retrouver la clef et le texte, période connue."""
    # Les textes sont assez longs : chaque colonne contient au moins une
    # quinzaine de lettres, sans quoi l'analyse de fréquences se trompe (et ce
    # n'est alors pas VOTRE code qui est faux, mais l'échantillon qui est trop
    # pauvre : c'est une leçon à retenir).
    essais = [
        ("LE DIRECTEUR DU PORT A RECU NOTRE LETTRE ET IL REPOND QUE LES "
         "MARCHANDISES ARRIVERONT PAR LE BATEAU DE MARDI", "TAMBOUR"),
        ("ATTAQUE PREVUE A L AUBE SUR LE FLANC DROIT DE LA COLLINE ET SUR LES "
         "DEUX PONTS DE LA RIVIERE DEVANT LE VILLAGE DE PIERREFEU OU LES "
         "SOLDATS DU POSTE ATTENDENT DES RENFORTS DEPUIS DEUX JOURS", "MARINE"),
        ("LES MARCHANDISES SONT RESTEES SUR LE QUAI TOUTE LA NUIT ET LES "
         "PORTEURS ONT REFUSE DE LES CHARGER AVANT L ARRIVEE DU CONTROLEUR DU "
         "PORT QUI DOIT VERIFIER LES PAPIERS ET LES SCEAUX APPOSES PAR LES "
         "DOUANIERS DE LA FRONTIERE", "PILOTE"),
    ]
    for clair, cle in essais:
        chiffre = vigenere_chiffrer_reference(clair, cle)
        cle_trouvee, clair_trouve = tp.forcer_vigenere(chiffre, len(cle))
        assert cle_trouvee == cle, (
            f"la clef utilisée était {cle!r}, votre attaque propose "
            f"{cle_trouvee!r}\n  message chiffré : {chiffre[:80]}...\n"
            "  Vérifiez que vous découpez bien les colonnes sur le texte SANS "
            "espaces."
        )
        assert clair_trouve == clair, (
            f"la clef {cle!r} est bien trouvée, mais le texte ne correspond "
            f"pas :\n  attendu : {clair}\n  obtenu  : {clair_trouve}"
        )


@epreuve("C.3", "la dépêche MESSAGE_VIGENERE_1 est déchiffrée")
def test_message_vigenere_1():
    """Première dépêche interceptée : la période est donnée."""
    cle, clair = tp.forcer_vigenere(tp.MESSAGE_VIGENERE_1, tp.PERIODE_1)
    _verifier_message("vigenere1", cle, clair)


@epreuve("C.4", "la dépêche MESSAGE_VIGENERE_2 est déchiffrée")
def test_message_vigenere_2():
    """Deuxième dépêche interceptée : la période est donnée."""
    cle, clair = tp.forcer_vigenere(tp.MESSAGE_VIGENERE_2, tp.PERIODE_2)
    _verifier_message("vigenere2", cle, clair)


@epreuve("C.5", "la dépêche MESSAGE_URGENT est déchiffrée")
def test_message_urgent():
    """Dépêche inédite : la période est donnée, la clef non. C'est nouveau !"""
    cle, clair = tp.forcer_vigenere(tp.MESSAGE_URGENT, tp.PERIODE_URGENT)
    _verifier_message("urgent", cle, clair)


@epreuve("C.6", "cle_par_texte_connu()")
def test_cle_par_texte_connu():
    """La clef se retrouve en comparant le clair et le chiffré, lettre à lettre."""
    essais = [
        ("BONJOUR", "CLE"),
        ("LE MESSAGE ARRIVE CE SOIR", "SIGNAL"),
        ("ATTAQUE A L AUBE", "CASQUE"),
    ]
    for clair, cle in essais:
        chiffre = vigenere_chiffrer_reference(clair, cle)
        trouvee = tp.cle_par_texte_connu(clair, chiffre)
        assert trouvee == cle, (
            f"avec {clair!r} chiffré par la clef {cle!r}, on attendait "
            f"{cle!r}, on obtient {trouvee!r}\n"
            "  Pensez à : clef = chiffré - clair (modulo 26), puis à chercher la "
            "plus petite période de la suite obtenue."
        )

    # Un fragment suffit : c'est tout l'intérêt de cette attaque.
    # Ici, le fragment connu (« LE MESS ») et sa version chiffrée ont des
    # longueurs différentes (l'espace n'est pas une lettre) : c'est justement le
    # cas à savoir traiter.
    fragment = vigenere_chiffrer_reference("LE MESS", "SIGNAL")
    trouvee = tp.cle_par_texte_connu("LE MESS", fragment)
    assert trouvee == "SIGNAL", (
        f"avec le fragment « LE MESS » chiffré par la clef 'SIGNAL' (ce qui "
        f"donne {fragment!r}), on attendait 'SIGNAL', on obtient {trouvee!r}\n"
        "  Les deux textes n'ont pas forcément le même nombre de lettres : "
        "comparez seulement le début commun."
    )


@epreuve("C.7", "la clef de MESSAGE_INTERCEPTE est retrouvée")
def test_cle_de_message_intercepte():
    """L'agent a photographié le début du texte clair : la clef est à nous."""
    assert tp.TEXTE_CONNU, (
        "la constante TEXTE_CONNU est vide ou a disparu : ne modifiez pas la "
        "zone générée de votre fichier"
    )
    attendu = EMPREINTES["connu"]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )

    cle = tp.cle_par_texte_connu(tp.TEXTE_CONNU, tp.MESSAGE_INTERCEPTE)
    assert empreinte(cle) == attendu["cle"], (
        f"la clef retrouvée est fausse (vous proposez {cle!r}).\n"
        f"  Le fragment connu fait {attendu['fragment']} lettres : c'est assez "
        "pour la clef entière.\n"
        "  Vérifiez que le fragment et le message intercepté sont bien comparés "
        "depuis le DÉBUT du message.\n"
        "  Astuce : affichez la suite des décalages, elle doit ressembler à une "
        "clef répétée, par exemple « EDFHEDFHEDFH... »."
    )
    print(f"          (clef retrouvée par texte connu : {cle})")


@epreuve("C.8", "MESSAGE_INTERCEPTE est entièrement déchiffré")
def test_message_intercepte_dechiffre():
    """On se sert de la clef retrouvée en C.7 pour lire tout le message."""
    attendu = EMPREINTES["connu"]
    assert tp.MESSAGE_INTERCEPTE, (
        "la constante MESSAGE_INTERCEPTE est vide ou a disparu : ne modifiez pas "
        "la zone générée de votre fichier"
    )

    # On retrouve la clef par texte connu, puis on l'utilise comme au C.2.
    cle = tp.cle_par_texte_connu(tp.TEXTE_CONNU, tp.MESSAGE_INTERCEPTE)
    cle_trouvee, clair = tp.forcer_vigenere(tp.MESSAGE_INTERCEPTE, len(cle))
    assert cle_trouvee == cle, (
        f"la clef retrouvée est {cle!r}, mais forcer_vigenere en propose "
        f"{cle_trouvee!r} : les deux attaques doivent aboutir à la même clef.\n"
        "  Vérifiez la période utilisée : c'est len(cle)."
    )
    _verifier_message("connu", cle_trouvee, clair)


if __name__ == "__main__":
    sys.exit(lancer())
