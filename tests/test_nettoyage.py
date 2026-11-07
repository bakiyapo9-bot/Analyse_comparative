import unittest
from src.nettoyage import convertir_prix, normaliser_texte

class TestNettoyage(unittest.TestCase):
    def test_prix_avec_fcfa(self):
        self.assertEqual(convertir_prix("102 900 FCFA"), 102900)

    def test_prix_excel_espacement_fin(self):
        self.assertEqual(convertir_prix("279\u202f300"), 279300)

    def test_prix_manquant(self):
        self.assertIsNone(convertir_prix("Prix sur demande"))

    def test_normalisation(self):
        self.assertEqual(normaliser_texte('  ÉCRAN  SAMSUNG 24" '), "ecran samsung 24")

if __name__ == "__main__":
    unittest.main()
