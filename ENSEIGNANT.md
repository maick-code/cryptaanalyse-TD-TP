# Guide de l'enseignant — TP de cryptographie (chapitres 1 et 2)

Ce dépôt contient un TP Python complet accompagnant les **chapitres 1 et 2** du cours
de Pascal Boyer, *Cryptographie 2013* (Université Paris 13) :

* **chapitre 1** — Généralités : historique, présentation axiomatique d'un code, principe de Kerckhoffs ;
* **chapitre 2** — Exemples simples : codes de permutation, codes de substitution, cryptanalyse,
  codes polyalphabétiques, code de VIC.

Trois séances de 2 h chacune, à pratiquer sur machine, avec épreuves automatiques.

---

## 1. Contenu et organisation

```
cryptaanalyse-TD-TP/
├── verifier.py                     lanceur global (toutes séances, ou une seule)
├── ENSEIGNANT.md                   ce guide
├── README.md                       mode d'emploi pour les étudiants
├── outils/                         le socle commun
│   ├── reference.py                primitives écrites par le professeur (scytale, Vigenère,
│   │                               VIC simplifié, nettoyage de texte, réhabilitation)
│   ├── texte_francais.py           corpus de référence, fréquences, khi-deux,
│   │                               vraisemblance de bigrammes, indice de coïncidence
│   ├── verif.py                    mini-harnais d'épreuves (bibliothèque standard uniquement)
│   ├── generer_messages.py         outil du professeur : régénère messages et empreintes
│   └── verifier_solutions.py       outil du professeur : vérifie que les blocs ✅ SOLUTION
│                                   suffisent à passer toutes les épreuves
├── seance1_permutation_substitution/
│   ├── tp1_permutation.py          fichier à compléter par les étudiants (9 fonctions)
│   │                               auto-suffisant : mini-cours de Python, recettes,
│   │                               squelettes à trous, solutions ✅, expériences,
│   │                               questions de rapport
│   ├── common.py                   réexporte les outils du professeur (compatibilité)
│   └── test_tp1_permutation.py     épreuves automatiques (11)
├── seance2_vigenere/
│   ├── tp2_vigenere.py             fichier à compléter (10 fonctions)
│   └── test_tp2_vigenere.py        épreuves automatiques (12)
├── seance3_cryptanalyse/
│   ├── tp3_vigenere_vic.py         fichier à compléter (12 fonctions)
│   └── test_tp3_vigenere_vic.py    épreuves automatiques (14)
└── corriges/
    ├── corrige_tp1_permutation.py  corrigés complets, testés par les mêmes épreuves
    ├── corrige_tp2_vigenere.py
    ├── corrige_tp3_vigenere_vic.py
    └── sources_messages.json       messages en clair et clefs (NE PAS DISTRIBUER)
```

**Ce que l'on distribue aux étudiants** : les trois dossiers `seanceX_.../` *et* le dossier
`outils/` (indispensable aux imports). Le dossier `corriges/` reste pour vous.

## 2. Comment lancer les épreuves

Dans le dossier d'une séance :

```bash
python3 test_tp1_permutation.py          # vérifie le travail de l'étudiant
TP_CORRIGE=1 python3 test_tp1_permutation.py   # vérifie votre corrigé
```

À la racine, pour tout lancer d'un coup :

```bash
python3 verifier.py            # les trois séances (fichiers étudiants)
python3 verifier.py 2          # seulement la séance 2
TP_CORRIGE=1 python3 verifier.py   # tout, en version corrigée
```

Chaque épreuve affiche `[OK]`, `[ÉCHEC]`, `TODO non fait` ou `erreur Python : ...`
avec un message rédigé pour l'étudiant (rappel de la consigne, valeurs attendues,
pistes). Aucune dépendance externe : ni `pytest`, ni `numpy`, ni accès réseau.
Les fichiers d'épreuves sont aussi compatibles `pytest` si vos machines l'ont
(`python3 -m pytest`).

Les réponses des exercices « message intercepté » ne sont **pas** écrites en clair dans
les fichiers d'épreuves : ceux-ci contiennent des empreintes SHA-256, produites par
`outils/generer_messages.py`. Un étudiant qui lit le fichier de tests n'y trouve donc
pas la solution.

Deux outils de maintenance, à lancer après toute modification :

```bash
python3 outils/generer_messages.py     # régénère messages + empreintes, et rejoue vos attaques
python3 outils/verifier_solutions.py   # recopie les blocs ✅ SOLUTION à la place des squelettes,
                                       # lance les épreuves, puis restaure les fichiers
```

