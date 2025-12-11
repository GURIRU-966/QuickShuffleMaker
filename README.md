# QuickShuffleMaker

複数アーティストの楽曲をまとめてSpotifyプレイリストを作成する簡易スクリプトです。

**要点**
- Python 3.x と `pip` が必要です。
- 依存は `requirements.txt`（`spotipy`, `python-dotenv`）に記載しています。
- Spotify API（開発者アカウント）で `CLIENT_ID`/`CLIENT_SECRET` を取得してください。

**セットアップ（推奨）**
- 仮想環境を作る場合:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

- もしくは（仮想環境不要）:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

- プロジェクトルートに `.env` を作り、Spotify認証情報を設定します:

```ini
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

**アーティスト指定方法**
1) ファイル指定（推奲）: `artists.txt` のようなテキストファイルに1行1アーティストを書き、`--artists-file` で渡します。

  - ファイル内でプレイリスト名を指定することもできます:
    - `playlist: プレイリスト名` または `# playlist: プレイリスト名`
    - 例:

```text
playlist: マイまとめプレイリスト
Yoasobi
Eve
RADWIMPS
# コメント行は無視されます
```

2) CLIで直接: `--artists "Artist1,Artist2"`（カンマ区切り）

**プレイリスト名の優先順位**
- `--playlist-name`（コマンドライン） > `playlist:`（ファイル内） > デフォルト `まとめプレイリスト`

**実行例**

```bash
# ファイル指定で実行（ファイル内の playlist: を使用）
python3 QuickShuffleMaker.py --artists-file artists.txt

# CLIで上書きして実行
python3 QuickShuffleMaker.py --artists-file artists.txt --playlist-name "週刊プレイリスト"

# 直接CLIで複数アーティストを渡す
python3 QuickShuffleMaker.py --artists "Yoasobi,Eve"
```

実行するとブラウザでSpotifyの認可フローが開き、承認後にプレイリストが作成されます。成功するとプレイリストのURLが表示されます。

**注意 / セキュリティ**
- `.env` にクライアントシークレットを保存する場合は `.gitignore` に追加してください。
- シークレットを誤って公開した場合はSpotifyダッシュボードで再生成してください。

**今後の改善案**
- 同名プレイリストの検出と追記/新規作成オプション
- `artists.json` によるメタ情報対応（追加の曲フィルタ等）
- 対話式入力UIや簡易Web UIの追加

貢献や要望があれば Issue を立ててください。

超バイブコーディングを感じる