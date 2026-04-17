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

#Spustenie projektu (terminal)

## Spustenie projektu (docker)

```bash
rasa train --config rasa/config.yml --domain rasa/domain.yml --data rasa/data
```

```bash
rasa run actions
```

```bash
rasa shell --endpoints rasa/endpoints.yml
```

### 1. Natrénovanie modelu

```bash
rasa train --config rasa/config.yml --domain rasa/domain.yml --data rasa/data
```

```bash
docker compose up --build
```

```bash
http://localhost:7860
```

Chatbot komunikuje cez REST API endpoint:

POST /webhooks/rest/webhook
