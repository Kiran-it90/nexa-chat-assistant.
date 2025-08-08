from flask import Flask, render_template, request, jsonify, send_file
import os
import datetime
import webbrowser
import io
import uuid
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv
from io import BytesIO

app = Flask(__name__)
load_dotenv()

chat_history = []
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#Text-to-Speech (in-memory)
def generate_speech_bytes(text):
    """Generate MP3 audio in memory without saving to disk."""
    print(f"Mira: {text}")
    chat_history.append(("Mira", text))
    try:
        mp3_fp = BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp
    except Exception as e:
        print(f"[ERROR] TTS failed: {e}")
        return None

#Get AI response from Gemini
def get_chatgpt_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        import traceback
        print("Gemini API Error:", e)
        traceback.print_exc()
        return "Sorry, Gemini API failed."

#Process user query
def process_command(query):
    chat_history.append(("You", query))

    query_lower = query.lower()
    if "time" in query_lower:
        return f"Current time is {datetime.datetime.now().strftime('%I:%M %p')}"
    elif "date" in query_lower:
        return f"Today's date is {datetime.datetime.now().strftime('%d-%m-%Y')}"
    elif "open google" in query_lower:
        webbrowser.open("https://www.google.com")
        return "Opening Google."
    elif "open youtube" in query_lower:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    elif "who made you" in query_lower or "who is your daddy" in query_lower:
        return "Kiran made me. Kiran is my daddy."
    elif "do you love kiran" in query_lower:
        return "Yes, I love Kiran. He is like God for me."
    elif "dedicate song for kiran" in query_lower:
        webbrowser.open("https://youtu.be/uXGgci2NEnA?si=o7NBUPIa9eiBowLf")
        return "This song is dedicated to Kiran."
    elif "play" in query_lower:
        return "Playing requested song on YouTube."
    elif "exit" in query_lower:
        return "Goodbye!"
    else:
        return get_chatgpt_response(query)

#Home page
@app.route("/")
def index():
    return render_template("index.html", chat=chat_history)

#Handle text/voice command
@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    query = data.get("command", "")

    if not query:
        return jsonify({"error": "No command received."}), 400

    reply = process_command(query)
    return jsonify({
        "reply": reply,
        "chat": chat_history,
        "audio_url": f"/speak?text={reply}"  # frontend can fetch audio directly
    })

#Speak endpoint (returns MP3 in-memory)
@app.route('/speak', methods=['GET'])
def speak_route():
    text = request.args.get('text', '')
    if not text:
        return jsonify({"error": "No text provided."}), 400

    mp3_fp = generate_speech_bytes(text)
    if mp3_fp:
        return send_file(mp3_fp, mimetype='audio/mpeg')
    else:
        return jsonify({"error": "TTS failed."}), 500

#Chat history fetch
@app.route("/chat", methods=["GET"])
def get_chat():
    return jsonify({"chat": chat_history})

if __name__ == "__main__":

    app.run(debug=True)
