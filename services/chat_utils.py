import re

def extract_song_and_artist(user_input):
    """Extracts the song and artist name from user input."""
    match = re.search(r'play\s+"?([^"]+)"?\s+by\s+([^"]+)', user_input, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None
