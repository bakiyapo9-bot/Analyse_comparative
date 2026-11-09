"""Interface graphique de l'application Analyse comparative."""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import threading
import tkinter as tk

from tkinter import ttk, messagebox
from pathlib import Path

import customtkinter as ctk

from config import (
    BASE_DIR,
    RAW_DIR,
    OUTPUT_DIR,
    LOGS_DIR,
    COMPARATIF_FILE,
    SYNTHESE_FILE,
    PANIER_FILE,
    HISTORIQUE_RESULT_FILE,
    JOURNAL_FILE,
)


# ============================================================
# CONFIGURATION GENERALE
# ============================================================

ENSEIGNES = (
    "Marché Lagune",
    "Baobab Shop",
    "Comptoir Ivoire",
)

# Palette officielle : blanc, orange et vert uniquement.
# Palette de couleurs : ORANGE DOMINANT

BLANC = "#FFFFFF"
FOND = "#FFFFFF"
CARTE = "#FFFFFF"

ORANGE = "#E86A33"
ORANGE_CLAIR = "#F2994A"
SIDEBAR = "#E86A33"
BORDURE = "#F2994A"

VERT = "#1F5F45"
VERT_FONCE = "#1F5F45"
VERT_MOYEN = "#2E7D5B"
VERT_CLAIR = "#E8F3ED"
MENTHE = "#E8F3ED"

# Alias avec préfixe COULEUR_ pour compatibilité
COULEUR_FOND = FOND
COULEUR_CARTE = CARTE
COULEUR_SIDEBAR = SIDEBAR
COULEUR_ACCENT = ORANGE
COULEUR_TEXTE = VERT_FONCE
COULEUR_SECONDAIRE = VERT_MOYEN
COULEUR_BORDURE = BORDURE
COULEUR_ORANGE = ORANGE
COULEUR_ORANGE_CLAIR = ORANGE_CLAIR
COULEUR_VERT = VERT
COULEUR_VERT_SECONDAIRE = VERT_MOYEN
COULEUR_VERT_CLAIR = VERT_CLAIR


# ============================================================
# APPLICATION PRINCIPALE
# ============================================================

