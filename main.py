from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL
from starlette.concurrency import run_in_threadpool
import time
import asyncio

app = FastAPI(title="Time-Limited Cache Music API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cookies file path
COOKIES_FILE = "cookies.txt"

# Cache dictionary
cache = {}
CACHE_EXPIRY = 300  # seconds, i.e., 5 minutes

# yt-dlp options
def ydl_opts(format_type: str):
    return {
        "format": format_type,
        "quiet": True,
        "cookiefile": COOKIES_FILE,
        "noplaylist": True,
        "nocheckcertificate": True,
        "extract_flat": False,
        "geo_bypass": True,
        "cachedir": False
    }

def _extract_info_sync(url: str, type_: str):
    # Check cache
    now = time.time()
    if url in cache:
        cached_data, timestamp = cache[url]
        if now - timestamp < CACHE_EXPIRY:
            return cached_data
        else:
            del cache[url]  # remove expired cache

    # Extract using yt-dlp
    opts = ydl_opts("bestaudio/best" if type_ == "audio" else "best")
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    result = {
        "title": info.get("title"),
        f"{type_}_url": info.get("url"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail")
    }

    # Save to cache
    cache[url] = (result, now)
    return result

# Async wrapper
async def extract_info(url: str, type_: str):
    try:
        return await run_in_threadpool(lambda: _extract_info_sync(url, type_))
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_audio")
async def get_audio(url: str = Query(..., description="YouTube video URL")):
    return await extract_info(url, "audio")

@app.get("/get_video")
async def get_video(url: str = Query(..., description="YouTube video URL")):
    return await extract_info(url, "video")

# Optional: periodic cleanup for expired cache (runs in background)
async def cache_cleaner():
    while True:
        now = time.time()
        to_delete = [url for url, (_, ts) in cache.items() if now - ts >= CACHE_EXPIRY]
        for url in to_delete:
            del cache[url]
        await asyncio.sleep(CACHE_EXPIRY // 2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cache_cleaner())
