from flask import Flask, request, jsonify, stream_with_context, Response, render_template
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app) 

# Initialize Groq Cloud API client
client = Groq(api_key=os.getenv("GROQ_API_KEY", "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"))

SYSTEM_PROMPT = """
You are a knowledgeable and accurate chatbot specializing in pop music. Here's how you should respond:
- Ensure all responses are factually correct, especially regarding artists, songs, and albums.
- Maintain a conversational and engaging tone.
- Stay up-to-date with the latest music trends, album releases, and viral moments.
- Provide recommendations, trivia, and insights concisely.
- Use bullet points for better readability if the response is longer.

Examples:
- "Hey, have you checked out [Artist]'s latest track? It's making waves! 🎶"
- "Fun fact: [Song] by [Artist] was inspired by [backstory]. Cool, right?"
- "Here’s a quick rundown of [Artist]’s new album:"
  <br>• Tracklist overview
  <br>• Vibes and genre
  <br>• Must-listen songs
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

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
            yield f"Error: {str(e)}"

    return Response(stream_with_context(generate_response()), content_type='text/html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
