# Guide de l'enseignant — TP de cryptanalyse linéaire

Ce dépôt contient **un seul TP**, consacré à la **cryptanalyse linéaire** dans le cadre de
la **cryptographie à clé secrète** (ou symétrique) : chiffrement par blocs, boîte S,
table des approximations linéaires, lemme du piling-up, attaque du dernier tour.

Il ne suppose **aucun** prérequis de cryptographie classique : le § A reprend depuis les
bits, le XOR et la parité. Il peut donc se placer après un cours d'introduction à la
cryptographie à clé secrète, ou en fin de module.

**Durée conseillée : 3 h.** Aucune dépendance externe, Python 3 suffit.

---

## 1. Contenu et organisation

```
cryptaanalyse-TD-TP/
├── verifier.py                        lanceur : python3 verifier.py
├── ENSEIGNANT.md                      ce guide
├── README.md                          mode d'emploi pour les étudiants
├── tp_cryptanalyse_lineaire.py        fichier à compléter (12 fonctions + 1 bonus)
│                                      § A cours (clé secrète, XOR, biais), § B boîte S/LAT,
│                                      § C SPN-8, § D ★ CRYPTANALYSE ★, § E expériences,
│                                      § F questions, § G exercices
├── donnees_lineaire.py                2 000 couples clair-chiffré (zone générée)
├── test_tp_cryptanalyse_lineaire.py   épreuves automatiques (16)
├── outils/
│   ├── lineaire.py                    socle : boîte S, SPN-8 de référence, LAT,
│   │                                  diversification, attaque de référence, statistiques
│   ├── verif.py                       mini-harnais d'épreuves (bibliothèque standard)
│   ├── generer_donnees_lineaire.py    outil du professeur : régénère données, calibre
│   │                                  la clé, réécrit les empreintes
│   └── verifier_solutions.py          outil du professeur : vérifie que les blocs
│                                      ✅ SOLUTION suffisent à passer toutes les épreuves
└── corriges/
    ├── corrige_tp_cryptanalyse_lineaire.py   corrigé complet, mêmes épreuves
    ├── corrige_exercices_lineaire.md         corrigé des exercices papier et du barème
    └── sources_lineaire.json                 clé maître et graine (NE PAS DISTRIBUER)
```

**Ce que l'on distribue aux étudiants** : `tp_cryptanalyse_lineaire.py`,
`donnees_lineaire.py`, `test_tp_cryptanalyse_lineaire.py`, `verifier.py` et le dossier
`outils/`. Le dossier `corriges/` reste pour vous.

## 2. Comment lancer les épreuves

Depuis la racine du dépôt :

```bash
python3 verifier.py                  # fichier des étudiants
TP_CORRIGE=1 python3 verifier.py     # corrigé du professeur (16/16 attendu)
```

Ou directement :

```bash
python3 test_tp_cryptanalyse_lineaire.py
TP_CORRIGE=1 python3 test_tp_cryptanalyse_lineaire.py
```

Vérifications de cohérence, à faire après toute modification du TP :

```bash
python3 outils/verifier_solutions.py           # recopier les ✅ donne-t-il 16/16 ?
python3 outils/generer_donnees_lineaire.py --verifier   # données conformes ?
```

## 3. Déroulé conseillé (3 h)

| Temps | Contenu | Où |
|---|---|---|
| 15 min | Cryptographie à clé secrète, Kerckhoffs, chiffrement par blocs, confusion/diffusion, modèle clair connu | § A du TP |
| 15 min | XOR, parité, masques ; les trois biais (`p`, `δ`, `ρ`) | § A du TP |
| 15 min | B.1–B.2 : parité masquée, boîte S | `tp_cryptanalyse_lineaire.py` |
| 20 min | B.3–B.4 : `S⁻¹`, puis la LAT ; **expérience 1** | idem |
| 25 min | C.1–C.2 : couche linéaire P, chiffrement SPN-8, vecteurs de test | idem |
| 15 min | **Expérience 2** : les trois biais de la trace `9 → 2 → 13` | § E du TP |
| 35 min | **D.1–D.3** : compter la relation, classer les 16 candidats, groupe de tête | idem |
| 30 min | **D.4–D.6** : clés candidates, vérification, attaque complète avec statuts | idem |
| 20 min | **Expérience 5** : à partir de quel `N` l'attaque est-elle fiable ? limites | § E |
| 10 min | Questions de rapport, exercices papier 1 à 3 | § F et § G |

