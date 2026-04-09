import requests
import gradio as gr

RASA_URL = "http://rasa:5005/webhooks/rest/webhook"

def chat_fn(message, history):
    payload = {"sender": "demo_user", "message": message}
    try:
        response = requests.post(RASA_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data:
            return "Nemám odpoveď."

        parts = []
        for item in data:
            if "text" in item and item["text"]:
                parts.append(item["text"])

        return "\n".join(parts) if parts else "Nemám textovú odpoveď."
    except Exception as e:
        return f"Chyba spojenia s chatbotom: {e}"

demo = gr.ChatInterface(
    fn=chat_fn,
    title="E-commerce chatbot – ukážka diplomovej práce",
    description="Vyhľadávanie produktov, sklad, objednávky a košík."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)