from time import perf_counter
from collections import defaultdict

def benchmark_recherche(historique, repetitions=100):
    # Recherche naïve : chaque recherche reparcourt toutes les lignes.
    cible=historique[-1] if historique else None
    t0=perf_counter()
    for _ in range(repetitions):
        next((r for r in historique if cible and r["date"]==cible["date"] and r["source"]==cible["source"] and r["produit_id"]==cible["produit_id"]),None)
    temps_lineaire=perf_counter()-t0
    # Indexation : une seule construction O(N), puis recherches moyennes O(1).
    t0=perf_counter(); index=defaultdict(list)
    for r in historique: index[(r["date"],r["source"],r["produit_id"])].append(r)
    temps_indexation=perf_counter()-t0
    cle=(cible["date"],cible["source"],cible["produit_id"]) if cible else None
    t0=perf_counter()
    for _ in range(repetitions):
        index.get(cle,[])
    temps_indexe=perf_counter()-t0
    return {"nombre_lignes":len(historique),"repetitions_recherche":repetitions,"recherche_lineaire_secondes":round(temps_lineaire,6),"construction_index_secondes":round(temps_indexation,6),"recherche_indexee_secondes":round(temps_indexe,6),"complexites":{"recherche_lineaire":"O(N) par recherche, O(R*N) pour R recherches","construction_index":"O(N)","recherche_indexee":"O(1) en moyenne par recherche","memoire_index":"O(N)"}}
