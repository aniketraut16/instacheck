from app.steps.step_1_get_url_from_link import get_link_from_url
from app.steps.step_2_save_video_and_audio_locally import save_video_and_audio_locally
from app.steps.step_3_get_audio_transcription import audio_to_text

async def check_authenticity(url: str, log: bool = False):
    if log:
        results = {}

    # get the link from the url
    if log:
        print("Getting link from url")
    link = get_link_from_url(url)
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
    video_and_audio = save_video_and_audio_locally(link['videoUrl'], link['filename'], log)
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
    transcription = audio_to_text(video_and_audio['audio'])
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

    return transcription