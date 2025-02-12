import os
import re
import requests
from flask import Flask, request, Response, render_template
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
from lyrics_scraper import get_lyrics

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a music assistant that can:
- Fetch lyrics when users ask about songs
- Find YouTube videos for songs
- Provide music recommendations and trivia
- Extract song or video names from user requests"""

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
MUSIXMATCH_API_KEY = "cf748eb6bbf678ec3b6eae7e175f9e29"

def get_youtube_video(query):
    try:
        params = {
            "part": "snippet",
            "q": query,
            "key": YOUTUBE_API_KEY,
            "maxResults": 1,
            "type": "video"
        }

        response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=params,
            timeout=10
        )
        data = response.json()

        if response.status_code != 200 or "items" not in data or not data["items"]:
            return None

        video_id = data["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        return None

def extract_song_and_artist(user_input):
    """Extracts the song and artist name from user input."""
    match = re.search(r'play\s+"?([^\"]+)"?\s+by\s+([^\"]+)', user_input, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

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
    except Exception as e:
        return "Error fetching artist info", "Error fetching lyrics"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return "Message cannot be empty", 400

    song_name, artist_name = extract_song_and_artist(user_message)

    if not song_name or not artist_name:
        return "Could not extract song and artist name. Please provide input in the format: Play [song] by [artist]", 400

    if user_message.lower().startswith("play"):
        artist_info, lyrics = get_lyrics_and_artist_info(song_name, artist_name)
        video_url = get_youtube_video(song_name)
        video_link = f"🎬 Listen the music <a href='{video_url}' target='_blank'>here</a>" if video_url else "❌ No video found."

        response = f"""
        {artist_info}
        <br><br>
        C'mon Sing with me :
        <br><br>
        <i>"{lyrics}"</i>
        <br><br>
        Wanna listen to full song?
        <br><br>
        {video_link}
        """
        return response

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    def generate_response():
        try:
            chat_completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                max_tokens=300,
                stream=True
            )
            response_buffer = ""
            for chunk in chat_completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    response_buffer += token
                    formatted_response = response_buffer.replace("- ", "<br>• ").replace("\n", "<br>")
                    formatted_response = formatted_response.replace("**", "<b>", 1).replace("**", "</b>", 1)
                    if token.endswith((" ", ".", "!", "?", "\n")):
                        yield formatted_response
                        response_buffer = ""
            if response_buffer:
                yield formatted_response
        except Exception as e:
            yield f"⚠️ Error: {str(e)}"

    return Response(generate_response(), content_type='text/html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)