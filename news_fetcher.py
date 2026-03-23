import requests
from datetime import datetime, timedelta
import os

def get_football_news(query_user=None):
    # 1. Kle API a (Tcheke si OS env la la, sinon itilize kle default la)
    api_key = os.getenv("NEWS_API_KEY", "50b2ce3fb7c84c9884325d35b53d5374")
    
    # Nou gade nouvèl depi 2 jou de sa
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    # 2. LIS 17 KLÈB YO (Pou rechèch otomatik)
    klèb_yo = (
        "(Manchester City OR Real Madrid OR Bayern Munich OR FC Barcelona OR "
        "Liverpool OR Arsenal OR PSG OR Inter Milan OR AC Milan OR "
        "Juventus OR Atletico Madrid OR Napoli OR Borussia Dortmund OR "
        "Manchester United OR Chelsea OR Marseille OR Lyon)"
    )
    
    # 3. KONSTRIKSYON RECHÈCH LA
    if query_user and query_user.strip():
        # Si itilizatè a tape yon bagay nan bwat rechèch la
        final_query = f"({query_user}) AND (football OR soccer)"
    else:
        # Si se robo a k ap travay pou kont li
        final_query = f"{klèb_yo} AND (football OR soccer)"
    
    # Nou itilize lang fr ak en pou n gen plis chans jwenn nouvèl fre
    url = f"https://newsapi.org/v2/everything?q={final_query}&from={yesterday}&language=fr&sortBy=publishedAt&pageSize=15&apiKey={api_key}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' 
        data = response.json()
        
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            
            # 4. NETWAYAJ LIS LA (Pou voye yon LIS diksyonè bay main.py)
            cleaned_list = []
            for a in articles:
                title = a.get("title")
                # Filtre atik ki pa gen tit oswa ki pa foutbòl (ex: handball)
                if title and "handball" not in title.lower():
                    cleaned_list.append({
                        "title": title,
                        "description": a.get("description", ""),
                        "urlToImage": a.get("urlToImage", ""),
                        "source": a.get("source", {"name": "NewsAPI"})
                    })
            
            print(f"✅ {len(cleaned_list)} nouvèl jwenn sou NewsAPI.")
            return cleaned_list 
            
        else:
            print(f"⚠️ Erè NewsAPI: {data.get('message')}")
            return []

    except Exception as e:
        print(f"❌ Erè koneksyon NewsAPI: {e}")
        return []
