#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
generate_expert_technical_drawing.py — Générateur SVG Expert Dessin Industriel
=============================================================================
Génère un plan technique complet au format SVG (A2 paysage) avec :
  - Vue de dessus complète avec cotations (largeur, hauteur, diametres)
  - Vue de face (tranche - profil épaisseur + redan)
  - Vue de droite (profil vertical)
  - Vue isométrique 3D avec ombrage
  - Cartouche ISO 7200 professionnel
  - Traits d'axe de symétrie (trait mixte ISO)
  - Lignes de cote avec flèches normalisées
  - Spécifications CNC C500

Usage :
  python3 generate_expert_technical_drawing.py --component waist_plate
  python3 generate_expert_technical_drawing.py --component all

Ce script fonctionne SANS FreeCAD - il utilise les données métriques
validées de l'AUDIT_METROLOGIQUE_Torse_et_Bassin.json.
=============================================================================
"""

import os
import sys
import math
import argparse

# =============================================================================
# BASE DE DONNÉES MÉTRIQUES VALIDÉES
# =============================================================================
COMPONENTS_DB = {
    "waist_plate": {
        "name": "Waist_Plate_7075",
        "designation": "Platine Supérieure Déportée Waist Yaw",
        "part_number": "ASV1_100_02A",
        "material": "Aluminium 7075-T6",
        "density": 2.81,
        "W": 176.09,
        "H": 176.09,
        "T": 9.00,
        "redan_depth": 3.0,
        "redan_diam": 94.0,
        "alesage_axial_diam": 80.00,
        "centrage_diam": 89.62,
        "m4_count": 4,
        "m4_pcd": 68.0,
        "m4_tap_diam": 3.30,
        "m5_count": 4,
        "m5_pcd": 120.0,
        "m5_drill_diam": 5.10,
        "corner_radius": 12.0,
        "volume_cm3": 173.25,
        "mass_g": 486.8,
        "tolerance_general": "ISO 2768-mK",
        "tolerance_alesage": "H7",
        "status": "VALIDE POUR FRAISAGE CNC C500",
        "revision": "02",
        "date": "2026-09-28",
        "author": "D-Bot Core Team",
        "scale": "1:1",
    }
}

C = {
    "bg":           "#0f172a",
    "panel":        "#1e293b",
    "panel_dark":   "#0b1329",
    "grid_line":    "#263357",
    "border":       "#38bdf8",
    "geom":         "#38bdf8",
    "geom_hidden":  "#1d4ed8",
    "axis":         "#64748b",
    "dim_line":     "#facc15",
    "dim_text":     "#facc15",
    "dim_diam":     "#fb923c",
    "annotation":   "#38bdf8",
    "callout_m4":   "#facc15",
    "callout_m5":   "#4ade80",
    "text_main":    "#f8fafc",
    "text_sec":     "#94a3b8",
    "text_label":   "#e2e8f0",
    "accent_green": "#4ade80",
    "header_blue":  "#0284c7",
    "hatch":        "#334155",
}

FONT_MONO = "'JetBrains Mono', 'Courier New', monospace"
FONT_SANS = "'Segoe UI', 'Inter', system-ui, sans-serif"
FONT_TITLE = "'Segoe UI', 'Inter', system-ui, sans-serif"


def arrow_marker_defs():
    return f"""
  <defs>
    <pattern id="bg_grid_sm" width="10" height="10" patternUnits="userSpaceOnUse">
      <path d="M 10 0 L 0 0 0 10" fill="none" stroke="{C['grid_line']}" stroke-width="0.4" opacity="0.5"/>
    </pattern>
    <pattern id="bg_grid_lg" width="50" height="50" patternUnits="userSpaceOnUse">
      <rect width="50" height="50" fill="url(#bg_grid_sm)"/>
      <path d="M 50 0 L 0 0 0 50" fill="none" stroke="{C['grid_line']}" stroke-width="0.8" opacity="0.35"/>
    </pattern>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">
      <path d="M 0 1 L 9 5 L 0 9 z" fill="{C['dim_line']}"/>
    </marker>
    <marker id="arr_r" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 10 1 L 1 5 L 10 9 z" fill="{C['dim_line']}"/>
    </marker>
    <marker id="arr_o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">
      <path d="M 0 1 L 9 5 L 0 9 z" fill="{C['dim_diam']}"/>
    </marker>
    <marker id="arr_ro" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 10 1 L 1 5 L 10 9 z" fill="{C['dim_diam']}"/>
    </marker>
    <filter id="shadow_panel">
      <feDropShadow dx="2" dy="3" stdDeviation="5" flood-color="#000" flood-opacity="0.5"/>
    </filter>
  </defs>"""


def dim_h(x1, x2, y_ref, offset, label):
    """Ligne de cote horizontale."""
    yext = y_ref + offset
    xm = (x1 + x2) / 2
    lw = max(len(label) * 6.8 + 12, 68)
    return f"""
    <line x1="{x1:.1f}" y1="{y_ref:.1f}" x2="{x1:.1f}" y2="{yext+5:.1f}" stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="3,2"/>
    <line x1="{x2:.1f}" y1="{y_ref:.1f}" x2="{x2:.1f}" y2="{yext+5:.1f}" stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="3,2"/>
    <line x1="{x1+3:.1f}" y1="{yext:.1f}" x2="{x2-3:.1f}" y2="{yext:.1f}" stroke="{C['dim_line']}" stroke-width="1.3"
          marker-end="url(#arr)" marker-start="url(#arr_r)"/>
    <rect x="{xm - lw/2:.1f}" y="{yext - 9:.1f}" width="{lw:.0f}" height="16" fill="{C['panel_dark']}" rx="3"/>
    <text x="{xm:.1f}" y="{yext + 3.5:.1f}" fill="{C['dim_text']}" font-family="{FONT_MONO}"
          font-size="10" font-weight="bold" text-anchor="middle">{label}</text>"""


def dim_v(x_ref, y1, y2, offset, label):
    """Ligne de cote verticale."""
    xext = x_ref + offset
    ym = (y1 + y2) / 2
    lw = max(len(label) * 6.8 + 12, 68)
    return f"""
    <line x1="{x_ref:.1f}" y1="{y1:.1f}" x2="{xext+5:.1f}" y2="{y1:.1f}" stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="3,2"/>
    <line x1="{x_ref:.1f}" y1="{y2:.1f}" x2="{xext+5:.1f}" y2="{y2:.1f}" stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="3,2"/>
    <line x1="{xext:.1f}" y1="{y1+3:.1f}" x2="{xext:.1f}" y2="{y2-3:.1f}" stroke="{C['dim_line']}" stroke-width="1.3"
          marker-end="url(#arr)" marker-start="url(#arr_r)"/>
    <rect x="{xext - 8:.1f}" y="{ym - lw/2:.1f}" width="16" height="{lw:.0f}" fill="{C['panel_dark']}" rx="3"
          transform="rotate(-90 {xext:.1f} {ym:.1f})"/>
    <text x="{xext:.1f}" y="{ym + 3.5:.1f}" fill="{C['dim_text']}" font-family="{FONT_MONO}"
          font-size="10" font-weight="bold" text-anchor="middle"
          transform="rotate(-90 {xext:.1f} {ym:.1f})">{label}</text>"""


def dim_diam(cx, cy, r, angle_deg, label):
    """Cote diamètre avec flèche depuis le centre."""
    a = math.radians(angle_deg)
    r_ext = r + 22
    r_lbl = r + 55
    lw = max(len(label) * 6.5, 80)
    return f"""
    <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx + r_ext*math.cos(a):.1f}" y2="{cy + r_ext*math.sin(a):.1f}"
          stroke="{C['dim_diam']}" stroke-width="1.1" marker-end="url(#arr_o)" marker-start="url(#arr_ro)"/>
    <rect x="{cx + r_lbl*math.cos(a) - lw/2:.1f}" y="{cy + r_lbl*math.sin(a) - 9:.1f}"
          width="{lw:.0f}" height="16" fill="{C['panel_dark']}" rx="3"/>
    <text x="{cx + r_lbl*math.cos(a):.1f}" y="{cy + r_lbl*math.sin(a) + 3.5:.1f}"
          fill="{C['dim_diam']}" font-family="{FONT_MONO}" font-size="10" font-weight="bold"
          text-anchor="middle">{label}</text>"""


def axis_cross(cx, cy, rx, ry):
    return f"""
    <line x1="{cx - rx:.1f}" y1="{cy:.1f}" x2="{cx + rx:.1f}" y2="{cy:.1f}"
          stroke="{C['axis']}" stroke-width="0.8" stroke-dasharray="12,3,2,3" opacity="0.85"/>
    <line x1="{cx:.1f}" y1="{cy - ry:.1f}" x2="{cx:.1f}" y2="{cy + ry:.1f}"
          stroke="{C['axis']}" stroke-width="0.8" stroke-dasharray="12,3,2,3" opacity="0.85"/>"""


def callout(px, py, bx, by, title, lines, color):
    bw = 200
    LINE_H = 15
    TITLE_H = 18
    PADDING = 6
    bh = PADDING + TITLE_H + len(lines) * LINE_H + PADDING
    rows = "\n".join(
        f'    <text x="{bx+10:.0f}" y="{by + PADDING + TITLE_H + (i+1)*LINE_H - 2:.0f}" fill="{C["text_sec"]}" '
        f'font-family="{FONT_SANS}" font-size="9">{ln}</text>'
        for i, ln in enumerate(lines)
    )
    mx = (px + bx + bw / 2) / 2
    title_y = by + PADDING + TITLE_H - 4
    return f"""
    <circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color}" opacity="0.9"/>
    <polyline points="{px:.1f},{py:.1f} {mx:.1f},{py:.1f} {bx:.1f},{by + bh/2:.1f}"
              fill="none" stroke="{color}" stroke-width="1.0" opacity="0.8"/>
    <rect x="{bx:.0f}" y="{by:.0f}" width="{bw}" height="{bh:.0f}" rx="4"
          fill="{C['panel_dark']}" fill-opacity="0.95" stroke="{color}" stroke-width="1"/>
    <text x="{bx+10:.0f}" y="{title_y:.0f}" fill="{color}" font-family="{FONT_SANS}"
          font-size="9.5" font-weight="bold">{title}</text>
    {rows}"""


def draw_view_top(comp, ox, oy, sc):
    W, H = comp["W"] * sc, comp["H"] * sc
    cr = comp["corner_radius"] * sc
    cx, cy = ox + W / 2, oy + H / 2
    D80r = comp["alesage_axial_diam"] * sc / 2
    D89r = comp["centrage_diam"] * sc / 2
    D94r = comp["redan_diam"] * sc / 2
    m4r_s = comp["m4_pcd"] * sc / 2
    m4d = comp["m4_tap_diam"] * sc / 2
    m5r_s = comp["m5_pcd"] * sc / 2
    m5d = comp["m5_drill_diam"] * sc / 2

    svg = f"""
  <!-- VUE DE DESSUS -->
  <rect x="{ox:.1f}" y="{oy:.1f}" width="{W:.1f}" height="{H:.1f}" rx="{cr:.1f}"
        fill="none" stroke="{C['geom']}" stroke-width="2.0"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{D94r:.1f}"
          fill="none" stroke="{C['geom_hidden']}" stroke-width="1.0" stroke-dasharray="8,3"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{D89r:.1f}"
          fill="none" stroke="{C['border']}" stroke-width="1.1" stroke-dasharray="10,3,2,3" opacity="0.75"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{D80r:.1f}"
          fill="{C['panel_dark']}" fill-opacity="0.45" stroke="{C['geom']}" stroke-width="2.0"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{m4r_s:.1f}"
          fill="none" stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="8,3,2,3" opacity="0.65"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{m5r_s:.1f}"
          fill="none" stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="8,3,2,3" opacity="0.65"/>"""

    for a in [45, 135, 225, 315]:
        hx = cx + m4r_s * math.cos(math.radians(a))
        hy = cy + m4r_s * math.sin(math.radians(a))
        svg += f"""
  <circle cx="{hx:.1f}" cy="{hy:.1f}" r="{m4d:.1f}"
          fill="none" stroke="{C['callout_m4']}" stroke-width="1.3"/>
  <circle cx="{hx:.1f}" cy="{hy:.1f}" r="{m4d*0.65:.1f}"
          fill="none" stroke="{C['callout_m4']}" stroke-width="0.6" stroke-dasharray="2,1"/>"""

    for a in [0, 90, 180, 270]:
        hx = cx + m5r_s * math.cos(math.radians(a))
        hy = cy + m5r_s * math.sin(math.radians(a))
        svg += f"""
  <circle cx="{hx:.1f}" cy="{hy:.1f}" r="{m5d:.1f}"
          fill="none" stroke="{C['callout_m5']}" stroke-width="1.3"/>"""

    svg += axis_cross(cx, cy, W / 2 + 20, H / 2 + 20)

    # Cotations
    svg += dim_h(ox, ox + W, oy + H, 38, f"{comp['W']:.2f} mm")
    svg += dim_v(ox + W, oy, oy + H, 38, f"{comp['H']:.2f} mm")
    svg += dim_diam(cx, cy, D80r, -30, f"Ø {comp['alesage_axial_diam']:.2f} H7")
    svg += dim_diam(cx, cy, D89r, 150, f"Ø {comp['centrage_diam']:.2f}")

    return svg, cx, cy, m4r_s, m5r_s


def draw_view_front(comp, ox, oy, sc):
    W = comp["W"] * sc
    T = comp["T"] * sc
    rd = comp["redan_depth"] * sc
    Drd = comp["redan_diam"] * sc

    svg = f"""
  <!-- VUE DE FACE -->
  <rect x="{ox:.1f}" y="{oy:.1f}" width="{W:.1f}" height="{T:.1f}"
        fill="{C['panel']}" fill-opacity="0.3" stroke="{C['geom']}" stroke-width="2.0"/>
  <rect x="{ox + (W - Drd)/2:.1f}" y="{oy + T - rd:.1f}" width="{Drd:.1f}" height="{rd:.1f}"
        fill="{C['panel_dark']}" fill-opacity="0.7" stroke="{C['geom']}" stroke-width="1.4"/>
  <line x1="{ox:.1f}" y1="{oy + T - rd:.1f}" x2="{ox + (W - Drd)/2:.1f}" y2="{oy + T - rd:.1f}"
        stroke="{C['geom_hidden']}" stroke-width="0.9" stroke-dasharray="6,3"/>
  <line x1="{ox + (W + Drd)/2:.1f}" y1="{oy + T - rd:.1f}" x2="{ox + W:.1f}" y2="{oy + T - rd:.1f}"
        stroke="{C['geom_hidden']}" stroke-width="0.9" stroke-dasharray="6,3"/>
  <line x1="{ox + W/2:.1f}" y1="{oy - 10}" x2="{ox + W/2:.1f}" y2="{oy + T + 10}"
        stroke="{C['axis']}" stroke-width="0.8" stroke-dasharray="10,3,2,3" opacity="0.8"/>"""

    # Hachures coupe redan
    rx0 = ox + (W - Drd) / 2
    ry0 = oy + T - rd
    step = 7
    n = int((Drd + rd) / step) + 3
    for i in range(n):
        sx = rx0 + i * step
        sy = ry0
        ex = sx - rd
        ey = ry0 + rd
        if ex < rx0:
            diff = rx0 - ex
            ex = rx0
            ey -= diff
        if sx > rx0 + Drd:
            diff = sx - (rx0 + Drd)
            sx = rx0 + Drd
            sy += diff
        if sy > ry0 + rd or ey < ry0:
            continue
        svg += f"""
  <line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"
        stroke="{C['hatch']}" stroke-width="0.8" opacity="0.7"/>"""

    # Cotes
    svg += dim_v(ox - 38, oy, oy + T, -38, f"{comp['T']:.2f} mm")
    # Cote reda séparément
    rx_right = ox + (W + Drd) / 2 + 8
    svg += f"""
  <line x1="{ox + (W + Drd)/2:.1f}" y1="{oy + T - rd:.1f}" x2="{rx_right + 25:.1f}" y2="{oy + T - rd:.1f}"
        stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="2,2"/>
  <line x1="{ox + (W + Drd)/2:.1f}" y1="{oy + T:.1f}" x2="{rx_right + 25:.1f}" y2="{oy + T:.1f}"
        stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="2,2"/>
  <line x1="{rx_right + 18:.1f}" y1="{oy + T - rd + 2:.1f}" x2="{rx_right + 18:.1f}" y2="{oy + T - 2:.1f}"
        stroke="{C['dim_diam']}" stroke-width="1.1" marker-end="url(#arr_o)" marker-start="url(#arr_ro)"/>
  <rect x="{rx_right + 22:.1f}" y="{oy + T - rd/2 - 9:.1f}" width="78" height="16" fill="{C['panel_dark']}" rx="3"/>
  <text x="{rx_right + 61:.1f}" y="{oy + T - rd/2 + 3:.1f}" fill="{C['dim_diam']}"
        font-family="{FONT_MONO}" font-size="10" font-weight="bold"
        text-anchor="middle">e = {comp['redan_depth']:.1f} mm</text>"""

    return svg


def draw_view_right(comp, ox, oy, sc):
    H = comp["H"] * sc
    T = comp["T"] * sc
    rd = comp["redan_depth"] * sc
    Drd = comp["redan_diam"] * sc

    svg = f"""
  <!-- VUE DE DROITE -->
  <rect x="{ox:.1f}" y="{oy:.1f}" width="{T:.1f}" height="{H:.1f}"
        fill="{C['panel']}" fill-opacity="0.3" stroke="{C['geom']}" stroke-width="2.0"/>
  <rect x="{ox:.1f}" y="{oy + (H - Drd)/2:.1f}" width="{rd:.1f}" height="{Drd:.1f}"
        fill="{C['panel_dark']}" fill-opacity="0.7" stroke="{C['geom']}" stroke-width="1.4"/>
  <line x1="{ox:.1f}" y1="{oy + (H - Drd)/2:.1f}" x2="{ox + T:.1f}" y2="{oy + (H - Drd)/2:.1f}"
        stroke="{C['geom_hidden']}" stroke-width="0.9" stroke-dasharray="6,3"/>
  <line x1="{ox:.1f}" y1="{oy + (H + Drd)/2:.1f}" x2="{ox + T:.1f}" y2="{oy + (H + Drd)/2:.1f}"
        stroke="{C['geom_hidden']}" stroke-width="0.9" stroke-dasharray="6,3"/>
  <line x1="{ox - 10}" y1="{oy + H/2:.1f}" x2="{ox + T + 10}" y2="{oy + H/2:.1f}"
        stroke="{C['axis']}" stroke-width="0.8" stroke-dasharray="10,3,2,3" opacity="0.8"/>"""

    svg += dim_h(ox, ox + T, oy + H, 38, f"{comp['T']:.2f} mm")
    # Note: H dimension not shown here (already on top view Y cote)

    return svg


def draw_view_iso(comp, cx, cy, sc_iso):
    W = comp["W"] * sc_iso
    H = comp["H"] * sc_iso
    T = comp["T"] * sc_iso
    D80r = comp["alesage_axial_diam"] * sc_iso / 2
    D89r = comp["centrage_diam"] * sc_iso / 2
    m5r_s = comp["m5_pcd"] * sc_iso / 2
    m5d = comp["m5_drill_diam"] * sc_iso / 2

    x0 = cx - W / 2
    y0 = cy - H / 2

    iso_a = math.radians(30)
    dx = T * math.cos(iso_a)
    dy = -T * math.sin(iso_a)

    svg = f"""
  <!-- VUE ISOMETRIQUE -->
  <polygon points="{x0+dx:.1f},{y0+dy:.1f} {x0+W+dx:.1f},{y0+dy:.1f} {x0+W:.1f},{y0:.1f} {x0:.1f},{y0:.1f}"
           fill="{C['panel']}" fill-opacity="0.65" stroke="{C['geom']}" stroke-width="1.5"/>
  <polygon points="{x0+W:.1f},{y0:.1f} {x0+W+dx:.1f},{y0+dy:.1f} {x0+W+dx:.1f},{y0+H+dy:.1f} {x0+W:.1f},{y0+H:.1f}"
           fill="{C['panel_dark']}" fill-opacity="0.85" stroke="{C['geom']}" stroke-width="1.5"/>
  <rect x="{x0:.1f}" y="{y0:.1f}" width="{W:.1f}" height="{H:.1f}"
        fill="{C['panel']}" fill-opacity="0.4" stroke="{C['geom']}" stroke-width="2.0" rx="{comp['corner_radius']*sc_iso:.1f}"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{D80r:.1f}"
          fill="{C['panel_dark']}" fill-opacity="0.75" stroke="{C['geom']}" stroke-width="1.8"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{D89r:.1f}"
          fill="none" stroke="{C['border']}" stroke-width="1.0" stroke-dasharray="8,3,2,3" opacity="0.7"/>
  <ellipse cx="{cx + dx/2:.1f}" cy="{y0 + dy/2:.1f}"
           rx="{D80r:.1f}" ry="{D80r * 0.28:.1f}"
           fill="{C['panel_dark']}" fill-opacity="0.5" stroke="{C['geom']}" stroke-width="1.1"/>
  <line x1="{x0:.1f}" y1="{y0+H:.1f}" x2="{x0+dx:.1f}" y2="{y0+H+dy:.1f}" stroke="{C['geom']}" stroke-width="1.5"/>
  <line x1="{x0+dx:.1f}" y1="{y0+dy:.1f}" x2="{x0+dx:.1f}" y2="{y0+H+dy:.1f}" stroke="{C['geom']}" stroke-width="1.5"/>
  <line x1="{x0+dx:.1f}" y1="{y0+H+dy:.1f}" x2="{x0+W+dx:.1f}" y2="{y0+H+dy:.1f}" stroke="{C['geom']}" stroke-width="1.5"/>"""

    for a in [0, 90, 180, 270]:
        hx = cx + m5r_s * math.cos(math.radians(a))
        hy = cy + m5r_s * math.sin(math.radians(a))
        svg += f"""
  <circle cx="{hx:.1f}" cy="{hy:.1f}" r="{m5d:.1f}"
          fill="{C['panel_dark']}" stroke="{C['callout_m5']}" stroke-width="1.1"/>"""

    # Angles trait-axe iso
    svg += f"""
  <line x1="{cx:.1f}" y1="{y0 - 10}" x2="{cx:.1f}" y2="{y0+H + 10}"
        stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="10,3,2,3" opacity="0.6"/>
  <line x1="{x0 - 10}" y1="{cy:.1f}" x2="{x0+W + 10}" y2="{cy:.1f}"
        stroke="{C['axis']}" stroke-width="0.7" stroke-dasharray="10,3,2,3" opacity="0.6"/>"""

    return svg


def draw_title_block(comp, ox, oy, W=320):
    row_h = 44
    rows = [
        ("PIECE :", comp["name"], C["text_main"], 13, "bold"),
        ("DESIGNATION :", comp["designation"], C["text_label"], 9.5, "normal"),
        ("MATERIAU :", f"{comp['material']}", C["text_main"], 10, "bold"),
        ("MASSE / EP. :", f"{comp['mass_g']:.1f} g  |  e = {comp['T']:.2f} mm", C["dim_line"], 11, "bold"),
        ("REF. / ECH. :", f"{comp['part_number']} | Ech. {comp['scale']}", C["text_label"], 10, "normal"),
        ("TOLERANCES :", comp["tolerance_general"], C["text_label"], 10, "normal"),
    ]
    total_h = 38 + len(rows) * row_h + 82

    svg = f"""
  <!-- CARTOUCHE ISO 7200 -->
  <g transform="translate({ox},{oy})">
    <rect width="{W}" height="{total_h}" rx="6" fill="{C['panel']}" stroke="{C['border']}" stroke-width="1.5" filter="url(#shadow_panel)"/>
    <rect width="{W}" height="38" rx="6" fill="{C['header_blue']}" opacity="0.25"/>
    <line x1="0" y1="38" x2="{W}" y2="38" stroke="{C['border']}" stroke-width="1"/>
    <text x="{W//2}" y="24" fill="{C['border']}" font-family="{FONT_TITLE}"
          font-size="12" font-weight="bold" text-anchor="middle" letter-spacing="1.5">D-BOT HUMANOID ROBOT V1</text>
    <line x1="110" y1="38" x2="110" y2="{38 + len(rows)*row_h}" stroke="{C['grid_line']}" stroke-width="0.8"/>"""

    y_cur = 38
    for i, (label, value, vc, fs, fw) in enumerate(rows):
        y_cur += row_h
        svg += f"""
    <line x1="0" y1="{y_cur}" x2="{W}" y2="{y_cur}" stroke="{C['grid_line']}" stroke-width="0.8"/>
    <text x="10" y="{y_cur - row_h//2 + 5}" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9" font-weight="bold">{label}</text>
    <text x="118" y="{y_cur - row_h//2 + 5}" fill="{vc}" font-family="{FONT_SANS}" font-size="{fs}" font-weight="{fw}">{value}</text>"""

    y_cur += 10
    svg += f"""
    <text x="14" y="{y_cur + 22}" fill="{C['accent_green']}" font-family="{FONT_SANS}" font-size="11" font-weight="bold">STATUT : {comp['status']}</text>
    <text x="14" y="{y_cur + 40}" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="8.5">Date : {comp['date']}  |  Rev. : {comp['revision']}  |  Auteur : {comp['author']}</text>
    <text x="14" y="{y_cur + 56}" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="8">Fichier : {comp['name']}_Plan2D.FCStd / .dxf</text>
  </g>"""

    return svg, total_h


def draw_specs(comp, ox, oy, W=320):
    svg = f"""
  <!-- SPECS D'ATELIER -->
  <g transform="translate({ox},{oy})">
    <rect width="{W}" height="298" rx="6" fill="{C['panel']}" stroke="{C['axis']}" stroke-width="1" filter="url(#shadow_panel)"/>
    <rect width="{W}" height="28" rx="6" fill="{C['panel']}" opacity="0.8"/>
    <text x="12" y="19" fill="{C['text_main']}" font-family="{FONT_SANS}" font-size="10" font-weight="bold">SPECIFICATIONS D'ATELIER (CNC C500)</text>
    <line x1="0" y1="28" x2="{W}" y2="28" stroke="{C['grid_line']}" stroke-width="0.8"/>

    <text x="10" y="46" fill="{C['border']}" font-family="{FONT_SANS}" font-size="9.5" font-weight="bold">1. MATERIAU BRUT ET USINAGE :</text>
    <text x="18" y="60" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Alliage : {comp['material']} (rho={comp['density']} g/cm3)</text>
    <text x="18" y="73" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Debit brut : {comp['W']:.0f} x {comp['H']:.0f} x {comp['T']+3:.0f} mm (surepais. +3 mm)</text>
    <text x="18" y="86" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Ep. finale : {comp['T']:.2f} mm (-0,05/0) — Redan : {comp['redan_depth']:.1f} mm</text>

    <text x="10" y="103" fill="{C['border']}" font-family="{FONT_SANS}" font-size="9.5" font-weight="bold">2. EBAVURAGE ET CHANFREINS :</text>
    <text x="18" y="117" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Chanfreins 0,3 mm x 45 deg sur tous les percages (zero morfil)</text>
    <text x="18" y="130" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Cassage d'aretes 0,5 mm x 45 deg sur pourtour exterieur</text>
    <text x="18" y="143" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Fraisure conique 90 deg sur alesage axial Ø{comp['alesage_axial_diam']:.0f} : noyage a fleur</text>

    <text x="10" y="160" fill="{C['border']}" font-family="{FONT_SANS}" font-size="9.5" font-weight="bold">3. AJUSTEMENTS FONCTIONNELS :</text>
    <text x="18" y="174" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Alesage RB8016 : Ø {comp['alesage_axial_diam']:.2f} mm — H7</text>
    <text x="18" y="187" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Centrage RS-06 : Ø {comp['centrage_diam']:.2f} mm | PCD M4 : +/- 0,02 mm</text>
    <text x="18" y="200" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Tolerance generale : {comp['tolerance_general']}</text>

    <text x="10" y="217" fill="{C['accent_green']}" font-family="{FONT_SANS}" font-size="9.5" font-weight="bold">4. METROLOGIE SUR MARBRE :</text>
    <text x="18" y="231" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Planeite globale &lt; 0,02 mm apres usinage 2 faces</text>
    <text x="18" y="244" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Perpendicularite alesage/face : &lt; 0,03 mm sur H={comp['T']:.0f} mm</text>
    <text x="18" y="257" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Rugosite Ra &lt; 1,6 um (Ra &lt; 0,8 um alesage)</text>
    <text x="18" y="270" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Controle CMM 100% : {comp['m4_count']}x M4 + {comp['m5_count']}x M5 + alesage central</text>
    <text x="18" y="283" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="9">* Volume B-Rep : {comp['volume_cm3']:.2f} cm3 | Masse th. : {comp['mass_g']:.1f} g</text>
  </g>"""
    return svg


def generate_full_plan(comp_key, output_dir):
    comp = COMPONENTS_DB[comp_key]
    name = comp["name"]
    out_path = os.path.join(output_dir, f"{name}_Plan2D_Expert.svg")

    PAGE_W = 1190
    PAGE_H = 842
    MARGIN = 18
    TITLE_W = 332
    HEADER_H = 56
    DRAW_H = PAGE_H - MARGIN * 2 - HEADER_H   # 750 px
    ZX = MARGIN
    ZY = MARGIN + HEADER_H                      # 92 px

    # ─── Échelle : sc=1.6 → W_s=281.7, H_s=281.7, T_s=14.4 ─────────────────
    tc_ox = PAGE_W - MARGIN - TITLE_W           # 840 px (séparation cartouche)
    sc = 1.6
    W_s = comp["W"] * sc    # 281.7
    H_s = comp["H"] * sc    # 281.7
    T_s = comp["T"] * sc    # 14.4

    # ─── Rangées ─────────────────────────────────────────────────────────────
    ROW_TOP_H = H_s + 70    # 351.7 px
    ROW_BOT_H = DRAW_H - ROW_TOP_H  # 398.3 px

    # ─── VUE DE DESSUS ───────────────────────────────────────────────────────
    VT_ox = ZX + 55         # 73
    VT_oy = ZY + 26         # 118 — espace pour label + cotes haut

    # ─── VUE DE DROITE ───────────────────────────────────────────────────────
    VR_ox = VT_ox + W_s + 55   # 410
    VR_oy = VT_oy               # 118 — alignée top avec vue dessus

    # ─── VUE ISOMÉTRIQUE ─────────────────────────────────────────────────────
    iso_zone_x = VR_ox + T_s + 35   # 459
    iso_zone_w = tc_ox - 10 - iso_zone_x  # 371
    sc_iso = 1.5
    VIso_cx = iso_zone_x + iso_zone_w / 2  # 644
    VIso_cy = ZY + ROW_TOP_H / 2           # 267

    # ─── VUE DE FACE ─────────────────────────────────────────────────────────
    VF_ox = VT_ox
    VF_oy = ZY + ROW_TOP_H + ROW_BOT_H * 0.22   # 513

    # ─── CALLOUTS : zone basse droite (sous la vue iso) ──────────────────────
    cx_t = VT_ox + W_s / 2   # centre vue dessus X
    cy_t = VT_oy + H_s / 2   # centre vue dessus Y
    m4r_s = comp["m4_pcd"] * sc / 2
    m5r_s = comp["m5_pcd"] * sc / 2

    cb_x = iso_zone_x        # 459 → callout boxes dans zone iso horizontale
    cb_y1 = ZY + ROW_TOP_H + 30    # 474 — callout M4
    cb_y2 = cb_y1 + 74 + 10        # 558 — callout M5
    cb_y3 = cb_y2 + 74 + 10        # 642 — callout alésage

    body = ""

    # Labels des vues (dans leur propre zone)
    body += f'\n  <text x="{VT_ox + W_s/2:.0f}" y="{VT_oy - 13:.0f}" fill="{C["text_label"]}" font-family="{FONT_SANS}" font-size="9.5" font-weight="600" text-anchor="middle" letter-spacing="0.4">VUE DE DESSUS (FACE USINEE) — ECH. 1:1</text>'
    body += f'\n  <text x="{VF_ox + W_s/2:.0f}" y="{VF_oy - 10:.0f}" fill="{C["text_label"]}" font-family="{FONT_SANS}" font-size="9.5" font-weight="600" text-anchor="middle" letter-spacing="0.4">VUE DE FACE (TRANCHE ET REDAN) — ECH. 1:1</text>'
    body += f'\n  <text x="{VR_ox + T_s/2:.0f}" y="{VR_oy - 13:.0f}" fill="{C["text_label"]}" font-family="{FONT_SANS}" font-size="9" font-weight="600" text-anchor="middle">VUE DE DROITE</text>'
    body += f'\n  <text x="{VIso_cx:.0f}" y="{ZY + ROW_TOP_H + 22:.0f}" fill="{C["text_label"]}" font-family="{FONT_SANS}" font-size="9.5" font-weight="600" text-anchor="middle" letter-spacing="0.4">VUE ISOMETRIQUE 3D</text>'

    # Lignes de séparation entre les rangées (trait fin)
    body += f'\n  <line x1="{MARGIN+2}" y1="{ZY + ROW_TOP_H + 2:.0f}" x2="{tc_ox - 10}" y2="{ZY + ROW_TOP_H + 2:.0f}" stroke="{C["grid_line"]}" stroke-width="0.8" opacity="0.5"/>'

    # Vues
    top_svg, cx_t, cy_t, m4r_s, m5r_s = draw_view_top(comp, VT_ox, VT_oy, sc)
    body += top_svg
    body += draw_view_front(comp, VF_ox, VF_oy, sc)
    body += draw_view_right(comp, VR_ox, VR_oy, sc)
    body += draw_view_iso(comp, VIso_cx, VIso_cy, sc_iso)

    # ─── Callout M4 ──────────────────────────────────────────────────────────
    m4_px = cx_t + m4r_s * math.cos(math.radians(45))
    m4_py = cy_t + m4r_s * math.sin(math.radians(45))
    body += callout(m4_px, m4_py, cb_x, cb_y1,
                    f"{comp['m4_count']}x M4 (PCD Ø {comp['m4_pcd']:.0f} mm)",
                    ["Taraudage M4 prof. 8 mm (borgne)",
                     "Fixation Stator RobStride RS-06",
                     "Entraxe PCD : +/- 0,02 mm"],
                    C["callout_m4"])

    # ─── Callout M5 ──────────────────────────────────────────────────────────
    m5_px = cx_t + m5r_s
    m5_py = cy_t
    body += callout(m5_px, m5_py, cb_x, cb_y2,
                    f"{comp['m5_count']}x Ø {comp['m5_drill_diam']:.2f} (Vis M5)",
                    ["Percages lisses debouchants",
                     "Fixation bague RB8016 + traverse",
                     "Chanfrein entree 0,3 x 45 deg"],
                    C["callout_m5"])

    # ─── Callout Alésage Central ─────────────────────────────────────────────
    body += callout(cx_t, cy_t, cb_x, cb_y3,
                    "Alesage Central (Usinage CN)",
                    [f"Alesage axial : Ø {comp['alesage_axial_diam']:.2f} H7 (RB8016)",
                     f"Centrage RS-06 : Ø {comp['centrage_diam']:.2f} mm",
                     f"Redan bague : Ø {comp['redan_diam']:.1f} x e={comp['redan_depth']:.1f} mm"],
                    C["border"])

    # ─── Cartouche + Specs ───────────────────────────────────────────────────
    cart_svg, cart_h = draw_title_block(comp, tc_ox, MARGIN + 6, TITLE_W)
    body += cart_svg
    specs_oy = MARGIN + 6 + cart_h + 14
    if specs_oy + 298 < PAGE_H - MARGIN:
        body += draw_specs(comp, tc_ox, specs_oy, TITLE_W)

    svg = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PAGE_W} {PAGE_H}" width="{PAGE_W}" height="{PAGE_H}">
{arrow_marker_defs()}
  <!-- Fond sombre Blueprint -->
  <rect width="{PAGE_W}" height="{PAGE_H}" fill="{C['bg']}"/>
  <rect x="{MARGIN}" y="{MARGIN}" width="{PAGE_W-MARGIN*2}" height="{PAGE_H-MARGIN*2}" fill="url(#bg_grid_lg)" rx="4"/>
  <!-- Cadre externe -->
  <rect x="{MARGIN}" y="{MARGIN}" width="{PAGE_W-MARGIN*2}" height="{PAGE_H-MARGIN*2}"
        fill="none" stroke="{C['border']}" stroke-width="1.8" rx="4"/>
  <!-- Séparateur en-tête -->
  <line x1="{MARGIN}" y1="{MARGIN+HEADER_H}" x2="{PAGE_W-MARGIN}" y2="{MARGIN+HEADER_H}"
        stroke="{C['border']}" stroke-width="1.2" opacity="0.65"/>
  <!-- Séparateur cartouche -->
  <line x1="{tc_ox - 8}" y1="{MARGIN}" x2="{tc_ox - 8}" y2="{PAGE_H-MARGIN}"
        stroke="{C['border']}" stroke-width="1.0" opacity="0.4"/>
  <!-- Titre en-tête -->
  <text x="{MARGIN+16}" y="{MARGIN+25}" fill="{C['border']}" font-family="{FONT_TITLE}"
        font-size="17" font-weight="bold" letter-spacing="1.5">PLAN TECHNIQUE MULTI-VUES ET VUE 3D ISOMETRIQUE</text>
  <text x="{MARGIN+16}" y="{MARGIN+44}" fill="{C['text_sec']}" font-family="{FONT_SANS}" font-size="10">
    Composant Structurel D-Bot — {comp['name']} ({comp['part_number']}) — Projection Orthogonale ISO — Format A2 Paysage</text>
{body}
  <!-- Pied de page -->
  <text x="{MARGIN+8}" y="{PAGE_H-MARGIN-5}" fill="{C['text_sec']}" font-family="{FONT_SANS}"
        font-size="8" opacity="0.6">
    Pipeline Souverain FreeCAD 1.1.3 / Python SVG Engine — Fichiers : {comp['name']}_Plan2D.FCStd / .dxf</text>
</svg>"""

    os.makedirs(output_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK Plan expert SVG genere : {out_path}")
    return out_path



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--component", default="waist_plate",
                        choices=list(COMPONENTS_DB.keys()) + ["all"])
    parser.add_argument("--output-dir", default="/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Plans_2D")
    args = parser.parse_args()

    if args.component == "all":
        for k in COMPONENTS_DB:
            generate_full_plan(k, args.output_dir)
    else:
        generate_full_plan(args.component, args.output_dir)


if __name__ == "__main__":
    main()
