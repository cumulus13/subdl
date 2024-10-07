#!c:/SDK/Anaconda3/python.exe
#from __future__ import print_function
import sys, os
#from safeprint import print as sprint
import imdb
import re
import argparse
from make_colors import make_colors
if any('debug' in i.lower() for i in  os.environ):
	from pydebugger.debug import debug
else:
	def debug(*args, **kwargs):
		return

import download
try:
	from . import trailer
except:
	import trailer
from qv import show	
import clipboard
from unidecode import unidecode
from rich import traceback as rich_traceback, console
import shutil
rich_traceback.install(theme='fruity', max_frames=30, width=shutil.get_terminal_size()[0])
console = console.Console()

class imdbcli_error(Exception):
	pass

class imdbcli(object):
	def __init__(self):
		super(imdbcli, self)
		
	def details(self, id, download_cover = False, download_json = False, download_path = "covers", cover_name = 'Poster', thumb_name = 'Thumb'):
		im = imdb.IMDb()
		data = im.get_movie(id)
		download_cover_is_finish = False
		download_thumb_finish = False
		download_poster_finish = False
		download_poster_is_error = False
		download_thumb_is_error = False
		#print("Keys =", data.keys())
		for x in data.keys():
			try:
				console.print(f"[bold #ffff00]{str(x).upper()}[/] {(32 - len(str(x))) * ' '} = [bold #ff55ff]{unidecode(data.get(x))}[/]")
			except:
				try:
					console.print(f"[bold #ffff00]{str(x).upper()}[/] {(32 - len(str(x))) * ' '} = [bold #ff55ff]{data.get(x)}[/]")
				except:
					#try:
						#sprint(make_colors(str(x).upper(), 'b', 'y'), (32 - len(str(x))) * ' ', "=", data.get(x))
					#except:
					console.print_exception(show_locals=True, theme='fruity', width=shutil.get_terminal_size()[0], max_frames=30)

			#print("Thumb  URL =", data.get('cover url'))
			#print("Poster URL =", data.get('full-size cover url'))
			if not download_cover_is_finish:
				if download_cover:
					if not os.path.isdir(download_path):
						os.makedirs(download_path)
					if not download_thumb_finish:
						if data.get('cover url'):
							if os.path.splitext(data.get('cover url'))[:-1][0].lower() in [".jpg", '.png', '.jpeg', '.webp', '.bmp']:
								thumb_name += os.path.splitext(data.get('cover url'))[:-1][0].lower()
							else:
								thumb_name += ".jpg"
							download.download(data.get('cover url'), download_path, thumb_name)
							download_thumb_finish = True
					else:
						download_thumb_is_error = True
					if not download_poster_finish:
						if data.get('full-size cover url'):
							if os.path.splitext(data.get('full-size cover url'))[:-1][0].lower() in [".jpg", '.png', '.jpeg', '.webp', '.bmp']:
								cover_name += os.path.splitext(data.get('full-size cover url'))[:-1][0].lower()
							else:
								cover_name += ".jpg"							
							download.download(data.get('full-size cover url'), download_path, cover_name)
							download_poster_finish = True
						else:
							download_poster_is_error = True
					download_cover_is_finish = True
			# else:
			# 	download_poster_finish = True
			# 	download_thumb_finish = True
			# 	download_cover_is_finish = True
		if download_thumb_is_error:
			#print(make_colors("No Image Thumb Url Found !", 'white', 'red', ['blink']))
			console.print(f"[#ffffff on #ff0000 blink]No Image Thumb Url Found ![/]")
		elif download_thumb_finish:
			#print(make_colors("Successfull download thumb image !", 'white', 'red', ['blink']))
			console.print(f"[black on #55ffff blink]Successfull download thumb image ![/]")
		if download_poster_is_error:
			#print(make_colors("No Image Poster Url Found !", 'white', 'red', ['blink']))
			console.print(f"[#ffffff on #ff0000 blink]No Image Poster Url Found ![/]")
		elif download_cover_is_finish:
			#print(make_colors("Successfull download Poster image !", 'white', 'red', ['blink']))
			console.print(f"[black on #ff00ff blink]Successfull download Poster image ![/]")
				
		return data
		
	def cli(self, movie = None, id = None, download_cover = False, download_json = False, download_path = 'covers', cover_name = 'Poster', thumb_name = 'Thumb', clip = False):
		im = imdb.IMDb()
		if movie:
			data = im.search_movie(movie)
			n = 1
			for i in data:
				#number = make_colors(str(n), 'cyan')
				number = str(n)
				if len(str(n)) == 1:
					#number = make_colors("0" + str(n), 'cyan')
					number = "0" + str(n)
				
				#title = make_colors(unidecode(i.get('long imdb title')), 'white', 'blue')
				#ID = make_colors(i.getID(), 'red', 'white')
				ID = i.getID()
				console.print(f'[bold #ff55ff]{number}.[/] [bold #55ffff]{unidecode(i.get("long imdb title"))}[/] [bold #aaff00]\[{ID}][/]')
				n += 1
			try:
				console.print(f"[bold #ffffff on #aa00ff]Select Number:[/] ", end = '')
				#q = input(make_colors("Select Number: ", 'b', 'y'))
				q = input()
			except:
				sys.exit()
			if q:
				if str(q).strip().isdigit():
					idx = data[int(str(q).strip()) - 1].getID()
					# debug(idx = idx, debug = True)
					if clip:
						clipboard.copy("tt" + str(idx))
					elif int(q) <= len(data):
						if __name__ == '__main__':
							self.details(idx, download_cover, download_json, download_path)
							clipboard.copy("tt" + str(idx))
						else:
							return "tt" + str(idx)
					#print(make_colors("Movie Selected:", 'black', 'yellow'), make_colors(data[int(str(q).strip()) - 1].get('long imdb title'), 'white', 'magenta'))
					console.print(f"[bold #fffff on #005500]Movie Selected:[/] [black on #ff5500]{data[int(str(q).strip()) - 1].get('long imdb title')}[/]")
				elif q.strip()[-1] == 't' or q.strip()[0] == 't':
					if q.strip()[-1] == 't':
						idx = q.strip()[:-1]
						idx = data[int(idx.strip()) - 1].getID()
					elif q.strip()[0] == 't':
						idx = q.strip()[1:]
						idx = data[int(idx.strip()) - 1].getID()						
					data_detail = self.details(idx, download_cover, download_json, download_path)
					debug(data_detail = data_detail, debug = 1)
					vkey = list(filter(lambda k: k.lower() == 'videos', list(data_detail.keys())))
					vf_image = list(filter(lambda k: k.lower() == 'full-size cover url', list(data_detail.keys())))
					if vkey:
						data_get = data_detail.get(vkey[0])
						debug(data_get = data_get, debug = 1)
						trailer.show(data_get[0])
					elif vf_image:
						data_get = data_detail.get(vf_image[0])
						debug(data_get = data_get)
						show(vf_image[0])
					
		elif id:
			data = im.get_movie(id)
			if data:
				self.details(id, download_cover, download_json, download_path)
				#print(make_colors("Movie Selected:", 'black', 'yellow'), make_colors(data.get('long imdb title'), 'white', 'magenta'))
				console.print(f"[bold #fffff on #005500]Movie Selected:[/] [black on #ff5500]{data.get('long imdb title')}[/]")
			else:
				#print(make_colors("No Movie Found !", 'white', 'red', ['blink']))
				console.print(f"[#fffff on #aa0000 blink]No Movie Found ![/]")
		else:
			raise imdbcli_error(make_colors("No Movie or ID given !", 'white', 'red', ['blink']))	
			
	def usage(self):
		
		MOVIE_NAME = ''
		parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
		parser.add_argument('-m', '--movie', action = 'store', help = 'Search by Movie Name')
		parser.add_argument('-c', '--copy-id', action = 'store_true', help = 'Copy Id to Clipboard')
		parser.add_argument('-id', '--id', action = 'store', help = 'Search by Movie id, just number without "tt"')
		parser.add_argument('-d', '--download', action = 'store_true', help = 'Download data as json')
		parser.add_argument('-dc', '--download-cover', action = 'store_true', help = 'Download Image Poster and Thumb')
		parser.add_argument('-p', '--download-path', action = 'store', help = 'Save all of Download data to directory', default = 'covers')
		parser.add_argument('-cn', '--cover-name', action = 'store', help='Save Cover Poster as name, default: "Poster"', default = 'Poster')
		parser.add_argument('-tn', '--thumb-name', action = 'store', help='Save Thumb as name, default: "Thumb"', default = 'Thumb')
		if len(sys.argv) == 1:
			parser.print_help()
			sys.exit()
		elif len(sys.argv) > 1 and len([i for i in sys.argv[1:] if not i in parser._option_string_actions.keys()]) > 1:
			parser.add_argument('MOVIES', action = 'store', help = 'Search by Movie Name', nargs='*')
			MOVIE_NAME = True
		args = parser.parse_args()
		if MOVIE_NAME:
			movie = " ".join(args.MOVIES)
			debug(movie = movie)
			movie = re.split("\|", movie)
			debug(movie = movie)
		else:
			movie = args.movie
		if isinstance(movie, list):
			for i in movie:
				if i == 'c':
					i = clipboard.paste()
				self.cli(i, args.id, args.download_cover, args.download, args.download_path, args.cover_name, args.thumb_name, args.copy_id)
		else:
			if movie == 'c':
				movie = clipboard.paste()
			self.cli(movie, args.id, args.download_cover, args.download, args.download_path, args.cover_name, args.thumb_name, args.copy_id)
			
if __name__ == '__main__':
	c = imdbcli()
	c.usage()
		