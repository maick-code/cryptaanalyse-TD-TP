# TP / PROJET : Développement d'un logiciel de cryptanalyse linéaire du DES avec Python et Tkinter

## 1. Contexte

La cryptanalyse est une discipline de la cryptologie qui consiste à étudier un système de
chiffrement afin d'évaluer sa résistance et, dans certaines conditions, de retrouver des
informations sur la clé secrète ou le message original.

La cryptanalyse linéaire, introduite par Mitsuru Matsui, exploite des relations statistiques
entre certains bits du texte clair, du texte chiffré et de la clé secrète. Ces relations ne
sont généralement pas toujours vraies : elles présentent un biais statistique qui peut être
exploité lorsqu'on dispose d'un nombre suffisant de couples clair-chiffré.

Dans ce projet, vous allez développer une application de bureau en Python, avec une interface
graphique Tkinter, permettant de réaliser une expérience de cryptanalyse linéaire sur une
version pédagogique du DES.

Le projet prendra la forme d'un défi entre groupes : chaque groupe jouera successivement le
rôle d'un concepteur de chiffrement et celui d'un cryptanalyste.

## 2. Objectif général

Concevoir une application permettant de :

- chiffrer un message avec une version pédagogique du DES ;
- produire et partager des couples texte clair–texte chiffré ;
- analyser statistiquement les données reçues d'un autre groupe ;
- tester des hypothèses sur certains bits de la clé ;
- présenter les résultats de l'attaque dans une interface graphique ;
- expliquer les limites et la fiabilité des résultats obtenus.

## 3. Travail à réaliser

### Partie A — Implémentation du chiffrement

Chaque groupe devra implémenter ou intégrer une version pédagogique du DES comprenant :

- le réseau de Feistel ;
- les fonctions d'expansion, de permutation et de substitution nécessaires ;
- les S-boxes ;
- la génération des sous-clés ;
- les opérations de chiffrement et de déchiffrement.

Pour que l'attaque reste réalisable, vous utiliserez un **DES réduit à un nombre limité de
rondes**, par exemple 4 à 6 rondes, avec une configuration identique pour tous les groupes.

Vous devrez préciser clairement les différences entre cette version pédagogique et le DES
standard à 16 rondes.

### Partie B — Génération des données

L'application devra permettre à un groupe de :

1. saisir un message ;
2. choisir ou générer une clé secrète ;
3. chiffrer le message ;
4. générer plusieurs couples texte clair–texte chiffré ;
5. exporter les données dans un fichier CSV ou TXT ;
6. transmettre ce fichier à un autre groupe sans révéler la clé secrète.

Le fichier transmis devra contenir les données nécessaires à l'analyse, mais jamais la clé
secrète.

### Partie C — Cryptanalyse linéaire

Le groupe receveur devra importer le fichier transmis et effectuer une attaque statistique.

L'application devra permettre de :

- sélectionner une approximation linéaire étudiée en cours ;
- calculer la fréquence de vérification de cette relation ;
- calculer le biais observé par rapport à une probabilité de 1/2 ;
- tester plusieurs hypothèses sur les bits ciblés de la sous-clé ;
- classer les hypothèses selon leur score statistique ;
- afficher les candidats les plus plausibles ;
- comparer les résultats obtenus avec les données expérimentales.

Vous devrez distinguer le **biais théorique**, le **biais estimé** à partir d'une
approximation et le **biais observé** sur les données de l'expérience.

Attention : le candidat qui obtient le meilleur score n'est pas nécessairement la bonne clé.
L'application devra signaler les égalités, les résultats ambigus et les cas où les données
sont insuffisantes.

### Partie D — Interface graphique Tkinter

L'application devra comporter au minimum les écrans ou onglets suivants :

**1. Chiffrement**

- saisie du message ;
- saisie ou génération de la clé ;
- affichage du cryptogramme ;
- génération et exportation des couples clair-chiffré.

**2. Importation des données**

- sélection du fichier reçu ;
- affichage du nombre de couples disponibles ;
- vérification du format des données.

**3. Cryptanalyse**

- choix de l'approximation linéaire ;
- lancement de l'analyse ;
- affichage du biais et des scores ;
- classement des hypothèses sur les bits de la sous-clé.

