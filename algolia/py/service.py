"""Algolia search service for semantic and full-text search."""

import os
from typing import Any, Dict, List, Optional

try:
    from algoliasearch.search_client import SearchClient
    from algoliasearch.search_client import QueryType
    from algoliasearch.search_client import RemoveWordsIfNoResults
except ImportError:
    # Fallback for different API versions
    SearchClient = None  # type: ignore


class AlgoliaService:
    """Service for interacting with Algolia search."""

    def __init__(
        self,
        application_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize Algolia service.

        Args:
            application_id: Algolia application ID. Defaults to ALGOLIA_APP_ID env var.
            api_key: Algolia API key. Defaults to ALGOLIA_API_KEY env var.

        Raises:
            ValueError: If credentials are not provided or available.
        """
        self.application_id = application_id or os.getenv("ALGOLIA_APP_ID")
        self.api_key = api_key or os.getenv("ALGOLIA_API_KEY")

        if not self.application_id or not self.api_key:
            raise ValueError(
                "Algolia credentials not provided. "
                "Set ALGOLIA_APP_ID and ALGOLIA_API_KEY environment variables."
            )

        if SearchClient is None:
            raise ImportError(
                "algoliasearch package required. Install with: pip install algoliasearch"
            )

        self.client = SearchClient.create(self.application_id, self.api_key)

    async def search_single_index(
        self,
        index_name: str,
        query: str,
        options: Optional[
            Dict[str, Dict[str, Any]]
        ] = None,
    ) -> Dict[str, Any]:
        """Search a single index with advanced parameters.

        Args:
            index_name: Name of the index to search.
            query: Search query string.
            options: Optional headers and query parameters.

        Returns:
            Search results dictionary.
        """
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
        }

        merged_params = {
            **default_params,
            "query": query,
            "getRankingInfo": True,
        }

        if options and "queryParameters" in options:
            merged_params.update(options["queryParameters"])

        index = self.client.init_index(index_name)
        results = index.search(query, merged_params)

        return results

    async def save_object(
        self,
        index_name: str,
        obj: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Save object to index (create or update).

        Args:
            index_name: Name of the index.
            obj: Object to save.

        Returns:
            Operation result.
        """
        index = self.client.init_index(index_name)
        return index.save_object(obj)

    async def get_object(
        self,
        index_name: str,
        object_id: str,
        attributes_to_retrieve: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get object from index.

        Args:
            index_name: Name of the index.
            object_id: Object ID.
            attributes_to_retrieve: Optional list of attributes to retrieve.

        Returns:
            Retrieved object.
        """
        index = self.client.init_index(index_name)
        params = {}
        if attributes_to_retrieve:
            params["attributesToRetrieve"] = attributes_to_retrieve

        return index.get_object(object_id, params)

    async def add_or_update_object(
        self,
        index_name: str,
        object_id: str,
        obj: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add or update object in index.

        Args:
            index_name: Name of the index.
            object_id: Object ID.
            obj: Object to add or update.

        Returns:
            Operation result.
        """
        index = self.client.init_index(index_name)
        obj["objectID"] = object_id
        return index.save_object(obj)

    async def delete_object(
        self,
        index_name: str,
        object_id: str,
    ) -> Dict[str, Any]:
        """Delete object from index.

        Args:
            index_name: Name of the index.
            object_id: Object ID to delete.

        Returns:
            Operation result.
        """
        index = self.client.init_index(index_name)
        return index.delete_object(object_id)

    async def delete_by(
        self,
        index_name: str,
        filters: str,
    ) -> Dict[str, Any]:
        """Delete objects matching filters.

        Args:
            index_name: Name of the index.
            filters: Filter string.

        Returns:
            Operation result.
        """
        index = self.client.init_index(index_name)
        return index.delete_by({"filters": filters})

    async def clear_objects(
        self,
        index_name: str,
    ) -> Dict[str, Any]:
        """Clear all objects from index.

        Args:
            index_name: Name of the index.

        Returns:
            Operation result.
        """
        index = self.client.init_index(index_name)
        return index.clear_objects()

    async def partial_update_object(
        self,
        index_name: str,
        object_id: str,
        attributes: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Partially update object in index.

        Args:
            index_name: Name of the index.
            object_id: Object ID.
            attributes: Attributes to update.

        Returns:
            Operation result.
        """
        index = self.client.init_index(index_name)
        attributes["objectID"] = object_id
        return index.partial_update_object(attributes)

    async def get_objects(
        self,
        requests: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Get multiple objects from different indices.

        Args:
            requests: List of request dicts with indexName, objectID, etc.

        Returns:
            Retrieved objects.
        """
        results = []
        for req in requests:
            index = self.client.init_index(req["indexName"])
            obj = index.get_object(
                req["objectID"],
                req.get("attributesToRetrieve"),
            )
            results.append(obj)

        return {"results": results}

    async def list_indices(
        self,
    ) -> Dict[str, Any]:
        """List all indices.

        Returns:
            Dictionary with indices information.
        """
        return self.client.list_indices()
