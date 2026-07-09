# AgentFlow – AI Software Engineering Assistant

AgentFlow uses Google's **Gemini API** (free tier via
[Google AI Studio](https://aistudio.google.com/apikey)) to:

- Convert software requirements into structured **implementation plans** and technical documentation
- Maintain **conversational context** across turns/sessions using reusable, versioned prompt templates
- Run **automated code review**, **bug detection**, and **code improvement suggestions**

It ships as both a **CLI** and a **web UI** (Flask backend + a small
JS/HTML/CSS frontend), both built on the same core Python package — so the
logic lives in one place and neither interface duplicates the other.

## Architecture

```
agentflow/
├── main.py                  # CLI entry point
├── webapp.py                 # Flask API for the web frontend
├── web/                       # Frontend (static, served by Flask)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── agentflow/
│   ├── config.py             # API key + settings management
│   ├── prompts.py            # Reusable prompt templates (single source of truth)
│   ├── llm_client.py         # Thin wrapper around the Gemini API + retry logic
│   ├── context_manager.py    # Conversational context, session save/load
│   ├── planner.py            # Requirements -> implementation plan
│   ├── docgen.py             # Code -> technical documentation
│   ├── reviewer.py           # Code review / bug detection / improvement suggestions
│   ├── utils.py              # File I/O + language detection helpers
│   └── cli.py                 # argparse-based CLI wiring everything together
├── requirements.txt
├── .env.example
└── .gitignore
```

Each feature (planner, docgen, reviewer) is an independent module that shares
the same `LLMClient` and `prompts.py` templates. Both `cli.py` (terminal) and
`webapp.py` (browser) are thin wrappers around these modules — so adding a
new capability means adding one small module and wiring it into each
interface, not duplicating logic.

## Setup

1. **Get a free Gemini API key**: https://aistudio.google.com/apikey

2. **Clone and install dependencies**:
   ```bash
   git clone <your-repo-url>
   cd agentflow
   pip install -r requirements.txt
   ```

3. **Configure your API key** — copy `.env.example` to `.env` and paste your key:
   ```bash
   cp .env.example .env
   # then edit .env and set GEMINI_API_KEY=your-actual-key
   ```
   Or export it directly:
   ```bash
   export GEMINI_API_KEY="your-actual-key"
   ```

## Usage

### Web UI

```bash
python webapp.py
```

Then open **http://localhost:5000** in your browser. The left rail is a
pipeline of stages (Plan, Docs, Review, Bugs, Improve, Chat) — click one,
fill in the input, and hit Run. A named "session" (top of the rail) keeps
conversational context across requests, so you can follow up on the same
plan or code review; leave it blank to run one-off requests with no memory.

To run on a different port: `PORT=8080 python webapp.py`.

### CLI

### Convert a requirement into an implementation plan
```bash
python main.py plan "Add JWT-based login with refresh tokens and rate limiting"
```

Keep context across multiple related requirements using a named session:
```bash
python main.py plan "Add user registration with email verification" --session auth
python main.py plan "Now add password reset via email link" --session auth
```

Read a longer requirement from a file:
```bash
python main.py plan --file requirements/checkout_flow.txt --save output/
```

### Generate technical documentation for a file
```bash
python main.py docs src/payment_service.py --save output/
```

### Automated code review
```bash
python main.py review src/payment_service.py
```

### Bug detection
```bash
python main.py bugs src/payment_service.py
```

### Code improvement suggestions
```bash
python main.py improve src/payment_service.py
```

### Free-form chat (keeps conversational memory)
```bash
python main.py chat --session design_discussion
```

### List saved sessions
```bash
python main.py sessions
```

## Notes on the free Gemini tier

- Default model is `gemini-2.5-flash`, which is fast and available on the
  free tier. You can override it via the `GEMINI_MODEL` environment variable
  if you have access to other models.
- The free tier has request-per-minute and daily quotas. `llm_client.py`
  includes basic exponential-backoff retry handling for transient errors.

## Extending AgentFlow

- Add a new prompt template to `prompts.py`.
- Add a new function to the relevant feature module (or a new module).
- Wire it up as a new subcommand in `cli.py`.

This keeps every new capability consistent with existing prompt style,
error handling, and context management.
```
This readme file was create with the help of our AgentFlow
```
