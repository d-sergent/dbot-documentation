import json
import os

# Configuration
DOCS_DIR = "/Users/davidsergent/Library/CloudStorage/GoogleDrive-davidsergent78@gmail.com/Mon Drive/Documentation"
OUTPUT_FILES = ["PORTAIL_D-BOT.html", "index.html"]

# List of files to include
files_to_read = [
    ('00_Index.md', 'Fondations', '00_Index'),
    ('01_Synthese_Projet.md', 'Fondations', '01_Synthese'),
    ('02_Liste_Achats.md', 'Fondations', '02_Liste_Achats'),
    ('03_Montage_Mecanique.md', 'Conception', '03_Montage_Mecanique'),
    ('04_Electronique_Cablage.md', 'Conception', '04_Electronique_Cablage'),
    ('05_Logiciel_Configuration.md', 'Conception', '05_Logiciel_Configuration'),
    ('06_Decisions_Architecturales.md', 'Conception', '06_Decisions_Architecturales'),
    ('14_Cinematique_Moteurs.md', 'Conception', '14_Cinematique_Moteurs'),
    ('15_Analyse_Biomecanique.md', 'Conception', '15_Hub_Biomecanique'),
    ('15a_Analyse_Locomotion_Baseline.md', 'Conception', '15a_Locomotion'),
    ('15b_Configurations_Moteurs.md', 'Conception', '15b_Configurations'),
    ('15c_Revision_Cardan_39kg.md', 'Conception', '15c_Cardan_39kg'),
    ('15d_Genou_et_Course.md', 'Conception', '15d_Genou_Course'),
    ('16_Conclusions_Architecture_DBot.md', 'Conception', '16_Conclusions'),
    ('19_Perception_Spatiale_LiDAR.md', 'Conception', '19_Perception_LiDAR'),
    ('07_Vision_IA.md', 'Perception', '07_Vision_IA'),
    ('08_Audio_Perception.md', 'Perception', '08_Audio_Perception'),
    ('09_Guide_Avance_Impression.md', 'Fabrication', '09_Guide_Avance_Impression'),
    ('10_Guide_Buse_Tungstene.md', 'Fabrication', '10_Guide_Buse_Tungstene'),
    ('12_Guide_Parties_Metal_CNC.md', 'Fabrication', '12_Guide_Parties_Metal_CNC'),
    ('11_Guide_SensiEDGE_Watchdog.md', 'Securite', '11_Guide_SensiEDGE_Watchdog'),
    ('13_Securite_Electrique.md', 'Securite', '13_Securite_Electrique'),
    ('16_Annexe_Batterie_NMC.md', 'Annexes', '16_Annexe_Batterie_NMC'),
    ('17_Annexe_Batterie_SemiSolide.md', 'Annexes', '17_Annexe_SemiSolide'),
    ('18_Annexe_Batterie_Comparatif.md', 'Annexes', '18_Annexe_Comparatif'),
    ('20_Etude_Cheville_Cardan.md', 'Annexes', '20_Etude_Cheville'),
    ('21_Etude_Usinage_CNC_Milo.md', 'Annexes', '21_Etude_Usinage_CNC_Milo'),
    ('21_Etude_Main_Robotique.md', 'Annexes', '21_Etude_Main_Robotique'),
    ('22_Usinage_CNC_C500.md', 'Annexes', '22_Usinage_CNC_C500'),
]

