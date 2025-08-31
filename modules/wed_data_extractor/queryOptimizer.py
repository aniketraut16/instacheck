from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional
from core.config import settings
import json
import logging


class DDGSQueryConfig(BaseModel):
    """Schema for DDGS query configuration"""
    query: str = Field(description="Optimized search query")
    region: str = Field(default="us-en", description="Search region")
    safesearch: str = Field(default="moderate", description="Safe search setting")
    timelimit: Optional[str] = Field(default=None, description="Time limit for results")
    max_results: Optional[int] = Field(default=10, description="Maximum number of results")
    backend: str = Field(default="auto", description="Backend search engine")


class DDGSQueryOptimizer:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.1
        )
        self.parser = JsonOutputParser(pydantic_object=DDGSQueryConfig)
        self.logger = logging.getLogger(__name__)
        
    def optimize_query(self, query: str) -> dict:
        try:
            prompt = ChatPromptTemplate.from_template("""
You are an expert search query optimizer for DDGS (Dux Distributed Global Search). 
Analyze the user query and return a JSON object with optimized parameters.

## DDGS Parameter Values:

### region (format: country-language):
- us-en (United States - English)
- uk-en (United Kingdom - English) 
- ca-en (Canada - English)
- au-en (Australia - English)
- de-de (Germany - German)
- fr-fr (France - French)
- es-es (Spain - Spanish)
- it-it (Italy - Italian)
- ru-ru (Russia - Russian)
- cn-zh (China - Chinese)
- jp-jp (Japan - Japanese)
- kr-kr (Korea - Korean)
- in-en (India - English)
- br-pt (Brazil - Portuguese)
- mx-es (Mexico - Spanish)
- ar-es (Argentina - Spanish)
- nl-nl (Netherlands - Dutch)
- se-sv (Sweden - Swedish)
- no-no (Norway - Norwegian)
- dk-da (Denmark - Danish)
- fi-fi (Finland - Finnish)
- pl-pl (Poland - Polish)
- wt-wt (Worldwide)

### safesearch:
- "on" (strict filtering)
- "moderate" (balanced filtering) 
- "off" (no filtering)

### timelimit:
- "d" (last day)
- "w" (last week) 
- "m" (last month)
- "y" (last year)
- null (no time limit)

### max_results:
- Integer between 1-200 (recommended: 10-50 for general searches)
- Higher values for research/comprehensive searches
- Lower values for quick answers

### backend:
- "auto" (recommended - uses best available engines)
- "bing" 
- "brave"
- "duckduckgo"
- "google"
- "mojeek"
- "mullvad_brave"
- "mullvad_google" 
- "yandex"
- "yahoo"
- "wikipedia"
- Comma-separated for multiple: "google,brave,yahoo"

## Query Optimization Rules:

1. **Query Enhancement:**
   - Add relevant keywords like "news", "latest", "2024", "2025" for recent events
   - Use quotes for exact phrases: "machine learning"
   - Add filetype: for specific documents (pdf, doc, etc.)
   - Use site: for specific websites
   - Remove filler words (the, a, an) unless needed for context
   - Add location-specific terms if relevant

2. **Parameter Selection:**
   - **region**: Match user's likely location/language or use "wt-wt" for global topics
   - **safesearch**: "off" for research/technical queries, "moderate" for general, "on" for family-friendly
   - **timelimit**: Use "d"/"w" for breaking news, "m"/"y" for recent developments, null for historical/general
   - **max_results**: 6-12 for quick answers, 12-20 for research, 2-6 for simple facts
   - **backend**: "auto" for most cases, "wikipedia" for factual/educational, "google,brave" for comprehensive

3. **Context Awareness:**
   - News/current events → add "latest", "breaking", set timelimit to "d" or "w"
   - Technical/academic → increase max_results, consider "filetype:pdf"
   - Local queries → set appropriate region
   - Shopping/products → add "review", "comparison", "best"
   - How-to queries → add "tutorial", "guide", "step by step"

User Query: "{query}"

Return ONLY a valid JSON object with the optimized parameters. No additional text or explanations.

{format_instructions}
            """)
            
            chain = prompt | self.llm | self.parser
            
            result = chain.invoke({
                "query": query,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Validate and sanitize the result
            validated_result = self._validate_parameters(result)
            
            self.logger.info(f"Query optimized: '{query}' -> {validated_result}")
            return validated_result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return self._fallback_optimization(query)
            
        except Exception as e:
            self.logger.error(f"Query optimization failed: {e}")
            return self._fallback_optimization(query)
    
    def _validate_parameters(self, result: dict) -> dict:
        """Validate and sanitize DDGS parameters"""
        validated = {}
        
        # Validate query
        validated['query'] = str(result.get('query', '')).strip()
        if not validated['query']:
            raise ValueError("Query cannot be empty")
        
        # Validate region
        valid_regions = [
            'us-en', 'uk-en', 'ca-en', 'au-en', 'de-de', 'fr-fr', 'es-es', 
            'it-it', 'ru-ru', 'cn-zh', 'jp-jp', 'kr-kr', 'in-en', 'br-pt',
            'mx-es', 'ar-es', 'nl-nl', 'se-sv', 'no-no', 'dk-da', 'fi-fi',
            'pl-pl', 'wt-wt'
        ]
        validated['region'] = result.get('region', 'us-en')
        if validated['region'] not in valid_regions:
            validated['region'] = 'us-en'
        
        # Validate safesearch
        valid_safesearch = ['on', 'moderate', 'off']
        validated['safesearch'] = result.get('safesearch', 'moderate')
        if validated['safesearch'] not in valid_safesearch:
            validated['safesearch'] = 'moderate'
        
        # Validate timelimit
        valid_timelimits = ['d', 'w', 'm', 'y', None]
        validated['timelimit'] = result.get('timelimit')
        if validated['timelimit'] not in valid_timelimits:
            validated['timelimit'] = None
        
        # Validate max_results
        max_results = result.get('max_results', 10)
        try:
            max_results = int(max_results)
            validated['max_results'] = max(1, min(200, max_results))
        except (ValueError, TypeError):
            validated['max_results'] = 10
        
        # Validate backend
        valid_backends = [
            'auto', 'bing', 'brave', 'duckduckgo', 'google', 'mojeek',
            'mullvad_brave', 'mullvad_google', 'yandex', 'yahoo', 'wikipedia'
        ]
        backend = result.get('backend', 'auto')
        if ',' in backend:  # Multiple backends
            backends = [b.strip() for b in backend.split(',')]
            valid_combo = all(b in valid_backends for b in backends)
            validated['backend'] = backend if valid_combo else 'auto'
        else:
            validated['backend'] = backend if backend in valid_backends else 'auto'
        
        return validated
    
    def _fallback_optimization(self, query: str) -> dict:
        """Fallback optimization when AI fails"""
        # Simple keyword-based optimization
        optimized_query = query.strip()
        
        # Add time-related keywords for current events
        current_keywords = ['news', 'latest', 'breaking', 'today', 'current', '2025']
        if any(keyword in query.lower() for keyword in current_keywords):
            timelimit = 'w'
        else:
            timelimit = None
        
        # Adjust safesearch based on query content
        research_keywords = ['research', 'study', 'academic', 'technical', 'analysis']
        safesearch = 'off' if any(keyword in query.lower() for keyword in research_keywords) else 'moderate'
        
        return {
            "query": optimized_query,
            "region": "us-en",
            "safesearch": safesearch,
            "timelimit": timelimit,
            "max_results": 20,
            "backend": "auto"
        }

def optimize_query(user_query: str) -> dict:
    optimizer = DDGSQueryOptimizer()
    return optimizer.optimize_query(user_query)