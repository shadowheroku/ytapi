from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from yt_dlp import YoutubeDL
from starlette.concurrency import run_in_threadpool
import time
import asyncio
import os
from typing import Optional

app = FastAPI(title="Enhanced YouTube Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
COOKIES_FILE = "cookies.txt"
DOWNLOAD_FOLDER = "downloads"
CACHE_EXPIRY = 300  # 5 minutes
MAX_FILE_SIZE_MB = 250  # Maximum allowed file size in MB

# Ensure download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Cache system
cache = {}

def ydl_opts(format_type: str, extract_audio: bool = False):
    """Generate yt-dlp options dictionary"""
    opts = {
        "format": format_type,
        "quiet": True,
        "cookiefile": COOKIES_FILE,
        "noplaylist": True,
        "nocheckcertificate": True,
        "extract_flat": False,
        "geo_bypass": True,
        "cachedir": False,
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(id)s.%(ext)s"),
    }
    if extract_audio:
        opts["postprocessors"] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    return opts

async def _download_media(video_id: str, media_type: str) -> Optional[str]:
    """Download media file and return local path"""
    format_type = "bestaudio/best" if media_type == "audio" else "bestvideo[height<=720]+bestaudio"
    extract_audio = media_type == "audio"
    
    ydl_options = ydl_opts(format_type, extract_audio)
    
    try:
        with YoutubeDL(ydl_options) as ydl:
            info = await run_in_threadpool(
                lambda: ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            )
            
            # Determine the downloaded file path
            ext = "mp3" if extract_audio else info['ext']
            file_path = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.{ext}")
            
            if os.path.exists(file_path):
                return file_path
            return None
    except Exception as e:
        print(f"Download failed: {e}")
        return None

@app.get("/get_audio")
async def get_audio(
    query: str = Query(..., description="YouTube URL or video ID"),
    api: Optional[str] = Query(None, description="API key for authentication")
):
    """Endpoint compatible with both query string and video ID"""
    # Extract video ID if URL is provided
    if "youtube.com" in query or "youtu.be" in query:
        video_id = extract_video_id(query)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    else:
        video_id = query  # Assume it's already a video ID
    
    # Check cache first
    if video_id in cache:
        cached_data, timestamp = cache[video_id]
        if time.time() - timestamp < CACHE_EXPIRY:
            return cached_data
    
    # Download the audio
    file_path = await _download_media(video_id, "audio")
    if not file_path:
        raise HTTPException(status_code=500, detail="Failed to download audio")
    
    # Prepare response
    result = {
        "status": "done",
        "link": f"/download/{os.path.basename(file_path)}",
        "format": "mp3",
        "video_id": video_id
    }
    
    # Update cache
    cache[video_id] = (result, time.time())
    
    return result

@app.get("/get_audio/song/{video_id}")
async def get_audio_by_id(
    video_id: str,
    api: Optional[str] = Query(None, description="API key for authentication")
):
    """Alternative endpoint that matches your client's expectations"""
    return await get_audio(video_id, api)

@app.get("/get_video")
async def get_video(
    query: str = Query(..., description="YouTube URL or video ID"),
    api: Optional[str] = Query(None, description="API key for authentication")
):
    """Video download endpoint"""
    # Extract video ID if URL is provided
    if "youtube.com" in query or "youtu.be" in query:
        video_id = extract_video_id(query)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    else:
        video_id = query
    
    # Check cache first
    if video_id in cache:
        cached_data, timestamp = cache[video_id]
        if time.time() - timestamp < CACHE_EXPIRY:
            return cached_data
    
    # Download the video
    file_path = await _download_media(video_id, "video")
    if not file_path:
        raise HTTPException(status_code=500, detail="Failed to download video")
    
    # Prepare response
    result = {
        "status": "done",
        "link": f"/download/{os.path.basename(file_path)}",
        "format": "mp4",
        "video_id": video_id
    }
    
    # Update cache
    cache[video_id] = (result, time.time())
    
    return result

@app.get("/get_video/song/{video_id}")
async def get_video_by_id(
    video_id: str,
    api: Optional[str] = Query(None, description="API key for authentication")
):
    """Alternative endpoint that matches your client's expectations"""
    return await get_video(video_id, api)

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Serve downloaded files"""
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL"""
    # Handle various YouTube URL formats
    patterns = [
        r"youtube\.com/watch\?v=([^&]+)",
        r"youtu\.be/([^?]+)",
        r"youtube\.com/embed/([^/]+)",
        r"youtube\.com/v/([^/]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def cache_cleaner():
    """Periodically clean expired cache entries"""
    while True:
        now = time.time()
        to_delete = [
            key for key, (_, timestamp) in cache.items() 
            if now - timestamp >= CACHE_EXPIRY
        ]
        for key in to_delete:
            del cache[key]
        
        # Clean up old download files
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            file_age = now - os.path.getmtime(file_path)
            if file_age > CACHE_EXPIRY:
                try:
                    os.remove(file_path)
                except:
                    pass
        
        await asyncio.sleep(CACHE_EXPIRY // 2)

@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    asyncio.create_task(cache_cleaner())