**4. Résultats**

- tableau des meilleurs candidats ;
- graphique comparant les scores ;
- interprétation des résultats ;
- indication du niveau d'incertitude.

**5. Aide**

- explication du principe de la cryptanalyse linéaire ;
- définition des termes : approximation, biais, sous-clé, S-box et réseau de Feistel.

L'interface devra être simple, compréhensible et utilisable sans modifier le code source.

## 4. Organisation du défi entre groupes

Chaque groupe devra participer à deux expériences.

### Expérience 1 — Groupe émetteur

Le groupe A :

1. choisit une clé secrète ;
2. génère un ensemble de couples clair-chiffré ;
3. exporte les données ;
4. transmet le fichier au groupe B, sans communiquer la clé.

### Expérience 2 — Groupe cryptanalyste

Le groupe B :

1. importe les données reçues ;
2. sélectionne une approximation adaptée à la version réduite du DES ;
3. effectue la cryptanalyse ;
4. présente les hypothèses les mieux classées ;
5. explique si les résultats permettent réellement d'identifier certains bits de la
   sous-clé.

Les groupes inverseront ensuite les rôles : le groupe B produira ses données et le groupe A
réalisera l'analyse.

**Règle importante :** tous les groupes doivent employer la même version du DES réduit et
les mêmes paramètres expérimentaux. Les clés doivent rester secrètes jusqu'à la fin de
l'évaluation.

## 5. Contraintes techniques

- Langage : Python 3.
- Interface graphique : Tkinter.
- Bibliothèques scientifiques et graphiques : facultatives, à justifier.
- Données : CSV ou TXT, avec un format documenté.
- Code : organisé en modules et fonctions réutilisables.
- Gestion des erreurs : fichiers invalides, données insuffisantes et saisies incorrectes.
- Sécurité : ne jamais exporter la clé secrète avec les couples clair-chiffré.
- Reproductibilité : permettre de fixer une graine aléatoire pour reproduire les expériences
  lorsque cela est pertinent.

Le code devra séparer la logique cryptographique, les calculs statistiques, la gestion des
fichiers et l'interface graphique.

## 6. Livrables

Chaque groupe devra remettre :

1. le code source complet ;
2. l'application Tkinter fonctionnelle ;
3. un fichier d'exemple contenant des couples clair-chiffré ;
4. un rapport expliquant l'algorithme et l'approximation utilisée ;
5. les résultats de l'attaque, avec des captures d'écran ;
6. une analyse des limites et des incertitudes ;
7. une démonstration orale de l'expérience menée contre un autre groupe.

## 7. Questions pour le rapport

1. Qu'est-ce qu'une approximation linéaire en cryptanalyse ?
2. Comment définit-on le biais d'une relation ?
3. Pourquoi faut-il de nombreux couples clair-chiffré ?
4. Pourquoi le meilleur candidat statistique peut-il être incorrect ?
5. Quel est le rôle des S-boxes dans la résistance du DES à la cryptanalyse linéaire ?
6. Quelles sont les différences entre le DES réduit utilisé dans ce projet et le DES
   standard ?
7. Pourquoi les résultats obtenus sur quelques rondes ne permettent-ils pas de conclure
   directement sur la sécurité du DES complet ?
8. Comment améliorer la fiabilité de l'expérience ?

## 8. Critères d'évaluation

- Fonctionnement du chiffrement et du déchiffrement : 20 %.
- Qualité de l'interface Tkinter : 15 %.
- Exactitude des calculs statistiques : 25 %.
- Fonctionnement et interprétation de l'attaque : 20 %.
- Qualité du code, des tests et de la documentation : 10 %.
- Démonstration et analyse critique : 10 %.

## 9. Résultat attendu

À la fin du projet, chaque groupe devra être capable de démontrer son logiciel, d'échanger
des données chiffrées avec un autre groupe, de mener une expérience de cryptanalyse linéaire
et d'expliquer scientifiquement ce que les résultats permettent — ou ne permettent pas — de
conclure sur la clé secrète.

Le but n'est pas simplement de retrouver une clé : il est de comprendre comment une faiblesse
statistique peut être exploitée, comment évaluer la qualité d'une attaque et pourquoi un
résultat expérimental doit toujours être interprété avec prudence.
