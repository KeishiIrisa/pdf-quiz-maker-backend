# TODO

- main.py
  - PDF ファイルを受け取り、
- pdf_process.py
  - 受け取った PDF ファイルを PyMuPDF4llm を用いてマークダウンテキストに加工する
- generate_quiz.py
  - pdf_process.py で作成したマークダウンからクイズをオブジェクト形式にして return する
  - LlamaIndex が使用できそう
- {supabase への書き込み}.py
  - quiz を supabase に書き込んで保存する

# Error

- Dockerfile で ENV を指定しても正しく反映されない（WORKDIR や PORT など）
