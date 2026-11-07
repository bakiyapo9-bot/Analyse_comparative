import csv, json
from openpyxl import load_workbook
from config import (CATALOGUE_FILE, MARCHE_FILE, BAOBAB_FILE, COMPTOIR_FILE, HISTORIQUE_FILE)
from utils.journal import anomalie

def lire_csv(chemin, delimiter=","):
    with open(chemin, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delimiter))

def charger_catalogue(chemin=CATALOGUE_FILE):
    lignes = lire_csv(chemin, ",")
    return {r["produit_id"]: r for r in lignes if r.get("produit_id")}

def charger_marche_lagune(chemin=MARCHE_FILE):
    return lire_csv(chemin, ";")

def charger_baobab_shop(chemin=BAOBAB_FILE):
    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("items", [])

def charger_comptoir_ivoire(chemin=COMPTOIR_FILE):
    wb = load_workbook(chemin, data_only=True, read_only=True)
    nom_feuille = "Tarifs octobre 2026"
    if nom_feuille not in wb.sheetnames:
        raise ValueError(f"Feuille Excel absente : {nom_feuille}")
    ws = wb[nom_feuille]
    entetes = [c.value for c in ws[3]]
    lignes = []
    for valeurs in ws.iter_rows(min_row=4, values_only=True):
        if not any(v is not None for v in valeurs):
            continue
        lignes.append(dict(zip(entetes, valeurs)))
    wb.close()
    return lignes

def charger_historique(chemin=HISTORIQUE_FILE):
    return lire_csv(chemin, ",")

def charger_toutes_les_donnees():
    donnees = {
        "catalogue": charger_catalogue(),
        "marche_lagune": charger_marche_lagune(),
        "baobab_shop": charger_baobab_shop(),
        "comptoir_ivoire": charger_comptoir_ivoire(),
        "historique": charger_historique(),
    }
    anomalie("Chargement terminé : " + ", ".join(f"{k}={len(v)}" for k, v in donnees.items()))
    return donnees
