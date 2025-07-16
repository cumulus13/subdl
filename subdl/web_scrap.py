
try:
    from .config import Config
except ImportError:
    from config import Config
from urllib.parse import quote_plus
from pydebugger.debug import debug
import os
from rich.console import Console
console = Console()

class WebScrap:
    
    @classmethod
    def search_web(cls, query):
        """
            Finding Subtitles Using Web Scraping
            This method scrapes the subdl.com website to find subtitles for a given query.
        """
        url = f"{Config.base_url}/search/{quote_plus(query)}"
        debug(url = url)
        try:
            response = Config.session.get(url)
            debug(status_code = response.status_code)
            if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']):
                with open('subdl_search.html', 'wb') as f:
                    f.write(response.content)
            if response.status_code == 200:
                results = object._parse_html_results(response.content)
                if results:
                    return results
            else:
                console.print(f"HTTP {response.status_code} for {url}")
                
        except Exception as e:
            console.print(f"Error accessing {url}: {e}")
        
        return []

    @classmethod
    def print_list_web(cls, results):
        """
            Print the list of results from web search
            This method is not implemented yet.
        """
        print("Web search results:")
        results = results.get('props', {}).get('pageProps', {}).get('list', [])
        for index, item in enumerate(results):
            debug(item = item)
            name = item.get('name', 'Unknown')
            original_name = item.get('original_name', 'Unknown')
            poster_url = item.get('poster_url', '')
            year = item.get('year', 'Unknown')
            subtitle_type = item.get('type', 'Unknown')
            link = item.get('link', '')
            
            print(f"{index + 1}. {name} ({year}) - {subtitle_type}")
            # print(f"   Original Name: {original_name}")
            # if poster_url:
            #     print(f"   Poster URL: {poster_url}")
            # print(f"   Link: {Config.base_url}{link}\n")
        
        q = input("Enter the number of the subtitle to download: ")
        if q and q.lower() in ['x', 'exit', 'q', 'quit']:
            print("Exiting...")
            return None
        try:
            index = int(q) - 1
            if 0 <= index < len(results):
                selected_item = results[index]
                return selected_item
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")
            
        return None
    