import requests
from datetime import datetime, timedelta
import os

def get_football_news(query_user=None):
    # Nou pran kle API a nan Environment Render la (oswa nou kite sa w te genyen an)
    api_key = os.getenv("NEWS_API_KEY", "50b2ce3fb7c84c9884325d35b53d5374")
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    # LIS KLÈB OU TE MANDE YO (SÈLMAN SA YO)
    klèb_yo = (
        "'Manchester City' OR 'Real Madrid' OR 'Bayern Munich' OR 'FC Barcelona' OR "
        "'Liverpool' OR 'Arsenal' OR 'PSG' OR 'Inter Milan' OR 'AC Milan' OR "
        "'Juventus' OR 'Atletico Madrid' OR 'Napoli' OR 'Borussia Dortmund' OR "
        "'Manchester United' OR 'Chelsea' OR 'Marseille' OR 'Lyon'"
    )
    
    # Si itilizatè a tape yon bagay espesifik, n ap itilize li. Sinon, n ap pran lis la.
    if query_user:
        final_query = f"({query_user}) AND football"
    else:
        final_query = f"({klèb_yo}) AND (football OR soccer)"
    
    # Nou chèche nouvèl yo an Fransè, soti nan de jou de sa pou rive jodi a
    url = f"https://newsapi.org/v2/everything?q={final_query}&from={yesterday}&language=fr&sortBy=publishedAt&pageSize=15&apiKey={api_key}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' 
        data = response.json()
        
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            # Netwaye rezilta yo: retire sa ki pa gen tit oswa ki pa foutbòl
            cleaned_articles = []
            for a in articles:
                title = a.get("title", "")
                desc = a.get("description", "")
                if title and "handball" not in title.lower():
                    # Nou fòme yon ti tèks senp pou AI a ka travay pi byen
                    cleaned_articles.append(f"⚽ {title}: {desc}")
            
            # Nou voye tout tèks la bay AI a (kole yo ansanm)
            return "\n\n".join(cleaned_articles)
        return ""
    except Exception as e:
        print(f"Erè NewsAPI: {e}")
        return ""
