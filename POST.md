# 30-in-15 · #11 — Discord AI Bot (build-in-public post)

**Attach:** a short screen-recording / screenshot of the bot replying in a channel + a /ask.
**Demo:** (public GritAI Discord invite link) · **Repo:** https://github.com/GritAI-Labs/discord-ai-bot

---

🤖 Project #11 of my "30 AI Projects in 15 Days" challenge is live: a Discord AI bot that actually lives in a server.

The first ten were request-in, answer-out web apps. This one is different on purpose — it's a long-running service. @mention it or DM it and it replies with a little conversational memory per channel; there's a /ask slash command and a /reset to clear its memory. The interesting part isn't the chat, it's everything around keeping a bot online and well-behaved.

Two things I cared about. First, it runs on our own local GPU fleet by default — no cloud LLM key, no per-message API bill — which is the whole point of a local AI studio. You can flip it to Claude with one env var if you want, but out of the box it's free and private. Second, every message hits an always-on safety gate before it ever reaches the model: a block-only line for the stuff that's never OK, plus a keep-it-clean filter, because a public bot is a different risk surface than a private demo.

Under the hood it's three small pieces: the Discord client (events, slash commands, per-user rate limiting, and it ignores other bots so it can't get stuck in a loop), a "brain" that gates input then adds short memory then calls the backend, and a guard module that reuses our canonical safety line. Build → run as a real service → keep it safe. That's the job.

▶ (invite link)
⭐ https://github.com/GritAI-Labs/discord-ai-bot

---

*(Post to LinkedIn + X. After posting, append the LinkedIn + X permalinks at the bottom, like #5–10.)*
