"""Algolia search service implementation.

Wrappers around Algolia API client providing type-safe, async-ready search operations.
"""

import os
from typing import Any, Optional, Dict, List, Sequence
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

try:
    from algoliasearch.search_client import SearchClient
except ImportError:
    logger.warning("algoliasearch package not installed. Install with: pip install algoliasearch")
    SearchClient = None


@dataclass
class SearchOptions:
    """Options for search queries."""
    headers: Optional[Dict[str, str]] = None
    query_parameters: Optional[Dict[str, Any]] = None


@dataclass
class SearchResult:
    """Represents a search result."""
    hits: List[Dict[str, Any]]
    nbHits: int
    nbPages: int
    page: int
    hitsPerPage: int
    processingTimeMS: int
    query: str
    ranking_info: Optional[List[Dict[str, Any]]] = None


class AlgoliaService:
    """Algolia search service for managing search indices and queries."""

    def __init__(self, app_id: str, api_key: str) -> None:
        """Initialize Algolia service.

        Args:
            app_id: Algolia application ID
            api_key: Algolia API key
        """
        if not SearchClient:
            raise ImportError(
                "algoliasearch package is required. Install with: pip install algoliasearch"
            )
        
        self.app_id = app_id
        self.api_key = api_key
        self.client = SearchClient.create(app_id, api_key)
        logger.info(f"Initialized Algolia service for app: {app_id}")

    async def search_single_index(
        self,
        index_name: str,
        query: str,
        options: Optional[SearchOptions] = None,
    ) -> SearchResult:
        """Search in a single index.

        Args:
            index_name: Name of the index to search
            query: Search query string
            options: Optional search options (headers, query parameters)

        Returns:
            SearchResult object with hits and metadata
        """
        if options is None:
            options = SearchOptions()

        default_params = {
            "hitsPerPage": 20,
            "page": 0,
            "attributesToRetrieve": ["*"],
            "typoTolerance": True,
            "ignorePlurals": True,
            "removeStopWords": True,
            "queryType": "prefixNone",
            "attributesToHighlight": ["*"],
            "highlightPreTag": "<em>",
            "highlightPostTag": "</em>",
            "analytics": True,
            "clickAnalytics": True,
            "enablePersonalization": False,
            "distinct": 1,
            "facets": ["*"],
            "minWordSizefor1Typo": 1,
            "minWordSizefor2Typos": 3,
            "advancedSyntax": True,
            "removeWordsIfNoResults": "lastWords",
            "getRankingInfo": True,
        }

        merged_params = {
            **default_params,
            "query": query,
            **(options.query_parameters or {}),
        }

        try:
            index = self.client.init_index(index_name)
            result = index.search(query, merged_params)
            
            logger.debug(f"Search completed: {result.get('nbHits', 0)} hits")
            
            return SearchResult(
                hits=result.get("hits", []),
                nbHits=result.get("nbHits", 0),
                nbPages=result.get("nbPages", 0),
                page=result.get("page", 0),
                hitsPerPage=result.get("hitsPerPage", 0),
                processingTimeMS=result.get("processingTimeMS", 0),
                query=result.get("query", ""),
                ranking_info=result.get("_rankingInfo"),
            )
        except Exception as e:
            logger.error(f"Search error in {index_name}: {e}")
            raise

    async def save_object(
        self, index_name: str, obj: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save an object to the index.

        Args:
            index_name: Name of the index
            obj: Object to save (must include 'objectID')

        Returns:
            Response from Algolia
        """
        try:
            index = self.client.init_index(index_name)
            response = index.save_object(obj)
            logger.debug(f"Object saved to {index_name}")
            return response
        except Exception as e:
            logger.error(f"Error saving object to {index_name}: {e}")
            raise

    async def get_object(
        self,
        index_name: str,
        object_id: str,
        attributes_to_retrieve: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get an object by ID.

        Args:
            index_name: Name of the index
            object_id: ID of the object
            attributes_to_retrieve: Optional list of attributes to retrieve

        Returns:
            The object
        """
        try:
            index = self.client.init_index(index_name)
            response = index.get_object(object_id)
            logger.debug(f"Object retrieved from {index_name}")
            return response
        except Exception as e:
            logger.error(f"Error getting object from {index_name}: {e}")
            raise

    async def add_or_update_object(
        self, index_name: str, object_id: str, obj: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add or update an object.

        Args:
            index_name: Name of the index
            object_id: ID of the object
            obj: Object data

        Returns:
            Response from Algolia
        """
        try:
            index = self.client.init_index(index_name)
            obj_with_id = {**obj, "objectID": object_id}
            response = index.save_object(obj_with_id)
            logger.debug(f"Object added/updated in {index_name}")
            return response
        except Exception as e:
            logger.error(f"Error updating object in {index_name}: {e}")
            raise

    async def delete_object(self, index_name: str, object_id: str) -> Dict[str, Any]:
        """Delete an object by ID.

        Args:
            index_name: Name of the index
            object_id: ID of the object to delete

        Returns:
            Response from Algolia
        """
        try:
            index = self.client.init_index(index_name)
            response = index.delete_object(object_id)
            logger.debug(f"Object deleted from {index_name}")
            return response
        except Exception as e:
            logger.error(f"Error deleting object from {index_name}: {e}")
            raise

    async def delete_by(
        self, index_name: str, filters: str
    ) -> Dict[str, Any]:
        """Delete objects matching filter criteria.

        Args:
            index_name: Name of the index
            filters: Filter string (e.g., "status:deleted")

        Returns:
            Response from Algolia
        """
        try:
            index = self.client.init_index(index_name)
            response = index.delete_by({"filters": filters})
            logger.debug(f"Objects deleted from {index_name} by filter")
            return response
        except Exception as e:
            logger.error(f"Error deleting by filter in {index_name}: {e}")
            raise

    async def clear_objects(self, index_name: str) -> Dict[str, Any]:
        """Clear all objects from an index.

        Args:
            index_name: Name of the index

        Returns:
            Response from Algolia
        """
        try:
            index = self.client.init_index(index_name)
            response = index.clear_objects()
            logger.debug(f"Index cleared: {index_name}")
            return response
        except Exception as e:
            logger.error(f"Error clearing index {index_name}: {e}")
            raise

    async def partial_update_object(
        self, index_name: str, object_id: str, attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Partially update an object.

        Args:
            index_name: Name of the index
            object_id: ID of the object
            attributes: Attributes to update

        Returns:
            Response from Algolia
        """
        try:
            index = self.client.init_index(index_name)
            response = index.partial_update_object({
                "objectID": object_id,
                **attributes,
            })
            logger.debug(f"Object partially updated in {index_name}")
            return response
        except Exception as e:
            logger.error(f"Error partially updating object in {index_name}: {e}")
            raise

    async def get_objects(
        self, requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get multiple objects by requests.

        Args:
            requests: List of request dicts with indexName and objectID

        Returns:
            Response from Algolia with requested objects
        """
        try:
            response = self.client.get_objects(requests)
            logger.debug(f"Retrieved {len(requests)} objects")
            return response
        except Exception as e:
            logger.error(f"Error getting multiple objects: {e}")
            raise

    async def list_indices(self) -> Dict[str, Any]:
        """List all indices.

        Returns:
            Dictionary containing list of indices
        """
        try:
            response = self.client.list_indices()
            logger.debug(f"Retrieved {len(response.get('items', []))} indices")
            return response
        except Exception as e:
            logger.error(f"Error listing indices: {e}")
            raise
