"""==========================================================================
 ÉPREUVES AUTOMATIQUES DU TP 1  (ne pas modifier ce fichier)
==========================================================================
Pour vérifier votre travail, tapez dans un terminal, dans ce dossier :

    python3 test_tp1_permutation.py

Chaque épreuve réussie s'affiche « [OK] », chaque épreuve ratée « [ÉCHEC] »
avec l'explication.  Relancez autant de fois que vous voulez : c'est en
essayant, en se trompant, puis en comprenant l'erreur, que l'on apprend.

Les épreuves de la partie C sont celles de la CRYPTANALYSE : elles vérifient que
vous avez retrouvé la méthode, la clef ET le texte des messages interceptés.  Le
fichier ne contient que des EMPREINTES de ces réponses : vous ne pouvez donc pas
tricher en le lisant, et c'est tant mieux.
==========================================================================
"""

import os
import sys

# Permet de trouver le dossier « outils » du dépôt, quel que soit l'endroit
# d'où l'on lance la commande.
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.verif import charger_module, empreinte, epreuve, lancer  # noqa: E402

tp = charger_module("tp1_permutation")

from common import comptage, scytale_chiffrer  # noqa: E402
from outils.reference import cesar_chiffrer, vider_les_espaces  # noqa: E402

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
EMPREINTES = {
    "scytale": {
        "longueur": 66,
        "texte": "5b701cd32afc4005c0d3bd2b5319aeea3d35879c3474f9011dd6580f82d9424b",
        "cle": "2c624232cdd221771294dfbb310aca000a0df6ac8b66b696d90ef06fdefb64a3",
        "methode": "27852a0d8891ba12730e3835c4d5bbdb6f16fa4faf42529dc826394064861ff1",
    },
    "cesar": {
        "longueur": 72,
        "texte": "bf20ebe9bc9d560f0885e9fe19b65d61c112b310b4dbd749b6a4ed19c76e04df",
        "cle": "4523540f1504cd17100c4835e85b7eefd49911580f8efff0599a8f283be6b9e3",
        "methode": "9719afb6914cede56aa9e49c32f6e7aa053303b32b37e307bdfa337b54594a82",
    },
    "mystere1": {
        "longueur": 58,
        "texte": "e6f7aa6ac3d27e059fefc0dd060587f00c19ace8b9106f266af852b9e679dbe0",
        "cle": "e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683",
        "methode": "27852a0d8891ba12730e3835c4d5bbdb6f16fa4faf42529dc826394064861ff1",
    },
    "mystere2": {
        "longueur": 65,
        "texte": "3944ec9d6b2275b3ada61d2f530687779e008ed9e0c5c932ed10cefe5f9b80b8",
        "cle": "4fc82b26aecb47d2868c4efbe3581732a3e7cbcc6c2efb32062c08170a05eeb8",
        "methode": "9719afb6914cede56aa9e49c32f6e7aa053303b32b37e307bdfa337b54594a82",
    },
    "mystere3": {
        "longueur": 58,
        "texte": "585746924f8be757402f34183de433f0275038f38d7965f76b204f814bb17a1c",
        "cle": "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",
        "methode": "27852a0d8891ba12730e3835c4d5bbdb6f16fa4faf42529dc826394064861ff1",
    },
}
# --- FIN DE LA ZONE GÉNÉRÉE ---


def _verifier_message(nom, methode, cle, texte):
    """Compare une attaque aux empreintes du professeur, avec des messages clairs.

    `nom` est le nom de l'entrée dans EMPREINTES, `methode` vaut "SCYTALE",
    "CESAR" ou None (quand la méthode n'est pas demandée).
    """
    attendu = EMPREINTES[nom]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )

    if methode is not None:
        assert empreinte(methode) == attendu["methode"], (
            f"vous proposez la méthode {methode}, ce n'est pas la bonne.\n"
            "  Réfléchissez : le chiffrement a-t-il REMPLACÉ les lettres (César, "
            "qui déplace les fréquences)\n"
            "  ou seulement DÉPLACÉ les lettres sans les changer (scytale, "
            "fréquences identiques) ?\n"
            "  Comparez les deux candidats avec vraisemblance(...) : le plus "
            "grand gagne."
        )

    assert empreinte(cle) == attendu["cle"], (
        f"la clef trouvée est fausse (vous proposez {cle!r}).\n"
        "  Pour la scytale : avez-vous bien pris la clef qui donne le texte "
        "ressemblant le plus à du français ?\n"
        "  Pour César : la bonne clef est celle dont la distance au français "
        "est la PLUS PETITE."
    )

    texte = texte[: attendu["longueur"]]
    assert empreinte(texte) == attendu["texte"], (
        "la clef est la bonne, mais le texte déchiffré ne correspond pas.\n"
        f"  votre déchiffrement commence par : {texte[:60]}...\n"
        "  (pour la scytale, les X de complément à la fin du message sont "
        "normaux : on les ignore)"
    )