Trois points à installer au tableau, dans cet ordre :

1. **le signe ne compte pas.** Le score `|2c − N|` mesure un écart au hasard ; un candidat
   à `p = 0,25` est aussi intéressant qu'un candidat à `p = 0,75`. C'est pourquoi
   plusieurs candidats sont à égalité (ici quatre), et pourquoi on conserve un **groupe**
   avant de vérifier ;
2. **le piling-up n'est pas une mesure.** Il prédit `p = 0,4375` ; le biais exact de la
   clé du jeu de données vaut `0,25` et `0,875`. L'écart n'est pas une erreur de calcul :
   les tours ne sont pas indépendants et plusieurs traces contribuent ;
3. **une attaque peut échouer**, et le programme doit le dire. Les statuts `elargie`,
   `incertaine` et `echec` sont là pour cela ; il n'y a aucune recherche exhaustive de
   secours. L'expérience 5 le montre sur de petits échantillons.

## 4. Les fonctions à écrire

| N° | Fonction | Objectif pédagogique |
|---|---|---|
| B.1 | `parite_masque` | XOR d'un mot, `bin(...).count("1") % 2` |
| B.2 | `appliquer_sbox` | extraction et recollement de quartets (`>>`, `&`, `<<`, `\|`) |
| B.3 | `sbox_inverse` | bijection, recherche d'antécédent |
| B.4 | `table_approximations` | double boucle, comptage, `LAT = #solutions − 8` |
| C.1 | `permuter` | couche linéaire, involution |
| C.2 | `chiffrer` | composition de fonctions, ordre des opérations, clés de tour |
| C.3 | `dechiffrer` (bonus) | inversion d'un chiffrement, ordre inverse |
| D.1 | `compter_relation` | ★ déchiffrement partiel du dernier tour, comptage |
| D.2 | `attaquer_quartet` | ★ score `\|2c − N\|`, tri, 16 candidats |
| D.3 | `groupe_de_tete` | ★ seuil relatif, gestion des ex æquo et des scores nuls |
| D.4 | `cle_candidates` | ★ bijection `M → K3`, filtrage par deux groupes |
| D.5 | `verifier_cles` | ★ vérification sur couples connus (le critère du cryptanalyste) |
| D.6 | `attaquer_cle` | ★ élargissement progressif, quatre statuts, refus de conclure |

Les épreuves B.5, C.3 et D.7–D.8 vérifient les valeurs de la trace, la sensibilité à la
clé et les **limites** (élargissement, échec, comparaison biais exact / mesuré / piling-up).

## 4 bis. Comment le guidage est organisé (et comment noter)

Chaque fonction suit le même plan, pour être lisible sans connaissances préalables :

* **OBJECTIF** : ce que la fonction doit faire ;
* **POURQUOI (COURS)** : son rôle dans la cryptanalyse linéaire ;
* **CE QUE TU DOIS FAIRE** : la recette numérotée, en français, indépendante du code ;
* **RAPPELS PYTHON** : l'instruction exacte dont l'étudiant a besoin ;
* **squelette à trous** : les boucles et affectations sont écrites, il reste les `...` ;
* **✅ SOLUTION** en commentaire, avec la consigne orale : « tu essaies d'abord, tu lis la
  solution si tu bloques plus de cinq minutes ».

Suggestion de barème (sur 20) : 12 points pour les épreuves automatiques, 4 points pour
les questions de rapport, 4 points pour la clarté du code et la capacité à expliquer une
fonction à l'oral. Pour le détail, voir `corriges/corrige_exercices_lineaire.md` : il
propose un barème qui valorise particulièrement l'exercice 5 (diagnostic d'un échec),
le plus discriminant.

## 5. Erreurs les plus fréquentes (à surveiller)

