import json
import os
import logging
from modules.wed_data_extractor.pipeline import get_wed_data
from app.steps.get_url_from_link import get_link_from_url
from app.steps.save_audio_locally import save_audio_locally
from app.steps.get_audio_transcription import audio_to_text
from app.steps.claims_extractor import extract_claims
from app.steps.claim_verifier import verify_claim

# Setup logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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

async def check_authenticity(url: str):
    # Load existing data
    data = load_data()
    

    url_key = url.strip()
    
    results = {}

    # Initialize entry for this URL if it doesn't exist
    if url_key not in data:
        data[url_key] = {}

    # get the link from the url
    logger.info("Getting link from url")
    
    # Check if we already have the link
    if 'link' not in data[url_key]:
        link = get_link_from_url(url)
        data[url_key]['link'] = link
        save_data(data)
    else:
        link = data[url_key]['link']
        logger.info("Using cached link")
    
    results['link'] = link
    if link.get('success'):
        logger.info("Link found")
    else:
        logger.error("Link not found")
    if not link.get('success'):
        results['final'] = link
        return results
        

    # save the video and audio locally
    logger.info("Saving video and audio locally")
    
    # Check if we already have video and audio
    if 'video_and_audio' not in data[url_key]:
        video_and_audio = save_audio_locally(link['videoUrl'], link['filename'])
        data[url_key]['video_and_audio'] = video_and_audio
        save_data(data)
    else:
        video_and_audio = data[url_key]['video_and_audio']
        logger.info("Using cached video and audio")
    
    results['video_and_audio'] = video_and_audio
    if video_and_audio.get('success'):
        logger.info("Video and audio saved locally")
    else:
        logger.error("Failed to save video and audio locally")
    if not video_and_audio.get('success'):
        results['final'] = video_and_audio
        return results

    # get the transcription of the audio
    logger.info("Getting transcription of audio")
    
    # Check if we already have transcription
    if 'transcription' not in data[url_key]:
        transcription = audio_to_text(video_and_audio['audio'])
        data[url_key]['transcription'] = transcription
        save_data(data)
    else:
        transcription = data[url_key]['transcription']
        logger.info("Using cached transcription")
    
    results['transcription'] = transcription
    if transcription:
        logger.info("Transcription generated")
    else:
        logger.error("Failed to get transcription")
    if not transcription:
        fail_msg = {'success': False, 'message': 'Failed to get transcription'}
        results['final'] = fail_msg
        return results
    
    # Check if we already have claims
    if 'claims' not in data[url_key]:
        claims = extract_claims(transcription)
        data[url_key]['claims'] = claims
        save_data(data)
    else:
        claims = data[url_key]['claims']
        logger.info("Using cached claims")
    logger.info(f" {len(claims)} Claims extracted")
    relavent_content = []
    for claim in claims:
        content = await get_wed_data(claim['claim'])
        relavent_content.append({'claim': claim['claim'], 'content': content})
        evidence_list = [result['snippet'] for result in content['results']]
        result = verify_claim(claim['claim'], evidence_list)
        relavent_content.append({ 'result': result})
    results['relavent_content'] = relavent_content
    if relavent_content:
        logger.info("Relavent content found")
    else:
        logger.error("Failed to find relavent content")
    if not relavent_content:
        fail_msg = {'success': False, 'message': 'Failed to find relavent content'}
        results['final'] = fail_msg
        return results
    return results