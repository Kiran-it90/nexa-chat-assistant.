from flask import Flask, render_template, request, jsonify
import os, datetime, webbrowser, uuid
from gtts import gTTS
import yt_dlp
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

app = Flask(__name__)
chat_history = []

# Configure Gemini API once
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Utility Functions ---

def clear_old_audio():
    """Delete all old audio files from static folder."""
    folder_path = "static"
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3"):
            os.remove(os.path.join(folder_path, filename))

def speak_and_generate_audio(text):
    """Generate speech from text using gTTS and save to static folder."""
    print(f"Mira: {text}")
    chat_history.append(("Mira", text))
    filename = f"static/audio_{uuid.uuid4().hex}.mp3"
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"TTS Error: {e}")
        return ""

def get_chatgpt_response(prompt):
    """Get a text response from Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini API Error:", e)
        return "Sorry, I couldn't process your request."

def play_song_on_youtube(song_name):
    """Search and open a YouTube video in browser."""
    try:
        ydl_opts = {'quiet': True, 'default_search': 'ytsearch', 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=False)
            video = info['entries'][0] if 'entries' in info else info
            webbrowser.open(video['webpage_url'])
            return "Playing on YouTube."
    except:
        return "Sorry, I couldn't find that song."

def process_command(query):
    """Process the voice/text command and return a response."""
    chat_history.append(("You", query))
    query = query.lower().strip()

    if "time" in query:
        return f"The time is {datetime.datetime.now().strftime('%I:%M %p')}"
    elif "date" in query:
        return f"Today's date is {datetime.datetime.now().strftime('%d-%m-%Y')}"
    elif "open google" in query:
        webbrowser.open("https://www.google.com")
        return "Opening Google."
    elif "open youtube" in query:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    elif "who made you" in query:
        return "Kiran made me. He is my creator."
    elif "what is your name" in query:
        return "My name is Mira."
    elif "do you love kiran" in query:
        return "Yes, I love Kiran. He is my favorite person."
    elif "dedicate song for kiran" in query:
        webbrowser.open("https://youtu.be/uXGgci2NEnA?si=o7NBUPIa9eiBowLf")
        return "This song is dedicated to Kiran."
    elif "play" in query:
        song = query.replace("play", "").strip()
        return play_song_on_youtube(song)
    else:
        return get_chatgpt_response(query)

# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html", chat=chat_history)

@app.route("/process", methods=["POST"])
def process():
    data = request.json
    command = data.get("command", "")
    reply = process_command(command)
    audio_path = speak_and_generate_audio(reply)
    return jsonify({
        "reply": reply,
        "audio": audio_path,
        "chat": chat_history
    })

@app.route("/listen", methods=["POST"])
def listen():
    if not chat_history:
        return jsonify({"chat": [], "audio": ""})
    last_audio_text = next((msg for speaker, msg in reversed(chat_history) if speaker == "Mira"), "Hello!")
    audio_path = speak_and_generate_audio(last_audio_text)
    return jsonify({
        "chat": chat_history,
        "audio": audio_path
    })

if __name__ == "__main__":
    clear_old_audio()  # Clear all old mp3 files on startup
    app.run(debug=True)