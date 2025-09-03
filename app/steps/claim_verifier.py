from typing import List
import logging
from modules.llm_clients.client import get_llm_client
logger = logging.getLogger(__name__)

async def verify_claim(claim: str , evidence: List[str]) -> str:
    prompt = f"""You are a fact-checking assistant. Analyze the claim against the provided evidence and determine if it is correct, partially correct, or incorrect.

CLAIM: {claim}

EVIDENCE:
{chr(10).join([f"- {ev}" for ev in evidence])}

INSTRUCTIONS:
- Base your analysis ONLY on the evidence provided above
- Do not use external knowledge unless the evidence is insufficient
- Classify the claim as: CORRECT, PARTIALLY CORRECT, or INCORRECT
- Provide a brief explanation for your classification
- Keep your response under 700 characters including spaces

Respond now:"""
    
    try:
        logger.info(f"Verifying claim: {claim[:100]}...")
        raw_response = await get_llm_client(prompt)
        return raw_response
    except Exception as e:
        logger.error(f"Error verifying claim: {e}")
        return None