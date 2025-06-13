#!/usr/bin/env python3
#coding:utf-8
"""
  Author:  cumulus13 --<cumulus13@gmail.com>
  Purpose: SubDL.com downloader - Fixed Version
  Created: 07/26/24
  Fixed: Better search handling and error recovery
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
import time
# try:
#     from .imdbcli import imdbcli
# except:
#     from imdbcli import imdbcli
    
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
    def clean_query(cls, query):
        """Clean and normalize search query"""
        # Remove common video formats and quality indicators
        query = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm)$', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\b(720p|1080p|480p|4k|2160p|hdtv|webrip|bluray|brrip|dvdrip|cam|ts|tc)\b', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\b(x264|x265|h264|h265|xvid|divx)\b', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\b(aac|ac3|dts|mp3)\b', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\b(yify|etrg|rarbg|ettv|ganool)\b', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\[.*?\]', '', query)  # Remove content in brackets
        query = re.sub(r'\{.*?\}', '', query)  # Remove content in braces
        query = re.sub(r'\s+', ' ', query).strip()  # Normalize whitespace
        return query

    @classmethod
    def extract_year(cls, query):
        """Extract year from query"""
        year_match = re.search(r'\b(19|20)\d{2}\b', query)
        if year_match:
            return year_match.group(0)
        
        # Also check for year in parentheses
        paren_year = re.findall(r'\((\d{4})\)', query)
        if paren_year:
            return paren_year[0]
        
        return None

    @classmethod
    def search_with_fallback(cls, query, languages="", max_retries=3):
        """Search with multiple fallback strategies"""
        
        # Strategy 1: Direct search
        for attempt in range(max_retries):
            try:
                result = cls.api_search(query, languages)
                if result and result.get('status') and result.get('subtitles'):
                    debug(f"Direct search successful on attempt {attempt + 1}")
                    return result
            except Exception as e:
                debug(f"Direct search attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        
        # Strategy 2: Clean query and retry
        cleaned_query = cls.clean_query(query)
        if cleaned_query != query:
            debug(f"Trying with cleaned query: {cleaned_query}")
            for attempt in range(max_retries):
                try:
                    result = cls.api_search(cleaned_query, languages)
                    if result and result.get('status') and result.get('subtitles'):
                        debug(f"Cleaned search successful on attempt {attempt + 1}")
                        return result
                except Exception as e:
                    debug(f"Cleaned search attempt {attempt + 1} failed: {e}")
                    time.sleep(1)
        
        # Strategy 3: Try with year extracted
        year = cls.extract_year(query)
        if year:
            query_with_year = re.sub(r'\b' + re.escape(year) + r'\b', '', query).strip()
            query_with_year = cls.clean_query(query_with_year)
            debug(f"Trying with year parameter: {query_with_year}, year: {year}")
            
            for attempt in range(max_retries):
                try:
                    result = cls.api_search(query_with_year, languages, year=year)
                    if result and result.get('status') and result.get('subtitles'):
                        debug(f"Year-based search successful on attempt {attempt + 1}")
                        return result
                except Exception as e:
                    debug(f"Year-based search attempt {attempt + 1} failed: {e}")
                    time.sleep(1)
        
        # Strategy 4: Try word-by-word removal (for complex titles)
        words = cleaned_query.split()
        if len(words) > 2:
            for i in range(len(words) - 1, 1, -1):
                partial_query = ' '.join(words[:i])
                debug(f"Trying partial query: {partial_query}")
                
                try:
                    result = cls.api_search(partial_query, languages)
                    if result and result.get('status') and result.get('subtitles'):
                        debug(f"Partial search successful with: {partial_query}")
                        return result
                except Exception as e:
                    debug(f"Partial search failed for {partial_query}: {e}")
                    time.sleep(1)
        
        return None

    @classmethod
    def api_search(cls, query, languages="", year=None, imdb_id=None, tmdb_id=None):
        """Make actual API call"""
        url = cls.URL + "api/v1/subtitles"
        
        params = {
            'api_key': cls.API_KEY,
            'languages': languages or cls.CONFIG.get_config('lang', 'names', 'ID') or 'ID',
        }
        
        if imdb_id:
            params['imdb_id'] = imdb_id
        elif tmdb_id:
            params['tmdb_id'] = tmdb_id
        else:
            params['film_name'] = query
        
        if year:
            params['year'] = year
            
        # Add additional headers to mimic browser behavior
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        debug(params=params)
        debug(url=url)
        
        response = cls.SESS.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        content = response.json()
        debug(content=content)
        
        if os.getenv('DEBUG') == '1' or os.getenv('DEBUG_SERVER'): 
            jprint(content)
            
        return content

    @classmethod
    def search(cls, query, download_path=None, copy_to_clipboard=False, languages="", params=None):
        data = []
        
        # Try search with fallback strategies
        content = cls.search_with_fallback(query, languages)
        
        # if not content:
        #     console.print("[white on red bold blink]No results found with any search strategy![/]")
        #     # Try IMDB search as last resort
        #     try:
        #         imdb_id = imdbcli().cli(query)
        #         debug(imdb_id=imdb_id)
        #         if imdb_id:
        #             content = cls.api_search("", languages, imdb_id=imdb_id)
        #     except Exception as e:
        #         debug(f"IMDB search failed: {e}")
                
        if not content or not content.get('status'):
            console.print("[white on red bold blink]No Subtitle FOUND![/]")
            if content and content.get('error'):
                console.print(f"[red]API Error: {content.get('error')}[/red]")
            return

        langs = []
        
        # Handle multiple movie results
        if content.get('results') and len(content.get('results')) > 1:
            console.print(f"[cyan b]Found[/cyan b] [white bold u]{len(content.get('results'))}[/white bold u] movies")
            m = 1
            for movie in content.get('results'):
                year_info = f" ({movie.get('year')})" if movie.get('year') else ""
                console.print(f"[cyan bold]{m:03}.[/] [#55ff00 bold]{movie.get('name')}{year_info}[/#55ff00 bold]")
                m += 1

            movie_selected = input(make_colors("Select movie number to download:", 'lw', 'm') + " ")
            if movie_selected and movie_selected.isdigit():
                selected_idx = int(movie_selected) - 1
                if 0 <= selected_idx < len(content.get('results')):
                    selected_movie = content.get('results')[selected_idx]
                    
                    # Search again with specific movie parameters
                    search_params = {}
                    if selected_movie.get('imdb_id'):
                        content = cls.api_search("", languages, imdb_id=selected_movie.get('imdb_id'))
                    elif selected_movie.get('tmdb_id'):
                        content = cls.api_search("", languages, tmdb_id=selected_movie.get('tmdb_id'))
                    else:
                        content = cls.api_search(selected_movie.get('name'), languages, 
                                               year=selected_movie.get('year'))
            elif movie_selected and movie_selected.lower() in ('q', 'x', 'exit', 'quit'):
                console.print("[#ff007f bold blink]Exit....[/#ff007f bold blink]")
                sys.exit(0)

        # Process subtitles
        if content.get('subtitles'):
            console.print(f"[cyan b]Found[/cyan b] [white bold u]{len(content.get('subtitles'))}[/white bold u] subtitles")
            langs = list(set([i.get('lang') for i in content.get('subtitles')]))
            debug(langs=langs)
            
            n = 1
            for lang in langs:
                lang_name = CODE.get(lang.lower(), lang)
                console.print(f"- [#ffaa00 bold]{lang} ({lang_name})[/#ffaa00 bold]")
                
                # Get subtitles for this language (both cases)
                lang_subs = [s for s in content.get('subtitles') 
                           if s.get('lang', '').lower() == lang.lower()]
                
                for s in lang_subs:
                    data.append(s)
                    release_info = f" - {s.get('release', '')}" if s.get('release') else ""
                    console.print(f"[cyan bold]{n:03}.[/cyan bold] [yellow bold]{s.get('name')}{release_info}[/yellow bold]")
                    n += 1

            # Handle subtitle selection
            sub_selected = input(make_colors("Select subtitle number(s) to download (comma/space separated):", 'lw', 'bl') + " ")
            debug(sub_selected=sub_selected)
            
            if sub_selected:
                if sub_selected.lower() in ('q', 'x', 'exit', 'quit'):
                    console.print("[#ff007f bold blink]Exit....[/#ff007f bold blink]")
                    sys.exit(0)
                
                # Parse selection (single number, comma-separated, or space-separated)
                selected_numbers = []
                if sub_selected.isdigit():
                    selected_numbers = [int(sub_selected)]
                elif "," in sub_selected:
                    selected_numbers = [int(i.strip()) for i in sub_selected.split(",") 
                                      if i.strip().isdigit()]
                elif " " in sub_selected:
                    selected_numbers = [int(i.strip()) for i in sub_selected.split() 
                                      if i.strip().isdigit()]
                
                # Download selected subtitles
                for num in selected_numbers:
                    if 1 <= num <= len(data):
                        subtitle = data[num - 1]
                        link = subtitle.get("url")
                        name = subtitle.get("name")
                        
                        if link:
                            download_link = cls.DURL + link
                            debug(download_link=download_link)
                            debug(name=name)
                            
                            try:
                                downloader.downloader(download_link, download_path, name, 
                                                    copyurl_only=copy_to_clipboard)
                                console.print(f"[green]✓ Downloaded: {name}[/green]")
                            except Exception as e:
                                console.print(f"[red]✗ Failed to download {name}: {e}[/red]")
                        else:
                            console.print("[white on red bold blink]No Download link FOUND![/]")
        else:
            console.print("[white on red bold blink]No Subtitles FOUND![/]")

    @classmethod
    def usage(cls):
        parser = argparse.ArgumentParser(description="SubDL.com subtitle downloader")
        parser.add_argument('MOVIE', 
                          help="Search movie name or directory name", 
                          action='store', nargs='*')
        parser.add_argument("-p", "--path", 
                          help="Save download to directory", 
                          action='store')
        parser.add_argument('-c', '--clip', 
                          help='Just copy link download, don\'t download', 
                          action='store_true')
        parser.add_argument("-l", '--langs', 
                          help=f'Languages, default is "{cls.CONFIG.get_config("lang", "names") or "ID"}"', 
                          nargs='*')

        if len(sys.argv) == 1:
            parser.print_help()
            return

        args = parser.parse_args()
        
        if not args.MOVIE:
            parser.print_help()
            return
            
        if args.MOVIE == ["."]:
            args.MOVIE = [os.getcwd()]

        # Process language arguments
        langs = []
        if args.langs:
            for l in args.langs:
                l_lower = l.lower()
                if l_lower in CODE:
                    langs.append(l_lower)
                else:
                    # Try to find by language name
                    found_codes = [k for k, v in CODE.items() if v.lower() == l_lower]
                    if found_codes:
                        langs.append(found_codes[0])
                    else:
                        console.print(f"[yellow]Warning: Language '{l}' not recognized[/yellow]")

        languages = ",".join(langs) if langs else None
        debug(languages=languages)

        # Process movie query
        query = " ".join(args.MOVIE)
        debug(original_query=query)
        
        # Determine download path
        download_path = args.path
        
        if os.path.isdir(query):
            download_path = os.path.realpath(query)
            query = os.path.basename(query)
        elif not download_path:
            # Try to determine if query contains a path
            potential_path = os.path.dirname(query)
            if potential_path and os.path.isdir(potential_path):
                download_path = potential_path
                query = os.path.basename(query)
        
        debug(final_query=query)
        debug(download_path=download_path)
        
        # Start search
        cls.search(query.strip(), download_path, args.clip, languages)


if __name__ == '__main__':
    Subdl.usage()