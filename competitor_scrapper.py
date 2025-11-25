import requests
from bs4 import BeautifulSoup

def analyze_competitors(urls):
    analysis = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string if soup.title else "No title"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        analysis.append({
            "url": url,
            "title": title,
            "meta_description": meta_desc["content"] if meta_desc else "None"
        })
    return analysis