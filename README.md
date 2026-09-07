# GritAI Discord AI Bot 🤖

A real AI assistant that **lives in a Discord server**. @mention it or DM it to chat, or use the `/ask`
slash command. It remembers the last few messages per channel, and — by default — runs on **our own
local GPU fleet** (no cloud LLM key required).

> Project **#11** of the *"30 AI Projects in 15 Days"* build-in-public challenge.
> Focus: **integrations + a long-running service** (vs. a request/response web app).

## What it does
- **Chat by @mention or DM** — natural, concise replies with short per-channel memory. Responds whether
  you mention the bot *user* or the integration *role* Discord auto-creates (a common autocomplete trap).
- **Slash commands:** `/ask <question>`, `/reset` (clear this channel's memory), `/help`.
- **Typing indicator** while it thinks; single-message-safe (trims to Discord's 2000-char limit).
- **Safety-gated input** — an always-on, block-only guard (minors + explicit content) before any model call.
- **Rate-limited** per user; ignores other bots (loop-safe).

## How it works
- `bot.py` — the Discord client (discord.py): events, slash commands, rate limiting.
- `brain.py` — reply generation: safety gate → conversation memory → LLM backend → reply.
- `guard.py` — the input safety line (reuses GritAI's canonical guard on our fleet; bundled denylist as a
  safe fallback in a standalone checkout).

**Backends** (`BOT_LLM_BACKEND`):
- `ollama` *(default)* — a local model on our GPU fleet. Free, private, on-brand for a local AI studio.
- `claude` — Anthropic API (set `ANTHROPIC_API_KEY`). Higher quality, paid.

## Run it
```bash
pip install -r requirements.txt
cp .env.example .env            # fill in DISCORD_BOT_TOKEN (+ backend of choice)
python bot.py
```

### Create the Discord app (one-time)
1. https://discord.com/developers/applications → **New Application**.
2. **Bot** → *Reset Token* → copy into `DISCORD_BOT_TOKEN`.
3. **Bot** → enable **Message Content Intent** (privileged) so it can read mentions.
4. **OAuth2 → URL Generator** → scopes `bot` + `applications.commands`; bot permissions: *Send Messages,
   Read Message History, Use Slash Commands*. Open the generated URL to invite it to your server.

## Deploy (always-on)
It's a long-running process — run it under any process supervisor (systemd, pm2, or our fleet's
supervisor pattern) so it stays online. Default backend talks to our local Ollama, so no external LLM
cost. Never commit `.env`; the token and any API key are read from the environment only.

---
Built by **Robert Lucyk** · [GritAI Solutions](https://gritai.solutions) · part of the 30-in-15 challenge.