class ApplicationAnalyseComparative(ctk.CTk):
    """Fenêtre principale de l'application."""

    def __init__(self):
        super().__init__()

        self.title("Analyse comparative")
        self.geometry("1280x800")
        self.minsize(1050, 680)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.configure(fg_color=FOND)

        self.page_actuelle = None
        self.nav_buttons = {}

        self.dernieres_performances = None

        self.nombre_produits = 0
        self.nombre_victoires = 0

        self._configurer_styles_tableaux()
        self._construire_structure()

        self.actualiser_indicateurs()
        self.afficher_page("Accueil")

    # ========================================================
    # CONFIGURATION DES TABLEAUX
    # ========================================================

    def _configurer_styles_tableaux(self):

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Comparateur.Treeview",
            background=BLANC,
            foreground=VERT_FONCE,
            fieldbackground=BLANC,
            rowheight=34,
            borderwidth=0,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Comparateur.Treeview.Heading",
            background=MENTHE,
            foreground=VERT_FONCE,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
        )

        style.map(
            "Comparateur.Treeview",
            background=[("selected", MENTHE)],
            foreground=[("selected", VERT_FONCE)],
        )

    # ========================================================
    # CONSTRUCTION DE LA STRUCTURE
    # ========================================================

    def _construire_structure(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Menu latéral

        self.sidebar = ctk.CTkFrame(
            self,
            width=235,
            corner_radius=0,
            fg_color=SIDEBAR,
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.sidebar.grid_propagate(False)

        logo = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        )

        logo.pack(
            fill="x",
            padx=20,
            pady=(26, 28),
        )

        ctk.CTkLabel(
            logo,
            text="Analyse comparative",
            text_color=BLANC,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=21,
                weight="bold",
            ),
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.sidebar,
            text="ESPACE DE TRAVAIL",
            text_color=MENTHE,
            font=ctk.CTkFont(
                size=10,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 10),
        )

        pages = [
            "Accueil",
            "Comparatif",
            "Synthèse",
            "Panier",
            "Historique",
            "Anomalies",
            "Sources & fichiers",
            "Tests",
            "Performances et complexité",
        ]

        for nom in pages:

            bouton = ctk.CTkButton(
                self.sidebar,
                text=nom,
                anchor="w",
                height=42,
                corner_radius=9,
                fg_color="transparent",
                hover_color=VERT_MOYEN,
                text_color=BLANC,
                font=ctk.CTkFont(size=13),
                command=lambda n=nom: self.afficher_page(n),
            )

            bouton.pack(
                fill="x",
                padx=13,
                pady=3,
            )

            self.nav_buttons[nom] = bouton

        # Partie inférieure du menu

        bas = ctk.CTkFrame(
            self.sidebar,
            fg_color=VERT_MOYEN,
            corner_radius=12,
        )

        bas.pack(
            side="bottom",
            fill="x",
            padx=14,
            pady=18,
        )

        ctk.CTkLabel(
            bas,
            text="PROJET PYTHON",
            text_color=BLANC,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(
            anchor="w",
            padx=12,
            pady=(11, 3),
        )

        ctk.CTkLabel(
            bas,
            text="CSV  •  JSON  •  EXCEL",
            text_color=MENTHE,
            font=ctk.CTkFont(size=10),
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 11),
        )

        # Zone principale

        self.zone_principale = ctk.CTkFrame(
            self,
            fg_color=FOND,
            corner_radius=0,
        )

        self.zone_principale.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.zone_principale.grid_rowconfigure(1, weight=1)
        self.zone_principale.grid_columnconfigure(0, weight=1)

        # En-tête

        self.entete = ctk.CTkFrame(
            self.zone_principale,
            fg_color=BLANC,
            corner_radius=0,
            height=76,
        )

        self.entete.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        self.entete.grid_columnconfigure(0, weight=1)

        self.titre_page = ctk.CTkLabel(
            self.entete,
            text="Accueil",
            text_color=VERT_FONCE,
            font=ctk.CTkFont(
                size=22,
                weight="bold",
            ),
        )

        self.titre_page.grid(
            row=0,
            column=0,
            sticky="w",
            padx=28,
            pady=(15, 0),
        )

        self.sous_titre = ctk.CTkLabel(
            self.entete,
            text="Vue générale de votre analyse commerciale",
            text_color=VERT_MOYEN,
            font=ctk.CTkFont(size=11),
        )

        self.sous_titre.grid(
            row=1,
            column=0,
            sticky="w",
            padx=29,
            pady=(2, 13),
        )

        self.bouton_actualiser = ctk.CTkButton(
            self.entete,
            text="Actualiser",
            width=115,
            height=34,
            fg_color=VERT,
            hover_color=VERT_MOYEN,
            text_color=BLANC,
            command=self.actualiser_page,
        )

        self.bouton_actualiser.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=25,
        )

        # Contenu défilant

        self.contenu = ctk.CTkScrollableFrame(
            self.zone_principale,
            fg_color=FOND,
            corner_radius=0,
        )

        self.contenu.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=22,
            pady=18,
        )

        self.contenu.grid_columnconfigure(0, weight=1)

        # Barre de statut

        self.barre_statut = ctk.CTkLabel(
            self.zone_principale,
            text="Prêt",
            anchor="w",
            text_color=VERT_MOYEN,
            font=ctk.CTkFont(size=10),
        )

        self.barre_statut.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=26,
            pady=(0, 9),
        )

    # ========================================================
    # FONCTIONS GRAPHIQUES GENERALES
    # ========================================================

    def _vider_contenu(self):

        for widget in self.contenu.winfo_children():
            widget.destroy()

    def _titre_section(self, parent, texte, aide=None):

        ctk.CTkLabel(
            parent,
            text=texte,
            text_color=VERT_FONCE,
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            pady=(4, 3),
        )

        if aide:

            ctk.CTkLabel(
                parent,
                text=aide,
                text_color=VERT_MOYEN,
                font=ctk.CTkFont(size=11),
            ).pack(
                anchor="w",
                pady=(0, 10),
            )

    def _carte(
        self,
        parent,
        titre,
        valeur,
        detail="",
        couleur=VERT,
    ):

        carte = ctk.CTkFrame(
            parent,
            fg_color=CARTE,
            corner_radius=13,
            border_width=1,
            border_color=BORDURE,
        )

        ctk.CTkLabel(
            carte,
            text=titre.upper(),
            text_color=VERT_MOYEN,
            font=ctk.CTkFont(
                size=10,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            padx=16,
            pady=(14, 4),
        )

        ctk.CTkLabel(
            carte,
            text=str(valeur),
            text_color=couleur,
            font=ctk.CTkFont(
                size=25,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            padx=16,
        )

        ctk.CTkLabel(
            carte,
            text=detail if detail else " ",
            text_color=VERT_MOYEN,
            font=ctk.CTkFont(size=10),
        ).pack(
            anchor="w",
            padx=16,
            pady=(2, 13),
        )

        return carte

    def _bouton_principal(self, parent, texte, commande):

        return ctk.CTkButton(
            parent,
            text=texte,
            command=commande,
            height=40,
            corner_radius=9,
            fg_color=VERT,
            hover_color=VERT_MOYEN,
            text_color=BLANC,
            font=ctk.CTkFont(
                size=12,
                weight="bold",
            ),
        )

    # ========================================================
    # NAVIGATION ENTRE LES PAGES
    # ========================================================

    def afficher_page(self, nom):

        self.page_actuelle = nom

        for n, bouton in self.nav_buttons.items():

            bouton.configure(
                fg_color=VERT_MOYEN if n == nom else "transparent",
                text_color=BLANC,
            )

        self.titre_page.configure(text=nom)

        descriptions = {
            "Accueil": "Vue générale de votre analyse commerciale",
            "Comparatif": "Consultez et recherchez les meilleurs prix",
            "Synthèse": "Indicateurs de performance et économies potentielles",
            "Panier": "Simulation du panier et plan d'achat",
            "Historique": "Évolution historique des prix",
            "Anomalies": "Contrôle qualité des données importées",
            "Sources & fichiers": "Vérification des fichiers et résultats",
            "Tests": "Contrôle automatique des modules du projet",
            "Performances et complexité": "Temps d'exécution et mémoire utilisée",
        }

        self.sous_titre.configure(
            text=descriptions.get(nom, "")
        )

        self._vider_contenu()

        pages = {
            "Accueil": self.page_accueil,
            "Comparatif": self.page_comparatif,
            "Synthèse": self.page_synthese,
            "Panier": self.page_panier,
            "Historique": self.page_historique,
            "Anomalies": self.page_anomalies,
            "Sources & fichiers": self.page_sources,
            "Tests": self.page_tests,
            "Performances et complexité": self.page_performances,
        }

        pages[nom]()

    def actualiser_page(self):

        self.actualiser_indicateurs()

        self.afficher_page(
            self.page_actuelle or "Accueil"
        )

        self._statut("Données actualisées.")

    # ========================================================
    # LECTURE ET TRAITEMENT DES DONNEES
    # ========================================================

    @staticmethod
    def _lire_json(chemin):

        if not chemin.exists():
            return None

        try:

            return json.loads(
                chemin.read_text(encoding="utf-8")
            )

        except (OSError, json.JSONDecodeError):

            return None

    @staticmethod
    def _lire_comparatif():

        if not COMPARATIF_FILE.exists():
            return []

        with open(
            COMPARATIF_FILE,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as fichier:

            return list(
                csv.DictReader(
                    fichier,
                    delimiter=";",
                )
            )

    @staticmethod
    def _nombre(valeur):
        """Convertit une valeur de prix en nombre."""

        if valeur in (None, "", "None"):
            return None

        try:

            if isinstance(valeur, (int, float)):
                return float(valeur)

            valeur = str(valeur).strip()

            valeur = (
                valeur.replace("FCFA", "")
                .replace("FCFA", "")
                .replace("\u00a0", "")
                .replace(" ", "")
            )

            if "," in valeur and "." not in valeur:
                valeur = valeur.replace(",", ".")

            return float(valeur)

        except (TypeError, ValueError):
            return None

    @classmethod
    def _fcfa(cls, valeur):

        nombre = cls._nombre(valeur)

        if nombre is None:
            return "—"

        return f"{nombre:,.0f} FCFA".replace(",", " ")

    @classmethod
    def _ecart_pourcentage(cls, prix_min, prix_max):
        """Calcule l'écart entre deux prix en pourcentage."""

        minimum = cls._nombre(prix_min)
        maximum = cls._nombre(prix_max)

        if minimum is None or maximum is None or minimum <= 0:
            return None

        return ((maximum - minimum) / minimum) * 100

    @classmethod
    def _calculer_ecart_produit(cls, ligne):
        """Calcule l'écart en pourcentage entre les boutiques."""

        prix = []

        for enseigne in ENSEIGNES:

            valeur = cls._nombre(
                ligne.get(enseigne)
            )

            if valeur is not None and valeur > 0:
                prix.append(valeur)

        if len(prix) < 2:
            return None

        return cls._ecart_pourcentage(
            min(prix),
            max(prix),
        )

    @classmethod
    def _pourcentage(cls, valeur):

        nombre = cls._nombre(valeur)

        if nombre is None:
            return "—"

        return f"{nombre:.2f} %".replace(".", ",")

    def _ecarts_moyens_par_enseigne(self):
        """Calcule le surcoût moyen de chaque boutique en %."""

        lignes = self._lire_comparatif()

        resultats = {}

        for enseigne in ENSEIGNES:

            ecarts = []

            for ligne in lignes:

                prix_boutique = self._nombre(
                    ligne.get(enseigne)
                )

                prix_valides = [
                    self._nombre(ligne.get(nom))
                    for nom in ENSEIGNES
                ]

                prix_valides = [
                    prix for prix in prix_valides
                    if prix is not None and prix > 0
                ]

                if (
                    prix_boutique is None
                    or prix_boutique <= 0
                    or not prix_valides
                ):
                    continue

                prix_min = min(prix_valides)

                ecart = (
                    (prix_boutique - prix_min)
                    / prix_min
                ) * 100

                ecarts.append(ecart)

            resultats[enseigne] = (
                sum(ecarts) / len(ecarts)
                if ecarts else None
            )

        return resultats

    def _statut(self, message):

        self.barre_statut.configure(
            text=message
        )

    def actualiser_indicateurs(self):

        lignes = self._lire_comparatif()

        synthese = (
            self._lire_json(SYNTHESE_FILE) or {}
        )

        self.nombre_produits = len(lignes)

        self.nombre_victoires = sum(
            synthese.get(
                "victoires_enseigne", {}
            ).values()
        )

    # ========================================================
    # PAGE ACCUEIL
    # ========================================================

    def page_accueil(self):

        synthese = self._lire_json(SYNTHESE_FILE) or {}

        lignes = self._lire_comparatif()

        top = synthese.get(
            "top_3_gains_a_comparer", []
        )

        fichiers = [
            "catalogue_reference.csv",
            "marche_lagune.csv",
            "baobab_shop.json",
            "comptoir_ivoire.xlsx",
            "historique_prix.csv",
        ]

        nb_sources = sum(
            (RAW_DIR / nom).exists()
            for nom in fichiers
        )

        bandeau = ctk.CTkFrame(
            self.contenu,
            fg_color=MENTHE,
            corner_radius=14,
        )

        bandeau.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 15),
        )

        bandeau.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            bandeau,
            text="Bienvenue dans votre espace de comparaison",
            text_color=VERT_FONCE,
            font=ctk.CTkFont(
                size=19,
                weight="bold",
            ),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(17, 4),
        )

        ctk.CTkLabel(
            bandeau,
            text="Analysez les offres des trois boutiques et repérez les économies possibles.",
            text_color=VERT_MOYEN,
            font=ctk.CTkFont(size=11),
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 16),
        )

        self._bouton_principal(
            bandeau,
            "Lancer l'analyse",
            self.lancer_analyse,
        ).grid(
            row=0,
            column=1,
            rowspan=2,
            padx=20,
            pady=15,
        )

        # Indicateurs

        indicateurs = ctk.CTkFrame(
            self.contenu,
            fg_color="transparent",
        )

        indicateurs.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 15),
        )

        for i in range(4):
            indicateurs.grid_columnconfigure(i, weight=1)

        cartes = [
            (
                "Produits comparables",
                len(lignes),
                "Produits analysés",
                VERT,
            ),
            (
                "Sources disponibles",
                f"{nb_sources}/5",
                "Fichiers sources détectés",
                ORANGE,
            ),
            (
                "Victoires boutique",
                self.nombre_victoires,
                "Meilleurs prix attribués",
                VERT,
            ),
            (
                "Top économies",
                self._fcfa(
                    top[0].get("gain_fcfa")
                ) if top else "—",
                "Gain maximal identifié",
                ORANGE,
            ),
        ]

        for i, (titre, valeur, detail, couleur) in enumerate(cartes):

            self._carte(
                indicateurs,
                titre,
                valeur,
                detail,
                couleur,
            ).grid(
                row=0,
                column=i,
                sticky="ew",
                padx=5,
            )

        # Partie inférieure

        bas = ctk.CTkFrame(
            self.contenu,
            fg_color="transparent",
        )

        bas.grid(
            row=2,
            column=0,
            sticky="ew",
        )

        bas.grid_columnconfigure(0, weight=1)
        bas.grid_columnconfigure(1, weight=1)

        bloc_top = ctk.CTkFrame(
            bas,
            fg_color=BLANC,
            corner_radius=13,
            border_width=1,
            border_color=BORDURE,
        )

        bloc_top.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7),
        )

        self._titre_section(
            bloc_top,
            "Top 3 des écarts de prix",
            "Produits présentant les gains les plus importants",
        )

        for i, produit in enumerate(top, 1):

            ligne = ctk.CTkFrame(
                bloc_top,
                fg_color=MENTHE,
                corner_radius=8,
            )

            ligne.pack(
                fill="x",
                padx=13,
                pady=4,
            )

            ctk.CTkLabel(
                ligne,
                text=f"{i:02d}",
                text_color=ORANGE,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold",
                ),
                width=30,
            ).pack(
                side="left",
                padx=8,
                pady=9,
            )

            ctk.CTkLabel(
                ligne,
                text=produit.get(
                    "produit",
                    produit.get("produit_id", "Produit"),
                ),
                text_color=VERT_FONCE,
                font=ctk.CTkFont(size=11),
                anchor="w",
            ).pack(
                side="left",
                fill="x",
                expand=True,
            )

            ctk.CTkLabel(
                ligne,
                text=self._fcfa(
                    produit.get("gain_fcfa")
                ),
                text_color=VERT,
                font=ctk.CTkFont(
                    size=11,
                    weight="bold",
                ),
            ).pack(
                side="right",
                padx=10,
            )

        if not top:

            ctk.CTkLabel(
                bloc_top,
                text="Lancez l'analyse pour afficher les résultats.",
                text_color=VERT_MOYEN,
            ).pack(
                padx=14,
                pady=20,
            )

        bloc_actions = ctk.CTkFrame(
            bas,
            fg_color=BLANC,
            corner_radius=13,
            border_width=1,
            border_color=BORDURE,
        )

        bloc_actions.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(7, 0),
        )

        self._titre_section(
            bloc_actions,
            "Accès rapide",
            "Ouvrez directement un espace de travail",
        )

        for texte, page in [
            ("Consulter le comparatif", "Comparatif"),
            ("Voir la synthèse", "Synthèse"),
            ("Simuler le panier", "Panier"),
            ("Consulter les anomalies", "Anomalies"),
        ]:

            ctk.CTkButton(
                bloc_actions,
                text=texte,
                anchor="w",
                fg_color=MENTHE,
                hover_color="#E8F3ED",
                text_color=VERT_FONCE,
                command=lambda p=page: self.afficher_page(p),
            ).pack(
                fill="x",
                padx=14,
                pady=5,
            )

    # ========================================================
    # CREATION DES TABLEAUX
    # ========================================================

    def _creer_tableau(
        self,
        parent,
        colonnes,
        hauteurs=14,
    ):

        cadre = ctk.CTkFrame(
            parent,
            fg_color=BLANC,
            corner_radius=10,
            border_width=1,
            border_color=BORDURE,
        )

        cadre.pack(
            fill="both",
            expand=True,
            pady=(8, 0),
        )

        tree = ttk.Treeview(
            cadre,
            columns=colonnes,
            show="headings",
            height=hauteurs,
            style="Comparateur.Treeview",
        )

        for colonne in colonnes:

            tree.heading(
                colonne,
                text=colonne,
            )

            tree.column(
                colonne,
                width=135,
                minwidth=85,
                anchor="w",
            )

        scroll_y = ttk.Scrollbar(
            cadre,
            orient="vertical",
            command=tree.yview,
        )

        scroll_x = ttk.Scrollbar(
            cadre,
            orient="horizontal",
            command=tree.xview,
        )

        tree.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )

        tree.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(8, 0),
            pady=8,
        )

        scroll_y.grid(
            row=0,
            column=1,
            sticky="ns",
            pady=8,
        )

        scroll_x.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(8, 0),
        )

        cadre.grid_rowconfigure(0, weight=1)
        cadre.grid_columnconfigure(0, weight=1)

        return tree

    # ========================================================
    # PAGE COMPARATIF
    # ========================================================

    def page_comparatif(self):

        lignes = self._lire_comparatif()

        barre = ctk.CTkFrame(
            self.contenu,
            fg_color="transparent",
        )

        barre.pack(
            fill="x",
            pady=(0, 8),
        )

        recherche = ctk.CTkEntry(
            barre,
            placeholder_text="Rechercher un produit ou une référence...",
            width=360,
            height=38,
        )

        recherche.pack(
            side="left",
            padx=(0, 8),
        )

        compteur = ctk.CTkLabel(
            barre,
            text=f"{len(lignes)} produit(s)",
            text_color=VERT_MOYEN,
        )

        compteur.pack(
            side="left",
            padx=8,
        )

        colonnes = (
            "Référence",
            "Produit",
            *ENSEIGNES,
            "Meilleure enseigne",
            "Meilleur prix",
            "Prix moyen",
            "Écart (%)",
        )

        tree = self._creer_tableau(
            self.contenu,
            colonnes,
            17,
        )

        tree.column("Produit", width=175)
        tree.column("Meilleure enseigne", width=160)
        tree.column("Écart (%)", width=110, anchor="center")

        def remplir(*_):

            tree.delete(
                *tree.get_children()
            )

            terme = recherche.get().strip().casefold()

            filtres = [
                ligne for ligne in lignes
                if terme in ligne.get("produit", "").casefold()
                or terme in ligne.get("produit_id", "").casefold()
            ]

            for ligne in filtres:

                valeurs = [
                    ligne.get("produit_id", ""),
                    ligne.get("produit", ""),
                ]

                valeurs += [
                    self._fcfa(
                        ligne.get(enseigne)
                    )
                    for enseigne in ENSEIGNES
                ]

                valeurs += [
                    ligne.get("meilleure_enseigne", ""),
                    self._fcfa(
                        ligne.get("meilleur_prix_fcfa")
                    ),
                    self._fcfa(
                        ligne.get("prix_moyen_fcfa")
                    ),
                    self._pourcentage(
                        self._calculer_ecart_produit(ligne)
                    ),
                ]

                tree.insert(
                    "",
                    "end",
                    values=valeurs,
                )

            compteur.configure(
                text=f"{len(filtres)} produit(s)"
            )

        recherche.bind(
            "<KeyRelease>",
            remplir,
        )

        remplir()

        if not lignes:

            ctk.CTkLabel(
                self.contenu,
                text="Aucun comparatif disponible. Lancez d'abord l'analyse complète.",
                text_color=VERT_MOYEN,
            ).pack(
                anchor="w",
                pady=12,
            )

    # ========================================================
    # PAGE SYNTHESE
    # ========================================================

    def page_synthese(self):

        s = self._lire_json(SYNTHESE_FILE)

        if not s:

            self._message_vide(
                "Aucune synthèse disponible. Lancez l'analyse complète."
            )

            return

        cartes = ctk.CTkFrame(
            self.contenu,
            fg_color="transparent",
        )

        cartes.pack(
            fill="x",
            pady=(0, 15),
        )

        for i in range(3):
            cartes.grid_columnconfigure(i, weight=1)

        # Nombre de produits

        self._carte(
            cartes,
            "Produits comparables",
            s.get("nombre_produits_comparables", 0),
            "Produits analysés",
            VERT,
        ).grid(
            row=0,
            column=0,
            padx=5,
            sticky="ew",
        )

        # Boutique gagnante

        victoires = s.get(
            "victoires_enseigne",
            {},
        )

        gagnant = (
            max(victoires, key=victoires.get)
            if victoires else "—"
        )

        self._carte(
            cartes,
            "Enseigne en tête",
            gagnant,
            f"{victoires.get(gagnant, 0)} meilleur(s) prix",
            ORANGE,
        ).grid(
            row=0,
            column=1,
            padx=5,
            sticky="ew",
        )

        # Gain maximal

        top = s.get(
            "top_3_gains_a_comparer",
            [],
        )

        self._carte(
            cartes,
            "Gain maximal",
            self._fcfa(
                top[0].get("gain_fcfa")
            ) if top else "—",
            "Économie potentielle",
            VERT,
        ).grid(
            row=0,
            column=2,
            padx=5,
            sticky="ew",
        )

        # Victoires par boutique

        self._titre_section(
            self.contenu,
            "Nombre de victoires par enseigne",
        )

        maximum = max(
            victoires.values(),
            default=1,
        )

        for enseigne, nombre in victoires.items():

            ligne = ctk.CTkFrame(
                self.contenu,
                fg_color=BLANC,
                corner_radius=9,
                border_width=1,
                border_color=BORDURE,
            )

            ligne.pack(
                fill="x",
                pady=4,
            )

            ctk.CTkLabel(
                ligne,
                text=enseigne,
                width=190,
                anchor="w",
                text_color=VERT_FONCE,
            ).pack(
                side="left",
                padx=14,
                pady=10,
            )

            barre = ctk.CTkProgressBar(
                ligne,
                width=300,
                progress_color=VERT_MOYEN,
                fg_color=MENTHE,
            )

            barre.pack(
                side="left",
                padx=8,
            )

            barre.set(
                nombre / maximum
            )

            ctk.CTkLabel(
                ligne,
                text=str(nombre),
                text_color=VERT,
                font=ctk.CTkFont(
                    size=12,
                    weight="bold",
                ),
            ).pack(
                side="right",
                padx=16,
            )

        # Ecarts moyens en pourcentage

        self._titre_section(
            self.contenu,
            "Surcoût moyen par rapport au meilleur prix (%)",
            "Pourcentage moyen payé en plus par rapport à l'offre la moins chère.",
        )

        ecarts = self._ecarts_moyens_par_enseigne()

        for enseigne, montant in ecarts.items():

            ligne = ctk.CTkFrame(
                self.contenu,
                fg_color=BLANC,
                corner_radius=8,
                border_width=1,
                border_color=BORDURE,
            )

            ligne.pack(
                fill="x",
                pady=3,
            )

            ctk.CTkLabel(
                ligne,
                text=enseigne,
                text_color=VERT_FONCE,
                anchor="w",
            ).pack(
                side="left",
                padx=14,
                pady=10,
            )

            ctk.CTkLabel(
                ligne,
                text=self._pourcentage(montant),
                text_color=ORANGE,
                font=ctk.CTkFont(
                    size=12,
                    weight="bold",
                ),
            ).pack(
                side="right",
                padx=14,
            )

        # Top 3 des gains

        self._titre_section(
            self.contenu,
            "Top 3 des gains à comparer",
        )

        tree = self._creer_tableau(
            self.contenu,
            (
                "Référence",
                "Produit",
                "Gain potentiel",
                "Gain (%)",
            ),
            4,
        )

        for produit in top:

            tree.insert(
                "",
                "end",
                values=(
                    produit.get("produit_id"),
                    produit.get("produit"),
                    self._fcfa(
                        produit.get("gain_fcfa")
                    ),
                    self._pourcentage(
                        produit.get("gain_pct_vs_min")
                    ),
                ),
            )

    # ========================================================
    # PAGE PANIER
    # ========================================================

    def page_panier(self):

        p = self._lire_json(PANIER_FILE)

        if not p:

            self._message_vide(
                "Aucune simulation disponible. Lancez l'analyse complète."
            )

            return

        totaux = p.get(
            "totaux_par_enseigne",
            {},
        )

        cartes = ctk.CTkFrame(
            self.contenu,
            fg_color="transparent",
        )

        cartes.pack(
            fill="x",
            pady=(0, 15),
        )

        for i in range(3):
            cartes.grid_columnconfigure(i, weight=1)

        for i, (enseigne, details) in enumerate(totaux.items()):

            total = details.get("total_fcfa")

            valeur = (
                self._fcfa(total)
                if total is not None
                else "Non calculable"
            )

            indisponibles = len(
                details.get(
                    "articles_indisponibles",
                    [],
                )
            )

            self._carte(
                cartes,
                enseigne,
                valeur,
                f"Articles indisponibles : {indisponibles}",
                VERT,
            ).grid(
                row=0,
                column=i,
                padx=5,
                sticky="ew",
            )

        multi = p.get(
            "panier_multi_enseignes",
            {},
        )

        resume = ctk.CTkFrame(
            self.contenu,
            fg_color=MENTHE,
            corner_radius=12,
        )

        resume.pack(
            fill="x",
            pady=(0, 12),
        )

        ctk.CTkLabel(
            resume,
            text="TOTAL DU PANIER MULTI-ENSEIGNES",
            text_color=VERT,
            font=ctk.CTkFont(
                size=10,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            padx=16,
            pady=(12, 3),
        )

        ctk.CTkLabel(
            resume,
            text=self._fcfa(
                multi.get("total_fcfa")
            ),
            text_color=VERT_FONCE,
            font=ctk.CTkFont(
                size=25,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            padx=16,
            pady=(0, 12),
        )

        self._titre_section(
            self.contenu,
            "Plan d'achat détaillé",
        )

        tree = self._creer_tableau(
            self.contenu,
            (
                "Référence",
                "Quantité",
                "Prix unitaire",
                "Enseigne",
            ),
            10,
        )

        for article in multi.get("plan_achat", []):

            tree.insert(
                "",
                "end",
                values=(
                    article.get("produit_id"),
                    article.get("quantite"),
                    self._fcfa(
                        article.get("prix_unitaire_fcfa")
                    ),
                    article.get("enseigne") or "Indisponible",
                ),
            )

    # ========================================================
    # PAGE HISTORIQUE
    # ========================================================

    def page_historique(self):

        h = self._lire_json(
            HISTORIQUE_RESULT_FILE
        )

        if not h:

            self._message_vide(
                "Aucune analyse historique disponible. Lancez l'analyse complète."
            )

            return

        info = ctk.CTkFrame(
            self.contenu,
            fg_color=MENTHE,
            corner_radius=12,
        )

        info.pack(
            fill="x",
            pady=(0, 15),
        )

        ctk.CTkLabel(
            info,
            text=f"Période étudiée : {h.get('periode', 'Non précisée')}",
            text_color=VERT_FONCE,
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            padx=16,
            pady=(12, 4),
        )

        ctk.CTkLabel(
            info,
            text=f"Période Black Friday : {h.get('semaine_black_friday', 'Non précisée')}",
            text_color=VERT_MOYEN,
            font=ctk.CTkFont(size=11),
        ).pack(
            anchor="w",
            padx=16,
            pady=(0, 12),
        )

        resultats = h.get(
            "resultats_par_enseigne",
            {},
        )

        colonnes = (
            "Enseigne",
            "Observations",
            "Prix moyen annuel",
            "Obs. Black Friday",
            "Prix moyen BF",
            "Variation BF",
        )

        tree = self._creer_tableau(
            self.contenu,
            colonnes,
            8,
        )

        for enseigne, resultat in resultats.items():

            variation = resultat.get(
                "variation_bf_vs_moyenne_pct"
            )

            tree.insert(
                "",
                "end",
                values=(
                    enseigne,
                    resultat.get("nombre_observations_annuelles"),
                    self._fcfa(
                        resultat.get("prix_moyen_annuel_fcfa")
                    ),
                    resultat.get("nombre_observations_black_friday"),
                    self._fcfa(
                        resultat.get("prix_moyen_black_friday_fcfa")
                    ),
                    self._pourcentage(variation),
                ),
            )

        if h.get("note"):

            ctk.CTkLabel(
                self.contenu,
                text=h["note"],
                text_color=VERT_MOYEN,
                wraplength=850,
                justify="left",
            ).pack(
                anchor="w",
                pady=12,
            )

    # ========================================================
    # PAGE ANOMALIES
    # ========================================================

    def page_anomalies(self):

        ctk.CTkLabel(
            self.contenu,
            text="Journal des anomalies",
            text_color=VERT_FONCE,
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 8),
        )

        texte = ctk.CTkTextbox(
            self.contenu,
            height=470,
            corner_radius=10,
            fg_color=BLANC,
            text_color=VERT_FONCE,
            border_width=1,
            border_color=BORDURE,
            font=ctk.CTkFont(
                family="Consolas",
                size=11,
            ),
        )

        texte.pack(
            fill="both",
            expand=True,
        )

        if JOURNAL_FILE.exists():

            contenu = JOURNAL_FILE.read_text(
                encoding="utf-8",
                errors="replace",
            )

            texte.insert(
                "1.0",
                contenu if contenu.strip()
                else "Aucune anomalie enregistrée.",
            )

        else:

            texte.insert(
                "1.0",
                "Le journal n'existe pas encore. Lancez l'analyse.",
            )

        texte.configure(
            state="disabled"
        )

        ctk.CTkButton(
            self.contenu,
            text="Ouvrir le dossier des journaux",
            fg_color=VERT,
            hover_color=VERT_MOYEN,
            command=lambda: self.ouvrir_dossier(LOGS_DIR),
        ).pack(
            anchor="w",
            pady=10,
        )

    # ========================================================
    # PAGE SOURCES ET FICHIERS
    # ========================================================

    def page_sources(self):

        attendus = [
            "catalogue_reference.csv",
            "marche_lagune.csv",
            "baobab_shop.json",
            "comptoir_ivoire.xlsx",
            "historique_prix.csv",
        ]

        self._titre_section(
            self.contenu,
            "Fichiers sources",
            "Les fichiers originaux sont conservés dans data/raw.",
        )

        tree = self._creer_tableau(
            self.contenu,
            ("Fichier", "État", "Taille"),
            7,
        )

        for nom in attendus:

            chemin = RAW_DIR / nom

            disponible = chemin.exists()

            etat = (
                "Disponible"
                if disponible
                else "Manquant"
            )

            taille = (
                f"{chemin.stat().st_size:,} octets".replace(",", " ")
                if disponible
                else "—"
            )

            tree.insert(
                "",
                "end",
                values=(nom, etat, taille),
            )

        self._titre_section(
            self.contenu,
            "Fichiers générés",
            "Résultats enregistrés dans data/output.",
        )

        tree_out = self._creer_tableau(
            self.contenu,
            ("Fichier", "Taille"),
            6,
        )

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        for chemin in sorted(OUTPUT_DIR.iterdir()):

            if chemin.is_file():

                tree_out.insert(
                    "",
                    "end",
                    values=(
                        chemin.name,
                        f"{chemin.stat().st_size:,} octets".replace(",", " "),
                    ),
                )

        boutons = ctk.CTkFrame(
            self.contenu,
            fg_color="transparent",
        )

        boutons.pack(
            fill="x",
            pady=12,
        )

        ctk.CTkButton(
            boutons,
            text="Ouvrir data/raw",
            fg_color=VERT,
            hover_color=VERT_MOYEN,
            command=lambda: self.ouvrir_dossier(RAW_DIR),
        ).pack(
            side="left",
            padx=(0, 8),
        )

        ctk.CTkButton(
            boutons,
            text="Ouvrir data/output",
            fg_color=ORANGE,
            hover_color=ORANGE_CLAIR,
            command=lambda: self.ouvrir_dossier(OUTPUT_DIR),
        ).pack(
            side="left",
        )

    # ========================================================
    # PAGE TESTS
    # ========================================================

    def page_tests(self):

        self._titre_section(
            self.contenu,
            "Vérification du projet",
            "Exécutez les tests unitaires sans quitter l'interface.",
        )

        self._bouton_principal(
            self.contenu,
            "Exécuter les tests unitaires",
            self.lancer_tests,
        ).pack(
            anchor="w",
            pady=(0, 12),
        )

        self.zone_tests = ctk.CTkTextbox(
            self.contenu,
            height=430,
            corner_radius=10,
            fg_color=BLANC,
            text_color=VERT_FONCE,
            border_width=1,
            border_color=BORDURE,
            font=ctk.CTkFont(
                family="Consolas",
                size=11,
            ),
        )

        self.zone_tests.pack(
            fill="both",
            expand=True,
        )

        self.zone_tests.insert(
            "1.0",
            "Les résultats des tests apparaîtront ici.",
        )

        self.zone_tests.configure(
            state="disabled"
        )

    # ========================================================
    # PAGE PERFORMANCES ET COMPLEXITE
    # ========================================================

    def page_performances(self):
        """Affiche les mesures de performance de chaque étape."""

        resultats = self.dernieres_performances or {}

        temps = resultats.get(
            "temps_execution",
            {},
        )

        memoire = resultats.get(
            "memoire_execution",
            {},
        )

        nombres = resultats.get(
            "nombre_produits_execution",
            {},
        )

        temps_total = resultats.get("temps_total")

        memoire_max = resultats.get(
            "memoire_max_etape_mo"
        )

        self._titre_section(
            self.contenu,
            "Performances et complexité",
            "Nombre de produits traités, temps d'exécution et mémoire maximale par étape.",
        )

        if not temps and not memoire and temps_total is None:

            self._message_vide(
                "Aucune mesure disponible. Lancez l'analyse complète."
            )

            return

        resume = ctk.CTkFrame(
            self.contenu,
            fg_color=BLANC,
            corner_radius=12,
            border_width=1,
            border_color=BORDURE,
        )

        resume.pack(
            fill="x",
            pady=(4, 14),
        )

        resume.grid_columnconfigure(
            (0, 1),
            weight=1,
        )

        valeur_totale = (
            f"{float(temps_total):.6f} seconde(s)"
            if isinstance(temps_total, (int, float))
            else "Non disponible"
        )

        ctk.CTkLabel(
            resume,
            text="TEMPS TOTAL DU PIPELINE",
            text_color=VERT_MOYEN,
            font=ctk.CTkFont(
                size=10,
                weight="bold",
            ),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=16,
            pady=(12, 3),
        )

        ctk.CTkLabel(
            resume,
            text=valeur_totale,
            text_color=ORANGE,
            font=ctk.CTkFont(
                size=22,
                weight="bold",
            ),
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=16,
            pady=(0, 12),
        )

        valeur_memoire = (
            f"{float(memoire_max):.6f} Mo"
            if isinstance(memoire_max, (int, float))
            else "Non disponible"
        )

        ctk.CTkLabel(
            resume,
            text="PIC MAXIMAL MESURÉ PAR ÉTAPE",
            text_color=VERT_MOYEN,
            font=ctk.CTkFont(
                size=10,
                weight="bold",
            ),
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=16,
            pady=(12, 3),
        )

        ctk.CTkLabel(
            resume,
            text=valeur_memoire,
            text_color=VERT,
            font=ctk.CTkFont(
                size=22,
                weight="bold",
            ),
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=16,
            pady=(0, 12),
        )

        self._titre_section(
            self.contenu,
            "Détail par étape",
            "Le nombre correspond aux éléments réellement transmis à chaque traitement.",
        )

        colonnes = (
            "Algorithme / étape",
            "Nombre de produits",
            "Temps d'exécution (s)",
            "Mémoire maximale (Mo)",
        )

        tree = self._creer_tableau(
            self.contenu,
            colonnes,
            12,
        )

        tree.column(
            "Algorithme / étape",
            width=210,
            minwidth=170,
        )

        tree.column(
            "Nombre de produits",
            width=150,
            minwidth=125,
            anchor="center",
        )

        tree.column(
            "Temps d'exécution (s)",
            width=170,
            minwidth=145,
            anchor="center",
        )

        tree.column(
            "Mémoire maximale (Mo)",
            width=180,
            minwidth=155,
            anchor="center",
        )

        if isinstance(temps, dict):

            for nom, duree in temps.items():

                nom_affiche = str(nom).strip()

                if nom_affiche.casefold() == "benchmark":
                    continue

                if "Ã" in nom_affiche or "Â" in nom_affiche:

                    try:
                        nom_affiche = (
                            nom_affiche.encode("latin-1")
                            .decode("utf-8")
                        )

                    except (
                        UnicodeEncodeError,
                        UnicodeDecodeError,
                    ):
                        pass

                try:

                    temps_affiche = f"{float(duree):.6f}"

                except (TypeError, ValueError):

                    temps_affiche = str(duree)

                nombre = (
                    nombres.get(nom, 0)
                    if isinstance(nombres, dict)
                    else 0
                )

                try:

                    nombre_affiche = (
                        f"{int(nombre):,}".replace(",", " ")
                    )

                except (TypeError, ValueError):

                    nombre_affiche = str(nombre)

                valeur_memoire = (
                    memoire.get(nom, 0.0)
                    if isinstance(memoire, dict)
                    else 0.0
                )

                try:

                    memoire_affichee = (
                        f"{float(valeur_memoire):.6f}"
                    )

                except (TypeError, ValueError):

                    memoire_affichee = str(valeur_memoire)

                tree.insert(
                    "",
                    "end",
                    values=(
                        nom_affiche,
                        nombre_affiche,
                        temps_affiche,
                        memoire_affichee,
                    ),
                )

        else:

            ctk.CTkLabel(
                self.contenu,
                text="Le champ temps_execution doit être un dictionnaire.",
                text_color=VERT_MOYEN,
            ).pack(
                anchor="w",
                pady=8,
            )

    # ========================================================
    # MESSAGE EN ABSENCE DE DONNEES
    # ========================================================

    def _message_vide(self, message):

        cadre = ctk.CTkFrame(
            self.contenu,
            fg_color=BLANC,
            corner_radius=12,
            border_width=1,
            border_color=BORDURE,
        )

        cadre.pack(
            fill="x",
            pady=20,
        )

        ctk.CTkLabel(
            cadre,
            text="Aucun résultat à afficher",
            text_color=VERT_FONCE,
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
        ).pack(
            padx=20,
            pady=(20, 5),
        )

        ctk.CTkLabel(
            cadre,
            text=message,
            text_color=VERT_MOYEN,
        ).pack(
            padx=20,
            pady=(0, 20),
        )

        self._bouton_principal(
            self.contenu,
            "Lancer l'analyse",
            self.lancer_analyse,
        ).pack(
            anchor="w",
        )

    # ========================================================
    # EXECUTION DE L'ANALYSE
    # ========================================================

    def lancer_analyse(self):

        confirmation = messagebox.askyesno(
            "Lancer l'analyse",
            "Exécuter le pipeline complet et actualiser les fichiers de résultats ?",
        )

        if not confirmation:
            return

        self._statut(
            "Analyse en cours..."
        )

        self._verrouiller_actions(True)

        def travail():

            try:

                from main import executer_pipeline

                resultats = executer_pipeline(
                    afficher=False
                )

                message = (
                    f"Analyse terminée : "
                    f"{len(resultats['comparatif'])} produits comparables.\n"
                    f"Victoires : "
                    f"{resultats['synthese']['victoires_enseigne']}\n"
                    f"Résultats enregistrés dans data/output."
                )

                self.after(
                    0,
                    lambda r=resultats: self._fin_analyse(
                        True,
                        message,
                        r,
                    ),
                )

            except Exception as erreur:

                self.after(
                    0,
                    lambda e=str(erreur): self._fin_analyse(
                        False,
                        e,
                    ),
                )

        threading.Thread(
            target=travail,
            daemon=True,
        ).start()

    def _fin_analyse(
        self,
        succes,
        message,
        resultats=None,
    ):

        self._verrouiller_actions(False)

        if succes and resultats is not None:

            self.dernieres_performances = resultats

        self.actualiser_page()

        if succes:

            self._statut(
                "Analyse terminée avec succès."
            )

            messagebox.showinfo(
                "Analyse terminée",
                message,
            )

        else:

            self._statut(
                "Une erreur est survenue pendant l'analyse."
            )

            messagebox.showerror(
                "Erreur d'analyse",
                message,
            )

    def _verrouiller_actions(self, verrouille):

        self.bouton_actualiser.configure(
            state="disabled" if verrouille else "normal"
        )

    # ========================================================
    # EXECUTION DES TESTS UNITAIRES
    # ========================================================

    def lancer_tests(self):

        if (
            not hasattr(self, "zone_tests")
            or not self.zone_tests.winfo_exists()
        ):

            self.afficher_page("Tests")

        self.zone_tests.configure(
            state="normal"
        )

        self.zone_tests.delete(
            "1.0",
            "end",
        )

        self.zone_tests.insert(
            "end",
            "Exécution des tests en cours...\n",
        )

        self.zone_tests.configure(
            state="disabled"
        )

        self._statut(
            "Tests unitaires en cours..."
        )

        def travail():

            commande = [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-v",
            ]

            try:

                resultat = subprocess.run(
                    commande,
                    cwd=BASE_DIR,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )

                sortie = (
                    resultat.stdout
                    + "\n"
                    + resultat.stderr
                )

                code = resultat.returncode

            except Exception as erreur:

                sortie = str(erreur)
                code = 1

            self.after(
                0,
                lambda: self._fin_tests(
                    code,
                    sortie,
                ),
            )

        threading.Thread(
            target=travail,
            daemon=True,
        ).start()

    def _fin_tests(self, code, sortie):

        self.zone_tests.configure(
            state="normal"
        )

        self.zone_tests.delete(
            "1.0",
            "end",
        )

        self.zone_tests.insert(
            "1.0",
            sortie or "Aucune sortie retournée par unittest.",
        )

        self.zone_tests.configure(
            state="disabled"
        )

        self._statut(
            "Tests terminés : "
            + ("succès." if code == 0 else "échec.")
        )

        if code == 0:

            messagebox.showinfo(
                "Tests unitaires",
                "Tous les tests unitaires sont réussis.",
            )

        else:

            messagebox.showwarning(
                "Tests unitaires",
                "Certains tests ont échoué. Consultez le détail dans l'onglet Tests.",
            )

    # ========================================================
    # OUVERTURE DES DOSSIERS
    # ========================================================

    @staticmethod
    def ouvrir_dossier(chemin: Path):

        chemin.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            if sys.platform.startswith("win"):

                os.startfile(str(chemin))

            elif sys.platform == "darwin":

                subprocess.Popen(
                    ["open", str(chemin)]
                )

            else:

                subprocess.Popen(
                    ["xdg-open", str(chemin)]
                )

        except OSError as erreur:

            messagebox.showerror(
                "Ouverture impossible",
                str(erreur),
            )


# ============================================================
# LANCEMENT DE L'INTERFACE
# ============================================================

def lancer_interface():
    """Crée et démarre l'application graphique."""

    application = ApplicationAnalyseComparative()

    application.mainloop()
