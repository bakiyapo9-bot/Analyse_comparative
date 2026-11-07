import unittest
from src.rapprochement import rapprocher_produit
class TestRapprochement(unittest.TestCase):
    def test_nom_variante(self):
        catalogue={"P04":{"nom":"Tecno Spark 20 128 Go"}}
        pid,score=rapprocher_produit("SPARK 20 128GB - TECNO",catalogue)
        self.assertEqual(pid,"P04")
if __name__=="__main__": unittest.main()
