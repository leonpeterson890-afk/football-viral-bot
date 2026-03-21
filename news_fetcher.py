import requests
from datetime import datetime, timedelta
import os

def get_football_news(query_user=None):
    # Kle API a
    api_key = os.getenv("NEWS_API_KEY", "50b2ce3fb7c84c9884325d35b53d5374")
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    # LIS 17 KLÈB YO
    klèb_yo = (
        "'Manchester City' OR 'Real Madrid' OR 'Bayern Munich' OR 'FC Barcelona' OR "
        "'Liverpool' OR 'Arsenal' OR 'PSG' OR 'Inter Milan' OR 'AC Milan' OR "
        "'Juventus' OR 'Atletico Madrid' OR 'Napoli' OR 'Borussia Dortmund' OR "
        "'Manchester United' OR 'Chelsea' OR 'Marseille' OR 'Lyon'"
    )
    
    if query_user:
        final_query = f"({query_user}) AND football"
    else:
        final_query = f"({klèb_yo}) AND (football OR soccer)"
    
    url = f"https://newsapi.org/v2/everything?q={final_query}&from={yesterday}&language=fr&sortBy=publishedAt&pageSize=15&apiKey={api_key}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' 
        data = response.json()
        
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            
            # NOU PRAL VOYE YON LIS ATIK KI PWÒP
            cleaned_list = []
            for a in articles:
                title = a.get("title", "")
                if title and "handball" not in title.lower():
                    # Nou rebati yon ti diksyonè pwòp pou main.py ka li l ak .get()
                    cleaned_list.append({
                        "title": title,
                        "description": a.get("description", ""),
                        "urlToImage": a.get("urlToImage", ""),
                        "source": a.get("source", {"name": "NewsAPI"})
                    })
            
            return cleaned_list # Sa a se yon LIS, li p ap bay erè 'str' ankò
        return []
    except Exception as e:
        print(f"Erè NewsAPI: {e}")
        return []
