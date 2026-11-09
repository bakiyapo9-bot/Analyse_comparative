
from time import perf_counter
from collections import defaultdict
import tracemalloc


def mesurer_memoire(fonction, *args):
    """Mesure la mémoire supplémentaire utilisée par une fonction."""

    tracemalloc.start()
    tracemalloc.reset_peak()

    memoire_depart, _ = tracemalloc.get_traced_memory()

    try:
        resultat = fonction(*args)

        memoire_actuelle, memoire_max = tracemalloc.get_traced_memory()

        return {
            "memoire_actuelle_mo": round(
                max(0, memoire_actuelle - memoire_depart) / (1024 ** 2), 6
            ),
            "memoire_max_mo": round(
                max(0, memoire_max - memoire_depart) / (1024 ** 2), 6
            )
        }

    finally:
        tracemalloc.stop()


def benchmark_recherche(historique, repetitions=100):
    """Compare les performances temporelles et spatiales."""

    cible = historique[-1] if historique else None

    # Recherche linéaire
    t0 = perf_counter()

    for _ in range(repetitions):
        next(
            (
                r for r in historique
                if cible
                and r["date"] == cible["date"]
                and r["source"] == cible["source"]
                and r["produit_id"] == cible["produit_id"]
            ),
            None
        )

    temps_lineaire = perf_counter() - t0

    # Construction de l'index
    def construire_index():
        index = defaultdict(list)

        for r in historique:
            index[
                (r["date"], r["source"], r["produit_id"])
            ].append(r)

        return index

    t0 = perf_counter()
    index = construire_index()
    temps_indexation = perf_counter() - t0

    # Mesure mémoire de la construction de l'index
    memoire = mesurer_memoire(construire_index)

    # Recherche indexée
    cle = (
        (cible["date"], cible["source"], cible["produit_id"])
        if cible else None
    )

    t0 = perf_counter()

    for _ in range(repetitions):
        index.get(cle, [])

    temps_indexe = perf_counter() - t0

    return {
        "nombre_lignes": len(historique),
        "repetitions_recherche": repetitions,

        "recherche_lineaire_secondes": round(temps_lineaire, 6),
        "construction_index_secondes": round(temps_indexation, 6),
        "recherche_indexee_secondes": round(temps_indexe, 6),

        "memoire_index_mo": memoire["memoire_max_mo"],
        "memoire_index_actuelle_mo": memoire["memoire_actuelle_mo"],

        "complexites": {
            "recherche_lineaire": "O(N) par recherche",
            "construction_index": "O(N)",
            "recherche_indexee": "O(1) en moyenne",
            "memoire_index": "O(N)"
        }
    }


def mesurer_temps(nom, fonction, *args):
    """Mesure le temps d'exécution d'une fonction."""

    debut = perf_counter()
    resultat = fonction(*args)
    fin = perf_counter()

    temps = fin - debut

    print(f"{nom} : {temps:.6f} seconde(s)")

    return resultat
