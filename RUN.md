# Run the Project

## Requirements

- Python 3.14 or compatible Python 3.x
- Internet access for the product API and Gemini API
- No virtual environment is required.

## Install

Install the project dependencies into your current Python environment:

```bash
pip install streamlit requests google-genai
```

## Configure

In PowerShell, set the Gemini API key for the current terminal session:

```powershell
$env:GEMINI_API_KEY = "your-api-key"
```

Do not put the key in `app.py` or commit it to GitHub. You can also enter the key in the app's password field.

## Start

Run the app from the project folder:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```
