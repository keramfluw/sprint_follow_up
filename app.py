# Qrauts AG Themensammler
# Streamlit App
# Features:
# - Sprint-Themen anlegen (Titel, Beschreibung, Kategorie, Links), Autor aus Dropdown (Marek, Annika, Kurt, Gerd)
# - Automatischer Eröffnungstag (Datum/Zeitstempel Europe/Berlin)
# - Updates & Kommentare mit Datum/Zeitstempel
# - Kategorien verwalten (hinzufügen/löschen) und Zuordnung pro Thema jederzeit änderbar
# - Filter (Kategorie, Person, Suche, Zeitraum), Mehrfachauswahl
# - Export gewählter Einträge (oder aller) als PDF
# - Hintergrund: animierte Windräder + kleine Pferde am unteren Rand (zufällig)
# - Natur-/Umwelt-Farbschema
#
# Start:  streamlit run app.py
# Python: 3.10+

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
from zoneinfo import ZoneInfo
import json
import re
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import utils

APP_TITLE = "Qrauts AG Themensammler"
USERS = ["Marek", "Annika", "Kurt", "Gerd"]
DEFAULT_CATEGORIES = ["Wohnungswirtschaft", "Privatpersonen", "Leuchtturmprojekte", "Cashflowprojekte"]
TZ = ZoneInfo("Europe/Berlin")
DB_PATH = "themensammler.db"

st.set_page_config(page_title=APP_TITLE, layout="wide")

