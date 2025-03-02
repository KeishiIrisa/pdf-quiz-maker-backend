import tempfile
from typing import List

from llama_index.readers.file import PDFReader
from markdown import Markdown


def process_markdown_to_html(markdown_text: str) -> str:
    md = Markdown()
    html = md.convert(markdown_text)
    return html


def process_pdf_file(pdf_file) -> List:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.file.read())
        tmp_path = tmp.name

    llama_reader = PDFReader()
    llama_docs = llama_reader.load_data(tmp_path)

    return llama_docs


def process_from_llama_docs_to_text(
    llama_docs: List, education_resources_id: str
) -> str:
    for doc in llama_docs:
        doc.metadata["uid"] = "1234abcd"
        doc.metadata["education_resources_id"] = education_resources_id

    combined_text = "\n".join(doc.text for doc in llama_docs)

    return combined_text


def change_objectid_to_str(result):
    result["_id"] = str(result["_id"])
    return result
