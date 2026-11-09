import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import json
import tracemalloc
from time import perf_counter

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


def mesurer_etape(nom, fonction, *args):
    """
    Exécute une étape et mesure son temps ainsi que le pic
    d'allocations mémoire Python supplémentaires pendant cette étape.

    La mémoire est exprimée en Mo (MiB : 1 048 576 octets).
    """
    tracer_deja_actif = tracemalloc.is_tracing()

    if not tracer_deja_actif:
        tracemalloc.start()

    tracemalloc.reset_peak()
    memoire_depart, _ = tracemalloc.get_traced_memory()

    debut = perf_counter()

    try:
        resultat = fonction(*args)
        fin = perf_counter()

        # Une fonction appelée peut avoir arrêté tracemalloc elle-même.
        if tracemalloc.is_tracing():
            _, pic_memoire = tracemalloc.get_traced_memory()
            memoire_max_mo = max(0, pic_memoire - memoire_depart) / (1024 ** 2)
        else:
            # Le benchmark interne mesure séparément la mémoire de son index.
            memoire_max_mo = 0.0
            if isinstance(resultat, dict):
                memoire_max_mo = resultat.get("memoire_index_mo", 0.0)

    finally:
        if not tracer_deja_actif and tracemalloc.is_tracing():
            tracemalloc.stop()

    duree = fin - debut

    print(
        f"{nom:<35} : {duree:.6f} seconde(s) | "
        f"{memoire_max_mo:.6f} Mo"
    )

    return resultat, duree, round(memoire_max_mo, 6)


def compter_elements(valeur):
    """Retourne le nombre d'éléments d'une collection, sans supposer son type."""
    try:
        return len(valeur)
    except TypeError:
        return 0