# ---------- Styling & Background Animations ----------
def inject_theme_and_animations():
    html = r'''
    <style>
      :root{
        --eco-green:#2F7D32;
        --leaf:#4CAF50;
        --earth:#2E3B2A;
        --sky:#E6F5EA;
        --sand:#DDEAD7;
        --ink:#0B1B13;
      }
      .stApp {
        background: linear-gradient(180deg, var(--sky) 0%, #F7FFF9 60%);
        color: var(--ink);
      }
      /* Cards */
      .stMarkdown, .stTextInput, .stSelectbox, .stDataFrame, .stExpander, .stButton>button, .stDownloadButton>button {
        border-radius: 12px !important;
      }
      /* Header */
      header[data-testid="stHeader"] {background: rgba(0,0,0,0);}
      /* Wind farm */
      .windfarm {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: -1;
      }
      .wind {
        position: absolute;
        bottom: 8rem;
        width: 140px; height: 180px;
        opacity: 0.25;
      }
      .mast {
        position:absolute; bottom:0; left:68px; width:4px; height:140px; background: var(--earth); border-radius:2px;
      }
      .nacelle {
        position:absolute; bottom:120px; left:58px; width:24px; height:10px; background: var(--earth); border-radius:4px;
      }
      .hub {
        position:absolute; bottom:126px; left:68px; width:8px; height:8px; background: var(--earth); border-radius:50%;
        transform-origin:center center;
      }
      .blade {
        position:absolute; bottom:126px; left:72px; width:80px; height:2px; background: var(--leaf);
        transform-origin: -4px 1px;
        border-radius:2px;
      }
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      .rotor { animation: spin var(--spd,10s) linear infinite; transform-origin: 72px 127px; }
      /* Horses */
      .field {
        position: fixed; bottom: 0; left: 0; right: 0; height: 120px;
        background: linear-gradient(0deg, #CFE8C5 0%, transparent 80%);
        z-index: 0; pointer-events: none;
      }
      .horse {
        position: fixed;
        bottom: 12px;
        font-size: 18px;
        opacity: 0.9;
        filter: saturate(0.6);
        animation-name: gallop;
        animation-timing-function: linear;
        animation-iteration-count: 1;
        pointer-events: none;
      }
      @keyframes gallop {
        from { transform: translateX(-10vw); }
        to   { transform: translateX(calc(100vw + 10vw)); }
      }
      /* Eco accents */
      div[data-testid="stSidebar"] {
        background: #F2FBF4;
        border-right: 1px solid #E0F2E6;
      }
      .eco-accent {
        border-left: 6px solid var(--leaf);
        padding-left: 12px;
        background: #F6FFF8;
        border-radius: 8px;
      }
      /* Dataframe tweaks */
      .stDataFrame { background: white; }
    </style>
    <div class="windfarm">
      <div class="wind" style="left:6vw;"><div class="mast"></div><div class="nacelle"></div><div class="rotor"><div class="hub"></div><div class="blade"></div><div class="blade" style="transform: rotate(120deg)"></div><div class="blade" style="transform: rotate(240deg)"></div></div></div>
      <div class="wind" style="left:18vw; transform: scale(0.9);"><div class="mast"></div><div class="nacelle"></div><div class="rotor" style="animation-duration:12s;"><div class="hub"></div><div class="blade"></div><div class="blade" style="transform: rotate(120deg)"></div><div class="blade" style="transform: rotate(240deg)"></div></div></div>
      <div class="wind" style="left:32vw; transform: scale(1.1);"><div class="mast"></div><div class="nacelle"></div><div class="rotor" style="animation-duration:8s;"><div class="hub"></div><div class="blade"></div><div class="blade" style="transform: rotate(120deg)"></div><div class="blade" style="transform: rotate(240deg)"></div></div></div>
      <div class="wind" style="left:56vw; transform: scale(0.85);"><div class="mast"></div><div class="nacelle"></div><div class="rotor" style="animation-duration:11s;"><div class="hub"></div><div class="blade"></div><div class="blade" style="transform: rotate(120deg)"></div><div class="blade" style="transform: rotate(240deg)"></div></div></div>
      <div class="wind" style="left:74vw; transform: scale(1.05);"><div class="mast"></div><div class="nacelle"></div><div class="rotor" style="animation-duration:9s;"><div class="hub"></div><div class="blade"></div><div class="blade" style="transform: rotate(120deg)"></div><div class="blade" style="transform: rotate(240deg)"></div></div></div>
    </div>
    <div class="field" id="horse-field"></div>
    <script>
      const emojis = ["🐎","🐴","🦄"];
      function spawnHorse(){
        const h = document.createElement("div");
        h.className = "horse";
        h.textContent = emojis[Math.floor(Math.random()*emojis.length)];
        const y = 6 + Math.random()*50;
        const dur = 10 + Math.random()*16;
        const size = 14 + Math.random()*14;
        h.style.bottom = y + "px";
        h.style.left = "-10vw";
        h.style.fontSize = size + "px";
        h.style.animationDuration = dur + "s";
        document.body.appendChild(h);
        setTimeout(()=> h.remove(), (dur+1)*1000);
      }
      // spawn bursts
      setInterval(()=>{
        if (document.visibilityState === 'visible'){
          const n = 1 + Math.floor(Math.random()*2);
          for(let i=0;i<n;i++){ setTimeout(spawnHorse, i*800); }
        }
      }, 6000);
    </script>
    '''
    st.markdown(html, unsafe_allow_html=True)

inject_theme_and_animations()

# ---------- Database ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS categories(
        name TEXT PRIMARY KEY
    );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS topics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        created_by TEXT,
        created_at TEXT,
        links TEXT DEFAULT '[]',
        FOREIGN KEY(category) REFERENCES categories(name) ON UPDATE CASCADE ON DELETE SET NULL
    );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS updates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        user TEXT,
        content TEXT,
        created_at TEXT,
        FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
    );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        user TEXT,
        content TEXT,
        created_at TEXT,
        FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
    );""")
    # Seed default categories if not present
    for cat in DEFAULT_CATEGORIES:
        try:
            cur.execute("INSERT OR IGNORE INTO categories(name) VALUES(?)", (cat,))
        except:
            pass
    conn.commit()
    return conn

conn = init_db()

# ---------- Helpers ----------
def now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")

def valid_url(url:str)->bool:
    return bool(re.match(r"^https?://", url.strip()))

def get_categories():
    return [r[0] for r in conn.execute("SELECT name FROM categories ORDER BY name ASC")]

def add_category(name:str):
    name = name.strip()
    if not name: return
    conn.execute("INSERT OR IGNORE INTO categories(name) VALUES(?)", (name,))
    conn.commit()

def delete_category(name:str):
    conn.execute("DELETE FROM categories WHERE name = ?", (name,))
    conn.commit()

def create_topic(title, description, category, created_by, links):
    created_at = now_iso()
    links_json = json.dumps(links, ensure_ascii=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO topics(title, description, category, created_by, created_at, links)
                   VALUES(?,?,?,?,?,?)""", (title, description, category, created_by, created_at, links_json))
    conn.commit()
    return cur.lastrowid

