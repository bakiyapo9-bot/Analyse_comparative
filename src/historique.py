import csv
from collections import defaultdict
from datetime import date
from config import HISTORIQUE_RESULT_FILE

def analyser_historique(lignes):
    annuel=defaultdict(list); black_friday=defaultdict(list)
    debut=date(2025,11,24); fin=date(2025,11,30)
    for r in lignes:
        try:
            d=date.fromisoformat(r["date"]); prix=int(float(r["prix_fcfa"])); source=r["source"]
        except (ValueError,KeyError,TypeError): continue
        annuel[source].append(prix)
        if debut<=d<=fin: black_friday[source].append(prix)
    resultat={}
    for source, valeurs in annuel.items():
        moyenne=sum(valeurs)/len(valeurs)
        bf=black_friday.get(source,[])
        moyenne_bf=sum(bf)/len(bf) if bf else None
        resultat[source]={"nombre_observations_annuelles":len(valeurs),"prix_moyen_annuel_fcfa":round(moyenne,2),"nombre_observations_black_friday":len(bf),"prix_moyen_black_friday_fcfa":round(moyenne_bf,2) if moyenne_bf is not None else None,"variation_bf_vs_moyenne_pct":round((moyenne_bf-moyenne)/moyenne*100,2) if moyenne_bf is not None and moyenne else None}
    return {"periode":"2025-11-01 au 2026-10-31","semaine_black_friday":"2025-11-24 au 2025-11-30","resultats_par_enseigne":resultat,"note":"Pour Comptoir Ivoire, l'historique contient le prix catalogue sans remise, conformément au fichier LISEZ-MOI."}
