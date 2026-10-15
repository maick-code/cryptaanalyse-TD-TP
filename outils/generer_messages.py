"""==========================================================================
 OUTIL DU PROFESSEUR — génération des messages chiffrés des TP
==========================================================================

Ce script lit les messages en clair dans `corriges/sources_messages.json`,
calcule les messages chiffrés, puis réécrit automatiquement :

  * les constantes des fichiers de TP des étudiants (`MESSAGE_SCYTALE`, ...) ;
  * les mêmes constantes dans les corrigés ;
  * les EMPREINTES des réponses dans les fichiers d'épreuves (`test_tpX_*.py`).

Usage (depuis la racine du dépôt) :

    python3 outils/generer_messages.py            # régénère tout
    python3 outils/generer_messages.py --verifier # vérifie sans écrire

Pourquoi des empreintes plutôt que les réponses en clair ?  Parce que les
fichiers d'épreuves sont distribués aux étudiants : s'ils contenaient les
messages en clair, ils contiendraient aussi les réponses !  Le script y range
donc l'empreinte SHA-256 du message attendu, que l'on peut comparer mais pas
retrouver.
==========================================================================
"""

from __future__ import annotations

import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from outils.reference import (  # noqa: E402
    ALPHABET_VIC,
    PERMUTATION_VIC,
    cesar_chiffrer,
    nettoyer,
    scytale_chiffrer,
    vic_chiffrer,
    vigenere_chiffrer,
)
from outils.verif import empreinte  # noqa: E402

SOURCE = os.path.join(RACINE, "corriges", "sources_messages.json")
DEBUT = "# --- DÉBUT DE LA ZONE GÉNÉRÉE (outils/generer_messages.py) ---"
FIN = "# --- FIN DE LA ZONE GÉNÉRÉE ---"

# ---------------------------------------------------------------------------
# Où écrire quoi : pour chaque fichier, la liste des constantes à y ranger.
#   (identifiant du message, nom de la constante, type de valeur)
# ---------------------------------------------------------------------------
ZONES_CONSTANTES = {
    "seance1_permutation_substitution/tp1_permutation.py": [
        ("tp1_scytale", "MESSAGE_SCYTALE", "chaine"),
        ("tp1_cesar", "MESSAGE_CESAR", "chaine"),
    ],
    "corriges/corrige_tp1_permutation.py": [
        ("tp1_scytale", "MESSAGE_SCYTALE", "chaine"),
        ("tp1_cesar", "MESSAGE_CESAR", "chaine"),
    ],
    "seance2_vigenere/tp2_vigenere.py": [
        ("tp2_vigenere1", "MESSAGE_VIGENERE_1", "chaine"),
        ("tp2_vigenere2", "MESSAGE_VIGENERE_2", "chaine"),
        ("tp2_vigenere1", "PERIODE_1", "periode"),
        ("tp2_vigenere2", "PERIODE_2", "periode"),
    ],
    "corriges/corrige_tp2_vigenere.py": [
        ("tp2_vigenere1", "MESSAGE_VIGENERE_1", "chaine"),
        ("tp2_vigenere2", "MESSAGE_VIGENERE_2", "chaine"),
        ("tp2_vigenere1", "PERIODE_1", "periode"),
        ("tp2_vigenere2", "PERIODE_2", "periode"),
    ],
    "seance3_cryptanalyse/tp3_vigenere_vic.py": [
        ("tp3_vigenere1", "MESSAGE_1", "chaine"),
        ("tp3_vigenere2", "MESSAGE_2", "chaine"),
        ("tp3_vic", "MESSAGE_VIC", "chaine"),
        ("tp3_vic", "CLE_VIC", "cle_vic"),
    ],
    "corriges/corrige_tp3_vigenere_vic.py": [
        ("tp3_vigenere1", "MESSAGE_1", "chaine"),
        ("tp3_vigenere2", "MESSAGE_2", "chaine"),
        ("tp3_vic", "MESSAGE_VIC", "chaine"),
        ("tp3_vic", "CLE_VIC", "cle_vic"),
    ],
}

# Pour chaque fichier d'épreuves, la table EMPREINTES à y ranger :
#   (identifiant du message, nom de la clef dans la table)
ZONES_EMPREINTES = {
    "seance1_permutation_substitution/test_tp1_permutation.py": [
        ("tp1_scytale", "scytale"),
        ("tp1_cesar", "cesar"),
    ],
    "seance2_vigenere/test_tp2_vigenere.py": [
        ("tp2_vigenere1", "vigenere1"),
        ("tp2_vigenere2", "vigenere2"),
    ],
    "seance3_cryptanalyse/test_tp3_vigenere_vic.py": [
        ("tp3_vigenere1", "vigenere1"),
        ("tp3_vigenere2", "vigenere2"),
        ("tp3_vic", "vic"),
    ],
}


# ---------------------------------------------------------------------------
# Préparation des messages
# ---------------------------------------------------------------------------