def update_topic_category(topic_id:int, category:str):
    conn.execute("UPDATE topics SET category=? WHERE id=?", (category, topic_id))
    conn.commit()

def add_link_to_topic(topic_id:int, url:str, label:str):
    row = conn.execute("SELECT links FROM topics WHERE id=?", (topic_id,)).fetchone()
    links = []
    if row and row[0]:
        try:
            links = json.loads(row[0])
        except:
            links = []
    links.append({"label":label.strip() or url.strip(), "url":url.strip()})
    conn.execute("UPDATE topics SET links=? WHERE id=?", (json.dumps(links, ensure_ascii=False), topic_id))
    conn.commit()

def list_topics(filters:dict):
    q = "SELECT id, title, description, category, created_by, created_at, links FROM topics WHERE 1=1"
    params = []
    if filters.get("categories"):
        q += " AND category IN ({})".format(",".join(["?"]*len(filters["categories"])))
        params += filters["categories"]
    if filters.get("users"):
        q += " AND created_by IN ({})".format(",".join(["?"]*len(filters["users"])))
        params += filters["users"]
    if filters.get("q"):
        q += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
        s = f"%{filters['q'].lower()}%"
        params += [s,s]
    if filters.get("date_from"):
        q += " AND date(created_at) >= date(?)"
        params.append(filters["date_from"].isoformat())
    if filters.get("date_to"):
        q += " AND date(created_at) <= date(?)"
        params.append(filters["date_to"].isoformat())
    q += " ORDER BY datetime(created_at) DESC"
    rows = conn.execute(q, params).fetchall()
    cols = ["id","Titel","Beschreibung","Kategorie","Autor","Erstellt am","Links"]
    df = pd.DataFrame(rows, columns=cols)
    return df

def add_update(topic_id:int, user:str, content:str):
    conn.execute("""INSERT INTO updates(topic_id,user,content,created_at)
                    VALUES(?,?,?,?)""", (topic_id, user, content, now_iso()))
    conn.commit()

def add_comment(topic_id:int, user:str, content:str):
    conn.execute("""INSERT INTO comments(topic_id,user,content,created_at)
                    VALUES(?,?,?,?)""", (topic_id, user, content, now_iso()))
    conn.commit()

def get_updates(topic_id:int):
    rows = conn.execute("SELECT user, content, created_at FROM updates WHERE topic_id=? ORDER BY datetime(created_at) DESC", (topic_id,)).fetchall()
    return rows

def get_comments(topic_id:int):
    rows = conn.execute("SELECT user, content, created_at FROM comments WHERE topic_id=? ORDER BY datetime(created_at) DESC", (topic_id,)).fetchall()
    return rows

