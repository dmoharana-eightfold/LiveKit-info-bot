# Employee Directory Voice Agent

A voice AI assistant for employee directory lookups built with [LiveKit Agents](https://docs.livekit.io/agents) and a React/Next.js frontend.

## Features

- Voice-based employee directory search
- Fuzzy name matching with intelligent suggestions
- Real-time metrics streaming (LLM, STT, TTS)
- Text chat support alongside voice
- Data guardrails (no salary/confidential info exposed)

## Architecture

<img width="960" height="632" alt="Screenshot 1404-10-24 at 14 42 34" src="https://github.com/user-attachments/assets/2cdb898c-f62f-42a5-acda-138ed725db61" />


## Project Structure

```
agent-starter-python/
├── src/
│   ├── agent.py              # Main agent entry point
│   ├── app.py                # Flask API server
│   ├── mock_data.json        # Employee data
│   └── agent/
│       ├── assistant.py      # Voice assistant & tools
│       ├── custom_llm.py     # Groq LLM adapter
│       ├── employee_data.py  # Data loader
│       ├── fuzzy_search.py   # Name matching
│       └── metrics_handler.py # Metrics streaming
├── frontend/                 # Next.js frontend
└── .env                      # Environment variables
```

## Environment Setup

### 1. Clone & Install Dependencies

```bash

# Backend (Python)
uv sync

# Frontend (Node.js)
cd frontend
pnpm install
cd ..
```

### 2. Create Environment File

Create a `.env` file in the project root:

```env
# LiveKit Cloud credentials
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Groq API (for LLM)
GROQ_API_KEY=your_groq_api_key
```

**Get your credentials:**
- [LiveKit Cloud](https://cloud.livekit.io/) - Sign up and create a project
- [Groq](https://console.groq.com/) - Get a free API key

Alternatively, use LiveKit CLI to auto-configure:

```bash
lk cloud auth
lk app env -w -d .env
```

### 3. Download Required Models

```bash
uv run python src/agent.py download-files
```

## Running the Project

### Start Backend Services

**Terminal 1 - Flask API Server:**

```bash
source .venv/bin/activate
python src/app.py
```
Server runs at `http://localhost:5000`

**Terminal 2 - Voice Agent:**

```bash
uv run python src/agent.py dev
```

### Start Frontend

**Terminal 3 - Next.js:**

```bash
cd frontend
npm run dev
```
Open `http://localhost:3000` in your browser.

## Usage

1. Click **"Start Call"** to connect
2. Ask questions like:
   - "Who is Rohit?"
   - "Tell me Rohit's Salary"
   - "Tell me about Rohet" (fuzzy matching works!)
3. Use the **chat button** to type instead of speaking
4. View real-time **metrics** in the top-right panel

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/token` | GET | Generate LiveKit room token |



## Development Commands

```bash
# Run agent in console mode (no frontend needed)
uv run python src/agent.py console

# Run agent in dev mode (with hot reload)
uv run python src/agent.py dev

# Run agent in production mode
uv run python src/agent.py start

# Run tests
uv run pytest
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Voice Agent | LiveKit Agents SDK |
| LLM | Groq (Llama 3.3 70B) |
| STT | AssemblyAI |
| TTS | Cartesia |
| VAD | Silero |
| Backend API | Flask + Flask-RESTx |
| Frontend | Next.js + React |
| Styling | Tailwind CSS |
