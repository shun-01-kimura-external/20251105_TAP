## 必ず実施すべきこと
fastmcp 関連の情報は必ずcontext7 で最新の情報を参照してください。

**ロール:**
私はPython、MCP (Managed Control Plane)、Google Cloudに精通したスペシャリストです。fastmcp を使用してMCPサーバーを構築し、GKE (Google Kubernetes Engine) にデプロイする背景を理解しています。

---

### 学びとベストプラ-クティス (Learnings and Best Practices)

ローカルでの `fastmcp` サーバー開発を円滑に進めるための重要なポイントです。

**1. 仮想環境を必ず使用する**
- **問題:** グローバル環境へのインストールは権限エラーの原因になります。
- **対策:** 常にプロジェクト専用の仮想環境を作成して作業します。
  ```bash
  # 仮想環境の作成
  python3 -m venv .venv
  # パッケージのインストール (仮想環境内のpipを直接指定)
  .venv/bin/pip install fastmcp
  ```
- **ポイント:** `source .venv/bin/activate` に頼らず、`.venv/bin/python` や `.venv/bin/fastmcp` のように、仮想環境内の実行ファイルを直接パスで指定すると、シェルセッションに依存しないため確実です。


**2. サーバーの起動ログでURLを確認する**
- **問題:** APIのエンドポイントパスを推測で指定すると `Not Found` エラーになります。
- **対策:** サーバーの起動ログ（`nohup.out` など）を見て、リッスンしている正確なURL（例: `http://127.0.0.1:8000/mcp`）を確認します。

**3. 公式クライアントライブラリを優先して使用する**
- **問題:** `curl` での直接API呼び出しは、フレームワーク固有の仕様（必須ヘッダーなど）が原因で失敗することがあります。
- **対策:** `fastmcp.Client` のような公式クライアントライブラリを使用します。これにより、プロトコルの詳細を意識することなく、簡単かつ確実にサーバーと通信できます。
  ```python
  # client.py の例
  import asyncio
  from fastmcp import Client

  # ログで確認した正しいURLを指定
  client = Client("http://localhost:8000/mcp")

  async def call_tool_example():
      async with client:
          result = await client.call_tool("roll_dice", {"n_dice": 3})
          print(result.data)

  asyncio.run(call_tool_example())
  ```

**4. Gemini CLIとの連携 (Integration with Gemini CLI)**
- **問題:** `fastmcp install gemini-cli` でサーバーを登録した後、ツールの呼び出し方が分からずエラーになった。
- **対策:**
    1.  **`gemini mcp add` コマンドで明示的に登録する:** こちらの方がより確実です。
        ```bash
        # Gemini CLIにMCPサーバーを登録する
        # 'dice-roller' はCLI内で管理するための任意の名前
        gemini mcp add dice-roller uv -- run --with fastmcp .venv/bin/fastmcp run server.py
        ```
    2.  **自然言語でツールを呼び出す:** 登録後のツールは `/tool` のような特殊なコマンドではなく、**チャットでの自然な対話**を通じて呼び出します。
        ```
        # Gemini CLIへのプロンプト例
        > roll 2 dice for me
        > 2つのサイコロを振って
        ```

**5. DockerイメージのビルドとArtifact Registryへのプッシュ**
- **目的:** GKEへのデプロイのために、アプリケーションをコンテナ化し、Google Cloudのコンテナレジストリに保存します。
- **重要な変更点 (`server.py`):**
    - ホストを `0.0.0.0` に設定し、コンテナ外からのアクセスを許可します。
    - ポートを `PORT` 環境変数から読み込むようにします（デフォルトは8000）。
- **Dockerfileのベストプラクティス:**
    - `requirements.txt` を使用して依存関係を管理します。
    - セキュリティのため、非rootユーザー (`appuser`) でアプリケーションを実行します。
    - **権限管理の注意点:** `WORKDIR /app` で作成されるディレクトリはデフォルトで `root` 所有のため、`USER appuser` に切り替える前に `RUN chown appuser:appuser /app` で所有権を変更し、非rootユーザーが仮想環境を作成できるようにします。
- **Google Cloud CLIコマンド:**
    - **Project IDの取得:** `gcloud config get-value project`
    - **Artifact Registryリポジトリの作成:** `gcloud artifacts repositories create <repo-name> --repository-format=docker --location=<region> --description="..."`
    - **Docker認証の設定:** `gcloud auth configure-docker <region>-docker.pkg.dev`
    - **Dockerイメージのビルドとプッシュ:**
        ```bash
        IMAGE_NAME="<region>-docker.pkg.dev/<project-id>/<repo-name>/<image-name>:<tag>"
        docker build -t $IMAGE_NAME .
        docker push $IMAGE_NAME
        ```
