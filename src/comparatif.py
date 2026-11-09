"""Comparaison : trouver la meilleure boutique pour chaque produit."""
import csv
from config import COMPARATIF_FILE

SOURCES = ("Marché Lagune", "Baobab Shop", "Comptoir Ivoire")


def regrouper_prix(offres):
    """Renvoie {produit_id: {boutique: prix}} avec seulement les offres valides."""
    prix = {}
    for offre in offres:
        valide = offre.get("produit_id") and offre.get("disponible") and offre.get("prix_paye") is not None
        if valide:
            pid = offre["produit_id"]
            if pid not in prix:
                prix[pid] = {}
            prix[pid][offre["source"]] = offre["prix_paye"]
    return prix


def construire_comparatif(offres, catalogue):
    prix_par_produit = regrouper_prix(offres)
    resultat = []

    for pid in sorted(prix_par_produit):
        prix_par_source = prix_par_produit[pid]
        if len(prix_par_source) < 2:          # impossible de comparer avec 1 seule boutique
            continue

        liste_prix = list(prix_par_source.values())
        minimum = min(liste_prix)
        maximum = max(liste_prix)
        moyenne = sum(liste_prix) / len(liste_prix)

        # S'il y a égalité, plusieurs boutiques gagnent
        gagnants = [s for s, p in prix_par_source.items() if p == minimum]

        ligne = {
            "produit_id": pid,
            "produit": catalogue[pid]["nom"],
            "meilleure_enseigne": " / ".join(gagnants),
            "meilleur_prix_fcfa": minimum,
            "prix_moyen_fcfa": round(moyenne),
            "ecart_max_min_fcfa": maximum - minimum,
            "ecart_pct_vs_min": round((maximum - minimum) / minimum * 100, 2) if minimum else 0,
            # Écart demandé dans le sujet : prix moyen - meilleur prix
            "ecart_moyen_vs_meilleur_fcfa": round(moyenne - minimum),
            "ecart_moyen_pct": round((moyenne - minimum) / moyenne * 100, 2) if moyenne else 0,
        }
        for source in SOURCES:
            ligne[source] = prix_par_source.get(source)   # None si absent
        resultat.append(ligne)

    return resultat


def exporter_comparatif(lignes, chemin=COMPARATIF_FILE):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    colonnes = ["produit_id", "produit", *SOURCES, "meilleure_enseigne", "meilleur_prix_fcfa",
                "prix_moyen_fcfa", "ecart_moyen_vs_meilleur_fcfa", "ecart_moyen_pct",
                "ecart_max_min_fcfa", "ecart_pct_vs_min"]
    with open(chemin, "w", encoding="utf-8-sig", newline="") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes, delimiter=";")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)
    return chemin