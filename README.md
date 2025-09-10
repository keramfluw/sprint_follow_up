# Qrauts AG Themensammler

Streamlit-App zur strukturierten Erfassung, Pflege und Auswertung von Themen/Sprint-Projekten für Marek, Annika, Kurt und Gerd.

## Features
- **Themen anlegen** mit Titel, Beschreibung, Rubrik, Links und **Autor** (Dropdown).
- **Automatischer Eröffnungstag** (Zeitstempel Europe/Berlin).
- **Updates** und **Kommentare** mit Datum/Zeitstempel.
- **Kategorien verwalten** (hinzufügen/löschen) und **Zuordnung je Thema** jederzeit änderbar.
- **Filter** (Rubrik, Autor, Suche, Zeitraum).
- **Mehrfachselektion** und **PDF-Export** (Auswahl / alle / einzelnes Thema).
- **Hintergrund-Animation**: Windräder und kleine Pferde am unteren Rand.
- **Natur-/Umwelt-Farbschema**.

## Installation
1. Python 3.10+ installieren.
2. Virtuelle Umgebung (optional) erstellen und aktivieren.
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

## Start
```bash
streamlit run app.py
```
Die App legt beim ersten Start eine SQLite-DB `themensammler.db` im App-Verzeichnis an.

## Export (PDF)
- In der Seitenleiste: **PDF export (Auswahl)** oder **PDF export (Alle)**.
- Pro Thema auch Einzel-Export möglich.
- PDF-Erstellung erfolgt lokal in der App (ReportLab).

## Hinweise
- **Benutzerliste** ist aktuell fest: *Marek, Annika, Kurt, Gerd.*
- **Rubriken** sind im UI pflegbar.
- **Links** je Thema: Mehrere möglich (http/https).
- Zeitstempel in **Europe/Berlin**.

## Ordnerstruktur
```
app.py
requirements.txt
README.md
```
