"""==========================================================================
 ÉPREUVES AUTOMATIQUES DU TP 1  (ne pas modifier ce fichier)
==========================================================================
Pour vérifier votre travail, tapez dans un terminal, dans ce dossier :

    python3 test_tp1_permutation.py

Chaque épreuve réussie s'affiche « [OK] », chaque épreuve ratée « [ÉCHEC] »
avec l'explication.  Relancez autant de fois que vous voulez : c'est en
essayant, en se trompant, puis en comprenant l'erreur, que l'on apprend.
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

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
EMPREINTES = {
    "scytale": {
        "longueur": 66,
        "texte": "5b701cd32afc4005c0d3bd2b5319aeea3d35879c3474f9011dd6580f82d9424b",
        "cle": "2c624232cdd221771294dfbb310aca000a0df6ac8b66b696d90ef06fdefb64a3",
    },
    "cesar": {
        "longueur": 72,
        "texte": "bf20ebe9bc9d560f0885e9fe19b65d61c112b310b4dbd749b6a4ed19c76e04df",
        "cle": "4523540f1504cd17100c4835e85b7eefd49911580f8efff0599a8f283be6b9e3",
    },
}
# --- FIN DE LA ZONE GÉNÉRÉE ---


# ==========================================================================
# PARTIE A — préparer le texte
# ==========================================================================

@epreuve("A.1", "nettoyer_simple()")
def test_nettoyer_simple():
    """Le texte doit être mis en majuscules et perdre tout ce qui n'est pas A...Z."""
    resultat = tp.nettoyer_simple("Bonjour, le monde !")
    assert resultat == "BONJOURLEMONDE", (
        f'pour "Bonjour, le monde !" on attendait "BONJOURLEMONDE", '
        f"on obtient {resultat!r}"
    )

    resultat = tp.nettoyer_simple("Le chat mange, en 2026.")
    assert resultat == "LECHATMANGEEN", (
        f'pour "Le chat mange, en 2026." on attendait "LECHATMANGEEN", '
        f"on obtient {resultat!r}"
    )

    resultat = tp.nettoyer_simple("DEJA PROPRE")
    assert resultat == "DEJAPROPRE", (
        f'pour "DEJA PROPRE" on attendait "DEJAPROPRE", on obtient {resultat!r}'
    )


@epreuve("A.2", "compter_lettres()")
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
        f"le total des comptes doit être 7 (le mot BONJOUR a 7 lettres), "
        f'on obtient {sum(resultat.values())}'
    )

    # Les minuscules comptent comme des majuscules, la ponctuation ne compte pas.
    resultat = tp.compter_lettres("a b, a !")
    assert resultat["A"] == 2 and resultat["B"] == 1, (
        'pour "a b, a !" on attendait 2 lettres A et 1 lettre B, '
        f'on obtient A = {resultat["A"]} et B = {resultat["B"]}'
    )

    # Cohérence avec l'outil comptage() fourni par le professeur.
    outil = comptage("LE MESSAGE ARRIVE CE SOIR")
    resultat = tp.compter_lettres("LE MESSAGE ARRIVE CE SOIR")
    assert resultat == outil, (
        "le résultat diffère de celui de l'outil comptage() fourni :\n"
        f"  vôtre  : {resultat}\n  attendu : {outil}"
    )


# ==========================================================================
# PARTIE B — scytale et son attaque
# ==========================================================================

@epreuve("B.1", "cle_scytale_possibles()")
def test_cle_scytale_possibles():
    """Les clefs proposées doivent diviser la longueur et laisser au moins 5 lignes."""
    for longueur, attendu in [
        (40, [2, 4, 5, 8]),
        (60, [2, 3, 4, 5, 6, 10, 12]),
        (35, [5, 7]),
        (10, [2]),
        (9, []),
    ]:
        resultat = list(tp.cle_scytale_possibles(longueur))
        assert resultat == attendu, (
            f"pour une longueur de {longueur} on attendait {attendu}, "
            f"on obtient {resultat}"
        )


