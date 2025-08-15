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

COOKIES_FILE = "cookies.txt"
cache = {}
CACHE_EXPIRY = 300  # 5 minutes

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

def _extract_info_sync(query: str, type_: str):
    """
    Extract info from YouTube URL or search query.
    If `query` is not a valid URL, treat it as a search query.
    """
    now = time.time()
    if query in cache:
        cached_data, timestamp = cache[query]
        if now - timestamp < CACHE_EXPIRY:
            return cached_data
        else:
            del cache[query]

    # Detect if query is a URL or search term
    if not query.startswith("http"):
        query = f"ytsearch1:{query}"  # Take first search result

    opts = ydl_opts("bestaudio/best" if type_ == "audio" else "best")
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=False)
        # If it's a search, yt-dlp returns 'entries'
        if "entries" in info:
            info = info["entries"][0]

    result = {
        "title": info.get("title"),
        f"{type_}_url": info.get("url"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail")
    }

    cache[query] = (result, now)
    return result

async def extract_info(query: str, type_: str):
    try:
        return await run_in_threadpool(lambda: _extract_info_sync(query, type_))
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_audio")
async def get_audio(query: str = Query(..., description="YouTube URL or search query")):
    return await extract_info(query, "audio")

@app.get("/get_video")
async def get_video(query: str = Query(..., description="YouTube URL or search query")):
    return await extract_info(query, "video")

async def cache_cleaner():
    while True:
        now = time.time()
        to_delete = [key for key, (_, ts) in cache.items() if now - ts >= CACHE_EXPIRY]
        for key in to_delete:
            del cache[key]
        await asyncio.sleep(CACHE_EXPIRY // 2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cache_cleaner())
