"""Historique : prix moyen sur l'année et pendant la semaine du Black Friday."""
from collections import defaultdict   # dictionnaire qui crée une liste vide tout seul
from datetime import date


def moyenne(valeurs):
    if not valeurs:
        return None
    return sum(valeurs) / len(valeurs)


def analyser_historique(lignes):
    prix_annee = defaultdict(list)          # {boutique: [prix, prix, ...]}
    prix_black_friday = defaultdict(list)
    debut = date(2025, 11, 24)
    fin = date(2025, 11, 30)

    for ligne in lignes:
        try:
            jour = date.fromisoformat(ligne["date"])
            prix = int(float(ligne["prix_fcfa"]))
            source = ligne["source"]
        except (ValueError, KeyError, TypeError):
            continue                        # ligne invalide : on l'ignore

        prix_annee[source].append(prix)
        if debut <= jour <= fin:
            prix_black_friday[source].append(prix)

    resultat = {}
    for source, valeurs in prix_annee.items():
        moy_annee = moyenne(valeurs)
        valeurs_bf = prix_black_friday.get(source, [])
        moy_bf = moyenne(valeurs_bf)

        variation = None
        if moy_bf is not None and moy_annee:
            variation = round((moy_bf - moy_annee) / moy_annee * 100, 2)

        resultat[source] = {
            "nombre_observations_annuelles": len(valeurs),
            "prix_moyen_annuel_fcfa": round(moy_annee, 2),
            "nombre_observations_black_friday": len(valeurs_bf),
            "prix_moyen_black_friday_fcfa": round(moy_bf, 2) if moy_bf is not None else None,
            "variation_bf_vs_moyenne_pct": variation,
        }

    return {"periode": "2025-11-01 au 2026-10-31",
            "semaine_black_friday": "2025-11-24 au 2025-11-30",
            "resultats_par_enseigne": resultat,
            "note": "Pour Comptoir Ivoire, l'historique contient le prix catalogue sans remise, conformément au fichier LISEZ-MOI."}