Le second répond à la question « un étudiant qui recopie fidèlement la solution imprimée
dans son fichier obtient-il bien toutes les épreuves ? ». Il garantit donc que le guidage
va bien jusqu'à la réponse, sans trou manquant.

## 3. Déroulé conseillé des séances

### Séance 1 — Généralités, permutation, substitution (2 h)

| Temps | Contenu | Où |
|---|---|---|
| 10 min | Définition axiomatique d'un code, Kerckhoffs, vocabulaire | lire le mini-cours (§ A du TP 1) |
| 15 min | Observation : histogramme du français, message intercepté | expériences 1 et 3 du TP 1 |
| 20 min | A.1 `nettoyer_simple`, A.2 `compter_lettres` | `tp1_permutation.py` |
| 25 min | B.1–B.3 : la scytale et son attaque (permutation) | idem |
| 30 min | C.1–C.3 : César, puis attaque par comparaison de fréquences | idem |
| 10 min | D.1 `message_compromis`, histoire de Marie Stuart | idem |
| 10 min | Rédaction des questions de rapport | § D du TP 1 |

Points à installer explicitement au tableau : la scytale ne change **aucune** lettre,
donc les fréquences restent celles du français ; ce sont des **bigrammes** (paires de
lettres) qui trahissent le mauvais ordre, d'où l'usage de `vraisemblance`.

### Séance 2 — Vigenère (2 h)

| Temps | Contenu | Où |
|---|---|---|
| 10 min | Idée du chiffre polyalphabétique, convention sur les espaces | rappels du cours du TP 2 |
| 20 min | A.1–A.3, B.1–B.2 : mettre Vigenère en œuvre | `tp2_vigenere.py` |
| 20 min | **Expérience centrale** : trois histogrammes (clair, César, Vigenère) | expérience 1 du TP 2 |
| 20 min | Expérience « une colonne = un César » | expérience 2 du TP 2 |
| 30 min | C.1–C.4 : casser les deux dépêches (périodes données) | `tp2_vigenere.py` |
| 15 min | D.1 : attaque à texte clair connu (méthode de Kasiski) | idem |
| 10 min | Double chiffrement, compromis du masque jetable | question 6 du TP 2 |

La difficulté technique de la séance est le compteur de lettres de clef : il ne
s'incrémente **que** sur les lettres (les espaces ne consomment rien). Faites écrire
au tableau le premier espace du message pour éviter l'erreur classique.

### Séance 3 — Kasiski, Friedman, VIC (2 h à 2 h 30)

| Temps | Contenu | Où |
|---|---|---|
| 10 min | Kasiski : pourquoi les distances sont multiples de la période | rappels du cours du TP 3 |
| 25 min | A.1–A.3 : indice de coïncidence, tableau des périodes | `tp3_vigenere_vic.py` |
| 20 min | B.1–B.3 : répétitions, distances, diviseurs + tableau de support | idem |
| 25 min | C.1–C.2 puis déchiffrement complet des deux dépêches | idem |
| 30 min | D.1–D.4 : VIC simplifié (damier, transposition, addition de clef) | idem |
| 15 min | Synthèse : César → Vigenère → VIC → Enigma ; questions de rapport | § questions du TP 3 |

Le point d'articulation de la séance est le suivant : **Kasiski seul est ambigu** (les
petits diviseurs 2, 3, 4 divisent beaucoup de distances par hasard), **l'indice de
coïncidence tranche**. Faites afficher les deux tableaux côte à côte (l'expérience 3 du
TP 3 le fait) : c'est une belle leçon de méthode.

## 4. Programme des fonctions à écrire

### Séance 1 — `tp1_permutation.py` (neuf fonctions)

| N° | Fonction | Objectif pédagogique |
|---|---|---|
| A.1 | `nettoyer_simple` | boucle, test de caractère, assemblage de chaîne |
| A.2 | `compter_lettres` | dictionnaire, initialisation des 26 clefs |
| B.1 | `cle_scytale_possibles` | divisibilité, filtrage d'une liste |
| B.2 | `decouper_en_morceaux` | slicing avec pas (`range(0, n, taille)`) |
| B.3 | `attaque_scytale` | recherche exhaustive + critère linguistique |
| C.1 | `cesar_chiffrer` | arithmétique modulaire, `ALPHABET.index` |
| C.2 | `cesar_dechiffrer` | réutilisation de code, décalage négatif |
| C.3 | `forcer_cesar` | minimisation d'une distance aux fréquences du français |
| D.1 | `message_compromis` | normalisation de texte, opérateur `in` |

