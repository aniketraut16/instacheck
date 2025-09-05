from fastapi import WebSocket
import json
import os
import logging
from modules.wed_data_extractor.pipeline import get_wed_data
from app.steps.get_url_from_link import get_link_from_url
from app.steps.save_audio_locally import save_audio_locally
from app.steps.get_audio_transcription import audio_to_text
from app.steps.claims_extractor import extract_claims
from app.steps.claim_verifier import verify_claim
from app.steps.responce_generator import generate_responce

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_data():
    if os.path.exists('db/data.json'):
        try:
            with open('db/data.json', 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_data(data):
    os.makedirs('db', exist_ok=True)
    with open('db/data.json', 'w') as f:
        json.dump(data, f, indent=2)

async def check_authenticity(websocket: WebSocket = None,url: str = None):
    data = load_data()

    url_key = url.strip()
    
    results = {}

    if url_key not in data:
        data[url_key] = {}

    logger.info("Getting link from url")
    await websocket.send_text(json.dumps({"step": "processing", "message": "Extracting link from url"}))
    
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
        await websocket.send_text(json.dumps({"step": "success", "message": "Extracted link from url"}))
    else:
        logger.error("Link not found")
        await websocket.send_text(json.dumps({"step": "error", "message": "Invalid URL"}))
    if not link.get('success'):
        results['final'] = link
        return results
        

    logger.info("Saving video and audio locally")
    await websocket.send_text(json.dumps({"step": "processing", "message": "Saving video and audio locally"}))
    
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
        await websocket.send_text(json.dumps({"step": "success", "message": "Video and audio saved locally"}))
    else:
        logger.error("Failed to save video and audio locally")
        await websocket.send_text(json.dumps({"step": "error", "message": "Failed to save video and audio locally"}))
    if not video_and_audio.get('success'):
        results['final'] = video_and_audio
        return results

    logger.info("Getting transcription of audio")
    await websocket.send_text(json.dumps({"step": "processing", "message": "Getting audio transcription"}))
    
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
        await websocket.send_text(json.dumps({"step": "success", "message": "Audio transcription generated"}))
    else:
        logger.error("Failed to get transcription")
        await websocket.send_text(json.dumps({"step": "warning", "message": "Failed to get audio transcription, proceeding with video analysis"}))
    if not transcription:
        fail_msg = {'success': False, 'message': 'Failed to get transcription'}
        results['final'] = fail_msg
        return results
    
    await websocket.send_text(json.dumps({"step": "processing", "message": "Extracting claims from transcription"}))
    claims = await extract_claims(transcription)
    logger.info(f" {len(claims)} Claims extracted")

    await websocket.send_text(json.dumps({"step": "success", "message": f"There are {len(claims)} claims made in the video"}))
    if not claims:
        fail_msg = {'success': False, 'message': 'Failed to extract claims'}
        results['final'] = fail_msg
        await websocket.send_text(json.dumps({"step": "error", "message": "There are no claims made in the video"}))
        return 
    
    await websocket.send_text(json.dumps({"step": "processing", "message": "Verifying claims with web data"}))
    relavent_content = []
    for claim in claims:
        content = await get_wed_data(claim['claim'],websocket=websocket)
        evidence_list = [result['snippet'] for result in content['results']]
        await websocket.send_text(json.dumps({"step": "processing", "message": f"Verifying claim: {claim['claim'][:100]}..."}))
        result = await verify_claim(claim['claim'], evidence_list)
        await websocket.send_text(json.dumps({"step": "success", "message": f"Claim: {claim['claim'][:100]}... verified"}))
        relavent_content.append({'claim': claim['claim'], 'content': content, 'result': result})
    results['relavent_content'] = relavent_content
    if relavent_content:
        logger.info("Relavent content found")
        await websocket.send_text(json.dumps({"step": "success", "message": "Claims verified with web data"}))
    else:
        logger.error("Failed to find relavent content")
        await websocket.send_text(json.dumps({"step": "error", "message": "Failed to find relevant content"}))
    if not relavent_content:
        fail_msg = {'success': False, 'message': 'Failed to find relavent content'}
        results['final'] = fail_msg
        return results
    
    await websocket.send_text(json.dumps({"step": "processing", "message": "Generating final response"}))
    formatted_data = [{'claim': item['claim'], 'verfication_result': item['result']} for item in relavent_content]
    responce = await generate_responce(formatted_data)
    results['responce'] = responce
    if responce:
        logger.info("Responce generated")
    else:
        logger.error("Failed to generate responce")
        await websocket.send_text(json.dumps({"step": "error", "message": "Failed to generate response"}))
    if not responce:
        fail_msg = {'success': False, 'message': 'Failed to generate responce'}
        results['final'] = fail_msg
        return results
    final_msg = {
        "final_msg":responce,
        "claims": []
    }
    for items in relavent_content:
        item = {
            'claim': items['claim'],
            'verfication_result': items['result'],
            'sources': []
        }
        for source in items['content']['results']:
            item['sources'].append(source['url'])
        final_msg['claims'].append(item)
        print(final_msg)
    await websocket.send_text(json.dumps({"step": "completed", "message": "Final response generated", "response": final_msg}))
    return 