


# SubDL.com Downloader

## Install

```bash:

$ pip install git+https://github.com/cumulus13/subdl

```
or 

```bash:
$ git clone https://github.com/cumulus13/subdl
$ cd subdl
$ pip install .

```

## Usage
```bash:
subdl [-h] [-p PATH] [-c] [-l [LANGS ...]] MOVIE

positional arguments:
  MOVIE                 Search movie name

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Save download to directory
  -c, --clip            Just copy link download, don"t download
  -l [LANGS ...], --langs [LANGS ...]
                        Languages, default is "EN", from configfile "subdl.ini", format: "en,english,id,indonesia,jp,japan". use
                        code lang or lang long name
```
### example usage:
   - download with folder name and save it in that folder
   ```bash:
    subdl "c:\MOVIES\Avatar (2023)" -l jp
   ```
   - download by movie name and save it to folder "C:\MOVIES\Heart of Stone (2023)"
   ```bash:
    subdl "Heart of Stone (2023)" -l id -p "c:\MOVIES\Heart of Stone (2023)"
   ```
 ### requirements (pip)
 - argparse
 - rich
 - configset
 - pydebugger
 - make_colors
 - requests
 - bitmath
 - clipboard
 - unidecode
 - git+https://github.com/cumulus13/jsoncolor (option)
 - git+https://github.com/cumulus13/xnotify (option)
 
## Author
[cumulus13](mailto:cumulus13@gmail.com)