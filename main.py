"""Point d'entrée en ligne de commande du tableau de bord commercial.

Exemple d'utilisation :
    python main.py --entree donnees_exemple.csv --sortie rapport.html
"""

import argparse

from pilotage import charger_ventes, generer_rapport


def main():
    """Lit les ventes, génère le rapport HTML et affiche les KPI."""
    parser = argparse.ArgumentParser(description="Tableau de bord commercial")
    parser.add_argument("--entree", default="donnees_exemple.csv")
    parser.add_argument("--sortie", default="rapport.html")
    args = parser.parse_args()

    ventes = charger_ventes(args.entree)
    kpi = generer_rapport(ventes, args.sortie)
    print(f"Chiffre d'affaires : {kpi['chiffre_affaires']:,.2f} €")
    print(f"Marge : {kpi['marge']:,.2f} € ({kpi['taux_marge']} %)")
    print(f"Panier moyen : {kpi['panier_moyen']:,.2f} €")
    print(f"Commandes : {kpi['nombre_commandes']}")
    print(f"Rapport généré : {args.sortie}")


if __name__ == "__main__":
    main()
