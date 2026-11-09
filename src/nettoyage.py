"""Nettoyage : rendre les données des 3 boutiques propres et comparables."""
import re
import unicodedata
from utils.journal import anomalie


def normaliser_texte(texte):
    """'  Écran  Samsung 24"  ' -> 'ecran samsung 24'"""
    texte = unicodedata.normalize("NFKD", str(texte or ""))
    texte = texte.encode("ascii", "ignore").decode("ascii")   # enlève les accents
    texte = texte.lower().replace("&", " et ")                # minuscules
    texte = re.sub(r"(\d)\s*gb\b", r"\1 go", texte)           # 128 GB -> 128 go
    texte = re.sub(r"(\d)\s*tb\b", r"\1 to", texte)           # 1 TB   -> 1 to
    texte = re.sub(r"[^a-z0-9]+", " ", texte)                 # garde lettres et chiffres
    return " ".join(texte.split())                            # un seul espace entre mots


def convertir_prix(valeur):
    """'12 500 FCFA' -> 12500 ; texte invalide -> None."""
    if valeur is None or str(valeur).strip() == "":
        return None
    if isinstance(valeur, (int, float)):
        return int(round(valeur))
    texte = str(valeur).replace(",", ".")
    texte = re.sub(r"[^0-9.]", "", texte)        # garde seulement chiffres et points
    try:
        return int(float(texte))
    except ValueError:
        return None


def creer_offre(source, reference, nom, prix, disponible, raison):
    """Fabrique une offre au format commun à toutes les boutiques."""
    return {
        "source": source,
        "reference": reference,
        "nom_brut": nom,
        "nom_normalise": normaliser_texte(nom),
        "prix_paye": prix,
        "disponible": disponible,
        "raison_indisponibilite": raison,
    }


def nettoyer_marche(lignes):
    resultat = []
    references_vues = set()
    for ligne in lignes:
        ref = str(ligne.get("reference", "")).strip()
        if ref in references_vues:                      # doublon : on l'ignore
            anomalie("Marché Lagune : doublon ignoré, référence " + ref)
            continue
        references_vues.add(ref)

        nom = str(ligne.get("designation", "")).strip()
        prix = convertir_prix(ligne.get("prix"))
        ancien_prix = convertir_prix(ligne.get("ancien_prix"))

        # Un prix plus de 3 fois supérieur à l'ancien prix est suspect
        if prix is not None and ancien_prix and prix > ancien_prix * 3:
            anomalie("Marché Lagune " + ref + " : prix suspect (" + str(prix) + " vs " + str(ancien_prix) + ")")
            prix = None

        dispo = str(ligne.get("disponibilite", "")).strip().lower()
        en_stock = dispo in ("en stock", "stock limite", "stock limité")

        if en_stock and prix is not None:
            raison = ""
        elif not en_stock:
            raison = dispo
        else:
            raison = "prix inexploitable ou suspect"

        if not nom:
            anomalie("Marché Lagune " + ref + " : désignation vide")
        if prix is None:
            anomalie("Marché Lagune " + ref + " : prix inexploitable")
        if not en_stock:
            anomalie("Marché Lagune " + ref + " : article non disponible (" + dispo + ")")

        resultat.append(creer_offre("Marché Lagune", ref, nom, prix, en_stock and prix is not None, raison))
    return resultat


def nettoyer_baobab(items):
    resultat = []
    for ligne in items:
        tarif = ligne.get("pricing") or {}
        prix = convertir_prix(tarif.get("amount"))
        livraison = convertir_prix(tarif.get("delivery_fee")) or 0
        stock = convertir_prix(ligne.get("stock")) or 0
        devise_ok = tarif.get("currency") in ("XOF", "FCFA")
        sku = ligne.get("sku")

        disponible = stock > 0 and prix is not None and devise_ok
        if disponible:
            raison = ""
        elif stock <= 0:
            raison = "rupture"
        else:
            raison = "prix/devise invalide"

        if prix is None:
            anomalie("Baobab Shop " + str(sku) + " : montant manquant")
        if stock <= 0:
            anomalie("Baobab Shop " + str(sku) + " : rupture de stock")
        if not devise_ok:
            anomalie("Baobab Shop " + str(sku) + " : devise inattendue " + str(tarif.get("currency")))

        # Le prix payé = prix de l'article + frais de livraison
        prix_paye = prix + livraison if (prix is not None and devise_ok) else None

        offre = creer_offre("Baobab Shop", sku, ligne.get("title", ""), prix_paye, disponible, raison)
        offre["prix_article"] = prix
        offre["livraison"] = livraison
        resultat.append(offre)
    return resultat


def nettoyer_comptoir(lignes):
    resultat = []
    for ligne in lignes:
        nom = str(ligne.get("Article") or "").strip()
        prix_catalogue = convertir_prix(ligne.get("Prix catalogue (FCFA)"))
        remise = convertir_prix(ligne.get("Remise (%)")) or 0
        stock = convertir_prix(ligne.get("Quantité en rayon")) or 0
        code = ligne.get("Code")

        # Le prix payé = prix catalogue moins la remise
        prix = None
        if prix_catalogue is not None:
            prix = round(prix_catalogue * (1 - remise / 100))

        disponible = stock > 0 and prix is not None
        if disponible:
            raison = ""
        elif stock <= 0:
            raison = "rupture"
        else:
            raison = "prix invalide"

        if prix_catalogue is None:
            anomalie("Comptoir Ivoire " + str(code) + " : prix catalogue invalide")
        if stock <= 0:
            anomalie("Comptoir Ivoire " + str(code) + " : quantité nulle")

        offre = creer_offre("Comptoir Ivoire", code, nom, prix, disponible, raison)
        offre["prix_catalogue"] = prix_catalogue
        offre["remise_pct"] = remise
        offre["stock"] = stock
        resultat.append(offre)
    return resultat


def nettoyer_toutes_les_boutiques(donnees):
    return (nettoyer_marche(donnees["marche_lagune"])
            + nettoyer_baobab(donnees["baobab_shop"])
            + nettoyer_comptoir(donnees["comptoir_ivoire"]))