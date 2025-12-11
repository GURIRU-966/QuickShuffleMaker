import os
import argparse
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
def read_artists_file(path):
    """Read artists from a text file.

    Supports an optional directive to set the playlist name. The file format:
      - Blank lines ignored
      - Comment lines start with `#` and are ignored, except `# playlist: NAME`
      - A line `playlist: NAME` (or `# playlist: NAME`) sets the playlist name
      - Other non-empty lines are treated as artist names (one per line)

    Returns tuple: (artist_names_list, playlist_name_or_None)
    """
    names = []
    playlist_name = None
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                raw = line.strip()
                if not raw:
                    continue

                # Handle commented directive like: # playlist: My Playlist
                if raw.startswith('#'):
                    directive = raw.lstrip('#').strip()
                    if directive.lower().startswith('playlist:'):
                        playlist_name = directive.split(':', 1)[1].strip()
                    # other comment - ignore
                    continue

                # Handle inline directive: playlist: My Playlist
                if raw.lower().startswith('playlist:'):
                    playlist_name = raw.split(':', 1)[1].strip()
                    continue

                # Normal artist line
                names.append(raw)
    except FileNotFoundError:
        print(f"アーティストファイルが見つかりません: {path}")
    return names, playlist_name


def main():
    parser = argparse.ArgumentParser(description="Create a Spotify playlist from multiple artists")
    parser.add_argument('--artists-file', '-f', help='Path to a text file containing artist names (one per line)')
    parser.add_argument('--artists', '-a', help='Comma-separated artist names')
    parser.add_argument('--playlist-name', '-p', default=None, help='Name for the created playlist (overrides file)')

    args = parser.parse_args()


    # Determine artist names and optional playlist name from file
    artist_names = []
    file_playlist_name = None
    if args.artists_file:
        artist_names, file_playlist_name = read_artists_file(args.artists_file)
    elif args.artists:
        artist_names = [s.strip() for s in args.artists.split(',') if s.strip()]
    else:
        artist_names = ["Yoasobi", "Eve"]  # デフォルト

    if not artist_names:
        print('対象のアーティストが指定されていません。`--artists-file` または `--artists` を使用してください。')
        return

    # Playlist name precedence: CLI option > file directive > default
    playlist_name = args.playlist_name if args.playlist_name else (file_playlist_name if file_playlist_name else 'まとめプレイリスト')

    track_ids = []
    for name in artist_names:
        aid = get_artist_id(name)
        if aid:
            track_ids.extend(get_all_tracks(aid))
        else:
            print(f"アーティストが見つかりません: {name}")

    # 重複を排除（順序を保つ）
    seen = set()
    unique_tracks = []
    for t in track_ids:
        if t not in seen:
            seen.add(t)
            unique_tracks.append(t)

    create_playlist_with_tracks(playlist_name, unique_tracks)


if __name__ == '__main__':
    main()
