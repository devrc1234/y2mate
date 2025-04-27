from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os

app = FastAPI()

# Allow Blogger frontend (CORS)
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
    selected_format = data.get("format", "best")  # Default to best

    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        # Clean the URL if extra parameters exist
        if "?" in video_url:
            video_url = video_url.split("?")[0]

        # Base yt-dlp options
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # Save path
            'noplaylist': True,                        # Only download single video
            'quiet': True,                             # Reduce log noise
            'force_generic_extractor': False,          # Default
        }

        # Adjust based on user format selection
        if selected_format == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        elif selected_format in ["144", "360", "480", "720", "1080"]:
            ydl_opts.update({
                'format': f'bestvideo[height<={selected_format}]+bestaudio/best/best',
            })
        else:
            ydl_opts.update({
                'format': 'best',
            })

        # Start download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        # File path handling
        if selected_format == "mp3":
            file_path = filename.rsplit('.', 1)[0] + ".mp3"
        else:
            file_path = filename

        # Serve the file
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/octet-stream', filename=os.path.basename(file_path))
        else:
            return JSONResponse(content={"error": "File not found"})

    except Exception as e:
        return JSONResponse(content={"error": str(e)})
