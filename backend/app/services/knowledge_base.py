"""
Knowledge base service for Chroma vector DB integration.
Handles ingestion, embedding, and retrieval of knowledge base documents.

Uses HuggingFace Embeddings (free, local) instead of OpenAI Embeddings.
"""
import os
from typing import List, Optional

from app.config import settings

# Try to import langchain + HuggingFace - fallback gracefully
try:
    from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class KnowledgeBase:
    """Manages Chroma vector store for knowledge base documents.
    
    Embeddings use the free, locally-run sentence-transformers/all-MiniLM-L6-v2
    model, so no API key is needed for the RAG pipeline.
    """

    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self._initialized = False

    def initialize(self):
        """Initialize embeddings and connect to Chroma."""
        if self._initialized:
            return

        if not LANGCHAIN_AVAILABLE:
            print("Warning: langchain not fully installed. Knowledge base will use mock mode.")
            self._initialized = True
            return

        print("Initialising HuggingFace embeddings (sentence-transformers/all-MiniLM-L6-v2)...")
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        except Exception as e:
            print(f"Warning: Could not load HuggingFace embeddings: {e}")
            print("Knowledge base will use mock mode.")
            self._initialized = True
            return

        persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(persist_dir, exist_ok=True)

        try:
            self.vector_store = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=persist_dir,
            )
            count = self.vector_store._collection.count()
            print(f"Chroma collection '{settings.COLLECTION_NAME}' has {count} documents.")
        except Exception as e:
            print(f"Warning: Could not connect to Chroma: {e}")
            self.vector_store = None

        self._initialized = True

    def ingest_pdfs(self, directory_path: str) -> int:
        """
        Load PDFs from directory, chunk them, embed, and store in Chroma.
        Returns number of chunks ingested.
        """
        if not LANGCHAIN_AVAILABLE:
            print("Mock mode: Skipping PDF ingestion (langchain not available).")
            return 0

        self.initialize()

        if self.embeddings is None:
            print("Mock mode: Embeddings unavailable, cannot ingest.")
            return 0

        if not os.path.isdir(directory_path):
            print(f"Directory not found: {directory_path}")
            return 0

        loader = DirectoryLoader(
            directory_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
        )
        documents = loader.load()

        if not documents:
            print(f"No PDF files found in {directory_path}")
            return 0

        print(f"Loaded {len(documents)} PDF pages/documents.")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks.")

        if self.vector_store is None:
            persist_dir = settings.CHROMA_PERSIST_DIR
            os.makedirs(persist_dir, exist_ok=True)
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name=settings.COLLECTION_NAME,
                persist_directory=persist_dir,
            )
        else:
            self.vector_store.add_documents(chunks)

        self.vector_store.persist()
        print(f"Ingested {len(chunks)} chunks into Chroma.")
        return len(chunks)

    def search(self, query: str, k: int = 5) -> List[str]:
        """
        Search the knowledge base for relevant chunks.
        Returns list of text chunks sorted by relevance.
        """
        if not LANGCHAIN_AVAILABLE or self.vector_store is None:
            print("Mock mode: Returning empty search results.")
            return []

        self.initialize()

        try:
            results = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []

    def count_documents(self) -> int:
        """Get the number of documents in the collection."""
        if not LANGCHAIN_AVAILABLE or self.vector_store is None:
            return 0
        try:
            return self.vector_store._collection.count()
        except Exception:
            return 0


# Singleton instance
knowledge_base = KnowledgeBase()