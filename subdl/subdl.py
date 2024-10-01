#!/usr/bin/env python3
#coding:utf-8
"""
  Author:  cumulus13 --<cumulus13@gmail.com>
  Purpose: SubDL.com downloader
  Created: 07/26/24
"""

import sys
import os
import argparse
from make_colors import make_colors
from pydebugger.debug import debug
from rich.console import Console
from configset import configset
from pathlib import Path
import requests
import re
from rich.pretty import pprint
if os.getenv('DEBUG') == '1' or os.getenv('DEBUG_SERVER'):
    from jsoncolor import jprint
try:
    from .downloader import Downloader as downloader
except ImportError:
    from downloader import Downloader as downloader
import argparse
try:
    from .langcode import CODE
except ImportError:
    from langcode import CODE

console = Console()

class Subdl:

    CONFIGFILE = str(Path(__file__).parent / 'subdl.ini')
    CONFIG = configset(CONFIGFILE)
    OURL = "https://subdl.com/"
    DURL = "https://dl.subdl.com"
    URL = "https://api.subdl.com/"
    SESS = requests.Session()
    API_KEY = CONFIG.get_config('api', 'key', 'zUjcID8DcqKffRNVe43bc3y8byfCSRmn') or 'zUjcID8DcqKffRNVe43bc3y8byfCSRmn'
    PARAMS = {}

    @classmethod
    def search(self, query, download_path = None, copy_to_clipboard = False, languages = ""):

        data = []

        url = self.URL + "api/v1/subtitles"
        params = {
            'film_name': query,
            'api_key': self.API_KEY,
            'languages': languages or self.CONFIG.get_config('lang', 'names', 'ID') or 'ID',
        }
        
        self.PARAMS.update(params)
        
        debug(params = params)
        debug(self_params = self.PARAMS)
        debug(url = url)
        a = self.SESS.get(url, params = self.PARAMS)
        content = a.json()
        debug(content = content)
        if os.getenv('DEBUG') == '1' or os.getenv('DEBUG_SERVER'): jprint(content)
        langs = []
        #index_movie = 0

        if content.get('status') and content.get('results'):
            if content.get('subtitles'):
                console.print(f"[cyan b]Found[/cyan b] [white bold u]{len(content.get('results'))}[/white bold u]")
                langs = list(set([i.get('lang') for i in content.get('subtitles')]))
                debug(langs = langs)
            m = 1
            if len(content.get('results')) > 1:
                for movie in content.get('results'):                
                    console.print(f"[cyan bold]{m: 03}.[/] [#55ff00 bold]{movie.get('name')}[/#55ff00 bold] [#ff00ff bold]")
                    m += 1                

                movie_selected = input(make_colors("select number to download:", 'lw', 'm') + " ")
                if movie_selected:
                    if movie_selected.isdigit():
                        if int(movie_selected) <= len(content.get('results')):
                            #index_movie = movie_selected - 1
                            params1 = params
                            if content.get('results')[int(movie_selected) - 1].get('name'):
                                params1.update({'film_name': content.get('results')[int(movie_selected) - 1].get('name'),})
                            if content.get('results')[int(movie_selected) - 1].get('imdb_id'):
                                params1.update({'imdb_id': content.get('results')[int(movie_selected) - 1].get('imdb_id'),})
                            if content.get('results')[int(movie_selected) - 1].get('tmdb_id'):
                                params1.update({'tmdb_id': content.get('results')[int(movie_selected) - 1].get('tmdb_id'),})
                            if content.get('results')[int(movie_selected) - 1].get('sd_id'):
                                params1.update({'sd_id': content.get('results')[int(movie_selected) - 1].get('sd_id'),})
                            if content.get('results')[int(movie_selected) - 1].get('type'):
                                params1.update({'type': content.get('results')[int(movie_selected) - 1].get('type'),})
                            if content.get('results')[int(movie_selected) - 1].get('year'):
                                params1.update({'year': content.get('results')[int(movie_selected) - 1].get('year'),})
                            debug(params1 = params1)
                            a = self.SESS.get(url, params = params1)
                            content = a.json()
                            debug(content = content)
                            if os.getenv('DEBUG') == '1' or os.getenv('DEBUG_SERVER'): jprint(content)
                    elif movie_selected.lower() in ('q', 'x', 'exit', 'quit'):
                        console.print("[#ff007f bold blink]Exit ....[/#ff007f bold blink]")
                        sys.exit(0)
            
            debug(content_get_subtitles = content.get('subtitles'))
            
            if content.get('subtitles'):
                if not langs:
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
                            downloader.downloader(download_link, download_path, name, copyurl_only = copy_to_clipboard) if link else console.print("[white on red bold blink]No Download link FOUND ![/]")
                    elif "," in sub_selected:
                        list_number_selected = [i.strip() for i in sub_selected.split(",")]
                        debug(list_number_selected = list_number_selected)
                        list_number_selected = list(filter(lambda k: k.strip().isdigit(), list_number_selected))
                        debug(list_number_selected = list_number_selected)
                        for s in list_number_selected:
                            if int(s) <= len(data):
                                link = data[int(s) - 1].get("url")
                                name = data[int(s) - 1].get("name")
                                debug(link = link)
                                debug(name = name)
                                download_link = self.DURL + link
                                debug(download_link = download_link)
                                #https://dl.subdl.com/subtitle/3392476-8315610
                                downloader.downloader(download_link, download_path, name, copyurl_only = copy_to_clipboard) if link else console.print("[white on red bold blink]No Download link FOUND ![/]")                        
    
                    elif " " in sub_selected:
                        list_number_selected = [i.strip() for i in sub_selected.split(" ")]
                        debug(list_number_selected = list_number_selected)
                        list_number_selected = list(filter(lambda k: k.strip().isdigit(), list_number_selected))
                        debug(list_number_selected = list_number_selected)
                        for s in list_number_selected:
                            if int(s) <= len(data):
                                link = data[int(s) - 1].get("url")
                                name = data[int(s) - 1].get("name")
                                debug(link = link)
                                debug(name = name)
                                download_link = self.DURL + link
                                debug(download_link = download_link)
                                #https://dl.subdl.com/subtitle/3392476-8315610
                                downloader.downloader(download_link, download_path, name, copyurl_only = copy_to_clipboard) if link else console.print("[white on red bold blink]No Download link FOUND ![/]")                                            
                    elif sub_selected.lower() in ('q', 'x', 'exit', 'quit'):
                        console.print("[#ff007f bold blink]Exit ....[/#ff007f bold blink]")
                        sys.exit(0)
            else:
                console.print("[white on red bold blink]No Subtitle FOUND ![/]")
                sys.exit(0)
    @classmethod
    def usage(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('MOVIE', help = "Search movie name or directory name, directory example: C:\MOVIES\Avatar (2023)", action = 'store', nargs = '*')
        parser.add_argument("-p", "--path", help = "Save download to directory", action = 'store')
        parser.add_argument('-c', '--clip', help = 'Just copy link download, don"t download', action = 'store_true')
        parser.add_argument("-l", '--langs', help = f'Languages, default is "{self.CONFIG.get_config("lang", "names") or "ID"}", from configfile "subdl.ini", format: "en,english,id,indonesia,jp,japan". use code lang or lang long name', nargs = '*')

        if len(sys.argv) == 1:
            parser.print_help()
        else:
            args = parser.parse_args()
            if args.MOVIE == ["."]:
                args.MOVIE = [os.getcwd()]
            langs = []
            if args.langs:
                for l in args.langs:
                    debug(l = l)
                    debug(CODE_get_l = CODE.get(l))
                    debug(check_lang = list(filter(lambda k: CODE.get(k).lower() == l.lower(), CODE)))
                    if (len(l) < 5 or "-" in l) and not str(l).isdigit() and CODE.get(l):
                        langs.append(l.lower())
                        debug(langs = langs)
                    elif len(l) > 5 and not "-" in l and list(filter(lambda k: CODE.get(k).lower() == l.lower(), CODE)):
                        debug(lang =  l)
                        debug(check_lang = list(filter(lambda k: CODE.get(k).lower() == l.lower(), CODE)))
                        try:
                            if list(filter(lambda k: CODE.get(k).lower() == l.lower(), CODE)): langs.append(list(filter(lambda k: CODE.get(k).lower() == l.lower(), CODE))[0])
                        except:
                            pass
                    elif list(filter(lambda k: CODE.get(k).lower() == l.lower(), CODE)):
                        debug(lang =  l)
                        debug(check_lang = list(filter(lambda k: CODE.get(k).lower() == l.lower(), CODE)))
                        try:
                            if list(filter(lambda k: CODE.get(k).lower() == l.lower(), CODE)): langs.append(list(filter(lambda k: CODE.get(k).lower() == l.lower(), CODE))[0])
                        except:
                            pass                        
                    else:
                        if CODE.get(l): langs.append(CODE.get(l))

            debug(langs = langs)

            languages = ",".join(langs) if langs else None

            debug(languages = languages)

            query = os.path.basename(" ".join(args.MOVIE))
            debug(query = query)
            if os.path.isdir(os.path.abspath(query.strip())):
                download_path = os.path.abspath(query.strip())
                debug("query download path is Directory [1]", download_path = download_path)
            elif os.path.isdir(os.path.realpath(query.strip())):
                download_path = os.path.realpath(query.strip())
                debug("query download path is Directory [2]", download_path = download_path)
            else:
                download_path = args.path
                debug(download_path = download_path)
            
            year = re.findall("\((\d{0,4})\)", query)
            if year:
                self.PARAMS.update({'year': year[0],})
            query = re.sub("\(\d{0,4}\)", "", query)
            debug(query = query)
            debug(download_path = download_path)
            self.search(query.strip(), download_path, args.clip, languages)


if __name__ == '__main__':
    Subdl.usage()

