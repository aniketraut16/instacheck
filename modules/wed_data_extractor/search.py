from ddgs import DDGS
from typing import List, Dict, Union
import logging


def get_search_results(search_config: Dict[str, Union[str, int, None]]) -> List[str]:
    logger = logging.getLogger(__name__)
    
    try:
        # Extract parameters from config with defaults
        query = search_config.get('query', '')
        region = search_config.get('region', 'us-en')
        safesearch = search_config.get('safesearch', 'moderate')
        timelimit = search_config.get('timelimit')
        max_results = search_config.get('max_results', 10)
        backend = search_config.get('backend', 'auto')
        
        # Validate required query parameter
        if not query or not query.strip():
            raise ValueError("Query parameter is required and cannot be empty")
        
        logger.info(f"Performing DDGS search with query: '{query}', max_results: {max_results}")
        
        # Initialize DDGS and perform search
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query=query.strip(),
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results,
                backend=backend
            ))
        
        # Extract URLs from results
        urls = []
        for result in results:
            if isinstance(result, dict) and 'href' in result:
                url = result['href']
                if url and url.startswith(('http://', 'https://')):
                    urls.append(url)
        
        logger.info(f"Successfully retrieved {len(urls)} URLs from {len(results)} results")
        
        if not urls:
            logger.warning(f"No valid URLs found for query: '{query}'")
            
        return urls
        
    except Exception as e:
        logger.error(f"Search failed for query '{search_config.get('query', 'unknown')}': {e}")
        raise Exception(f"Failed to perform search: {str(e)}")


def get_enhanced_search_results(search_config: Dict[str, Union[str, int, None]], 
                              include_metadata: bool = False) -> Union[List[str], List[Dict]]:

    logger = logging.getLogger(__name__)
    
    try:
        # Extract parameters
        query = search_config.get('query', '')
        region = search_config.get('region', 'us-en')
        safesearch = search_config.get('safesearch', 'moderate')
        timelimit = search_config.get('timelimit')
        max_results = search_config.get('max_results', 10)
        backend = search_config.get('backend', 'auto')
        
        if not query or not query.strip():
            raise ValueError("Query parameter is required and cannot be empty")
        
        logger.info(f"Performing enhanced DDGS search: '{query}'")
        
        # Perform search
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query=query.strip(),
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results,
                backend=backend
            ))
        
        if include_metadata:
            # Return URLs with metadata
            enhanced_results = []
            for result in results:
                if isinstance(result, dict) and 'href' in result:
                    enhanced_result = {
                        'url': result['href'],
                        'title': result.get('title', ''),
                        'body': result.get('body', ''),
                        'source': result.get('source', ''),
                    }
                    enhanced_results.append(enhanced_result)
            
            logger.info(f"Retrieved {len(enhanced_results)} results with metadata")
            return enhanced_results
        else:
            # Return URLs only
            urls = [result['href'] for result in results 
                   if isinstance(result, dict) and 'href' in result 
                   and result['href'].startswith(('http://', 'https://'))]
            
            logger.info(f"Retrieved {len(urls)} URLs")
            return urls
            
    except Exception as e:
        logger.error(f"Enhanced search failed: {e}")
        raise Exception(f"Failed to perform enhanced search: {str(e)}")