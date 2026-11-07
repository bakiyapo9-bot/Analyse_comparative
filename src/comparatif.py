import csv
from config import COMPARATIF_FILE

SOURCES=("Marché Lagune", "Baobab Shop", "Comptoir Ivoire")

def construire_comparatif(offres, catalogue):
    par_produit={}
    for o in offres:
        if o.get("produit_id") and o.get("disponible") and o.get("prix_paye") is not None:
            par_produit.setdefault(o["produit_id"], {})[o["source"]]=o["prix_paye"]
    resultat=[]
    for pid, prix_par_source in par_produit.items():
        if len(prix_par_source)<2: continue
        minimum=min(prix_par_source.values()); maximum=max(prix_par_source.values()); moyenne=sum(prix_par_source.values())/len(prix_par_source)
        gagnants=[s for s,p in prix_par_source.items() if p==minimum]
        row={"produit_id":pid,"produit":catalogue[pid]["nom"],"meilleure_enseigne":" / ".join(gagnants),"meilleur_prix_fcfa":minimum,"prix_moyen_fcfa":round(moyenne),"ecart_max_min_fcfa":maximum-minimum,"ecart_pct_vs_min":round((maximum-minimum)/minimum*100,2) if minimum else 0}
        for s in SOURCES: row[s]=prix_par_source.get(s)
        resultat.append(row)
    resultat.sort(key=lambda x:x["produit_id"])
    return resultat

def exporter_comparatif(lignes, chemin=COMPARATIF_FILE):
    chemin.parent.mkdir(parents=True,exist_ok=True)
    champs=["produit_id","produit",*SOURCES,"meilleure_enseigne","meilleur_prix_fcfa","prix_moyen_fcfa","ecart_max_min_fcfa","ecart_pct_vs_min"]
    with open(chemin,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=champs,delimiter=";"); w.writeheader(); w.writerows(lignes)
    return chemin
