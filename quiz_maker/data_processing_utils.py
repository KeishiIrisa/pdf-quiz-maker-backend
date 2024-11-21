from typing import List

import tempfile
import pymupdf4llm

def process_pdf_file(pdf_file) -> List:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.file.read())
        tmp_path = tmp.name
    
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_docs = llama_reader.load_data(tmp_path)
    
    return llama_docs

def process_from_llama_docs_to_text(llama_docs: List, education_resources_id: str) -> str:
    for doc in llama_docs:
        # TODO uidがハードコーディングなので編集すること
        doc.metadata["uid"] = "1234abcd"
        doc.metadata["education_resources_id"] = education_resources_id
    
    # TODO ここわざわざllama_docにする必要あるの？
    combined_text = "\n".join(doc.text for doc in llama_docs)
    
    return combined_text
