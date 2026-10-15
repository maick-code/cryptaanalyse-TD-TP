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
│   ├── tp1_permutation.py          fichier à compléter par les étudiants (6 fonctions)
│   │                               auto-suffisant : mini-cours de Python (§ A), code (§ B),
│   │                               ★ CRYPTANALYSE ★ (§ C), histoire (§ D), expériences (§ E),
│   │                               questions de rapport (§ F)
│   ├── common.py                   réexporte les outils du professeur (compatibilité)
│   └── test_tp1_permutation.py     épreuves automatiques (11)
├── seance2_vigenere/
│   ├── tp2_vigenere.py             fichier à compléter (5 fonctions) : § A cours, § B code,
│   │                               § C ★ CRYPTANALYSE ★, § D expériences, § E questions
│   └── test_tp2_vigenere.py        épreuves automatiques (10)
├── seance3_cryptanalyse/
│   ├── tp3_vigenere_vic.py         fichier à compléter (7 fonctions) : § A cours, § B analyse,
│   │                               § C ★ CRYPTANALYSE ★, § D code de VIC, § E expériences,
│   │                               § F questions
│   └── test_tp3_vigenere_vic.py    épreuves automatiques (12)
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

Les épreuves se répartissent ainsi (33 au total, dont **23 portent sur la
cryptanalyse** — les messages interceptés et les fonctions d'attaque) :

| Séance | Fonctions | Épreuves | dont ★ CRYPTANALYSE ★ |
|---|---|---|---|
| 1 | 6 | 11 | C.1 → C.8 (8) |
| 2 | 5 | 10 | C.1 → C.8 (8) |
| 3 | 7 | 12 | C.1 → C.7 (7) + D.3 (VIC) |

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
| 10 min | Définition axiomatique d'un code, Kerckhoffs, vocabulaire + les dix gestes de Python | § A du TP 1 |
| 15 min | Observation : histogramme du français, `MESSAGE_CESAR` à l'œil | expériences 1 et 3 du TP 1 |
| 20 min | B.1 `compter_lettres`, B.2–B.3 `cesar_chiffrer`/`cesar_dechiffrer` | `tp1_permutation.py` |
| 20 min | **C.1 `attaque_scytale`** : casser la permutation sans la clef | idem |
| 20 min | **C.2 `forcer_cesar`** : casser la substitution par les fréquences | idem |
| 20 min | **C.3 `identifier_et_dechiffrer`** : reconnaître la méthode, puis les cinq messages interceptés | idem, épreuves C.4 à C.8 |
| 10 min | Marie Stuart (supplément historique) | § D du TP 1 |
| 5 min | Rédaction des questions de rapport | § F du TP 1 |

La cryptanalyse occupe 60 min sur 120 : c'est volontaire, c'est le sujet du chapitre 2.

Points à installer explicitement au tableau : la scytale ne change **aucune** lettre,
donc les fréquences restent celles du français ; ce sont des **bigrammes** (paires de
lettres) qui trahissent le mauvais ordre, d'où l'usage de `vraisemblance` fourni.
Deuxième point : **l'indice de coïncidence ne sert à rien ici** (il est invariant par
décalage de l'alphabet), alors qu'il sera l'outil central du TP 3 — les étudiants
retrouveront ce fil.

Contrainte matérielle à annoncer : sur un texte trop court, toute attaque par les
fréquences se trompe — et ce n'est pas la faute de leur code. Les cas d'école des
épreuves sont dimensionnés en conséquence (60 à 180 lettres ; au TP 2, chaque colonne
doit contenir une quinzaine de lettres). Faites plutôt constater la limite que
l'affirmer : refaites `forcer_cesar` sur un message d'une vingtaine de lettres, la bonne
clef n'arrive plus en tête. C'est la leçon de méthode la plus utile de ces séances.

### Séance 2 — Vigenère (2 h)

| Temps | Contenu | Où |
|---|---|---|
| 10 min | Idée du chiffre polyalphabétique, convention sur les espaces | § A du TP 2 |
| 15 min | B.1–B.2 : mettre Vigenère en œuvre (chiffrer, déchiffrer) | `tp2_vigenere.py` |
| 10 min | **Expérience centrale** : trois histogrammes (clair, César, Vigenère) | expérience 1 du TP 2 |
| 40 min | **C.1–C.2** : une colonne = un César, puis casser trois dépêches à période donnée | idem, épreuves C.3 à C.5 |
| 25 min | **C.3** : attaque à texte clair connu, `MESSAGE_INTERCEPTE` entièrement retrouvé | idem, épreuves C.6 à C.8 |
| 15 min | Expérience 4 (clef plus longue que le texte connu), question 6 (deux messages, même clef), rédaction | § D et § E du TP 2 |

La difficulté technique de la séance est le compteur de lettres de clef : il ne
s'incrémente **que** sur les lettres (les espaces ne consomment rien). Faites écrire
au tableau le premier espace du message pour éviter l'erreur classique.

### Séance 3 — Kasiski, Friedman, VIC (2 h à 2 h 30)

| Temps | Contenu | Où |
|---|---|---|
| 10 min | Kasiski : pourquoi les distances sont des multiples de la période | § A du TP 3 |
| 20 min | B.1–B.2 : indice de coïncidence, tableau des périodes, période probable | `tp3_vigenere_vic.py` |
| 25 min | **C.1–C.2** : répétitions, distances, votes des diviseurs | idem |
| 25 min | **C.3** : période **et** clef retrouvées, les quatre dépêches déchiffrées | idem, épreuves C.4 à C.7 |
| 30 min | D.1–D.2 : VIC allégé (damier, addition de clef, transposition), `MESSAGE_VIC` | idem, épreuve D.3 |
| 10 min | Expérience 3 (croiser Kasiski et Friedman) | § E du TP 3 |
| 10 min | Synthèse : César → Vigenère → VIC → Enigma ; questions de rapport | § F du TP 3 |

Le point d'articulation de la séance est le suivant : **Kasiski seul est ambigu** (les
petits diviseurs 2, 3, 4 divisent beaucoup de distances par hasard), **l'indice de
coïncidence tranche**. Faites afficher les deux tableaux côte à côte (l'expérience 3 du
TP 3 le fait) : c'est une belle leçon de méthode.

