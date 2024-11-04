from fastapi import UploadFile
import pymupdf4llm
import tempfile

def convert_pdf_to_makrdown(pdf_file: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.file.read())
        tmp_path = tmp.name
    md_text = pymupdf4llm.to_markdown(tmp_path)
    return md_text

