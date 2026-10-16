"""==========================================================================
 ÉPREUVES AUTOMATIQUES DU TP 3  (ne pas modifier ce fichier)
==========================================================================
Pour vérifier votre travail, tapez dans un terminal, dans ce dossier :

    python3 test_tp3_vigenere_vic.py

Chaque épreuve réussie s'affiche « [OK] », chaque épreuve ratée « [ÉCHEC] »
avec l'explication.

Les épreuves des parties B, C et D sont celles de la CRYPTANALYSE : trouver la
période sans aucune indication, casser les dépêches, puis déchiffrer un message
du code de VIC.  Le fichier ne contient que des EMPREINTES (SHA-256) des
réponses : vous ne pouvez donc pas tricher en le lisant.
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
    ALPHABET,
    caractere_vic,
    colonnes,
    vider_les_espaces,
    vic_chiffrer,
    vigenere_chiffrer as vigenere_chiffrer_reference,
)

# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---
EMPREINTES = {
    "vigenere1": {
        "longueur": 620,
        "texte": "6e9788b7a06f5e9f4947c322ab403797265efe913369e7f07edeca2c33778ac3",
        "cle": "9122217c16ac79733338b07428c95b67ee7240a4d69f6580d14a7c6505fef172",
        "methode": "59634baee12f7567c95b1aee0b104300aad5be4073d5e363b257c50346019b05",
        "periode": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
    },
    "vigenere2": {
        "longueur": 700,
        "texte": "8e2c8c45afaa1e3f869a4bb33e5d9e1a850a959aad0e5bb145710e7ab961597a",
        "cle": "269dc135897f427830329acc2c45b49557050472c6d4e7246ec6d90e51ad301f",
        "methode": "59634baee12f7567c95b1aee0b104300aad5be4073d5e363b257c50346019b05",
        "periode": "7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451",
    },
    "vigenere3": {
        "longueur": 540,
        "texte": "d1f57e7bbb5a8eea41f0d06924897c9fbe402ef42f843d78f01740fe983cc8c6",
        "cle": "54b3ab0c04942c2e051ada940c940b12260437d6973e516f395082bc62fe274a",
        "methode": "59634baee12f7567c95b1aee0b104300aad5be4073d5e363b257c50346019b05",
        "periode": "2c624232cdd221771294dfbb310aca000a0df6ac8b66b696d90ef06fdefb64a3",
    },
    "vigenere4": {
        "longueur": 300,
        "texte": "558f7a8ae6c8512c56b7bdd7c0642acae0550b9fcb04bb1031c2502d3334833f",
        "cle": "5a26316ae6c2a43ea8eaa4b452ad5ac315b38f6201c88e21516708df1c8fa80f",
        "methode": "59634baee12f7567c95b1aee0b104300aad5be4073d5e363b257c50346019b05",
        "periode": "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",
    },
    "vic": {
        "longueur": 80,
        "texte": "46c49bb04aba374ed308c86c531c2ade68d6f1b40c58a16d87808067ed8d9f3d",
        "cle": "b2a2f01fd91682e4f012509566bc45c88c6cfa43171b6d7d16cff44572ebf57b",
        "methode": "c520993fd56626d5a52045521e6e3192a16838b8193b76b9448c99f35039730f",
    },
}
# --- FIN DE LA ZONE GÉNÉRÉE ---


def _verifier_depache(nom, periode, cle, clair):
    """Compare une dépêche déchiffrée aux empreintes du professeur."""
    attendu = EMPREINTES[nom]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )

    assert empreinte(periode) == attendu["periode"], (
        f"la période trouvée est fausse (vous proposez {periode}).\n"
        "  Rappel de la méthode : c'est la plus PETITE période dont l'indice de "
        "coïncidence atteint 90 % du meilleur.\n"
        "  Astuce : affichez indices_par_periode(message, 15) ; les multiples de "
        "la vraie période ressortent souvent (2p, 3p...) — il faut prendre la "
        "plus petite qui « marche »."
    )

    assert empreinte(cle) == attendu["cle"], (
        f"la période est bonne, mais la clef est fausse (vous proposez {cle!r}).\n"
        "  Chaque colonne doit être attaquée séparément : décalage 0 -> A, "
        "1 -> B, etc.\n"
        "  Une seule colonne mal reconnue suffit à changer une lettre de clef."
    )

    clair = clair[: attendu["longueur"]]
    assert empreinte(clair) == attendu["texte"], (
        "la période et la clef sont bonnes, mais le texte déchiffré ne "
        "correspond pas.\n"
        f"  votre déchiffrement commence par : {clair[:60]}...\n"
        "  Vérifiez le recollement des colonnes (outil `recoller`)."
    )


# ==========================================================================
# § B — les outils d'analyse
# ==========================================================================

@epreuve("B.1", "indice_coincidence_moyen()")
def test_indice_coincidence_moyen():
    """L'indice doit être élevé sur la vraie période, faible sinon."""
    assert tp.indice_coincidence_moyen("ABAB", 2) == 1.0, (
        "pour 'ABAB' avec la période 2, les colonnes sont 'AA' et 'BB' : deux "
        "lettres tirées dans 'AA' sont toujours égales, l'indice vaut donc 1.0 ; "
        f"on obtient {tp.indice_coincidence_moyen('ABAB', 2)}"
    )
    assert tp.indice_coincidence_moyen("", 3) == 0.0, (
        "un texte vide doit renvoyer 0.0 (et non provoquer une division par zéro)"
    )

    # Sur un vrai message : 0,075 pour la bonne période, bien moins sinon.
    clair = vider_les_espaces(
        "LE CONSEIL DE LA NATION SE REUNIT DEMAIN MATIN A HUIT HEURES DEVANT "
        "LA GRANDE PORTE DU PALAIS ET LE DIRECTEUR DU PORT A RECU NOTRE LETTRE"
    )
    chiffre = vigenere_chiffrer_reference(clair, "PILOTE")
    vrai = tp.indice_coincidence_moyen(chiffre, 6)
    faux = tp.indice_coincidence_moyen(chiffre, 4)
    assert vrai > 0.07, (
        f"pour la vraie période (6), l'indice moyen doit dépasser 0,07 : "
        f"on obtient {vrai:.4f}\n  Le texte est-il bien découpé en colonnes "
        "(outil `colonnes`) ?"
    )
    assert faux < 0.06, (
        f"pour une période fausse (4), l'indice moyen doit rester sous 0,06 : "
        f"on obtient {faux:.4f}"
    )


