
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os

app = FastAPI()

@app.post("/download")
async def download_video(request: Request):
    data = await request.json()
    video_url = data.get("url")

    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        return JSONResponse(content={"filename": os.path.basename(filename)})

    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.get("/file/{filename}")
async def get_file(filename: str):
    file_path = f"downloads/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='video/mp4', filename=filename)
    else:
        return JSONResponse(content={"error": "File not found"})
