import os
import sqlite3
import logging
import requests
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

# Enpòtasyon modil yo
from news_fetcher import get_football_news
from ai_generator import generate_viral_script

app = FastAPI(title="Football Viral Bot Pro Max")

# --- KONFIGIRASYON WHATSAPP (Ranplase ak pa w si w vle notifikasyon) ---
WHATSAPP_PHONE = "509XXXXXXXX"  # Mete nimewo w
WHATSAPP_API_KEY = "XXXXXX"      # Mete API Key CallMeBot la

def voye_whatsapp(mesaj):
    if WHATSAPP_API_KEY != "XXXXXX":
        url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={mesaj}&apikey={WHATSAPP_API_KEY}"
        try: requests.get(url)
        except: print("Erè WhatsApp")

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
            # Nou pran 3 premye nouvèl yo pou n pa depase limit AI a
            for art in articles[:3]:
                context = f"Tit: {art['title']}\nDeskripsyon: {art['description']}"
                script = generate_viral_script(context)
                
                save_to_db(art['title'], art['source']['name'], art['urlToImage'], script)
                
                # Voye yon bip sou WhatsApp pou chak nouvèl
                voye_whatsapp(f"⚽ *Nouvèl Foutbòl:* {art['title']}")
                
            print("✅ Nouvèl otomatik sove!")
    except Exception as e:
        print(f"Erè nan Job: {e}")

# --- ROUTE POU RECHÈCH ---
@app.get("/search")
async def search_news(q: str = Query(...)):
    print(f"🔎 Rechèch espesifik sou: {q}")
    articles = get_football_news(query_user=q)
    
    if not articles or not isinstance(articles, list):
        return {"count": 0, "results": []}

    results = []
    for art in articles[:2]: # Nou trete sèlman 2 pou l ka rapid
        try:
            context = f"Tit: {art['title']}\nDeskripsyon: {art['description']}"
            script = generate_viral_script(context)
            save_to_db(art['title'], art['source']['name'], art['urlToImage'], script)
            results.append({
                "title": art['title'],
                "image_url": art['urlToImage'],
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
    # auto_fetch_job() # Nou ka kòmante sa pou Render pa "crash" lè l fenk limen

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