def preparer(messages: dict) -> dict:
    """Renvoie un dictionnaire {identifiant: dictionnaire complété} où l'on a
    ajouté `clair_prepare` (le message tel qu'il sera déchiffré) et `chiffre`."""
    resultat = {}
    for identifiant, description in messages.items():
        if identifiant.startswith("_"):
            continue
        methode = description["methode"]
        preparation = description.get("preparation", "nettoyer")

        if preparation == "nettoyer":
            clair = nettoyer(description["clair"])
        elif preparation == "majuscules":
            clair = description["clair"].upper()
        else:
            raise ValueError(f"préparation inconnue : {preparation}")

        if description.get("longueur"):
            clair = clair[: description["longueur"]]

        if methode == "scytale":
            chiffre = scytale_chiffrer(clair, description["cle"])
        elif methode == "cesar":
            chiffre = cesar_chiffrer(clair, description["cle"])
        elif methode == "vigenere":
            chiffre = vigenere_chiffrer(clair, description["cle"])
        elif methode == "vic":
            _verifier_message_vic(clair, identifiant)
            chiffre = vic_chiffrer(clair, description["cle"],
                                   description.get("cle_transposition") or PERMUTATION_VIC)
        else:
            raise ValueError(f"méthode inconnue : {methode}")

        resultat[identifiant] = dict(description)
        resultat[identifiant].update({"clair_prepare": clair, "chiffre": chiffre})
    return resultat


def _verifier_message_vic(clair: str, identifiant: str) -> None:
    """Le VIC n'accepte que les 10 lettres du damier et des blocs de 10 lettres."""
    interdites = sorted({c for c in clair if c not in ALPHABET_VIC})
    if interdites:
        raise ValueError(
            f"[{identifiant}] ces lettres n'appartiennent pas au damier VIC "
            f"{ALPHABET_VIC!r} : {', '.join(interdites)}"
        )
    reste = len(clair) % 10
    if reste:
        raise ValueError(
            f"[{identifiant}] le message VIC fait {len(clair)} lettres : il en "
            f"faudrait {10 - reste} de plus (ou {reste} de moins) pour obtenir "
            "des blocs complets de 10 lettres."
        )


# ---------------------------------------------------------------------------
# Écriture dans les fichiers
# ---------------------------------------------------------------------------

def litteral_chaine(texte: str, largeur: int = 62, nom: str = "", indentation: str = "") -> str:
    """Écrit une longue chaîne sous forme de morceaux juxtaposés de `largeur`."""
    morceaux = [texte[i:i + largeur] for i in range(0, len(texte), largeur)] or [""]
    lignes = [f"{nom} = ("] if nom else ["("]
    for morceau in morceaux:
        lignes.append(f'{indentation}    "{morceau}"')
    lignes.append(f"{indentation})" if nom else ")")
    return "\n".join(lignes)


def texte_de_la_zone(identifiant, nom, type_valeur, messages) -> str:
    message = messages[identifiant]
    if type_valeur == "chaine":
        return f"{nom} = (\n" + "".join(
            f'    "{message["chiffre"][i:i + 62]}"\n'
            for i in range(0, len(message["chiffre"]), 62)
        ) + ")"
    if type_valeur == "periode":
        return f"{nom} = {len(message['cle'])}"
    if type_valeur == "cle_vic":
        return f'{nom} = "{message["cle"]}"'
    raise ValueError(f"type de valeur inconnu : {type_valeur}")


def remplacer_zone(chemin: str, contenu: str, ecrire: bool) -> None:
    chemin_complet = os.path.join(RACINE, chemin)
    if not os.path.exists(chemin_complet):
        print(f"  (ignoré : {chemin} n'existe pas encore)")
        return
    with open(chemin_complet, encoding="utf-8") as fichier:
        ancien = fichier.read()
    if DEBUT not in ancien or FIN not in ancien:
        print(f"  /!\\ {chemin} : zone générée introuvable, fichier laissé tel quel")
        return
    debut = ancien.index(DEBUT)
    fin = ancien.index(FIN) + len(FIN)
    nouveau = ancien[:debut] + DEBUT + "\n" + contenu + "\n" + FIN + ancien[fin:]
    if ecrire and nouveau != ancien:
        with open(chemin_complet, "w", encoding="utf-8") as fichier:
            fichier.write(nouveau)
    etat = "écrit" if ecrire else "vérifié"
    print(f"  {etat} : {chemin}")


# ---------------------------------------------------------------------------
# Vérification finale : les attaques du professeur retrouvent-elles le clair ?
# ---------------------------------------------------------------------------

