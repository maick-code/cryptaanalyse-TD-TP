# Corrigé des exercices papier — cryptanalyse linéaire

**Réservé au professeur.** Ce fichier corrige les exercices du § G du fichier
étudiant, et donne les valeurs numériques exactes du jeu de données
(`M = 19`, 2 000 couples, graine 20261022).

Rappels de conventions, utilisés partout ci-dessous :

```
p     = probabilité que la relation soit vraie
delta = p - 1/2          (biais absolu)
rho   = 2p - 1 = 2 delta (corrélation)
LAT[a][b] = 16 delta = 8 rho        (boîte S de 4 bits)
piling-up : rho_total = produit des rho_i ;  p = 1/2 + rho_total/2
```

---

## Exercice 1 — calculer `LAT[9][2]` à la main

Masque d'entrée `a = 9 = 1001` (bits 3 et 0), masque de sortie `b = 2 = 0010`
(bit 1). On calcule `parité(x, 9)` et `parité(S[x], 2)` pour les 16 quartets :

| x | binaire | parité(x,9) | S[x] | S[x] binaire | parité(S[x],2) | égal ? |
|---:|---|---:|---:|---|---:|---|
| 0 | 0000 | 0 | 12 | 1100 | 0 | oui |
| 1 | 0001 | 1 | 5 | 0101 | 0 | non |
| 2 | 0010 | 0 | 6 | 0110 | 1 | non |
| 3 | 0011 | 1 | 11 | 1011 | 1 | oui |
| 4 | 0100 | 0 | 9 | 1001 | 0 | oui |
| 5 | 0101 | 1 | 0 | 0000 | 0 | non |
| 6 | 0110 | 0 | 10 | 1010 | 1 | non |
| 7 | 0111 | 1 | 13 | 1101 | 0 | non |
| 8 | 1000 | 1 | 3 | 0011 | 1 | oui |
| 9 | 1001 | 0 | 14 | 1110 | 1 | non |
| 10 | 1010 | 1 | 15 | 1111 | 1 | oui |
| 11 | 1011 | 0 | 8 | 1000 | 0 | oui |
| 12 | 1100 | 1 | 4 | 0100 | 0 | non |
| 13 | 1101 | 0 | 7 | 0111 | 1 | non |
| 14 | 1110 | 1 | 1 | 0001 | 0 | non |
| 15 | 1111 | 0 | 2 | 0010 | 1 | non |

**6 égalités sur 16**, donc

```
LAT[9][2] = 6 - 8 = -2
p = 6/16 = 0,375      delta = -1/8 = -0,125      rho = -1/4
```

Le signe est négatif : la relation est vraie *moins* souvent que le hasard.
Cela ne gêne pas l'attaque, car le score utilise une valeur absolue et le
signe exact dépend de la constante de clé (voir exercice 2).

---

## Exercice 2 — `p`, `delta`, `rho`, et le piège du signe

**a)** `p = 0,5625`

```
delta = 0,5625 - 0,5 = 0,0625 = 1/16
rho   = 2 × 0,0625   = 0,125  = 1/8
```

**b)** `rho = -0,25`

```
delta = rho/2 = -0,125 = -1/8
p     = 1/2 + rho/2 = 0,375
```

**c)** `p = 0,75` ou `p = 0,25` : **les deux sont aussi bons**.

```
p = 0,75 -> rho = +0,5      p = 0,25 -> rho = -0,5
|rho| = 0,5 dans les deux cas
```

Ce qui compte est `|rho| = |2p - 1|`, pas l'écart à 1/2 « dans un sens
privilégié ». Un candidat à `p = 0,25` apporte autant d'information qu'un
candidat à `p = 0,75`. C'est exactement pourquoi le score `|2c - N|` du TP
met ces candidats à égalité, et pourquoi il faut un **groupe** puis une
vérification.

---

## Exercice 3 — piling-up et nombre de tours

Avec `m` approximations indépendantes de corrélation `rho_i = 1/4` :

```
rho_total = (1/4)^m        p = 1/2 + rho_total/2
```

