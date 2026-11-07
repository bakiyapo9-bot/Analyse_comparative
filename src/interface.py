"""Interface graphique de l’application Analyse comparative."""

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
    BASE_DIR, RAW_DIR, OUTPUT_DIR, LOGS_DIR, COMPARATIF_FILE,
    SYNTHESE_FILE, PANIER_FILE, HISTORIQUE_RESULT_FILE, JOURNAL_FILE,
)


ENSEIGNES = ("Marché Lagune", "Baobab Shop", "Comptoir Ivoire")

# Palette de l'application
COULEUR_FOND = "#F4F7FB"
COULEUR_CARTE = "#FFFFFF"
COULEUR_SIDEBAR = "#14213D"
COULEUR_ACCENT = "#2563EB"
COULEUR_TEXTE = "#172033"
COULEUR_SECONDAIRE = "#64748B"
COULEUR_BORDURE = "#E2E8F0"


class ApplicationAnalyseComparative(ctk.CTk):
    """Fenêtre principale de l’application Analyse comparative."""

    def __init__(self):
        super().__init__()
        self.title("Analyse comparative")
        self.geometry("1280x800")
        self.minsize(1050, 680)
        self.configure(fg_color=COULEUR_FOND)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.page_actuelle = None
        self.nav_buttons = {}
        # Valeurs par défaut disponibles dès le premier affichage de l'accueil.
        self.nombre_produits = 0
        self.nombre_victoires = 0
        self._configurer_styles_tableaux()
        self._construire_structure()
        # Charger les indicateurs AVANT de construire la page qui les affiche.
        self.actualiser_indicateurs()
        self.afficher_page("Accueil")

    # ------------------------------------------------------------------ UI
    def _configurer_styles_tableaux(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Comparateur.Treeview", background="#FFFFFF", foreground=COULEUR_TEXTE,
            fieldbackground="#FFFFFF", rowheight=34, borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Comparateur.Treeview.Heading", background="#EEF2F7",
            foreground="#334155", relief="flat", font=("Segoe UI", 9, "bold"),
        )
        style.map("Comparateur.Treeview", background=[("selected", "#DBEAFE")],
                  foreground=[("selected", COULEUR_TEXTE)])

    def _construire_structure(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=235, corner_radius=0, fg_color=COULEUR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.pack(fill="x", padx=20, pady=(26, 28))
        ctk.CTkLabel(logo, text="Analyse comparative", text_color="#FFFFFF",
                     font=ctk.CTkFont(family="Segoe UI", size=21, weight="bold")).pack(anchor="w")

        ctk.CTkLabel(self.sidebar, text="ESPACE DE TRAVAIL", text_color="#8293AF",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=22, pady=(0, 10))
        pages = ["Accueil", "Comparatif", "Synthèse", "Panier",
                 "Historique", "Anomalies", "Sources & fichiers", "Tests"]
        for nom in pages:
            bouton = ctk.CTkButton(
                self.sidebar, text=nom, anchor="w", height=42,
                corner_radius=9, fg_color="transparent", hover_color="#243653",
                text_color="#DCE6F5", font=ctk.CTkFont(size=13),
                command=lambda n=nom: self.afficher_page(n),
            )
            bouton.pack(fill="x", padx=13, pady=3)
            self.nav_buttons[nom] = bouton

        bas = ctk.CTkFrame(self.sidebar, fg_color="#1C2D4B", corner_radius=12)
        bas.pack(side="bottom", fill="x", padx=14, pady=18)
        ctk.CTkLabel(bas, text="PROJET PYTHON", text_color="#FFFFFF",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(11, 3))
        ctk.CTkLabel(bas, text="CSV  •  JSON  •  EXCEL", text_color="#A9B8D0",
                     font=ctk.CTkFont(size=10)).pack(anchor="w", padx=12, pady=(0, 11))

        self.zone_principale = ctk.CTkFrame(self, fg_color=COULEUR_FOND, corner_radius=0)
        self.zone_principale.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.zone_principale.grid_rowconfigure(1, weight=1)
        self.zone_principale.grid_columnconfigure(0, weight=1)

        self.entete = ctk.CTkFrame(self.zone_principale, fg_color=COULEUR_CARTE,
                                   corner_radius=0, height=76)
        self.entete.grid(row=0, column=0, sticky="ew")
        self.entete.grid_columnconfigure(0, weight=1)
        self.titre_page = ctk.CTkLabel(self.entete, text="Accueil", text_color=COULEUR_TEXTE,
                                       font=ctk.CTkFont(size=22, weight="bold"))
        self.titre_page.grid(row=0, column=0, sticky="w", padx=28, pady=(15, 0))
        self.sous_titre = ctk.CTkLabel(self.entete, text="Vue générale de votre analyse commerciale",
                                       text_color=COULEUR_SECONDAIRE, font=ctk.CTkFont(size=11))
        self.sous_titre.grid(row=1, column=0, sticky="w", padx=29, pady=(2, 13))
        self.bouton_actualiser = ctk.CTkButton(self.entete, text="Actualiser", width=115,
                                              height=34, command=self.actualiser_page)
        self.bouton_actualiser.grid(row=0, column=1, rowspan=2, padx=25)

        self.contenu = ctk.CTkScrollableFrame(self.zone_principale, fg_color="transparent",
                                              corner_radius=0)
        self.contenu.grid(row=1, column=0, sticky="nsew", padx=22, pady=18)
        self.contenu.grid_columnconfigure(0, weight=1)

        self.barre_statut = ctk.CTkLabel(self.zone_principale, text="Prêt", anchor="w",
                                         text_color=COULEUR_SECONDAIRE,
                                         font=ctk.CTkFont(size=10))
        self.barre_statut.grid(row=2, column=0, sticky="ew", padx=26, pady=(0, 9))

    def _vider_contenu(self):
        for widget in self.contenu.winfo_children():
            widget.destroy()

    def _titre_section(self, parent, texte, aide=None):
        ctk.CTkLabel(parent, text=texte, text_color=COULEUR_TEXTE,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(4, 3))
        if aide:
            ctk.CTkLabel(parent, text=aide, text_color=COULEUR_SECONDAIRE,
                         font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(0, 10))

    def _carte(self, parent, titre, valeur, detail="", couleur=COULEUR_ACCENT):
        carte = ctk.CTkFrame(parent, fg_color=COULEUR_CARTE, corner_radius=13,
                             border_width=1, border_color=COULEUR_BORDURE)
        ctk.CTkLabel(carte, text=titre.upper(), text_color=COULEUR_SECONDAIRE,
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkLabel(carte, text=str(valeur), text_color=couleur,
                     font=ctk.CTkFont(size=25, weight="bold")).pack(anchor="w", padx=16)
        if detail:
            ctk.CTkLabel(carte, text=detail, text_color=COULEUR_SECONDAIRE,
                         font=ctk.CTkFont(size=10)).pack(anchor="w", padx=16, pady=(2, 13))
        else:
            ctk.CTkLabel(carte, text=" ").pack(pady=(0, 8))
        return carte

    def _bouton_principal(self, parent, texte, commande):
        return ctk.CTkButton(parent, text=texte, command=commande, height=40,
                             corner_radius=9, font=ctk.CTkFont(size=12, weight="bold"))

    def afficher_page(self, nom):
        self.page_actuelle = nom
        for n, bouton in self.nav_buttons.items():
            bouton.configure(fg_color="#2A4267" if n == nom else "transparent",
                             text_color="#FFFFFF" if n == nom else "#DCE6F5")
        self.titre_page.configure(text=nom)
        descriptions = {
            "Accueil": "Vue générale de votre analyse commerciale",
            "Comparatif": "Consultez et recherchez les meilleurs prix par produit",
            "Synthèse": "Indicateurs de performance et économies potentielles",
            "Panier": "Simulation du panier de rentrée et plan d'achat",
            "Historique": "Évolution annuelle des prix et période Black Friday",
            "Anomalies": "Contrôle qualité des données importées",
            "Sources & fichiers": "Vérification des fichiers et accès aux résultats",
            "Tests": "Contrôle automatique des modules du projet",
        }
        self.sous_titre.configure(text=descriptions.get(nom, ""))
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
        }
        pages[nom]()

    def actualiser_page(self):
        self.actualiser_indicateurs()
        self.afficher_page(self.page_actuelle or "Accueil")
        self._statut("Données actualisées.")

    # ------------------------------------------------------------- Données
    @staticmethod
    def _lire_json(chemin):
        if not chemin.exists():
            return None
        try:
            return json.loads(chemin.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def _lire_comparatif():
        if not COMPARATIF_FILE.exists():
            return []
        with open(COMPARATIF_FILE, "r", encoding="utf-8-sig", newline="") as fichier:
            return list(csv.DictReader(fichier, delimiter=";"))

    @staticmethod
    def _fcfa(valeur):
        if valeur in (None, "", "None"):
            return "—"
        try:
            return f"{float(valeur):,.0f} FCFA".replace(",", " ")
        except (TypeError, ValueError):
            return str(valeur)

    def _statut(self, message):
        self.barre_statut.configure(text=message)

    def actualiser_indicateurs(self):
        lignes = self._lire_comparatif()
        synthese = self._lire_json(SYNTHESE_FILE) or {}
        self.nombre_produits = len(lignes)
        self.nombre_victoires = sum(synthese.get("victoires_enseigne", {}).values())

    # --------------------------------------------------------------- Accueil
    def page_accueil(self):
        synthese = self._lire_json(SYNTHESE_FILE) or {}
        lignes = self._lire_comparatif()
        top = synthese.get("top_3_gains_a_comparer", [])
        nb_sources = sum((RAW_DIR / n).exists() for n in [
            "catalogue_reference.csv", "marche_lagune.csv", "baobab_shop.json",
            "comptoir_ivoire.xlsx", "historique_prix.csv"])

        bandeau = ctk.CTkFrame(self.contenu, fg_color="#E8F0FF", corner_radius=14)
        bandeau.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        bandeau.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bandeau, text="Bienvenue dans votre espace de comparaison",
                     text_color="#173B76", font=ctk.CTkFont(size=19, weight="bold")).grid(
                         row=0, column=0, sticky="w", padx=20, pady=(17, 4))
        ctk.CTkLabel(bandeau, text="Analysez les offres des trois boutiques et repérez les économies possibles.",
                     text_color="#45638F", font=ctk.CTkFont(size=11)).grid(
                         row=1, column=0, sticky="w", padx=20, pady=(0, 16))
        self._bouton_principal(bandeau, "Lancer l'analyse", self.lancer_analyse).grid(
            row=0, column=1, rowspan=2, padx=20, pady=15)

        indicateurs = ctk.CTkFrame(self.contenu, fg_color="transparent")
        indicateurs.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        for i in range(4): indicateurs.grid_columnconfigure(i, weight=1)
        cartes = [
            ("Produits comparables", len(lignes), "Produits avec au moins deux offres"),
            ("Sources disponibles", f"{nb_sources}/5", "Fichiers sources détectés"),
            ("Victoires boutique", self.nombre_victoires, "Meilleurs prix attribués"),
            ("Top économies", self._fcfa(top[0].get("gain_fcfa")) if top else "—", "Gain maximal identifié"),
        ]
        for i, (titre, valeur, detail) in enumerate(cartes):
            self._carte(indicateurs, titre, valeur, detail).grid(row=0, column=i, sticky="ew", padx=5)

        bas = ctk.CTkFrame(self.contenu, fg_color="transparent")
        bas.grid(row=2, column=0, sticky="ew")
        bas.grid_columnconfigure(0, weight=1)
        bas.grid_columnconfigure(1, weight=1)
        bloc_top = ctk.CTkFrame(bas, fg_color=COULEUR_CARTE, corner_radius=13,
                                border_width=1, border_color=COULEUR_BORDURE)
        bloc_top.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        self._titre_section(bloc_top, "Top 3 des écarts de prix", "Produits présentant les écarts les plus importants")
        for i, p in enumerate(top, 1):
            ligne = ctk.CTkFrame(bloc_top, fg_color="#F8FAFC", corner_radius=8)
            ligne.pack(fill="x", padx=13, pady=4)
            ctk.CTkLabel(ligne, text=f"{i:02d}", text_color=COULEUR_ACCENT,
                         font=ctk.CTkFont(size=13, weight="bold"), width=30).pack(side="left", padx=8, pady=9)
            ctk.CTkLabel(ligne, text=p.get("produit", p.get("produit_id", "Produit")),
                         text_color=COULEUR_TEXTE, font=ctk.CTkFont(size=11), anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(ligne, text=self._fcfa(p.get("gain_fcfa")), text_color="#15803D",
                         font=ctk.CTkFont(size=11, weight="bold")).pack(side="right", padx=10)
        if not top:
            ctk.CTkLabel(bloc_top, text="Lancez l'analyse pour afficher les résultats.",
                         text_color=COULEUR_SECONDAIRE).pack(padx=14, pady=20)

        bloc_actions = ctk.CTkFrame(bas, fg_color=COULEUR_CARTE, corner_radius=13,
                                    border_width=1, border_color=COULEUR_BORDURE)
        bloc_actions.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        self._titre_section(bloc_actions, "Accès rapide", "Ouvrez directement un espace de travail")
        for texte, page in [("Consulter le comparatif", "Comparatif"), ("Voir la synthèse", "Synthèse"),
                            ("Simuler le panier", "Panier"), ("Consulter les anomalies", "Anomalies")]:
            ctk.CTkButton(bloc_actions, text=texte, anchor="w", fg_color="#F1F5F9",
                          hover_color="#E2E8F0", text_color=COULEUR_TEXTE,
                          command=lambda p=page: self.afficher_page(p)).pack(fill="x", padx=14, pady=5)

    # ------------------------------------------------------------ Comparatif
    def _creer_tableau(self, parent, colonnes, hauteurs=14):
        cadre = ctk.CTkFrame(parent, fg_color=COULEUR_CARTE, corner_radius=10,
                             border_width=1, border_color=COULEUR_BORDURE)
        cadre.pack(fill="both", expand=True, pady=(8, 0))
        tree = ttk.Treeview(cadre, columns=colonnes, show="headings", height=hauteurs,
                            style="Comparateur.Treeview")
        for col in colonnes:
            tree.heading(col, text=col)
            tree.column(col, width=135, minwidth=85, anchor="w")
        scroll_y = ttk.Scrollbar(cadre, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(cadre, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        scroll_y.grid(row=0, column=1, sticky="ns", pady=8)
        scroll_x.grid(row=1, column=0, sticky="ew", padx=(8, 0))
        cadre.grid_rowconfigure(0, weight=1)
        cadre.grid_columnconfigure(0, weight=1)
        return tree

    def page_comparatif(self):
        lignes = self._lire_comparatif()
        barre = ctk.CTkFrame(self.contenu, fg_color="transparent")
        barre.pack(fill="x", pady=(0, 8))
        recherche = ctk.CTkEntry(barre, placeholder_text="Rechercher par nom ou référence (ex. P04)...", width=360, height=38)
        recherche.pack(side="left", padx=(0, 8))
        compteur = ctk.CTkLabel(barre, text=f"{len(lignes)} produit(s)", text_color=COULEUR_SECONDAIRE)
        compteur.pack(side="left", padx=8)
        colonnes = ("Référence", "Produit", *ENSEIGNES, "Meilleure enseigne", "Meilleur prix", "Prix moyen", "Écart")
        tree = self._creer_tableau(self.contenu, colonnes, 17)

        def remplir(*_):
            tree.delete(*tree.get_children())
            terme = recherche.get().strip().casefold()
            filtres = [r for r in lignes if terme in r.get("produit", "").casefold() or terme in r.get("produit_id", "").casefold()]
            for r in filtres:
                valeurs = [r.get("produit_id", ""), r.get("produit", "")]
                valeurs += [self._fcfa(r.get(e)).replace(" FCFA", "") for e in ENSEIGNES]
                valeurs += [r.get("meilleure_enseigne", ""), self._fcfa(r.get("meilleur_prix_fcfa")),
                            self._fcfa(r.get("prix_moyen_fcfa")), self._fcfa(r.get("ecart_max_min_fcfa"))]
                tree.insert("", "end", values=valeurs)
            compteur.configure(text=f"{len(filtres)} produit(s)")
        recherche.bind("<KeyRelease>", remplir)
        remplir()
        if not lignes:
            ctk.CTkLabel(self.contenu, text="Aucun comparatif disponible. Lancez d'abord l'analyse complète.",
                         text_color=COULEUR_SECONDAIRE).pack(anchor="w", pady=12)

    # --------------------------------------------------------------- Synthèse
    def page_synthese(self):
        s = self._lire_json(SYNTHESE_FILE)
        if not s:
            self._message_vide("Aucune synthèse disponible. Lancez l'analyse complète.")
            return
        cartes = ctk.CTkFrame(self.contenu, fg_color="transparent")
        cartes.pack(fill="x", pady=(0, 15))
        for i in range(3): cartes.grid_columnconfigure(i, weight=1)
        self._carte(cartes, "Produits comparables", s.get("nombre_produits_comparables", 0), "Produits analysés").grid(row=0, column=0, padx=5, sticky="ew")
        victoires = s.get("victoires_enseigne", {})
        gagnant = max(victoires, key=victoires.get) if victoires else "—"
        self._carte(cartes, "Enseigne en tête", gagnant, f"{victoires.get(gagnant, 0)} meilleur(s) prix", "#15803D").grid(row=0, column=1, padx=5, sticky="ew")
        top = s.get("top_3_gains_a_comparer", [])
        self._carte(cartes, "Écart maximal", self._fcfa(top[0].get("gain_fcfa")) if top else "—", "Sur le top 3").grid(row=0, column=2, padx=5, sticky="ew")

        self._titre_section(self.contenu, "Nombre de victoires par enseigne")
        for enseigne, nombre in victoires.items():
            ligne = ctk.CTkFrame(self.contenu, fg_color=COULEUR_CARTE, corner_radius=9)
            ligne.pack(fill="x", pady=4)
            ctk.CTkLabel(ligne, text=enseigne, width=190, anchor="w", text_color=COULEUR_TEXTE).pack(side="left", padx=14, pady=10)
            ctk.CTkProgressBar(ligne, width=300, progress_color=COULEUR_ACCENT).pack(side="left", padx=8)
            # La barre est renseignée après création pour éviter une division par zéro.
            barre = ligne.winfo_children()[-1]
            barre.set(nombre / max(victoires.values(), default=1))
            ctk.CTkLabel(ligne, text=str(nombre), text_color=COULEUR_TEXTE,
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", padx=16)

        self._titre_section(self.contenu, "Écart moyen au meilleur prix", "Montant moyen payé en plus par rapport au prix le plus bas")
        ecarts = s.get("ecart_moyen_fcfa_vs_prix_bas", {})
        for enseigne, montant in ecarts.items():
            ligne = ctk.CTkFrame(self.contenu, fg_color=COULEUR_CARTE, corner_radius=8)
            ligne.pack(fill="x", pady=3)
            ctk.CTkLabel(ligne, text=enseigne, text_color=COULEUR_TEXTE, anchor="w").pack(side="left", padx=14, pady=10)
            ctk.CTkLabel(ligne, text=self._fcfa(montant), text_color=COULEUR_ACCENT,
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", padx=14)

        self._titre_section(self.contenu, "Top 3 des gains à comparer")
        tree = self._creer_tableau(self.contenu, ("Référence", "Produit", "Gain potentiel", "Gain (%)"), 4)
        for p in top:
            tree.insert("", "end", values=(p.get("produit_id"), p.get("produit"), self._fcfa(p.get("gain_fcfa")), f"{p.get('gain_pct_vs_min', 0)} %"))

    # ---------------------------------------------------------------- Panier
    def page_panier(self):
        p = self._lire_json(PANIER_FILE)
        if not p:
            self._message_vide("Aucune simulation disponible. Lancez l'analyse complète.")
            return
        totaux = p.get("totaux_par_enseigne", {})
        cartes = ctk.CTkFrame(self.contenu, fg_color="transparent")
        cartes.pack(fill="x", pady=(0, 15))
        for i in range(3): cartes.grid_columnconfigure(i, weight=1)
        for i, (enseigne, details) in enumerate(totaux.items()):
            total = details.get("total_fcfa")
            valeur = self._fcfa(total) if total is not None else "Non calculable"
            indispo = len(details.get("articles_indisponibles", []))
            self._carte(cartes, enseigne, valeur, f"Articles indisponibles : {indispo}").grid(row=0, column=i, padx=5, sticky="ew")
        multi = p.get("panier_multi_enseignes", {})
        resume = ctk.CTkFrame(self.contenu, fg_color="#EAF7EF", corner_radius=12)
        resume.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(resume, text="TOTAL DU PANIER MULTI-ENSEIGNES", text_color="#166534",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=16, pady=(12, 3))
        ctk.CTkLabel(resume, text=self._fcfa(multi.get("total_fcfa")), text_color="#166534",
                     font=ctk.CTkFont(size=25, weight="bold")).pack(anchor="w", padx=16, pady=(0, 12))
        self._titre_section(self.contenu, "Plan d'achat détaillé")
        tree = self._creer_tableau(self.contenu, ("Référence", "Quantité", "Prix unitaire", "Enseigne"), 10)
        for a in multi.get("plan_achat", []):
            tree.insert("", "end", values=(a.get("produit_id"), a.get("quantite"), self._fcfa(a.get("prix_unitaire_fcfa")), a.get("enseigne") or "Indisponible"))

    # ------------------------------------------------------------- Historique
    def page_historique(self):
        h = self._lire_json(HISTORIQUE_RESULT_FILE)
        if not h:
            self._message_vide("Aucune analyse historique disponible. Lancez l'analyse complète.")
            return
        info = ctk.CTkFrame(self.contenu, fg_color="#E8F0FF", corner_radius=12)
        info.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(info, text=f"Période étudiée : {h.get('periode', 'Non précisée')}",
                     text_color="#173B76", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(info, text=f"Période Black Friday : {h.get('semaine_black_friday', 'Non précisée')}",
                     text_color="#45638F", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=16, pady=(0, 12))
        resultats = h.get("resultats_par_enseigne", {})
        colonnes = ("Enseigne", "Observations", "Prix moyen annuel", "Obs. Black Friday", "Prix moyen BF", "Variation BF")
        tree = self._creer_tableau(self.contenu, colonnes, 8)
        for enseigne, r in resultats.items():
            tree.insert("", "end", values=(enseigne, r.get("nombre_observations_annuelles"),
                self._fcfa(r.get("prix_moyen_annuel_fcfa")), r.get("nombre_observations_black_friday"),
                self._fcfa(r.get("prix_moyen_black_friday_fcfa")),
                "—" if r.get("variation_bf_vs_moyenne_pct") is None else f"{r.get('variation_bf_vs_moyenne_pct')} %"))
        if h.get("note"):
            ctk.CTkLabel(self.contenu, text=h["note"], text_color=COULEUR_SECONDAIRE,
                         wraplength=850, justify="left").pack(anchor="w", pady=12)

    # -------------------------------------------------------------- Anomalies
    def page_anomalies(self):
        ctk.CTkLabel(self.contenu, text="Journal des anomalies", text_color=COULEUR_TEXTE,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 8))
        texte = ctk.CTkTextbox(self.contenu, height=470, corner_radius=10,
                               fg_color=COULEUR_CARTE, text_color=COULEUR_TEXTE,
                               border_width=1, border_color=COULEUR_BORDURE,
                               font=ctk.CTkFont(family="Consolas", size=11))
        texte.pack(fill="both", expand=True)
        if JOURNAL_FILE.exists():
            contenu = JOURNAL_FILE.read_text(encoding="utf-8", errors="replace")
            texte.insert("1.0", contenu if contenu.strip() else "Aucune anomalie enregistrée.")
        else:
            texte.insert("1.0", "Le journal n'existe pas encore. Lancez l'analyse pour créer le journal.")
        texte.configure(state="disabled")
        ctk.CTkButton(self.contenu, text="Ouvrir le dossier des journaux", command=lambda: self.ouvrir_dossier(LOGS_DIR)).pack(anchor="w", pady=10)

    # -------------------------------------------------------- Sources/fichiers
    def page_sources(self):
        attendus = ["catalogue_reference.csv", "marche_lagune.csv", "baobab_shop.json",
                    "comptoir_ivoire.xlsx", "historique_prix.csv"]
        self._titre_section(self.contenu, "Fichiers sources", "Les fichiers originaux sont conservés dans data/raw.")
        tree = self._creer_tableau(self.contenu, ("Fichier", "État", "Taille"), 7)
        for nom in attendus:
            chemin = RAW_DIR / nom
            etat = "Disponible" if chemin.exists() else "Manquant"
            taille = f"{chemin.stat().st_size:,} octets".replace(",", " ") if chemin.exists() else "—"
            tree.insert("", "end", values=(nom, etat, taille))
        self._titre_section(self.contenu, "Fichiers générés", "Résultats enregistrés dans data/output.")
        tree_out = self._creer_tableau(self.contenu, ("Fichier", "Taille"), 6)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        for chemin in sorted(OUTPUT_DIR.iterdir()):
            if chemin.is_file():
                tree_out.insert("", "end", values=(chemin.name, f"{chemin.stat().st_size:,} octets".replace(",", " ")))
        boutons = ctk.CTkFrame(self.contenu, fg_color="transparent")
        boutons.pack(fill="x", pady=12)
        ctk.CTkButton(boutons, text="Ouvrir data/raw", command=lambda: self.ouvrir_dossier(RAW_DIR)).pack(side="left", padx=(0, 8))
        ctk.CTkButton(boutons, text="Ouvrir data/output", command=lambda: self.ouvrir_dossier(OUTPUT_DIR)).pack(side="left")

    # ------------------------------------------------------------------ Tests
    def page_tests(self):
        self._titre_section(self.contenu, "Vérification du projet", "Exécutez les tests unitaires sans quitter l'interface.")
        self._bouton_principal(self.contenu, "Exécuter les tests unitaires", self.lancer_tests).pack(anchor="w", pady=(0, 12))
        self.zone_tests = ctk.CTkTextbox(self.contenu, height=430, corner_radius=10,
                                         fg_color=COULEUR_CARTE, text_color=COULEUR_TEXTE,
                                         border_width=1, border_color=COULEUR_BORDURE,
                                         font=ctk.CTkFont(family="Consolas", size=11))
        self.zone_tests.pack(fill="both", expand=True)
        self.zone_tests.insert("1.0", "Les résultats des tests apparaîtront ici.")
        self.zone_tests.configure(state="disabled")

    def _message_vide(self, message):
        cadre = ctk.CTkFrame(self.contenu, fg_color=COULEUR_CARTE, corner_radius=12)
        cadre.pack(fill="x", pady=20)
        ctk.CTkLabel(cadre, text="Aucun résultat à afficher", text_color=COULEUR_TEXTE,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(padx=20, pady=(20, 5))
        ctk.CTkLabel(cadre, text=message, text_color=COULEUR_SECONDAIRE).pack(padx=20, pady=(0, 20))
        self._bouton_principal(self.contenu, "Lancer l'analyse", self.lancer_analyse).pack(anchor="w")

    # --------------------------------------------------------------- Actions
    def lancer_analyse(self):
        if not messagebox.askyesno("Lancer l'analyse", "Exécuter le pipeline complet et actualiser les fichiers de résultats ?"):
            return
        self._statut("Analyse en cours…")
        self._verrouiller_actions(True)

        def travail():
            try:
                from main import executer_pipeline
                resultats = executer_pipeline(afficher=False)
                message = (f"Analyse terminée : {len(resultats['comparatif'])} produits comparables.\n"
                           f"Victoires : {resultats['synthese']['victoires_enseigne']}\n"
                           f"Résultats enregistrés dans data/output.")
                self.after(0, lambda: self._fin_analyse(True, message))
            except Exception as erreur:
                self.after(0, lambda e=str(erreur): self._fin_analyse(False, e))

        threading.Thread(target=travail, daemon=True).start()

    def _fin_analyse(self, succes, message):
        self._verrouiller_actions(False)
        self.actualiser_page()
        if succes:
            self._statut("Analyse terminée avec succès.")
            messagebox.showinfo("Analyse terminée", message)
        else:
            self._statut("Une erreur est survenue pendant l'analyse.")
            messagebox.showerror("Erreur d'analyse", message)

    def _verrouiller_actions(self, verrouille):
        self.bouton_actualiser.configure(state="disabled" if verrouille else "normal")

    def lancer_tests(self):
        if not hasattr(self, "zone_tests") or not self.zone_tests.winfo_exists():
            self.afficher_page("Tests")
        self.zone_tests.configure(state="normal")
        self.zone_tests.delete("1.0", "end")
        self.zone_tests.insert("end", "Exécution des tests en cours…\n")
        self.zone_tests.configure(state="disabled")
        self._statut("Tests unitaires en cours…")

        def travail():
            commande = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
            resultat = subprocess.run(commande, cwd=BASE_DIR, capture_output=True, text=True,
                                      encoding="utf-8", errors="replace")
            sortie = resultat.stdout + "\n" + resultat.stderr
            self.after(0, lambda: self._fin_tests(resultat.returncode, sortie))

        threading.Thread(target=travail, daemon=True).start()

    def _fin_tests(self, code, sortie):
        self.zone_tests.configure(state="normal")
        self.zone_tests.delete("1.0", "end")
        self.zone_tests.insert("1.0", sortie or "Aucune sortie retournée par unittest.")
        self.zone_tests.configure(state="disabled")
        self._statut("Tests terminés : " + ("succès." if code == 0 else "échec."))
        if code == 0:
            messagebox.showinfo("Tests unitaires", "Tous les tests unitaires sont réussis.")
        else:
            messagebox.showwarning("Tests unitaires", "Certains tests ont échoué. Consultez le détail dans l'onglet Tests.")

    @staticmethod
    def ouvrir_dossier(chemin: Path):
        chemin.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(chemin))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(chemin)])
            else:
                subprocess.Popen(["xdg-open", str(chemin)])
        except OSError as erreur:
            messagebox.showerror("Ouverture impossible", str(erreur))


def lancer_interface():
    """Crée et démarre l'application graphique."""
    application = ApplicationAnalyseComparative()
    application.mainloop()
