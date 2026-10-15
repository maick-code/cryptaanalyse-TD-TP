# TP Python de cryptographie — chapitres 1 et 2

Travaux pratiques accompagnant les chapitres **1 (Généralités)** et **2 (Exemples simples :
permutation, substitution, cryptanalyse, codes polyalphabétiques, code de VIC)** du cours de
cryptographie de Pascal Boyer (Université Paris 13, *Cryptographie 2013*).

Trois séances à pratiquer sur machine. **Aucune installation n'est nécessaire** : ni
bibliothèque à ajouter, ni accès à Internet. Python 3 suffit.

Chaque séance comporte une **partie ★ CRYPTANALYSE ★** dédiée (section `§ C`, ou
`§ C`–`§ D` au TP 3) : c'est la partie principale du TP. Tu y attaques de vrais messages
interceptés, dont **tu ne connais pas la clef**.

---

## Si tu ne connais pas Python : lis ceci

Tu n'as pas besoin de savoir programmer pour faire ce TP. Chaque fichier de TP est écrit
pour toi, et il contient :

1. **un mini-cours de Python** (« les dix gestes ») en tête de fichier : variables,
   chaînes de caractères, boucles, listes, dictionnaires, fonctions — avec des exemples ;
2. **cinq à sept fonctions à écrire** (six au TP 1, cinq au TP 2, sept au TP 3), chacune
   sur le même modèle :

   * **OBJECTIF** : ce que la fonction doit faire ;
   * **POURQUOI (COURS)** : d'où cela vient dans le cours de cryptographie ;
   * **CE QUE TU DOIS FAIRE** : la recette, étape par étape, en français ;
   * **RAPPELS PYTHON** : l'instruction Python exacte dont tu as besoin ;
   * **À COMPLÉTER** : le squelette de la fonction : les lignes sont écrites, il te
     reste à remplacer les `...` par ce qui est demandé en commentaire ;
   * **✅ SOLUTION** : le code complet, en commentaire, que tu recopies *après avoir
     essayé* (la solution est dans ton fichier : elle est là pour t'aider, pas pour
     remplacer ton travail) ;

3. **des expériences à faire dans l'interpréteur Python** : tu observes toi-même les
   phénomènes du cours (les fréquences restent-elles ? le tableau des indices montre-t-il
   la période ?) ;
4. **des questions de rapport**, à rédiger en fin de séance.

### Le plan de chaque fichier

| Partie | TP 1 | TP 2 | TP 3 |
|---|---|---|---|
| `§ A` | les dix gestes de Python | rappels du cours sur Vigenère | rappels (Kasiski, Friedman, VIC) |
| `§ B` | ce qui sert à **chiffrer** | ce qui sert à **chiffrer** | les outils d'**analyse** |
| `§ C` | ★ **CRYPTANALYSE** ★ | ★ **CRYPTANALYSE** ★ | ★ **CRYPTANALYSE** ★ (le cœur) |
| `§ D` | histoire : Marie Stuart | expériences | code de **VIC** |
| `§ E` | expériences | questions de rapport | expériences |
| `§ F` | questions de rapport | — | questions de rapport |

Une fois que tu sais chiffrer, tu apprends à **casser** : c'est tout le sujet du
chapitre 2 du cours.

## Par où commencer

```bash
python3 verifier.py          # état de ton travail, séance par séance
```

Puis, séance par séance, dans l'ordre :

| Séance | Dossier | Fichier à compléter | Épreuves |
|---|---|---|---|
| 1 | `seance1_permutation_substitution/` | `tp1_permutation.py` (6 fonctions) | 11 épreuves — `python3 test_tp1_permutation.py` |
| 2 | `seance2_vigenere/` | `tp2_vigenere.py` (5 fonctions) | 10 épreuves — `python3 test_tp2_vigenere.py` |
| 3 | `seance3_cryptanalyse/` | `tp3_vigenere_vic.py` (7 fonctions) | 12 épreuves — `python3 test_tp3_vigenere_vic.py` |

### Programme des séances

1. **Séance 1** — définir un code comme le fait le cours ($d_k(e_k(x)) = x$), compter les
   lettres d'un texte, écrire le code de César, puis le **casser sans connaître la clef**
   et enfin **reconnaître tout seul** lequel des deux codes a été utilisé, sur **cinq
   messages interceptés**.
