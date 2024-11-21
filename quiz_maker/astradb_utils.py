import os

from dotenv import load_dotenv
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.astra_db import AstraDBVectorStore
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter

load_dotenv()

ASTRA_DB_COLLECTION = os.environ.get("ASTRA_DB_COLLECTION")
ASTRA_DB_API_ENDPOINT = os.environ.get("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_TOKEN = os.environ.get("ASTRA_DB_TOKEN")

def save_vectors_to_astra(llama_docs):
    astra_db_store = AstraDBVectorStore(
        token=ASTRA_DB_TOKEN,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        collection_name=ASTRA_DB_COLLECTION,
        embedding_dimension=1536
    )
    
    storage_context = StorageContext.from_defaults(vector_store=astra_db_store)
    index = VectorStoreIndex.from_documents(
        llama_docs, storage_context=storage_context
    )
    
    return index

def get_query_engine(education_resources_id: str):

   
    astra_db_store = AstraDBVectorStore(
        token=ASTRA_DB_TOKEN,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        collection_name=ASTRA_DB_COLLECTION,
        embedding_dimension=1536
    )

    index = VectorStoreIndex.from_vector_store(vector_store=astra_db_store)
    query_engine = index.as_query_engine(
        filters = MetadataFilters(
            filters=[
                ExactMatchFilter(key="education_resources_id", value=education_resources_id)
            ]
        )
    )
    
    return query_engine
