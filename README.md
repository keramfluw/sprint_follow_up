# Qrauts AG Themensammler – Full Export Edition

- **Voll-Export (XLSX)**: Alle Themen + Links + Updates + Kommentare + Meta, direkt als Download.
- Archiv-Funktion (Excel + GitHub-RAW lesen), PDF-Export (Auswahl/alle/einzeln), Excel-Import.
- Hintergrund: Windräder + kleine Pferde (CSS). Zeitstempel lesbar formatiert.

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## XLSX Voll-Export
- Sidebar → **📤 Voll-Export (XLSX)** → Download `themensammler_full_export.xlsx`.
- Tabs: `Topics`, `Links`, `Updates`, `Comments`, `Meta`.

## GitHub-Archiv
- Sidebar → **📦 Archiv (Excel)**: RAW-URL hinterlegen (lesen), lokales `archiv.xlsx` (nur archivierte Themen) generieren und manuell ins Repo pushen.

