"""Synthèse : qui gagne le plus souvent ? quels produits ont le plus gros écart ?"""
from src.comparatif import SOURCES


def calculer_synthese(comparatif):
    victoires = {}                              # {boutique: part de victoires}
    ecarts = {source: [] for source in SOURCES}  # {boutique: [écart avec le meilleur prix]}
    gains = []

    for ligne in comparatif:
        # Chaque produit donne 1 victoire au total.
        # En cas d'égalité, cette victoire est partagée entre les gagnants.
        gagnants = ligne["meilleure_enseigne"].split(" / ")
        part = 1 / len(gagnants)
        for gagnant in gagnants:
            victoires[gagnant] = victoires.get(gagnant, 0) + part

        meilleur_prix = ligne["meilleur_prix_fcfa"]
        for source in SOURCES:
            prix = ligne.get(source)
            if prix is not None:
                ecarts[source].append(prix - meilleur_prix)

        gains.append({"produit_id": ligne["produit_id"], "produit": ligne["produit"],
                      "gain_fcfa": ligne["ecart_max_min_fcfa"],
                      "gain_pct_vs_min": ligne["ecart_pct_vs_min"]})

    # Arrondi pour éviter les nombres du type 9.333333 (le total reste égal au nombre de produits)
    victoires = {nom: round(v, 2) for nom, v in victoires.items()}

    ecart_moyen = {}
    for source, liste in ecarts.items():
        ecart_moyen[source] = round(sum(liste) / len(liste), 2) if liste else None

    gains.sort(key=lambda g: g["gain_fcfa"], reverse=True)   # plus gros gain en premier

    return {"nombre_produits_comparables": len(comparatif),
            "victoires_enseigne": victoires,
            "ecart_moyen_fcfa_vs_prix_bas": ecart_moyen,
            "top_3_gains_a_comparer": gains[:3]}