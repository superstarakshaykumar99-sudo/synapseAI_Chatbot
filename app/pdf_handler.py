import os
import fitz  # PyMuPDF
from openai import OpenAI
import numpy as np

from app.config import DOCS_DIR, FAISS_INDEX_PATH, EMBEDDING_MODEL
from utils.helpers import chunk_text
from utils.logger import logger

class VectorStore:
    def __init__(self):
        logger.info("Initializing vector store with OpenAI Embeddings...")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY is not set. Vector store (PDF Chat) will temporarily be disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
        
        self.embeddings_file = os.path.join(FAISS_INDEX_PATH, "embeddings.npy")
        self.texts_file = os.path.join(FAISS_INDEX_PATH, "texts.npy")
        
        self.embeddings = []
        self.chunks = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.embeddings_file) and os.path.exists(self.texts_file):
            logger.info("Loading existing Numpy index...")
            self.embeddings = np.load(self.embeddings_file, allow_pickle=True).tolist()
            self.chunks = np.load(self.texts_file, allow_pickle=True).tolist()
            logger.info(f"Loaded {len(self.chunks)} chunks from vector store.")
        else:
            logger.info("Creating new Numpy index...")
            self.embeddings = []
            self.chunks = []

    def save(self):
        np.save(self.embeddings_file, np.array(self.embeddings))
        np.save(self.texts_file, np.array(self.chunks))
        logger.info("Saved Numpy index to disk.")

    def add_texts(self, texts: list[str]):
        if not texts or not self.client:
            logger.warning("Cannot index PDF: OPENAI_API_KEY is not set.")
            return
            
        # Get embeddings from OpenAI
        response = self.client.embeddings.create(input=texts, model="text-embedding-3-small")
        new_embeddings = [data.embedding for data in response.data]
        
        self.embeddings.extend(new_embeddings)
        self.chunks.extend(texts)
        self.save()
        logger.info(f"Added {len(texts)} new chunks to vector store.")

    def search(self, query: str, k: int = 3) -> list[str]:
        if not self.chunks or len(self.embeddings) == 0 or not self.client:
            return []
            
        response = self.client.embeddings.create(input=[query], model="text-embedding-3-small")
        query_vector = np.array(response.data[0].embedding)
        
        # Compute cosine similarity using numpy
        db_vectors = np.array(self.embeddings)
        similarities = np.dot(db_vectors, query_vector) / (np.linalg.norm(db_vectors, axis=1) * np.linalg.norm(query_vector))
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        results = [self.chunks[i] for i in top_indices if i < len(self.chunks)]
        return results

# Global singleton
vector_store = VectorStore()

def process_pdf(file_path: str):
    """Extracts text from PDF, chunks it, and adds to vector store."""
    logger.info(f"Processing PDF: {file_path}")
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
            
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        vector_store.add_texts(chunks)
        
        return True, f"Successfully processed and indexed {len(chunks)} chunks."
    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {e}")
        return False, str(e)

def get_context_for_query(query: str, k: int = 3) -> str:
    """Retrieves relevant text chunks for a given query."""
    results = vector_store.search(query, k=k)
    if not results:
        return ""
    return "\\n\\n---\\n\\n".join(results)
