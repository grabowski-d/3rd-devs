"""Algolia search."""
import os
class AlgoliaClient:
    def __init__(self):
        self.app_id = os.getenv('ALGOLIA_APP_ID')
        self.api_key = os.getenv('ALGOLIA_API_KEY')
