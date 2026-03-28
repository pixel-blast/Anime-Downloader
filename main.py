#Pixel Blast
#https://pixelblast.vercel.app
#A batch downloader for animeheaven.me that fetches video sources and downloads episodes with retry and resume support.

import requests
from bs4 import BeautifulSoup
import re
import asyncio
import aiohttp
import os
from tqdm import tqdm

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://animeheaven.me/"
}

RETRIES = 3
BATCH_SIZE = 3  

def get_episodes(url):
    print("\nFetching episodes...")

    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    blocks = soup.find_all("a", onclick=re.compile(r'gatea\("'))

    episodes = []

    for a in blocks:
        match = re.search(r'gatea\("(.+?)"\)', a.get("onclick", ""))
        ep_div = a.find("div", class_="watch2")

        if match and ep_div:
            episodes.append({
                "episode": int(ep_div.text.strip()),
                "id": match.group(1)
            })

    unique = {ep["episode"]: ep for ep in episodes}
    episodes = sorted(unique.values(), key=lambda x: x["episode"])

    print(f"Found {len(episodes)} episodes")
    return episodes

def filter_range(eps, start, end):
    selected = [ep for ep in eps if start <= ep["episode"] <= end]
    print(f"Selected: {[ep['episode'] for ep in selected]}")
    return selected

async def get_video_sources(session, ep):
    for attempt in range(RETRIES):
        try:
            print(f"Fetching sources for EP {ep['episode']} (try {attempt+1})")

            session.cookie_jar.update_cookies({"key": ep["id"]})

            async with session.get("https://animeheaven.me/gate.php") as resp:
                html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")

            sources = [
                s.get("src")
                for s in soup.find_all("source")
                if s.get("src") and "video.mp4" in s.get("src")
            ]

            if sources:
                return {
                    "episode": ep["episode"],
                    "sources": sources
                }

        except Exception:
            print(f"Retry {attempt+1} EP {ep['episode']}")

        await asyncio.sleep(1)

    print(f"Failed sources EP {ep['episode']}")
    return None

async def download_episode(session, ep_data):
    ep = ep_data["episode"]
    filename = os.path.join(DOWNLOAD_DIR, f"Episode_{ep}.mp4")

    if os.path.exists(filename):
        print(f"Skipping EP {ep}")
        return

    for url in ep_data["sources"]:
        for attempt in range(RETRIES):
            try:
                existing_size = 0

                if os.path.exists(filename):
                    existing_size = os.path.getsize(filename)

                headers = HEADERS.copy()

                if existing_size > 0:
                    headers["Range"] = f"bytes={existing_size}-"
                    print(f"Resuming EP {ep}")
                else:
                    print(f"\nDownloading EP {ep} (try {attempt+1})")

                timeout = aiohttp.ClientTimeout(total=None, sock_read=120)

                async with session.get(url, headers=headers, timeout=timeout) as resp:

                    if resp.status in [200, 206]:
                        total_size = int(resp.headers.get("content-length", 0)) + existing_size

                        mode = "ab" if existing_size > 0 else "wb"

                        with open(filename, mode) as f:
                            with tqdm(
                                total=total_size,
                                initial=existing_size,
                                unit="B",
                                unit_scale=True,
                                desc=f"Ep {ep}",
                            ) as pbar:

                                async for chunk in resp.content.iter_chunked(256 * 1024):
                                    if chunk:
                                        f.write(chunk)
                                        pbar.update(len(chunk))

                        print(f"Finished EP {ep}")
                        return

            except asyncio.TimeoutError:
                print(f"Timeout EP {ep}")
            except asyncio.CancelledError:
                print(f"Interrupted EP {ep}")
            except Exception as e:
                print(f"Error EP {ep}: {e}")

            await asyncio.sleep(2)

    print(f"Failed EP {ep}")

async def main():
    print("\nBATCHED DOWNLOADER START\n")

    url = input("URL: ")
    start = int(input("Start: "))
    end = int(input("End: "))

    episodes = get_episodes(url)
    selected = filter_range(episodes, start, end)

    async with aiohttp.ClientSession(headers=HEADERS) as session:

        video_data = []

        for ep in selected:
            data = await get_video_sources(session, ep)
            if data:
                video_data.append(data)
            await asyncio.sleep(0.5)

        video_data.sort(key=lambda x: x["episode"])

        print(f"\nReady to download {len(video_data)} episodes\n")

        for i in range(0, len(video_data), BATCH_SIZE):
            batch = video_data[i:i + BATCH_SIZE]

            print(f"\nBatch {i//BATCH_SIZE + 1}: {[ep['episode'] for ep in batch]}")

            tasks = [
                download_episode(session, ep)
                for ep in batch
            ]

            await asyncio.gather(*tasks)

            print("Cooling down...\n")
            await asyncio.sleep(3)

    print("\nDONE")

if __name__ == "__main__":
    asyncio.run(main())