# Domnigent 🌐  
AI-powered domain name generator + availability checker (Hugging Face + RDAP) built with Streamlit.

Domnigent takes a user prompt (business idea / vibe / keywords), generates brandable domain name ideas using a Hugging Face LLM, then checks which ones are available using RDAP lookups.

---

## 1. Features
- **Prompt → domain ideas** using Hugging Face (via LangChain)
- **Clean + validate** model output (dedupe, regex validation)
- **Availability checking** using RDAP (redirect-aware + rate-limit safe)
- **Streamlit UI** for quick usage

---

## 2. Tech Stack
- Python
- Streamlit
- LangChain (`langchain_huggingface`)
- Hugging Face Inference
- RDAP (via `rdap.org` bootstrap + registry RDAP)
- `requests`, `python-dotenv`

---

## 3. Project Structure
- `app.py` — Streamlit UI
- `domain_agent.py` — generation + cleaning + RDAP availability checker
- `test_generate.py` — CLI testing script
- `requirements.txt` — dependencies

---

## 4. Setup

### 1) Clone the repo
```bash
git clone https://github.com/KoushikRama/Domnigent.git
cd Domnigent
```

### 2) Activate the Environment
```bash
.venv\Scripts\Activate.ps1
```

### 3) Install the requirements
```bash
pip install -r requirements.txt
```

### 4) Add your Hugging Face API key in .env
```env
HUGGINGFACEHUB_API_TOKEN=hf_your_token_here
HF_CHAT_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

### 5) Run the App
```bash
streamlit run app.y
```

---

## 6.How Availability Checker works
- The app queries https://rdap.org/domain/<domain> as a bootstrap service
- If redirected (302), it follows the Location header to the authoritative registry
- Registry responses are interpreted as:
    200 → domain exists (taken)
    404 → domain not found (likely available)
- Rate limits (429) are handled using backoff and retry
- Uncertain responses are treated as unavailable

---
## 7) Link for a quick demo
(https://eyyt8yzp5pp4wfj9tuesqq.streamlit.app/)