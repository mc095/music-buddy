import os
import requests
from dotenv import load_dotenv

load_dotenv()

MUSIXMATCH_API_KEY = os.getenv("MUSIXMATCH_API_KEY")

def get_lyrics_and_artist_info(song_name, artist_name):
    try:
        # Fetch lyrics
        lyrics_url = f"https://api.musixmatch.com/ws/1.1/matcher.lyrics.get?q_track={song_name}&q_artist={artist_name}&apikey={MUSIXMATCH_API_KEY}"
        lyrics_response = requests.get(lyrics_url).json()
        lyrics = lyrics_response.get("message", {}).get("body", {}).get("lyrics", {}).get("lyrics_body", "Lyrics not found.")
        lyrics_lines = lyrics.split('\n')
        main_verse = '\n'.join(lyrics_lines[:8])  # First 8 lines

        # Hardcoded artist description
        artist_info = f"🎤 {artist_name} is an iconic artist loved by many."

        return artist_info, main_verse

    except Exception as e:
        return f"Error: {str(e)}", "Lyrics not found."
