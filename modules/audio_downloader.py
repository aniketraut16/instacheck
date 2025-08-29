import os
import requests
from pathlib import Path
from audio_extract import extract_audio

ROOT_DIR = Path.cwd() / "reels"
AUDIO_DIR = ROOT_DIR / "audio"
TEMP_DIR = ROOT_DIR / "temp"

for d in [ROOT_DIR, AUDIO_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def save_audio_only(url: str, filename: str, log: bool = False):
    """
    Downloads a video from the given URL to a temporary location,
    extracts audio as mp3, saves it to AUDIO_DIR, and deletes the temp video.
    Returns only the audio file URL.
    """
    try:
        if not url or not filename:
            return {"success": False}

        video_name = os.path.splitext(filename)[0]
        audio_path = AUDIO_DIR / f"{video_name}.mp3"

        if audio_path.exists():
            if log:
                print("Audio already exists, skipping download and extraction")
            audio_url = f"/reels/audio/{audio_path.name}"
            return {
                "success": True,
                "audio": audio_url
            }

        temp_video_path = TEMP_DIR / filename

        if log:
            print("Downloading video for audio extraction")
        if not download_temp_video(url, temp_video_path):
            if log:
                print("Failed to download video")
            return {"success": False}

        if log:
            print("Extracting audio from video")
        if not extract_audio_from_video(temp_video_path, audio_path):
            if log:
                print("Failed to extract audio")
            if temp_video_path.exists():
                temp_video_path.unlink()
            return {"success": False}

        if temp_video_path.exists():
            temp_video_path.unlink()

        audio_url = f"/reels/audio/{audio_path.name}"
        return {
            "success": True,
            "audio": audio_url
        }
    except Exception:
        return {"success": False}

def download_temp_video(url: str, temp_video_path: Path) -> bool:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, stream=True, timeout=30, headers=headers)
        response.raise_for_status()
        with open(temp_video_path, 'wb') as writer:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    writer.write(chunk)
        return True
    except Exception:
        return False

def extract_audio_from_video(video_path: Path, audio_path: Path) -> bool:
    try:
        if not video_path.exists():
            return False
        extract_audio(input_path=str(video_path), output_path=str(audio_path))
        return audio_path.exists()
    except Exception:
        return False
