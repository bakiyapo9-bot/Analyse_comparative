"""Point d'entrée du projet : lance l'interface graphique CustomTkinter."""

import json

from config import (
    SYNTHESE_FILE,
    PANIER_FILE,
    HISTORIQUE_RESULT_FILE,
    RAPPROCHEMENT_FILE,
    PRIX_NETTOYES_FILE,
)
from src.chargement import charger_toutes_les_donnees
from src.nettoyage import nettoyer_toutes_les_boutiques
from src.rapprochement import rapprocher_toutes_les_offres
from src.comparatif import construire_comparatif, exporter_comparatif
from src.synthese import calculer_synthese
from src.panier import simuler_panier
from src.historique import analyser_historique
from src.complexite import benchmark_recherche


def sauvegarder_json(chemin, objet):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(objet, fichier, ensure_ascii=False, indent=2, default=str)


def executer_pipeline(afficher=True):
    """Exécute les huit livrables et retourne tous les résultats utiles."""
    if afficher:
        print("=" * 66)
        print(" ANALYSE COMPARATIVE — PIPELINE COMPLET ")
        print("=" * 66)

    donnees = charger_toutes_les_donnees()
    offres = nettoyer_toutes_les_boutiques(donnees)
    sauvegarder_json(PRIX_NETTOYES_FILE, offres)

    offres = rapprocher_toutes_les_offres(offres, donnees["catalogue"])
    sauvegarder_json(RAPPROCHEMENT_FILE, offres)

    comparatif = construire_comparatif(offres, donnees["catalogue"])
    exporter_comparatif(comparatif)

    synthese = calculer_synthese(comparatif)
    sauvegarder_json(SYNTHESE_FILE, synthese)

    panier = simuler_panier(offres, donnees["catalogue"])
    sauvegarder_json(PANIER_FILE, panier)

    historique = analyser_historique(donnees["historique"])
    sauvegarder_json(HISTORIQUE_RESULT_FILE, historique)

    benchmark = benchmark_recherche(donnees["historique"])

    resultats = {
        "donnees": donnees,
        "offres": offres,
        "comparatif": comparatif,
        "synthese": synthese,
        "panier": panier,
        "historique": historique,
        "benchmark": benchmark,
    }

    if afficher:
        print(f"Sources chargées : {len(donnees['marche_lagune'])} lignes Marché Lagune, "
              f"{len(donnees['baobab_shop'])} Baobab, "
              f"{len(donnees['comptoir_ivoire'])} Comptoir, "
              f"{len(donnees['historique'])} observations historiques")
        print(f"Offres rapprochées : {sum(o.get('produit_id') is not None for o in offres)}/{len(offres)}")
        print(f"Produits comparables : {len(comparatif)}")
        print("\nVictoires :", synthese["victoires_enseigne"])
        print("\nTop 3 gains :")
        for ligne in synthese["top_3_gains_a_comparer"]:
            print(f" - {ligne['produit_id']} {ligne['produit']} : {ligne['gain_fcfa']:,} FCFA")
        print("\nPanier multi-enseignes :", panier["panier_multi_enseignes"]["total_fcfa"])
        print("\nBenchmark :", benchmark)
        print("\nFichiers générés dans data/output et data/processed.")

    return resultats


def main():
    """Lance l'interface graphique. Le pipeline reste appelable séparément."""
    try:
        from src.interface import lancer_interface
        lancer_interface()
    except ModuleNotFoundError as erreur:
        if erreur.name == "customtkinter":
            print("La bibliothèque CustomTkinter n'est pas installée.")
            print("Installez les dépendances avec : python -m pip install -r requirements.txt")
        else:
            raise


if __name__ == "__main__":
    main()
