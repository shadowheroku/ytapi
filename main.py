from fastapi import FastAPI, Query
from yt_dlp import YoutubeDL
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Self-Hosted Music API with Cookies")

# Allow your bot to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to cookies file
YOUTUBE_COOKIES = {
    "HSID": "A6ZfyYUep0Np9MQw1",
    "SSID": "Agye2vfnm-dkrucAt",
    "APISID": "kz7E2afizJqVhEVm/AO-71rWNJbOrr03lY",
    "SAPISID": "7fJ-lvyh4STWCBvz/Adsi-bKLNu39ch5Wh",
    "__Secure-1PAPISID": "7fJ-lvyh4STWCBvz/Adsi-bKLNu39ch5Wh",
    "__Secure-3PAPISID": "7fJ-lvyh4STWCBvz/Adsi-bKLNu39ch5Wh",
    "LOGIN_INFO": "AFmmF2swRAIgDG6w06DO6jzGmopZi4YYYaDhOoEY4gB5zstRy3l5-zkCIHcUr0KOk-7uvH446znpbL79FTkyI348bB0GXULReZdc:QUQ3MjNmeVpIUXUzSXhOV0l1aHRNMFV2dVE0ckJjRG15VnFPVnNRWEh3UUpGQnpyX1RNZDZtRkduZ0pxclducjMzOVEwcWI2dWJPY3BnSnNSd2U0NHRmQlJJYjljY29hcV9iemhKblhUVDN0NGdIQzdOcUVWZmd6M3NtQ20wU1hoUUtsVS1zWENUcDNuU2E2YkM1dU9rREI2NWVDbXB3OVhR",
    "_ga": "GA1.1.1034053585.1745164239",
    "PREF": "f4=4000000&f6=40000000&tz=Asia.Calcutta&f7=150&repeat=NONE&autoplay=true",
    "_ga_VCGEPY40VB": "GS1.1.1745164238.1.1.1745164471.60.0.0",
    "SID": "g.a0000AjzvmDVdcaAaK1FXG6J6NdEurHHeyqSwjCWLIYz3KFegHsV1dE2o6KB33rpb_7g4EETTwACgYKASgSARESFQHGX2Miuat42fzbV_FlDrWm7uO5uhoVAUF8yKpdsOfPj1S0UexoyV_vrSKm0076",
    "__Secure-1PSID": "g.a0000AjzvmDVdcaAaK1FXG6J6NdEurHHeyqSwjCWLIYz3KFegHsVXiz1bbBKw2CtB1qgIa3yMwACgYKATsSARESFQHGX2Mi4Bb47FQb7KtwstoGlnPu5BoVAUF8yKospSKEGprHVlU1MWg9X8OY0076",
    "__Secure-3PSID": "g.a0000AjzvmDVdcaAaK1FXG6J6NdEurHHeyqSwjCWLIYz3KFegHsVD9L5Es1hvyFBrrSUHltu1AACgYKAeASARESFQHGX2Mi3-d_L7JlUeEUkEoBBNB7ixoVAUF8yKqmRh47rBnVkvAEjDwFQBOi0076",
    "__Secure-1PSIDTS": "sidts-CjEB5H03P76CfTuDrEptMyBc4lmS9r9lj00UpSAzq0XGHzTBeVopT-czfu05ofCKmqwjEAA",
    "__Secure-3PSIDTS": "sidts-CjEB5H03P76CfTuDrEptMyBc4lmS9r9lj00UpSAzq0XGHzTBeVopT-czfu05ofCKmqwjEAA",
    "ST-tladcw": "session_logininfo=AFmmF2swRAIgDG6w06DO6jzGmopZi4YYYaDhOoEY4gB5zstRy3l5-zkCIHcUr0KOk-7uvH446znpbL79FTkyI348bB0GXULReZdc%3AQUQ3MjNmeVpIUXUzSXhOV0l1aHRNMFV2dVE0ckJjRG15VnFPVnNRWEh3UUpGQnpyX1RNZDZtRkduZ0pxclducjMzOVEwcWI2dWJPY3BnSnNSd2U0NHRmQlJJYjljY29hcV9iemhKblhUVDN0NGdIQzdOcUVWZmd6M3NtQ20wU1hoUUtsVS1zWENUcDNuU2E2YkM1dU9rREI2NWVDbXB3OVhR",
    "ST-hcbf8d": "session_logininfo=AFmmF2swRAIgDG6w06DO6jzGmopZi4YYYaDhOoEY4gB5zstRy3l5-zkCIHcUr0KOk-7uvH446znpbL79FTkyI348bB0GXULReZdc%3AQUQ3MjNmeVpIUXUzSXhOV0l1aHRNMFV2dVE0ckJjRG15VnFPVnNRWEh3UUpGQnpyX1RNZDZtRkduZ0pxclducjMzOVEwcWI2dWJPY3BnSnNSd2U0NHRmQlJJYjljY29hcV9iemhKblhUVDN0NGdIQzdOcUVWZmd6M3NtQ20wU1hoUUtsVS1zWENUcDNuU2E2YkM1dU9rREI2NWVDbXB3OVhR",
    "CONSISTENCY": "AKreu9ss6A1cWyOBPQIevB5i3CBQpA24lG14GWfx9J8FQEJl_c4TxE0SALvKq_9ZRbZYQZ8tXJL9oPFko9ZJ2DvXaOoixN1XJtAj7Iv7Cp78CI513y-UfdOdYwwBFyG7kBSDCWYKcOReMW1j9IMgEsZl",
    "ST-xuwub9": "session_logininfo=AFmmF2swRAIgDG6w06DO6jzGmopZi4YYYaDhOoEY4gB5zstRy3l5-zkCIHcUr0KOk-7uvH446znpbL79FTkyI348bB0GXULReZdc%3AQUQ3MjNmeVpIUXUzSXhOV0l1aHRNMFV2dVE0ckJjRG15VnFPVnNRWEh3UUpGQnpyX1RNZDZtRkduZ0pxclducjMzOVEwcWI2dWJPY3BnSnNSd2U0NHRmQlJJYjljY29hcV9iemhKblhUVDN0NGdIQzdOcUVWZmd6M3NtQ20wU1hoUUtsVS1zWENUcDNuU2E2YkM1dU9rREI2NWVDbXB3OVhR",
    "NID": "525=o5Zo-6YOpBN6Dzz8e_ZCtBhH9DV-BXeaklxwdxYlaTZIh_kuk4LtDVwjs7b9aOKcB_ZZ4ZKzdnMrtOkRh2nHMrwPsw7uj4ryrqSYXFMQ_9OhFsJgsvNboG7O9XdbqV71HEPPjYvrZpfxzv04l7bfajdk20naPbr0iURXOtqk-oacmlDX3VG9V6yXmoQLJvHJSwDWS8k7Yp3VN36qO1jzFsJusVnKlbA",
    "SIDCC": "AKEyXzXhVeGWqkM8KpthieBpkKNuRM4FJM4I-RC_fgt1zYYkEN9GBTL14_J08Ha4xY39WBUMRmc",
    "__Secure-1PSIDCC": "AKEyXzWYSQQLNFNzUBG65zTPZ9KiNIjJDEnA56Xf0_wWml43d6lVW9mgiTimERxVsMwlvmAAJ2I",
    "__Secure-3PSIDCC": "AKEyXzUbnXc5Ds2goppj666xVEzaeDkzFlptzEhv7KajA3rMRbFSUKI5gCNJA_CHS1RSaQXe8I8",
    "VISITOR_INFO1_LIVE": "PXh3lLWceIU",
    "VISITOR_PRIVACY_METADATA": "CgJJThIEGgAgKQ%3D%3D",
    "YSC": "XLreCjZcX7Q",
    "__Secure-ROLLOUT_TOKEN": "CPWMs-mStNuj7gEQtImonuWvjAMYyfnJ4qiMjwM%3D"
}



# yt-dlp options for audio streaming
ydl_opts_audio = {
    "format": "bestaudio/best",
    "quiet": True,
    "cookies": YOUTUBE_COOKIES,  # Use cookies to bypass YouTube bot checks
}

# yt-dlp options for video streaming
ydl_opts_video = {
    "format": "best",
    "quiet": True,
    "cookies": YOUTUBE_COOKIES,
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
