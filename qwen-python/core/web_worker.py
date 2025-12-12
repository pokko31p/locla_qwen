import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

WEB_AVAILABLE = True

def fetch_web_context(query: str, max_results: int = 4, max_chars: int = 4000) -> str:
    """
    Поиск через DuckDuckGo HTML (стабильный метод без API ключей).
    Возвращает качественные сниппеты.
    """
    q = (query or "").strip()
    if not q: return ""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    parts = []
    
    try:
        # Используем html.duckduckgo.com - он дает нормальные заголовки и описания
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(q)}"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Ищем результаты
            results = soup.find_all("div", class_="result", limit=max_results)
            
            for i, res in enumerate(results):
                # Извлекаем заголовок
                title_tag = res.find("a", class_="result__a")
                if not title_tag: continue
                title = title_tag.get_text(strip=True)
                href = title_tag.get("href", "")
                
                # Извлекаем описание (сниппет)
                snippet_tag = res.find("a", class_="result__snippet")
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                
                if title and snippet:
                    parts.append(f"[Источник {i+1}]: {title}\nСсылка: {href}\nИнформация: {snippet}\n")
    except Exception as e:
        print(f"Web Error: {e}")

    # Если DuckDuckGo не сработал, пробуем Wikipedia как резерв
    if not parts:
        try:
            api = "https://ru.wikipedia.org/w/api.php"
            params = {
                "action": "opensearch",
                "search": q,
                "limit": 3,
                "namespace": 0,
                "format": "json"
            }
            r = requests.get(api, params=params, headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                # data[1] - заголовки, data[2] - описания, data[3] - ссылки
                if len(data) > 3:
                    for i in range(len(data[1])):
                        parts.append(f"[Wiki {i+1}]: {data[1][i]}\n{data[2][i]}\nСсылка: {data[3][i]}\n")
        except: pass

    result_text = "\n".join(parts)
    if len(result_text) > max_chars:
        result_text = result_text[:max_chars] + "..."
        
    return result_text