
try:
    from .config import Config
except ImportError:
    from config import Config
from urllib.parse import quote_plus
from pydebugger.debug import debug
import os
from jsoncolor import jprint #(https://github.com/cumulus13/jsoncolor)
from rich.console import Console
console = Console()

class ApiScrap:

    @classmethod    
    def search_api(cls, query):
        """
            Search subtitles using SubDL API3
            example output:
            {
                "results": [
                    {
                        "link": "/subtitle/sd10434/diablo",
                        "name": "Diablo",
                        "original_name": "Diablo",
                        "poster_url": "https://poster.subdl.com/poster/6uAVDyWhkXfaMo09hNpyqR0xkFp.jpg",
                        "type": "movie",
                        "year": 2016
                    },
                    {
                        "link": "/subtitle/sd1301452/diablo-guardin",
                        "name": "Diablo Guardi\u00c3\u00a1n",
                        "original_name": "Diablo Guardi\u00c3\u00a1n",
                        "poster_url": "https://poster.subdl.com/poster/5aPeosEyu2axBCRoFJ9osO4mEPo.jpg",
                        "type": "tv",
                        "year": 2018
                    }
                    ...
                ]
            }
        """
        # if not self.api_key:
        #     return []
            
        endpoint = f"{Config.api3_url}auto"
        params = {
            'query': quote_plus(query), 
        }
        
        try:
            print(f"Search through fire: {endpoint}")
            response = Config.session.get(endpoint, params=params)
            
            if response.status_code == 200:
                data = response.json()
                debug(data = data)
                if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']): jprint(data)
                if data.get('results'):
                    return data.get('results', [])
                else:
                    print("The fire did not return the results")
            else:
                print(f"API Response Code: {response.status_code}")
                if response.status_code == 422:
                    print("Error 422: invalid parameters or problematic fire fire")
                
        except Exception as e:
            print(f"Error API: {e}")
        
        return []

    @classmethod
    def print_list_api(cls, results):
        """
            Print the list of results from API3
        """
        if not results:
            print("No results found.")
            return
        
        for index, item in enumerate(results):
            name = item.get('name', 'Unknown')
            original_name = item.get('original_name', 'Unknown')
            poster_url = item.get('poster_url', '')
            year = item.get('year', 'Unknown')
            subtitle_type = item.get('type', 'Unknown')
            link = item.get('link', '')
            
            if subtitle_type == 'movie':
                console.print(f"{index + 1}. [#00FFFF]{name}[/] [#FFFF00]({year})[/] - {subtitle_type}")
            elif subtitle_type == 'tv':
                console.print(f"{index + 1}. [#FFAA00]{name}[/] [#FFFF00]({year})[/] - {subtitle_type}")
            # print(f"   Original Name: {original_name}")
            # if poster_url:
            #     print(f"   Poster URL: {poster_url}")
            # print(f"   Link: {Config.base_url}{link}\n")
        
        q = console.input("[bold #00FFFF]Enter the number of the subtitle to download:[/] ")
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
    
    