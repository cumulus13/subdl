# SubDL - Subtitle Downloader & Scraper for subdl.com

**SubDL** is a Python-powered CLI tool for searching and downloading subtitles from [subdl.com](https://subdl.com).  
It supports both API and web scraping, offers interactive selection, and features a rich progress bar for downloads.

---

## 🚀 Features

- **Search subtitles** via SubDL API or web scraping fallback
- **Interactive selection** of movies/series and subtitle languages
- **Batch download**: download all, by index, or by name
- **Rich progress bar** for downloads
- **Debugging & pretty-print** for developers (with `DEBUG` env)
- **Customizable download path**
- **Python 3.8+** compatible

---

## ⚡ Installation

1. **Clone this repo:**
   ```bash
   git clone https://github.com/yourusername/subdl.git
   cd subdl/subdl
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install requests beautifulsoup4 rich rich-argparse configset jsoncolor json5
   ```

---

## 🛠️ Usage

### Basic search and download
```bash
python subdl.py "movie or series name"
```

### Force web scraping (if API fails or for more results)
```bash
python subdl.py "movie name" --web
```

### Set custom download directory
```bash
python subdl.py "movie name" -p ./my_subtitles
```

### Interactive selection
- Choose the movie/series from the list
- Choose subtitle language
- Choose subtitle(s) to download (single, multiple, or all)

### Batch download
- Enter `a` to download all subtitles in a language
- Enter `1,3,5` to download by indices
- Enter subtitle names separated by space to download by name

---

## 🧑‍💻 Developer/Debug Mode

Set `DEBUG` or `DEBUG_SERVER` in your environment to enable extra logging and pretty JSON dumps:
```bash
export DEBUG=1
python subdl.py "movie name"
```

---

## 📦 Example

```bash
python subdl.py "avengers endgame"
```
- Select the movie from the list
- Select language (e.g. English)
- Select subtitle(s) to download

---

## 📝 Notes

- This tool scrapes subdl.com and may break if the site changes.
- For best results, use Python 3.8+ and a modern terminal.
- All downloads go to the `subtitles` folder by default (or your custom path).

---

## 🪲 Issues & Contributions

- Found a bug? Open an issue or PR!
- Want a new feature? Fork and hack away!

---

## 📄 License

MIT License

---

**Happy subtitle hunting! 🎬**
 
## Author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 [Support me on Patreon](https://www.patreon.com/cumulus13)