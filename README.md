# QuickShuffleMaker

簡単に複数アーティストの楽曲をまとめてプレイリスト作成するためのスクリプトです。

**使い方（概要）**
- **Prerequisites**: Python 3.x と `pip` が必要です。
- 依存パッケージは `requirements.txt` に記載しています。
- 使用するにはSpotify for Developersの登録が必要です(突っかかりがちなリダイレクトURLは"http://127.0.0.1:8888/callback"でいけます)

**セットアップ**
- 依存関係をインストール:

```bash
python3 -m pip install -r requirements.txt
```

- プロジェクトルートに `.env` を作り、Spotify の認証情報を設定してください（以下参照）。

**`.env` に書く内容（例）**
```ini
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=your_redirect_uris_here
```

- 各要素はSpotify for Developersで設定、指定されたものを使用してください。

**実行方法**
- アーティスト名は現状 `QuickShuffleMaker.py` 内の `artist_names` リストを直接編集して指定します。

```bash
python3 QuickShuffleMaker.py
```

実行すると、指定したアーティストの曲をまとめたプレイリストが作成され、Spotify のプレイリスト URL が表示されます。

**セキュリティ**
- 秘密情報は `.env` に入れておき、`.gitignore` で無視するようにしています。万が一 `CLIENT_SECRET` 等を公開してしまった場合は、Spotify のダッシュボードでシークレットを再生成してください。

**今後の予定（短め）**
- 現在は `artist_names` を手動編集する方式ですが、より使いやすくするために以下の改善を予定しています:
	- コマンドライン引数や対話式プロンプトでアーティストを指定できるようにする
	- GUI または簡易 Web UI を検討
	- アーティスト重複や同一曲の重複排除などの改善

貢献や要望があれば Issue を立ててください。

---
小さなメモ: `.gitignore` に `.env` とキャッシュが追加されていることを確認してください（今の設定で追加済みです）。

超バイブコーディングを感じる