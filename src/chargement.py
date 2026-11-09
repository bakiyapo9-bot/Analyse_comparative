"""Chargement : lire les fichiers et les mettre en mémoire."""
import csv
import json
from openpyxl import load_workbook
from config import CATALOGUE_FILE, MARCHE_FILE, BAOBAB_FILE, COMPTOIR_FILE, HISTORIQUE_FILE
from utils.journal import anomalie


def lire_csv(chemin, separateur=","):
    """Lit un CSV : renvoie une liste de dictionnaires (1 dictionnaire = 1 ligne)."""
    with open(chemin, encoding="utf-8-sig", newline="") as fichier:
        return list(csv.DictReader(fichier, delimiter=separateur))


def charger_catalogue(chemin=CATALOGUE_FILE):
    """Renvoie un dictionnaire {produit_id: ligne du produit}."""
    catalogue = {}
    for ligne in lire_csv(chemin, ","):
        if ligne.get("produit_id"):
            catalogue[ligne["produit_id"]] = ligne
    return catalogue


def charger_marche_lagune(chemin=MARCHE_FILE):
    return lire_csv(chemin, ";")


def charger_baobab_shop(chemin=BAOBAB_FILE):
    with open(chemin, encoding="utf-8") as fichier:
        donnees = json.load(fichier)
    return donnees.get("items", [])


def charger_comptoir_ivoire(chemin=COMPTOIR_FILE):
    classeur = load_workbook(chemin, data_only=True, read_only=True)
    nom_feuille = "Tarifs octobre 2026"
    if nom_feuille not in classeur.sheetnames:
        raise ValueError("Feuille Excel absente : " + nom_feuille)

    lignes_excel = list(classeur[nom_feuille].iter_rows(min_row=3, values_only=True))
    classeur.close()

    entetes = lignes_excel[0]          # la ligne 3 contient les titres des colonnes
    lignes = []
    for valeurs in lignes_excel[1:]:   # les données commencent à la ligne 4
        if any(v is not None for v in valeurs):      # on ignore les lignes vides
            lignes.append(dict(zip(entetes, valeurs)))
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
    resume = ", ".join(nom + "=" + str(len(contenu)) for nom, contenu in donnees.items())
    anomalie("Chargement terminé : " + resume)
    return donnees