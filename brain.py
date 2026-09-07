#!/usr/bin/env python
"""The bot's brain: safety-gated, memory-aware reply generation.

Backends (set LLM_BACKEND):
  - "ollama" (default) — a local model on our own GPU fleet. Free, private, no cloud key. On-brand for a
    "local AI production studio". Point OLLAMA_URL at your host.
  - "claude"           — Anthropic API (set ANTHROPIC_API_KEY). Higher quality, paid.

Every user turn is passed through guard.check() first (block-only minors/SFW line). Errors log the
exception TYPE only — never the message/repr — so an API error can never echo a key into logs.
"""
import os, json, collections, urllib.request

import guard

BACKEND      = os.environ.get("BOT_LLM_BACKEND", "ollama").lower()
# Namespaced (BOT_*) so the bot never inherits unrelated studio-wide OLLAMA_MODEL/URL exports.
OLLAMA_URL   = os.environ.get("BOT_OLLAMA_URL", "http://192.168.12.223:11434")   # Spark by default
OLLAMA_MODEL = os.environ.get("BOT_OLLAMA_MODEL", "qwen2.5:7b")
ANTHROPIC_KEY   = (os.environ.get("ANTHROPIC_API_KEY") or "").strip() or None
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")
BOT_NAME     = os.environ.get("BOT_NAME", "GritAI Bot")
MAX_TURNS    = int(os.environ.get("MAX_TURNS", "8"))     # remembered exchanges per conversation
MAX_INPUT    = int(os.environ.get("MAX_INPUT", "1500"))  # chars accepted from a user turn

SYSTEM = (
    f"You are {BOT_NAME}, a helpful, friendly AI assistant living in a Discord server, built by GritAI "
    "Solutions. Be concise and useful — Discord messages are short. Use plain language, a little warmth, "
    "and Discord markdown when it helps (bold, `code`, lists). If you don't know, say so. Keep it clean "
    "and professional; you're a general-purpose assistant for a public server."
)

# conversation_key -> deque[(role, content)]
_MEM = collections.defaultdict(lambda: collections.deque(maxlen=MAX_TURNS * 2))


def reset(conversation_key: str):
    _MEM.pop(conversation_key, None)


def _ollama(messages):
    body = json.dumps({"model": OLLAMA_MODEL, "messages": messages, "stream": False,
                       "options": {"temperature": 0.6, "num_predict": 500}}).encode()
    req = urllib.request.Request(OLLAMA_URL + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())["message"]["content"].strip()


def _claude(messages):
    # messages: list of {role, content} with roles user/assistant; system passed separately.
    sys_msg = SYSTEM
    convo = [m for m in messages if m["role"] != "system"]
    body = json.dumps({"model": ANTHROPIC_MODEL, "max_tokens": 500, "system": sys_msg,
                       "messages": convo}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
        "x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    data = json.loads(urllib.request.urlopen(req, timeout=60).read())
    return "".join(b.get("text", "") for b in data.get("content", [])).strip()


def generate(conversation_key: str, user_text: str) -> str:
    """Safety-gate -> build context -> call backend -> remember -> return reply text."""
    text = (user_text or "").strip()[:MAX_INPUT]
    if not text:
        return "Ask me anything!"

    ok, reason = guard.check(text)
    if not ok:
        return reason

    mem = _MEM[conversation_key]
    messages = [{"role": "system", "content": SYSTEM}]
    messages += [{"role": r, "content": c} for (r, c) in mem]
    messages.append({"role": "user", "content": text})

    try:
        reply = _claude(messages) if BACKEND == "claude" else _ollama(messages)
    except Exception as e:
        print(f"generate error: backend={BACKEND} {type(e).__name__}")   # TYPE only — never repr/secrets
        return "⚠️ My brain hiccuped — try again in a moment."

    if not reply:
        return "I didn't quite catch that — can you rephrase?"

    mem.append(("user", text))
    mem.append(("assistant", reply))
    return reply[:1900]   # Discord single-message limit is 2000 chars


if __name__ == "__main__":
    # Local smoke test (no Discord needed): prove the brain + backend + guard path work.
    k = "cli"
    for q in ["hey, what can you do?", "give me 3 tips for a faster morning routine", "thanks!"]:
        print(f"\nUSER: {q}\nBOT : {generate(k, q)}")
