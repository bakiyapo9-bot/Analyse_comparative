from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

CATALOGUE_FILE = RAW_DIR / "catalogue_reference.csv"
MARCHE_FILE = RAW_DIR / "marche_lagune.csv"
BAOBAB_FILE = RAW_DIR / "baobab_shop.json"
COMPTOIR_FILE = RAW_DIR / "comptoir_ivoire.xlsx"
HISTORIQUE_FILE = RAW_DIR / "historique_prix.csv"

COMPARATIF_FILE = OUTPUT_DIR / "comparatif_produits.csv"
SYNTHESE_FILE = OUTPUT_DIR / "synthese.json"
PANIER_FILE = OUTPUT_DIR / "panier.json"
HISTORIQUE_RESULT_FILE = OUTPUT_DIR / "analyse_historique.json"
RAPPROCHEMENT_FILE = PROCESSED_DIR / "rapprochement.json"
PRIX_NETTOYES_FILE = PROCESSED_DIR / "prix_normalises.json"
JOURNAL_FILE = LOGS_DIR / "journal_anomalies.log"
