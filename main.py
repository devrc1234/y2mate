from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import time

app = FastAPI()

# Allow Blogger or any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create downloads folder if missing
if not os.path.exists('downloads'):
    os.makedirs('downloads')

def clean_old_files(folder='downloads', max_age_minutes=60):
    now = time.time()
    max_age_seconds = max_age_minutes * 60

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                os.remove(file_path)

@app.post("/download")
async def download_video(request: Request):
    try:
        data = await request.json()
        url = data.get("url")

        if "?" in url:
            url = url.split("?")[0]

        # Clean old files
        clean_old_files()

        # Save files before downloading
        existing_files = set(os.listdir('downloads'))

        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'format': 'bestvideo+bestaudio/best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Find new downloaded file
        new_files = set(os.listdir('downloads')) - existing_files
        if not new_files:
            return JSONResponse(content={"error": "No file downloaded."})

        file_path = max(
            [os.path.join('downloads', f) for f in new_files],
            key=os.path.getmtime
        )

        return FileResponse(file_path, media_type='application/octet-stream', filename=os.path.basename(file_path))

    except Exception as e:
        return JSONResponse(content={"error": str(e)})