# ==========================================================================
# § B — le code à écrire
# ==========================================================================

@epreuve("B.1", "compter_lettres()")
def test_compter_lettres():
    """Le comptage doit donner les 26 lettres, avec les bonnes valeurs."""
    resultat = tp.compter_lettres("BONJOUR")
    assert len(resultat) == 26, (
        f"on attendait un dictionnaire de 26 cases, on en obtient {len(resultat)}"
    )
    assert resultat["O"] == 2, f'la lettre O apparaît 2 fois, on obtient {resultat["O"]}'
    assert resultat["B"] == 1, f'la lettre B apparaît 1 fois, on obtient {resultat["B"]}'
    assert resultat["A"] == 0, (
        f'la lettre A est absente, on attendait 0, on obtient {resultat["A"]}'
    )
    assert sum(resultat.values()) == 7, (
        f"le total des comptes doit être 7 (BONJOUR a 7 lettres), "
        f"on obtient {sum(resultat.values())}"
    )

    resultat = tp.compter_lettres("a b, a !")
    assert resultat["A"] == 2 and resultat["B"] == 1, (
        'pour "a b, a !" on attendait 2 lettres A et 1 lettre B, '
        f'on obtient {resultat["A"]} et {resultat["B"]}'
    )


@epreuve("B.2", "cesar_chiffrer()")
def test_cesar_chiffrer():
    """Le décalage se fait modulo 26, en conservant les autres caractères."""
    for texte, cle, attendu in [
        ("AVE", 3, "DYH"),
        ("BONJOUR, LE MONDE", 3, "ERQMRXU, OH PRQGH"),
        ("XYZ", 3, "ABC"),
        ("abc", 1, "BCD"),
        ("AAAA", 0, "AAAA"),
        ("ZZZ", 25, "YYY"),
    ]:
        resultat = tp.cesar_chiffrer(texte, cle)
        assert resultat == attendu, (
            f"pour {texte!r} avec la clef {cle}, on attendait {attendu!r}, "
            f"on obtient {resultat!r}"
        )


@epreuve("B.3", "cesar_dechiffrer()")
def test_cesar_dechiffrer():
    """Déchiffrer doit défaire exactement le chiffrement."""
    for texte in ["BONJOUR, LE MONDE", "AVE CESAR", "ZZZ", "L'AMI ARRIVE"]:
        for cle in range(26):
            chiffre = cesar_chiffrer(texte, cle)
            resultat = tp.cesar_dechiffrer(chiffre, cle)
            assert resultat == texte, (
                f"après chiffrement avec la clef {cle}, on attendait {texte!r}, "
                f"on obtient {resultat!r}"
            )


# ==========================================================================
# § C — ★ CRYPTANALYSE ★
# ==========================================================================

@epreuve("C.1", "attaque_scytale()")
def test_attaque_scytale():
    """L'attaque doit retrouver la clef et le message, sans la connaître."""
    essais = [
        ("LERENDEZVOUSESTFIXEAMIDI", 4),
        ("LEGRANDMESSAGERARRIVECETTEAPRESMIDI", 7),
        ("NOUSPARTONSDEMAINMATINAVECLEGROUPEENTIER", 3),
    ]
    for message, cle in essais:
        chiffre = scytale_chiffrer(message, cle)
        cle_trouvee, texte_trouve = tp.attaque_scytale(chiffre)
        assert cle_trouvee == cle, (
            f"la clef utilisée était {cle}, votre attaque propose {cle_trouvee}\n"
            f"  texte chiffré : {chiffre}"
        )
        assert texte_trouve[:len(message)] == message, (
            f"la clef {cle} est bien trouvée, mais le texte déchiffré ne "
            f"correspond pas :\n  attendu : {message}\n  obtenu  : {texte_trouve}"
        )


@epreuve("C.2", "forcer_cesar()")
def test_forcer_cesar():
    """Les 26 clefs doivent être essayées, et la bonne reconnue."""
    essais = [
        ("LE MESSAGE ARRIVE CE SOIR", 19),
        ("LE CONVOI PART DEMAIN MATIN A L AUBE", 3),
        ("RENDEZ VOUS AU PORT A MIDI AVEC LE COLIS DE LA VEUVE ET LE COURRIER", 22),
        ("TOUT EST CALME SUR LE FRONT", 0),
    ]
    for message, cle in essais:
        chiffre = cesar_chiffrer(message, cle)
        cle_trouvee, texte_trouve = tp.forcer_cesar(chiffre)
        assert cle_trouvee == cle, (
            f"la clef utilisée était {cle}, votre attaque propose {cle_trouvee}\n"
            f"  texte chiffré : {chiffre}"
        )
        assert texte_trouve == message, (
            f"la clef {cle} est bien trouvée, mais le texte déchiffré ne "
            f"correspond pas :\n  attendu : {message}\n  obtenu  : {texte_trouve}"
        )


