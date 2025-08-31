from typing import Dict, Any
from modules.wed_data_extractor.search import get_search_results
from modules.wed_data_extractor.scraper import scrape_all_urls
from modules.wed_data_extractor.embedder import embed_and_search
from modules.wed_data_extractor.queryOptimizer import optimize_query
from modules.wed_data_extractor.relevant_content_extractor import relevant_content_extractor


async def get_wed_data(query: str ) -> Dict[str, Any]:
    if not query or not isinstance(query, str):
        return {"summary": [], "sources": [], "error": "Invalid query"}
    
    optimized_query = optimize_query(query)
    urls = get_search_results(optimized_query)
    # print(urls)
    
    if not urls:
        return {"summary": [], "sources": [], "error": "No search results found"}
    
    # raw_data = await scrape_all_urls(urls)
    # # print(raw_data)
    
    # if not raw_data:
    #     return {"summary": [], "sources": urls, "error": "Failed to scrape content"}
    
    # results = embed_and_search(raw_data, query)
    results = await relevant_content_extractor(urls, query)


    # print(summary)
    return {"sources": urls , "results": results}
    # return {"summary": summary, "sources": urls}
