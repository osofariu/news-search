from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import logging

logger = logging.getLogger(__name__)


class Index:
    def create_vector_store(self, search_date):
        schema = ".[].headline"
        vector_store_name = f"index/{search_date}.faiss_index"

        if os.path.exists(vector_store_name):
            return
        else:
            print(f"Indexing {search_date}")

        # Load your document
        loader = JSONLoader(f"cache/{search_date}.json", jq_schema=schema)
        documents = loader.load()

        # Split the document into manageable chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)

        # Initialize the OpenAI Embeddings
        embeddings = OpenAIEmbeddings()

        # Create a FAISS vector store from the documents and embeddings
        vector_store = FAISS.from_documents(docs, embeddings)

        # Save the FAISS index to disk
        vector_store.save_local(f"index/{search_date}.faiss_index")

    def search_index(self, archive_date, topic):
        embeddings = OpenAIEmbeddings()
        logger.info(f"Looking for index: {f"index/{archive_date}.faiss_index"}")
        get_vector_store = FAISS.load_local(
            f"index/{archive_date}.faiss_index",
            embeddings,
            allow_dangerous_deserialization=True,
        )

        results = get_vector_store.similarity_search(topic, k=5)

        logger.info(
            f"index matches: for {topic} in {archive_date}: {[result.page_content for result in results]}"
        )
        return [result.page_content for result in results]
