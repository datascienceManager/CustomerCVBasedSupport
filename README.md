# 🎬 OTT Customer Support Assistant

An AI-powered bilingual (English & Arabic) customer support system for OTT streaming platforms. Supports both text chat and voice interaction, with conversation storage in SQLite and Google Sheets.

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 💬 Chat Support | GPT-4o powered text chat |
| 🎙️ Voice Support | Whisper transcription + gTTS voice reply |
| 🌐 Bilingual | English & Arabic (auto-detect) |
| 🗄️ SQLite DB | Local conversation storage |
| 📊 Google Sheets | Real-time sync to spreadsheet |
| 📈 Dashboard | Analytics, export CSV, download DB |

---

## 🏗️ Project Structure

```
ott-support/
├── app.py                  # Main Streamlit app
├── requirements.txt
├── .env.example            # Environment variables template
├── .gitignore
├── README.md
├── credentials.json        # ← Google service account (DO NOT COMMIT)
├── data/
│   └── conversations.db    # ← SQLite DB (auto-created)
├── pages/
│   ├── chat_page.py        # Chat UI
│   ├── voice_page.py       # Voice UI
│   ├── dashboard_page.py   # Admin dashboard
│   └── about_page.py       # About page
└── utils/
    ├── ai_engine.py        # OpenAI GPT-4 + Whisper + gTTS
    ├── database.py         # SQLite operations
    └── sheets.py           # Google Sheets integration
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ott-support.git
cd ott-support
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in:
```
OPENAI_API_KEY=sk-...
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_SERVICE_ACCOUNT_JSON=credentials.json
```

---

## 🔑 API Keys Setup

### OpenAI API Key
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new key
3. Add to `.env` as `OPENAI_API_KEY`

---

## 📊 Google Sheets Setup

### Step 1: Create a Google Cloud Project
1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g., `ott-support`)
3. Enable these APIs:
   - **Google Sheets API**
   - **Google Drive API**

### Step 2: Create a Service Account
1. Go to **IAM & Admin → Service Accounts**
2. Click **Create Service Account**
3. Name it `ott-support-bot`
4. Click **Done**
5. Click on the service account → **Keys** → **Add Key** → **JSON**
6. Download and rename the file to `credentials.json`
7. Place it in the project root (it's in `.gitignore` — never commit it!)

### Step 3: Create a Google Sheet
1. Go to [https://sheets.google.com](https://sheets.google.com)
2. Create a new spreadsheet named `OTT Support Conversations`
3. Copy the **Sheet ID** from the URL:
   - URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`
   - Copy the `YOUR_SHEET_ID` part
4. Add it to `.env` as `GOOGLE_SHEET_ID`

### Step 4: Share the Sheet with Service Account
1. Open your Google Sheet
2. Click **Share**
3. Paste the service account email (found in `credentials.json` as `client_email`)
4. Give it **Editor** access

---

## ▶️ Run the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🎙️ Voice Support Usage

Since browsers block direct microphone access in Streamlit, the voice feature uses file upload:

1. **Record audio** on your phone or using any recorder app
2. Save as WAV, MP3, or M4A
3. **Upload** the file in the Voice Support tab
4. Click **Process Audio**
5. The app will:
   - Transcribe your speech (Whisper)
   - Generate AI response (GPT-4o)
   - Play the response as audio (gTTS)

---

## 📁 Database Schema

### `sessions` table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment PK |
| session_id | TEXT | Unique session identifier |
| language | TEXT | 'en' or 'ar' |
| mode | TEXT | 'chat' or 'voice' |
| created_at | TEXT | Timestamp |

### `messages` table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment PK |
| session_id | TEXT | Foreign key to sessions |
| role | TEXT | 'user' or 'assistant' |
| content | TEXT | Message text |
| language | TEXT | 'en' or 'ar' |
| mode | TEXT | 'chat' or 'voice' |
| timestamp | TEXT | Timestamp |

### `feedback` table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment PK |
| session_id | TEXT | Foreign key |
| rating | INTEGER | 1-5 stars |
| comment | TEXT | Optional comment |
| timestamp | TEXT | Timestamp |

---

## 🐙 GitHub Setup

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: OTT Support Assistant"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ott-support.git
git branch -M main
git push -u origin main
```

> ⚠️ **Never commit** `.env` or `credentials.json` — they're in `.gitignore`

---

## 🌐 Deployment (Optional)

### Streamlit Cloud
1. Push to GitHub
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Add secrets in the Streamlit dashboard (same as `.env` values)
5. Upload `credentials.json` content as a secret

---

## 🛠️ VS Code Tips

1. Install the **Python** extension
2. Install **Pylance** for IntelliSense
3. Set interpreter to your venv: `Ctrl+Shift+P` → `Python: Select Interpreter`
4. Run directly: open terminal and run `streamlit run app.py`

---

## 📄 License
MIT License — free to use and modify.
