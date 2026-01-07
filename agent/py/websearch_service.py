"""Web search service using Firecrawl."""
import aiohttp
from typing import List, Dict, Any, Optional
from .types import AllowedDomain, SearchResult, Query, IDoc
from .openai_service import OpenAIService
from .text_service import TextService
from openai.types.chat import ChatCompletionMessageParam


class WebSearchService:
    """Web search service with Firecrawl integration."""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.text_service = TextService()
        self.allowed_domains = [
            AllowedDomain('Wikipedia', 'wikipedia.org', True),
            AllowedDomain('FS.blog', 'fs.blog', True),
            AllowedDomain('arXiv', 'arxiv.org', True),
            AllowedDomain('OpenAI', 'openai.com', True),
            AllowedDomain('Reuters', 'reuters.com', True),
            AllowedDomain('MIT Technology Review', 'technologyreview.com', True),
            AllowedDomain('TechCrunch', 'techcrunch.com', True),
            AllowedDomain('Hacker News', 'news.ycombinator.com', True),
            AllowedDomain('Anthropic', 'anthropic.com', True),
            AllowedDomain('DeepMind', 'deepmind.google', True),
        ]
        self.api_key = os.getenv('FIRECRAWL_API_KEY', '')
    
    async def is_web_search_needed(self, messages: List[ChatCompletionMessageParam]) -> bool:
        """Determine if web search is needed.
        
        Args:
            messages: Chat messages.
        
        Returns:
            Whether web search is needed.
        """
        system_prompt: ChatCompletionMessageParam = {
            'role': 'system',
            'content': 'Determine if web search is needed to answer the query. Respond with JSON: {"should_search": bool}'
        }
        
        response = await self.openai_service.completion(
            messages=[system_prompt] + messages,
            json_mode=True
        )
        
        try:
            import json
            result = json.loads(response.choices[0].message.content or '{}')
            return result.get('should_search', False)
        except:
            return False
    
    async def generate_queries(self, messages: List[ChatCompletionMessageParam]) -> Dict[str, Any]:
        """Generate search queries.
        
        Args:
            messages: Chat messages.
        
        Returns:
            Dict with queries and thoughts.
        """
        domain_list = ', '.join([f'{d.name} ({d.url})' for d in self.allowed_domains])
        system_prompt: ChatCompletionMessageParam = {
            'role': 'system',
            'content': f'''Generate search queries for the given question. Return JSON:
{{
  "queries": [{{"q": "query text", "url": "domain.com"}}, ...],
  "_thoughts": "explanation"
}}

Allowed domains: {domain_list}'''
        }
        
        response = await self.openai_service.completion(
            messages=[system_prompt] + messages,
            json_mode=True
        )
        
        try:
            import json
            return json.loads(response.choices[0].message.content or '{}')
        except:
            return {'queries': [], '_thoughts': ''}
    
    async def search_web(self, queries: List[Query], conversation_uuid: str) -> List[Dict[str, Any]]:
        """Search the web using Firecrawl.
        
        Args:
            queries: Search queries.
            conversation_uuid: Conversation UUID.
        
        Returns:
            Search results.
        """
        search_results = []
        
        async with aiohttp.ClientSession() as session:
            for query in queries:
                try:
                    url_parts = query.url.split('.')
                    domain = '.'.join(url_parts[-2:]) if len(url_parts) > 1 else query.url
                    site_query = f'site:{domain} {query.q}'
                    
                    async with session.post(
                        'https://api.firecrawl.dev/v0/search',
                        json={
                            'query': site_query,
                            'searchOptions': {'limit': 6},
                            'pageOptions': {'fetchPageContent': False}
                        },
                        headers={
                            'Authorization': f'Bearer {self.api_key}',
                            'Content-Type': 'application/json'
                        }
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get('success') and data.get('data'):
                                results = [{
                                    'url': item['url'],
                                    'title': item.get('title', ''),
                                    'description': item.get('description', '')
                                } for item in data['data']]
                                search_results.append({
                                    'query': query.q,
                                    'domain': domain,
                                    'results': results
                                })
                except Exception as e:
                    print(f'Error searching {query.q}: {e}')
        
        return search_results
    
    async def scrape_urls(self, urls: List[str], conversation_uuid: str) -> List[Dict[str, str]]:
        """Scrape URLs for content.
        
        Args:
            urls: URLs to scrape.
            conversation_uuid: Conversation UUID.
        
        Returns:
            Scraped content.
        """
        scrappable_urls = [
            url for url in urls
            if any(domain.url in url for domain in self.allowed_domains if domain.scrappable)
        ]
        
        scrapedContent = []
        async with aiohttp.ClientSession() as session:
            for url in scrappable_urls:
                try:
                    async with session.post(
                        'https://api.firecrawl.dev/v0/scrape',
                        json={
                            'url': url,
                            'formats': ['markdown']
                        },
                        headers={'Authorization': f'Bearer {self.api_key}'}
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get('success') and data['data'].get('markdown'):
                                scrapedContent.append({
                                    'url': url,
                                    'content': data['data']['markdown']
                                })
                except Exception as e:
                    print(f'Error scraping {url}: {e}')
        
        return scrapedContent
    
    async def search(self, query: str, conversation_uuid: str) -> List[IDoc]:
        """Execute complete web search.
        
        Args:
            query: Search query.
            conversation_uuid: Conversation UUID.
        
        Returns:
            List of documents.
        """
        messages: List[ChatCompletionMessageParam] = [{'role': 'user', 'content': query}]
        
        # Check if search is needed
        if not await self.is_web_search_needed(messages):
            return []
        
        # Generate queries
        query_result = await self.generate_queries(messages)
        queries = [
            Query(q=q['q'], url=q['url'])
            for q in query_result.get('queries', [])
            if any(d.url in q.get('url', '') for d in self.allowed_domains)
        ]
        
        if not queries:
            return []
        
        # Search web
        search_results = await self.search_web(queries, conversation_uuid)
        
        # Extract URLs to scrape
        urls_to_scrape = []
        for sr in search_results:
            urls_to_scrape.extend([r['url'] for r in sr['results']])
        
        # Scrape URLs
        scraped_content = await self.scrape_urls(urls_to_scrape, conversation_uuid)
        
        # Create documents
        docs: List[IDoc] = []
        for sr in search_results:
            for result in sr['results']:
                scraped = next((s for s in scraped_content if s['url'] == result['url']), None)
                content = scraped['content'] if scraped else result['description']
                
                doc = await self.text_service.document(
                    text=content,
                    name=result['title'],
                    description=f'Web search result for: "{sr["query"]}"',
                    doc_type='web_page',
                    content_type='complete' if scraped else 'chunk',
                    source=result['url'],
                    conversation_uuid=conversation_uuid
                )
                docs.append(doc)
        
        return docs
