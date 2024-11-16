import os
import time
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

load_dotenv()

# Configuración de Spotify API
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_SECRET")
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback/'
SCOPE = "playlist-read-private"

# Autenticación de Spotify
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE
))

# Configuración de YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
def authenticate_youtube():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    credentials = flow.run_local_server()
    return build("youtube", "v3", credentials=credentials)

youtube = authenticate_youtube()

def list_spotify_playlists():
    playlists = spotify.current_user_playlists()
    playlist_options = {}
    for i, playlist in enumerate(playlists['items']):
        print(f"{i + 1}. {playlist['name']}")
        playlist_options[i + 1] = playlist['id']
    return playlist_options

def get_spotify_tracks(playlist_id):
    results = spotify.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append(f"{track['name']} {track['artists'][0]['name']}")
    return tracks

def create_youtube_playlist(youtube, name, description="Playlist importada de Spotify"):
    try:
        playlist = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": name,
                    "description": description
                },
                "status": {
                    "privacyStatus": "private"
                }
            }
        ).execute()
        return playlist["id"]
    except HttpError as e:
        print(f"Error al crear la lista de reproducción: {e}")
        raise

def add_to_youtube_playlist(youtube, playlist_id, tracks):
    for track in tracks:
        retries = 5
        while retries > 0:
            try:
                search_response = youtube.search().list(
                    q=track,
                    part="id,snippet",
                    maxResults=1
                ).execute()

                if search_response["items"]:
                    video_id = search_response["items"][0]["id"].get("videoId")
                    if video_id:
                        youtube.playlistItems().insert(
                            part="snippet",
                            body={
                                "snippet": {
                                    "playlistId": playlist_id,
                                    "resourceId": {
                                        "kind": "youtube#video",
                                        "videoId": video_id,
                                    },
                                }
                            }
                        ).execute()
                        print(f"Añadido: {track}")
                break
            except HttpError as e:
                print(f"Error al añadir {track}: {e}")
                if e.resp.status in [409, 503]:
                    retries -= 1
                    print(f"Reintentando... ({5 - retries}/5)")
                    time.sleep(2 ** (5 - retries))  # Espera exponencial
                else:
                    print(f"No se pudo añadir {track}, saltando.")
                    break

if __name__ == "__main__":
    print("Listas de reproducción disponibles en Spotify:")
    playlist_options = list_spotify_playlists()

    choice = int(input("Ingresa el número de la lista de reproducción que deseas transferir: "))
    spotify_playlist_id = playlist_options[choice]

    spotify_playlist_name = spotify.playlist(spotify_playlist_id)["name"]

    tracks = get_spotify_tracks(spotify_playlist_id)

    print(f"Creando lista de reproducción en YouTube Music: {spotify_playlist_name}")
    youtube_playlist_id = create_youtube_playlist(youtube, spotify_playlist_name)

    print("Transfiriendo canciones...")
    add_to_youtube_playlist(youtube, youtube_playlist_id, tracks)
    print(f"¡Transferencia completada! Lista de reproducción creada: {spotify_playlist_name}")
