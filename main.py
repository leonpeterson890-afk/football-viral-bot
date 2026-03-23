import os
import sqlite3
import logging
import requests
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

# Enpòtasyon modil ou yo (Asire w yo nan menm folder a)
try:
    from news_fetcher import get_football_news
    from ai_generator import generate_viral_script
except ImportError as e:
    print(f"❌ ERÈ ENPÒTASYON: Manke yon fichye .py! {e}")

app = FastAPI(title="Football Viral Bot Pro Max")

# 1. SEKIRITE (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. DATABASE (Amelyore pou montre erè)
def init_db():
    db_path = 'football.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE, 
                source TEXT,
                image_url TEXT,
                scripts_multilingue TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ DATABASE PARE E OPERASYONÈL!")
    except Exception as e:
        print(f"❌ ERÈ KRITIK DB: {e}")

def save_to_db(title, source, img, scripts):
    try:
        conn = sqlite3.connect('football.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO news (title, source, image_url, scripts_multilingue) VALUES (?, ?, ?, ?)",
                       (title, str(source), img, scripts))
        if cursor.rowcount > 0:
            print(f"💾 Sove nan DB: {title[:30]}...")
        else:
            print(f"ℹ️ Tit sa egziste deja, mwen pa double l: {title[:30]}...")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ ERÈ NAN SOVE DB: {e}")

# 3. TRAVAY OTOMATIK (Job)
def auto_fetch_job():
    print("🔄 [JOB] Robot ap chèche nouvèl otomatik...")
    try:
        articles = get_football_news() 
        if articles and isinstance(articles, list):
            print(f"🔎 [JOB] Jwenn {len(articles)} nouvèl fre.")
            for art in articles[:3]:
                context = f"Tit: {art.get('title')}\nDeskripsyon: {art.get('description')}"
                script = generate_viral_script(context)
                save_to_db(art.get('title'), art.get('source', {}).get('name'), art.get('urlToImage'), script)
        else:
            print("⚠️ [JOB] API a pa tounen okenn nouvèl.")
    except Exception as e:
        print(f"❌ ERÈ NAN JOB OTOMATIK: {e}")

# --- ROUTE POU RECHÈCH (Sa bouton Fresh News la itilize) ---
@app.get("/search")
async def search_news(q: str = Query(...)):
    print(f"🔎 RECHÈCH MANYÈL: {q}")
    try:
        articles = get_football_news(query_user=q)
        
        if not articles or not isinstance(articles, list):
            print("⚠️ API a pa bay anyen pou rechèch sa.")
            return {"count": 0, "results": [], "message": "Pa gen nouvèl jwenn"}

        results = []
        for art in articles[:3]: 
            try:
                title = art.get('title')
                desc = art.get('description', '')
                img = art.get('urlToImage')
                source_name = art.get('source', {}).get('name', 'News')

                print(f"🤖 AI ap trete: {title[:40]}...")
                script = generate_viral_script(f"Tit: {title}\nDeskripsyon: {desc}")
                
                save_to_db(title, source_name, img, script)
                
                results.append({
                    "title": title,
                    "image_url": img,
                    "scripts_multilingue": script,
                    "source": source_name
                })
            except Exception as ai_err:
                print(f"❌ Erè nan trete yon atik: {ai_err}")
                continue
        
        return {"count": len(results), "results": results}
    except Exception as e:
        print(f"❌ Erè jeneral nan /search: {e}")
        return {"count": 0, "results": [], "error": str(e)}

# 4. ROUTES POU UI
@app.get("/gui")
async def get_ui():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "index.html manke!", "files": os.listdir(".")}

@app.get("/history")
async def get_history(limit: int = 15):
    try:
        conn = sqlite3.connect('football.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM news ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return {"results": [dict(row) for row in rows]}
    except Exception as e:
        print(f"❌ Erè nan chaje istwa: {e}")
        return {"results": [], "error": str(e)}

@app.get("/")
async def root():
    return {"status": "online", "gui": "/gui"}

# SCHEDULER (Ranje pou Render pa bloke l)
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(auto_fetch_job, 'interval', minutes=30)
scheduler.start()

@app.on_event("startup")
async def startup_event():
    init_db()
    # Opsyonèl: Ou ka de-kòmante liy anba a pou l chèche nouvèl menm kote l limen an
    # auto_fetch_job()
