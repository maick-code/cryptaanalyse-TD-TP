# TP Python — cryptanalyse linéaire (cryptographie à clé secrète)

Travaux pratiques de **cryptanalyse linéaire**, la méthode inventée par Mitsuru Matsui en
1993 pour attaquer le DES. Le cadre est celui de la **cryptographie à clé secrète** (ou
symétrique) : une même clé sert à chiffrer et à déchiffrer, l'algorithme est public, seule
la clé est secrète.

**Aucune installation n'est nécessaire** : ni bibliothèque à ajouter, ni accès à Internet.
Python 3 suffit. `numpy` et `matplotlib` ne sont jamais requis (ils sont seulement
mentionnés en extension).

---

## Le sujet, en une page

Un chiffrement par blocs transforme un bloc de `n` bits en un autre bloc de `n` bits à
l'aide d'une clé secrète. Il alterne des couches **non linéaires** (les boîtes S, qui
apportent la *confusion*) et des couches **linéaires** (les permutations, qui apportent la
*diffusion*), répétées sur plusieurs tours.

La cryptanalyse linéaire cherche une relation **linéaire** entre les bits du clair, ceux
du chiffré et ceux de la clé — un simple XOR de bits choisis par des masques — qui soit
vraie *un peu plus souvent que le hasard*. Ce déséquilibre s'appelle le **biais**. Il
suffit à retrouver la clé.

| Notion | Notation | Où dans le TP |
|---|---|---|
| Probabilité qu'une relation soit vraie | `p` | § A |
| Biais absolu | `δ = p − 1/2` | § A |
| Corrélation (déséquilibre) | `ρ = 2p − 1 = 2δ` | § A |
| Table des approximations d'une boîte S | `LAT[a][b] = 16δ = 8ρ` | § B |
| Chaînage de plusieurs approximations | piling-up : `ρ_total = ∏ ρ_i` | § D |
| Écart à la moyenne observé sur `N` couples | `z = ρ√N` | § E |

---

## Le mini-chiffre étudié : SPN-8

Un chiffrement par blocs jouet, assez petit pour tenir dans une séance, assez riche pour
contenir toute la méthode :

```
      m  (8 bits)
      │
      ⊕ K0
      │
   ┌──┴──┐
   │  S  │   deux boîtes S de 4 bits (celles de PRESENT)
   └──┬──┘
      │  P    échange des deux quartets
      ⊕ K1
      │
   │  S  │  P  ⊕ K2
      │
   │  S  │  P  ⊕ K3
      │
      C  (8 bits)
```

- **Bloc** : 8 bits, vus comme deux quartets.
- **Clé** : 8 bits, diversifiée en quatre clés de tour `K0 … K3`.
- **3 tours**, une seule couche linéaire (échange des quartets).
- La clé maître est **inconnue** : c'est l'objet de l'attaque.

Le TP ne prétend pas que ce chiffre soit sûr : il est cassable par force brute (256 clés).
C'est précisément l'intérêt pédagogique — on voit *comment* une attaque statistique
retrouve la clé sans énumérer tout l'espace.

---

## Par où commencer

```bash
python3 verifier.py          # état de ton travail
```

Ton fichier est `tp_cryptanalyse_lineaire.py` : **12 fonctions à écrire, plus 1 bonus**,
et 16 épreuves automatiques.

| Commande | Ce qu'elle fait |
|---|---|
| `python3 verifier.py` | lance les 16 épreuves sur ton fichier |
| `python3 test_tp_cryptanalyse_lineaire.py` | la même chose, directement |
| `python3 tp_cryptanalyse_lineaire.py` | affiche où tu en es, fonction par fonction |
| `TP_CORRIGE=1 python3 verifier.py` | vérifie le corrigé du professeur |

---

## Le plan du fichier