def build_pdf(selected_ids:list[int]) -> bytes:
    # Gather data
    if not selected_ids:
        # export all
        ids = [r[0] for r in conn.execute("SELECT id FROM topics ORDER BY datetime(created_at) DESC").fetchall()]
    else:
        ids = selected_ids

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 2*cm
    y = height - margin

    def write_line(text, font="Helvetica", size=10, leading=12):
        nonlocal y
        c.setFont(font, size)
        wrapped = utils.simpleSplit(text, font, size, width - 2*margin)
        for line in wrapped:
            if y < margin + leading:
                c.showPage()
                y = height - margin
                c.setFont(font, size)
            c.drawString(margin, y, line)
            y -= leading

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, f"{APP_TITLE} – Export")
    y -= 18
    c.setFont("Helvetica", 9)
    c.drawString(margin, y, f"Erstellt am: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %Z')} | Anzahl Themen: {len(ids)}")
    y -= 16
    c.line(margin, y, width - margin, y)
    y -= 14

    for tid in ids:
        row = conn.execute("SELECT id, title, description, category, created_by, created_at, links FROM topics WHERE id=?", (tid,)).fetchone()
        if not row: continue
        (tid, title, desc, cat, author, created_at, links_json) = row

        c.setFont("Helvetica-Bold", 12)
        write_line(f"#{tid}  {title}", "Helvetica-Bold", 12, 14)
        write_line(f"Rubrik: {cat}   |   Autor: {author}   |   Eröffnung: {created_at}", "Helvetica", 9, 12)
        if desc:
            write_line("Beschreibung:", "Helvetica-Bold", 10, 12)
            write_line(desc, "Helvetica", 10, 12)
        # Links
        try:
            links = json.loads(links_json) if links_json else []
        except:
            links = []
        if links:
            write_line("Links:", "Helvetica-Bold", 10, 12)
            for l in links:
                write_line(f"• {l.get('label')}: {l.get('url')}", "Helvetica", 9, 12)
        # Updates
        ups = get_updates(tid)
        if ups:
            write_line("Updates:", "Helvetica-Bold", 10, 12)
            for u in ups:
                write_line(f"• {u[2]} – {u[0]}: {u[1]}", "Helvetica", 9, 12)
        # Kommentare
        cms = get_comments(tid)
        if cms:
            write_line("Kommentare:", "Helvetica-Bold", 10, 12)
            for cmn in cms:
                write_line(f"• {cmn[2]} – {cmn[0]}: {cmn[1]}", "Helvetica", 9, 12)
        # Separator
        y -= 6
        c.setStrokeColorRGB(0.7,0.82,0.74)
        c.line(margin, y, width - margin, y)
        y -= 16
        c.setStrokeColorRGB(0,0,0)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# ---------- Sidebar ----------
st.sidebar.title("⚙️ Einstellungen & Export")
current_user = st.sidebar.selectbox("Ich bin:", USERS, index=0)

with st.sidebar.expander("Kategorien verwalten", expanded=False):
    st.caption("Standard: " + ", ".join(DEFAULT_CATEGORIES))
    new_cat = st.text_input("Neue Kategorie hinzufügen")
    if st.button("➕ Hinzufügen", use_container_width=True):
        add_category(new_cat)
        st.success(f"Kategorie '{new_cat}' hinzugefügt.")
    cats = get_categories()
    if cats:
        del_cat = st.selectbox("Kategorie löschen", ["– Auswählen –"] + cats)
        if st.button("🗑️ Löschen", use_container_width=True, disabled=(del_cat=="– Auswählen –")):
            delete_category(del_cat)
            st.warning(f"Kategorie '{del_cat}' gelöscht. Bestehende Themen behalten die Bezeichnung ggf. bis zur Neuzuordnung.")

# Filters
with st.sidebar.expander("🔎 Filter", expanded=False):
    fcats = st.multiselect("Rubriken", options=get_categories())
    fusers = st.multiselect("Autoren", options=USERS)
    q = st.text_input("Suche (Titel/Beschreibung)")
    c1, c2 = st.columns(2)
    with c1:
        dfrom = st.date_input("Von (inkl.)", value=None)
    with c2:
        dto = st.date_input("Bis (inkl.)", value=None)
    st.session_state["_filters"] = {"categories": fcats, "users": fusers, "q": q, "date_from": dfrom or None, "date_to": dto or None}

# Export
if "selected_ids" not in st.session_state:
    st.session_state["selected_ids"] = set()

