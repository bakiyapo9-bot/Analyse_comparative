from difflib import SequenceMatcher
from src.nettoyage import normaliser_texte
from utils.journal import anomalie

def _score(a,b):
    ta=set(a.split()); tb=set(b.split())
    j=len(ta&tb)/len(ta|tb) if ta|tb else 0
    return max(SequenceMatcher(None,a,b).ratio(), j)

ALIASES = {
    # Variantes linguistiques/abréviations observées dans les fichiers fournis.
    "hisense fridge 205l": "P20",
    "frigo hisense 205l": "P20",
    "lg air conditioner 1hp": "P24",
    "clim lg 1cv": "P24",
    "philips steam iron": "P27",
    "samsung microwave 23l": "P28",
    "hisense air conditioner 1 5hp": "P30",
}

def rapprocher_produit(nom, catalogue, seuil=0.42):
    cible=normaliser_texte(nom)
    if cible in ALIASES and ALIASES[cible] in catalogue:
        return ALIASES[cible], 1.0
    choix=[]
    for pid, produit in catalogue.items():
        ref=normaliser_texte(produit["nom"]); score=_score(cible,ref)
        # Les chiffres distinctifs (modèle/capacité) doivent être compatibles.
        nums=set(x for x in cible.split() if any(c.isdigit() for c in x))
        nums_ref=set(x for x in ref.split() if any(c.isdigit() for c in x))
        communs=nums & nums_ref
        if nums and nums_ref and not communs:
            score *= 0.55
        choix.append((score,pid))
    choix.sort(reverse=True)
    if not choix or choix[0][0] < seuil:
        return None, (choix[0][0] if choix else 0)
    # Évite une attribution incertaine en cas de scores trop proches.
    if len(choix)>1 and choix[0][0]-choix[1][0] < 0.025:
        anomalie(f"Rapprochement ambigu pour '{nom}' : {choix[:2]}")
    return choix[0][1], choix[0][0]

def rapprocher_toutes_les_offres(offres, catalogue):
    for offre in offres:
        pid, score=rapprocher_produit(offre["nom_brut"], catalogue)
        offre["produit_id"]=pid; offre["score_rapprochement"]=round(score,4)
        if pid is None: anomalie(f"Produit non rapproché : {offre['source']} / {offre['nom_brut']}")
    return offres
