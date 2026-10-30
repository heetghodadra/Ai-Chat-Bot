# AI Product Chatbot

A professional Streamlit chatbot that uses Gemini to answer questions only from the live product catalog provided by `https://dummyjson.com/products`.

## Features

- Gemini-powered chat responses
- Product data loaded directly from the API
- No local keyword matching or product scoring logic for responses
- Polished UI with a dark editorial layout

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your Gemini API key as an environment variable. In PowerShell:

```powershell
$env:GEMINI_API_KEY = "your-api-key"
```

Alternatively, create `.streamlit/secrets.toml` with:

```toml
GEMINI_API_KEY = "your-api-key"
```

For Streamlit Community Cloud, add the same setting under **App settings → Secrets**. Do not commit API keys to this repository.

3. Run the app:

```bash
streamlit run app.py
```

## Notes

- The default model name is `gemini-3.1-flash-lite-preview`.
- If your Google account does not yet have access to that exact model name, change it in the sidebar to a supported Gemini model.
- The app passes the product catalog to the model and instructs it to answer strictly from the API data.
