"""Memory service implementation."""

import json
import os
import uuid
import yaml
import shutil
import glob
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from slugify import slugify

# Reuse OpenAI and Langfuse services from audio-map or context as they are identical
from audio_map.py.openai_service import OpenAIService
from audio_map.py.langfuse_service import LangfuseService
from .vector_store import VectorStore


class MemoryService:
    """Service for managing memories."""

    def __init__(
        self,
        openai_service: OpenAIService,
        langfuse_service: LangfuseService,
        base_dir: str = "memory/memories",
    ):
        """Initialize memory service.

        Args:
            openai_service: OpenAI service instance.
            langfuse_service: Langfuse service instance.
            base_dir: Base directory for memories.
        """
        self.openai_service = openai_service
        self.langfuse_service = langfuse_service
        self.base_dir = base_dir
        self.index_file = os.path.join(self.base_dir, "index.jsonl")
        
        # 3072 for text-embedding-3-large
        self.vector_store = VectorStore(3072, self.base_dir)
        
        # Initialize async (mocked here, should be called in async context)
        # self.vector_store.load()

    async def initialize(self) -> None:
        """Initialize resources asynchronously."""
        await self.vector_store.load()
        await self._ensure_directories()

    async def _ensure_directories(self) -> None:
        """Ensure memory directories exist."""
        categories = [
            "profiles",
            "preferences",
            "resources",
            "events",
            "locations",
            "environment",
        ]
        subcategories = {
            "profiles": ["basic", "work", "development", "relationships"],
            "preferences": ["hobbies", "interests"],
            "resources": [
                "books",
                "movies",
                "music",
                "videos",
                "images",
                "apps",
                "devices",
                "courses",
                "articles",
                "communities",
                "channels",
                "documents",
                "notepad",
            ],
            "events": ["personal", "professional"],
            "locations": ["places", "favorites"],
            "environment": ["current"],
        }

        for category in categories:
            cat_path = os.path.join(self.base_dir, category)
            os.makedirs(cat_path, exist_ok=True)
            
            if category in subcategories:
                for sub in subcategories[category]:
                    os.makedirs(os.path.join(cat_path, sub), exist_ok=True)

    async def _append_to_index(self, memory: Dict[str, Any]) -> None:
        """Append memory to index file.

        Args:
            memory: Memory object.
        """
        with open(self.index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(memory) + "\n")

    def _json_to_markdown(self, memory: Dict[str, Any]) -> str:
        """Convert memory object to markdown with frontmatter.

        Args:
            memory: Memory object.

        Returns:
            Markdown string.
        """
        content = memory.get("content", {})
        text_content = content.pop("text", "")
        
        # Prepare frontmatter data (exclude content)
        frontmatter_data = {k: v for k, v in memory.items() if k != "content"}
        
        # Dump YAML
        yaml_frontmatter = yaml.dump(
            frontmatter_data, sort_keys=False, default_flow_style=False, allow_unicode=True
        )
        
        markdown = f"---\n{yaml_frontmatter}---\n\n{text_content}"
        
        # Add tags
        metadata = memory.get("metadata", {})
        tags = metadata.get("tags", [])
        if tags:
            markdown += "\n\n"
            markdown += " ".join([f"#{tag.replace(' ', '_')}" for tag in tags])
            
        return markdown

    def _markdown_to_json(self, markdown: str) -> Dict[str, Any]:
        """Convert markdown with frontmatter to memory object.

        Args:
            markdown: Markdown content.

        Returns:
            Memory dictionary.
        """
        parts = markdown.split("---")
        if len(parts) < 3:
            raise ValueError("Invalid markdown format")
            
        frontmatter = parts[1]
        content = "---".join(parts[2:]).strip()
        
        data = yaml.safe_load(frontmatter)
        
        # Split hashtags
        content_parts = content.split("\n\n")
        main_content = content
        hashtags = ""
        
        # Heuristic: if last part looks like tags
        if content_parts and content_parts[-1].strip().startswith("#"):
            hashtags = content_parts[-1].strip()
            main_content = "\n\n".join(content_parts[:-1]).strip()
            
            # Extract tags and merge
            tags_from_content = [
                t.replace("#", "").replace("_", " ") for t in hashtags.split()
            ]
            if "metadata" not in data:
                data["metadata"] = {}
            
            current_tags = data["metadata"].get("tags", [])
            data["metadata"]["tags"] = list(set(current_tags + tags_from_content))

        data["content"] = {
            "text": main_content,
            "hashtags": hashtags
        }
        
        return data

    def _get_memory_file_path(self, memory: Dict[str, Any]) -> str:
        """Get file path for memory.

        Args:
            memory: Memory object.

        Returns:
            File path.
        """
        slug_name = slugify(memory["name"])
        slug_cat = slugify(memory["category"])
        slug_sub = slugify(memory["subcategory"])
        
        return os.path.join(
            self.base_dir, slug_cat, slug_sub, f"{slug_name}.md"
        )

    async def create_memory(
        self,
        memory: Dict[str, Any],
        trace: Any,
    ) -> Dict[str, Any]:
        """Create a new memory.

        Args:
            memory: Memory data (without uuid).
            trace: Trace object.

        Returns:
            Created memory.
        """
        new_memory = memory.copy()
        new_memory["uuid"] = str(uuid.uuid4())
        new_memory["created_at"] = datetime.utcnow().isoformat()
        new_memory["updated_at"] = datetime.utcnow().isoformat()
        
        try:
            # Create embedding
            text = new_memory["content"]["text"]
            embedding = await self.openai_service.create_embedding(text)
            
            # Add to vector store
            await self.vector_store.add(embedding, new_memory["uuid"])
            
            # Save file
            file_path = self._get_memory_file_path(new_memory)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            markdown = self._json_to_markdown(new_memory)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown)
                
            await self._append_to_index(new_memory)
            
            self.langfuse_service.create_event(
                trace, "CreateMemory", input=memory, output=new_memory
            )
            
            return new_memory
            
        except Exception as error:
            print(f"Error creating memory: {error}")
            raise

    async def get_memory(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get memory by UUID.

        Args:
            uuid: Memory UUID.

        Returns:
            Memory object or None.
        """
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    mem = json.loads(line)
                    if mem["uuid"] == uuid:
                        # Load full content from file
                        file_path = self._get_memory_file_path(mem)
                        with open(file_path, "r", encoding="utf-8") as mf:
                            return self._markdown_to_json(mf.read())
            return None
        except Exception as error:
            print(f"Error getting memory: {error}")
            return None

    async def search_similar_memories(
        self, query: str, k: int = 15
    ) -> List[Dict[str, Any]]:
        """Search similar memories.

        Args:
            query: Search query.
            k: Number of results.

        Returns:
            List of memories with similarity score.
        """
        embedding = await self.openai_service.create_embedding(query)
        results = await self.vector_store.search(embedding, k)
        
        memories = []
        for res in results:
            mem = await self.get_memory(res["id"])
            if mem:
                mem["similarity"] = res["similarity"]
                memories.append(mem)
                
        return memories

    async def recall(self, queries: List[str], trace: Any) -> str:
        """Recall memories for multiple queries.

        Args:
            queries: List of queries.
            trace: Trace object.

        Returns:
            Formatted XML string of memories.
        """
        try:
            all_memories = []
            seen_uuids = set()
            
            for query in queries:
                mems = await self.search_similar_memories(query)
                for mem in mems:
                    if mem["uuid"] not in seen_uuids:
                        all_memories.append(mem)
                        seen_uuids.add(mem["uuid"])
            
            if not all_memories:
                result = "<recalled_memories>No relevant memories found.</recalled_memories>"
            else:
                formatted = "\n".join([self._format_memory(m) for m in all_memories])
                result = f"<recalled_memories>\n{formatted}\n</recalled_memories>"
                
            self.langfuse_service.create_event(
                trace, "Recall memories", input=queries, output=result
            )
            return result
            
        except Exception as error:
            print(f"Error recalling memories: {error}")
            raise

    def _format_memory(self, memory: Dict[str, Any]) -> str:
        """Format memory for prompt.

        Args:
            memory: Memory object.

        Returns:
            XML string.
        """
        meta = memory.get("metadata", {})
        urls = ""
        if "urls" in meta and meta["urls"]:
            urls = f"\nURLs: {', '.join(meta['urls'])}"
            
        return (
            f'<memory uuid="{memory["uuid"]}" '
            f'name="{memory["name"]}" '
            f'category="{memory["category"]}" '
            f'subcategory="{memory["subcategory"]}" '
            f'lastmodified="{memory["updated_at"]}">'
            f'{memory["content"]["text"]}{urls}'
            f'</memory>'
        )
