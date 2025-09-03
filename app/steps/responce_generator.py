from typing import List
import logging
from modules.llm_clients.client import get_llm_client
logger = logging.getLogger(__name__)
async def generate_responce(data: List[dict]) -> str:
    formatted_data = "\n".join([f"Claim: {item['claim']}\nVerfication Result: {item['verfication_result']}" for item in data])
    prompt = f"""You are a video authenticity analyst. After thoroughly examining a video's content and fact-checking its claims, provide your final assessment.

VIDEO FACT-CHECK RESULTS:
{formatted_data}

TASK:
Based on your comprehensive analysis of the video's content and the verification of its claims, determine the overall authenticity of this video.

INSTRUCTIONS:
- Write as if you have analyzed the entire video content, not just individual claims
- Conclude whether the video is AUTHENTIC, PARTIALLY AUTHENTIC, or INAUTHENTIC
- Focus on the video's overall credibility and trustworthiness
- Avoid mentioning claim counts or statistical breakdowns
- Write a cohesive assessment about the video's content quality and reliability
- Keep your entire response between 1000 and 1500 characters including spaces

Respond now:"""
    
    raw_response = await get_llm_client(prompt)
    return raw_response