| m | rho_total | delta_total | p |
|---:|---|---|---|
| 2 | 1/16 = 0,0625 | 1/32 = 0,03125 | 0,53125 |
| 3 | 1/64 = 0,015625 | 1/128 = 0,0078125 | 0,5078125 |
| 4 | 1/256 = 0,00390625 | 1/512 = 0,001953125 | 0,501953125 |

**Conclusion :** chaque tour supplémentaire multiplie la corrélation par
`1/4`, donc divise le biais par 4. Il faut alors environ `4² = 16` fois plus
de couples pour garder le même z-score (`z = rho × sqrt(N)`). C'est la raison
profonde pour laquelle un chiffre réel utilise beaucoup de tours : au bout de
8 tours, `rho = 1/4^8 ≈ 1,5 × 10^-5`, et il faudrait de l'ordre de `10^10`
couples.

Vérification de l'équivalence des deux écritures (demandée en question 3) :

```
rho_total = (1/4)^m
delta_total = rho_total/2 = (1/4)^m / 2 = 2^(m-1) × (1/8)^m   car 1/8 = delta_i
p = 1/2 + 2^(m-1) × produit des delta_i
```

Les deux formules donnent bien le même `p`.

---

## Exercice 4 — écrire `dechiffrer`

```python
def dechiffrer(bloc, cles):
    x = bloc & 0xFF
    for tour in range(len(cles) - 1, 0, -1):
        x = permuter(x ^ cles[tour])
        x = (sbox_inverse((x >> 4) & 0xF) << 4) | sbox_inverse(x & 0xF)
    return (x ^ cles[0]) & 0xFF
```

Vérification :

```python
cles = diversifier(19)
all(dechiffrer(chiffrer(m, cles), cles) == m for m in range(256))   # True
```

**Point de vigilance :** l'ordre est XOR, puis P, puis S⁻¹. Au chiffrement on
a fait S, puis P, puis XOR : il faut donc défaire dans l'ordre inverse.

---

## Exercice 5 — remonter les tours : un échec instructif

**La méthode.** `K3` connu, on calcule pour chaque couple l'état `x2` :

```
C = P(S(x2)) ^ K3   =>   S(x2) = P(C ^ K3)   =>   x2 = S⁻¹(P(C ^ K3))
```

On obtient 2 000 couples `(m, x2)` d'un chiffre réduit à deux tours, de clés
`(K0, K1, K2)`. On applique alors la même attaque, avec la trace à **une**
approximation `9 -> 2`, pour retrouver un quartet de `K2`.

**Le résultat est un échec**, et c'est le but de l'exercice. Mesures sur le
jeu de données (2 000 couples, `M = 19`, `K2 = 0xB1`) :

| Trace | Vrai quartet | Groupe de tête (seuil 0,8) | Vrai dans le groupe ? |
|---|---|---|---|
| départ bas → `K2_bas` | `0x1` | `[3, 8, 14, 15]` | **non** |
| départ haut → `K2_haut` | `0xB` | `[8, 10, 12]` | **non** |

En élargissant à 0,6 puis 0,4, le vrai quartet reste absent : la
vérification ne peut jamais aboutir.

**Pourquoi ?** Avec une seule approximation de 4 bits, le biais exact du bon
candidat vaut `|LAT[a][b]|/16 ≤ 1/4`. Mais un **mauvais** candidat ne
correspond pas à la même approximation : en notant `Δ = K2_bas ⊕ k`, il
calcule

```
u = S⁻¹( S(x1) ⊕ Δ )
```

et le biais de `parité(x1, b)` contre `parité(u, b)` peut atteindre `1/2`,
donc **dépasser** celui du bon candidat. Sur deux tours chaînés, ce
phénomène existe aussi, mais le biais exact du bon candidat est plus fort
(0,25 et 0,375 pour notre clé), ce qui le maintient dans le groupe.

**Conclusion à faire écrire aux étudiants :** une attaque linéaire ne réussit
pas toujours. Remonter les tours exige des traces plus longues (donc un
chiffre plus faible ou plus de tours couverts), et surtout un biais du bon
candidat nettement supérieur à celui des concurrents. C'est une limite
structurelle, pas un bug.

---

## Exercice 6 — changer de trace

Il n'y a pas de réponse unique. La démarche attendue :