@epreuve("B.2", "periode_probable()")
def test_periode_probable():
    """La période trouvée doit être la vraie, pour plusieurs longueurs de clef."""
    for cle in ["TAMBOUR", "MARINE", "PILOTE", "GALERE"]:
        clair = vider_les_espaces(
            "LE COURRIER ARRIVE DEUX FOIS PAR SEMAINE PAR LE BATEAU DE LA COTE "
            "ET LES NOUVELLES DU PORT SONT TOUJOURS ATTENDUES AVEC IMPATIENCE "
            "PAR LES HABITANTS DE LA VILLE ET PAR LES MARINS DU QUARTIER QUI "
            "VIENNENT CHAQUE SOIR SUR LE QUAI POUR REGARDER LES BATEAUX RENTRER "
            "AU PORT AVANT LA NUIT TOMBEE CAR LE PILOTE DU PORT ANNONCE QUE LA "
            "MER SERA GROSSE DEMAIN MATIN ET QUE LES PETITS BATEAUX DEVRONT "
            "RESTER A QUAI JUSQUA NOUVEL ORDRE DU CAPITAINE DU PORT"
        )
        chiffre = vigenere_chiffrer_reference(clair, cle)
        periode = tp.periode_probable(chiffre)
        assert periode == len(cle), (
            f"avec une clef de {len(cle)} lettres ({cle!r}), votre fonction "
            f"propose la période {periode}\n"
            "  Rappel : on prend la PLUS PETITE période qui atteint 90 % du "
            "meilleur indice, et non la plus grande."
        )


# ==========================================================================
# § C — ★ CRYPTANALYSE DE VIGENÈRE ★
# ==========================================================================

