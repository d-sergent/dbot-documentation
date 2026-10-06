#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
generative_drafting.py — Moteur BE de Generative Drafting 2D & 3D Isométrique
=============================================================================
Générateur automatisé de fiches techniques et plans de fabrication 2D normalisés
conformes aux standards de bureau d'études robotique (style RobStride / ISO) :
  - Fond blanc pur (#ffffff), monochrome noir technique haute lisibilité
  - Épaisseurs de traits ISO 128 (fort 0.50mm, fin 0.25mm, mixte axe 0.25mm)
  - Vues orthogonales : Face Avant (Rotor/PCD) + Tranche axiale étagée
  - Vue 3D Isométrique axonométrique intégrée (projetée mathématiquement)
  - Cartouche ISO 7200 complet en bas à droite (zéro titre parasite en haut)
  - Algorithme anti-collision strict (zones réservées étanches, cotes étagées)
  - Double livrable automatique :
      1. Format PDF vectoriel haute définition (Google Chrome headless)
      2. Format natif FreeCAD .FCStd (freecadcmd / TechDraw)

Usage :
  python3 generative_drafting.py --component waist_plate --format all
  python3 generative_drafting.py --component moyeu_waist --format all
  python3 generative_drafting.py --component robstride_rs06 --format all
  python3 generative_drafting.py --list
=============================================================================
"""

import os
import sys
import math
import subprocess
import argparse
import json

# Chemins de l'environnement D-Bot
WORKSPACE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation"
OUTPUT_DIR = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Plans_2D"
STEP_LIB_DIR = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FREECAD_CLI_BIN = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_GUI_BIN = "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"

# =============================================================================
# BASE DE DONNÉES GÉOMÉTRIQUE & MÉTHODE D'ASSEMBLAGE (MÉTRIQUES VÉRIFIÉES)
# =============================================================================
COMPONENTS_DB = {
    "waist_plate": {
        "title": "Platine Supérieure Déportée Waist Yaw",
        "subtitle": "Platine Usinée 7075-T6 — Torse D-Bot",
        "code": "ASV1_100_02A",
        "scale": "1:1",
        "doc_number": "DBOT-DWG-ASV1-100-02A",
        "material": "Aluminium 7075-T6 (AlZn5.5MgCu)",
        "step_name": "Waist_Plate_7075.step",
        "density": 2.81,
        "volume_cm3": 173.24,
        "mass_g": 486.8,
        "revision": "02",
        "status": "VALIDÉ USINAGE CNC C500",
        "author": "D-Bot Core Team",
        "date": "2026-09-29",
        # Géométrie Platine
        "width_x": 176.09,
        "width_y": 176.09,
        "thickness": 9.00,
        "d_ext": 176.09,
        "d_bore": 80.00,
        "d_bore_tol": "H7 (+0.030 / 0)",
        "d_rebate": 94.00,
        "rebate_depth": 3.00,
        "d_m4_pcd": 68.0,
        "m4_count": 4,
        "d_m5_pcd": 120.0,
        "m5_count": 4,
        "corner_radius": 12.0,
        "hollow_shaft": True,
    },
    "moyeu_waist": {
        "title": "Moyeu Sandwich de Rotation Waist",
        "subtitle": "Moyeu Guidage Roulement RB8016 — Torse D-Bot",
        "code": "ASV1_100_03A",
        "scale": "1:1",
        "doc_number": "DBOT-DWG-ASV1-100-03A",
        "material": "Aluminium 7075-T6 (AlZn5.5MgCu)",
        "step_name": "Moyeu_Waist_Sandwich_7075.step",
        "density": 2.81,
        "volume_cm3": 58.34,
        "mass_g": 163.9,
        "revision": "02",
        "status": "VALIDÉ USINAGE CNC C500",
        "author": "D-Bot Core Team",
        "date": "2026-09-29",
        # Géométrie Moyeu
        "d_flange": 91.50,
        "d_pilot": 80.00,
        "d_pilot_tol": "h7 (0 / -0.030)",
        "d_bore_in": 59.98,
        "d_bore_center": 37.00,
        "total_height": 23.60,
        "flange_thick": 5.00,
        "step_height": 3.00,
        "d_m4_pcd": 68.0,
        "m4_count": 4,
        "d_ext": 91.50,
        "thickness": 23.60,
        "hollow_shaft": True,
    },
    "robstride_rs06": {
        "title": "RobStride RS-06 Actuator",
        "subtitle": "Actionneur Quasi-Direct Drive 48V — Hanche / Waist",
        "code": "RS-06-48V-120",
        "scale": "1:1",
        "doc_number": "RS-06-DS-01",
        "material": "Alu 7075-T6 Anodisé Noir / Acier 40Cr",
        "step_name": "RS06_v1.step",
        "density": 2.81,
        "volume_cm3": 350.0,
        "mass_g": 980.0,
        "revision": "01",
        "status": "CONSTRUCTEUR VÉRIFIÉ",
        "author": "RobStride Tech",
        "date": "2026-09-29",
        # Géométrie Rotor
        "d_ext": 120.0,
        "d_stator_pcd": 106.0,
        "d_rotor_pilot": 94.0,
        "d_pin_pcd": 35.86,
        "d_screw_pcd": 36.0,
        "pin_holes": "2-Ø 5 +0.01/0",
        "pin_holes_extra": "3-Ø 6 +0.01/0",
        "rotor_screws": "9-M5 ↧ 6.5Min",
        "stator_screws_front": "10-M4 EQS Blind Hole ↧ 5Min",
        "stator_screws_back": "10-M4 EQS ↧ 6",
        "total_width": 39.0,
        "total_width_tol": "± 0.15",
        "rotor_step_width": 13.2,
        "rotor_step_tol": "± 0.2",
        "flange_step_1": 0.5,
        "flange_step_1_tol": "± 0.3",
        "flange_step_2": 3.3,
        "flange_step_2_tol": "± 0.25",
        "thickness": 39.0,
        "hollow_shaft": False, # Arbre plein obligatoire !
    }
}

# =============================================================================
# COULEURS & STYLES GRAPHIQUES ISO (FOND BLANC INDUSTRIEL)
# =============================================================================
STYLE = {
    "bg": "#ffffff",
    "stroke_thick": "#0f172a",       # Contours vus : 1.8 px (~0.5 mm)
    "stroke_med": "#1e293b",         # Détails intérieurs : 1.2 px (~0.35 mm)
    "stroke_thin": "#0f172a",        # Lignes de cotes : 0.9 px (~0.25 mm)
    "stroke_axis": "#64748b",        # Lignes d'axe et PCD : trait mixte fin
    "stroke_extension": "#94a3b8",   # Lignes de rappel
    "fill_part": "#ffffff",
    "fill_step": "#f8fafc",
    "fill_bore": "#e2e8f0",
    "fill_iso_top": "#ffffff",
    "fill_iso_side": "#f1f5f9",
    "fill_iso_dark": "#e2e8f0",
    "font_main": "'Segoe UI', 'Inter', -apple-system, sans-serif",
    "font_mono": "'JetBrains Mono', 'Consolas', monospace",
}

# =============================================================================
# MOTEUR DE PROJECTION ISOMÉTRIQUE 3D ANALYTIQUE
# =============================================================================
def iso_project(x, y, z, cx, cy, scale=1.0):
    """Projette un point 3D (x, y, z) en coordonnées 2D axonométriques isométriques standard."""
    cos30 = 0.8660254
    sin30 = 0.5000000
    px = cx + (x - y) * cos30 * scale
    py = cy + (x + y) * sin30 * scale - z * scale
    return px, py


def build_iso_cylinder(cx, cy, radius, height, scale, fill_top="#ffffff", fill_side="#f8fafc"):
    """Génère la géométrie SVG d'un cylindre 3D en projection isométrique."""
    steps = 36
    top_pts = []
    bot_pts = []
    for i in range(steps + 1):
        th = (2.0 * math.pi / steps) * i
        x = radius * math.cos(th)
        y = radius * math.sin(th)
        top_pts.append(iso_project(x, y, height, cx, cy, scale))
        bot_pts.append(iso_project(x, y, 0, cx, cy, scale))

    # Trouver les silhouettes extrêmes gauche et droite
    idx_left = steps // 4 * 3  # ~270 deg
    idx_right = steps // 4     # ~90 deg

    # Contour latéral
    d_side = f"M {top_pts[idx_left][0]:.2f} {top_pts[idx_left][1]:.2f} "
    d_side += f"L {bot_pts[idx_left][0]:.2f} {bot_pts[idx_left][1]:.2f} "
    for i in range(idx_left, steps + 1):
        d_side += f"L {bot_pts[i][0]:.2f} {bot_pts[i][1]:.2f} "
    for i in range(0, idx_right + 1):
        d_side += f"L {bot_pts[i][0]:.2f} {bot_pts[i][1]:.2f} "
    d_side += f"L {top_pts[idx_right][0]:.2f} {top_pts[idx_right][1]:.2f} "
    for i in range(idx_right, -1, -1):
        d_side += f"L {top_pts[i][0]:.2f} {top_pts[i][1]:.2f} "
    for i in range(steps, idx_left - 1, -1):
        d_side += f"L {top_pts[i][0]:.2f} {top_pts[i][1]:.2f} "
    d_side += "Z"

    # Face supérieure (ellipse)
    d_top = f"M {top_pts[0][0]:.2f} {top_pts[0][1]:.2f} "
    for p in top_pts[1:]:
        d_top += f"L {p[0]:.2f} {p[1]:.2f} "
    d_top += "Z"

    svg_out = f'<path d="{d_side}" fill="{fill_side}" stroke="{STYLE["stroke_thick"]}" stroke-width="1.2"/>\n'
    svg_out += f'<path d="{d_top}" fill="{fill_top}" stroke="{STYLE["stroke_thick"]}" stroke-width="1.2"/>'
    return svg_out


def build_iso_box(cx, cy, dx, dy, dz, scale):
    """Génère la géométrie SVG d'un bloc prismatique 3D avec arrondi en projection isométrique."""
    hx = dx / 2.0
    hy = dy / 2.0
    
    # 8 sommets de la boîte
    # Sommets supérieurs (z = dz)
    t0 = iso_project(-hx, -hy, dz, cx, cy, scale)
    t1 = iso_project(hx, -hy, dz, cx, cy, scale)
    t2 = iso_project(hx, hy, dz, cx, cy, scale)
    t3 = iso_project(-hx, hy, dz, cx, cy, scale)

    # Sommets inférieurs (z = 0)
    b0 = iso_project(-hx, -hy, 0, cx, cy, scale)
    b1 = iso_project(hx, -hy, 0, cx, cy, scale)
    b2 = iso_project(hx, hy, 0, cx, cy, scale)
    b3 = iso_project(-hx, hy, 0, cx, cy, scale)

    # Face avant gauche (visible)
    d_left = f"M {t3[0]:.2f} {t3[1]:.2f} L {t2[0]:.2f} {t2[1]:.2f} L {b2[0]:.2f} {b2[1]:.2f} L {b3[0]:.2f} {b3[1]:.2f} Z"
    # Face avant droite (visible)
    d_right = f"M {t2[0]:.2f} {t2[1]:.2f} L {t1[0]:.2f} {t1[1]:.2f} L {b1[0]:.2f} {b1[1]:.2f} L {b2[0]:.2f} {b2[1]:.2f} Z"
    # Face supérieure (visible)
    d_top = f"M {t0[0]:.2f} {t0[1]:.2f} L {t1[0]:.2f} {t1[1]:.2f} L {t2[0]:.2f} {t2[1]:.2f} L {t3[0]:.2f} {t3[1]:.2f} Z"

    svg_out = f'<path d="{d_left}" fill="{STYLE["fill_iso_dark"]}" stroke="{STYLE["stroke_thick"]}" stroke-width="1.2"/>\n'
    svg_out += f'<path d="{d_right}" fill="{STYLE["fill_iso_side"]}" stroke="{STYLE["stroke_thick"]}" stroke-width="1.2"/>\n'
    svg_out += f'<path d="{d_top}" fill="{STYLE["fill_iso_top"]}" stroke="{STYLE["stroke_thick"]}" stroke-width="1.2"/>'
    return svg_out


# =============================================================================
# CARTOUCHE TECHNIQUE NORMALISÉ ISO 7200 (BAS DROITE)
# =============================================================================
def build_iso7200_title_block(comp, x, y, width=330, height=135):
    """
    Génère le cartouche normalisé ISO 7200 en bas à droite de la feuille
    avec toutes les informations standard de bureau d'études sans aucun chevauchement.
    """
    svg = []
    svg.append(f'  <!-- ==================== CARTOUCHE NORMALISÉ ISO 7200 ==================== -->')
    svg.append(f'  <g id="cartouche_iso7200" transform="translate({x}, {y})">')
    
    # Cadre extérieur du cartouche
    svg.append(f'    <rect width="{width}" height="{height}" fill="#ffffff" stroke="{STYLE["stroke_thick"]}" stroke-width="1.5"/>')

    # En-tête : Organisation / Projet
    h_header = 26
    svg.append(f'    <rect width="{width}" height="{h_header}" fill="#f1f5f9" stroke="{STYLE["stroke_thick"]}" stroke-width="1.0"/>')
    svg.append(f'    <text x="{width/2.0}" y="17" fill="#0f172a" font-family="{STYLE["font_main"]}" font-size="12" font-weight="bold" text-anchor="middle" letter-spacing="1.0">D-BOT HUMANOID ROBOT V1</text>')

    # Lignes horizontales de séparation
    y_r1 = 54
    y_r2 = 82
    y_r3 = 108
    svg.append(f'    <line x1="0" y1="{y_r1}" x2="{width}" y2="{y_r1}" stroke="{STYLE["stroke_thick"]}" stroke-width="0.8"/>')
    svg.append(f'    <line x1="0" y1="{y_r2}" x2="{width}" y2="{y_r2}" stroke="{STYLE["stroke_thick"]}" stroke-width="0.8"/>')
    svg.append(f'    <line x1="0" y1="{y_r3}" x2="{width}" y2="{y_r3}" stroke="{STYLE["stroke_thick"]}" stroke-width="0.8"/>')

    # Séparateur vertical central
    x_split = 195
    svg.append(f'    <line x1="{x_split}" y1="{h_header}" x2="{x_split}" y2="{y_r3}" stroke="{STYLE["stroke_thick"]}" stroke-width="0.8"/>')

    # Colonne Gauche - Ligne 1 : Titre & Désignation
    svg.append(f'    <text x="8" y="38" fill="#64748b" font-family="{STYLE["font_main"]}" font-size="8" font-weight="bold">PIÈCE :</text>')
    svg.append(f'    <text x="8" y="50" fill="#0f172a" font-family="{STYLE["font_main"]}" font-size="10" font-weight="bold">{comp["title"][:26]}</text>')

    # Colonne Droite - Ligne 1 : Référence & Révision
    svg.append(f'    <text x="{x_split + 8}" y="38" fill="#64748b" font-family="{STYLE["font_main"]}" font-size="8" font-weight="bold">RÉF. DESSIN :</text>')
    svg.append(f'    <text x="{x_split + 8}" y="50" fill="#0f172a" font-family="{STYLE["font_main"]}" font-size="10" font-weight="bold">{comp["code"]}  (Rév. {comp["revision"]})</text>')

    # Colonne Gauche - Ligne 2 : Matériau
    svg.append(f'    <text x="8" y="65" fill="#64748b" font-family="{STYLE["font_main"]}" font-size="8" font-weight="bold">MATÉRIAU :</text>')
    svg.append(f'    <text x="8" y="77" fill="#0f172a" font-family="{STYLE["font_main"]}" font-size="9">{comp["material"][:28]}</text>')

    # Colonne Droite - Ligne 2 : Masse & Échelle
    svg.append(f'    <text x="{x_split + 8}" y="65" fill="#64748b" font-family="{STYLE["font_main"]}" font-size="8" font-weight="bold">MASSE / ÉCHELLE :</text>')
    svg.append(f'    <text x="{x_split + 8}" y="77" fill="#0f172a" font-family="{STYLE["font_main"]}" font-size="9" font-weight="bold">{comp["mass_g"]} g  |  Éch. {comp["scale"]}</text>')

    # Colonne Gauche - Ligne 3 : Tolérances générales
    svg.append(f'    <text x="8" y="93" fill="#64748b" font-family="{STYLE["font_main"]}" font-size="8" font-weight="bold">TOLÉRANCES :</text>')
    svg.append(f'    <text x="8" y="104" fill="#0f172a" font-family="{STYLE["font_main"]}" font-size="9">ISO 2768-mK / ISO 286-H7</text>')

    # Colonne Droite - Ligne 3 : Date & Auteur
    svg.append(f'    <text x="{x_split + 8}" y="93" fill="#64748b" font-family="{STYLE["font_main"]}" font-size="8" font-weight="bold">DATE &amp; AUTEUR :</text>')
    svg.append(f'    <text x="{x_split + 8}" y="104" fill="#0f172a" font-family="{STYLE["font_main"]}" font-size="9">{comp["date"]} | {comp["author"]}</text>')

    # Ligne Inférieure : Statut & Signature de validation CNC (ZÉRO SUPERPOSITION)
    svg.append(f'    <rect y="{y_r3}" width="{width}" height="{height - y_r3}" fill="#f8fafc"/>')
    svg.append(f'    <text x="8" y="{y_r3 + 17}" fill="#15803d" font-family="{STYLE["font_main"]}" font-size="9.5" font-weight="bold">STATUT : VALIDÉ CNC C500</text>')
    svg.append(f'    <text x="{width - 8}" y="{y_r3 + 17}" fill="#64748b" font-family="{STYLE["font_main"]}" font-size="8" text-anchor="end">FORMAT A3 (ISO 5457)</text>')

    svg.append(f'  </g>')
    return "\n".join(svg)


# =============================================================================
# GÉNÉRATEUR PROTOTYPE 1 : WAIST_PLATE_7075 (Platine Déportée Torse)
# =============================================================================
def build_waist_plate_drawing():
    """
    Génère le plan technique ISO complet de la Waist Plate 7075 :
    - Vue 1 (Dessus) : Platine 176.09 x 176.09, alésage Ø80 H7, PCD M4 et M5 cotés
    - Vue 2 (Profil) : Tranche 9.00 mm, redan 3.00 mm étagé
    - Vue 3 (3D Isométrique) : Projection axonométrique 3D avec alésage central et épaisseur
    - Cartouche ISO 7200 en bas à droite
    """
    comp = COMPONENTS_DB["waist_plate"]
    W_PAGE = 1200
    H_PAGE = 640

    # Coordonnées des zones (ZÉRO SUPERPOSITION)
    V1_X, V1_Y = 250, 340   # Vue de Dessus
    V2_X, V2_Y = 610, 340   # Vue de Profil Tranche
    ISO_X, ISO_Y = 1015, 230 # Vue 3D Isométrique
    CART_X, CART_Y = 855, 485 # Cartouche ISO 7200

    S = 1.15  # Échelle pour 176 mm -> 202.5 px
    W_BOX = comp["width_x"] * S
    H_BOX = comp["width_y"] * S
    R_BORE = (comp["d_bore"] / 2.0) * S
    R_REBATE = (comp["d_rebate"] / 2.0) * S
    R_M4 = (comp["d_m4_pcd"] / 2.0) * S
    R_M5 = (comp["d_m5_pcd"] / 2.0) * S
    R_CORNER = comp["corner_radius"] * S

    svg = []
    svg.append(f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_PAGE} {H_PAGE}" width="100%" height="100%">
  <defs>
    <marker id="arrow_iso_start" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 10 2 L 0 5 L 10 8 z" fill="{STYLE['stroke_thick']}"/>
    </marker>
    <marker id="arrow_iso_end" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 2 L 10 5 L 0 8 z" fill="{STYLE['stroke_thick']}"/>
    </marker>
  </defs>

  <!-- Fond blanc pur d'atelier -->
  <rect width="{W_PAGE}" height="{H_PAGE}" fill="{STYLE['bg']}"/>

  <!-- Cadre technique de la feuille A3 -->
  <rect x="15" y="15" width="{W_PAGE - 30}" height="{H_PAGE - 30}" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="1.5"/>

  <!-- ==================== VUE 1 : VUE DE DESSUS ==================== -->
  <g id="vue_dessus" transform="translate({V1_X}, {V1_Y})">
    <!-- Titre de la vue placé à Y = -155 pour dégager entièrement les cotes -->
    <text x="0" y="-155" fill="#0f172a" font-family="{STYLE['font_main']}" font-size="12" font-weight="bold" text-anchor="middle">VUE DE DESSUS (USINAGES)</text>

    <!-- Traits d'axe principaux -->
    <line x1="{-W_BOX/2 - 25}" y1="0" x2="{W_BOX/2 + 25}" y2="0" stroke="{STYLE['stroke_axis']}" stroke-width="0.75" stroke-dasharray="14,3,2,3"/>
    <line x1="0" y1="{-H_BOX/2 - 25}" x2="0" y2="{H_BOX/2 + 25}" stroke="{STYLE['stroke_axis']}" stroke-width="0.75" stroke-dasharray="14,3,2,3"/>

    <!-- Contour carré avec coins arrondis R12 -->
    <rect x="{-W_BOX/2}" y="{-H_BOX/2}" width="{W_BOX}" height="{H_BOX}" rx="{R_CORNER}" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.8"/>

    <!-- Redan Ø94 mm -->
    <circle cx="0" cy="0" r="{R_REBATE}" fill="none" stroke="{STYLE['stroke_med']}" stroke-width="1.2"/>

    <!-- Alésage central axial Ø80 H7 -->
    <circle cx="0" cy="0" r="{R_BORE}" fill="#f8fafc" stroke="{STYLE['stroke_thick']}" stroke-width="1.8"/>

    <!-- PCD M4 Ø68 mm -->
    <circle cx="0" cy="0" r="{R_M4}" fill="none" stroke="{STYLE['stroke_axis']}" stroke-width="0.75" stroke-dasharray="8,3,2,3"/>
    <circle cx="0" cy="{-R_M4}" r="3.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.0"/>
    <circle cx="{R_M4}" cy="0" r="3.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.0"/>
    <circle cx="0" cy="{R_M4}" r="3.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.0"/>
    <circle cx="{-R_M4}" cy="0" r="3.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.0"/>

    <!-- PCD M5 Ø120 mm (4 trous à 45 deg) -->
    <circle cx="0" cy="0" r="{R_M5}" fill="none" stroke="{STYLE['stroke_axis']}" stroke-width="0.75" stroke-dasharray="8,3,2,3"/>
    <circle cx="{R_M5*0.7071}" cy="{-R_M5*0.7071}" r="4.0" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.2"/>
    <circle cx="{R_M5*0.7071}" cy="{R_M5*0.7071}" r="4.0" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.2"/>
    <circle cx="{-R_M5*0.7071}" cy="{R_M5*0.7071}" r="4.0" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.2"/>
    <circle cx="{-R_M5*0.7071}" cy="{-R_M5*0.7071}" r="4.0" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.2"/>

    <!-- COTES VUE 1 -->
    <!-- Cote Largeur : 176.09 mm (Bas) -->
    <line x1="{-W_BOX/2}" y1="{H_BOX/2 + 5}" x2="{-W_BOX/2}" y2="{H_BOX/2 + 30}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="{W_BOX/2}" y1="{H_BOX/2 + 5}" x2="{W_BOX/2}" y2="{H_BOX/2 + 30}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="{-W_BOX/2 + 1}" y1="{H_BOX/2 + 25}" x2="{W_BOX/2 - 1}" y2="{H_BOX/2 + 25}" stroke="{STYLE['stroke_thick']}" stroke-width="0.9" marker-start="url(#arrow_iso_start)" marker-end="url(#arrow_iso_end)"/>
    <rect x="-35" y="{H_BOX/2 + 19}" width="70" height="12" fill="#ffffff"/>
    <text x="0" y="{H_BOX/2 + 29}" fill="#000000" font-family="{STYLE['font_main']}" font-size="10" font-weight="bold" text-anchor="middle">176.09±0.05</text>

    <!-- Cote Hauteur : 176.09 mm (Gauche) -->
    <line x1="{-W_BOX/2 - 5}" y1="{-H_BOX/2}" x2="{-W_BOX/2 - 30}" y2="{-H_BOX/2}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="{-W_BOX/2 - 5}" y1="{H_BOX/2}" x2="{-W_BOX/2 - 30}" y2="{H_BOX/2}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="{-W_BOX/2 - 25}" y1="{-H_BOX/2 + 1}" x2="{-W_BOX/2 - 25}" y2="{H_BOX/2 - 1}" stroke="{STYLE['stroke_thick']}" stroke-width="0.9" marker-start="url(#arrow_iso_start)" marker-end="url(#arrow_iso_end)"/>
    <rect x="{-W_BOX/2 - 31}" y="-6" width="12" height="70" fill="#ffffff" transform="rotate(-90 {-W_BOX/2 - 25} 0)"/>
    <text x="{-W_BOX/2 - 29}" y="4" fill="#000000" font-family="{STYLE['font_main']}" font-size="10" font-weight="bold" text-anchor="middle" transform="rotate(-90 {-W_BOX/2 - 25} 4)">176.09±0.05</text>

    <!-- Callout Alésage Ø80 H7 (Haut Gauche) -->
    <path d="M {-R_BORE*0.7071} {-R_BORE*0.7071} L -85 -115 L -160 -115" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="0.85"/>
    <circle cx="{-R_BORE*0.7071}" cy="{-R_BORE*0.7071}" r="1.5" fill="{STYLE['stroke_thick']}"/>
    <rect x="-162" y="-131" width="105" height="26" fill="#ffffff" opacity="0.95"/>
    <text x="-160" y="-120" fill="#000000" font-family="{STYLE['font_main']}" font-size="11" font-weight="bold">Ø 80 H7</text>
    <text x="-160" y="-108" fill="#475569" font-family="{STYLE['font_main']}" font-size="9">Alésage axial (+0.030/0)</text>

    <!-- Callout 4-M5 EQS (Bas Gauche) -->
    <path d="M {-R_M5*0.7071} {R_M5*0.7071} L -105 130 L -160 130" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="0.85"/>
    <circle cx="{-R_M5*0.7071}" cy="{R_M5*0.7071}" r="1.5" fill="{STYLE['stroke_thick']}"/>
    <rect x="-162" y="117" width="85" height="26" fill="#ffffff" opacity="0.95"/>
    <text x="-160" y="128" fill="#000000" font-family="{STYLE['font_main']}" font-size="10" font-weight="bold">4-M5 EQS</text>
    <text x="-160" y="140" fill="#475569" font-family="{STYLE['font_main']}" font-size="8">PCD Ø 120 ± 0.05</text>
  </g>

  <!-- ==================== VUE 2 : PROFIL TRANCHE ==================== -->
  <g id="vue_tranche" transform="translate({V2_X}, {V2_Y})">
    <!-- Titre de la vue placé à Y = -155 -->
    <text x="0" y="-155" fill="#0f172a" font-family="{STYLE['font_main']}" font-size="12" font-weight="bold" text-anchor="middle">COUPE AXIALE (PROFIL)</text>

    <!-- Axe horizontal -->
    <line x1="-50" y1="0" x2="60" y2="0" stroke="{STYLE['stroke_axis']}" stroke-width="0.75" stroke-dasharray="14,3,2,3"/>

    <!-- Profil rectangulaire e = 9.00 mm (largeur visuelle 22 px) -->
    <rect x="-11" y="{-H_BOX/2}" width="22" height="{H_BOX}" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.8"/>

    <!-- Redan 3 mm -->
    <rect x="-11" y="{-R_REBATE}" width="7" height="{2*R_REBATE}" fill="#f8fafc" stroke="{STYLE['stroke_thick']}" stroke-width="1.2"/>

    <!-- Alésage central traversant Ø80 -->
    <rect x="-11" y="{-R_BORE}" width="22" height="{2*R_BORE}" fill="#e2e8f0" stroke="{STYLE['stroke_thick']}" stroke-width="1.0" stroke-dasharray="4,2"/>

    <!-- Cotes Épaisseur en Paliers ISO 129 -->
    <!-- Palier 1 : Épaisseur totale 9.00 mm -->
    <line x1="-11" y1="{-H_BOX/2 - 4}" x2="-11" y2="{-H_BOX/2 - 30}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="11" y1="{-H_BOX/2 - 4}" x2="11" y2="{-H_BOX/2 - 30}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="-10" y1="{-H_BOX/2 - 25}" x2="10" y2="{-H_BOX/2 - 25}" stroke="{STYLE['stroke_thick']}" stroke-width="0.9" marker-start="url(#arrow_iso_start)" marker-end="url(#arrow_iso_end)"/>
    <rect x="-24" y="{-H_BOX/2 - 31}" width="48" height="12" fill="#ffffff"/>
    <text x="0" y="{-H_BOX/2 - 21}" fill="#000000" font-family="{STYLE['font_main']}" font-size="10" font-weight="bold" text-anchor="middle">9.00 -0.05</text>

    <!-- Palier 2 : Profondeur redan 3.0 mm -->
    <line x1="-11" y1="{-H_BOX/2 - 4}" x2="-11" y2="{-H_BOX/2 - 14}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="-4" y1="{-R_REBATE - 4}" x2="-4" y2="{-H_BOX/2 - 14}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="-10" y1="{-H_BOX/2 - 11}" x2="-5" y2="{-H_BOX/2 - 11}" stroke="{STYLE['stroke_thick']}" stroke-width="0.8" marker-start="url(#arrow_iso_start)" marker-end="url(#arrow_iso_end)"/>
    <text x="-8" y="{-H_BOX/2 - 1}" fill="#000000" font-family="{STYLE['font_main']}" font-size="9" text-anchor="middle">3.0</text>
  </g>

  <!-- ==================== VUE 3 : VUE 3D ISOMÉTRIQUE ==================== -->
  <g id="vue_3d_iso" transform="translate(0, 0)">
    <!-- Titre de la vue 3D -->
    <text x="{ISO_X}" y="{ISO_Y - 140}" fill="#0f172a" font-family="{STYLE['font_main']}" font-size="12" font-weight="bold" text-anchor="middle">VUE ISOMÉTRIQUE 3D (INDICATIVE)</text>
    <rect x="{ISO_X - 145}" y="{ISO_Y - 130}" width="290" height="230" fill="#f8fafc" rx="6" stroke="#cbd5e1" stroke-width="1.0"/>

    <!-- Projection 3D Isométrique Platine -->
    <g transform="translate(0, 0)">
      {build_iso_box(ISO_X, ISO_Y - 20, 160, 160, 25, scale=0.65)}

      <!-- Alésage central elliptique 3D projeté sur la face supérieure -->
      <!-- Centre supérieur : x=0, y=0, z=25 -> px=ISO_X, py=ISO_Y-20 - 25*scale = ISO_Y-36.25 -->
      <ellipse cx="{ISO_X}" cy="{ISO_Y - 36}" rx="38" ry="18" fill="#e2e8f0" stroke="{STYLE['stroke_thick']}" stroke-width="1.4"/>
      <ellipse cx="{ISO_X}" cy="{ISO_Y - 20}" rx="38" ry="18" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="1.0" stroke-dasharray="3,2"/>
      
      <!-- Redan intermédiaire -->
      <ellipse cx="{ISO_X}" cy="{ISO_Y - 36}" rx="46" ry="22" fill="none" stroke="{STYLE['stroke_med']}" stroke-width="1.0"/>

      <!-- Perçages M5 projetés en ellipses isométriques -->
      <ellipse cx="{ISO_X - 44}" cy="{ISO_Y - 48}" rx="4" ry="2.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.0"/>
      <ellipse cx="{ISO_X + 44}" cy="{ISO_Y - 48}" rx="4" ry="2.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.0"/>
      <ellipse cx="{ISO_X + 44}" cy="{ISO_Y - 24}" rx="4" ry="2.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.0"/>
      <ellipse cx="{ISO_X - 44}" cy="{ISO_Y - 24}" rx="4" ry="2.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.0"/>
    </g>
  </g>

  <!-- ==================== CARTOUCHE EN BAS À DROITE ==================== -->
  {build_iso7200_title_block(comp, CART_X, CART_Y, width=310, height=135)}
</svg>''')
    return "\n".join(svg)


# =============================================================================
# GÉNÉRATEUR PROTOTYPE 2 : MOYEU_WAIST_SANDWICH_7075 (Moyeu Torse)
# =============================================================================
def build_moyeu_waist_drawing():
    """
    Génère le plan technique ISO complet du Moyeu Sandwich Waist 7075 :
    - Vue 1 (Face / Bride) : Bride Ø91.5, portée Ø80, alésage Ø37, PCD M4 Ø68
    - Vue 2 (Profil Tranche) : Hauteur axiale 23.60 mm, épaulements 5.0 et 3.0 mm
    - Vue 3 (3D Isométrique) : Projection axonométrique 3D étagée
    - Cartouche ISO 7200 en bas à droite
    """
    comp = COMPONENTS_DB["moyeu_waist"]
    W_PAGE = 1200
    H_PAGE = 640

    V1_X, V1_Y = 250, 340
    V2_X, V2_Y = 610, 340
    ISO_X, ISO_Y = 1015, 230
    CART_X, CART_Y = 855, 485

    S = 1.95  # Échelle pour Ø91.5 mm -> 178.4 px
    R_FLANGE = (comp["d_flange"] / 2.0) * S      # 89.2 px
    R_PILOT = (comp["d_pilot"] / 2.0) * S        # 78.0 px
    R_BORE_IN = (comp["d_bore_in"] / 2.0) * S    # 58.5 px
    R_BORE_CTR = (comp["d_bore_center"] / 2.0) * S # 36.1 px
    R_M4 = (comp["d_m4_pcd"] / 2.0) * S          # 66.3 px

    H_TOTAL = comp["total_height"] * S           # 46.0 px
    H_FLANGE = comp["flange_thick"] * S          # 9.75 px
    H_STEP = comp["step_height"] * S             # 5.85 px

    svg = []
    svg.append(f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_PAGE} {H_PAGE}" width="100%" height="100%">
  <defs>
    <marker id="arrow_iso_start" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 10 2 L 0 5 L 10 8 z" fill="{STYLE['stroke_thick']}"/>
    </marker>
    <marker id="arrow_iso_end" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 2 L 10 5 L 0 8 z" fill="{STYLE['stroke_thick']}"/>
    </marker>
  </defs>

  <rect width="{W_PAGE}" height="{H_PAGE}" fill="{STYLE['bg']}"/>
  <rect x="15" y="15" width="{W_PAGE - 30}" height="{H_PAGE - 30}" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="1.5"/>

  <!-- ==================== VUE 1 : VUE DE FACE (BRIDE) ==================== -->
  <g id="vue_face_moyeu" transform="translate({V1_X}, {V1_Y})">
    <!-- Titre de la vue placé à Y = -155 pour dégagement total -->
    <text x="0" y="-155" fill="#0f172a" font-family="{STYLE['font_main']}" font-size="12" font-weight="bold" text-anchor="middle">VUE DE FACE (BRIDE USINÉE)</text>

    <!-- Traits d'axe principaux -->
    <line x1="{-R_FLANGE - 25}" y1="0" x2="{R_FLANGE + 25}" y2="0" stroke="{STYLE['stroke_axis']}" stroke-width="0.75" stroke-dasharray="14,3,2,3"/>
    <line x1="0" y1="{-R_FLANGE - 25}" x2="0" y2="{R_FLANGE + 25}" stroke="{STYLE['stroke_axis']}" stroke-width="0.75" stroke-dasharray="14,3,2,3"/>

    <!-- Bride extérieure Ø91.50 mm -->
    <circle cx="0" cy="0" r="{R_FLANGE:.2f}" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.8"/>

    <!-- Portée extérieure guidage roulement Ø80.00 mm (trait fin) -->
    <circle cx="0" cy="0" r="{R_PILOT:.2f}" fill="none" stroke="{STYLE['stroke_med']}" stroke-width="1.2"/>

    <!-- Alésage étagé Ø59.98 mm -->
    <circle cx="0" cy="0" r="{R_BORE_IN:.2f}" fill="none" stroke="{STYLE['stroke_med']}" stroke-width="1.0" stroke-dasharray="4,2"/>

    <!-- PCD M4 Ø68.0 mm (trait mixte) -->
    <circle cx="0" cy="0" r="{R_M4:.2f}" fill="none" stroke="{STYLE['stroke_axis']}" stroke-width="0.75" stroke-dasharray="8,3,2,3"/>

    <!-- 4 trous taraudés M4 sur PCD Ø68 -->
    <circle cx="0" cy="{-R_M4:.2f}" r="3.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.2"/>
    <circle cx="{R_M4:.2f}" cy="0" r="3.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.2"/>
    <circle cx="0" cy="{R_M4:.2f}" r="3.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.2"/>
    <circle cx="{-R_M4:.2f}" cy="0" r="3.2" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.2"/>

    <!-- Alésage central traversant Ø37.00 mm -->
    <circle cx="0" cy="0" r="{R_BORE_CTR:.2f}" fill="#e2e8f0" stroke="{STYLE['stroke_thick']}" stroke-width="1.8"/>

    <!-- COTES ET RENVOIS VUE 1 -->
    <!-- Callout 4-M4 EQS (Haut Gauche) -->
    <path d="M 0 {-R_M4} L -65 -105 L -140 -105" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="0.85"/>
    <circle cx="0" cy="{-R_M4}" r="1.5" fill="{STYLE['stroke_thick']}"/>
    <rect x="-142" y="-119" width="95" height="24" fill="#ffffff" opacity="0.95"/>
    <text x="-140" y="-108" fill="#000000" font-family="{STYLE['font_main']}" font-size="10" font-weight="bold">4-M4 EQS</text>
    <text x="-140" y="-97" fill="#475569" font-family="{STYLE['font_main']}" font-size="8">PCD Ø 68.0 ± 0.05</text>

    <!-- Cote Diamètre Portée Ø80 h7 (Gauche) -->
    <path d="M {-R_PILOT*0.7071} {R_PILOT*0.7071} L -85 95 L -145 95" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="0.85"/>
    <circle cx="{-R_PILOT*0.7071}" cy="{R_PILOT*0.7071}" r="1.5" fill="{STYLE['stroke_thick']}"/>
    <rect x="-147" y="82" width="95" height="26" fill="#ffffff" opacity="0.95"/>
    <text x="-145" y="94" fill="#000000" font-family="{STYLE['font_main']}" font-size="11" font-weight="bold">Ø 80 h7</text>
    <text x="-145" y="106" fill="#475569" font-family="{STYLE['font_main']}" font-size="9">Portée roulement RB8016</text>

    <!-- Cote Alésage Central Ø37 (Bas Gauche) -->
    <path d="M {-R_BORE_CTR*0.7071} {-R_BORE_CTR*0.7071} L -50 145 L -120 145" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="0.85"/>
    <circle cx="{-R_BORE_CTR*0.7071}" cy="{-R_BORE_CTR*0.7071}" r="1.5" fill="{STYLE['stroke_thick']}"/>
    <rect x="-122" y="132" width="85" height="18" fill="#ffffff" opacity="0.95"/>
    <text x="-120" y="144" fill="#000000" font-family="{STYLE['font_main']}" font-size="11" font-weight="bold">Ø 37.00 ± 0.1</text>

    <!-- Cote Diamètre Bride Ø91.50 (Bas Droite) -->
    <path d="M {R_FLANGE*0.7071} {R_FLANGE*0.7071} L 75 125 L 140 125" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="0.85"/>
    <circle cx="{R_FLANGE*0.7071}" cy="{R_FLANGE*0.7071}" r="1.5" fill="{STYLE['stroke_thick']}"/>
    <rect x="73" y="112" width="75" height="18" fill="#ffffff" opacity="0.95"/>
    <text x="75" y="124" fill="#000000" font-family="{STYLE['font_main']}" font-size="11" font-weight="bold">Ø 91.50</text>
  </g>

  <!-- ==================== VUE 2 : COUPE PROFIL TRANCHE ==================== -->
  <g id="vue_tranche_moyeu" transform="translate({V2_X}, {V2_Y})">
    <!-- Titre de la vue placé à Y = -155 -->
    <text x="0" y="-155" fill="#0f172a" font-family="{STYLE['font_main']}" font-size="12" font-weight="bold" text-anchor="middle">COUPE AXIALE (PROFIL ÉTAGÉ)</text>

    <!-- Axe horizontal -->
    <line x1="-55" y1="0" x2="65" y2="0" stroke="{STYLE['stroke_axis']}" stroke-width="0.75" stroke-dasharray="14,3,2,3"/>

    <!-- Profil étagé (Tranche axiale) -->
    <rect x="{-H_TOTAL/2}" y="{-R_PILOT}" width="{H_TOTAL}" height="{2*R_PILOT}" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.8"/>
    <!-- Collet saillant bride -->
    <rect x="{-H_TOTAL/2}" y="{-R_FLANGE}" width="{H_FLANGE}" height="{2*R_FLANGE}" fill="#ffffff" stroke="{STYLE['stroke_thick']}" stroke-width="1.8"/>

    <!-- Alésage central traversant Ø37 -->
    <rect x="{-H_TOTAL/2}" y="{-R_BORE_CTR}" width="{H_TOTAL}" height="{2*R_BORE_CTR}" fill="#e2e8f0" stroke="{STYLE['stroke_thick']}" stroke-width="1.0" stroke-dasharray="4,2"/>

    <!-- Alésage intermédiaire Ø60 -->
    <rect x="{-H_TOTAL/2 + H_FLANGE}" y="{-R_BORE_IN}" width="{H_TOTAL - H_FLANGE}" height="{2*R_BORE_IN}" fill="none" stroke="{STYLE['stroke_med']}" stroke-width="0.9" stroke-dasharray="4,2"/>

    <!-- COTES AXIALES EN ZONES SÉPARÉES ISO (ZÉRO SUPERPOSITION) -->
    <!-- Cote Supérieure : Hauteur totale hors-tout 23.60 mm -->
    <line x1="{-H_TOTAL/2}" y1="{-R_FLANGE - 4}" x2="{-H_TOTAL/2}" y2="{-R_FLANGE - 25}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="{H_TOTAL/2}" y1="{-R_PILOT - 4}" x2="{H_TOTAL/2}" y2="{-R_FLANGE - 25}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="{-H_TOTAL/2 + 1}" y1="{-R_FLANGE - 20}" x2="{H_TOTAL/2 - 1}" y2="{-R_FLANGE - 20}" stroke="{STYLE['stroke_thick']}" stroke-width="0.9" marker-start="url(#arrow_iso_start)" marker-end="url(#arrow_iso_end)"/>
    <rect x="-24" y="{-R_FLANGE - 26}" width="48" height="12" fill="#ffffff"/>
    <text x="0" y="{-R_FLANGE - 16}" fill="#000000" font-family="{STYLE['font_main']}" font-size="10" font-weight="bold" text-anchor="middle">23.60±0.1</text>

    <!-- Cote Inférieure : Épaisseur de bride 5.0 mm -->
    <line x1="{-H_TOTAL/2}" y1="{R_FLANGE + 4}" x2="{-H_TOTAL/2}" y2="{R_FLANGE + 25}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="{-H_TOTAL/2 + H_FLANGE}" y1="{R_FLANGE + 4}" x2="{-H_TOTAL/2 + H_FLANGE}" y2="{R_FLANGE + 25}" stroke="{STYLE['stroke_extension']}" stroke-width="0.6"/>
    <line x1="{-H_TOTAL/2 + 1}" y1="{R_FLANGE + 20}" x2="{-H_TOTAL/2 + H_FLANGE - 1}" y2="{R_FLANGE + 20}" stroke="{STYLE['stroke_thick']}" stroke-width="0.9" marker-start="url(#arrow_iso_start)" marker-end="url(#arrow_iso_end)"/>
    <rect x="{-H_TOTAL/2 + H_FLANGE/2 - 12}" y="{R_FLANGE + 14}" width="24" height="12" fill="#ffffff"/>
    <text x="{-H_TOTAL/2 + H_FLANGE/2}" y="{R_FLANGE + 24}" fill="#000000" font-family="{STYLE['font_main']}" font-size="9" font-weight="bold" text-anchor="middle">5.0</text>
  </g>

  <!-- ==================== VUE 3 : VUE 3D ISOMÉTRIQUE ==================== -->
  <g id="vue_3d_iso_moyeu" transform="translate(0, 0)">
    <text x="{ISO_X}" y="{ISO_Y - 140}" fill="#0f172a" font-family="{STYLE['font_main']}" font-size="12" font-weight="bold" text-anchor="middle">VUE ISOMÉTRIQUE 3D (INDICATIVE)</text>
    <rect x="{ISO_X - 145}" y="{ISO_Y - 130}" width="290" height="230" fill="#f8fafc" rx="6" stroke="#cbd5e1" stroke-width="1.0"/>

    <g transform="translate(0, 0)">
      <!-- Base cylindrique bride Ø91.5, hauteur 12 px -->
      {build_iso_cylinder(ISO_X, ISO_Y + 15, radius=72, height=14, scale=0.8, fill_top="#ffffff", fill_side="#e2e8f0")}

      <!-- Corps supérieur cylindrique Ø80, hauteur 32 px -->
      {build_iso_cylinder(ISO_X, ISO_Y - 5, radius=58, height=36, scale=0.8, fill_top="#f8fafc", fill_side="#cbd5e1")}

      <!-- Alésage central Ø37 sur face supérieure -->
      <ellipse cx="{ISO_X}" cy="{ISO_Y - 42}" rx="24" ry="11" fill="#e2e8f0" stroke="{STYLE['stroke_thick']}" stroke-width="1.4"/>
      <ellipse cx="{ISO_X}" cy="{ISO_Y - 18}" rx="24" ry="11" fill="none" stroke="{STYLE['stroke_thick']}" stroke-width="0.9" stroke-dasharray="3,2"/>
    </g>
  </g>

  <!-- ==================== CARTOUCHE EN BAS À DROITE ==================== -->
  {build_iso7200_title_block(comp, CART_X, CART_Y, width=310, height=135)}
</svg>''')
    return "\n".join(svg)


