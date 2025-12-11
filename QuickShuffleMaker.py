import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables from a .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # If dotenv isn't installed, fall back to environment variables
    pass

# API keys and redirect URI are now read from environment variables.
# Put them in a `.env` file or export them in your shell.
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callb")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set in the environment or .env file")

scope = "playlist-modify-public playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

# -------------------------
# アーティスト検索 → ID取得
# -------------------------
def get_artist_id(name):
    result = sp.search(q=name, type="artist", limit=1)
    if result["artists"]["items"]:
        return result["artists"]["items"][0]["id"]
    return None

# -------------------------
# アーティストの全曲を取得
# -------------------------
def get_all_tracks(artist_id):
    tracks = []
    albums = sp.artist_albums(artist_id, album_type="album,single", limit=50)
    
    for album in albums['items']:
        album_tracks = sp.album_tracks(album['id'])
        for t in album_tracks['items']:
            tracks.append(t['id'])
    return tracks

# -------------------------
# プレイリストに全曲を追加
# -------------------------
def create_playlist_with_tracks(name, track_ids):
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user_id, name)
    
    # Spotifyは100曲ずつしか追加できないので分割
    for i in range(0, len(track_ids), 100):
        sp.playlist_add_items(playlist["id"], track_ids[i:i+100])
    
    print("プレイリスト作成完了！ →", playlist["external_urls"]["spotify"])

# -------------------------
# メイン処理
# -------------------------
artist_names = ["Yoasobi", "Eve"]  # ←ここに複数アーティスト名

track_ids = []
for name in artist_names:
    aid = get_artist_id(name)
    if aid:
        track_ids.extend(get_all_tracks(aid))
    else:
        print(f"アーティストが見つかりません: {name}")

create_playlist_with_tracks("まとめプレイリスト", track_ids)