@epreuve("B.2", "decouper_en_morceaux()")
def test_decouper_en_morceaux():
    """Le découpage doit respecter la taille demandée et le dernier morceau."""
    for texte, taille, attendu in [
        ("ABCDEFGH", 3, ["ABC", "DEF", "GH"]),
        ("ABCDEF", 3, ["ABC", "DEF"]),
        ("AB", 5, ["AB"]),
        ("", 4, []),
        ("ABCDE", 1, ["A", "B", "C", "D", "E"]),
    ]:
        resultat = list(tp.decouper_en_morceaux(texte, taille))
        assert resultat == attendu, (
            f"pour {texte!r} découpé par {taille} on attendait {attendu}, "
            f"on obtient {resultat}"
        )


@epreuve("B.3", "attaque_scytale()")
def test_attaque_scytale():
    """L'attaque doit retrouver la clef et le message, sans la connaître."""
    essais = [
        ("LERENDEZVOUSESTFIXEAMIDI", 4),
        ("LEGRANDMESSAGERARRIVECETTEAPRESMIDI", 7),
        ("NOUSPARTONSDEMAINMATINAVECLEGROUPEENTIER", 5),
    ]
    for message, cle in essais:
        chiffre = scytale_chiffrer(message, cle)
        resultat = tp.attaque_scytale(chiffre)
        cle_trouvee, texte_trouve = resultat
        assert cle_trouvee == cle, (
            f"la clef utilisée était {cle}, votre attaque propose {cle_trouvee}\n"
            f"  texte chiffré : {chiffre}"
        )
        assert texte_trouve[:len(message)] == message, (
            f"la clef {cle} est bien trouvée, mais le texte déchiffré ne "
            f"correspond pas :\n  attendu : {message}\n  obtenu  : {texte_trouve}"
        )


@epreuve("B.4", "le message scytale du TP est déchiffré")
def test_message_scytale_du_tp():
    """Le message MESSAGE_SCYTALE de votre fichier doit être déchiffré correctement."""
    if not hasattr(tp, "MESSAGE_SCYTALE"):
        raise AssertionError("la constante MESSAGE_SCYTALE a disparu de votre fichier")

    longueur = EMPREINTES["scytale"]["longueur"]
    cle, texte = tp.attaque_scytale(tp.MESSAGE_SCYTALE)
    assert longueur > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )
    assert empreinte(cle) == EMPREINTES["scytale"]["cle"], (
        f"la clef trouvée pour MESSAGE_SCYTALE est fausse (vous proposez {cle}). "
        "Avez-vous bien pris la clef qui donne le texte ressemblant le plus à "
        "du français ?"
    )
    assert empreinte(texte[:longueur]) == EMPREINTES["scytale"]["texte"], (
        "la clef est la bonne, mais le message déchiffré ne correspond pas.\n"
        f"  votre déchiffrement commence par : {texte[:60]}...\n"
        "  (les X de complément en fin de message sont normaux, on les ignore)"
    )


# ==========================================================================
# PARTIE C — César
# ==========================================================================

@epreuve("C.1", "cesar_chiffrer()")
def test_cesar_chiffrer():
    """Le décalage doit se faire modulo 26, en conservant les autres caractères."""
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
            f"cesar_chiffrer({texte!r}, {cle}) : attendu {attendu!r}, "
            f"obtenu {resultat!r}"
        )


@epreuve("C.2", "cesar_dechiffrer()")
def test_cesar_dechiffrer():
    """Le déchiffrement doit être exactement l'opération inverse du chiffrement."""
    assert tp.cesar_dechiffrer("ERQMRXU, OH PRQGH", 3) == "BONJOUR, LE MONDE", (
        "cesar_dechiffrer('ERQMRXU, OH PRQGH', 3) devrait valoir "
        "'BONJOUR, LE MONDE'"
    )
    assert tp.cesar_dechiffrer("ABC", 3) == "XYZ"

    message = "LE MESSAGE ARRIVE CE SOIR, PREPAREZ LA RECEPTION"
    for cle in range(26):
        chiffre = tp.cesar_chiffrer(message, cle)
        clair = tp.cesar_dechiffrer(chiffre, cle)
        assert clair == message, (
            f"pour la clef {cle}, on chiffre puis on déchiffre, et l'on ne "
            f"retrouve pas le message :\n  attendu : {message}\n  obtenu  : {clair}\n"
            "  c'est la définition même d'un code : d_k(e_k(x)) = x !"
        )


