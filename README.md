# TP Python de cryptographie — chapitres 1 et 2

Travaux pratiques accompagnant les chapitres **1 (Généralités)** et **2 (Exemples simples :
permutation, substitution, cryptanalyse, codes polyalphabétiques, code de VIC)** du cours de
cryptographie de Pascal Boyer (Université Paris 13, *Cryptographie 2013*).

Trois séances, à pratiquer sur machine, avec vérification automatique du travail.
**Aucune installation n'est nécessaire** : ni bibliothèque à ajouter, ni accès à Internet.
Python 3 suffit.

---

## Par où commencer

```bash
python3 verifier.py          # état de votre travail, séance par séance
```

Puis, séance par séance, dans l'ordre :

| Séance | Dossier | Feuille de TD | Fichier à compléter | Épreuves |
|---|---|---|---|---|
| 1 | `seance1_permutation_substitution/` | `td1_generalites_permutation_substitution.ipynb` | `tp1_permutation.py` (9 fonctions) | `python3 test_tp1_permutation.py` |
| 2 | `seance2_vigenere/` | `td2_vigenere.ipynb` | `tp2_vigenere.py` (10 fonctions) | `python3 test_tp2_vigenere.py` |
| 3 | `seance3_cryptanalyse/` | `td3_cryptanalyse_vigenere_vic.ipynb` | `tp3_vigenere_vic.py` (12 fonctions) | `python3 test_tp3_vigenere_vic.py` |

### Programme des séances

1. **Séance 1** — définir un code comme le fait le cours ($d_k(e_k(x)) = x$), écrire une
   scytale et son attaque, écrire le code de César et le casser sans connaître la clef.
2. **Séance 2** — mettre en œuvre Vigenère, vérifier par l'expérience que l'analyse de
   fréquences globale échoue, puis la reprendre **colonne par colonne** pour déchiffrer
   deux dépêches interceptées (périodes fournies).
3. **Séance 3** — trouver la période sans aucune indication (Kasiski et indice de
   coïncidence), déchiffrer deux longues dépêches, puis découvrir le **code de VIC**
   (damier 10 × 10, addition de clef modulo 10, transposition).

## Comment travailler

1. Ouvrez la **feuille de TD** (`.ipynb`) : elle rappelle le cours, propose des
   expériences guidées et se termine par les questions de rapport.
2. Ouvrez le **fichier de TP** (`.py`) : les fonctions à écrire y sont décrites une par
   une, avec la consigne, des exemples et des indications. Remplacez chaque
   `raise NotImplementedError(...)` par votre code.
3. Après **chaque** fonction écrite, lancez les épreuves :

   ```bash
   python3 test_tp1_permutation.py
   ```

   Vous obtenez un bilan du type `Bilan : 7/11 épreuves réussies`, et pour chaque échec
   une explication en français. Relancez autant de fois que nécessaire.

4. Dans le notebook, la cellule `verifier()` fait la même chose, et `charger()` recharge
   votre fichier après modification.

### Règles du jeu

* **Ne modifiez jamais** les fichiers `test_*.py`, ni le dossier `outils/`, ni les zones
  encadrées par `# --- DÉBUT DE LA ZONE GÉNÉRÉE ---` : ils appartiennent au professeur.
* Vous pouvez toujours essayer votre code dans l'interpréteur :

  ```bash
  python3
  >>> from tp1_permutation import *
  >>> cesar_chiffrer("BONAVENTURE", 3)
  ```

* Les messages chiffrés à déchiffrer sont dans votre fichier de TP (`MESSAGE_SCYTALE`,
  `MESSAGE_CESAR`, `MESSAGE_VIGENERE_1`...). Leurs clefs sont inconnues : c'est à votre
  programme de les retrouver.

## Ce qui est fourni, ce qui est à faire

* `outils/reference.py` : les primitives déjà écrites (scytale, Vigenère, VIC simplifié,
  nettoyage de texte, transposition) — à lire, c'est du code dont vous pouvez vous
  inspirer.
* `outils/texte_francais.py` : le « modèle du français » utilisé par la cryptanalyse
  (fréquences des lettres, histogrammes, khi-deux, vraisemblance des paires de lettres,
  indice de coïncidence).
* `corriges/` : les corrigés complets, réservés au professeur.
* Tout le reste (les fonctions listées dans les fichiers de TP) est à écrire par vous.

## Rendu

Vos trois fichiers complétés (`tp1_permutation.py`, `tp2_vigenere.py`,
`tp3_vigenere_vic.py`) et les réponses aux « questions de rapport » de chaque notebook.

---

*Pour l'organisation des séances, les choix techniques et la façon de régénérer les
messages interceptés, voir `ENSEIGNANT.md`. Pour tester les corrigés :
`TP_CORRIGE=1 python3 verifier.py`.*
