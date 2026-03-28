"""RAG (Retrieval-Augmented Generation) knowledge base for agent"""

from abc import ABC, abstractmethod
from typing import Any

from src.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeBase(ABC):
    """Abstract base class for knowledge base implementations"""

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """Retrieve relevant documents for a query"""

    @abstractmethod
    async def add_document(self, content: str, metadata: dict[str, Any] | None = None):
        """Add a document to the knowledge base"""


class SimpleKnowledgeBase(KnowledgeBase):
    """Simple in-memory knowledge base for POC"""

    def __init__(self):
        """Initialize knowledge base"""
        self.documents: list[dict[str, Any]] = []
        self._load_default_knowledge()

    def _load_default_knowledge(self):
        """Load default knowledge for the agent"""
        default_docs = [
            {
                "content": "Our product is a comprehensive CRM solution that helps businesses manage customer relationships.",
                "metadata": {"category": "product", "type": "overview"},
            },
            {
                "content": "We offer free consultation calls for new customers to understand their needs.",
                "metadata": {"category": "sales", "type": "offer"},
            },
            {
                "content": "Appointments can be scheduled Monday through Friday, 9 AM to 5 PM EST.",
                "metadata": {"category": "scheduling", "type": "availability"},
            },
            {
                "content": "Our pricing starts at $99 per month for the basic plan.",
                "metadata": {"category": "pricing", "type": "rates"},
            },
            {
                "content": "We provide 24/7 support for all our customers.",
                "metadata": {"category": "support", "type": "policy"},
            },
        ]

        for doc in default_docs:
            self.documents.append(doc)
            logger.info("Loaded knowledge document", category=doc["metadata"].get("category"))

    async def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """Retrieve relevant documents for a query"""
        query_lower = query.lower()
        scored_docs = []

        for doc in self.documents:
            content_lower = doc["content"].lower()
            relevance_score = self._calculate_relevance(query_lower, content_lower)

            if relevance_score > 0:
                scored_docs.append((doc["content"], relevance_score))

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        results = [doc[0] for doc in scored_docs[:top_k]]

        logger.info("Retrieved knowledge documents", query=query[:50], count=len(results))
        return results

    async def add_document(self, content: str, metadata: dict[str, Any] | None = None):
        """Add a document to the knowledge base"""
        doc = {
            "content": content,
            "metadata": metadata or {},
        }
        self.documents.append(doc)
        logger.info(
            "Added knowledge document", category=metadata.get("category") if metadata else None
        )

    def _calculate_relevance(self, query: str, content: str) -> float:
        """Simple keyword-based relevance scoring"""
        query_words = set(query.split())
        content_words = set(content.split())

        # Simple Jaccard similarity
        intersection = len(query_words & content_words)
        union = len(query_words | content_words)

        if union == 0:
            return 0.0

        return intersection / union


class LLMKnowledgeBase(KnowledgeBase):
    """LLM-based knowledge base using embeddings"""

    def __init__(self, api_key: str):
        """Initialize LLM knowledge base"""
        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=api_key)
            self.documents: list[dict[str, Any]] = []
            self.embeddings: dict[str, list[float]] = {}
            logger.info("Initialized LLM knowledge base")
        except ImportError:
            raise ImportError("OpenAI client required for LLMKnowledgeBase")

    async def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """Retrieve relevant documents using embeddings"""
        if not self.documents:
            return []

        try:
            # Get query embedding
            query_response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query,
            )
            query_embedding = query_response.data[0].embedding

            # Calculate similarities
            import numpy as np

            similarities = []

            for i, doc in enumerate(self.documents):
                doc_content = doc["content"]
                doc_embedding = self.embeddings.get(doc_content)

                if doc_embedding:
                    similarity = np.dot(query_embedding, doc_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                    )
                    similarities.append((doc_content, similarity))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            results = [doc[0] for doc in similarities[:top_k]]

            logger.info("Retrieved documents via embeddings", query=query[:50], count=len(results))
            return results

        except Exception as e:
            logger.error("Failed to retrieve documents via embeddings", error=str(e))
            return []

    async def add_document(self, content: str, metadata: dict[str, Any] | None = None):
        """Add a document and compute its embedding"""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=content,
            )
            embedding = response.data[0].embedding

            self.documents.append({"content": content, "metadata": metadata or {}})
            self.embeddings[content] = embedding

            logger.info(
                "Added document with embedding",
                category=metadata.get("category") if metadata else None,
            )

        except Exception as e:
            logger.error("Failed to add document", error=str(e))


class KnowledgeBaseFactory:
    """Factory for creating knowledge base instances"""

    @staticmethod
    def create(kb_type: str = "simple", **kwargs) -> KnowledgeBase:
        """Create a knowledge base instance"""
        if kb_type == "simple":
            return SimpleKnowledgeBase()
        if kb_type == "llm":
            return LLMKnowledgeBase(**kwargs)
        return SimpleKnowledgeBase()