1. **Confondre les deux traces.** `depart_haut=False` (trace basse) sert à retrouver
   **K3_HAUT** ; `depart_haut=True` (trace haute) sert à retrouver **K3_BAS**. C'est
   contre-intuitif, et c'est l'erreur la plus fréquente de la séance. Le message de
   l'épreuve D.4 la signale explicitement.
2. **Croire que « mauvais candidat » = « biais nul ».** Faux, et c'est mesuré. Sur notre
   clé, quatre candidats ont exactement le même score que le bon, et 522 couples
   (clé, candidat) faux de l'ensemble des 256 clés ont `|δ| ≥ 0,25`. Faites afficher les
   16 comptes (expérience 3) avant de parler de « bruit ».
3. **Confondre les trois biais.** Le piling-up (`0,4375`) est une **prédiction**, le biais
   exact (`0,25` / `0,875`) est une propriété du chiffre pour cette clé, le biais mesuré
   (`≈ 0,258` / `0,873`) est une **estimation** sur 2 000 couples. Les trois interviennent
   à des titres différents ; le § A les définit.
4. **Vouloir « sauver » une attaque qui échoue.** Le statut `echec` n'est pas un bug.
   Interdire toute recherche exhaustive de secours est un choix pédagogique explicite :
   on préfère un échec signalé à une réussite maquillée.
5. **Oublier que le score est une valeur absolue.** Il met à égalité `p = 0,25` et
   `p = 0,75`. Ce n'est pas un défaut du programme mais une conséquence mathématique, et
   c'est ce qui rend la vérification (D.5) indispensable.
6. **Textes trop courts** : aucun critère statistique ne fonctionne sur vingt couples.
   Les expériences 5 et l'épreuve D.7 font constater la limite plutôt que l'affirmer.

## 6. Régénérer les données

La clé, la graine et le nombre de couples sont dans `corriges/sources_lineaire.json` :

```bash
python3 outils/generer_donnees_lineaire.py              # régénère données + empreintes
python3 outils/generer_donnees_lineaire.py --verifier   # vérifie sans écrire
python3 outils/generer_donnees_lineaire.py --calibrer   # cherche une clé admissible
```

Le script refuse d'écrire si l'attaque ne retrouve pas la clé, ou si les biais, groupes et
candidats ne sont pas ceux qu'annonce le TP. Il réécrit la zone générée de
`donnees_lineaire.py` et les empreintes (`cle_maitre`, `groupe_haut`, `groupe_bas`,
`candidats`, `donnees`) du fichier d'épreuves. **Ne modifiez jamais ces zones à la main.**

**Si vous changez la clé, relisez le § 7** : sur les 256 clés possibles, 13 seulement
conviennent. Le mode `--calibrer` les cherche pour vous.

## 7. Choix techniques et honnêteté scientifique

### Le chiffre

SPN-8 : bloc de 8 bits, deux quartets, boîte S de PRESENT (biais maximal `1/4`), couche
linéaire = échange des quartets, trois tours, clé maître de 8 bits diversifiée en quatre
clés de tour. Ce format tient dans une séance de 3 h et permet l'attaque du dernier tour
sur **16 candidats** par quartet. Le TD de référence (Bombar, TD 6) travaille sur 32 bits
avec SageMath : mêmes concepts, coût machine sans commune mesure.

### La trace

`9 → 2 → 13` sur **deux** tours. La troisième approximation n'est pas ajoutée parce
qu'une trace qui traverse les trois tours se termine sur la *sortie* de la boîte S du
dernier tour, qui dépend des 8 bits de `K3` : il faudrait alors 256 candidats, et
l'attaque ne gagnerait plus rien. C'est une erreur de conception à éviter si vous
modifiez le chiffre.

### Les trois biais

Le TP distingue `p`, `δ = p − 1/2` et `ρ = 2p − 1`, et n'emploie jamais « epsilon » sans
le définir. Le piling-up s'écrit `ρ_total = ∏ ρ_i`, donc `p = 1/2 + ρ_total/2`, ce qui est
équivalent à `p = 1/2 + 2^(m−1) ∏ δ_i`. Les deux écritures sont vérifiées par
l'exercice 3.

