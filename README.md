# Qrauts AG Themensammler (mit Archiv & Import)

## Features
- Themen/Sprints mit Titel, Beschreibung, Rubrik, Links, Autor (Marek/Annika/Kurt/Gerd)
- Automatische Zeitstempel (Europe/Berlin)
- Updates & Kommentare je Thema
- Kategorien verwalten (CRUD), Zuordnung änderbar
- Filter (Rubrik, Autor, Suche, Zeitraum), Auswahl -> PDF-Export (Auswahl/alle/einzelnes Thema)
- **Archiv-Funktion**: Themen archivieren/wiederherstellen; Excel-Export `archiv.xlsx`
- **GitHub-Archiv**: RAW-URL in der Sidebar hinterlegen -> `archiv.xlsx` laden; lokales Archiv erzeugen und manuell ins Repo pushen
- Hintergrund: Windräder + kleine Pferde (CSS-Animation); Naturfarben

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Archiv (Excel)
- In der Sidebar kann die RAW-URL Deiner `archiv.xlsx` gesetzt werden (READ).
- Mit „Lokales Archiv erzeugen“ wird eine aktuelle `archiv.xlsx` im App-Ordner erzeugt. Diese kannst Du committen/pushen.

## Import
- Excel: Spalten **Titel, Beschreibung, Rubrik, Autor, Eroeffnung, Links(JSON optional)**.

## Hinweise
- Die DB `themensammler.db` wird automatisch angelegt. In dieser ZIP ist sie bereits mit den Themen aus Deinem PDF vorbefüllt.
