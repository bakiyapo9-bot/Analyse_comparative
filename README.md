# Analyse comparative

Application Python de comparaison de trois enseignes à partir de fichiers CSV, JSON et Excel. Le projet comprend une **interface graphique de bureau réalisée avec CustomTkinter** pour lancer les traitements et consulter les résultats.

# Architecture du projet

├── README.md
├── .gitignore
├── src
│   ├── chargement.py
│   ├── comparatif.py
│   ├── complexite.py
│   ├── historique.py
│   ├── interface.py
│   ├── nettoyage.py
│   ├── panier.py
│   ├── rapprochement.py
│   └── synthese.py
├── utils
│   ├── formatage.py
│   └── journal.py
├── tests
│   ├── test_chargement.py
│   ├── test_comparatif.py
│   ├── test_nettoyage.py
│   └── test_rapprochement.py
├── config.py
├── console.py
├── data
│   ├── raw
│   │   ├── baobab_shop.json
│   │   ├── catalogue_reference.csv
│   │   ├── comptoir_ivoire.xlsx
│   │   ├── historique_prix.csv
│   │   └── marche_lagune.csv
│   ├── processed
│   │   ├── prix_normalises.json
│   │   └── rapprochement.json
│   └── output
│       ├── analyse_historique.json
│       ├── comparatif_produits.csv
│       ├── panier.json
│       └── synthese.json
├── logs
│   └── journal_anomalies.log
├── main.py
└── requirements.txt