col_dl1, col_dl2 = st.sidebar.columns(2)
with col_dl1:
    if st.button("🧾 PDF export (Auswahl)"):
        pdf = build_pdf(sorted(list(st.session_state["selected_ids"])))
        st.sidebar.download_button("📥 Download Auswahl.pdf", data=pdf, file_name="themensammler_auswahl.pdf")
with col_dl2:
    if st.button("🧾 PDF export (Alle)"):
        pdf = build_pdf([])
        st.sidebar.download_button("📥 Download Alle.pdf", data=pdf, file_name="themensammler_alle.pdf")

# ---------- Main ----------
st.title(f"🌿 {APP_TITLE}")
st.markdown("""
<div class="eco-accent">
<b>Zweck:</b> Themen als Sprint-Projekte erfassen, updaten, kommentieren und selektiv/exportieren.
</div>
""", unsafe_allow_html=True)

tab_new, tab_list = st.tabs(["➕ Neues Thema", "📚 Themenübersicht"])

with tab_new:
    st.subheader("Neues Thema anlegen")

    with st.form("new_topic"):
        title = st.text_input("Titel*", placeholder="Kurzer, prägnanter Titel", max_chars=180)
        desc = st.text_area("Beschreibung", height=160, placeholder="Kurzbeschreibung, Ziel, Deliverables, To-Dos ...")
        cat = st.selectbox("Rubrik", options=get_categories())
        st.caption("Rubriken können links in den Einstellungen verwaltet werden.")
        st.markdown("**Links zum Thema (optional)**")
        # dynamic link inputs
        if "link_rows" not in st.session_state: st.session_state.link_rows = 1
        lr_cols = st.columns([3,6,2])
        with lr_cols[0]:
            label0 = st.text_input("Label 1", key="lbl_0", placeholder="z.B. Dossier, Referenz, Ticket")
        with lr_cols[1]:
            url0 = st.text_input("URL 1", key="url_0", placeholder="https://...")
        with lr_cols[2]:
            st.write("")
            if st.button("＋ Mehr Links", key="more_links"):
                st.session_state.link_rows += 1
        links = []
        for i in range(1, st.session_state.link_rows):
            c = st.columns([3,6,1])
            with c[0]:
                lbl = st.text_input(f"Label {i+1}", key=f"lbl_{i}")
            with c[1]:
                u = st.text_input(f"URL {i+1}", key=f"url_{i}")
            links.append({"label": lbl.strip() if lbl else (u.strip() if u else ""), "url": u.strip() if u else ""})
        if url0:
            links = [{"label": label0.strip() if label0 else url0.strip(), "url": url0.strip()}] + links

        submitted = st.form_submit_button("✅ Thema anlegen", use_container_width=True)
        if submitted:
            if not title.strip():
                st.error("Titel ist erforderlich.")
            elif any(l.get("url") and not valid_url(l["url"]) for l in links):
                st.error("Bitte gültige URLs mit http(s):// angeben.")
            else:
                # filter empty links
                clean_links = [l for l in links if l.get("url")]
                tid = create_topic(title.strip(), desc.strip(), cat, current_user, clean_links)
                st.success(f"Thema #{tid} angelegt von {current_user} am {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}")
                # reset link rows
                st.session_state.link_rows = 1
                for k in list(st.session_state.keys()):
                    if k.startswith("lbl_") or k.startswith("url_"):
                        del st.session_state[k]

