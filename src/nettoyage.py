import re, unicodedata
from utils.journal import anomalie

def normaliser_texte(texte):
    texte = unicodedata.normalize("NFKD", str(texte or "")).encode("ascii", "ignore").decode("ascii")
    texte = texte.lower().replace("&", " et ")
    texte = re.sub(r"\b(128|256|512|64)\s*gb\b", r"\1 go", texte)
    texte = re.sub(r"\b(1|1\.5)\s*tb\b", r"\1 to", texte)
    texte = re.sub(r"[^a-z0-9]+", " ", texte)
    return " ".join(texte.split())

def convertir_prix(valeur):
    if valeur is None or str(valeur).strip() == "":
        return None
    if isinstance(valeur, (int, float)):
        return int(round(valeur))
    texte = str(valeur).replace("FCFA", "").replace("XOF", "")
    texte = texte.replace("\u202f", "").replace("\xa0", "").replace(" ", "").replace(",", ".")
    texte = re.sub(r"[^0-9.]", "", texte)
    try:
        return int(float(texte)) if texte else None
    except ValueError:
        return None

def nettoyer_marche(lignes):
    resultat, vus = [], set()
    for r in lignes:
        ref = str(r.get("reference", "")).strip()
        if ref in vus:
            anomalie(f"Marché Lagune : doublon ignoré, référence {ref}")
            continue
        vus.add(ref)
        nom = str(r.get("designation", "")).strip()
        prix = convertir_prix(r.get("prix"))
        ancien_prix = convertir_prix(r.get("ancien_prix"))
        prix_suspect = prix is not None and ancien_prix is not None and ancien_prix > 0 and prix > ancien_prix * 3
        if prix_suspect:
            anomalie(f"Marché Lagune {ref} : prix actuel très supérieur à l'ancien prix ({prix} vs {ancien_prix}) ; prix écarté comme suspect, validation humaine nécessaire")
            prix = None
        dispo = str(r.get("disponibilite", "")).strip().lower()
        disponible = dispo in ("en stock", "stock limite", "stock limité")
        if not nom: anomalie(f"Marché Lagune {ref} : désignation vide")
        if prix is None: anomalie(f"Marché Lagune {ref} : prix inexploitable ({r.get('prix')})")
        if not disponible: anomalie(f"Marché Lagune {ref} : article non disponible ({dispo})")
        resultat.append({"source":"Marché Lagune", "reference":ref, "nom_brut":nom, "nom_normalise":normaliser_texte(nom), "prix_paye":prix, "disponible":disponible and prix is not None, "raison_indisponibilite":dispo if not disponible else ("prix inexploitable ou suspect" if prix is None else "")})
    return resultat

def nettoyer_baobab(items):
    resultat=[]
    for r in items:
        pricing=r.get("pricing") or {}; prix=convertir_prix(pricing.get("amount")); livraison=convertir_prix(pricing.get("delivery_fee")) or 0
        stock=convertir_prix(r.get("stock")) or 0; devise=pricing.get("currency")
        valide_devise=devise in ("XOF", "FCFA")
        disponible=stock>0 and prix is not None and valide_devise
        if prix is None: anomalie(f"Baobab Shop {r.get('sku')} : montant manquant/inexploitable")
        if stock<=0: anomalie(f"Baobab Shop {r.get('sku')} : rupture de stock")
        if not valide_devise: anomalie(f"Baobab Shop {r.get('sku')} : devise inattendue {devise}")
        resultat.append({"source":"Baobab Shop", "reference":r.get("sku"), "nom_brut":r.get("title", ""), "nom_normalise":normaliser_texte(r.get("title", "")), "prix_paye":prix+livraison if prix is not None and valide_devise else None, "disponible":disponible, "raison_indisponibilite":"" if disponible else ("rupture" if stock<=0 else "prix/devise invalide"), "prix_article":prix, "livraison":livraison})
    return resultat

def nettoyer_comptoir(lignes):
    resultat=[]
    for r in lignes:
        nom=str(r.get("Article") or "").strip(); brut=convertir_prix(r.get("Prix catalogue (FCFA)")); remise=convertir_prix(r.get("Remise (%)")) or 0; stock=convertir_prix(r.get("Quantité en rayon")) or 0
        prix=round(brut*(1-remise/100)) if brut is not None else None
        disponible=stock>0 and prix is not None
        if brut is None: anomalie(f"Comptoir Ivoire {r.get('Code')} : prix catalogue invalide")
        if stock<=0: anomalie(f"Comptoir Ivoire {r.get('Code')} : quantité nulle/rupture")
        resultat.append({"source":"Comptoir Ivoire", "reference":r.get("Code"), "nom_brut":nom, "nom_normalise":normaliser_texte(nom), "prix_paye":prix, "disponible":disponible, "raison_indisponibilite":"" if disponible else ("rupture" if stock<=0 else "prix invalide"), "prix_catalogue":brut, "remise_pct":remise, "stock":stock})
    return resultat

def nettoyer_toutes_les_boutiques(donnees):
    return nettoyer_marche(donnees["marche_lagune"])+nettoyer_baobab(donnees["baobab_shop"])+nettoyer_comptoir(donnees["comptoir_ivoire"])
