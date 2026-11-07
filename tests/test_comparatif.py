import unittest
from src.comparatif import construire_comparatif
class TestComparatif(unittest.TestCase):
    def test_comparaison(self):
        offres=[{"produit_id":"P1","source":"A","disponible":True,"prix_paye":100},{"produit_id":"P1","source":"B","disponible":True,"prix_paye":120}]
        r=construire_comparatif(offres,{"P1":{"nom":"Produit test"}})
        self.assertEqual(len(r),1); self.assertEqual(r[0]["meilleur_prix_fcfa"],100); self.assertEqual(r[0]["ecart_max_min_fcfa"],20)
if __name__=="__main__": unittest.main()
