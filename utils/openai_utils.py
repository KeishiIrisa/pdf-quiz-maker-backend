import os
import re

import openai
from dotenv import load_dotenv
from llama_index.core import PromptTemplate, Settings
from llama_index.core.base.response.schema import PydanticResponse
from llama_index.llms.openai import OpenAI as OpenAILlamaIndex
from openai import OpenAI

from db.astradb_utils import get_query_engine
from schemas.ai_service import Html, Source
from schemas.quiz import Quiz

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
ASTRA_DB_COLLECTION = os.environ.get("ASTRA_DB_COLLECTION")
ASTRA_DB_API_ENDPOINT = os.environ.get("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_TOKEN = os.environ.get("ASTRA_DB_TOKEN")


def generate_html_from_text(text: str) -> str:
    client = OpenAI()
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "あなたは与えられたテキストを受け取り、視覚的に理解しやすいようにhtmlの形式で出力するアシスタントです。重要な部分が理解しやすいように、表、段落、太字の利用も必要ならば行なってください。ただし元となる受け取った文章は必ず全て改変することなく出力してください。htmlは一番外側をdivタグにすること。出力形式は与えられた形式に従うこと",
            },
            {"role": "user", "content": text},
        ],
        response_format=Html,
    )

    html_content = completion.choices[0].message.parsed.html

    html_content = re.sub(r"\n", "", html_content)
    html_content = re.sub(r">\s+<", "><", html_content)

    return html_content


def generate_quiz_by_education_resources_id(
    education_resources_id: str, learning_content: str
):
    llm = OpenAILlamaIndex(model=os.getenv("OPENAI_LLM_MODEL"))
    structured_llm = llm.as_structured_llm(Quiz)
    Settings.llm = structured_llm

    query_engine = get_query_engine(education_resources_id)

    prompt_tmpl = PromptTemplate(
        "あなたは学習教材から、より理解を深めるための問題とその答えを作成する役割が与えられています。{learning_content}を覚えるための問題とその答え、その問題の解説の3つを与えられたデータ形式で出力しなさい。ただしSourcesの値は空配列にしておくこと"
    )
    structured_prompt = prompt_tmpl.format(learning_content=learning_content)

    try:
        response_llamaindex: PydanticResponse = query_engine.query(structured_prompt)

        if not isinstance(response_llamaindex, PydanticResponse):
            raise ValueError("Query response is Empty Response")

        response_dict = response_llamaindex.response.model_dump()
        source_nodes_dict = [
            node.model_dump() for node in response_llamaindex.source_nodes
        ]

        sources = [
            Source(
                text=source_node["node"]["text"],
                page=source_node["node"]["relationships"]["1"]["metadata"][
                    "page_label"
                ],
                file_path=source_node["node"]["relationships"]["1"]["metadata"][
                    "file_name"
                ],
                score=source_node["score"],
            )
            for source_node in source_nodes_dict
        ]

        quiz = Quiz(
            question=response_dict["question"],
            answer=response_dict["answer"],
            description=response_dict["description"],
            sources=sources,
        )

        return quiz

    except openai.RateLimitError as e:
        raise RuntimeError(f"Rate limit exceeded: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")
