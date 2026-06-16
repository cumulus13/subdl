#!/usr/bin/env python3
"""
Subdl.com Scraper Subtitles 
Script to search and download subtitles from subdl.com 
Using a scraping web and fire (if there is a fire key)
"""

import sys
from ctraceback import CTraceback
sys.excepthook = CTraceback(local=False)
import os
import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from pydebugger.debug import debug
from rich_argparse import RichHelpFormatter, _lazy_rich as rr
from typing import ClassVar
from rich.console import Console
from configset import configset
from pathlib import Path
import json5
from jsoncolor import jprint

console = Console()
CONFIGFILE = str(Path(__file__).parent / Path(__file__).stem) + '.ini'
CONFIG = configset(CONFIGFILE)

try:
    from .config import Config
except ImportError:
    from config import Config

try:
    from .web_scrap import WebScrap
except ImportError:
    from web_scrap import WebScrap

try:
    from .api_scrap import ApiScrap
except ImportError:
    from api_scrap import ApiScrap
        
class CustomRichHelpFormatter(RichHelpFormatter):
    """A custom RichHelpFormatter with modified styles."""

    styles: ClassVar[dict[str, rr.StyleType]] = {
        "argparse.args": "bold #FFFF00",  # Changed from cyan
        "argparse.groups": "#AA55FF",   # Changed from dark_orange
        "argparse.help": "bold #00FFFF",    # Changed from default
        "argparse.metavar": "bold #FF00FF", # Changed from dark_cyan
        "argparse.syntax": "underline", # Changed from bold
        "argparse.text": "white",   # Changed from default
        "argparse.prog": "bold #00AAFF italic",     # Changed from grey50
        "argparse.default": "bold", # Changed from italic
    }

