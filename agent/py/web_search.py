"""Web search service using Firecrawl API."""
import os
import json
from typing import List, Dict, Optional, Any
import aiohttp
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion
from .openai_service import OpenAIService
from .text_service import TextService, IDoc


class WebSearchService:
    """Service for web search and content extraction."""

    def __init__(self):
        """Initialize web search service."""
        self.openai_service = OpenAIService()
        self.text_service = TextService()
        self.api_key = os.getenv('FIRECRAWL_API_KEY', '')
        
        self.allowed_domains = [
            {'name': 'Wikipedia', 'url': 'wikipedia.org', 'scrappable': True},
            {'name': 'FS.blog', 'url': 'fs.blog', 'scrappable': True},
            {'name': 'arXiv', 'url': 'arxiv.org', 'scrappable': True},
            {'name': 'OpenAI', 'url': 'openai.com', 'scrappable': True},
            {'name': 'Reuters', 'url': 'reuters.com', 'scrappable': True},
            {'name': 'MIT Technology Review', 'url': 'technologyreview.com', 'scrappable': True},
            {'name': 'TechCrunch', 'url': 'techcrunch.com', 'scrappable': True},
            {'name': 'Hacker News', 'url': 'news.ycombinator.com', 'scrappable': True},
            {'name': 'Anthropic', 'url': 'anthropic.com', 'scrappable': True},
            {'name': 'DeepMind', 'url': 'deepmind.google', 'scrappable': True},
        ]

    async def is_web_search_needed(self, messages: List[ChatCompletionMessageParam]) -> Dict[str, Any]:
        """Determine if web search is needed."""
        system_prompt = {
            'role': 'system',
            'content': '''Analyze if a web search is needed to answer this query.
            
Respond with JSON:
{
    "_thoughts": "your analysis",
    "shouldSearch": true/false
}
'''
        }

        response = await self.openai_service.completion({
            'messages': [system_prompt, *messages],
            'model': 'gpt-4o',
            'jsonMode': True
        })

        if isinstance(response, ChatCompletion):
            content = response.choices[0].message.content
            if content:
                return json.loads(content)
        return {'shouldSearch': False}

    async def generate_queries(
        self,
        messages: List[ChatCompletionMessageParam]
    ) -> Dict[str, Any]:
        """Generate search queries for the user message."""
        domains_str = '\n'.join(
            f'- {d["name"]}: {d["url"]} (scrappable: {d["scrappable"]})'
            for d in self.allowed_domains
        )

        system_prompt = {
            'role': 'system',
            'content': f'''Generate specific search queries and select appropriate domains.

Allowed domains:
{domains_str}

Respond with JSON:
{{
    "_thoughts": "your analysis",
    "queries": [{{
        "q": "search query",
        "url": "domain url"
    }}]
}}
'''
        }

        try:
            response = await self.openai_service.completion({
                'messages': [system_prompt, *messages],
                'model': 'gpt-4o',
                'jsonMode': True
            })

            if isinstance(response, ChatCompletion):
                content = response.choices[0].message.content
                if content:
                    result = json.loads(content)
                    # Filter to allowed domains
                    filtered_queries = [
                        q for q in result.get('queries', [])
                        if any(d['url'] in q.get('url', '') for d in self.allowed_domains)
                    ]
                    return {'queries': filtered_queries, '_thoughts': result.get('_thoughts', '')}
        except Exception as e:
            print(f'Error generating queries: {e}')

        return {'queries': [], '_thoughts': ''}

    async def search_web(self, queries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Search the web using Firecrawl API."""
        results = []

        for query_item in queries:
            q = query_item.get('q', '')
            url = query_item.get('url', '')

            try:
                # Build site-specific search query
                if not url.startswith('https://'):
                    url = f'https://{url}'

                from urllib.parse import urlparse
                domain = urlparse(url).hostname.replace('www.', '')
                site_query = f'site:{domain} {q}'

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        'https://api.firecrawl.dev/v0/search',
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.api_key}'
                        },
                        json={
                            'query': site_query,
                            'searchOptions': {'limit': 6},
                            'pageOptions': {'fetchPageContent': False}
                        }
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get('success') and data.get('data'):
                                results.append({
                                    'query': q,
                                    'domain': url,
                                    'results': [
                                        {
                                            'url': item.get('url'),
                                            'title': item.get('title'),
                                            'description': item.get('description')
                                        }
                                        for item in data.get('data', [])
                                    ]
                                })
                        else:
                            results.append({
                                'query': q,
                                'domain': url,
                                'results': []
                            })
            except Exception as e:
                print(f'Error searching "{q}": {e}')
                results.append({
                    'query': q,
                    'domain': url,
                    'results': []
                })

        return results

    async def scrape_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """Scrape content from URLs."""
        # Filter to scrappable domains
        scrappable_urls = []
        for url in urls:
            from urllib.parse import urlparse
            domain = urlparse(url).hostname.replace('www.', '')
            if any(d['url'] == domain and d['scrappable'] for d in self.allowed_domains):
                scrappable_urls.append(url.rstrip('/'))

        results = []
        for url in scrappable_urls:
            try:
                # This would use actual Firecrawl in production
                # For now, return empty content
                results.append({
                    'url': url,
                    'content': ''
                })
            except Exception as e:
                print(f'Error scraping {url}: {e}')
                results.append({
                    'url': url,
                    'content': ''
                })

        return results

    async def search(
        self,
        query: str,
        conversation_uuid: str
    ) -> List[IDoc]:
        """Perform complete web search workflow.
        
        Args:
            query: User query.
            conversation_uuid: Conversation ID for tracking.
        
        Returns:
            List of IDoc documents with search results.
        """
        messages: List[ChatCompletionMessageParam] = [
            {'role': 'user', 'content': query}
        ]

        # Generate queries
        query_result = await self.generate_queries(messages)
        queries = query_result.get('queries', [])

        docs: List[IDoc] = []

        if queries:
            # Search web
            search_results = await self.search_web(queries)

            # Scrape URLs
            all_urls = [
                r['url']
                for sr in search_results
                for r in sr.get('results', [])
            ]
            scraped = await self.scrape_urls(all_urls)

            # Create documents
            for search_result in search_results:
                for result in search_result.get('results', []):
                    # Find scraped content
                    scraped_item = next(
                        (s for s in scraped if s['url'].rstrip('/') == result['url'].rstrip('/')),
                        None
                    )
                    content = scraped_item['content'] if scraped_item else result.get('description', '')

                    if content:
                        doc = await self.text_service.document(
                            content,
                            'gpt-4o',
                            {
                                'name': result.get('title'),
                                'description': f'Search result for "{search_result["query"]}"',
                                'source': result.get('url'),
                                'content_type': 'complete' if scraped_item else 'chunk',
                                'conversation_uuid': conversation_uuid,
                            }
                        )
                        docs.append(doc)

        return docs
