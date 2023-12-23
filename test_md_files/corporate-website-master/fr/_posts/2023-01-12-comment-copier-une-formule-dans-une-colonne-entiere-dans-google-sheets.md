---
author: full
categories:
- data-analysis
date: 2023-01-12
description: You are working inside a Google Spreadsheet where a formula needs to
  copied down to the last row of the sheet. You also need the formula to be added
  automatically when a new row is added to the Google Sheet.
image: https://sergioafanou.github.io/blog/assets/images/12.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: howtocopy_a_formula_downanentirecolumn
tags:
- spreadsheet
- productivity
- dataanalysis
title: Comment copier une formule dans une colonne entière dans Google Sheets
---

Vous travaillez dans une feuille de calcul Google où une formule doit être copiée jusqu'à la dernière ligne de la feuille. Vous avez également besoin que la formule soit ajoutée automatiquement lorsqu'une nouvelle ligne est ajoutée à la feuille Google.
Il existe plusieurs façons de résoudre ce problème.

# Copier la formule dans Google Sheets

L'approche la plus simple pour copier des formules consiste à utiliser la poignée de remplissage dans Google Sheets. Écrivez votre formule dans la première ligne de votre feuille de calcul, puis pointez votre souris vers le coin inférieur droit de la cellule de formule.

Le pointeur se transforme en une poignée de remplissage (symbole plus noir) que vous pouvez faire glisser jusqu'à la dernière ligne de la feuille. La poignée de recopie copiera non seulement les formules dans toutes les cellules adjacentes, mais copiera également la mise en forme visuelle.

Si vous devez copier les formules entre les cellules mais sans aucune mise en forme, sélectionnez la cellule qui contient la mise en forme et appuyez sur ```Ctrl+C``` pour la copier dans le presse-papiers. Ensuite, sélectionnez la plage où cette formule doit être appliquée, cliquez avec le bouton droit de la souris, choisissez Collage spécial et Coller la formule uniquement.

# Appliquer la formule à toute la colonne dans Google Sheets

Si vous avez des centaines de lignes dans une feuille de calcul Google et que vous souhaitez appliquer la même formule à toutes les lignes d'une colonne particulière, il existe une solution plus efficace que le copier-coller - les formules matricielles.


Mettez en surbrillance la première cellule de la colonne et tapez la formule comme précédemment. Cependant, au lieu de spécifier une seule cellule comme paramètre, nous spécifierons la colonne entière en utilisant la notation ```B2: B``` (commencez à partir de la cellule B2 et descendez jusqu'à la dernière ligne de la colonne B).
Appuyez ensuite sur ```Ctrl + Maj + Entrée``` ou ```Cmd + Maj + Entrée``` sur Mac, et Google Sheets entourera automatiquement votre formule avec la fonction ```ARRAYFORMULA```.

Ainsi, nous pourrions appliquer la formule à toute la colonne de la feuille de calcul avec une seule cellule. Les formules matricielles sont plus efficaces car elles traitent un lot de lignes en une seule fois. Ils sont également plus faciles à gérer car il vous suffit de modifier une seule cellule pour modifier la formule.


Un problème que vous avez peut-être remarqué avec les formules ci-dessus est qu'il s'applique à chaque ligne de la colonne où vous souhaitez uniquement ajouter des formules aux lignes contenant des données et ignorer les lignes vides.


Cela peut être fait en ajoutant un IF contient à notre ```ARRAYFORMULA``` afin qu'il n'applique la formule à aucune des lignes vides.


Google Spreadsheet propose deux fonctions pour aider à tester si une cellule est vide ou maintenant.
```ISBLANK(A1)``` - Renvoie TRUE si la cellule référencée est vide.
```LEN(A1) <> 0``` - Renvoie VRAI si la cellule référencée n'est pas vide, FAUX sinon
Nos formules matricielles modifiées se liraient donc :

## Utilisation de ISBLANK (référence de cellule) :

Il existe plusieurs autres façons de tester si une cellule est vide ou non dans google sheets :

```
=TableauFormule(SI(ESTVIDE(B2:B), "", ARRONDI(B2:B*18%, 2)))
=TableauFormule(SI(NBCAR(B2:B)<>0, ARRONDI(B2:B*18%, 2), ""))
=TableauFormule(SI(B2:B="", "", ARRONDI(B2:B\*18%, 2)))
```

### Utiliser des formules matricielles dans les en-têtes de colonne

Dans nos exemples précédents, le texte des titres de colonne (comme Taxe, Montant total) était pré-rempli et les formules n'étaient ajoutées qu'à la première ligne de l'ensemble de données.
Nous pouvons encore améliorer notre formule afin qu'elles puissent être appliquées à l'en-tête de colonne lui-même. Si l'index de la ligne actuelle est 1, calculé à l'aide de la fonction ROW(), la formule affiche le titre de la colonne, sinon elle effectue le calcul à l'aide de la formule.

```
=TableauFormule(SI(LIGNE(B:B)=1,"Taxe",SI(ESTVIDE(B:B),"",ROND(B:B\*18%, 2))))
```

### Formules de remplissage automatique dans les soumissions de formulaires Google

Les fonctions ```ARRAYFORMULA``` sont particulièrement utiles pour Google Forms lorsque les réponses du formulaire sont enregistrées dans une feuille Google. Vous ne pouvez pas effectuer de calculs en direct dans Google Forms, mais ils peuvent être effectués dans la feuille de calcul qui collecte les réponses.
Vous pouvez créer de nouvelles colonnes dans la feuille de calcul Google et appliquer ```ARRAYFORMULA``` à la première ligne des colonnes ajoutées.
Lorsqu'une nouvelle soumission de formulaire est reçue, une nouvelle ligne est ajoutée à la feuille Google et les formules sont clonées et automatiquement appliquées aux nouvelles lignes sans que vous ayez à copier-coller des éléments.

### Comment utiliser VLOOKUP dans ARRAYFORMULA

Vous pouvez combiner ```ARRAYFORMULA``` avec ```VLOOKUP``` pour effectuer rapidement une recherche sur une colonne entière.
Supposons que vous ayez une feuille « Fruits » qui répertorie les noms de fruits dans la colonne A et les prix correspondants dans la colonne B. La deuxième feuille « Commandes » contient les noms de fruits dans la colonne A, la quantité dans la colonne B et vous êtes censé calculer la commande. montant de la colonne C.

```
=TableauFormule(
SI(LIGNE(A:A)=1,
"Total",
SI(PAS(ESTVIDE(A:A)), RECHERCHEV(A:A, Fruits!A2:B6, 2, FAUX) \* B:B, "")))
```

En anglais simple, si la ligne de la cellule actuelle est 1, affichez le titre de la colonne en texte brut. Si la ligne est supérieure à 1 et que la colonne A de la ligne courante n'est pas vide, effectuez une ```RECHERCHEV``` pour récupérer le prix de l'article de la feuille Fruits. Multipliez ensuite ce prix par la quantité dans la cellule B et affichez la valeur dans la cellule C.
Si votre plage RECHERCHEV se trouve dans une autre feuille de calcul Google, utilisez la fonction ```IMPORTRANGE()``` avec l'```ID ```de l'autre feuille Google.
Veuillez noter que vous devrez peut-être utiliser des points-virgules dans les formules de la feuille de calcul au lieu de virgules pour certains paramètres régionaux.
