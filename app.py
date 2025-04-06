from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Memory file path
MEMORY_FILE = "memory.json"

# Ensure memory file exists
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)

# Load memory
def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

# Save memory
def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")

    memory = load_memory()
    memory.append({"role": "user", "text": user_msg})

    # Prepare messages for Gemini
    chat_input = []
    for m in memory[-10:]:  # send last 10 messages only
        chat_input.append({"role": m["role"], "parts": [m["text"]]})

    try:
        response = model.generate_content(chat_input)
        bot_reply = response.text.strip()

        memory.append({"role": "model", "text": bot_reply})
        save_memory(memory)

        return jsonify({"reply": bot_reply})
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"reply": "Oops! Something went wrong."})

if __name__ == "__main__":
    app.run(debug=True)