| Partie | Contenu | Fonctions |
|---|---|---|
| `§ A` | cryptographie à clé secrète, XOR, parité, masques, les trois biais | — |
| `§ B` | la boîte S et sa table d'approximations (LAT) | `parite_masque`, `appliquer_sbox`, `sbox_inverse`, `table_approximations` |
| `§ C` | le mini-chiffre SPN-8 | `permuter`, `chiffrer`, `dechiffrer` (bonus) |
| `§ D` | ★ **CRYPTANALYSE LINÉAIRE** ★ la trace et l'attaque | `compter_relation`, `attaquer_quartet`, `groupe_de_tete`, `cle_candidates`, `verifier_cles`, `attaquer_cle` |
| `§ E` | six expériences à faire dans l'interpréteur | — |
| `§ F` | dix questions de rapport | — |
| `§ G` | exercices papier et extensions | — |

La cryptanalyse occupe le `§ D` entier : c'est le cœur de la séance.

---

## Comment travailler

1. Ouvre `tp_cryptanalyse_lineaire.py` dans un éditeur et lis le `§ A` (le cours) puis
   le mode d'emploi en tête de fichier.
2. Écris **une** fonction : chaque exercice suit toujours le même plan —
   **OBJECTIF**, **POURQUOI (COURS)**, **CE QUE TU DOIS FAIRE** (la recette en français),
   **RAPPELS PYTHON**, **À COMPLÉTER** (le squelette à trous), puis **✅ SOLUTION** en
   commentaire, à recopier *après avoir essayé*.
3. Lance les épreuves :

   ```bash
   python3 verifier.py
   ```

   Tu obtiens `Bilan : 7/16 épreuves réussies`, et pour chaque échec une explication.
4. Fais les expériences du `§ E`, puis réponds aux questions du `§ F`.

### Règles du jeu

* **Ne modifie jamais** `test_tp_cryptanalyse_lineaire.py`, ni le dossier `outils/` : ils
  appartiennent au professeur. Tu peux les **lire** : `outils/lineaire.py` est commenté
  pour toi.
* Les 2 000 couples clair-chiffré sont dans `donnees_lineaire.py`. La clé n'y est pas.
* Les épreuves n'écrivent jamais la réponse en clair : elles comparent des empreintes
  SHA-256, pour que le fichier de test ne te donne pas la solution.

---

## Ce qui est fourni, ce qui est à faire

* `outils/lineaire.py` — la boîte S, les constantes, la diversification de clé, les
  mesures statistiques (`z_score`, `intervalle_confiance`) et l'affichage de la LAT.
  Tout le « rangement » est là pour que tu consacres ton temps à la cryptanalyse.
* `donnees_lineaire.py` — les 2 000 couples interceptés.
* `outils/verif.py` — le mini-harnais d'épreuves (bibliothèque standard uniquement).
* `corriges/` — les corrigés, réservés au professeur.

Tout ce qui fait la cryptanalyse — la LAT, le chiffrement, l'attaque — est à toi.

---

## Les limites, annoncées d'avance

Ce TP ne prétend pas qu'une attaque linéaire réussit toujours. Trois faits sont mesurés
et commentés :

1. **Le biais dépend de la clé.** Sur ce bloc de 8 bits, 80 clés sur 256 ont un biais
   exact *nul* dans une orientation. Le jeu de données a été calibré pour que ce ne soit
   pas le cas ici.
2. **Les mauvais candidats ne sont pas neutres.** Plusieurs candidats faux peuvent avoir
   exactement le même score que le bon : il faut un *groupe* puis une vérification.
3. **L'attaque peut échouer.** La fonction `attaquer_cle` renvoie un statut
   (`certaine`, `elargie`, `incertaine`, `echec`) et ne masque jamais un échec par une
   recherche exhaustive.

C'est une partie du sujet, pas un défaut du TP.

---

*Pour l'organisation de la séance, les choix techniques et la façon de régénérer les
données, voir `ENSEIGNANT.md`. Pour tester le corrigé : `TP_CORRIGE=1 python3 verifier.py`.*
