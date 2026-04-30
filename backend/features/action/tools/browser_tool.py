import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

class BrowserTool:
    """
    TITUS Digital Sense: The Web Sensing Tool.
    Used by agents to research the internet and extract data.
    """
    
    @staticmethod
    def search(query, max_results=5):
        """Performs a deep-sensing search on the web."""
        print(f"[*] BrowserTool: Searching for '{query}'...")
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=max_results)]
                return {"status": "SUCCESS", "results": results}
        except Exception as e:
            return {"status": "ERROR", "msg": str(e)}

    @staticmethod
    def scrape_url(url):
        """Scrapes the content of a specific webpage."""
        print(f"[*] BrowserTool: Scrapping content from {url}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extract paragraphs and meaningful text
            paragraphs = [p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3'])]
            content = "\n".join(paragraphs).strip()
            
            if len(content) < 50:
                return {"status": "ERROR", "msg": "Insufficient content extracted."}
                
            return {"status": "SUCCESS", "content": content[:10000]} # Limit to 10k chars for LLM safety
        except Exception as e:
            return {"status": "ERROR", "msg": str(e)}
            
if __name__ == "__main__":
    tool = BrowserTool()
    res = tool.search("TITUS AI Agent")
    print(res)
