"""Pilotage commercial : nettoyage, KPI, graphiques et rapport HTML.

Ce module ne dépend d'aucune bibliothèque externe : il n'utilise que la
bibliothèque standard de Python, pour que le projet tourne partout sans
installation compliquée.
"""

import csv
from collections import Counter, defaultdict


def charger_ventes(chemin):
    """Lit un fichier CSV de ventes et renvoie une liste de dictionnaires."""
    ventes = []
    with open(chemin, newline="", encoding="utf-8") as fichier:
        for ligne in csv.DictReader(fichier):
            try:
                ventes.append(
                    {
                        "date": ligne["date"],
                        "commande": ligne["commande"],
                        "region": ligne["region"],
                        "produit": ligne["produit"],
                        "categorie": ligne["categorie"],
                        "quantite": int(ligne["quantite"]),
                        "prix_unitaire": float(ligne["prix_unitaire"]),
                        "cout_unitaire": float(ligne["cout_unitaire"]),
                    }
                )
            except (KeyError, ValueError):
                # Ligne incomplète ou mal typée : elle sera comptée comme rejetée.
                ventes.append({"rejetee": True, "ligne": ligne})
    return ventes


def nettoyer(ventes):
    """Sépare les ventes valides des lignes rejetées.

    Une vente est rejetée si sa quantité est nulle ou négative, si un prix
    ou un coût est négatif, ou si sa ligne n'a pas pu être lue.
    """
    propres, rejetees = [], []
    for vente in ventes:
        if vente.get("rejetee"):
            rejetees.append(vente)
            continue
        if vente["quantite"] <= 0:
            rejetees.append(vente)
            continue
        if vente["prix_unitaire"] < 0 or vente["cout_unitaire"] < 0:
            rejetees.append(vente)
            continue
        propres.append(vente)
    return propres, rejetees


def calculer_kpi(ventes):
    """Calcule les indicateurs principaux à partir des ventes nettoyées."""
    chiffre_affaires = sum(v["quantite"] * v["prix_unitaire"] for v in ventes)
    cout_total = sum(v["quantite"] * v["cout_unitaire"] for v in ventes)
    marge = chiffre_affaires - cout_total
    taux_marge = (marge / chiffre_affaires * 100) if chiffre_affaires else 0.0
    commandes = {v["commande"] for v in ventes}
    panier_moyen = (chiffre_affaires / len(commandes)) if commandes else 0.0
    return {
        "chiffre_affaires": round(chiffre_affaires, 2),
        "cout_total": round(cout_total, 2),
        "marge": round(marge, 2),
        "taux_marge": round(taux_marge, 1),
        "nombre_ventes": len(ventes),
        "nombre_commandes": len(commandes),
        "panier_moyen": round(panier_moyen, 2),
    }


def ventes_par_mois(ventes):
    """Regroupe le chiffre d'affaires par mois (format AAAA-MM)."""
    totaux = defaultdict(float)
    for vente in ventes:
        totaux[vente["date"][:7]] += vente["quantite"] * vente["prix_unitaire"]
    return dict(sorted(totaux.items()))


def ventes_par_region(ventes):
    """Regroupe le chiffre d'affaires par région, trié par ordre décroissant."""
    totaux = defaultdict(float)
    for vente in ventes:
        totaux[vente["region"]] += vente["quantite"] * vente["prix_unitaire"]
    return dict(sorted(totaux.items(), key=lambda item: -item[1]))


def top_produits(ventes, limite=5):
    """Renvoie les produits les plus vendus en chiffre d'affaires."""
    totaux = defaultdict(float)
    for vente in ventes:
        totaux[vente["produit"]] += vente["quantite"] * vente["prix_unitaire"]
    classement = sorted(totaux.items(), key=lambda item: -item[1])
    return classement[:limite]


def interpreter(kpi, par_mois, par_region, classement):
    """Rédige une interprétation en français à partir des indicateurs.

    L'objectif est de transformer des chiffres en lecture métier : ce qui
    progresse, ce qui concentre le chiffre d'affaires, et ce qu'il faut
    surveiller. Aucune phrase n'est inventée : chaque constat s'appuie sur
    un chiffre calculé juste avant.
    """
    phrases = []
    if par_mois:
        meilleur_mois = max(par_mois, key=par_mois.get)
        phrases.append(
            f"Le meilleur mois est {meilleur_mois} "
            f"({par_mois[meilleur_mois]:,.2f} € de chiffre d'affaires)."
        )
    if par_region:
        premiere_region = next(iter(par_region))
        part = par_region[premiere_region] / kpi["chiffre_affaires"] * 100
        phrases.append(
            f"La région {premiere_region} concentre {part:.1f} % du chiffre "
            "d'affaires : c'est le premier levier de croissance, mais aussi "
            "la première dépendance à surveiller."
        )
    if classement:
        premier_produit, montant = classement[0]
        part = montant / kpi["chiffre_affaires"] * 100
        phrases.append(
            f"Le produit le plus vendu est « {premier_produit} » "
            f"({montant:,.2f} €, soit {part:.1f} % du total)."
        )
    if kpi["taux_marge"] >= 30:
        phrases.append(
            f"La marge est saine ({kpi['taux_marge']} %) : le prix de vente "
            "couvre largement les coûts."
        )
    elif kpi["taux_marge"] >= 0:
        phrases.append(
            f"La marge est serrée ({kpi['taux_marge']} %) : il faut surveiller "
            "les coûts avant d'accorder des remises."
        )
    else:
        phrases.append("La marge est négative : les ventes se font à perte.")
    phrases.append(
        f"Le panier moyen est de {kpi['panier_moyen']:,.2f} € pour "
        f"{kpi['nombre_commandes']} commandes."
    )
    return phrases


