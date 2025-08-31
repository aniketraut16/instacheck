from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel, Field
from typing import List, Literal
import json
import logging
from core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Claim(BaseModel):
    """Represents a single verifiable claim extracted from transcription."""
    claim: str = Field(
        description="A clear, specific statement that can be proven true or false through fact-checking"
    )
    category: Literal[
        "health_medical", 
        "political_news", 
        "celebrity_gossip", 
        "financial_market", 
        "scientific_fact", 
        "historical_event", 
        "product_review", 
        "social_issue", 
        "technology_tech", 
        "sports_entertainment", 
        "weather_natural", 
        "business_economy", 
        "education_academic", 
        "legal_regulatory", 
        "cultural_trend"
    ] = Field(description="Category that best describes the nature of the claim")

class ClaimsExtraction(BaseModel):
    """Container for all extracted claims from a transcription."""
    claims: List[Claim] = Field(description="List of verifiable claims extracted from the transcription")

class InstagramReelClaimsExtractor:
    """
    Advanced claims extraction system for Instagram Reel transcriptions.
    Designed for authenticity checking and fact verification workflows.
    """
    
    def __init__(self, model_name: str = "gpt-oss:20b"):
        """Initialize the claims extractor with specified LLM model."""
        self.llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.0,
    google_api_key=settings.GOOGLE_API_KEY
)
        self.output_parser = PydanticOutputParser(pydantic_object=ClaimsExtraction)
        self.prompt = self._create_extraction_prompt()
        self.chain = self.prompt | self.llm | self.output_parser
        
    def _create_extraction_prompt(self) -> PromptTemplate:
        """Create a comprehensive prompt template for claim extraction."""
        
        template = """
You are an expert fact-checker. Extract verifiable claims from Instagram Reel transcription for authenticity verification.

TASK: Extract 2-5 SPECIFIC, EVIDENCE-BACKED claims that can be fact-checked with concrete sources.

CRITICAL REQUIREMENTS:
- Claims must include SPECIFIC details (names, dates, numbers, locations, companies)
- Avoid vague terms like "experts say", "studies show", "some people believe"
- Claims must be verifiable through official sources, databases, or documented records
- NO subjective interpretations or theoretical statements

EXTRACT ONLY:
✓ Specific product specifications with exact numbers/features
✓ Named company announcements with dates/details
✓ Exact statistics with sources or studies mentioned
✓ Specific news events with names, dates, locations
✓ Measurable health/medical data with study names or institutions
✓ Financial data with exact figures and timeframes
✓ Named individuals making specific statements

NEVER EXTRACT:
✗ "Experts think..." or "Studies suggest..." without naming the expert/study
✗ Theoretical explanations without concrete evidence
✗ Vague health benefits without specific data
✗ Opinions disguised as facts
✗ Unattributed quotes or claims

GOOD EXAMPLES:
✓ "iPhone 15 Pro has 48MP main camera" (verifiable spec)
✓ "Tesla stock dropped 12% on March 15, 2024" (specific data)
✓ "Dr. Smith from Harvard published study showing 25% improvement" (named source)

BAD EXAMPLES:
✗ "Experts believe quantum computing works across universes" (vague, theoretical)
✗ "This product is amazing for health" (subjective, no specifics)
✗ "Many studies prove this works" (no named studies)

CATEGORIES: health_medical, political_news, celebrity_gossip, financial_market, scientific_fact, historical_event, product_review, social_issue, technology_tech, sports_entertainment, weather_natural, business_economy, education_academic, legal_regulatory, cultural_trend.

TRANSCRIPTION: {transcription}

Extract only claims with CONCRETE EVIDENCE POTENTIAL. If a claim cannot be verified through official sources, documentation, or databases, DO NOT include it.

{format_instructions}
"""

        return PromptTemplate(
            template=template,
            input_variables=["transcription"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
    
    def extract_claims(self, transcription: str) -> List[dict]:
        """
        Extract verifiable claims from Instagram Reel transcription.
        
        Args:
            transcription (str): The text transcription of the Instagram Reel
            
        Returns:
            List[dict]: List of extracted claims with their categories
            
        Raises:
            ValueError: If transcription is empty or invalid
            Exception: If extraction fails after retries
        """
        
        if not transcription or not transcription.strip():
            raise ValueError("Transcription cannot be empty")
            
        try:
            logger.info(f"Extracting claims from transcription: {transcription[:100]}...")
            
            # Invoke the chain
            result = self.chain.invoke({"transcription": transcription.strip()})
            
            # Convert to dictionary format
            claims_list = [
                {
                    "claim": claim.claim,
                    "category": claim.category
                }
                for claim in result.claims
            ]
            
            logger.info(f"Successfully extracted {len(claims_list)} claims")
            return claims_list
            
        except OutputParserException as e:
            logger.error(f"Output parsing failed: {e}")
            # Fallback: try to extract claims with simpler parsing
            return self._fallback_extraction(transcription)
            
        except Exception as e:
            logger.error(f"Claim extraction failed: {e}")
            raise Exception(f"Failed to extract claims: {str(e)}")
    
    def _fallback_extraction(self, transcription: str) -> List[dict]:
        """Fallback method if structured parsing fails."""
        try:
            # Create a simpler prompt for fallback
            simple_prompt = PromptTemplate.from_template(
                """Extract 2-5 verifiable claims from this transcription. 
                Return as JSON array with objects containing 'claim' and 'category' fields.
                Categories: health_medical, political_news, celebrity_gossip, financial_market, 
                scientific_fact, historical_event, product_review, social_issue, technology_tech, 
                sports_entertainment, weather_natural, business_economy, education_academic, 
                legal_regulatory, cultural_trend
                
                Transcription: {transcription}"""
            )
            
            simple_chain = simple_prompt | self.llm
            response = simple_chain.invoke({"transcription": transcription})
            
            # Try to parse as JSON
            try:
                claims_data = json.loads(response.content)
                if isinstance(claims_data, list):
                    return claims_data
            except json.JSONDecodeError:
                pass
                
            logger.warning("Fallback extraction failed, returning empty list")
            return []
            
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")
            return []

def extract_claims(transcription: str, model_name: str = "gpt-oss:20b") -> List[dict]:
    """
    Convenience function to extract claims from Instagram Reel transcription.
    
    Args:
        transcription (str): The text transcription of the Instagram Reel
        model_name (str): The LLM model to use for extraction
        
    Returns:
        List[dict]: List of extracted claims with categories
        
    Example:
        >>> claims = extract_claims("The new iPhone 15 has 48MP camera and costs $999")
        >>> print(claims)
        [
            {
                "claim": "iPhone 15 has a 48MP camera",
                "category": "technology_tech"
            },
            {
                "claim": "iPhone 15 costs $999",
                "category": "technology_tech"
            }
        ]
    """
    extractor = InstagramReelClaimsExtractor(model_name=model_name)
    return extractor.extract_claims(transcription)

# Example usage and testing
if __name__ == "__main__":
    # Test the extractor
    sample_transcription = """
    Hey guys! The new iPhone 15 Pro Max has a 48MP main camera and costs $1199. 
    Tesla announced their Model S now has 405-mile EPA range. Elon Musk said this on Twitter yesterday.
    According to the FDA, this new supplement contains 500mg of vitamin D per tablet.
    The S&P 500 closed at 4,387 points on Friday. My skincare routine includes retinol serum.
    """
    
    try:
        extractor = InstagramReelClaimsExtractor()
        claims = extractor.extract_claims(sample_transcription)
        
        print("Extracted Claims:")
        print(json.dumps(claims, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")