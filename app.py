from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests

app = FastAPI()

RASA_URL = "http://127.0.0.1:5005/webhooks/rest/webhook"


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    payload = {"sender": "demo_user", "message": req.message}

    try:
        response = requests.post(RASA_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data:
            return {"reply": "Nemám odpoveď."}

        parts = [item["text"] for item in data if "text" in item and item["text"]]
        return {"reply": "\n".join(parts) if parts else "Nemám textovú odpoveď."}
    except Exception as e:
        return {"reply": f"Chyba spojenia s chatbotom: {e}"}


@app.get("/", response_class=HTMLResponse)
def chat_ui():
    return """
    <!DOCTYPE html>
    <html lang="sk">
    <head>
        <meta charset="UTF-8">
        <title>E-commerce chatbot – ukážka diplomovej práce</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 40px auto; }
            #chat { border: 1px solid #ccc; padding: 16px; height: 400px; overflow-y: auto; margin-bottom: 12px; }
            .user { font-weight: bold; margin-top: 12px; }
            .bot { margin-top: 6px; white-space: pre-wrap; }
            input { width: 78%; padding: 10px; }
            button { width: 20%; padding: 10px; }
        </style>
    </head>
    <body>
        <h1>E-commerce chatbot – ukážka diplomovej práce</h1>
        <div id="chat"></div>
        <input id="msg" type="text" placeholder="Napíš správu..." />
        <button onclick="sendMessage()">Odoslať</button>

        <script>
            async function sendMessage() {
                const input = document.getElementById("msg");
                const message = input.value.trim();
                if (!message) return;

                const chat = document.getElementById("chat");
                chat.innerHTML += `<div class="user">Ty:</div><div>${message}</div>`;
                input.value = "";

                try {
                    const response = await fetch("/chat", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({ message })
                    });
                    const data = await response.json();
                    chat.innerHTML += `<div class="user">Chatbot:</div><div class="bot">${data.reply}</div>`;
                } catch (e) {
                    chat.innerHTML += `<div class="user">Chatbot:</div><div class="bot">Chyba spojenia.</div>`;
                }

                chat.scrollTop = chat.scrollHeight;
            }

            document.getElementById("msg").addEventListener("keydown", function(e) {
                if (e.key === "Enter") sendMessage();
            });
        </script>
    </body>
    </html>
    """