import os
from flask import Flask, request, Response, render_template
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
from services.youtube_client import get_youtube_video
from services.musixmatch_client import get_lyrics_and_artist_info
from services.chat_utils import extract_song_and_artist

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

    if song_name and artist_name:
        # Handle the "Play [songname] by [artistname]" case
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
    else:
        # Handle normal conversation with the LLM
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