with tab_list:
    st.subheader("Themenübersicht & Follow-ups")

    # Load data with filters
    df = list_topics(st.session_state.get("_filters", {}))
    if df.empty:
        st.info("Keine Themen gefunden. Lege ein erstes Thema an.")
    else:
        # Select all toggle
        sel_all = st.checkbox("Alle auswählen / Auswahl zurücksetzen")
        if sel_all:
            st.session_state["selected_ids"] = set(df["id"].tolist())
        else:
            # don't clear selection automatically to avoid surprise
            pass

        # Table-like rendering with expanders
        for _, row in df.iterrows():
            tid = int(row["id"])
            title = row["Titel"]
            cat = row["Kategorie"]
            author = row["Autor"]
            created_at = row["Erstellt am"]
            desc = row["Beschreibung"]
            links = []
            try:
                links = json.loads(row["Links"]) if row["Links"] else []
            except:
                links = []

            with st.expander(f"#{tid} • {title}"):
                top_cols = st.columns([1,3,2,2,2])
                with top_cols[0]:
                    checked = st.checkbox("Auswählen", key=f"sel_{tid}", value=(tid in st.session_state['selected_ids']))
                    if checked:
                        st.session_state["selected_ids"].add(tid)
                    else:
                        st.session_state["selected_ids"].discard(tid)
                with top_cols[1]:
                    st.markdown(f"**Rubrik:** {cat}")
                    # change category
                    cats_all = get_categories()
                    new_cat = st.selectbox("Rubrik ändern", options=cats_all, index=cats_all.index(cat) if cat in cats_all else 0, key=f"cat_{tid}")
                    if st.button("💾 Speichern", key=f"save_cat_{tid}"):
                        update_topic_category(tid, new_cat)
                        st.success("Rubrik aktualisiert")
                with top_cols[2]:
                    st.markdown(f"**Autor:** {author}")
                    st.caption(f"Eröffnung: {created_at}")
                with top_cols[3]:
                    st.markdown("**Links:**")
                    if links:
                        for l in links:
                            st.markdown(f"• [{l.get('label') or l.get('url')}]({l.get('url')})")
                    add_l = st.text_input("Neue URL", key=f"new_url_{tid}", placeholder="https://...")
                    add_l_lbl = st.text_input("Label", key=f"new_url_lbl_{tid}", placeholder="z.B. Ticket, Doku")
                    if st.button("➕ Link hinzufügen", key=f"btn_add_link_{tid}"):
                        if add_l and valid_url(add_l):
                            add_link_to_topic(tid, add_l, add_l_lbl or add_l)
                            st.success("Link hinzugefügt")
                        else:
                            st.error("Bitte gültige URL mit http(s):// eingeben.")
                with top_cols[4]:
                    st.markdown("**Aktionen:**")
                    if st.button("🧾 Nur dieses Thema exportieren (PDF)", key=f"exp_one_{tid}"):
                        pdf = build_pdf([tid])
                        st.download_button("📥 Download PDF", data=pdf, file_name=f"thema_{tid}.pdf", key=f"dwn_{tid}")

                st.markdown("---")
                st.markdown("**Beschreibung**")
                st.write(desc or "—")

                # Updates
                st.markdown("**Updates**")
                ups = get_updates(tid)
                if ups:
                    for u in ups:
                        st.markdown(f"- _{u[2]}_ – **{u[0]}**: {u[1]}")
                with st.form(f"form_up_{tid}", clear_on_submit=True):
                    up_txt = st.text_area("Update hinzufügen", key=f"up_txt_{tid}", height=80, placeholder="Was ist neu?")
                    if st.form_submit_button("✅ Update speichern"):
                        if up_txt.strip():
                            add_update(tid, current_user, up_txt.strip())
                            st.success("Update gespeichert.")
                        else:
                            st.error("Bitte Inhalt eingeben.")

                # Comments
                st.markdown("**Kommentare**")
                cms = get_comments(tid)
                if cms:
                    for cmt in cms:
                        st.markdown(f"- _{cmt[2]}_ – **{cmt[0]}**: {cmt[1]}")
                with st.form(f"form_cm_{tid}", clear_on_submit=True):
                    cm_txt = st.text_area("Kommentar hinzufügen", key=f"cm_txt_{tid}", height=60, placeholder="Gedanke, Frage, Hinweis ...")
                    if st.form_submit_button("💬 Kommentar speichern"):
                        if cm_txt.strip():
                            add_comment(tid, current_user, cm_txt.strip())
                            st.success("Kommentar gespeichert.")
                        else:
                            st.error("Bitte Inhalt eingeben.")

# Footer note
st.caption("© Qrauts AG – Nachhaltige Energieprojekte strukturiert steuern.")