2. **Séance 2** — mettre en œuvre Vigenère, constater par l'expérience que l'analyse de
   fréquences globale échoue, puis la reprendre **colonne par colonne** : trois dépêches
   interceptées (périodes fournies) et une quatrième à **texte clair connu**.
3. **Séance 3** — trouver la période **sans aucune indication** (Kasiski croisé avec
   l'indice de coïncidence), déchiffrer **quatre dépêches**, puis découvrir le **code de
   VIC** (damier 10 × 10, addition de clef modulo 10, transposition) sur un message
   intercepté de plus.

## Comment travailler

1. Ouvre le fichier de TP (`.py`) dans un éditeur (Thonny, VS Code, Idle, ou n'importe
   quel traitement de texte) et lis le mode d'emploi, puis le mini-cours de Python.
2. Écris **une** fonction : remplace les `...` du squelette en suivant la recette. Si tu
   bloques plus de cinq minutes, lis le bloc ✅ SOLUTION, comprends-le, et recopie-le.
3. Lance les épreuves :

   ```bash
   python3 test_tp1_permutation.py
   ```

   Tu obtiens un bilan du type `Bilan : 7/11 épreuves réussies`, et pour chaque échec une
   explication en français. Relance autant de fois que nécessaire.

4. Tu peux toujours essayer ton code dans l'interpréteur :

   ```bash
   python3
   >>> from tp1_permutation import *
   >>> cesar_chiffrer("BONAVENTURE", 3)
   ```

5. Fais les expériences de la fin du fichier, puis réponds aux questions de rapport.

### Règles du jeu

* **Ne modifie jamais** les fichiers `test_*.py`, le fichier `common.py`, ni le dossier
  `outils/` : ils appartiennent au professeur. Tu peux les **lire** autant que tu veux :
  `outils/reference.py` est commenté presque ligne par ligne, exprès pour toi.
* Les messages chiffrés à déchiffrer sont dans ton fichier de TP (`MESSAGE_SCYTALE`,
  `MESSAGE_CESAR`, `MESSAGE_MYSTERE_1` à `_3`, `MESSAGE_VIGENERE_1` et `_2`,
  `MESSAGE_URGENT`, `MESSAGE_INTERCEPTE`, `MESSAGE_1` à `MESSAGE_4`, `MESSAGE_VIC`).
  Leurs clefs sont inconnues : c'est à ton programme de les retrouver. Les épreuves
  n'écrivent jamais la réponse en clair : elles comparent une empreinte (`empreinte` du
  module `verif`), pour que le fichier de tests ne te donne pas la solution.
* Ne modifie pas les zones encadrées par `# --- DÉBUT DE LA ZONE GÉNÉRÉE ---` : elles
  contiennent les messages interceptés, fournis par le professeur.

## Ce qui est fourni, ce qui est à faire

* `outils/reference.py` : les primitives déjà écrites (scytale, Vigenère, VIC simplifié,
  nettoyage de texte, transposition) — commentées ligne à ligne.
* `outils/texte_francais.py` : le « modèle du français » utilisé par la cryptanalyse
  (fréquences des lettres, histogrammes, khi-deux, vraisemblance des paires de lettres,
  indice de coïncidence).
* Tout le reste (les fonctions listées dans les fichiers de TP) est à écrire par toi,
  avec la recette et la solution sous les yeux. Ces outils sont fournis **exprès** : les
  manipulations de chaînes ne sont pas le sujet de la cryptographie, et ils te permettent
  de consacrer l'essentiel de la séance à la partie ★ CRYPTANALYSE ★.
* `corriges/` : les corrigés complets, réservés au professeur.

## Rendu

Tes trois fichiers complétés (`tp1_permutation.py`, `tp2_vigenere.py`,
`tp3_vigenere_vic.py`) et les réponses aux questions de rapport (qui sont en fin de chaque
fichier de TP).

---

*Pour l'organisation des séances, les choix techniques et la façon de régénérer les
messages interceptés, voir `ENSEIGNANT.md`. Pour tester les corrigés :
`TP_CORRIGE=1 python3 verifier.py`.*
