import requests

def get_market_news():
    url = "https://newsapi.org/v2/top-headlines?category=business&apiKey=YOUR_NEWS_API"

    res = requests.get(url).json()

    news_list = [article['title'] for article in res['articles'][:5]]

    return news_list