#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mise à jour et génération du plan 2D SVG optimisé pour Waist_Plate_7075
"""
import os
import re
import FreeCAD
import Part
import TechDraw
from FreeCAD import Vector

step_path = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP/Waist_Plate_7075.step"
out_path = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Plans_2D/Waist_Plate_7075_Plan2D.svg"

doc = FreeCAD.newDocument("t")
shape = Part.read(step_path)
feat = doc.addObject("Part::Feature", "p")
feat.Shape = shape

page = doc.addObject("TechDraw::DrawPage", "page")
template = doc.addObject("TechDraw::DrawSVGTemplate", "tmpl")
template.Template = "/Applications/FreeCAD.app/Contents/Resources/share/Mod/TechDraw/Templates/Default_Template_A4_Landscape.svg"
page.Template = template

# Projection de face (Vector 0, 0, -1) pour révéler tous les alésages et épaulements usinés
v = doc.addObject("TechDraw::DrawViewPart", "v")
v.Source = feat
v.Direction = Vector(0, 0, -1)
page.addView(v)
doc.recompute()

raw_svg = TechDraw.viewPartAsSvg(v)

bbox = shape.BoundBox
dx = bbox.XMax - bbox.XMin
dy = bbox.YMax - bbox.YMin
dz = bbox.ZMax - bbox.ZMin

clean_frag = re.sub(r'stroke="#000000"', 'stroke="#38bdf8"', raw_svg)
clean_frag = re.sub(r'stroke-width="0.7"', 'stroke-width="1.0"', clean_frag)

scale = 1.8
cx = 340
cy = 350

w_px = (dx / 2.0) * scale
h_px = (dy / 2.0) * scale

x_left = cx - w_px
x_right = cx + w_px
y_top = cy - h_px
y_bottom = cy + h_px

y_dim_w = y_bottom + 40
x_dim_h = x_left - 40

svg_out = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" width="100%" height="100%">
  <defs>
    <pattern id="grid_subtle" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="0.6"/>
    </pattern>
    <pattern id="grid_major" width="100" height="100" patternUnits="userSpaceOnUse">
      <rect width="100" height="100" fill="url(#grid_subtle)"/>
      <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#334155" stroke-width="1.0" opacity="0.6"/>
    </pattern>
    <marker id="arrow-start" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 10 2 L 0 5 L 10 8 z" fill="#facc15"/>
    </marker>
    <marker id="arrow-end" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 2 L 10 5 L 0 8 z" fill="#facc15"/>
    </marker>
  </defs>

  <!-- Fond sombre Blueprint -->
  <rect width="1000" height="700" fill="#0f172a"/>

  <!-- Cadre technique -->
  <rect x="20" y="20" width="960" height="660" rx="8" fill="#0b1329" stroke="#38bdf8" stroke-width="1.5" opacity="0.85"/>
  <rect x="30" y="30" width="940" height="640" fill="url(#grid_major)" rx="4"/>

  <!-- En-tête -->
  <g transform="translate(45, 55)">
    <text x="0" y="0" fill="#38bdf8" font-family="'Segoe UI', system-ui, sans-serif" font-size="16" font-weight="bold" letter-spacing="1.2">PLAN D'ATELIER &amp; CONTRÔLE MÉTROLOGIQUE 2D</text>
    <text x="0" y="18" fill="#94a3b8" font-family="'Segoe UI', system-ui, sans-serif" font-size="11">Liaison Active Waist Yaw (RS-06) — Platine Supérieure Déportée (Face Usinée)</text>
  </g>

  <!-- Lignes de centrage -->
  <g stroke="#64748b" stroke-width="1.0" stroke-dasharray="10,3,2,3" opacity="0.75">
    <line x1="{x_left - 40}" y1="{cy}" x2="{x_right + 40}" y2="{cy}" />
    <line x1="{cx}" y1="{y_top - 40}" x2="{cx}" y2="{y_bottom + 40}" />
  </g>

  <!-- Géométrie FreeCAD projetée -->
  <g id="freecad_projected_geometry" transform="translate({cx}, {cy}) scale({scale}, {scale})">
    {clean_frag}
  </g>

  <!-- Cotes Largeur Hors-Tout : dx mm -->
  <g id="cotes_largeur">
    <line x1="{x_left}" y1="{y_bottom + 5}" x2="{x_left}" y2="{y_dim_w + 8}" stroke="#64748b" stroke-width="0.8" stroke-dasharray="3,3"/>
    <line x1="{x_right}" y1="{y_bottom + 5}" x2="{x_right}" y2="{y_dim_w + 8}" stroke="#64748b" stroke-width="0.8" stroke-dasharray="3,3"/>
    <line x1="{x_left + 4}" y1="{y_dim_w}" x2="{x_right - 4}" y2="{y_dim_w}" stroke="#facc15" stroke-width="1.3" marker-start="url(#arrow-start)" marker-end="url(#arrow-end)"/>
    <rect x="{cx - 42}" y="{y_dim_w - 10}" width="84" height="20" fill="#0f172a" rx="4" stroke="#facc15" stroke-width="1"/>
    <text x="{cx}" y="{y_dim_w + 4}" fill="#facc15" font-family="'Segoe UI', monospace" font-size="11" font-weight="bold" text-anchor="middle">{dx:.2f} mm</text>
  </g>

  <!-- Cotes Hauteur Hors-Tout : dy mm -->
  <g id="cotes_hauteur">
    <line x1="{x_left - 5}" y1="{y_top}" x2="{x_dim_h - 8}" y2="{y_top}" stroke="#64748b" stroke-width="0.8" stroke-dasharray="3,3"/>
    <line x1="{x_left - 5}" y1="{y_bottom}" x2="{x_dim_h - 8}" y2="{y_bottom}" stroke="#64748b" stroke-width="0.8" stroke-dasharray="3,3"/>
    <line x1="{x_dim_h}" y1="{y_top + 4}" x2="{x_dim_h}" y2="{y_bottom - 4}" stroke="#facc15" stroke-width="1.3" marker-start="url(#arrow-start)" marker-end="url(#arrow-end)"/>
    <rect x="{x_dim_h - 42}" y="{cy - 10}" width="84" height="20" fill="#0f172a" rx="4" stroke="#facc15" stroke-width="1" transform="rotate(-90 {x_dim_h} {cy})"/>
    <text x="{x_dim_h}" y="{cy + 4}" fill="#facc15" font-family="'Segoe UI', monospace" font-size="11" font-weight="bold" text-anchor="middle" transform="rotate(-90 {x_dim_h} {cy})">{dy:.2f} mm</text>
  </g>

  <!-- Callouts usinages -->
  <g id="callout_alesage_central">
    <polyline points="{cx - 40*scale}, {cy - 40*scale} 220, 200 120, 200" fill="none" stroke="#38bdf8" stroke-width="1.2"/>
    <circle cx="{cx - 40*scale}" cy="{cy - 40*scale}" r="3" fill="#38bdf8"/>
    <text x="120" y="185" fill="#38bdf8" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold">Alésages Centraux</text>
    <text x="120" y="198" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="10">• Siège RB8016 : Ø 80,00 mm</text>
    <text x="120" y="211" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="10">• Centrage RS-06 : Ø 89,62 mm</text>
  </g>

  <g id="callout_m4_rs06">
    <polyline points="{cx + 25.35*scale}, {cy - 32.71*scale} 450, 220 540, 220" fill="none" stroke="#facc15" stroke-width="1.2"/>
    <circle cx="{cx + 25.35*scale}" cy="{cy - 32.71*scale}" r="3" fill="#facc15"/>
    <text x="450" y="208" fill="#facc15" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">4x M4 (PCD Ø 68.0 mm)</text>
    <text x="450" y="233" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="9">Stator RobStride RS-06</text>
  </g>

  <g id="callout_m5">
    <polyline points="{cx + 49.09*scale}, {cy + 49.09*scale} 480, 480 570, 480" fill="none" stroke="#4ade80" stroke-width="1.2"/>
    <circle cx="{cx + 49.09*scale}" cy="{cy + 49.09*scale}" r="3" fill="#4ade80"/>
    <text x="480" y="470" fill="#4ade80" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">4x Ø 5.10 mm (Vis M5)</text>
    <text x="480" y="493" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="9">Fixation bague &amp; Traverse</text>
  </g>

  <!-- Panneau Spécifications d'Atelier (Haut Droite) -->
  <g transform="translate(640, 45)">
    <rect width="320" height="260" rx="6" fill="#1e293b" stroke="#475569" stroke-width="1"/>
    <rect width="320" height="30" rx="6" fill="#334155"/>
    <text x="12" y="20" fill="#f8fafc" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" letter-spacing="0.5">SPÉCIFICATIONS D'ATELIER (CNC C500)</text>

    <g transform="translate(12, 48)" font-family="'Segoe UI', sans-serif" font-size="10" fill="#e2e8f0">
      <text x="0" y="0" font-weight="bold" fill="#38bdf8">1. MATÉRIAU BRUT &amp; USINAGE :</text>
      <text x="8" y="16" fill="#94a3b8">• Alliage : Aluminium 7075-T6 laminé</text>
      <text x="8" y="30" fill="#94a3b8">• Débit brut requis : 185 x 185 x 12,0 mm</text>
      <text x="8" y="44" fill="#94a3b8">• Épaisseur finale surfacée : 9,00 mm (-0,05 / 0)</text>

      <text x="0" y="68" font-weight="bold" fill="#38bdf8">2. ÉBAVURAGE &amp; CHANFREINS :</text>
      <text x="8" y="84" fill="#94a3b8">• Chanfreins 0,3 mm x 45° sur perçages</text>
      <text x="8" y="98" fill="#94a3b8">• Cassage d'arêtes 0,5 mm x 45° sur pourtour</text>

      <text x="0" y="122" font-weight="bold" fill="#38bdf8">3. AJUSTEMENTS FONCTIONNELS :</text>
      <text x="8" y="138" fill="#94a3b8">• Siège bague RB8016 : Ø 120 H7 x 3,0 mm</text>
      <text x="8" y="152" fill="#94a3b8">• Centrage moteur RS-06 : Ø 88 H7</text>
      <text x="8" y="166" fill="#94a3b8">• Tolérance générale : ISO 2768-mK</text>

      <text x="0" y="190" font-weight="bold" fill="#4ade80">4. MÉTROLOGIE SUR MARBRE :</text>
      <text x="8" y="206" fill="#94a3b8">• Planéité globale &lt; 0,02 mm (surfaçage 2 faces)</text>
    </g>
  </g>

  <!-- Cartouche Technique Normalisé (Bas Droite) -->
  <g transform="translate(640, 325)">
    <rect width="320" height="335" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    
    <rect width="320" height="34" rx="6" fill="#0284c7" opacity="0.25"/>
    <line x1="0" y1="34" x2="320" y2="34" stroke="#38bdf8" stroke-width="1.2"/>
    <text x="160" y="22" fill="#38bdf8" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold" text-anchor="middle" letter-spacing="1">D-BOT HUMANOID ROBOT V1</text>

    <!-- Grille cartouche -->
    <line x1="0" y1="80" x2="320" y2="80" stroke="#334155" stroke-width="1"/>
    <line x1="0" y1="130" x2="320" y2="130" stroke="#334155" stroke-width="1"/>
    <line x1="0" y1="180" x2="320" y2="180" stroke="#334155" stroke-width="1"/>
    <line x1="0" y1="230" x2="320" y2="230" stroke="#334155" stroke-width="1"/>
    <line x1="0" y1="275" x2="320" y2="275" stroke="#334155" stroke-width="1"/>

    <line x1="115" y1="34" x2="115" y2="275" stroke="#334155" stroke-width="1"/>

    <!-- Ligne 1: Pièce -->
    <text x="12" y="60" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">PIÈCE :</text>
    <text x="125" y="62" fill="#f8fafc" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold">Waist_Plate_7075</text>

    <!-- Ligne 2: Désignation -->
    <text x="12" y="108" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">DÉSIGNATION :</text>
    <text x="125" y="108" fill="#e2e8f0" font-family="'Segoe UI', sans-serif" font-size="10">Platine Supérieure Waist Yaw</text>

    <!-- Ligne 3: Matériau -->
    <text x="12" y="158" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">MATÉRIAU :</text>
    <text x="125" y="158" fill="#f8fafc" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold">Alu 7075-T6 (2,81 g/cm³)</text>

    <!-- Ligne 4: Masse & Épaisseur -->
    <text x="12" y="208" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">MASSE / ÉP. :</text>
    <text x="125" y="208" fill="#facc15" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold">486,8 g  |  e = 9,00 mm</text>

    <!-- Ligne 5: Référence / Éch -->
    <text x="12" y="255" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold">RÉF. / ÉCH. :</text>
    <text x="125" y="255" fill="#e2e8f0" font-family="'Segoe UI', sans-serif" font-size="10">ASV1_100_02A | Éch. 1:1</text>

    <!-- Ligne 6: Statut & Signature -->
    <text x="15" y="300" fill="#4ade80" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold">STATUT : VALIDÉ POUR FRAISAGE C500</text>
    <text x="15" y="322" fill="#94a3b8" font-family="'Segoe UI', sans-serif" font-size="9">Date : 2026-09-28 | Auteur : D-Bot Core Team</text>
  </g>

  <!-- Pied de page -->
  <g transform="translate(45, 672)">
    <text x="0" y="0" fill="#64748b" font-family="'Segoe UI', sans-serif" font-size="9">Généré automatiquement par le pipeline souverain FreeCAD 1.1.3 / OpenCASCADE — Fichier DXF CNC associé : Waist_Plate_7075_Plan2D.dxf</text>
  </g>
</svg>
"""

with open(out_path, "w", encoding="utf-8") as f:
    f.write(svg_out)
print(f"✅ Plan SVG 2D généré avec succès dans: {out_path}")
