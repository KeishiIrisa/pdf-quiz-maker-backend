# TODO

- main.py
  - PDF ファイルを受け取り、
- pdf_process.py
  - 受け取った PDF ファイルを PyMuPDF4llm を用いてマークダウンテキストに加工する
- generate_quiz.py
  - pdf_process.py で作成したマークダウンからクイズをオブジェクト形式にして return する
    - llamaindex の ChatPromptsTemplate が使用できそう[https://arc.net/l/quote/rwbrrgey]
    - step1: llamaIndex の queryengine で
  - LlamaIndex が使用できそう
- {supabase への書き込み}.py
  - quiz を supabase に書き込んで保存する

# generate_quiz's architecture

1. クライアントから覚えたい部分、単語を受け取る

- いつか chrome の拡張機能にして、選択した部分を body に含めて、API 叩く

2. prompt に受け取った覚えたい部分を含めて、RAG を使用してクイズを生成

- (ex){グルコース}に関する問題を生成してください
- JSON structured で response、さらに参考にしたファイル内の文章をハイライト

3. response を DB に保存

4. (発展)ファイルをアップロードするだけで、重要な部分をリスト化 → それを for 文でテスト生成

# embedding architecture

1. pdf ファイルが新しいものだったら、embedding して storage を作る
2. 2 回め以降の RAG だったら、保存した storage から利用する(参考)[https://youtu.be/D4MjdLDEIpc?si=liU6IQQHBO1JRSqu]

# DB architecture

## Astra DB

1.

## SupaBase

1.

# Error

- Dockerfile で ENV を指定しても正しく反映されない（WORKDIR や PORT など）
