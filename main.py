import os
import sqlite3
import logging
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

# Enpòtasyon modil ou yo
from news_fetcher import fetch_latest_football_news
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
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            conn.close()
        except sqlite3.DatabaseError:
            print("⚠️ Vye database la gate, m ap efasé l...")
            try: os.remove(db_path)
            except: pass

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
        print(f"❌ Erè Grav DB: {e}")

def save_to_db(title, source, img, scripts):
    try:
        conn = sqlite3.connect('football.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO news (title, source, image_url, scripts_multilingue) VALUES (?, ?, ?, ?)",
                       (title, source, img, scripts))
        conn.commit()
        conn.close()
    except: pass

# 3. TRAVAY OTOMATIK
def auto_fetch_job():
    print("🔄 Robot ap chèche nouvèl jeneral...")
    try:
        articles = fetch_latest_football_news() # Sèvi ak lis Messi/Ronaldo a
        if articles:
            for article in articles[:3]:
                script = generate_viral_script(article)
                save_to_db(article.get("title"), article.get("source", {}).get("name"), article.get("urlToImage"), script)
            print("✅ Nouvèl otomatik sove!")
    except Exception as e:
        print(f"Erè nan Job: {e}")

# --- NOUVO: ROUTE POU RECHÈCH ---
@app.get("/search")
async def search_news(q: str = Query(...)):
    """Route sa a pèmèt ou tape nan navigatè a: /search?q=Mbappe"""
    print(f"🔎 Rechèch espesifik sou: {q}")
    articles = fetch_latest_football_news(query_user=q)
    results = []
    
    # Nou pran 2 nouvèl sou sa w mande a epi AI ap travay sou yo rapid
    for a in articles[:2]:
        try:
            script = generate_viral_script(a)
            # Nou sove l tou nan history a pou w ka jwenn li nan GUI a pita
            save_to_db(a.get("title"), a.get("source", {}).get("name"), a.get("urlToImage"), script)
            results.append({
                "title": a.get("title"),
                "image_url": a.get("urlToImage"),
                "scripts_multilingue": script
            })
        except: continue
    return {"count": len(results), "results": results}

# Scheduler la
scheduler = BackgroundScheduler()
scheduler.add_job(auto_fetch_job, 'interval', minutes=30)
scheduler.start()

@app.on_event("startup")
def startup_event():
    init_db()
    auto_fetch_job()

# 4. ROUTES
@app.get("/gui")
async def get_ui():
    return FileResponse("index.html")

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
    return {"status": "online", "gui_url": "/gui"}