### Séance 2 — `tp2_vigenere.py` (dix fonctions)

`indice_de_la_lettre`, `decaler_lettre`, `vider_les_espaces`, `vigenere_chiffrer`,
`vigenere_dechiffrer`, `forcer_cesar_sur_colonne`, `colonnes`, `recoller`,
`forcer_vigenere`, `cle_par_texte_connu`.

### Séance 3 — `tp3_vigenere_vic.py` (douze fonctions)

`indice_coincidence_moyen`, `indices_par_periode`, `periode_probable`,
`grammes_repetes`, `kasiski_distances`, `diviseurs`, `forcer_cesar_sur_colonne`,
`forcer_vigenere`, `caractere_vic`, `ligne_du_damier`, `chiffre_du_damier`,
`dechiffrer_message_vic`.

## 4 bis. Comment le guidage est organisé (et comment noter)

Les étudiants n'ont pas de niveau en Python. Chaque fichier de TP est donc construit pour
être lu et suivi sans connaissances préalables :

* **mini-cours en tête de fichier** : les dix gestes de Python utilisés (variables, chaînes,
  boucles, listes, dictionnaires, fonctions), avec des exemples courts et les cinq erreurs
  classiques ;
* **recette numérotée** en français pour chaque fonction, indépendante du code ;
* **squelette à trous** : les boucles, tests et affectations sont déjà écrits ; l'étudiant
  remplace les `...` par l'expression demandée (le commentaire en face dit ce qu'il faut
  mettre) ;
* **bloc ✅ SOLUTION** en commentaire dans le même fichier, avec la consigne orale : « tu
  essaies d'abord, tu lis la solution si tu bloques plus de cinq minutes ». La solution
  complète est donc disponible, mais il faut la recopier et la comprendre ;
* **fonctions de contrôle** en fin de fichier (`python3 tpX_....py`) qui affichent, fonction
  par fonction, « pas encore terminée » ou le résultat obtenu ;
* **expériences** à taper dans l'interpréteur (`python3`), suivies de **questions de
  rapport**.

Suggestion de barème (sur 20) : 12 points pour les épreuves automatiques (`[OK]` comptés sur
le total de la séance), 4 points pour les questions de rapport, 4 points pour la clarté du
code et la capacité à expliquer une fonction à l'oral. Les blocs ✅ étant fournis, la note
de code ne doit pas récompenser la recopie, mais l'explication : faites commenter une
fonction au tableau, ou poser une question du type « que renvoie `candidat[:40]` et
pourquoi ? ».

## 5. Erreurs les plus fréquentes (à surveiller)

1. **Oublier `% 26`** : `ALPHABET[indice + cle]` provoque un `IndexError` dès qu'on
   dépasse Z. Le message d'épreuve est explicite.
2. **Faire consommer la clef par les espaces** (séance 2) : l'épreuve B.1 le détecte
   immédiatement grâce à un cas contenant des espaces et de la ponctuation.
3. **Comparer les fréquences pour attaquer la scytale** : cela ne peut pas marcher ;
   l'épreuve B.3 échoue alors de façon incompréhensible pour l'étudiant. Il faut
   insister : la permutation ne change pas les comptes de lettres, elle change
   l'ordre, donc il faut un modèle de **bigrammes** (`vraisemblance`).
4. **Utiliser l'indice de coïncidence pour casser César** : il est *invariant* par
   décalage de l'alphabet. C'est la raison pour laquelle on fournit `distance_au_francais`
   (khi-deux) et non l'indice de coïncidence pour la séance 1. Le TP 1 le dit
   explicitement.
5. **`recoller` avec `i // periode` et `i % periode` inversés** : faire dessiner le
   tableau à deux lignes au tableau noir.
6. **Croire qu'on retrouve une clef plus longue que le texte connu** (D.1 séance 2) :
   impossible ; le message d'épreuve le dit.
7. **VIC : oublier la transposition inverse** (`permutation_inverse`) ou retirer la
   clef avant de détransposer. L'ordre des opérations est rappelé dans la docstring
   et dans le message d'échec.
8. **Textes trop courts** : aucun critère statistique ne fonctionne sur 20 lettres.
   Les épreuves n'utilisent que des messages assez longs, et les docstrings précisent
   les ordres de grandeur, pour éviter de décourager les étudiants.

## 6. Modifier les messages interceptés