def verifier_attaques(messages: dict) -> bool:
    """Rejoue les attaques des corrigés sur les messages générés.

    Si l'une d'elles échoue, c'est que le message choisi est trop court, ou trop
    pauvre en français pour être cassable : il faut alors le rallonger ou le
    changer.  (C'est exactement ce que l'on demande aux étudiants de faire !)
    """
    tout_bon = True

    try:
        from corriges.corrige_tp1_permutation import attaque_scytale, forcer_cesar
    except Exception as erreur:  # noqa: BLE001
        print(f"  (corrigé du TP 1 non testé : {erreur})")
    else:
        cle, texte = attaque_scytale(messages["tp1_scytale"]["chiffre"])
        attendu = messages["tp1_scytale"]["clair_prepare"]
        if cle == messages["tp1_scytale"]["cle"] and texte[:len(attendu)] == attendu:
            print("  TP 1 / scytale : attaque réussie (clef et texte retrouvés)")
        else:
            tout_bon = False
            print("  /!\\ TP 1 / scytale : l'attaque échoue sur ce message")

        cle, texte = forcer_cesar(messages["tp1_cesar"]["chiffre"])
        attendu = messages["tp1_cesar"]["clair_prepare"]
        if cle == messages["tp1_cesar"]["cle"] and texte[:len(attendu)] == attendu:
            print("  TP 1 / César : attaque réussie (clef et texte retrouvés)")
        else:
            tout_bon = False
            print("  /!\\ TP 1 / César : l'attaque échoue sur ce message")

    try:
        from corriges.corrige_tp2_vigenere import forcer_vigenere
    except Exception as erreur:  # noqa: BLE001
        print(f"  (corrigé du TP 2 non testé : {erreur})")
    else:
        for identifiant in ("tp2_vigenere1", "tp2_vigenere2"):
            message = messages[identifiant]
            periode = len(message["cle"])
            cle, clair = forcer_vigenere(message["chiffre"], periode)
            if cle == message["cle"] and clair[:len(message["clair_prepare"])] == message["clair_prepare"]:
                print(f"  TP 2 / {identifiant} : attaque réussie (clef {cle})")
            else:
                tout_bon = False
                print(f"  /!\\ TP 2 / {identifiant} : l'attaque échoue "
                      f"(clef trouvée {cle}, attendue {message['cle']})")

    try:
        from corriges.corrige_tp3_vigenere_vic import forcer_vigenere, periode_probable
    except Exception as erreur:  # noqa: BLE001
        print(f"  (corrigé du TP 3 non testé : {erreur})")
    else:
        for identifiant in ("tp3_vigenere1", "tp3_vigenere2"):
            message = messages[identifiant]
            periode = periode_probable(message["chiffre"])
            if periode == len(message["cle"]):
                print(f"  TP 3 / {identifiant} : période {periode} retrouvée "
                      f"(vraie période : {len(message['cle'])})")
            else:
                tout_bon = False
                print(f"  /!\\ TP 3 / {identifiant} : période trouvée {periode}, "
                      f"attendue {len(message['cle'])}")
            cle, clair = forcer_vigenere(message["chiffre"], len(message["cle"]))
            if cle == message["cle"]:
                print(f"  TP 3 / {identifiant} : clef {cle} retrouvée")
            else:
                tout_bon = False
                print(f"  /!\\ TP 3 / {identifiant} : clef trouvée {cle}, "
                      f"attendue {message['cle']}")

    return tout_bon


def main() -> int:
    ecrire = "--verifier" not in sys.argv
    with open(SOURCE, encoding="utf-8") as fichier:
        messages = preparer(json.load(fichier))

    print("Messages préparés :")
    for identifiant, message in messages.items():
        print(f"  {identifiant:16s} {message['methode']:9s} "
              f"clef={message['cle']!s:12s} {len(message['clair_prepare']):4d} lettres "
              f"-> {len(message['chiffre'])} caractères chiffrés")

    print("\nVérification des attaques du professeur :")
    tout_bon = verifier_attaques(messages)

    print("\nÉcriture des constantes :")
    for chemin, plan in ZONES_CONSTANTES.items():
        contenu = "\n\n".join(
            texte_de_la_zone(identifiant, nom, type_valeur, messages)
            for identifiant, nom, type_valeur in plan
        )
        remplacer_zone(chemin, contenu, ecrire)

    print("\nÉcriture des empreintes des réponses :")
    for chemin, plan in ZONES_EMPREINTES.items():
        lignes = ["EMPREINTES = {"]
        for identifiant, nom in plan:
            message = messages[identifiant]
            lignes.append(f'    "{nom}": {{')
            lignes.append(f'        "longueur": {len(message["clair_prepare"])},')
            lignes.append(f'        "texte": "{empreinte(message["clair_prepare"])}",')
            lignes.append(f'        "cle": "{empreinte(message["cle"])}",')
            if message["methode"] == "vigenere":
                lignes.append(f'        "periode": "{empreinte(len(message["cle"]))}",')
            lignes.append("    },")
        lignes.append("}")
        remplacer_zone(chemin, "\n".join(lignes), ecrire)

    print()
    if tout_bon:
        print("Tout est cohérent : chaque message peut être cassé par le corrigé.")
    else:
        print("ATTENTION : au moins un message résiste aux attaques du corrigé.")
    return 0 if tout_bon else 1


if __name__ == "__main__":
    sys.exit(main())
