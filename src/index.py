from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import logging

from cache import NewsCache
from utils import file_is_expired

logger = logging.getLogger(__name__)


class Index:
    def __init__(self, cache=NewsCache(), max_index_age_days=5):
        self.max_index_age_days = max_index_age_days
        self.index_path = "index"
        self.cache = cache

    def create_vector_store(self, search_date):
        schema = ".[].headline"
        vector_store_name = f"{self.index_path}/{search_date}.faiss_index"
        index_file = os.path.join(vector_store_name, "index.faiss")
        if os.path.exists(index_file) and not file_is_expired(
            index_file, search_date, self.max_index_age_days
        ):
            logger.info(f"Index already exists for {search_date} and not expired")
            return
        else:
            logger.info(f"Indexing {search_date}")

        # Load your document
        cached_data = self.cache.get_path(search_date)
        loader = JSONLoader(cached_data, jq_schema=schema)
        documents = loader.load()

        # Split the document into manageable chunks
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)

        # Initialize the OpenAI Embeddings
        embeddings = OpenAIEmbeddings(chunk_size=300)

        # Create a FAISS vector store from the documents and embeddings
        vector_store = FAISS.from_documents(docs, embeddings)

        # Save the FAISS index to disk
        vector_store.save_local(f"{self.index_path}/{search_date}.faiss_index")

    def search_index(self, archive_date, topic):
        embeddings = OpenAIEmbeddings()
        logger.info(
            f"Looking for index: {f"{self.index_path}/{archive_date}.faiss_index"}"
        )
        get_vector_store = FAISS.load_local(
            f"{self.index_path}/{archive_date}.faiss_index",
            embeddings,
            allow_dangerous_deserialization=True,
        )

        results = get_vector_store.similarity_search(topic, k=5)

        logger.info(
            f"index matches: for {topic} in {archive_date}: {[result.page_content for result in results]}"
        )
        return [result.page_content for result in results]