## 4. Programme des fonctions à écrire

Chaque fichier est organisé de la même façon : `§ B` = ce qui sert à **chiffrer**,
`§ C` = ★ **CRYPTANALYSE** ★ (la partie principale), puis expériences et questions.
Seules les fonctions de `§ B` et `§ C` (et `§ D` pour le VIC) sont à écrire : tout le
reste — découpage, recollage, colonnes, tableaux, critères statistiques — est fourni dans
`outils/`.

### Séance 1 — `tp1_permutation.py` (six fonctions, 11 épreuves)

| N° | Fonction | Objectif pédagogique |
|---|---|---|
| B.1 | `compter_lettres` | dictionnaire, initialisation des 26 clefs, parcours d'une chaîne |
| B.2 | `cesar_chiffrer` | arithmétique modulaire (`% 26`), appel d'une fonction fournie |
| B.3 | `cesar_dechiffrer` | réutilisation d'un code écrit, `%` et décalage négatif |
| C.1 | `attaque_scytale` | ★ recherche exhaustive sur les clefs + critère `vraisemblance` |
| C.2 | `forcer_cesar` | ★ minimisation de `distance_au_francais` sur les 26 clefs |
| C.3 | `identifier_et_dechiffrer` | ★ choisir entre deux attaques et renvoyer la méthode trouvée |

Les épreuves C.4 à C.8 sont des **messages interceptés** à casser : `MESSAGE_SCYTALE`,
`MESSAGE_CESAR`, puis trois messages « mystère » dont la méthode elle-même est inconnue.

### Séance 2 — `tp2_vigenere.py` (cinq fonctions, 10 épreuves)

| N° | Fonction | Objectif pédagogique |
|---|---|---|
| B.1 | `vigenere_chiffrer` | compteur de lettres de clef qui doit **ignorer** espaces et ponctuation |
| B.2 | `vigenere_dechiffrer` | symétrie des deux opérations (`-decalage % 26`) |
| C.1 | `decalage_probable` | ★ une colonne = un César : chi-deux sur une colonne de texte |
| C.2 | `forcer_vigenere` | ★ `colonnes` → un César par colonne → `recoller` |
| C.3 | `cle_par_texte_connu` | ★ retrouver la clef à partir d'un fragment de texte clair connu |

