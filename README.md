## Štruktúra porjektu

├── rasa/                    # Rasa projekt (NLU, rules, domain, config)

├── actions/                 # custom actions

├── api_server.py            # backend API server

├── app.py                   # Gradio web rozhranie

├── docker-compose.yml       # kontajnerizácia projektu

├── generic_api_config.json  # mapovanie externého API
├── README.md

## Demo

https://huggingface.co/spaces/Nxt2/template-rasa-ecommerce

Používateľ si môže chatbot vyskúšať bez nutnosti lokálnej inštalácie.

##Spustenie projektu (terminal)

### 1. Natrénovanie modelu
```bash
rasa train --config rasa/config.yml --domain rasa/domain.yml --data rasa/data
```
### 2. Spustenie akcií
```bash
rasa run actions
```

### 3. Spustenie v termináli
```bash
rasa shell --endpoints rasa/endpoints.yml
```

## Spustenie projektu (docker)


### 1. Natrénovanie modelu
```bash
rasa train --config rasa/config.yml --domain rasa/domain.yml --data rasa/data
```

### 2.Zostavenie imagu a spustenie kontajneru
```bash
docker compose up --build
```

### 3. webové rozhranie
```bash
http://localhost:7860
```

Chatbot komunikuje cez REST API endpoint:

POST /webhooks/rest/webhook
