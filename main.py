from fastapi import FastAPI, Query
from yt_dlp import YoutubeDL
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Self-Hosted Music API")

# Allow your bot to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# yt-dlp options for audio streaming
ydl_opts_audio = {
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": False,
}

# yt-dlp options for video streaming
ydl_opts_video = {
    "format": "best",
    "quiet": True,
    "extract_flat": False,
}


@app.get("/get_audio")
def get_audio(url: str = Query(..., description="YouTube video URL")):
    """
    Returns direct audio URL and metadata for a YouTube video.
    """
    try:
        with YoutubeDL(ydl_opts_audio) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get("url")
            title = info.get("title")
            duration = info.get("duration")
            thumbnail = info.get("thumbnail")
        return {
            "title": title,
            "audio_url": audio_url,
            "duration": duration,
            "thumbnail": thumbnail
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/get_video")
def get_video(url: str = Query(..., description="YouTube video URL")):
    """
    Returns direct video URL and metadata for a YouTube video.
    """
    try:
        with YoutubeDL(ydl_opts_video) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get("url")
            title = info.get("title")
            duration = info.get("duration")
            thumbnail = info.get("thumbnail")
        return {
            "title": title,
            "video_url": video_url,
            "duration": duration,
            "thumbnail": thumbnail
        }
    except Exception as e:
        return {"error": str(e)}
