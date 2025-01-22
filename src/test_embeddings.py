from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import CharacterTextSplitter

schema = ".[].abstract"

# Load your document
loader = JSONLoader("cache/2023-08.json", jq_schema=schema)
documents = loader.load()

# Split the document into manageable chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

from langchain_openai import OpenAIEmbeddings

# Initialize the OpenAI Embeddings
embeddings = OpenAIEmbeddings()

from langchain_community.vectorstores import FAISS

# Create a FAISS vector store from the documents and embeddings
vector_store = FAISS.from_documents(docs, embeddings)

# Define your query
query = "Putin and Ukraine"

# Perform the search
results = vector_store.similarity_search(query, k=3)

# Display the results
for result in results:
    print(result.page_content)
