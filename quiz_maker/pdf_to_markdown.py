from fastapi import UploadFile
import pymupdf4llm

def convert_pdf_to_makrdown(pdf_file: UploadFile) -> str:
    md_text = pymupdf4llm.to_markdown(pdf_file)
    return md_text[:200]

