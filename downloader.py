import os
from make_colors import make_colors
import sys
from pydebugger.debug import debug
import bitmath
from pathlib import Path
from configset import configset
from rich.console import Console
if sys.version_info.major == 2:
    import urlparse
else:
    from urllib.parse import urlparse
import traceback
from datetime import datetime
import clipboard
from xnotify import notify
from unidecode import unidecode
import re

console = Console()

class Downloader:
    
    CONFIGFILE = str(Path(__file__).parent / 'subdl.ini')
    CONFIG = configset(CONFIGFILE)
    
    @classmethod
    def logger(self, message, status="info"):
        logfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(self.CONFIG.configname).split(".")[0] + ".log")
        if not os.path.isfile(logfile):
            lf = open(logfile, 'wb')
            lf.close()
        real_size = bitmath.getsize(logfile).kB.value
        max_size = self.CONFIG.get_config("LOG", 'max_size')
        debug(max_size = max_size)
        if max_size:
            debug(is_max_size = True)
            try:
                max_size = bitmath.parse_string_unsafe(max_size).kB.value
            except:
                max_size = 0
            if real_size > max_size:
                try:
                    os.remove(logfile)
                except:
                    print("ERROR: [remove logfile]:", traceback.format_exc())
                try:
                    lf = open(logfile, 'wb')
                    lf.close()
                except:
                    print("ERROR: [renew logfile]:", traceback.format_exc())


        str_format = datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S.%f") + " - [{}] {}".format(status, message) + "\n"
        with open(logfile, 'ab') as ff:
            if sys.version_info.major == 3:
                ff.write(bytes(str_format, encoding='utf-8'))
            else:
                ff.write(str_format)
        
    @classmethod
    def downloader(self, url, download_path = None, saveas = None, confirm = False, copyurl_only = False, cookie = {}, postData = {}):
        debug(download_path = download_path)    
        debug(saveas = saveas)
        
        try:
            if not Path(download_path).is_dir() and not copyurl_only:
                download_path = None
        except:
            pass
    
        if not download_path and not copyurl_only:
            if os.getenv('DOWNLOAD_PATH'): download_path = os.getenv('DOWNLOAD_PATH')
            if self.CONFIG.get_config('DOWNLOAD', 'path', os.getcwd()):
                download_path = self.CONFIG.get_config('DOWNLOAD', 'path')
                debug(download_path_config = download_path)
        debug(download_path0 = download_path)
    
        if not copyurl_only: print(make_colors("DOWNLOAD_PATH:", 'lw', 'bl') + " " + make_colors(download_path, 'b', 'ly'))
    
        if not download_path and not copyurl_only: download_path = ''
    
        if 'linux' in sys.platform and download_path and not os.path.isdir(download_path) and not copyurl_only:
    
            debug(download_path0 = download_path)
            if not os.path.isdir(download_path):
                #this_user = getpass.getuser()
                login_user = os.getlogin()
                env_user = os.getenv('USER')
                debug(login_user = login_user)
                debug(env_user = env_user)
                #this_uid = os.getuid()
                download_path = r"/home/{0}/Downloads".format(login_user)
                debug(download_path = download_path)
    
        if download_path and not os.path.isdir(download_path) and not copyurl_only:
            try:
                os.makedirs(download_path)
            except:
                pass
    
        if download_path and not os.path.isdir(download_path) and not copyurl_only:
            try:
                os.makedirs(download_path)
            except OSError:
                tp, tr, vl = sys.exec_info()
                debug(ERROR_MSG = vl.__class__.__name__)
                if vl.__class__.__name__ == 'OSError':
                    print("[white on red bold]Permission failed make dir:[/] [white on blue]{download_path}[/]")
    
    
        if not download_path and not copyurl_only:
            download_path = os.getcwd()
        if download_path and not os.access(download_path, os.W_OK|os.R_OK|os.X_OK) and not copyurl_only:
            print(make_colors("You not have Permission save to dir:", 'lw', 'lr' + " " + make_colors(download_path, 'lr', 'lw')))
            download_path = os.getcwd()
        if not copyurl_only:
            print(make_colors("DOWNLOAD PATH:", 'lw', 'bl') + " " + make_colors(download_path, 'lw', 'lr'))
        debug(download_path = download_path)
        debug(url = url)
    
        try:
            from idm import IDMan
            d = IDMan()
        except:
            from pywget import wget as d
        
        debug(copyurl_only = copyurl_only)
        debug(netloc = urlparse(url).netloc)
    
        print(make_colors("DOWNLOAD LINK:", 'b', 'lc') + " " + make_colors(url, 'b', 'ly'))
    
        if copyurl_only: clipboard.copy(url)
        print(make_colors("SAVEAS:", 'lw', 'bl') + " " + make_colors(saveas, 'lw', 'r'))
        debug(url = url)
        debug(download_path = download_path)
        debug(saveas = saveas)

        if sys.platform == 'win32':
            self.logger("downloader [win32]: downloading: {} --> {} --> {}".format(url, url, saveas))
            d.download(url, download_path, saveas, confirm = confirm, cookie = cookie, postData = postData)
            
        else:
            self.logger("downloader [linux]: downloading: {} --> {} --> {}".format(unidecode(url), unidecode(url), unidecode(saveas)))
            debug(saveas = saveas)
            self.download_linux(url, download_path, saveas, cookies = {}, headers = {})
            self.logger("downloader [linux]: finish: {} --> {} --> {}".format(unidecode(url), unidecode(url), unidecode(saveas)))
            
        icon = None
        if os.path.isfile(os.path.join(os.path.dirname(__file__), 'logo.png')):
            icon = os.path.join(os.path.dirname(__file__), 'logo.png')
    
        notify.send("SubDL", "downloading", 'downloading', "Download start: " + saveas, ['start', 'ready', 'downloading', 'finish', 'seleced', 'process', 'clipboard'], icon = icon)
    
        debug(url = url)
        if url:
            return url
        return url
    
    @classmethod
    def download_linux(self, url, download_path=os.getcwd(), saveas=None, cookies = {}, downloader = 'wget', check_file = True, headers = None):
        '''
            downloader: aria2c, wget, uget, persepolis
        '''
        if saveas: saveas = re.sub("\.\.", ".", saveas)
        if not download_path or not os.path.isdir(download_path):
            if self.CONFIG.get_config('DOWNLOAD', 'path', os.getcwd()):
                download_path = self.CONFIG.get_config('DOWNLOAD', 'path')
        print(make_colors("DOWNLOAD_PATH (linux):", 'lw', 'bl') + " " + make_colors(download_path, 'b', 'ly'))
        print(make_colors("DOWNLOAD LINK [direct]:", 'b', 'lc') + " " + make_colors(url, 'b', 'ly'))
        if sys.version_info.major == 3:
            aria2c = os.popen("aria2c")
            wget = os.popen("wget")
            persepolis = os.popen("persepolis --help")
        else:
            aria2c = os.popen3("aria2c")
            wget = os.popen3("wget")
            persepolis = os.popen3("persepolis --help")
    
        if downloader == 'aria2c' and not re.findall("not found\n", aria2c[2].readlines()[0]):
            if saveas:
                saveas = '-o "{0}"'.format(saveas.encode('utf-8', errors = 'ignore'))
            cmd = 'aria2c -c -d "{0}" "{1}" {2} --file-allocation=none'.format(os.path.abspath(download_path), url, saveas)
            os.system(cmd)
            self.logger(cmd)
        elif downloader == 'wget':
            if sys.version_info.major == 2:
                if re.findall("not found\n", wget[2].readlines()[0]):
                    print(make_colors("Download Failed !", 'lw', 'r'))
                    return False
            filename = ''
            if saveas:
                if sys.version_info.major == 3:
                    filename = os.path.join(os.path.abspath(download_path), saveas)
                    saveas = ' -O "{}"'.format(os.path.join(os.path.abspath(download_path), saveas))
                else:
                    filename = os.path.join(os.path.abspath(download_path), saveas.decode('utf-8', errors = 'ignore'))
                    saveas = ' -O "{}"'.format(os.path.join(os.path.abspath(download_path), saveas.decode('utf-8', errors = 'ignore')))
            else:
                saveas = '-P "{0}"'.format(os.path.abspath(download_path))
                filename = os.path.join(os.path.abspath(download_path), os.path.basename(url))
            headers_add = ''
            header_cookie = ""
            if cookies:
                for i in cookies: header_cookie +=str(i) + "= " + cookies.get(i) + "; "
                headers_add = ' --header="Cookie: ' + header_cookie[:-2] + '"' +\
                    ' --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"' +\
                    ' --header="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"' +\
                    ' --header="Sec-Fetch-Site: same-origin" --header="Accept-Encoding: gzip, deflate, br" --header="Connection: keep-alive"' +\
                    ' --header="Upgrade-Insecure-Requests: 1"' +\
                    ' --header="Sec-Fetch-Mode: navigate"' +\
                    ' --header="Sec-Fetch-User: ?1"' +\
                    ' --header="Sec-Fetch-Dest: document"'
            debug(headers = headers)
            headers = headers_add + " ".join([' --header="' + i + ": " + headers.get(i) + '"' for i in headers])
            debug(headers = headers)
            cmd = 'wget -c "' + url + '" {}'.format(unidecode(saveas)) + headers
    
            if 'racaty' in url: cmd+= ' --no-check-certificate'
            print(make_colors("CMD:", 'lw', 'lr') + " " + make_colors(cmd, 'lw', 'r'))
            a = os.system(cmd)
            self.logger(cmd)
            if a:
                self.logger("It's seem error while downloading: {}".format(url), 'error')
            if self.CONFIG.get_config('policy', 'size'):
                size = ''
                try:
                    size = bitmath.parse_string_unsafe(self.CONFIG.get_config('policy', 'size'))
                except ValueError as e:
                    self.logger(str(e), 'error')
                if check_file:
                    if size and not bitmath.getsize(filename).MB.value > size.value:
                        print(make_colors("REMOVE FILE", 'lw', 'r') + " [" + make_colors(bitmath.getsize(filename).kB) + "]: " + make_colors(filename, 'y') + " ...")
                        os.remove(filename)
                        self.logger("File not qualify of size policy", 'critical')
    
        elif downloader == 'persepolis'  and not re.findall("not found\n", persepolis[2].readlines()[0]):
            cmd = 'persepolis --link "{0}"'.format(url)
            a = os.system(cmd)
            if a:
                self.logger("It's seem error while downloading: {}".format(url), 'error')
            self.logger(cmd)
        else:
            try:
                from pywget import wget as d
                d.download(url, download_path, saveas.decode('utf-8', errors = 'ignore'))
                self.logger("download: {} --> {}".format(url, os.path.join(download_path, saveas.decode('utf-8', errors = 'ignore'))))
            except Exception as e:
                print(make_colors("Can't Download this file !, no Downloader supported !", 'lw', 'lr', ['blink']))
                clipboard.copy(url)
                self.logger("download: copy '{}' --> clipboard".format(url), "error")
                self.logger(str(e), 'error')
    
    
