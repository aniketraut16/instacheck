import json
import os
from app.steps.step_1_get_url_from_link import get_link_from_url
from app.steps.step_2_save_video_and_audio_locally import save_video_and_audio_locally
from app.steps.step_3_get_audio_transcription import audio_to_text
from app.steps.claims_extractor import extract_claims

def load_data():
    """Load existing data from db/data.json"""
    if os.path.exists('db/data.json'):
        try:
            with open('db/data.json', 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_data(data):
    """Save data to db/data.json"""
    os.makedirs('db', exist_ok=True)
    with open('db/data.json', 'w') as f:
        json.dump(data, f, indent=2)

async def check_authenticity(url: str, log: bool = False):
    # Load existing data
    data = load_data()
    
    # Use URL as key for caching
    url_key = url.strip()
    
    if log:
        results = {}

    # Check if we already have complete results for this URL
    if url_key in data and data[url_key].get('claims'):
        if log:
            print("Found cached results for this URL")
            return data[url_key]
        return data[url_key]['claims']

    # Initialize entry for this URL if it doesn't exist
    if url_key not in data:
        data[url_key] = {}

    # get the link from the url
    if log:
        print("Getting link from url")
    
    # Check if we already have the link
    if 'link' not in data[url_key]:
        link = get_link_from_url(url)
        data[url_key]['link'] = link
        save_data(data)
    else:
        link = data[url_key]['link']
        if log:
            print("Using cached link")
    
    if log:
        results['link'] = link
        if link.get('success'):
            print("Link found")
        else:
            print("Link not found")
    if not link.get('success'):
        if log:
            results['final'] = link
            return results
        return link
        

    # save the video and audio locally
    if log:
        print("Saving video and audio locally")
    
    # Check if we already have video and audio
    if 'video_and_audio' not in data[url_key]:
        video_and_audio = save_video_and_audio_locally(link['videoUrl'], link['filename'], log)
        data[url_key]['video_and_audio'] = video_and_audio
        save_data(data)
    else:
        video_and_audio = data[url_key]['video_and_audio']
        if log:
            print("Using cached video and audio")
    
    if log:
        results['video_and_audio'] = video_and_audio
        if video_and_audio.get('success'):
            print("Video and audio saved locally")
        else:
            print("Failed to save video and audio locally")
    if not video_and_audio.get('success'):
        if log:
            results['final'] = video_and_audio
            return results
        return video_and_audio

    # get the transcription of the audio
    if log:
        print("Getting transcription of audio")
    
    # Check if we already have transcription
    if 'transcription' not in data[url_key]:
        transcription = audio_to_text(video_and_audio['audio'])
        data[url_key]['transcription'] = transcription
        save_data(data)
    else:
        transcription = data[url_key]['transcription']
        if log:
            print("Using cached transcription")
    
    if log:
        results['transcription'] = transcription
        if transcription:
            print("Transcription generated")
        else:
            print("Failed to get transcription")
    if not transcription:
        fail_msg = {'success': False, 'message': 'Failed to get transcription'}
        if log:
            results['final'] = fail_msg
            return results
        return fail_msg

    # Extract claims
    if 'claims' not in data[url_key]:
        claims = extract_claims(transcription)
        data[url_key]['claims'] = claims
        save_data(data)
    else:
        claims = data[url_key]['claims']
        if log:
            print("Using cached claims")
    
    if log:
        results['claims'] = claims
        if claims:
            print("Claims extracted")
        else:
            print("Failed to extract claims")
        return results
    return claims