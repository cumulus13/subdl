import sys
import os
import argparse
from make_colors import make_colors
from pydebugger.debug import debug
from rich.console import Console
from configset import configset
from pathlib import Path
import requests
from bs4 import BeautifulSoup as bs
import re
from rich.pretty import pprint
from jsoncolor import jprint
try:
    from .downloader import Downloader as downloader
except ImportError:
    from downloader import Downloader as downloader
import argparse


console = Console()

class Subdl:
    
    CONFIGFILE = str(Path(__file__).parent / 'subdl.ini')
    CONFIG = configset(CONFIGFILE)
    OURL = "https://subdl.com/"
    DURL = "https://dl.subdl.com"
    URL = "https://api.subdl.com/"
    SESS = requests.Session()
    API_KEY = CONFIG.get_config('api', 'key', 'zUjcID8DcqKffRNVe43bc3y8byfCSRmn') or 'zUjcID8DcqKffRNVe43bc3y8byfCSRmn'
    
    
    @classmethod
    def search(self, query, download_path = None, copy_to_clipboard = False):
        
        data = []
        
        url = self.URL + "api/v1/subtitles"
        params = {
            'film_name': query,
            'api_key': self.API_KEY,
            'languages': self.CONFIG.get_config('lang', 'names', 'ID') or 'ID',
        }
        a = self.SESS.get(url, params = params)
        content = a.json()
        debug(content = content)
        jprint(content)
        
        if content.get('status') and content.get('results'):
            console.print(f"[cyan b]Found[/cyan b] [white bold u]{len(content.get('results'))}[/white bold u]")
            langs = list(set([i.get('lang') for i in content.get('subtitles')]))
            debug(langs = langs)
            
            n = 1
            for lang in langs:
                console.print(f"- [#ffaa00 bold]{lang}[/#ffaa00 bold] [#ff00ff bold]{'(complete)' if str(lang).islower() else ''}")
                for s in list(filter(lambda k: k.get('lang') == lang, content.get('subtitles'))):
                    data.append(s)
                    console.print(f"[cyan bold]{n: 03}.[/cyan bold] [yellow bold]{s.get('name')}[/yellow bold]")
                    n += 1
                    
            sub_selected = input(make_colors("select number to download:", 'lw', 'bl') + " ")
            debug(sub_selected = sub_selected)
            if sub_selected:
                if sub_selected.isdigit():
                    if int(sub_selected) <= len(data):
                        link = data[int(sub_selected) - 1].get("url")
                        name = data[int(sub_selected) - 1].get("name")
                        debug(link = link)
                        debug(name = name)
                        download_link = self.DURL + link
                        debug(download_link = download_link)
                        #https://dl.subdl.com/subtitle/3392476-8315610
                        downloader.downloader(download_link, copy_to_clipboard, name, copyurl_only = copy_to_clipboard) if link else console.print("[white on red bold blink]No Download link FOUND ![/]")
                        
                elif sub_selected.lower() in ('q', 'x', 'exit', 'quit'):
                    console.print("[#ff007f bold blink]Exit ....[/#ff007f bold blink]")
                    sys.exit(0)
                
    @classmethod
    def usage(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('MOVIE', help = "Search movie name", action = 'store', nargs = '*')
        parser.add_argument("-p", "--path", help = "Save download to directory", action = 'store')
        parser.add_argument('-c', '--clip', help = 'Just copy link download, don"t download', action = 'store_true')
        
        if len(sys.argv) == 1:
            parser.print_help()
        else:
            args = parser.parse_args()
            if os.path.isdir(args.MOVIE):
                download_path = args.MOVIE
            else:
                download_path = args.path
            query = os.path.basename(" ".join(args.MOVIE))
            debug(query = query)
            query = re.sub("\(\d{0,4}\)", "", query)
            debug(query = query)
            debug(download_path = download_path)
            self.search(query.strip(), download_path, args.clip)
        
    
if __name__ == '__main__':
    Subdl.usage()
    
        