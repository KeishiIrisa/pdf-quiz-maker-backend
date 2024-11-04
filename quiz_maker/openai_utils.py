import os
import tempfile
from typing import List

from dotenv import load_dotenv
from fastapi import UploadFile
from pydantic import BaseModel

import openai
import pymupdf4llm
from llama_index.core import GPTVectorStoreIndex, Settings, PromptTemplate
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

class Quiz(BaseModel):
    question: str
    answer: str
    description: str

def answer_question_from_pdf(pdf_file: UploadFile, learning_content: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.file.read())
        tmp_path = tmp.name
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_doc = llama_reader.load_data(tmp_path)
    
    # set openai embedding model
    Settings.embed_model = OpenAIEmbedding(model=os.getenv("OPENAI_EMBED_MODEL"))
    
    # set structured llm
    llm = OpenAI(model=os.getenv("OPENAI_LLM_MODEL"))
    structured_llm = llm.as_structured_llm(Quiz)
    Settings.llm = structured_llm
    
    index = GPTVectorStoreIndex.from_documents(
        llama_doc
    )
    
    # create query engine
    query_engine = index.as_query_engine()
    
    # create an prompt template
    prompt_tmpl = PromptTemplate(
        "あなたは学習教材から、より理解を深めるための問題とその答えを作成する役割が与えられています。{learning_content}を覚えるための問題とその答え、その問題の解説の3つを与えられたデータ形式で出力しなさい"
    )
    structured_prompt = prompt_tmpl.format(learning_content=learning_content)
    
    try:
        response = query_engine.query(structured_prompt)
        return response
    except openai.RateLimitError as e:
        return f"Rate limit exceeded: {e}"
