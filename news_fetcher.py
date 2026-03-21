import requests
from datetime import datetime, timedelta

def fetch_latest_football_news(query_user=None):
    api_key = "50b2ce3fb7c84c9884325d35b53d5374"
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    # Si itilizatè a fè yon rechèch, nou itilize sa li mande a. 
    # Sinon, nou itilize gwo lis pa w la.
    if query_user:
        final_query = f"({query_user}) AND football"
    else:
        final_query = (
            "(Messi OR Ronaldo OR 'Real Madrid' OR 'FC Barcelona' OR 'Manchester United' OR "
            "'Liverpool' OR 'Bayern Munich' OR 'PSG' OR 'Manchester City' OR 'Arsenal' OR "
            "'Premier League' OR 'La Liga' OR 'Serie A' OR 'Bundesliga' OR 'Ligue 1' OR "
            "'Champions League') AND football"
        )
    
    url = f"https://newsapi.org/v2/everything?q={final_query}&from={yesterday}&language=fr&sortBy=publishedAt&apiKey={api_key}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' 
        data = response.json()
        
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            # Netwaye rezilta yo
            return [a for a in articles if a.get("title") and "handball" not in a.get("title").lower()]
        return []
    except Exception as e:
        print(f"Erè NewsAPI: {e}")
        return []