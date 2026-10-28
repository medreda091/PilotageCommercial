# PilotageCommercial

Tableau de bord commercial en Python, sans aucune dépendance externe : à partir
d'un simple fichier CSV de ventes, il nettoie les données, calcule les
indicateurs clés, génère des graphiques et rédige une interprétation en français.

L'idée est simple : un décideur doit comprendre la situation en 30 secondes,
sans ouvrir un tableur ni lancer un outil compliqué.

## Résultat sur les données d'exemple

| Indicateur | Valeur |
|---|---|
| Chiffre d'affaires | 4 335,72 € |
| Marge | 1 921,72 € (44,3 %) |
| Panier moyen | 228,20 € |
| Commandes | 19 |

Ce que disent les chiffres, généré automatiquement par le programme :

- Le meilleur mois est 2026-03 (1 803,90 € de chiffre d'affaires).
- La région Île-de-France concentre 59,6 % du chiffre d'affaires : c'est le
  premier levier de croissance, mais aussi la première dépendance à surveiller.
- Le produit le plus vendu est « Écran 27 pouces » (1 743,00 €, soit 40,2 %
  du total).
- La marge est saine (44,3 %) : le prix de vente couvre largement les coûts.
- Le panier moyen est de 228,20 € pour 19 commandes.

## Ce que fait le projet

- **Nettoyage** : les lignes invalides (quantité négative, prix négatif, ligne
  incomplète) sont rejetées et comptées, jamais mélangées aux résultats.
- **KPI** : chiffre d'affaires, coûts, marge et taux de marge, panier moyen,
  nombre de commandes.
- **Analyses** : chiffre d'affaires par mois, par région, et classement des
  produits les plus vendus.
- **Visualisation** : graphiques en barres SVG générés sans bibliothèque
  externe, intégrés dans un rapport HTML autonome.
- **Interprétation** : chaque phrase du rapport s'appuie sur un chiffre calculé,
  jamais sur une impression.

## Utilisation

Python 3.11 ou plus, aucune installation nécessaire :

```bash
python main.py --entree donnees_exemple.csv --sortie rapport.html
```

Puis ouvrir `rapport.html` dans un navigateur. Pour utiliser vos propres
données, il suffit d'un CSV avec les colonnes suivantes :

```
date,commande,region,produit,categorie,quantite,prix_unitaire,cout_unitaire
```

## Structure du projet

```
main.py                 Point d'entrée en ligne de commande
pilotage.py             Nettoyage, KPI, graphiques SVG, rapport HTML
donnees_exemple.csv     Jeu de données d'exemple (20 ventes)
tests/test_pilotage.py  Tests unitaires
Dockerfile              Image Docker pour lancer le projet partout
```

## Tests

```bash
python -m unittest discover -s tests -v
```

12 tests, tous verts : nettoyage, calcul des KPI, regroupements par mois /
région / produit, interprétation et génération du rapport HTML.

## Stack

Python (bibliothèque standard uniquement), HTML / SVG, Docker.