def generate_portal():
    docs = {}
    print(f"Reading {len(files_to_read)} files from {DOCS_DIR}...")
    
    for filename, group, key in files_to_read:
        filepath = os.path.join(DOCS_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    docs[f'{group}: {key}'] = f.read()
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        else:
            print(f"Warning: File not found: {filename}")

    # Serialize docs to JSON for embedding
    docs_js = json.dumps(docs, ensure_ascii=False)

    # HTML Template
    html_template = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portail Documentation D-Bot</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body { box-sizing: border-box; min-width: 200px; max-width: 1200px; margin: 0 auto; padding: 45px; display: flex; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
        #sidebar { width: 280px; padding-right: 20px; border-right: 1px solid #e1e4e8; height: calc(100vh - 90px); overflow-y: auto; position: sticky; top: 45px; flex-shrink: 0; }
        #content { flex: 1; padding-left: 40px; min-width: 0; }
        .markdown-body { max-width: 100%; overflow-x: auto; }
        .markdown-body table { font-size: 0.78em; width: 100%; table-layout: fixed; }
        .markdown-body table th { padding: 4px 5px; white-space: normal; line-height: 1.3; }
        .markdown-body table td { padding: 4px 5px; line-height: 1.3; }
        .nav-item { display: block; padding: 8px 12px; text-decoration: none; color: #0366d6; border-radius: 6px; cursor: pointer; font-size: 14px; margin-bottom: 2px; }
        .nav-item:hover { background-color: #f6f8fa; }
        .nav-item.active { background-color: #0366d6; color: white; font-weight: bold; }
        .nav-group { font-weight: bold; margin-top: 20px; margin-bottom: 8px; padding-left: 12px; color: #24292e; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; border-left: 3px solid #0366d6; }
        .nav-group:first-child { margin-top: 0; }
        @media (max-width: 767px) { body { flex-direction: column; padding: 15px; } #sidebar { width: 100%; border-right: none; border-bottom: 1px solid #e1e4e8; height: auto; position: relative; top: 0; margin-bottom: 20px; } #content { padding-left: 0; } }
    </style>
</head>
<body>
    <div id="sidebar">
        <h2 style="font-size: 1.3em; margin-bottom: 20px; color: #24292e;">📚 D-Bot Documentation</h2>
        <div id="nav-list"></div>
    </div>
    <div id="content" class="markdown-body"><div id="view"></div></div>
    <script>
        mermaid.initialize({ startOnLoad: false });
        // Injected docs content
        const docs = DOCS_PLACEHOLDER;
        
        const navList = document.getElementById('nav-list');
        const view = document.getElementById('view');
        
        function renderDoc(key) {
            view.innerHTML = marked.parse(docs[key]);
            mermaid.run({ nodes: view.querySelectorAll('.language-mermaid') });
            window.scrollTo(0, 0);
            document.querySelectorAll('.nav-item').forEach(el => { el.classList.toggle('active', el.dataset.key === key); });
            history.replaceState(null, null, '#' + encodeURIComponent(key));
        }
        
        let currentGroup = "";
        Object.keys(docs).forEach(label => {
            const [group, name] = label.split(': ');
            if (group !== currentGroup) {
                const groupEl = document.createElement('div');
                groupEl.className = 'nav-group';
                groupEl.innerText = group;
                navList.appendChild(groupEl);
                currentGroup = group;
            }
            const item = document.createElement('a');
            item.className = 'nav-item';
            item.innerText = name.replace(/_/g, ' ');
            item.dataset.key = label;
            item.onclick = () => renderDoc(label);
            navList.appendChild(item);
        });
        
        const hash = decodeURIComponent(window.location.hash.substring(1));
        if (hash && docs[hash]) { renderDoc(hash); } else { renderDoc("Fondations: 00_Index"); }
        
        view.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (!link) return;
            const href = link.getAttribute('href');
            if (!href) return;
            if (href.startsWith('./') || href.endsWith('.md')) {
                e.preventDefault();
                const filename = href.replace('./', '').replace('.md', '');
                const match = Object.keys(docs).find(k => k.includes(filename));
                if (match) { renderDoc(match); }
            }
        });
    </script>
</body>
</html>"""

    # Replace placeholder
    final_html = html_template.replace("DOCS_PLACEHOLDER", docs_js)

    # Write output files
    for outfile in OUTPUT_FILES:
        outpath = os.path.join(DOCS_DIR, outfile)
        try:
            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(final_html)
            print(f"Successfully generated {outfile}")
        except Exception as e:
            print(f"Error writing {outfile}: {e}")

if __name__ == "__main__":
    generate_portal()
