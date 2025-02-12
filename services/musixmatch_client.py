import os
import requests

MUSIXMATCH_API_KEY = os.getenv("MUSIXMATCH_API_KEY")

def get_lyrics_and_artist_info(song_name, artist_name):
    try:
        # Fetch lyrics
        lyrics_url = f"https://api.musixmatch.com/ws/1.1/matcher.lyrics.get?q_track={song_name}&q_artist={artist_name}&apikey={MUSIXMATCH_API_KEY}"
        lyrics_response = requests.get(lyrics_url).json()
        lyrics = lyrics_response.get("message", {}).get("body", {}).get("lyrics", {}).get("lyrics_body", "Lyrics not found.")

        # Extract main verse (first 8 lines)
        lyrics_lines = lyrics.split('\n')
        main_verse = '\n'.join(lyrics_lines[:8])

        # Fetch artist info
        artist_url = f"https://api.musixmatch.com/ws/1.1/artist.search?q_artist={artist_name}&apikey={MUSIXMATCH_API_KEY}"
        artist_response = requests.get(artist_url).json()
        artist_info = "No artist info available."

        if "message" in artist_response and "body" in artist_response["message"]:
            artist_list = artist_response["message"]["body"].get("artist_list", [])
            if artist_list:
                artist_desc = artist_list[0]["artist"].get("artist_name", "") + " is a popular artist known for their unique sound."
                artist_info = artist_desc

        return artist_info, main_verse
    except Exception:
        return "Error fetching artist info", "Error fetching lyrics"
