# Pixel Blast Anime Downloader

A simple and efficient batch downloader for anime episodes.

This tool fetches episode lists from AnimeHeaven, extracts playable video sources, and downloads them in batches with retry and resume support. It is designed to be lightweight, reliable, and easy to use from the terminal.

---

## Features

- Fetches all available episodes automatically
- Select a custom episode range to download
- Batch downloading for better stability
- Resume support if downloads are interrupted
- Retry system for failed requests
- Progress tracking using a clean terminal progress bar

---

## Requirements

- Python 3.8 or higher

---

## Installation

Clone the repository or download the script, then install dependencies:

```bash
pip install requests beautifulsoup4 aiohttp tqdm
```

---

## Usage

Run the script:

```bash
python your_script_name.py
```

You will be prompted for:

- Anime URL
- Start episode number
- End episode number

Example:

```
URL: https://animeheaven.me/detail/one-piece
Start: 1
End: 10
```

Downloaded files will be saved in the `downloads` folder.

---

## How It Works

1. Scrapes the episode list from the given URL
2. Extracts internal video source identifiers
3. Fetches actual video stream links
4. Downloads episodes in batches with retry handling
5. Automatically resumes incomplete downloads

---

## Notes

- A working VPN may be required depending on your region and the website's restrictions
- Download speed depends on your internet connection and server response
- Avoid setting very high batch sizes to prevent connection issues

---

## Disclaimer

This project is for educational purposes only. Make sure you have the right to download and use the content you access.

---

## Author

Built by Goutham Kumar A  
https://pixelblast.vercel.app