@epreuve("C.3", "forcer_cesar()")
def test_forcer_cesar():
    """La clef doit être retrouvée automatiquement, sans être donnée."""
    essais = [
        ("LE GRAND MESSAGE ARRIVE CE SOIR, LA MISSION EST EN COURS", 3),
        ("NOUS PARTONS DEMAIN MATIN A SEPT HEURES POUR LA COTE OUEST", 17),
        ("CE SOIR NOUS MANGEONS DU POISSON ET DES LEGUMES DU JARDIN", 11),
    ]
    for message, cle in essais:
        chiffre = tp.cesar_chiffrer(message, cle)
        resultat = tp.forcer_cesar(chiffre)
        cle_trouvee, texte_trouve = resultat
        assert cle_trouvee == cle, (
            f"la clef utilisée était {cle}, votre programme propose {cle_trouvee}\n"
            f"  texte chiffré : {chiffre}"
        )
        assert texte_trouve == message, (
            f"la clef {cle} est bonne mais le texte ne l'est pas :\n"
            f"  attendu : {message}\n  obtenu  : {texte_trouve}"
        )


@epreuve("C.4", "le message César du TP est déchiffré")
def test_message_cesar_du_tp():
    """Le message MESSAGE_CESAR de votre fichier doit être déchiffré correctement."""
    if not hasattr(tp, "MESSAGE_CESAR"):
        raise AssertionError("la constante MESSAGE_CESAR a disparu de votre fichier")

    longueur = EMPREINTES["cesar"]["longueur"]
    cle, texte = tp.forcer_cesar(tp.MESSAGE_CESAR)
    assert longueur > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )
    assert empreinte(cle) == EMPREINTES["cesar"]["cle"], (
        f"la clef trouvée pour MESSAGE_CESAR est fausse (vous proposez {cle}). "
        "Cherchez la clef qui donne le texte le plus proche du français, "
        "autrement dit la plus petite distance au français."
    )
    assert empreinte(texte[:longueur]) == EMPREINTES["cesar"]["texte"], (
        "la clef est la bonne, mais le message déchiffré ne correspond pas.\n"
        f"  votre déchiffrement commence par : {texte[:60]}..."
    )


# ==========================================================================
# PARTIE D — historique et messages truqués
# ==========================================================================

@epreuve("D.1", "message_compromis()")
def test_message_compromis():
    """La comparaison doit ignorer espaces, casse et ponctuation."""
    document = "XWWD TXH, O'DSSURFKH. ATTAQUE A L'AUBE, PREVENEZ LE BATELIER."

    assert tp.message_compromis("ATTAQUE A L AUBE", document) is True, (
        "la phrase « ATTAQUE A L'AUBE » se retrouve bien dans le document "
        "intercepté : on attendait True"
    )
    assert tp.message_compromis("attaquons a l'aube", document) is False, (
        "« ATTAQUONS A L'AUBE » ne se trouve PAS mot pour mot dans le document "
        "(à cause du S et du N) : on attendait False"
    )
    assert tp.message_compromis("attaquons", document) is False, (
        "« attaquons » n'est pas contenu dans le document : on attendait False"
    )
    assert tp.message_compromis("FUITE", document) is False, (
        "« FUITE » ne se trouve pas dans le document : on attendait False"
    )
    assert tp.message_compromis("BATEAU", "XWWD. LE BATELIER PART DEMAIN") is False, (
        "« BATEAU » ne se trouve pas dans « LE BATELIER PART DEMAIN » "
        "(BATELIER n'est pas BATEAU) : on attendait False"
    )
    assert tp.message_compromis("batelier part", "xwwd. le batelier part demain") is True, (
        "la casse et les espaces ne doivent pas gêner : on attendait True"
    )


if __name__ == "__main__":
    sys.exit(lancer())
