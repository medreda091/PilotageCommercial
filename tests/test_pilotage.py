"""Tests du module de pilotage commercial (bibliothèque standard uniquement)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pilotage import (
    calculer_kpi,
    generer_rapport,
    graphique_barres_svg,
    interpreter,
    nettoyer,
    top_produits,
    ventes_par_mois,
    ventes_par_region,
)

EXEMPLE = [
    {
        "date": "2026-01-05",
        "commande": "C1",
        "region": "Nord",
        "produit": "Casque",
        "categorie": "Audio",
        "quantite": 2,
        "prix_unitaire": 100.0,
        "cout_unitaire": 60.0,
    },
    {
        "date": "2026-02-05",
        "commande": "C2",
        "region": "Sud",
        "produit": "Clavier",
        "categorie": "Périphériques",
        "quantite": 1,
        "prix_unitaire": 200.0,
        "cout_unitaire": 100.0,
    },
]


class TestNettoyage(unittest.TestCase):
    """Vérifie que les lignes invalides sont bien rejetées."""

    def test_rejet_quantite_negative(self):
        """Une quantité négative ne doit pas entrer dans les ventes propres."""
        mauvaise = dict(EXEMPLE[0], quantite=-1)
        propres, rejetees = nettoyer([mauvaise])
        self.assertEqual(propres, [])
        self.assertEqual(len(rejetees), 1)

    def test_rejet_prix_negatif(self):
        """Un prix négatif ne doit pas entrer dans les ventes propres."""
        mauvaise = dict(EXEMPLE[0], prix_unitaire=-5.0)
        propres, rejetees = nettoyer([mauvaise])
        self.assertEqual(propres, [])
        self.assertEqual(len(rejetees), 1)

    def test_lignes_valides_conservees(self):
        """Les lignes valides passent toutes le nettoyage."""
        propres, rejetees = nettoyer(EXEMPLE)
        self.assertEqual(len(propres), 2)
        self.assertEqual(rejetees, [])


class TestKpi(unittest.TestCase):
    """Vérifie les calculs d'indicateurs sur un petit jeu de données."""

    def test_chiffre_affaires_et_marge(self):
        """CA = 400 €, coûts = 220 €, marge = 180 €, taux = 45 %."""
        kpi = calculer_kpi(EXEMPLE)
        self.assertEqual(kpi["chiffre_affaires"], 400.0)
        self.assertEqual(kpi["cout_total"], 220.0)
        self.assertEqual(kpi["marge"], 180.0)
        self.assertEqual(kpi["taux_marge"], 45.0)

    def test_panier_moyen(self):
        """Deux commandes pour 400 € : le panier moyen est de 200 €."""
        kpi = calculer_kpi(EXEMPLE)
        self.assertEqual(kpi["nombre_commandes"], 2)
        self.assertEqual(kpi["panier_moyen"], 200.0)

    def test_kpi_sans_vente(self):
        """Sans vente, les indicateurs sont à zéro sans planter."""
        kpi = calculer_kpi([])
        self.assertEqual(kpi["chiffre_affaires"], 0.0)
        self.assertEqual(kpi["taux_marge"], 0.0)
        self.assertEqual(kpi["panier_moyen"], 0.0)


class TestRegroupements(unittest.TestCase):
    """Vérifie les regroupements par mois, région et produit."""

    def test_ventes_par_mois(self):
        """Chaque mois regroupe bien son propre chiffre d'affaires."""
        par_mois = ventes_par_mois(EXEMPLE)
        self.assertEqual(par_mois, {"2026-01": 200.0, "2026-02": 200.0})

    def test_ventes_par_region_triees(self):
        """Les régions sont triées par chiffre d'affaires décroissant."""
        par_region = ventes_par_region(EXEMPLE)
        self.assertEqual(list(par_region.keys()), ["Nord", "Sud"])

    def test_top_produits(self):
        """Le produit le plus vendu arrive en premier."""
        classement = top_produits(EXEMPLE)
        self.assertEqual(classement[0], ("Casque", 200.0))
        self.assertEqual(classement[1], ("Clavier", 200.0))


class TestRapport(unittest.TestCase):
    """Vérifie l'interprétation et la génération du rapport HTML."""

    def test_interpretation_non_vide(self):
        """L'interprétation contient au moins une phrase par thème."""
        kpi = calculer_kpi(EXEMPLE)
        phrases = interpreter(
            kpi,
            ventes_par_mois(EXEMPLE),
            ventes_par_region(EXEMPLE),
            top_produits(EXEMPLE),
        )
        self.assertGreaterEqual(len(phrases), 4)
        self.assertTrue(any("Casque" in phrase for phrase in phrases))

    def test_graphique_svg(self):
        """Le graphique généré est bien du SVG."""
        svg = graphique_barres_svg(["Janvier"], [100.0])
        self.assertIn("<svg", svg)
        self.assertIn("Janvier", svg)

    def test_rapport_html_contient_kpi(self):
        """Le rapport HTML contient les KPI et l'interprétation."""
        sortie = "/tmp/rapport_pilotage_test.html"
        kpi = generer_rapport(EXEMPLE, sortie)
        with open(sortie, encoding="utf-8") as fichier:
            contenu = fichier.read()
        self.assertIn("400", contenu)
        self.assertIn("Ce que disent les chiffres", contenu)
        self.assertEqual(kpi["chiffre_affaires"], 400.0)


if __name__ == "__main__":
    unittest.main()