class SubDL(WebScrap, ApiScrap):
    def __init__(self):#, api_key='zUjcID8DcqKffRNVe43bc3y8byfCSRmn'):
        self.console = console
        super().__init__()
        
    def _parse_html_results(self, html):
        """
            Parse hasil HTML untuk mencari subtitle
            Example output:
            {
                "buildId": "C5zLWqjvaXWJ4DrheckWW",
                "defaultLocale": "en",
                "gssp": true,
                "isExperimentalCompile": false,
                "isFallback": false,
                "locale": "en",
                "locales": [
                    "en",
                    "fa",
                    ...
                 ],
                "page": "/search/[...slug]",
                "props": {
                    "__N_SSP": true,
                    "pageProps": {
                        "list": [
                            {
                                "name": "Diablo",
                                "original_name": "Diablo",
                                "poster_url": "https://poster.subdl.com/poster/6uAVDyWhkXfaMo09hNpyqR0xkFp.jpg",
                                "sd_id": "sd10434",
                                "slug": "diablo",
                                "subtitles_count": 57,
                                "type": "movie",
                                "year": 2016
                            },
                            {
                                "name": "Diablo",
                                ...
                        ],
                        "query": "diablo",
                        "scList": []
                    }
                },
                "query": {
                    "slug": [
                        "diablo"
                    ]
                },
                "scriptLoader": [
                    {
                        "dangerouslySetInnerHTML": {
                            "__html": "{\"@context\":\"https://schema.org\",\"@type\":\"WebSite\",\"url\":\"https://subdl.com\",\"potentialAction\":{\"@type\":\"SearchAction\",\"target ...
                         },
                        "id": "json-ld",
                        "strategy": "afterInteractive",
                        "type": "application/ld+json"
                    },
                    {
                        "async": true,
                        "id": "GA1",
                        "src": "https://www.googletagmanager.com/gtag/js?id=G-N02LL12MHK",
                        "strategy": "afterInteractive"
                    },
                    {
                        "dangerouslySetInnerHTML": {
                            "__html": "\n            window.dataLayer = window.dataLayer || [];\n            function gtag(){dataLayer.push(arguments);}\n            gtag('js', new Date());\n            \n            gtag('config', 'G-N02LL12MHK');\n            "
                        },
                        "id": "GA",
                        "strategy": "afterInteractive"
                    }
                ]
            }
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # find __NEXT_DATA__
        # next_data = soup.find('script', type='application/ld+json', id='__NEXT_DATA__')
        next_data = soup.find('script', id='__NEXT_DATA__')
        debug(next_data = next_data)
        next_data_json = json5.loads(next_data.string) if next_data else {}
        debug(next_data_json = next_data_json)
        if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']): jprint(next_data_json)
        
        return next_data_json
            
    def get_download_links(self, data, build_id=None):
        """
            Get download links from the subtitle page
            This method scrapes the subtitle page to find download links.
        """
        debug(data = data)
        url = None
        data_links = {}
        #example must be url: https://subdl.com/_next/data/C5zLWqjvaXWJ4DrheckWW/en/subtitle/sd12679827/diablo.json?slug=sd12679827&slug=diablo
        # https://subdl.com/_next/data/C5zLWqjvaXWJ4DrheckWW/en/subtitle/sd87696/avengersendgame.json?slug=sd87696&slug=avengersendgame
        # https://subdl.com/_next/data/C5zLWqjvaXWJ4DrheckWW/en/subtitle/sd87696/avengersendgame.json?slug=sd87696&slug=avengersendgame
        if isinstance(data, dict) and data.get('slug') and build_id:
            slug = data['slug']
            debug(slug = slug)
            sd_id = data.get('sd_id', '')
            debug(sd_id = sd_id)
            url = f"{Config.base_url}/_next/data/{build_id}/en/subtitle/{sd_id}/{slug}.json?slug={sd_id}&slug={slug}"
            debug(url = url)
            response = Config.session.get(url)
            if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']):
                with open('subdl_subtitle_web1.json', 'wb') as f:
                    f.write(response.content)
            data_links = response.json()
            debug(data_links = data_links)
            if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']): jprint(data_links)
            
        elif isinstance(data, dict) and data.get('link'):
            # If data is a string, it might be a link
            url = urljoin(Config.base_url, data.get('link', ''))
            debug(url = url)
        
            response = Config.session.get(url)
            if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']):
                with open('subdl_subtitle_web.html', 'wb') as f:
                    f.write(response.content)
            data_links = self._parse_html_results(response.content)
            if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']):
                with open('subdl_subtitle_web2.json', 'w') as f:
                    f.write(str(data_links))
            debug(data_links = data_links)
            if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']): jprint(data_links)
            
        else:
            print("Invalid data format for download links.")
            return {}
        
        if not data_links:
            print("No download links found.")
            return {}
        
        return data_links
    
    def download_subtitle(self, download_url, output_dir='subtitles'):
        """
            Download the subtitle file from the given URL
            This method downloads the subtitle file and saves it to the specified output directory.
            Download use rich with progress bar
        """
        if not download_url:
            print("No download URL provided.")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        filename = os.path.basename(download_url)
        output_path = os.path.join(output_dir, filename)
        
        try:
            response = Config.session.get(download_url, stream=True)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Subtitle downloaded successfully: {output_path}")
            else:
                print(f"Failed to download subtitle. HTTP Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading subtitle: {e}")
    
    def print_list_subtitles(self, data_links, download_path = None):
        """
            Print the list of subtitles from get_download_links
        """
        debug(data_links = data_links)
        if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']): jprint(data_links)
        data_langs = data_links.get('props').get('pageProps').get('langList')
        for index, lang in enumerate(data_langs):
            #"langList": [
            # { "lang": "arabic", "count": 42 },
            # { "lang": "farsi_persian", "count": 73 },
        
            console.print(f"{str(index + 1).zfill(2)}. [#00FFFF]{lang['lang']}[/] - [#FFFF00]{lang['count']}[/] subtitles")
        
        q1 = console.input("[bold #00FFFF]Enter the number of the language to download subtitles:[/] ")
        if q1 and q1.lower() in ['x', 'exit', 'q', 'quit']:
            print("Exiting...")
            return None
        if q1.isdigit() and int(q1) <= len(data_langs):
            index = int(q1) - 1
            if 0 <= index < len(data_langs):
                selected_lang = data_langs[index]
                lang = selected_lang['lang']
                count = selected_lang['count']
                console.print(f"Selected Language: [#00FFFF]{lang}[/] with [#FFFF00]{count}[/] subtitles")
                
                # Get the download links for the selected language
                list_subtitles = data_links.get('props').get('pageProps', {}).get('groupedSubtitles', {}).get(lang, [])
                #example:
                # "groupedSubtitles": {
                # "arabic": [
                #     {
                #         "id": 758663,
                #         "language": "arabic",
                #         "quality": "trailar",
                #         "link": "758663-1949685.zip",
                #         "bucketLink": "758663/1949685.zip",
                #         "author": "kimosubtitles",
                #         "season": 0,
                #         "episode": 0,
                #         "title": "Marvel Studios' Avengers_ Endgame - Official Trailer",
                #         "extra": "",
                #         "e": true,
                #         "n_id": "nYPJ3MdcxI",
                #         "downloads": 113,
                #         "hi": 0,
                #         "releases": [],
                #         "rate": null,
                #         "date": 1552597500000,
                #         "comment": "ترجمه   kamel Ahmed",
                #         "slug": "avengersendgame"
                #     },
                if not list_subtitles:
                    print(f"No subtitles found for language: {lang}")
                    return
                print(f"Subtitles for language: {lang} ({count} found)")
                for sub_index, subtitle in enumerate(list_subtitles):
                    title = subtitle.get('title', 'Unknown')
                    author = subtitle.get('author', 'Unknown')
                    downloads = subtitle.get('downloads', 0)
                    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(subtitle.get('date', 0) / 1000))
                    console.print(f"{str(sub_index + 1).zfill(2)}. [#00FFFF]{title}[/] by [#FFFF00]{author}[/] - [#FFAA00]{downloads}[/] downloads on {date} ({subtitle.get('quality', 'Unknown')})")
                    
                q2 = console.input("[bold #00FFFF]Enter the number of the subtitle to download:[/] ")
                if q2 and q2.lower() in ['x', 'exit', 'q', 'quit']:
                    print("Exiting...")
                    return None
                if q2.isdigit() and int(q2) <= len(list_subtitles):
                    sub_index = int(q2) - 1
                    if 0 <= sub_index < len(list_subtitles):
                        selected_subtitle = list_subtitles[sub_index]
                        link = selected_subtitle.get('link', '')
                        if link:
                            # example: https://dl.subdl.com/subtitle/758781-2025215.zip
                            download_url = f"https://dl.subdl.com/subtitle/{link}"
                            debug(download_url = download_url)
                            print(f"Downloading subtitle: {selected_subtitle.get('title', 'Unknown')} from {download_url}")
                            self.download_subtitle(download_url, download_path or 'subtitles')
                        else:
                            print("No download link found for the selected subtitle.")
                    else:
                        print("Invalid selection.")
                elif q2 and q2 == 'a':
                    print("Downloading all subtitles...")
                    for subtitle in list_subtitles:
                        link = subtitle.get('link', '')
                        if link:
                            download_url = f"https://dl.subdl.com/subtitle/{link}"
                            debug(download_url = download_url)
                            print(f"Downloading subtitle: {subtitle.get('title', 'Unknown')} from {download_url}")
                            self.download_subtitle(download_url, download_path or 'subtitles')
                        else:
                            print("No download link found for the subtitle.")
                elif q2 and "," in q2:
                    print("Downloading multiple subtitles...")
                    indices = [int(i.strip()) - 1 for i in q2.split(',') if i.strip().isdigit()]
                    for sub_index in indices:
                        if 0 <= sub_index < len(list_subtitles):
                            selected_subtitle = list_subtitles[sub_index]
                            link = selected_subtitle.get('link', '')
                            if link:
                                download_url = f"https://dl.subdl.com/subtitle/{link}"
                                debug(download_url = download_url)
                                print(f"Downloading subtitle: {selected_subtitle.get('title', 'Unknown')} from {download_url}")
                                self.download_subtitle(download_url, download_path or 'subtitles')
                            else:
                                print(f"No download link found for subtitle index {sub_index + 1}.")
                        else:
                            print(f"Invalid selection for subtitle index {sub_index + 1}.")
                elif q2 and " " in q2.strip():
                    print("Downloading multiple subtitles by name...")
                    names = [name.strip() for name in q2.split(' ') if name.strip()]
                    for name in names:
                        found = False
                        for subtitle in list_subtitles:
                            if subtitle.get('title', '').lower() == name.lower():
                                link = subtitle.get('link', '')
                                if link:
                                    download_url = f"https://dl.subdl.com/subtitle/{link}"
                                    debug(download_url = download_url)
                                    print(f"Downloading subtitle: {subtitle.get('title', 'Unknown')} from {download_url}")
                                    self.download_subtitle(download_url, download_path or 'subtitles')
                                    found = True
                                    break
                        if not found:
                            print(f"No subtitle found with the name: {name}")
            else:
                print("Invalid selection.")
    
    def navigator(self, query, force_web = False, download_path = None):
        """
            Navigate through the results and download subtitles
        """
        data_links = {}
        if not force_web:
            # Search using API3
            results = self.search_api3(query)
            if results:
                selected_item = self.print_list_api3(results)
                debug(selected_item = selected_item)
                data_links = self.get_download_links(selected_item)
        
        if not results or force_web:
            print("No results found in API3, trying web search...")
            # Fallback to web search
            results = self.search_web(query)
            if results:
                selected_item = self.print_list_web(results)
                debug(selected_item = selected_item)
                if selected_item:
                    build_id = results.get('buildId', '')
                    debug(build_id = build_id)
                    data_links = self.get_download_links(selected_item, build_id)
                else:
                    print("No valid selection made from web search.")
            else:
                print("No results found in web search.")
                return
        
        if data_links:
            debug(data_links = data_links)
            if any(d in os.environ for d in ['DEBUG', 'DEBUG_SERVER']): jprint(data_links)
            self.print_list_subtitles(data_links, download_path)
            
    def usage(self):
        """
            Usage of the SubDL script
        """
        hello = """███████╗██╗   ██╗██████╗ ██╗                                                                   