Tout est centralisé dans `corriges/sources_messages.json` (réservé au professeur) :

```bash
# 1. modifier les messages/clefs dans corriges/sources_messages.json
# 2. régénérer constantes + empreintes, et vérifier que le corrigé sait encore casser
python3 outils/generer_messages.py
python3 outils/generer_messages.py --verifier   # vérifie sans écrire
```

Le script :

1. prépare les messages (nettoyage, longueur imposée) ;
2. chiaffe par la méthode demandée (`scytale`, `cesar`, `vigenere`, `vic`) ;
3. **rejoue les attaques de vos corrigés** et crie s'il y a un message impossible à
   casser (trop court, texte trop pauvre) ;
4. réécrit les zones `# --- DÉBUT DE LA ZONE GÉNÉRÉE ---` des fichiers de TP, des
   corrigés et des fichiers d'épreuves. **Ne modifiez jamais ces zones à la main.**

Contraintes à respecter pour le VIC : message écrit uniquement avec les 10 lettres du
damier (`ALPHABET_VIC = "SENATROIDL"`) et de longueur multiple de 10 ; le script
indique le nombre de lettres à ajouter ou à retirer si ce n'est pas le cas.

## 7. Choix techniques et honnêteté scientifique

* **Langue et alphabets** : les textes sont ramenés en majuscules sans accent
  (`outils/reference.nettoyer`). Le corpus de référence (`outils/texte_francais.py`)
  est un texte français d'environ 2 400 lettres, ce qui donne des fréquences très
  proches des valeurs publiées : E ≈ 16,5 %, S ≈ 8,9 %, T ≈ 7,7 %, indice de
  coïncidence ≈ 0,075.
* **Vigenère** : convention classique — les caractères non alphabétiques sont recopiés
  et ne consomment pas de lettre de clef. La séance 2 fait étudier l'autre convention
  expérimentalement (c'est un exercice du TD d'origine).
* **VIC** : nous utilisons une **version simplifiée assumée**. Le vrai VIC a quatre
  étapes, avec une clef de 5 chiffres écrite dans le message (deux fois) et un chiffre
  indicateur tiré au hasard. Ici : la clef est fournie au déchiffreur, l'indicateur est
  la position du caractère dans son bloc de 10, et le damier 10 × 10 est un carré latin
  construit comme celui du VIC (chaque ligne et chaque colonne contient les 10 lettres
  une fois). Les différences sont documentées dans `outils/reference.py`, section 5, et
  dans les rappels du cours du fichier de TP de la séance 3. Les TDs de l'enseignement de P. Boyer contiennent le
  vrai tableau du VIC : il suffit de le recopier à la place du nôtre (`TABLEAU_VIC`),
  le reste du code étant inchangé — mais il faut alors adapter la règle de conversion
  lettres ↔ chiffres, qui dépend de la table utilisée.
* **Critères statistiques fournis aux étudiants** : `distance_au_francais` (khi-deux sur
  les fréquences de lettres) pour la séance 1, `vraisemblance` (log-vraisemblance
  moyenne des bigrammes, estimée sur le corpus de référence) pour l'attaque de la
  scytale, `indice_de_coincidence` pour la séance 3. Ce sont les critères classiques du
  domaine, sous une forme utilisable en première année.
* **Code fourni lisible** : `outils/reference.py` et `outils/texte_francais.py` sont
  commentés presque ligne à ligne en français simple, pour que les étudiants puissent lire
  le code du professeur (usage de `%`, `//`, `enumerate`, dictionnaires, etc.). Les
  fichiers de TP ne comportent aucune bibliothèque externe, uniquement la bibliothèque
  standard de Python 3.
* **Barème robuste** : les épreuves ont été vérifiées contre deux implémentations
  indépendantes (le corrigé, et une seconde écriture de style différent, utilisant
  d'autres critères statistiques sur les cas marginaux). Les tests ne dépendent pas
  d'un style de programmation particulier.

## 8. Aller plus loin avec les étudiants

* chapitre 3 (chiffrement en chaînes, confidentialité parfaite) : le masque jetable
  se discute très bien en prolongement de la séance 2 ;
* Enigma et les répétitions récurrentes : la méthode de Kasiski de la séance 3 en est
  le principe élémentaire ;
* l'indice de coïncidence mutuel, qui permet de retrouver la période sans référence à
  la langue (utilisable en projet sur de vrais corpus) ;
* la cryptanalyse du VIC réel, dans les TDs de l'enseignement d'origine, constitue un
  excellent sujet de projet de fin de module.
