from fastapi import FastAPI, UploadFile, File
from quiz_maker.pdf_to_markdown import convert_pdf_to_makrdown

app = FastAPI()

@app.get("/")
def read_root():
    return {"Message": "Hello keishi..."}

@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    markdown_text = convert_pdf_to_makrdown(file)
    return {"filename": file.filename, "markdown": markdown_text}