@epreuve("C.1", "kasiski_distances()")
def test_kasiski_distances():
    """Les distances entre répétitions doivent être exactes et triées."""
    essais = [
        ("ABCXABCXXXABC", "ABC", [4, 6]),
        ("ABABAB", "AB", [2]),
        ("ABCDE", "ZZ", []),
        ("XABCYABCZABCWABC", "ABC", [4]),   # même distance : sans doublon
    ]
    for chiffre, mot, attendu in essais:
        resultat = tp.kasiski_distances(chiffre, mot)
        assert resultat == attendu, (
            f"pour le groupe {mot!r} dans {chiffre!r}, on attendait {attendu}, "
            f"on obtient {resultat}\n"
            "  Les distances se calculent entre positions CONSÉCUTIVES, sans "
            "doublon."
        )


@epreuve("C.2", "support_kasiski()")
def test_support_kasiski():
    """Chaque distance doit faire voter tous ses diviseurs (2 à maximum)."""
    # 'ABC' apparaît aux positions 1, 5 et 10 : distances 4 et 5.
    # Diviseurs de 4 (entre 2 et 10) : 2 et 4.   Diviseurs de 5 : 5.
    resultat = tp.support_kasiski("XABCYABCZZABC", taille=3, maximum=10)
    attendu = {2: 1, 4: 1, 5: 1}
    assert resultat == attendu, (
        "pour 'XABCYABCZZABC' : 'ABC' apparaît aux positions 1, 5 et 10, donc "
        "les distances sont 4 et 5.\n"
        "  La distance 4 fait voter 2 et 4 ; la distance 5 fait voter 5.\n"
        f"  on attendait {attendu}, on obtient {resultat}\n"
        "  (le diviseur 1 est ignoré : il divise tout, il ne prouve rien, et les "
        "distances identiques sont comptées une seule fois)"
    )

    # Sur une vraie dépêche, la vraie période doit être bien classée... sans être
    # forcément première : c'est pourquoi on croise avec l'indice de coïncidence.
    support = tp.support_kasiski(tp.MESSAGE_2)
    assert support, (
        "sur MESSAGE_2, aucun groupe répété n'a été trouvé : vérifiez que vous "
        "utilisez bien l'outil `grammes_repetes` avec la taille donnée"
    )

    # Retrouver la vraie période SANS l'écrire dans ce fichier : on la cherche
    # parmi les périodes possibles par empreinte (le fichier de tests est
    # distribué aux étudiants, il ne doit pas contenir la réponse en clair).
    vraie_periode = None
    for candidat in range(2, 16):
        if empreinte(candidat) == EMPREINTES["vigenere2"]["periode"]:
            vraie_periode = candidat
            break
    assert vraie_periode is not None, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )

    classement = sorted(support, key=lambda p: (-support[p], p))
    assert vraie_periode in classement[:5], (
        f"la vraie période de MESSAGE_2 devrait figurer parmi les cinq "
        f"meilleures candidates de Kasiski ; votre classement commence par "
        f"{classement[:5]}\n"
        "  Vérifiez que chaque distance fait bien voter TOUS ses diviseurs."
    )


@epreuve("C.3", "forcer_vigenere()")
def test_forcer_vigenere():
    """L'attaque complète, période connue (comme au TP 2, mais avec vos outils)."""
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
        # Les dépêches de ce TP sont fournies en lettres seules.
        clair = vider_les_espaces(clair)
        chiffre = vigenere_chiffrer_reference(clair, cle)
        cle_trouvee, clair_trouve = tp.forcer_vigenere(chiffre, len(cle))
        assert cle_trouvee == cle, (
            f"la clef utilisée était {cle!r}, votre attaque propose "
            f"{cle_trouvee!r}\n  message chiffré : {chiffre[:80]}..."
        )
        assert clair_trouve[:len(clair)] == clair, (
            f"la clef {cle!r} est bien trouvée, mais le texte ne correspond "
            f"pas :\n  attendu : {clair[:80]}\n  obtenu  : {clair_trouve[:80]}"
        )


@epreuve("C.4", "la dépêche MESSAGE_1 est déchiffrée")
def test_message_1():
    """Première dépêche : période inconnue (c'est nouveau !)."""
    periode = tp.periode_probable(tp.MESSAGE_1)
    cle, clair = tp.forcer_vigenere(tp.MESSAGE_1, periode)
    _verifier_depache("vigenere1", periode, cle, clair)


