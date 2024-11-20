import os
import tempfile
import json
from typing import List

from dotenv import load_dotenv
from fastapi import UploadFile
from pydantic import BaseModel
import openai
import pymupdf4llm
from llama_index.core import GPTVectorStoreIndex, Settings, PromptTemplate, StorageContext, VectorStoreIndex
from llama_index.core.base.response.schema import PydanticResponse
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.astra_db import AstraDBVectorStore

from quiz_maker.mongodb_utils import insert_quiz
from quiz_maker.models import Quiz, Source


load_dotenv()

ASTRA_DB_COLLECTION = os.environ.get("ASTRA_DB_COLLECTION")
ASTRA_DB_API_ENDPOINT = os.environ.get("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_TOKEN = os.environ.get("ASTRA_DB_TOKEN")


def answer_question_from_pdf(pdf_file: UploadFile, learning_content: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.file.read())
        tmp_path = tmp.name
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_doc = llama_reader.load_data(tmp_path)
    
    # # set openai embedding model
    # Settings.embed_model = OpenAIEmbedding(model=os.getenv("OPENAI_EMBED_MODEL"))
    
    # set structured llm
    llm = OpenAI(model=os.getenv("OPENAI_LLM_MODEL"))
    structured_llm = llm.as_structured_llm(Quiz)
    Settings.llm = structured_llm
    
    # index = GPTVectorStoreIndex.from_documents(
    #     llama_doc
    # )
    astra_db_store = AstraDBVectorStore(
        token=ASTRA_DB_TOKEN,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        collection_name=ASTRA_DB_COLLECTION,
        embedding_dimension=1536
    )
    
    storage_context = StorageContext.from_defaults(vector_store=astra_db_store)
    index = VectorStoreIndex.from_documents(
        llama_doc, storage_context=storage_context
    )
    
    # create query engine
    query_engine = index.as_query_engine()
    
    # create an prompt template
    prompt_tmpl = PromptTemplate(
        "あなたは学習教材から、より理解を深めるための問題とその答えを作成する役割が与えられています。{learning_content}を覚えるための問題とその答え、その問題の解説の3つを与えられたデータ形式で出力しなさい。ただしSourcesの値は空配列にしておくこと"
    )
    structured_prompt = prompt_tmpl.format(learning_content=learning_content)
    
    try:
        response_llamaindex: PydanticResponse = query_engine.query(structured_prompt)
        
        if response_llamaindex is None:
            raise ValueError("Query returned None")
        
        # change each response value(response, source_nodes) to dictionary type
        response_dict = response_llamaindex.response.model_dump()
        source_nodes_dict = [node.model_dump() for node in response_llamaindex.source_nodes]
        
        sources = [
            Source(
                text=source_node["node"]["text"],
                page=source_node["node"]["relationships"]["1"]["metadata"]["page"],
                file_path=source_node["node"]["relationships"]["1"]["metadata"]["file_path"],
                score=source_node["score"]
            )
            for source_node in source_nodes_dict
        ]
        
        # Create Quiz object
        quiz = Quiz(
            question=response_dict["question"],
            answer=response_dict["answer"],
            description=response_dict["description"],
            sources=sources
        )

        # # store in mongodb
        # insert_quiz(quiz.model_dump())
        
        return quiz
    except openai.RateLimitError as e:
        return f"Rate limit exceeded: {e}"
    except Exception as e:
        return f"An error occurred: {e}"
