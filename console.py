"""Application console interactive de gestion du projet."""

import csv
import json
import subprocess
import sys
from pathlib import Path

from config import (
    BASE_DIR,
    RAW_DIR,
    OUTPUT_DIR,
    LOGS_DIR,
    COMPARATIF_FILE,
    SYNTHESE_FILE,
    PANIER_FILE,
    HISTORIQUE_RESULT_FILE,
    JOURNAL_FILE,
)
from main import executer_pipeline


ENSEIGNES = ("Marché Lagune", "Baobab Shop", "Comptoir Ivoire")


def lire_json(chemin):
    if not chemin.exists():
        return None
    with open(chemin, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


def afficher_titre(titre):
    print("\n" + "=" * 72)
    print(f" {titre}")
    print("=" * 72)


def attendre():
    input("\nAppuie sur Entrée pour revenir au menu...")


def verifier_sources():
    fichiers = sorted(RAW_DIR.glob("*")) if RAW_DIR.exists() else []
    attendus = [
        "catalogue_reference.csv",
        "marche_lagune.csv",
        "baobab_shop.json",
        "comptoir_ivoire.xlsx",
        "historique_prix.csv",
    ]
    afficher_titre("ÉTAT DES FICHIERS SOURCES")
    presents = {f.name for f in fichiers if f.is_file()}
    for nom in attendus:
        etat = "OK" if nom in presents else "MANQUANT"
        print(f"[{etat:8}] {nom}")
    print(f"\nDossier des sources : {RAW_DIR}")


def lancer_analyse():
    afficher_titre("EXÉCUTION DE L'ANALYSE COMPLÈTE")
    try:
        executer_pipeline(afficher=True)
        print("\nAnalyse terminée avec succès.")
    except Exception as erreur:
        print(f"\nUne erreur a empêché l'analyse : {erreur}")
        print("Vérifie les fichiers sources et les dépendances installées.")


def afficher_comparatif():
    afficher_titre("COMPARATIF DES PRIX")
    if not COMPARATIF_FILE.exists():
        print("Aucun comparatif disponible. Lance d'abord l'analyse complète (option 1).")
        return
    with open(COMPARATIF_FILE, "r", encoding="utf-8-sig", newline="") as fichier:
        lignes = list(csv.DictReader(fichier, delimiter=";"))
    if not lignes:
        print("Le fichier comparatif ne contient aucune ligne.")
        return
    print(f"{len(lignes)} produits comparables\n")
    for ligne in lignes:
        print(f"{ligne['produit_id']} — {ligne['produit']}")
        for enseigne in ENSEIGNES:
            prix = ligne.get(enseigne) or "Indisponible"
            if prix != "Indisponible":
                prix = f"{int(float(prix)):,} FCFA".replace(",", " ")
            print(f"   {enseigne:<20} : {prix}")
        print(f"   Meilleur prix       : {ligne['meilleur_prix_fcfa']} FCFA ({ligne['meilleure_enseigne']})")
        print(f"   Écart maximal       : {ligne['ecart_max_min_fcfa']} FCFA ({ligne['ecart_pct_vs_min']} %)\n")


def rechercher_produit():
    afficher_titre("RECHERCHER UN PRODUIT")
    if not COMPARATIF_FILE.exists():
        print("Aucun résultat. Lance d'abord l'analyse complète (option 1).")
        return
    terme = input("Saisis un nom de produit ou un identifiant (ex. P04) : ").strip().casefold()
    if not terme:
        print("Recherche vide.")
        return
    with open(COMPARATIF_FILE, "r", encoding="utf-8-sig", newline="") as fichier:
        lignes = list(csv.DictReader(fichier, delimiter=";"))
    resultats = [r for r in lignes if terme in r["produit"].casefold() or terme in r["produit_id"].casefold()]
    if not resultats:
        print("Aucun produit correspondant dans le comparatif.")
        return
    for r in resultats:
        print(f"\n{r['produit_id']} — {r['produit']}")
        print(f"Meilleure enseigne : {r['meilleure_enseigne']}")
        print(f"Meilleur prix     : {int(float(r['meilleur_prix_fcfa'])):,} FCFA".replace(",", " "))
        print(f"Prix moyen        : {int(float(r['prix_moyen_fcfa'])):,} FCFA".replace(",", " "))
        print(f"Écart             : {r['ecart_max_min_fcfa']} FCFA ({r['ecart_pct_vs_min']} %)" )
        for enseigne in ENSEIGNES:
            print(f"{enseigne:<20}: {r.get(enseigne) or 'Indisponible'}")


def afficher_synthese():
    afficher_titre("SYNTHÈSE GÉNÉRALE")
    synthese = lire_json(SYNTHESE_FILE)
    if synthese is None:
        print("Aucune synthèse disponible. Lance d'abord l'analyse complète (option 1).")
        return
    print(f"Produits comparables : {synthese['nombre_produits_comparables']}")
    print("\nNombre de meilleurs prix par enseigne :")
    for enseigne, nombre in synthese["victoires_enseigne"].items():
        print(f"  - {enseigne} : {nombre}")
    print("\nÉcart moyen par enseigne par rapport au prix le plus bas :")
    for enseigne, valeur in synthese["ecart_moyen_fcfa_vs_prix_bas"].items():
        affichage = "Non calculé" if valeur is None else f"{valeur:,.0f} FCFA".replace(",", " ")
        print(f"  - {enseigne} : {affichage}")
    print("\nTop 3 des gains à comparer :")
    for i, produit in enumerate(synthese["top_3_gains_a_comparer"], start=1):
        print(f"  {i}. {produit['produit_id']} — {produit['produit']} : "
              f"{produit['gain_fcfa']:,} FCFA".replace(",", " "))


def afficher_panier():
    afficher_titre("SIMULATION DU PANIER DE RENTRÉE")
    panier = lire_json(PANIER_FILE)
    if panier is None:
        print("Aucun panier calculé. Lance d'abord l'analyse complète (option 1).")
        return
    for enseigne, details in panier["totaux_par_enseigne"].items():
        total = details["total_fcfa"]
        montant = "Impossible (articles indisponibles)" if total is None else f"{total:,.0f} FCFA".replace(",", " ")
        print(f"\n{enseigne} : {montant}")
        if details["articles_indisponibles"]:
            print("  Articles manquants : " + ", ".join(details["articles_indisponibles"]))
    multi = panier["panier_multi_enseignes"]
    total_multi = multi["total_fcfa"]
    print("\nPanier multi-enseignes : " + ("Non calculable" if total_multi is None else f"{total_multi:,.0f} FCFA".replace(",", " ")))
    print("Plan d'achat :")
    for article in multi["plan_achat"]:
        if article.get("enseigne"):
            print(f"  - {article['produit_id']} : {article['quantite']} × "
                  f"{article['prix_unitaire_fcfa']} FCFA chez {article['enseigne']}")
        else:
            print(f"  - {article['produit_id']} : indisponible dans les trois enseignes")


def afficher_historique():
    afficher_titre("ANALYSE HISTORIQUE ET BLACK FRIDAY")
    historique = lire_json(HISTORIQUE_RESULT_FILE)
    if historique is None:
        print("Aucune analyse historique. Lance d'abord l'analyse complète (option 1).")
        return
    print(f"Période étudiée : {historique['periode']}")
    print(f"Période Black Friday : {historique['semaine_black_friday']}\n")
    for enseigne, resultat in historique["resultats_par_enseigne"].items():
        print(enseigne)
        print(f"  Observations : {resultat['nombre_observations_annuelles']}")
        print(f"  Prix moyen annuel : {resultat['prix_moyen_annuel_fcfa']} FCFA")
        print(f"  Observations Black Friday : {resultat['nombre_observations_black_friday']}")
        print(f"  Prix moyen Black Friday : {resultat['prix_moyen_black_friday_fcfa']} FCFA")
        print(f"  Variation : {resultat['variation_bf_vs_moyenne_pct']} %\n")


def afficher_anomalies():
    afficher_titre("JOURNAL DES ANOMALIES")
    if not JOURNAL_FILE.exists() or JOURNAL_FILE.stat().st_size == 0:
        print("Aucune anomalie enregistrée ou journal inexistant.")
        return
    contenu = JOURNAL_FILE.read_text(encoding="utf-8", errors="replace")
    print(contenu[-12000:])
    if len(contenu) > 12000:
        print("\n[Affichage limité aux 12 000 derniers caractères]")


def lancer_tests():
    afficher_titre("TESTS UNITAIRES")
    commande = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    resultat = subprocess.run(commande, cwd=BASE_DIR)
    print("\nTous les tests sont réussis." if resultat.returncode == 0 else "Certains tests ont échoué.")


def ouvrir_dossier_sortie():
    afficher_titre("FICHIERS GÉNÉRÉS")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fichiers = list(OUTPUT_DIR.iterdir())
    if not fichiers:
        print("Le dossier de sortie est vide. Lance d'abord l'analyse complète.")
    else:
        for fichier in fichiers:
            print(f" - {fichier.name} ({fichier.stat().st_size} octets)")
    print(f"\nEmplacement : {OUTPUT_DIR}")


def afficher_menu():
    print("\n" + "=" * 72)
    print("       APPLICATION CONSOLE — GESTION DU COMPARATEUR DE PRIX")
    print("=" * 72)
    print(" 1. Lancer l'analyse complète")
    print(" 2. Afficher le comparatif des prix")
    print(" 3. Rechercher un produit")
    print(" 4. Consulter la synthèse générale")
    print(" 5. Consulter le panier de rentrée")
    print(" 6. Consulter l'analyse historique / Black Friday")
    print(" 7. Consulter le journal des anomalies")
    print(" 8. Vérifier les fichiers sources")
    print(" 9. Lister les fichiers générés")
    print("10. Exécuter les tests unitaires")
    print(" 0. Quitter")
    print("-" * 72)


def main():
    actions = {
        "1": lancer_analyse,
        "2": afficher_comparatif,
        "3": rechercher_produit,
        "4": afficher_synthese,
        "5": afficher_panier,
        "6": afficher_historique,
        "7": afficher_anomalies,
        "8": verifier_sources,
        "9": ouvrir_dossier_sortie,
        "10": lancer_tests,
    }
    while True:
        afficher_menu()
        choix = input("Ton choix : ").strip()
        if choix == "0":
            print("\nMerci d'avoir utilisé le gestionnaire du comparateur. À bientôt !")
            break
        action = actions.get(choix)
        if action is None:
            print("Choix invalide. Sélectionne un numéro du menu.")
        else:
            try:
                action()
            except KeyboardInterrupt:
                print("\nOpération interrompue par l'utilisateur.")
            except Exception as erreur:
                print(f"\nErreur pendant l'opération : {erreur}")
            attendre()


if __name__ == "__main__":
    main()