@epreuve("C.5", "la dépêche MESSAGE_2 est déchiffrée")
def test_message_2():
    """Deuxième dépêche : période inconnue."""
    periode = tp.periode_probable(tp.MESSAGE_2)
    cle, clair = tp.forcer_vigenere(tp.MESSAGE_2, periode)
    _verifier_depache("vigenere2", periode, cle, clair)


@epreuve("C.6", "la dépêche MESSAGE_3 est déchiffrée")
def test_message_3():
    """Troisième dépêche, jamais vue : période inconnue."""
    periode = tp.periode_probable(tp.MESSAGE_3)
    cle, clair = tp.forcer_vigenere(tp.MESSAGE_3, periode)
    _verifier_depache("vigenere3", periode, cle, clair)


@epreuve("C.7", "la dépêche MESSAGE_4 est déchiffrée")
def test_message_4():
    """Quatrième dépêche, plus courte donc plus difficile : période inconnue."""
    periode = tp.periode_probable(tp.MESSAGE_4)
    cle, clair = tp.forcer_vigenere(tp.MESSAGE_4, periode)
    _verifier_depache("vigenere4", periode, cle, clair)


# ==========================================================================
# § D — code de VIC
# ==========================================================================

@epreuve("D.1", "chiffre_du_damier()")
def test_chiffre_du_damier():
    """Le déchiffrement d'un caractère doit défaire le chiffrement."""
    for chiffre_message in (0, 3, 7, 9):
        for chiffre_clef in (0, 1, 5, 9):
            for position in (0, 4, 9):
                lettre = caractere_vic(chiffre_message, chiffre_clef, position)
                resultat = tp.chiffre_du_damier(lettre, chiffre_clef, position)
                assert resultat == chiffre_message, (
                    f"le chiffre {chiffre_message} a été transformé en lettre "
                    f"{lettre!r} avec le chiffre de clef {chiffre_clef} et la "
                    f"position {position} ; votre fonction propose "
                    f"{resultat} au lieu de {chiffre_message}\n"
                    "  Rappel : ligne = (message + clef) % 10, donc "
                    "message = (ligne - clef) % 10."
                )


@epreuve("D.2", "dechiffrer_message_vic()")
def test_dechiffrer_message_vic():
    """Le déchiffrement doit être l'inverse exact du chiffrement."""
    messages = [
        ("SENATORILTROISLIONST", "12345"),
        ("LIONSENATO", "5241730219"),
        ("DANSLESENTIERSOTROIS", "7"),
    ]
    for message, cle in messages:
        chiffre = vic_chiffrer(message, cle)
        resultat = tp.dechiffrer_message_vic(chiffre, cle)
        assert resultat == message, (
            f"le message {message!r} chiffré par la clef {cle!r} devient "
            f"{chiffre!r} ; votre déchiffrement redonne {resultat!r}\n"
            "  Les quatre étapes se refont à l'envers : damier, transposition, "
            "retrait de la clef, chiffres -> lettres."
        )


@epreuve("D.3", "le message MESSAGE_VIC est déchiffré")
def test_message_vic():
    """Le message du VIC, avec la clef fournie par le professeur."""
    assert tp.MESSAGE_VIC and tp.CLE_VIC, (
        "les constantes MESSAGE_VIC et CLE_VIC ne doivent pas être modifiées : "
        "elles contiennent le message intercepté et sa clef"
    )
    attendu = EMPREINTES["vic"]
    assert attendu["longueur"] > 0, (
        "les empreintes n'ont pas été générées : lancez "
        "« python3 outils/generer_messages.py » (réservé au professeur)"
    )

    resultat = tp.dechiffrer_message_vic(tp.MESSAGE_VIC, tp.CLE_VIC)
    resultat = resultat[: attendu["longueur"]]
    assert empreinte(resultat) == attendu["texte"], (
        "le message VIC n'est pas déchiffré correctement.\n"
        f"  votre résultat commence par : {resultat[:60]}...\n"
        "  Vérifiez l'ordre des étapes : (4) lettres -> chiffres avec le damier, "
        "(3) transposition défaite, (2) retrait de la clef, (1) chiffres -> "
        "lettres."
    )


if __name__ == "__main__":
    sys.exit(lancer())
