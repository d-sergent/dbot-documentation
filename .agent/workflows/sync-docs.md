---
description: Sync dbot-documentation to Google Drive after modifications
---

# Sync Documentation to Google Drive

After modifying any documentation file in the dbot-documentation project, follow these steps:

## 1. Regenerate the portal

Run the portal generation script (inline Python) from the dbot-documentation directory to update `index.html` and `PORTAIL_D-BOT.html`.

## 2. Git commit and push

// turbo
```bash
cd /Users/davidsergent/.gemini/antigravity/scratch/dbot-documentation && git add -A && git commit -m "<commit message>" && git push origin main
```

## 3. Copy to Google Drive

// turbo
```bash
rsync -av --exclude='.git' --exclude='.DS_Store' /Users/davidsergent/.gemini/antigravity/scratch/dbot-documentation/ "/Users/davidsergent/Library/CloudStorage/GoogleDrive-davidsergent78@gmail.com/Mon Drive/Documentation/"
```

This syncs all documentation files (markdown, HTML portal, assets) to the user's Google Drive, excluding git metadata.