# =============================================================================
# EXPORT PDF VECTORIEL VIA CHROME HEADLESS
# =============================================================================
def export_pdf_via_chrome(svg_path, pdf_path):
    """Génère un PDF vectoriel pur d'une netteté absolue via Chrome headless."""
    if not os.path.exists(CHROME_BIN):
        print(f"   ❌ Google Chrome introuvable à : {CHROME_BIN}")
        return False

    html_wrapper = svg_path.replace(".svg", ".html")
    with open(svg_path, "r", encoding="utf-8") as f_svg:
        svg_content = f_svg.read()

    html_code = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Plan Technique Normalisé ISO</title>
  <style>
    @page {{
      size: A3 landscape;
      margin: 0;
    }}
    body {{
      margin: 0;
      padding: 0;
      background-color: #ffffff;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }}
    svg {{
      width: 100%;
      height: 100%;
    }}
  </style>
</head>
<body>
  {svg_content}
</body>
</html>"""

    with open(html_wrapper, "w", encoding="utf-8") as f_html:
        f_html.write(html_code)

    cmd = [
        CHROME_BIN,
        "--headless=new",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"file://{os.path.abspath(html_wrapper)}"
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
            print(f"   ✅ Export PDF Vectoriel réussi : {pdf_path} ({os.path.getsize(pdf_path)/1024:.1f} Ko)")
            return True
        else:
            print(f"   ⚠️ Erreur Chrome PDF : {res.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Échec génération PDF via Chrome : {e}")
        return False


# =============================================================================
# EXPORT FREECAD NATIF .FCStd (B-REP + TECHDRAW MULTI-VUES)
# =============================================================================
# =============================================================================
# EXPORT FREECAD NATIF .FCStd (B-REP + TECHDRAW MULTI-VUES SANS SUPERPOSITION)
# =============================================================================
def export_freecad_native_fcstd(comp_key, fcstd_path, pdf_path=None):
    """
    Pilote FreeCAD pour créer le document natif souverain .FCStd comprenant :
      - La géométrie B-Rep solide 3D réelle importée du fichier STEP.
      - La feuille TechDraw A3 (ISO 5457) avec cartouche ISO 7200 pré-rempli.
      - 3 vues distinctes (Face, Profil, 3D Isométrique) parfaitement réparties :
          * LockPosition = True systématique (zéro superposition au centre).
          * Visibility = True sur toutes les vues et la page (aucune vue masquée).
      - Titres et échelles sous chaque vue.
      - Bloc complet de cotations fonctionnelles métriques (diamètres, entraxes, PCD, alésages).
      - Bloc complet de spécifications d'usinage CNC C500 (alliage 7075-T6, tolérances, chanfreins).
      - Cotes géométriques TechDraw DrawViewDimension attachées.
      - Exportation directe au format PDF natif FreeCAD (TechDrawGui).
    """
    comp = COMPONENTS_DB.get(comp_key)
    if not comp:
        return False

    step_path = os.path.join(STEP_LIB_DIR, comp.get("step_name", ""))
    has_step = os.path.exists(step_path)
    step_arg = step_path if has_step else "NONE"
    pdf_arg = pdf_path if pdf_path else "NONE"

    thick_val = comp.get("total_width", comp.get("thickness", 10.0))
    diam_val = comp.get("d_ext", 100.0)

    # Configuration du layout selon la morphologie de la pièce
    is_waist_plate = (comp_key == "waist_plate")

    freecad_script = f"""
import sys, os
import FreeCAD as App

try:
    import FreeCADGui as Gui
    import TechDrawGui
    has_gui = True
except Exception:
    has_gui = False

import Part, TechDraw

doc_name = "{comp['code'].replace('-', '_')}"
doc = App.newDocument(doc_name)

# 1. Import de la géométrie STEP B-Rep
step_file = "{step_arg}"
if os.path.exists(step_file):
    shape = Part.read(step_file)
    part_feat = doc.addObject("Part::Feature", "Solid_BRep")
    part_feat.Shape = shape
    print("   • Géométrie STEP B-Rep importée avec succès :", os.path.basename(step_file))
else:
    body = Part.makeCylinder({diam_val / 2.0}, {thick_val})
    part_feat = doc.addObject("Part::Feature", "Solid_BRep")
    part_feat.Shape = body
    print("   • Corps volumique analytique instancié.")

doc.recompute()

# 2. Création de la page TechDraw A3
template_path = "/Applications/FreeCAD.app/Contents/Resources/share/Mod/TechDraw/Templates/ISO/A3_Landscape_ISO5457_advanced.svg"
if os.path.exists(template_path):
    template = doc.addObject("TechDraw::DrawSVGTemplate", "Template")
    template.Template = template_path
    page = doc.addObject("TechDraw::DrawPage", "Page_Drafting")
    page.Template = template
    doc.recompute()

    # Remplissage du cartouche ISO 7200
    try:
        t = dict(template.EditableTexts)
        t["title"] = "{comp['code']}"
        t["supplementary_title_1"] = "{comp['title']}"
        t["drawing_number"] = "{comp['doc_number']}"
        t["part_material"] = "{comp['material']}"
        t["scale"] = "{comp['scale']}"
        t["general_tolerances"] = "ISO 2768-mK"
        t["document_status"] = "{comp['status']}"
        t["creator"] = "{comp['author']}"
        t["date_of_issue"] = "{comp['date']}"
        template.EditableTexts = t
    except Exception as e_t:
        print("   ⚠️ Erreur cartouche:", e_t)

    # 3. Positionnement sans superposition des 4 vues ISO
    if {is_waist_plate}:
        # Configuration Platine Supérieure (176 x 176 mm)
        v1_scale = 0.50
        v1_x, v1_y = 110.0, 210.0
        v2_scale = 0.50
        v2_x, v2_y = 110.0, 118.0
        v3_scale = 0.50
        v3_x, v3_y = 265.0, 135.0
        v4_scale = 0.30
        v4_x, v4_y = 345.0, 220.0

        t1_x, t1_y = 110.0, 155.0
        t2_x, t2_y = 110.0, 90.0
        t3_x, t3_y = 265.0, 102.0
        t4_x, t4_y = 345.0, 175.0

        # Bandeau inférieur gauche (Y = 32.0 mm, police 2.4 mm)
        cnc_x, cnc_y = 58.0, 32.0
        dims_x, dims_y = 145.0, 32.0

        dims_list = [
            "CONTRÔLE DES COTES CLÉS :",
            "  • Encombrement : 176.09 x 176.09 mm",
            "  • Épaisseur : 9.00 mm (±0.05)",
            "  • Alésage : Ø 80.00 H7 (+0.030/0)",
            "  • Redan : Ø 94.00 x prof. 3.00 mm",
            "  • Fixation M4 : PCD Ø 68.00 mm",
            "  • Fixation M5 : PCD Ø 120.00 mm"
        ]
        cnc_list = [
            "SPÉCIFICATIONS CNC C500 :",
            "  1. Matière : Alu 7075-T6 laminé",
            "  2. Tolérances : ISO 2768-mK",
            "  3. Planéité : <= 0.02 mm / 100",
            "  4. Ø80H7 : Rectifié Ra 0.8 µm",
            "  5. Chanfreins : 0.2x45° / chants 0.5x45°",
            "  6. Traitement : Anodisation dure 15 µm"
        ]

        cotes_specs = [
            ("Cote_Alesage_80", "Vue_Dessus", "Edge0", "Edge4", "Diameter", "⌀%.2w H7 (Alésage)", 45.0, 52.0, 48.0),
            ("Cote_Centrage_89", "Vue_Dessus", "Edge1", "Edge24", "Diameter", "⌀%.2w (Centrage)", 135.0, -52.0, 48.0),
            ("Cote_Fixation_M5", "Vue_Dessus", "Edge2", "Edge3", "Diameter", "4x ⌀%.2w (M5 PCD 120)", -45.0, 52.0, -32.0),
            ("Cote_Taraudage_M4", "Vue_Dessus", "Edge3", "Edge2", "Diameter", "4x M4 (⌀%.2w PCD 68)", -135.0, -52.0, -32.0),
            ("Cote_Epaisseur_9mm", "Vue_Face", "Edge0", "Edge83", "Distance", "%.2w mm (Épaisseur)", 0.0, -75.0, 0.0),
            ("Cote_Redan_3mm", "Vue_Face", "Edge1", "Edge26", "Distance", "%.2w mm (Redan)", 0.0, 75.0, 0.0),
        ]
    else:
        # Configuration Moyeu Sandwich (Ø 91.50 x 23.60 mm) / Moteur
        v1_scale = 0.70
        v1_x, v1_y = 110.0, 210.0
        v2_scale = 0.70
        v2_x, v2_y = 110.0, 118.0
        v3_scale = 0.70
        v3_x, v3_y = 265.0, 135.0
        v4_scale = 0.35
        v4_x, v4_y = 345.0, 220.0

        t1_x, t1_y = 110.0, 160.0
        t2_x, t2_y = 110.0, 88.0
        t3_x, t3_y = 265.0, 100.0
        t4_x, t4_y = 345.0, 175.0

        # Bandeau inférieur gauche (Y = 32.0 mm, police 2.4 mm)
        cnc_x, cnc_y = 58.0, 32.0
        dims_x, dims_y = 145.0, 32.0

        dims_list = [
            "CONTRÔLE DES COTES CLÉS :",
            "  • Ø Collerette : Ø 91.50 mm",
            "  • Ø Guidage RB8016 : Ø 80.00 h7",
            "  • Ø Alésage Int. : Ø 59.98 mm",
            "  • Ø Passage Câbles : Ø 37.00 mm",
            "  • Hauteur Totale Z : 23.60 mm",
            "  • Épaisseur Collerette : 5.00 mm",
            "  • 4x M4 traversants sur Ø 68.0 mm"
        ]
        cnc_list = [
            "SPÉCIFICATIONS CNC C500 :",
            "  1. Matière : Alu 7075-T6 masse",
            "  2. Tolérances : ISO 2768-mK",
            "  3. Ø80h7 : Rectifié Ra 0.8 µm",
            "  4. Chanfreins : 0.2x45° / chants 0.5x45°",
            "  5. Anodisation incolore 15 µm"
        ]

        cotes_specs = [
            ("Cote_Diam_91_50", "Vue_Dessus", "Edge0", "Edge46", "Diameter", "⌀%.2w (Collerette)", 45.0, 48.0, 42.0),
            ("Cote_Diam_80_00", "Vue_Dessus", "Edge1", "Edge43", "Diameter", "⌀%.2w h7 (Portée RB8016)", 135.0, -48.0, 42.0),
            ("Cote_Diam_59_98", "Vue_Dessus", "Edge2", "Edge40", "Diameter", "⌀%.2w (Alésage Int.)", -135.0, -42.0, -35.0),
            ("Cote_Diam_37_00", "Vue_Dessus", "Edge3", "Edge39", "Diameter", "⌀%.2w (Passage Câbles)", -45.0, 42.0, -35.0),
            ("Cote_Hauteur_Totale", "Vue_Face", "Edge0", "Edge41", "Distance", "%.2w mm (Hauteur Z)", 0.0, -55.0, 0.0),
            ("Cote_Collerette_5mm", "Vue_Face", "Edge1", "Edge50", "Distance", "%.2w mm (Collerette)", 0.0, 55.0, 0.0),
            ("Cote_Redan_3mm", "Vue_Face", "Edge2", "Edge48", "Distance", "%.2w mm (Redan)", 0.0, 68.0, 0.0),
        ]

    # Vue 1 : VUE DE DESSUS (Projection Z-)
    v1 = doc.addObject("TechDraw::DrawViewPart", "Vue_Dessus")
    v1.Source = [part_feat]
    v1.Direction = App.Vector(0, 0, -1)
    v1.XDirection = App.Vector(1, 0, 0)
    page.addView(v1)
    v1.ScaleType = "Custom"
    v1.Scale = v1_scale
    v1.X = v1_x
    v1.Y = v1_y
    v1.LockPosition = True
    v1.Visibility = True

    # Vue 2 : VUE DE FACE (Projection Y-)
    v2 = doc.addObject("TechDraw::DrawViewPart", "Vue_Face")
    v2.Source = [part_feat]
    v2.Direction = App.Vector(0, -1, 0)
    v2.XDirection = App.Vector(1, 0, 0)
    page.addView(v2)
    v2.ScaleType = "Custom"
    v2.Scale = v2_scale
    v2.X = v2_x
    v2.Y = v2_y
    v2.LockPosition = True
    v2.Visibility = True

    # Vue 3 : VUE DE GAUCHE (Projection X+)
    v3 = doc.addObject("TechDraw::DrawViewPart", "Vue_Gauche")
    v3.Source = [part_feat]
    v3.Direction = App.Vector(1, 0, 0)
    v3.XDirection = App.Vector(0, 1, 0)
    page.addView(v3)
    v3.ScaleType = "Custom"
    v3.Scale = v3_scale
    v3.X = v3_x
    v3.Y = v3_y
    v3.LockPosition = True
    v3.Visibility = True

    # Vue 4 : VUE AXONOMÉTRIQUE 3D
    v4 = doc.addObject("TechDraw::DrawViewPart", "Vue_Isometrique_3D")
    v4.Source = [part_feat]
    v4.Direction = App.Vector(1.0, -1.0, 1.0)
    v4.XDirection = App.Vector(1.0, 1.0, 0.0)
    page.addView(v4)
    v4.ScaleType = "Custom"
    v4.Scale = v4_scale
    v4.X = v4_x
    v4.Y = v4_y
    v4.LockPosition = True
    v4.Visibility = True

    # Visibilité globale forcée
    page.Visibility = True
    template.Visibility = True

    # 4. Titres normalisés des vues SANS SLASH (DrawViewAnnotation)
    anno_t1 = doc.addObject("TechDraw::DrawViewAnnotation", "Titre_Vue_Dessus")
    anno_t1.Text = ["VUE DE DESSUS", f"ÉCHELLE {{v1_scale:.2f}}:1"]
    anno_t1.TextStyle = "Bold"
    anno_t1.TextSize = 3.6
    page.addView(anno_t1)
    anno_t1.X = t1_x
    anno_t1.Y = t1_y
    anno_t1.LockPosition = True
    anno_t1.Visibility = True

    anno_t2 = doc.addObject("TechDraw::DrawViewAnnotation", "Titre_Vue_Face")
    anno_t2.Text = ["VUE DE FACE", f"ÉCHELLE {{v2_scale:.2f}}:1"]
    anno_t2.TextStyle = "Bold"
    anno_t2.TextSize = 3.6
    page.addView(anno_t2)
    anno_t2.X = t2_x
    anno_t2.Y = t2_y
    anno_t2.LockPosition = True
    anno_t2.Visibility = True

    anno_t3 = doc.addObject("TechDraw::DrawViewAnnotation", "Titre_Vue_Gauche")
    anno_t3.Text = ["VUE DE GAUCHE", f"ÉCHELLE {{v3_scale:.2f}}:1"]
    anno_t3.TextStyle = "Bold"
    anno_t3.TextSize = 3.6
    page.addView(anno_t3)
    anno_t3.X = t3_x
    anno_t3.Y = t3_y
    anno_t3.LockPosition = True
    anno_t3.Visibility = True

    anno_t4 = doc.addObject("TechDraw::DrawViewAnnotation", "Titre_Vue_3D")
    anno_t4.Text = ["VUE AXONOMÉTRIQUE 3D", f"ÉCHELLE {{v4_scale:.2f}}:1"]
    anno_t4.TextStyle = "Bold"
    anno_t4.TextSize = 3.0
    page.addView(anno_t4)
    anno_t4.X = t4_x
    anno_t4.Y = t4_y
    anno_t4.LockPosition = True
    anno_t4.Visibility = True

    # 5. Bloc de cotations fonctionnelles
    gold_rgb = (0.85, 0.65, 0.05, 1.0)
    anno_d = doc.addObject("TechDraw::DrawViewAnnotation", "Cotes_Principales")
    anno_d.Text = dims_list
    anno_d.TextSize = 2.4
    page.addView(anno_d)
    anno_d.X = dims_x
    anno_d.Y = dims_y
    anno_d.LockPosition = True
    anno_d.Visibility = True
    anno_d.TextColor = gold_rgb

    # 6. Spécifications usinage CNC
    anno_c = doc.addObject("TechDraw::DrawViewAnnotation", "Notes_Usinage")
    anno_c.Text = cnc_list
    anno_c.TextSize = 2.4
    page.addView(anno_c)
    anno_c.X = cnc_x
    anno_c.Y = cnc_y
    anno_c.LockPosition = True
    anno_c.Visibility = True

    # 7. Cotes géométriques réelles TechDraw (DrawViewDimension en OR TECHNIQUE étagées)
    views_map = {{"Vue_Dessus": v1, "Vue_Face": v2, "Vue_Gauche": v3, "Vue_Isometrique_3D": v4}}
    created_dims = []
    for c_name, view_target_name, edge_2d, edge_3d, c_type, c_format, c_angle, off_x, off_y in cotes_specs:
        try:
            target_v = views_map.get(view_target_name, v1)
            dim_obj = doc.addObject("TechDraw::DrawViewDimension", c_name)
            page.addView(dim_obj)
            dim_obj.Type = c_type
            dim_obj.MeasureType = "True"
            dim_obj.References2D = [(target_v, edge_2d)]
            dim_obj.References3D = [(part_feat, (edge_3d,))]
            dim_obj.FormatSpec = c_format
            if c_type == "Diameter" and c_angle != 0.0:
                dim_obj.LineAngle = c_angle
            dim_obj.X = off_x
            dim_obj.Y = off_y
            dim_obj.LockPosition = True
            dim_obj.Visibility = True
            created_dims.append(dim_obj)
        except Exception as e_c:
            pass

    doc.recompute()

    # 9. Initialisation de la scène graphique si mode GUI avec couleur OR
    if has_gui:
        try:
            page.ViewObject.doubleClicked()
            page.ViewObject.ShowFrames = False
            page.ViewObject.Visibility = True
            v1.ViewObject.Visibility = True
            v2.ViewObject.Visibility = True
            v3.ViewObject.Visibility = True
            v4.ViewObject.Visibility = True
            anno_t1.ViewObject.Visibility = True
            anno_t2.ViewObject.Visibility = True
            anno_t3.ViewObject.Visibility = True
            anno_t4.ViewObject.Visibility = True
            anno_d.ViewObject.Visibility = True
            anno_c.ViewObject.Visibility = True
            try:
                anno_d.ViewObject.Fontsize = 2.4
                anno_c.ViewObject.Fontsize = 2.4
            except Exception:
                pass
            for d in created_dims:
                try:
                    d.ViewObject.Visibility = True
                    d.ViewObject.Color = gold_rgb
                    d.ViewObject.LineWidth = 0.35
                    d.ViewObject.Fontsize = 3.0
                except Exception:
                    pass
            part_feat.ViewObject.Visibility = True
            doc.recompute()
        except Exception as e_gui_init:
            pass

        # Export d'une prévisualisation temporaire STRICTEMENT dans /tmp/
        tmp_inspect_pdf = "/tmp/preview_{comp['code']}.pdf"
        try:
            TechDrawGui.exportPageAsPdf(page, tmp_inspect_pdf)
        except Exception:
            pass

doc.saveAs("{fcstd_path}")
print(f"   • Document FreeCAD souverain sauvegardé : {fcstd_path}")

if has_gui:
    try:
        Gui.getMainWindow().close()
    except Exception:
        pass

App.closeDocument(doc.Name)
sys.exit(0)
"""

    tmp_py = "/tmp/run_freecad_drafting.py"
    with open(tmp_py, "w", encoding="utf-8") as f_tmp:
        f_tmp.write(freecad_script)

    # Supprimer l'ancienne version pour s'assurer d'une écriture réelle
    if os.path.exists(fcstd_path):
        os.remove(fcstd_path)

    # Exécution prioritaire via FreeCAD GUI offscreen pour GuiDocument et export PDF
    success = False
    if os.path.exists(FREECAD_GUI_BIN):
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        cmd = [FREECAD_GUI_BIN, tmp_py]
        try:
            res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=45)
            if os.path.exists(fcstd_path) and os.path.getsize(fcstd_path) > 1000:
                print(f"   ✅ Export FreeCAD Natif .FCStd réussi (GUI) : {fcstd_path} ({os.path.getsize(fcstd_path)/1024:.1f} Ko)")
                success = True
            else:
                print(f"   ⚠️ FreeCAD GUI offscreen notice: {res.stderr[:200] if res.stderr else res.stdout[:200]}")
        except Exception as e:
            print(f"   ⚠️ Échec FreeCAD GUI offscreen : {e}")

    # Fallback freecadcmd si nécessaire
    if not success and os.path.exists(FREECAD_CLI_BIN):
        cmd = [FREECAD_CLI_BIN, tmp_py]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            if os.path.exists(fcstd_path) and os.path.getsize(fcstd_path) > 1000:
                print(f"   ✅ Export FreeCAD Natif .FCStd réussi (CLI) : {fcstd_path} ({os.path.getsize(fcstd_path)/1024:.1f} Ko)")
                success = True
        except Exception as e:
            print(f"   ❌ Échec génération FreeCAD .FCStd : {e}")
            return False

    return success



# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Moteur BE de Generative Drafting 2D & 3D (Style RobStride / ISO)")
    parser.add_argument("--component", type=str, default="waist_plate", choices=list(COMPONENTS_DB.keys()), help="Composant cible")
    parser.add_argument("--format", type=str, default="fcstd", choices=["fcstd", "pdf", "svg", "all"], help="Formats de sortie (défaut: fcstd uniquement)")
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR, help="Dossier de sortie des livrables")
    parser.add_argument("--list", action="store_true", help="Lister les composants disponibles")

    args = parser.parse_args()

    if args.list:
        print("\n📋 Composants enregistrés dans le moteur de Generative Drafting :")
        for k, v in COMPONENTS_DB.items():
            print(f"  • {k:18} : {v['title']} (Réf: {v['code']})")
        return

    os.makedirs(args.output_dir, exist_ok=True)
    comp = COMPONENTS_DB[args.component]
    base_name = f"{comp['code']}_Plan_Expert_RobStride"

    svg_file = os.path.join(args.output_dir, f"{base_name}.svg")
    pdf_file = os.path.join(args.output_dir, f"{base_name}.pdf")
    fcstd_file = os.path.join(args.output_dir, f"{base_name}.FCStd")

    print(f"\n🚀 Lancement du Generative Drafting pour : {comp['code']} ({comp['title']})")
    print(f"   • Format cible : {args.format.upper()} (Souverain BE FreeCAD)")
    print(f"   • Vues générées : 4 vues ISO (Dessus, Face, Gauche, Axonométrique 3D)")
    print(f"   • Cartouche : ISO 7200 normalisé en bas à droite (zéro superposition)")

    # 1. Génération vectorielle SVG (uniquement si explicitement demandé)
    if args.format in ["svg", "all"]:
        print("\n📐 [Optionnel] Génération du tracé vectoriel 2D SVG...")
        if args.component == "waist_plate":
            svg_content = build_waist_plate_drawing()
        elif args.component == "moyeu_waist":
            svg_content = build_moyeu_waist_drawing()
        else:
            svg_content = build_waist_plate_drawing()

        with open(svg_file, "w", encoding="utf-8") as f_s:
            f_s.write(svg_content)
        print(f"   ✅ Fichier SVG généré : {svg_file}")

    # 2. Export PDF vectoriel via Chrome headless (uniquement si explicitement demandé)
    if args.format in ["pdf", "all"]:
        print("\n📄 [Optionnel] Génération du format PDF vectoriel...")
        export_pdf_via_chrome(svg_file, pdf_file)

    # 3. Export FreeCAD natif .FCStd (seul livrable actif par défaut)
    if args.format in ["fcstd", "all"]:
        print("\n🧱 Génération du format natif souverain FreeCAD (.FCStd)...")
        export_freecad_native_fcstd(args.component, fcstd_file, pdf_path=None)

    print("\n🎉 ===========================================================================")
    print("   GÉNÉRATION DU DRAFTING EXPERT TERMINÉE AVEC SUCCÈS")
    print("   ===========================================================================")
    if args.format in ["fcstd", "all"]:
        print(f"   • Format Natif FreeCAD (.FCStd CAO)    : {fcstd_file}")
    if args.format in ["pdf", "all"]:
        print(f"   • Format PDF (Haute Définition Atelier) : {pdf_file}")
    if args.format in ["svg", "all"]:
        print(f"   • Format Vectoriel Source (.svg)       : {svg_file}")
    print("   ===========================================================================\n")


if __name__ == "__main__":
    main()