### Le calibrage est assumé

Sur un bloc de 8 bits, le biais exact dépend de la clé et peut être **nul** : 80 clés sur
256 ont un biais nul dans une orientation donnée, et seules 13 remplissent les conditions
du TP. `M = 19` a été choisie pour cela. Sans ce calibrage, une clé sur deux environ
rendrait l'attaque impossible — ce qui serait une mauvaise surprise en TP, mais qui est
une propriété réelle du chiffre. L'expérience 6 le montre aux étudiants, et la question 4
leur demande de l'expliquer.

### Les limites sont documentées, pas masquées

`attaquer_cle` renvoie un statut (`certaine`, `elargie`, `incertaine`, `echec`) et ne fait
**jamais** de recherche exhaustive de secours. Les épreuves D.7 vérifient deux cas
déterministes : sur `PAIRES[0:10]` l'attaque doit élargir, sur `PAIRES[60:70]` elle doit
échouer.

**Fiabilité mesurée** (300 tirages aléatoires dans les 2 000 couples, clé `M = 19`) :

| `N` | certaine | élargie | échec | clé correcte | faux positifs |
|---:|---:|---:|---:|---:|---:|
| 20 | 123 | 146 | 31 | 269/300 | 0 |
| 50 | 172 | 119 | 9 | 291/300 | 0 |
| 100 | 222 | 77 | 1 | 299/300 | 0 |
| 200 | 251 | 49 | 0 | 300/300 | 0 |
| 400 | 293 | 7 | 0 | 300/300 | 0 |
| 1 000 | 300 | 0 | 0 | 300/300 | 0 |
| 2 000 | 300 | 0 | 0 | 300/300 | 0 |

À `N = 2 000`, le seuil 0,8 suffit toujours et l'attaque ne se trompe jamais sur ces
300 tirages. En dessous de 200 couples, les statuts `elargie` et `echec` apparaissent :
c'est exactement ce que l'expérience 5 fait observer, et ce que l'épreuve D.7 vérifie.
Aucun faux positif n'a été observé, mais la garantie n'est pas absolue : c'est une
probabilité, pas un théorème.

### Les mauvais candidats ne sont pas équilibrés

Le TP mesure (D.2, expérience 3) que plusieurs candidats faux atteignent le score du bon.
L'exercice 5 va plus loin : à un tour, aucun candidat vrai n'est même dans le groupe.
C'est une limite structurelle de l'attaque linéaire à une approximation de 4 bits.

### Barème robuste

Les épreuves ont été vérifiées de trois façons : le corrigé passe les 16 épreuves
(`TP_CORRIGE=1 python3 verifier.py` → 16/16) ; `outils/generer_donnees_lineaire.py`
vérifie que l'attaque retrouve la clé et que les valeurs annoncées sont exactes ;
`outils/verifier_solutions.py` vérifie que recopier fidèlement les blocs ✅ SOLUTION suffit
à obtenir 100 %. Les épreuves ne dépendent donc ni d'un style de programmation
particulier, ni d'une interprétation de la consigne.

## 8. Aller plus loin avec les étudiants

* **Matsui 1 et 2** : remonter les clés tour par tour (voir l'exercice 5, qui montre
  justement pourquoi c'est difficile sur ce chiffre).
* **Cryptanalyse différentielle** : monter la même attaque avec des différences, et
  comparer les deux taux de succès à nombre de couples égal. Excellent sujet de projet.
* **SPN-16** : quatre boîtes S et une permutation de bits ; l'attaque porte alors sur
  256 candidats par quartet. Bonne transition vers les chiffres réels.
* **DES et AES** : relier le biais `1/4` de nos boîtes S aux biais de `~10^-6` du DES, et
  calculer pourquoi Matsui avait besoin de `2^47` couples.
* **Modes d'opération** : après avoir cassé un bloc, discuter CBC, CTR et l'effet d'un
  mode sur les attaques à clair connu.
* **Lecture du TD d'origine** (M. Bombar, TD 6) : même sujet, 32 bits, SageMath.
