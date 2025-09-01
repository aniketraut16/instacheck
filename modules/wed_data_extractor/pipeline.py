from typing import Dict, Any
from modules.wed_data_extractor.search import get_search_results
from modules.wed_data_extractor.scraper import scrape_all_urls
from modules.wed_data_extractor.embedder import embed_and_search
from modules.wed_data_extractor.queryOptimizer import optimize_query
from modules.wed_data_extractor.relevant_content_extractor import relevant_content_extractor
from fastapi import WebSocket

async def get_wed_data(query: str,websocket: WebSocket = None) -> Dict[str, Any]:
    if not query or not isinstance(query, str):
        return {"summary": [], "sources": [], "error": "Invalid query"}
    
    optimized_query = optimize_query(query)
    urls = get_search_results(optimized_query)
    
    if not urls:
        return {"summary": [], "sources": [], "error": "No search results found"}
    results = await relevant_content_extractor(urls, query,websocket=websocket)

    return {"sources": urls , "results": results}
