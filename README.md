# InstaCheck

## Introduction

InstaCheck is a Chrome extension that helps users **verify the authenticity of claims in Instagram Reels** in real time.
It uses **OpenAI Whisper** for transcription, **GPT-OSS** for claim extraction and reasoning, and integrates **web + vector database retrieval** for evidence-backed verification.
The result: a **fast, transparent, and privacy-first fact-checking experience** delivered directly in your browser.

---

## How it Works

1. **Input** – User pastes a reel URL or uploads an `.mp4`.
2. **Transcription** – Audio is extracted and transcribed using OpenAI Whisper.
3. **Claim Extraction** – GPT-OSS identifies factual claims from the transcript.
4. **Verification** – Each claim is cross-checked via GPT-OSS + trusted evidence (web search, scraping, vector DB).
5. **Final Verdict** – The system returns a verdict for each claim (Authentic ✅ / Misleading ❌) with linked evidence.
6. **Seamless Experience** – All results are shown directly in the Chrome extension, without interrupting reel-watching.

---

## Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/aniketraut16/instacheck.git
cd instacheck
```

### 2. Configure Settings

Edit the `core/config.py` file:

```python
from dotenv import load_dotenv
import os

load_dotenv()

class LLMSettings:
    provider: str = "ollama" # ollama or groq
    api_key: str = os.getenv("GROQ_API_KEY") if provider == "groq" else None

llm_settings = LLMSettings()
```

Set `provider` as **ollama** or **groq**:

* **If using Ollama:**

  * Install Ollama: [https://ollama.com/download](https://ollama.com/download)
  * Pull the GPT-OSS model:

    ```bash
    ollama pull gpt-oss:20b
    ```
  * Verify installation by running a test prompt in Ollama.

* **If using Groq:**

  * Generate an API key from [Groq Console](https://console.groq.com/).
  * Create a `.env` file in the project root and add:

    ```env
    GROQ_API_KEY="<your_key>"
    ```

### 3. Run with Docker

Make sure **Docker** is installed.

* First-time build:

  ```bash
  docker compose -f docker-compose.dev.yml up --build
  ```
* Subsequent runs:

  ```bash
  docker compose -f docker-compose.dev.yml up
  ```

⏳ This may take **5–10 minutes** on the first build. Once done, the server will be running.

### 4. Load Chrome Extension

* Open **Chrome → Extensions → Manage Extensions**.
* Enable **Developer Mode**.
* Click **Load unpacked** and select the `extension` folder from the repo.
* The extension will now be ready to use! 🎉

---

## How to Contribute

We welcome contributions! 🚀

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes and push:

   ```bash
   git push origin feature-name
   ```
4. Submit a pull request.

