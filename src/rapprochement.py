"""Rapprochement : retrouver à quel produit du catalogue correspond chaque offre."""
from difflib import SequenceMatcher
from src.nettoyage import normaliser_texte
from utils.journal import anomalie

# Noms qui ne se ressemblent pas assez : on donne directement le bon produit
ALIASES = {
    "hisense fridge 205l": "P20",
    "frigo hisense 205l": "P20",
    "lg air conditioner 1hp": "P24",
    "clim lg 1cv": "P24",
    "philips steam iron": "P27",
    "samsung microwave 23l": "P28",
    "hisense air conditioner 1 5hp": "P30",
}


def calculer_score(nom_a, nom_b):
    """Score de ressemblance entre 0 (rien en commun) et 1 (identiques)."""
    score_lettres = SequenceMatcher(None, nom_a, nom_b).ratio()

    mots_a = set(nom_a.split())
    mots_b = set(nom_b.split())
    tous_les_mots = mots_a | mots_b
    score_mots = len(mots_a & mots_b) / len(tous_les_mots) if tous_les_mots else 0

    return max(score_lettres, score_mots)


def mots_avec_chiffres(texte):
    """'samsung 24 pouces' -> {'24'} : les chiffres identifient le modèle."""
    return set(mot for mot in texte.split() if any(c.isdigit() for c in mot))


def rapprocher_produit(nom, catalogue, seuil=0.42):
    cible = normaliser_texte(nom)

    # 1. Cas simple : le nom est dans la liste des alias
    if cible in ALIASES and ALIASES[cible] in catalogue:
        return ALIASES[cible], 1.0

    # 2. On calcule un score avec chaque produit du catalogue
    scores = []
    for pid, produit in catalogue.items():
        reference = normaliser_texte(produit["nom"])
        score = calculer_score(cible, reference)

        # Si les deux noms ont des chiffres mais aucun en commun -> pénalité
        chiffres_cible = mots_avec_chiffres(cible)
        chiffres_ref = mots_avec_chiffres(reference)
        if chiffres_cible and chiffres_ref and not (chiffres_cible & chiffres_ref):
            score = score * 0.55

        scores.append((score, pid))

    scores.sort(reverse=True)           # meilleur score en premier

    # 3. Pas assez ressemblant : on abandonne
    if not scores or scores[0][0] < seuil:
        return None, (scores[0][0] if scores else 0)

    # 4. Deux scores presque égaux : on prévient (réponse incertaine)
    if len(scores) > 1 and scores[0][0] - scores[1][0] < 0.025:
        anomalie("Rapprochement ambigu pour '" + nom + "' : " + str(scores[:2]))

    return scores[0][1], scores[0][0]


def rapprocher_toutes_les_offres(offres, catalogue):
    for offre in offres:
        pid, score = rapprocher_produit(offre["nom_brut"], catalogue)
        offre["produit_id"] = pid
        offre["score_rapprochement"] = round(score, 4)
        if pid is None:
            anomalie("Produit non rapproché : " + offre["source"] + " / " + offre["nom_brut"])
    return offres