PANIER={"P04":1,"P12":1,"P14":2,"P15":1,"P28":1}

def simuler_panier(offres, catalogue):
    prix={}
    for o in offres:
        if o.get("produit_id") and o.get("disponible") and o.get("prix_paye") is not None:
            prix.setdefault(o["produit_id"],{})[o["source"]]=o["prix_paye"]
    totaux={}; details={}
    for source in ("Marché Lagune","Baobab Shop","Comptoir Ivoire"):
        total=0; manquants=[]; lignes=[]
        for pid,qte in PANIER.items():
            p=prix.get(pid,{}).get(source)
            if p is None: manquants.append(pid)
            else: total+=p*qte
            lignes.append({"produit_id":pid,"produit":catalogue[pid]["nom"],"quantite":qte,"prix_unitaire_fcfa":p,"sous_total_fcfa":p*qte if p is not None else None})
        totaux[source]=total if not manquants else None
        details[source]={"total_fcfa":totaux[source],"articles_indisponibles":manquants,"lignes":lignes}
    meilleur_total=0; plan=[]
    for pid,qte in PANIER.items():
        options=prix.get(pid,{})
        if not options:
            plan.append({"produit_id":pid,"quantite":qte,"enseigne":None,"prix_unitaire_fcfa":None}); continue
        source,p=min(options.items(),key=lambda x:x[1]); meilleur_total+=p*qte
        plan.append({"produit_id":pid,"produit":catalogue[pid]["nom"],"quantite":qte,"enseigne":source,"prix_unitaire_fcfa":p,"sous_total_fcfa":p*qte})
    complet=all(x.get("enseigne") for x in plan)
    return {"composition":PANIER,"totaux_par_enseigne":details,"panier_multi_enseignes":{"total_fcfa":meilleur_total if complet else None,"plan_achat":plan}}
