from dotenv import load_dotenv
import os
import openai
from fastapi import UploadFile
import pymupdf4llm
import tempfile
from llama_index.core import GPTVectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

def answer_question_from_pdf(pdf_file: UploadFile, question: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.file.read())
        tmp_path = tmp.name
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_doc = llama_reader.load_data(tmp_path)
    
    # set openai embedding model and llm
    Settings.embed_model = OpenAIEmbedding(model=os.getenv("OPENAI_EMBED_MODEL"))
    Settings.llm = OpenAI(model=os.getenv("OPENAI_LLM_MODEL"))
    
    index = GPTVectorStoreIndex.from_documents(
        llama_doc
    )
    
    # create query engine
    query_engine = index.as_query_engine()
    try:
        response = query_engine.query(question)
        return response
    except openai.RateLimitError as e:
        return f"Rate limit exceeded: {e}"
