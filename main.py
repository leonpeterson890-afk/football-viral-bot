import os
import sqlite3
import logging
import requests
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

# Enpòtasyon modil ou yo
from news_fetcher import get_football_news
from ai_generator import generate_viral_script

app = FastAPI(title="Football Viral Bot Pro Max")

# 1. SEKIRITE (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. DATABASE
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
        print("✅ DATABASE PARE!")
    except Exception as e:
        print(f"❌ Erè DB: {e}")

def save_to_db(title, source, img, scripts):
    try:
        conn = sqlite3.connect('football.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO news (title, source, image_url, scripts_multilingue) VALUES (?, ?, ?, ?)",
                       (title, str(source), img, scripts))
        conn.commit()
        conn.close()
    except: pass

# 3. TRAVAY OTOMATIK
def auto_fetch_job():
    print("🔄 Robot ap chèche nouvèl pou klèb ou yo...")
    try:
        articles = get_football_news() 
        if articles and isinstance(articles, list):
            # Nou trete 3 nouvèl sèlman pou evite "Time Out" sou Render
            for art in articles[:3]:
                context = f"Tit: {art.get('title')}\nDeskripsyon: {art.get('description')}"
                script = generate_viral_script(context)
                save_to_db(art.get('title'), art.get('source', {}).get('name'), art.get('urlToImage'), script)
            print("✅ Nouvèl otomatik sove!")
    except Exception as e:
        print(f"Erè nan Job: {e}")

# --- ROUTE POU RECHÈCH (Sa bouton Fresh News la itilize) ---
@app.get("/search")
async def search_news(q: str = Query(...)):
    print(f"🔎 Rechèch espesifik sou: {q}")
    articles = get_football_news(query_user=q)
    
    if not articles or not isinstance(articles, list):
        return {"count": 0, "results": []}

    results = []
    for art in articles[:3]: 
        try:
            context = f"Tit: {art.get('title')}\nDeskripsyon: {art.get('description')}"
            script = generate_viral_script(context)
            save_to_db(art.get('title'), art.get('source', {}).get('name', 'News'), art.get('urlToImage'), script)
            results.append({
                "title": art.get('title'),
                "image_url": art.get('urlToImage'),
                "scripts_multilingue": script
            })
        except: continue
        
    return {"count": len(results), "results": results}

# 4. ROUTES POU PAJ YO
@app.get("/gui")
async def get_ui():
    # Verifikasyon si fichye a la tout bon vre pou evite "Not Found"
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "Fichye index.html la manke nan folder a!", "files_found": os.listdir(".")}

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
        return {"results": [], "error": str(e)}

@app.get("/")
async def root():
    return {
        "status": "online", 
        "message": "Robot a ap mache byen!",
        "paj_la": "/gui"
    }

# Scheduler la
scheduler = BackgroundScheduler()
scheduler.add_job(auto_fetch_job, 'interval', minutes=30)
scheduler.start()

@app.on_event("startup")
def startup_event():
    init_db()
