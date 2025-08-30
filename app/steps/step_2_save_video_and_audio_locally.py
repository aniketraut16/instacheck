import os
import ffmpeg
from audio_extract import extract_audio
import subprocess
import requests
from pathlib import Path

ROOT_DIR = Path.cwd() / "reels"
VIDEO_DIR = ROOT_DIR / "video"
AUDIO_DIR = ROOT_DIR / "audio"

for d in [ROOT_DIR, VIDEO_DIR, AUDIO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def check_ffmpeg_installation() -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def save_video_and_audio_locally(url: str, filename: str,log: bool = False):
    try:
        if not url or not filename:
            return {"success": False}

        # Check if video and audio already exist
        video_path = VIDEO_DIR / filename
        video_name = os.path.splitext(filename)[0]
        audio_path = AUDIO_DIR / f"{video_name}.mp3"
        
        if video_path.exists() and audio_path.exists():
            if log:
                print("Video and audio already exist, skipping download and processing")
            video_url = f"/reels/video/{filename}"
            audio_filename = f"{video_name}.mp3"
            audio_url = f"/reels/audio/{audio_filename}"
            return {
                "success": True,
                "video": video_url,
                "audio": audio_url
            }

        if log:
            print("Downloading video")
        video_path = download_reel(url, filename)
        if log:
            if video_path:
                print("Video downloaded")
            else:
                print("Failed to download video")
        if log:
            print("Converting video to audio")
        if not video_path:
            return {"success": False}

        if log:
            print("Compressing video")
        audio_path = video_to_audio(video_path)
        if not audio_path:
            return {"success": False}
        
        video_url = f"/reels/video/{filename}"
        audio_filename = os.path.basename(audio_path)
        audio_url = f"/reels/audio/{audio_filename}"

        return {
            "success": True,
            "video": video_url,
            "audio": audio_url
        }
    except Exception:
        return {"success": False}

def download_reel(url: str, filename: str) -> str:
    try:
        file_path = VIDEO_DIR / filename
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, stream=True, timeout=30, headers=headers)
        response.raise_for_status()
        with open(file_path, 'wb') as writer:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    writer.write(chunk)
        return str(file_path)
    except Exception:
        return None

def video_to_audio(video_path: str) -> str:
    try:
        video_filename = os.path.basename(video_path)
        video_name = os.path.splitext(video_filename)[0]
        audio_path = AUDIO_DIR / f"{video_name}.mp3"
        if audio_path.exists():
            return str(audio_path)
        if not os.path.exists(video_path):
            return None
        extract_audio(input_path=video_path, output_path=str(audio_path))
        return str(audio_path)
    except Exception:
        return None
