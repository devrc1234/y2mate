from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import time

app = FastAPI()

# Allow CORS (Frontend can call Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create 'downloads' folder if missing
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

@app.post("/formats")
async def get_formats(request: Request):
    """
    Get available video and audio formats from a URL
    """
    try:
        data = await request.json()
        url = data.get("url")
        if not url:
            return JSONResponse(content={"error": "URL missing"})

        if "?" in url:
            url = url.split("?")[0]

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get('formats', []):
            if (f.get('height') and f.get('vcodec') != 'none') or (f.get('acodec') != 'none' and f.get('vcodec') == 'none'):
                size = f.get('filesize') or f.get('filesize_approx')
                formats.append({
                    'format_id': f['format_id'],
                    'ext': f['ext'],
                    'height': f.get('height'),
                    'note': f.get('format_note') or f.get('format'),
                    'filesize': size
                })

        return {"formats": formats}

    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.post("/download")
async def download_video(request: Request):
    """
    Download selected video/audio format
    """
    try:
        data = await request.json()
        url = data.get("url")
        format_id = data.get("format_id")

        if not url or not format_id:
            return JSONResponse(content={"error": "URL or Format ID missing"})

        if "?" in url:
            url = url.split("?")[0]

        # Clean old files
        clean_old_files()

        existing_files = set(os.listdir('downloads'))

        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'format': f"{format_id}+bestaudio/best" if format_id.isdigit() else format_id,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

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
