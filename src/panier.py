"""Panier : combien coÃ»te un panier type dans chaque boutique ?"""
from src.comparatif import regrouper_prix, SOURCES

# produit -> quantitÃ© achetÃ©e
PANIER = {"P04": 1, "P12": 1, "P14": 2, "P15": 1, "P28": 1}


def simuler_panier(offres, catalogue):
    prix = regrouper_prix(offres)

    # Partie 1 : total du panier dans chaque boutique
    totaux = {}
    for source in SOURCES:
        total = 0
        manquants = []
        lignes = []
        for pid, quantite in PANIER.items():
            prix_unitaire = prix.get(pid, {}).get(source)
            sous_total = None
            if prix_unitaire is None:
                manquants.append(pid)          # la boutique n'a pas cet article
            else:
                sous_total = prix_unitaire * quantite
                total = total + sous_total
            lignes.append({"produit_id": pid, "produit": catalogue[pid]["nom"],
                           "quantite": quantite, "prix_unitaire_fcfa": prix_unitaire,
                           "sous_total_fcfa": sous_total})
        # Si un article manque, le total n'a pas de sens -> None
        totaux[source] = {"total_fcfa": total if not manquants else None,
                          "articles_indisponibles": manquants, "lignes": lignes}

    # Partie 2 : acheter chaque article dans la boutique la moins chÃ¨re
    total_multi = 0
    plan = []
    complet = True
    for pid, quantite in PANIER.items():
        options = prix.get(pid, {})
        if not options:
            complet = False
            plan.append({"produit_id": pid, "quantite": quantite,
                         "enseigne": None, "prix_unitaire_fcfa": None})
            continue

        meilleure_source = None
        meilleur_prix = None
        for source, p in options.items():
            if meilleur_prix is None or p < meilleur_prix:
                meilleure_source = source
                meilleur_prix = p

        total_multi = total_multi + meilleur_prix * quantite
        plan.append({"produit_id": pid, "produit": catalogue[pid]["nom"], "quantite": quantite,
                     "enseigne": meilleure_source, "prix_unitaire_fcfa": meilleur_prix,
                     "sous_total_fcfa": meilleur_prix * quantite})

    return {"composition": PANIER,
            "totaux_par_enseigne": totaux,
            "panier_multi_enseignes": {"total_fcfa": total_multi if complet else None,
                                       "plan_achat": plan}}
