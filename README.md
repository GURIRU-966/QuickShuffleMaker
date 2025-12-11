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

仮想環境を使わない場合:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

ルートに `.env` を作成し、Spotify認証情報を設定します:

```ini
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

**`artists-file` の記法（推奨）**

- 行単位で1エントリ（空行は無視）
- コメントは行頭に `#` を付ける
- プレーンテキストで記述（バッククオートや余分な記号は避ける）

例:

```text
# プレイリスト名（任意）
playlist: マイまとめプレイリスト

# アーティスト名（Spotify表示名）
YOASOBI

# SpotifyのアーティストID
artist_id: 5ydDSP9qSxEOlHWnpbblFB

# Spotify URI
spotify_uri: spotify:artist:5eOzdoFyAe6ugv5bhf1wQr

# Spotify URL
spotify_url: https://open.spotify.com/artist/5ofxS8vbpzqmcgfs8LouBQ

# コメントは # で始める
# この行は無視されます
```

- 優先順位: `--playlist-name`（CLI） > `playlist:`（ファイル内） > デフォルト名

**使い方（例）**

ファイル指定で実行（`example.txt` を使用）:

```bash
python3 QuickShuffleMaker.py --artists-file example.txt
```

CLIでプレイリスト名を上書きして実行:

```bash
python3 QuickShuffleMaker.py --artists-file example.txt --playlist-name "週刊プレイリスト"
```

CLIで直接アーティストを渡す（カンマ区切り）:

```bash
python3 QuickShuffleMaker.py --artists "YOASOBI,Eve"
```

実行するとブラウザでSpotifyの認可フローが開き、承認後にプレイリストが作成されます。成功するとプレイリストのURLが表示されます。

**注意事項**
- `.env` にクライアントシークレットを保存する場合は取り扱いに注意してください。公開してしまった場合はSpotifyダッシュボードで再生成してください。

貢献や要望があれば Issue を立ててください。

***

更新内容: README を整理し、`artists-file` 記法と実行例を明確化しました。

バイブコーディング