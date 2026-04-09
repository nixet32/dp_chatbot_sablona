**Návrh a implementácia šablón pre Rasa zameraných na e-commerce aplikácie**

Tento projekt predstavuje návrh a implementáciu univerzálnej šablóny pre e-commerce chatboty vo frameworku Rasa.
.
├── rasa/                    # Rasa projekt (NLU, rules, domain, config)

├── actions/                 # custom actions

├── api_server.py            # backend API server

├── app.py                   # Gradio web rozhranie

├── docker-compose.yml       # kontajnerizácia projektu

├── generic_api_config.json  # mapovanie externého API

├── README.md

##  Demo
https://huggingface.co/spaces/Nxt2/template-rasa-ecommerce

Používateľ si môže chatbot vyskúšať bez nutnosti lokálnej inštalácie.

## Použité technológie

- Rasa (NLU + Core)
- Python (Action Server)
- FastAPI (backend API)
- Docker & Docker Compose
- Gradio (webové rozhranie)

##  Spustenie projektu (lokálne)

### 1. Natrénovanie modelu

```bash
rasa train --config rasa/config.yml --domain rasa/domain.yml --data rasa/data
```

### 2. Spustenie cez Docker

```bash
docker compose up
```

### 3. Otvorenie web rozhrania

Po spustení je demo dostupné na adrese:
```link
http://localhost:7860
```
Chatbot komunikuje cez REST API endpoint:

POST /webhooks/rest/webhook

