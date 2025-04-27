from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os

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

@app.post("/formats")
async def get_formats(request: Request):
    """
    Get available formats for a given video URL
    """
    try:
        data = await request.json()
        url = data.get("url")

        if "?" in url:
            url = url.split("?")[0]

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'force_generic_extractor': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        formats = []
        for f in info.get('formats', []):
            # Only return formats with height (video) or audio
            if f.get('height') or (f.get('acodec') != 'none' and f.get('vcodec') == 'none'):
                formats.append({
                    'format_id': f['format_id'],
                    'ext': f['ext'],
                    'height': f.get('height'),
                    'note': f.get('format_note') or f.get('format')
                })

        return {"formats": formats}

    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.post("/download")
async def download_video(request: Request):
    """
    Download the video/audio in the selected format
    """
    try:
        data = await request.json()
        url = data.get("url")
        format_id = data.get("format_id")

        if "?" in url:
            url = url.split("?")[0]

        # Define output template
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'format': format_id
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        file_path = filename

        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/octet-stream', filename=os.path.basename(file_path))
        else:
            return JSONResponse(content={"error": "File not found"})

    except Exception as e:
        return JSONResponse(content={"error": str(e)})