██╔════╝██║   ██║██╔══██╗██║                                                                   
███████╗██║   ██║██████╔╝██║                                                                   
╚════██║██║   ██║██╔══██╗██║                                                                   
███████║╚██████╔╝██████╔╝███████╗                                                              
╚══════╝ ╚═════╝ ╚═════╝ ╚══════╝                                                              
                                                                                               
██████╗  ██████╗ ██╗    ██╗███╗   ██╗██╗      ██████╗  █████╗ ██████╗ ███████╗██████╗          
██╔══██╗██╔═══██╗██║    ██║████╗  ██║██║     ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗         
██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║██║     ██║   ██║███████║██║  ██║█████╗  ██████╔╝         
██║  ██║██║   ██║██║███╗██║██║╚██╗██║██║     ██║   ██║██╔══██║██║  ██║██╔══╝  ██╔══██╗         
██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║███████╗╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║         
╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝         
                                                                                               
██████╗ ██╗   ██╗     ██████╗██╗   ██╗███╗   ███╗██╗   ██╗██╗     ██╗   ██╗███████╗ ██╗██████╗ 
██╔══██╗╚██╗ ██╔╝    ██╔════╝██║   ██║████╗ ████║██║   ██║██║     ██║   ██║██╔════╝███║╚════██╗
██████╔╝ ╚████╔╝     ██║     ██║   ██║██╔████╔██║██║   ██║██║     ██║   ██║███████╗╚██║ █████╔╝
██╔══██╗  ╚██╔╝      ██║     ██║   ██║██║╚██╔╝██║██║   ██║██║     ██║   ██║╚════██║ ██║ ╚═══██╗
██████╔╝   ██║       ╚██████╗╚██████╔╝██║ ╚═╝ ██║╚██████╔╝███████╗╚██████╔╝███████║ ██║██████╔╝
╚═════╝    ╚═╝        ╚═════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝ ╚═╝╚═════╝ """
        print(hello, "\n")
        parser = argparse.ArgumentParser(
            description="Subdl.com Scraper Subtitles",
            formatter_class=CustomRichHelpFormatter
        )
        parser.add_argument('query', nargs="*", help='Search query for subtitles')
        parser.add_argument('--web', action='store_true', help='Force web search instead of API3')
        parser.add_argument('-p', '--download-path', type=str, default='subtitles', help='Path to save downloaded subtitles (default: subtitles)')
        
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)
        
        args = parser.parse_args()
        
        if args.query:
            print(f"Searching for subtitles: {args.query}")
            query = " ".join(args.query)[:-1] if args.query[-1].endswith(os.path.sep) else " ".join(args.query)
            download_path = args.download_path
            if os.path.isdir(query):
                download_path = query
            self.navigator(query, force_web=args.web, download_path=download_path)
        else:
            print("Please provide a search query.")
        
if __name__ == "__main__":
    SubDL().usage()