def graphique_barres_svg(etiquettes, valeurs, largeur=640, hauteur=280):
    """Génère un graphique en barres SVG simple, sans dépendance externe."""
    if not valeurs:
        return "<p>Aucune donnée à afficher.</p>"
    maximum = max(valeurs)
    marge_gauche, marge_bas = 120, 30
    zone_largeur = largeur - marge_gauche - 20
    zone_hauteur = hauteur - marge_bas - 20
    barre_hauteur = zone_hauteur / len(valeurs)
    morceaux = [f'<svg width="{largeur}" height="{hauteur}" xmlns="http://www.w3.org/2000/svg">']
    for i, (etiquette, valeur) in enumerate(zip(etiquettes, valeurs)):
        longueur = (valeur / maximum * zone_largeur) if maximum else 0
        y = 10 + i * barre_hauteur
        morceaux.append(
            f'<text x="10" y="{y + barre_hauteur / 2 + 4}" font-size="12">{etiquette}</text>'
        )
        morceaux.append(
            f'<rect x="{marge_gauche}" y="{y + 3}" width="{longueur:.1f}" '
            f'height="{barre_hauteur - 6}" fill="#0f766e" />'
        )
        morceaux.append(
            f'<text x="{marge_gauche + longueur + 6}" y="{y + barre_hauteur / 2 + 4}" '
            f'font-size="12">{valeur:,.2f} €</text>'
        )
    morceaux.append("</svg>")
    return "\n".join(morceaux)


def generer_rapport(ventes, chemin_sortie):
    """Calcule les KPI et écrit le tableau de bord HTML complet."""
    propres, rejetees = nettoyer(ventes)
    kpi = calculer_kpi(propres)
    par_mois = ventes_par_mois(propres)
    par_region = ventes_par_region(propres)
    classement = top_produits(propres)
    phrases = interpreter(kpi, par_mois, par_region, classement)

    graphique_mois = graphique_barres_svg(list(par_mois.keys()), list(par_mois.values()))
    graphique_regions = graphique_barres_svg(
        list(par_region.keys()), list(par_region.values())
    )
    lignes_top = "\n".join(
        f"<tr><td>{produit}</td><td>{montant:,.2f} €</td></tr>"
        for produit, montant in classement
    )
    interpretations = "\n".join(f"<li>{phrase}</li>" for phrase in phrases)

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>Tableau de bord commercial</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; color: #1f2937; }}
h1 {{ color: #0f766e; }}
.kpi {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.carte {{ border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; min-width: 160px; }}
.carte strong {{ display: block; font-size: 1.4em; color: #0f766e; }}
table {{ border-collapse: collapse; margin-top: 16px; }}
td, th {{ border: 1px solid #d1d5db; padding: 8px 12px; text-align: left; }}
</style></head>
<body>
<h1>Tableau de bord commercial</h1>
<div class="kpi">
<div class="carte">Chiffre d'affaires<strong>{kpi['chiffre_affaires']:,.2f} €</strong></div>
<div class="carte">Marge<strong>{kpi['marge']:,.2f} € ({kpi['taux_marge']} %)</strong></div>
<div class="carte">Panier moyen<strong>{kpi['panier_moyen']:,.2f} €</strong></div>
<div class="carte">Commandes<strong>{kpi['nombre_commandes']}</strong></div>
</div>
<p>{len(rejetees)} ligne(s) rejetée(s) au nettoyage.</p>
<h2>Chiffre d'affaires par mois</h2>
{graphique_mois}
<h2>Chiffre d'affaires par région</h2>
{graphique_regions}
<h2>Produits les plus vendus</h2>
<table><tr><th>Produit</th><th>Chiffre d'affaires</th></tr>{lignes_top}</table>
<h2>Ce que disent les chiffres</h2>
<ul>{interpretations}</ul>
</body></html>
"""
    with open(chemin_sortie, "w", encoding="utf-8") as fichier:
        fichier.write(html)
    return kpi