def executer_pipeline(afficher=True):
    debut_total = perf_counter()

    temps_execution = {}
    memoire_execution = {}

    if afficher:
        print("=" * 75)
        print(" ANALYSE COMPARATIVE — PIPELINE COMPLET ")
        print("=" * 75)
        print("\nMESURE DU TEMPS ET DE LA MEMOIRE")
        print("-" * 75)

    # 1. CHARGEMENT
    donnees, temps_execution["Chargement"], memoire_execution["Chargement"] = mesurer_etape(
        "Chargement des données",
        charger_toutes_les_donnees
    )

    # 2. NETTOYAGE
    offres, temps_execution["Nettoyage"], memoire_execution["Nettoyage"] = mesurer_etape(
        "Nettoyage des données",
        nettoyer_toutes_les_boutiques,
        donnees
    )

    sauvegarder_json(PRIX_NETTOYES_FILE, offres)

    # 3. RAPPROCHEMENT
    offres, temps_execution["Rapprochement"], memoire_execution["Rapprochement"] = mesurer_etape(
        "Rapprochement des produits",
        rapprocher_toutes_les_offres,
        offres,
        donnees["catalogue"]
    )

    sauvegarder_json(RAPPROCHEMENT_FILE, offres)

    # 4. COMPARAISON
    comparatif, temps_execution["Comparaison"], memoire_execution["Comparaison"] = mesurer_etape(
        "Comparaison des prix",
        construire_comparatif,
        offres,
        donnees["catalogue"]
    )

    # 5. EXPORTATION
    _, temps_execution["Exportation"], memoire_execution["Exportation"] = mesurer_etape(
        "Exportation du comparatif",
        exporter_comparatif,
        comparatif
    )

    # 6. SYNTHESE
    synthese, temps_execution["Synthèse"], memoire_execution["Synthèse"] = mesurer_etape(
        "Calcul de la synthèse",
        calculer_synthese,
        comparatif
    )

    sauvegarder_json(SYNTHESE_FILE, synthese)

    # 7. PANIER
    panier, temps_execution["Panier"], memoire_execution["Panier"] = mesurer_etape(
        "Simulation du panier",
        simuler_panier,
        offres,
        donnees["catalogue"]
    )

    sauvegarder_json(PANIER_FILE, panier)

    # 8. ANALYSE HISTORIQUE
    historique, temps_execution["Historique"], memoire_execution["Historique"] = mesurer_etape(
        "Analyse de l'historique",
        analyser_historique,
        donnees["historique"]
    )

    sauvegarder_json(HISTORIQUE_RESULT_FILE, historique)

    # 9. BENCHMARK DE RECHERCHE
    benchmark, temps_execution["Benchmark"], memoire_execution["Benchmark"] = mesurer_etape(
        "Benchmark de recherche",
        benchmark_recherche,
        donnees["historique"]
    )

    fin_total = perf_counter()
    temps_total = fin_total - debut_total

    # Nombre d'éléments réellement traités par chaque étape.
    # Pour le chargement, on compte les offres issues des trois boutiques.
    nombre_produits_execution = {
        "Chargement": sum(
            compter_elements(donnees.get(cle, []))
            for cle in ("marche_lagune", "baobab_shop", "comptoir_ivoire")
        ),
        "Nettoyage": compter_elements(offres),
        "Rapprochement": compter_elements(offres),
        "Comparaison": compter_elements(comparatif),
        "Exportation": compter_elements(comparatif),
        "Synthèse": compter_elements(comparatif),
        "Panier": compter_elements(donnees.get("catalogue", [])),
        # Pour l'historique et le benchmark, il s'agit du nombre d'observations.
        "Historique": compter_elements(donnees.get("historique", [])),
        "Benchmark": compter_elements(donnees.get("historique", [])),
    }

    # Pic le plus élevé parmi les mesures individuelles des étapes.
    # Ce n'est pas le pic RAM global du processus.
    memoire_max_etape_mo = max(memoire_execution.values(), default=0.0)

    resultats = {
        "donnees": donnees,
        "offres": offres,
        "comparatif": comparatif,
        "synthese": synthese,
        "panier": panier,
        "historique": historique,
        "benchmark": benchmark,
        "temps_execution": temps_execution,
        "temps_total": temps_total,
        "memoire_execution": memoire_execution,
        "nombre_produits_execution": nombre_produits_execution,
        "memoire_max_etape_mo": memoire_max_etape_mo,
    }

    if afficher:
        print("\n" + "=" * 75)
        print(" RESULTATS DU PROJET ")
        print("=" * 75)

        print(
            f"Sources chargées : "
            f"{len(donnees['marche_lagune'])} lignes Marché Lagune, "
            f"{len(donnees['baobab_shop'])} Baobab, "
            f"{len(donnees['comptoir_ivoire'])} Comptoir, "
            f"{len(donnees['historique'])} observations historiques"
        )

        print(
            f"Offres rapprochées : "
            f"{sum(o.get('produit_id') is not None for o in offres)}"
            f"/{len(offres)}"
        )

        print(f"Produits comparables : {len(comparatif)}")
        print("\nVictoires :", synthese["victoires_enseigne"])
        print("\nTop 3 gains :")

        for ligne in synthese["top_3_gains_a_comparer"]:
            print(
                f" - {ligne['produit_id']} "
                f"{ligne['produit']} : "
                f"{ligne['gain_fcfa']:,} FCFA"
            )

        print(
            "\nPanier multi-enseignes :",
            panier["panier_multi_enseignes"]["total_fcfa"]
        )

        print("\nBenchmark :", benchmark)

        print("\n" + "=" * 75)
        print(" TABLEAU DES PERFORMANCES ")
        print("=" * 75)
        print(
            f"{'Traitement':<30} "
            f"{'Produits':>12} "
            f"{'Temps (s)':>14} "
            f"{'Mémoire (Mo)':>16}"
        )
        print("-" * 82)

        for nom, duree in temps_execution.items():
            memoire = memoire_execution.get(nom, 0.0)
            nombre = nombre_produits_execution.get(nom, 0)
            print(f"{nom:<30} {nombre:>12} {duree:>14.6f} {memoire:>16.6f}")

        print("-" * 82)
        print(f"{'TEMPS TOTAL':<30} {temps_total:>14.6f}")
        print(
            f"Pic maximal mesuré parmi les étapes : "
            f"{memoire_max_etape_mo:.6f} Mo"
        )
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
            print(
                "Installez les dépendances avec : "
                "python -m pip install -r requirements.txt"
            )
        else:
            raise


if __name__ == "__main__":
    main()
