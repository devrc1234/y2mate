from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/download")
async def download_video(request: Request):
    data = await request.json()
    video_url = data.get("url")
    
    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'merge_output_format': 'mp4',  # Force final file to mp4
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        file_path = filename
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='video/mp4', filename=os.path.basename(file_path))
        else:
            return JSONResponse(content={"error": "File not found"})

    except Exception as e:
        return JSONResponse(content={"error": str(e)})