1. choisir un couple `(a, b)` de la LAT, avec `|LAT[a][b]|` grand ;
2. vérifier que le masque arrive sur le bon quartet après `P` (propagation
   `(haut, bas)` comme au § D) ;
3. calculer le piling-up : `rho = (LAT[a][b]/8) × (LAT[b][c]/8)` ;
4. mesurer le biais exact sur les 256 blocs, puis le biais mesuré sur
   2 000 couples ;
5. relancer l'attaque et compter les succès sur plusieurs tirages.

**Ce que l'on observe :** la plupart des traces ont un biais exact **nul**
pour `M = 19` (voir exercice 8) ; seules quelques-unes fonctionnent. C'est
pourquoi le jeu de données a été calibré, et pourquoi le choix de la trace
est un vrai travail de cryptanalyste.

---

## Exercice 7 — diversification de clé sur 32 bits

Le TD d'origine (Bombar, TD 6) tire chaque clé de tour en sélectionnant
certains bits de la clé maître `K` de 32 bits. Principe de la correction :

1. construire les trois listes de sélection `K0`, `K1`, `K2` (32 indices
   chacune, données par la table du TD) ;
2. `K3` ne dépend que de 8 bits de `K` : l'attaquer linéairement donne donc
   8 bits de la clé maître ;
3. il reste `2^24` possibilités pour les 24 autres bits. On les énumère et
   l'on teste sur 2 couples clair-chiffré : chaque test coûte deux
   chiffrements, soit environ `2 × 2^24 ≈ 3,4 × 10^7` chiffrements ;
4. on peut réduire encore en recommençant l'attaque sur `K2`, puis `K1`,
   ce qui donne 24 bits au total et laisse `2^8` candidats.

**Ce qu'il faut retenir :** la cryptanalyse linéaire ne retrouve pas « la
clé » d'un coup ; elle **réduit l'espace de recherche**, et le reste se fait
par énumération et vérification. C'est exactement ce que fait `attaquer_cle`
en passant de 256 clés à 4, puis à 1.

---

## Exercice 8 — score, parité de `N`, et biais nul

**a) Si `N` est impair**, `2c - N` est impair : le score ne peut pas valoir 0.
Le minimum est 1, atteint pour `c = (N-1)/2` ou `c = (N+1)/2`.

```
N = 5 : scores possibles = 1, 3, 5
N = 6 : scores possibles = 0, 2, 4, 6
```

Cela ne change rien à l'attaque : « pas de biais » signifie « score minimal »,
pas « score nul ». Le classement reste valable.

**b) Si le biais exact est nul pour la clé utilisée**, tous les candidats se
valent en espérance : le classement ne fait que refléter le bruit de
l'échantillon. Le groupe de tête est alors arbitraire, et la vérification
échoue le plus souvent : l'attaque doit renvoyer `"echec"` ou
`"incertaine"`, jamais une clé inventée.

**c) Ordre de grandeur.** Sur les 256 clés maîtres possibles :

| Statistique | Valeur mesurée |
|---|---|
| clés avec `|delta| = 0` dans une orientation | 80 / 256 |
| clés avec `|delta| >= 0,25` dans les deux orientations | 16 / 256 |
| clés admissibles pour le TP (avec bon quartet dans le groupe) | 13 / 256 |
| valeurs possibles de `|delta|` exact | 0 ; 0,125 ; 0,25 ; 0,375 |

C'est pourquoi `M = 19` a été **choisi** : sans calibrage, une clé sur deux
environ ne permettrait pas l'attaque. Le TP le dit explicitement, et c'est
une différence essentielle avec un vrai chiffrement, où l'on ne choisit pas
la clé de l'adversaire.

---

## Barème suggéré

| Partie | Points |
|---|---|
| Épreuves automatiques B et C (8 épreuves) | 5 |
| Épreuves automatiques D (8 épreuves) | 7 |
| Exercices papier 1 à 3 | 3 |
| Exercice 5 (diagnostic argumenté) | 3 |
| Questions de rapport (10 questions) | 2 |

Total sur 20. L'exercice 5 est le plus discriminant : il récompense la
compréhension des limites, pas la recopie d'une attaque qui marche.