Épreuves C.3 à C.5 : `MESSAGE_VIGENERE_1`, `MESSAGE_VIGENERE_2`, `MESSAGE_URGENT` (période
donnée). Épreuves C.7 et C.8 : `MESSAGE_INTERCEPTE`, avec un fragment de texte connu.

### Séance 3 — `tp3_vigenere_vic.py` (sept fonctions, 12 épreuves)

| N° | Fonction | Objectif pédagogique |
|---|---|---|
| B.1 | `indice_coincidence_moyen` | moyenne des indices des colonnes : critère de Friedman |
| B.2 | `periode_probable` | choisir la **plus petite** période au-dessus de 90 % du meilleur indice |
| C.1 | `kasiski_distances` | positions successives d'un groupe (`find`), distances sans doublon |
| C.2 | `support_kasiski` | ★ dictionnaire de votes des diviseurs de chaque distance |
| C.3 | `forcer_vigenere` | ★ attaque complète : période inconnue puis colonnes |
| D.1 | `chiffre_du_damier` | lecture d'un carré latin, addition modulo 10 |
| D.2 | `dechiffrer_message_vic` | soustraction, permutation inverse, réhabilitation du texte |

Épreuves C.4 à C.7 : les quatre dépêches `MESSAGE_1` à `MESSAGE_4`, **période inconnue**.
Épreuve D.3 : `MESSAGE_VIC` (clef fournie, comme convenu pour l'allègement).

## 4 bis. Comment le guidage est organisé (et comment noter)

Les étudiants n'ont pas de niveau en Python. Chaque fichier de TP est donc construit pour
être lu et suivi sans connaissances préalables, et **tout ce qui n'est pas la
cryptanalyse est fourni** : c'est ce qui permet de faire tenir 23 épreuves
cryptographiques dans trois séances de 2 h.

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

Suggestion de barème (sur 20) : 12 points pour les épreuves automatiques (`[OK]` comptés
sur le total de la séance : 11, 10 et 12 selon la séance), 4 points pour les questions de
rapport, 4 points pour la clarté du code et la capacité à expliquer une fonction à l'oral.
Comme 23 des 33 épreuves portent sur des messages interceptés, le barème récompense
spontanément la cryptanalyse et non la recopie des squelettes. Les blocs ✅ étant fournis, la note
de code ne doit pas récompenser la recopie, mais l'explication : faites commenter une
fonction au tableau, ou poser une question du type « que renvoie `candidat[:40]` et
pourquoi ? ».

## 5. Erreurs les plus fréquentes (à surveiller)

1. **Oublier `% 26`** : `ALPHABET[indice + cle]` provoque un `IndexError` dès qu'on dépasse
   Z. Le message d'épreuve est explicite (épreuve B.2 du TP 1).
2. **Faire consommer la clef par les espaces** (TP 2) : l'épreuve B.1 le détecte
   immédiatement grâce à un cas contenant espaces et ponctuation. Faites écrire au tableau
   le premier espace de `"LE MESSAGE ARRIVE"` : le compteur ne doit pas avancer.
3. **Découper les colonnes sur un texte qui contient encore ses espaces** : `colonnes`
   attend le texte réduit aux lettres (`vider_les_espaces`). Sinon toutes les colonnes sont
   décalées à partir du premier espace et l'attaque propose une clef fausse. C'est
   l'erreur la plus fréquente de la séance 2 (épreuve C.2), et la plus difficile à voir
   à l'œil nu : la faire écrire au tableau avant de lancer les épreuves.
4. **Comparer les fréquences des lettres pour attaquer la scytale** : la permutation ne
   change pas les comptes, elle change l'**ordre**. Il faut un modèle de bigrammes, d'où
   l'outil `vraisemblance` fourni. L'expérience 1 le montre en dix secondes, l'expérience 2
   donne le bon critère.
5. **Utiliser l'indice de coïncidence pour casser César** : il est *invariant* par décalage
   de l'alphabet. C'est pourquoi la séance 1 fournit `distance_au_francais` (khi-deux) et
   non l'indice de coïncidence ; la séance 3, elle, l'utilise pour trouver la **période**
   (l'indice d'un texte polyalphabétique n'est élevé que si l'on aligne les bonnes
   colonnes). Fil rouge à ne pas perdre : chaque instrument a son domaine de validité.
6. **Se tromper de sens dans `recoller`** : on recolle avec `i // periode` (le rang dans la
   colonne) et `i % periode` (la colonne), et non l'inverse. Le couple `divmod` est fourni
   pour cette raison.
7. **Croire qu'on peut retrouver une clef plus longue que le texte connu** (C.3 du TP 2) :
   impossible ; le message d'épreuve le dit explicitement. On ne peut aligner que les
   lettres de clef rencontrées.
8. **VIC : message mal formé** — il doit être écrit uniquement avec les dix lettres du
   damier (`ALPHABET_VIC`) et avoir une longueur multiple de 10 (l'épreuve D.2 le vérifie,
   le script de génération compte les lettres à ajouter ou à retirer). Erreur voisine :
   appliquer la transposition inverse dans le mauvais ordre, c'est-à-dire oublier de
   repasser par `permutation_inverse` avant de réhabiliter le texte.
9. **Textes trop courts** : aucun critère statistique ne fonctionne sur vingt lettres.
   Les épreuves n'utilisent que des messages dimensionnés pour cela, et les docstrings
   précisent les ordres de grandeur — à dire aux étudiants pour qu'ils ne se croient pas
   fautifs.

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
2. chiffre par la méthode demandée (`scytale`, `cesar`, `vigenere`, `vic`) ;
3. **rejoue les attaques de vos corrigés** et crie s'il y a un message impossible à
   casser (trop court, texte trop pauvre) ;
4. réécrit les zones `# --- DÉBUT DE LA ZONE GÉNÉRÉE ---` des fichiers de TP, des
   corrigés **et des fichiers d'épreuves** (les empreintes SHA-256). **Ne modifiez jamais
   ces zones à la main** : elles sont écrasées à la génération suivante.

Conséquence à retenir : si vous remplacez un fichier de TP par une nouvelle version
(ou si vous videz sa zone générée), **relancez la génération** pour réinstaller les
messages et les empreintes, puis `outils/verifier_solutions.py`. Les étiquettes
disponibles pour les empreintes sont `scytale`, `cesar`, `mystere1/2/3` (TP 1),
`vigenere1`, `vigenere2`, `urgent`, `connu` (TP 2), `vigenere1` à `vigenere4`, `vic`
(TP 3) : les fichiers d'épreuves les lisent par leur nom.

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
* **Allègement volontaire du code à écrire** : pour que la cryptanalyse tienne dans une
  séance de 2 h, les étudiants n'écrivent que 18 fonctions (6 + 5 + 7), dont 9 sont des
  attaques ; tout le reste est fourni. Le principe est explicité dans chaque fichier de
  TP : « les outils de rangement dont tu aurais besoin sont déjà écrits ; tu peux donc
  consacrer tout ton temps aux attaques ».
* **Barème robuste** : les épreuves ont été vérifiées de bout en bout, et de trois façons :
  les corrigés passent les 33 épreuves (`TP_CORRIGE=1 python3 verifier.py` → 33/33) ;
  `outils/generer_messages.py` vérifie que **chaque message intercepté est effectivement
  cassable** par le corrigé dans les conditions de la séance (période trouvée, Kasiski
  bien classé, VIC déchiffré) ; `outils/verifier_solutions.py` vérifie que recopier
  fidèlement les blocs ✅ SOLUTION suffit à obtenir 100 %. Les épreuves ne dépendent donc
  ni d'un style de programmation particulier, ni d'une interprétation de la consigne.

## 8. Aller plus loin avec les étudiants

* chapitre 3 (chiffrement en chaînes, confidentialité parfaite) : le masque jetable
  se discute très bien en prolongement de la séance 2 ;
* Enigma et les répétitions récurrentes : la méthode de Kasiski de la séance 3 en est
  le principe élémentaire ;
* l'indice de coïncidence mutuel, qui permet de retrouver la période sans référence à
  la langue (utilisable en projet sur de vrais corpus) ;
* la cryptanalyse du VIC réel, dans les TDs de l'enseignement d'origine, constitue un
  excellent sujet de projet de fin de module.
