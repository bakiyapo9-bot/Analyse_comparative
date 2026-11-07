from collections import Counter

def calculer_synthese(comparatif):
    victoires=Counter(); ecarts={"Marché Lagune":[],"Baobab Shop":[],"Comptoir Ivoire":[]}
    gains=[]
    for r in comparatif:
        gagnants=r["meilleure_enseigne"].split(" / ")
        for g in gagnants: victoires[g]+=1
        bas=r["meilleur_prix_fcfa"]
        for s in ecarts:
            p=r.get(s)
            if p is not None: ecarts[s].append(p-bas)
        gains.append({"produit_id":r["produit_id"],"produit":r["produit"],"gain_fcfa":r["ecart_max_min_fcfa"],"gain_pct_vs_min":r["ecart_pct_vs_min"]})
    moyennes={s:round(sum(v)/len(v),2) if v else None for s,v in ecarts.items()}
    gains.sort(key=lambda x:x["gain_fcfa"],reverse=True)
    return {"nombre_produits_comparables":len(comparatif),"victoires_enseigne":dict(victoires),"ecart_moyen_fcfa_vs_prix_bas":moyennes,"top_3_gains_a_comparer":gains[:3]}
