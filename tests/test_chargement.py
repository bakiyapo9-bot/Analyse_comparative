import unittest
from src.chargement import charger_catalogue, charger_marche_lagune, charger_baobab_shop, charger_comptoir_ivoire, charger_historique
class TestChargement(unittest.TestCase):
    def test_sources_non_vides(self):
        self.assertEqual(len(charger_catalogue()),30)
        self.assertGreater(len(charger_marche_lagune()),0)
        self.assertGreater(len(charger_baobab_shop()),0)
        self.assertGreater(len(charger_comptoir_ivoire()),0)
        self.assertGreater(len(charger_historique()),20000)
if __name__=="__main__": unittest.main()