@epreuve("C.3", "identifier_et_dechiffrer()")
def test_identifier_et_dechiffrer():
    """Les deux méthodes doivent être essayées, et la bonne reconnue."""
    essais = [
        ("scytale", 4, "LE MESSAGER ARRIVE AU VILLAGE AVANT LA NUIT ET REPART AU MATIN"),
        ("cesar", 19, "LE MESSAGE ARRIVE CE SOIR A DIX HEURES DEVANT LA PORTE"),
        ("scytale", 3, "LE TRAIN PART A MIDI ET LE COURRIER SUIT LA ROUTE DE LA VALLEE"),
        ("cesar", 13, "ATTENTION AUX VOITURES SUR LA ROUTE DE LA COTE CE MATIN"),
    ]
    for methode, cle, message in essais:
        # La fonction travaille sur les lettres seules : les espaces et la
        # ponctuation sont donc considérés comme absents.
        message_propre = vider_les_espaces(message)
        if methode == "scytale":
            chiffre = scytale_chiffrer(message_propre, cle)
        else:
            chiffre = cesar_chiffrer(message_propre, cle)

        resultat = tp.identifier_et_dechiffrer(chiffre)
        assert isinstance(resultat, tuple) and len(resultat) == 3, (
            "la fonction doit renvoyer TROIS valeurs : la méthode, la clef et "
            "le texte\n  par exemple : return (\"CESAR\", cle, texte)\n"
            f"  on obtient : {resultat!r}"
        )
        methode_trouvee, cle_trouvee, texte_trouve = resultat
        assert methode_trouvee == methode.upper(), (
            f"le message a été chiffré par {methode.upper()}, votre fonction "
            f"propose {methode_trouvee!r}\n  texte chiffré : {chiffre}\n"
            "  Rappel : comparez les DEUX candidats avec vraisemblance(...)."
        )
        assert cle_trouvee == cle, (
            f"la méthode est reconnue ({methode.upper()}), mais la clef est "
            f"fausse : vous proposez {cle_trouvee}, la bonne est {cle}\n"
            f"  texte chiffré : {chiffre}"
        )
        assert texte_trouve[:len(message_propre)] == message_propre, (
            "la méthode et la clef sont bonnes, mais le texte non :\n"
            f"  attendu (sans espaces) : {message_propre}\n"
            f"  obtenu                 : {texte_trouve}\n"
            "  Rappel : identifier_et_dechiffrer travaille sur les lettres seules, "
            "elle renvoie donc aussi un texte sans espaces."
        )


@epreuve("C.4", "le message MESSAGE_SCYTALE est déchiffré")
def test_message_scytale():
    """Premier message intercepté : une scytale, clef inconnue."""
    assert hasattr(tp, "MESSAGE_SCYTALE") and tp.MESSAGE_SCYTALE, (
        "la constante MESSAGE_SCYTALE est vide ou a disparu de votre fichier : "
        "ne modifiez pas la zone générée"
    )
    cle, texte = tp.attaque_scytale(tp.MESSAGE_SCYTALE)
    _verifier_message("scytale", "SCYTALE", cle, texte)


@epreuve("C.5", "le message MESSAGE_CESAR est déchiffré")
def test_message_cesar():
    """Deuxième message intercepté : un César, clef inconnue."""
    assert hasattr(tp, "MESSAGE_CESAR") and tp.MESSAGE_CESAR, (
        "la constante MESSAGE_CESAR est vide ou a disparu de votre fichier : "
        "ne modifiez pas la zone générée"
    )
    cle, texte = tp.forcer_cesar(tp.MESSAGE_CESAR)
    _verifier_message("cesar", "CESAR", cle, texte)


@epreuve("C.6", "le message MESSAGE_MYSTERE_1 est déchiffré")
def test_mystere1():
    """Message mystère : la méthode elle-même est inconnue."""
    methode, cle, texte = tp.identifier_et_dechiffrer(tp.MESSAGE_MYSTERE_1)
    _verifier_message("mystere1", methode, cle, texte)


@epreuve("C.7", "le message MESSAGE_MYSTERE_2 est déchiffré")
def test_mystere2():
    """Message mystère : la méthode elle-même est inconnue."""
    methode, cle, texte = tp.identifier_et_dechiffrer(tp.MESSAGE_MYSTERE_2)
    _verifier_message("mystere2", methode, cle, texte)


@epreuve("C.8", "le message MESSAGE_MYSTERE_3 est déchiffré")
def test_mystere3():
    """Message mystère : la méthode elle-même est inconnue."""
    methode, cle, texte = tp.identifier_et_dechiffrer(tp.MESSAGE_MYSTERE_3)
    _verifier_message("mystere3", methode, cle, texte)


if __name__ == "__main__":
    sys.exit(lancer())
