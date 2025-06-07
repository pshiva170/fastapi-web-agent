import httpx
from bs4 import BeautifulSoup

async def scrape_homepage_content(url: str) -> str:
    """
    Asynchronously scrapes the text content from a website's homepage.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
                script_or_style.decompose()

            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit content size to avoid overly large LLM context
            max_chars = 12000
            return text[:max_chars]

        except httpx.RequestError as e:
            raise Exception(f"Error fetching URL {url}: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred during scraping: {e}")
