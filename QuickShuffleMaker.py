import os
import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import threading
import functools
import time
import re

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


def with_progress(message_template=None, interval=0.6):
    """Decorator: show lightweight progress messages while a function runs.

    - `message_template` may be a format string where positional args from the
      wrapped function are substituted (e.g. "作業中: {}") . If omitted, the
      function name is used.
    - `interval` controls how often the spinner updates (seconds).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Prepare message
            try:
                if message_template:
                    msg = message_template.format(*args, **kwargs)
                else:
                    msg = f"{func.__name__} 実行中"
            except Exception:
                msg = f"{func.__name__} 実行中"

            stop_event = threading.Event()

            def spinner():
                chars = "|/-\\"
                i = 0
                while not stop_event.is_set():
                    print(f"{msg} {chars[i % len(chars)]}", end='\r', flush=True)
                    i += 1
                    stop_event.wait(interval)
                # clear line
                print(' ' * 80, end='\r', flush=True)

            th = threading.Thread(target=spinner, daemon=True)
            th.start()
            try:
                return func(*args, **kwargs)
            finally:
                stop_event.set()
                th.join()
                print(f"{msg} 完了")

        return wrapper
    return decorator

# -------------------------
# アーティスト検索 → ID取得
# -------------------------
@with_progress("アーティスト検索中: {}", interval=0.4)
def get_artist_id(name):
    result = sp.search(q=name, type="artist", limit=1)
    if result["artists"]["items"]:
        return result["artists"]["items"][0]["id"]
    return None

# -------------------------
# アーティストの全曲を取得
# -------------------------
@with_progress("曲取得中 (アーティストID: {})", interval=0.6)
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
@with_progress("プレイリストに追加中: {}", interval=0.6)
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


def parse_artist_token(token):
    """Parse an artist token which may be:

    - a plain artist name (e.g. "Eve")
    - a Spotify artist ID (22 chars, alphanumeric)
    - a Spotify URI (e.g. "spotify:artist:ID")
    - a Spotify artist URL (e.g. "https://open.spotify.com/artist/ID")
    - an explicit directive like "id:ID" or "artist_id:ID"

    Returns a tuple (is_id, value) where `is_id` is True when `value`
    is already a Spotify artist ID; otherwise `value` is treated as a
    search name.
    """
    t = token.strip()
    if not t:
        return False, t

    # Remove common wrapping characters/backticks while parsing
    cleaned = t.replace('`', '').strip()
    low = cleaned.lower()

    # explicit prefix
    if low.startswith('id:'):
        return True, cleaned.split(':', 1)[1].strip()
    if low.startswith('artist_id:'):
        return True, cleaned.split(':', 1)[1].strip()

    # spotify uri anywhere in the line (allow labels like "Spotify URI:")
    m_uri = re.search(r"spotify:artist:([A-Za-z0-9]+)", cleaned, re.IGNORECASE)
    if m_uri:
        return True, m_uri.group(1)

    # spotify url anywhere in the line
    m_url = re.search(r"open\.spotify\.com/artist/([A-Za-z0-9]+)", cleaned, re.IGNORECASE)
    if m_url:
        return True, m_url.group(1)

    # direct-ish ID: spotify IDs are typically 22 chars base62-ish
    if 20 <= len(cleaned) <= 24 and cleaned.isalnum():
        return True, cleaned

    # otherwise treat as name
    return False, cleaned


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
    for token in artist_names:
        is_id, val = parse_artist_token(token)
        if is_id:
            aid = val
        else:
            aid = get_artist_id(val)

        if aid:
            track_ids.extend(get_all_tracks(aid))
        else:
            print(f"アーティストが見つかりません: {token}")

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
