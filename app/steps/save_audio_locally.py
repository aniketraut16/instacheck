import os
from audio_extract import extract_audio
import subprocess
import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

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

def save_audio_locally(url: str, filename: str):
    try:
        if not url or not filename:
            return {"success": False}

        # Check if audio already exists
        video_name = os.path.splitext(filename)[0]
        audio_path = AUDIO_DIR / f"{video_name}.mp3"
        
        if audio_path.exists():
            logger.info("Audio already exists, skipping download and processing")
            audio_filename = f"{video_name}.mp3"
            audio_url = f"/reels/audio/{audio_filename}"
            return {
                "success": True,
                "audio": audio_url
            }

        logger.info("Downloading video")
        video_path = download_reel(url, filename)
        if video_path:
            logger.info("Video downloaded")
        else:
            logger.error("Failed to download video")
            
        if not video_path:
            return {"success": False}

        logger.info("Converting video to audio")
        audio_path = video_to_audio(video_path)
        
        # Delete the video file after extracting audio
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info("Video file deleted after audio extraction")
        except Exception as e:
            logger.warning(f"Failed to delete video file: {e}")
        
        if not audio_path:
            return {"success": False}
        
        audio_filename = os.path.basename(audio_path)
        audio_url = f"/reels/audio/{audio_filename}"

        return {
            "success": True,
            "audio": audio_url
        }
    except Exception as e:
        logger.error(f"Error in save_audio_locally: {e}")
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
    except Exception as e:
        logger.error(f"Error downloading reel: {e}")
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
    except Exception as e:
        logger.error(f"Error converting video to audio: {e}")
        return None
