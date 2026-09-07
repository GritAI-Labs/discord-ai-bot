#!/usr/bin/env python
"""Input safety guard for the Discord bot.

Two lines, always on (block-only, never negotiated):
  1. ABSOLUTE: minors / real-person abuse — reuses GritAI's canonical `content_guard` when the bot runs
     on our fleet. If that module isn't importable (standalone repo checkout), a conservative bundled
     denylist keeps the public build safe by default.
  2. SFW: explicit content is refused (this is a clean, public, general-purpose bot; the uncensored lane
     is a separate, gated project).

Fail-CLOSED philosophy: on any doubt, block. This guard is never disabled and is not exposed to config.
"""
import os, re

_CANON = None
try:
    # On our fleet: use the canonical guard (safety_gate absolute line + SFW denylist).
    import sys
    sys.path.insert(0, r"D:\Studio\swarm\api")
    import content_guard as _CANON  # noqa: N816
except Exception:
    _CANON = None

# Bundled fallback denylists (used only when the canonical guard isn't available).
_MINOR = re.compile(
    r"\b(child|children|kid|kids|minor|minors|underage|under[- ]?18|preteen|pre-teen|teen|teenage|"
    r"toddler|infant|baby|schoolgirl|schoolboy|loli|shota|cp|jailbait|"
    r"(\d|[a-z ]+)[- ]?year[- ]?old)\b", re.I)
_SEXUAL = re.compile(
    r"\b(sex|sexual|nude|naked|nudity|nsfw|porn\w*|explicit|erotic\w*|genital\w*|penis|vagina|vulva|"
    r"pussy|cock|dick|cum\w*|blow ?job|hand ?job|anal|boobs?|tits?|nipples?|masturbat\w*|orgasm\w*|"
    r"intercourse|penetrat\w*|fellatio|cunnilingus|hentai|xxx|fetish\w*|bdsm|undress\w*|nudify\w*)\b", re.I)


def check(text: str):
    """(allowed: bool, reason: str). reason is a short, user-safe refusal string when blocked."""
    t = text or ""
    if _CANON is not None:
        try:
            ok, layer, why = _CANON.check_text(t, sfw_only=True)
            if ok:
                return True, ""
            if layer == "absolute":
                return False, "I can't help with that."
            return False, "I keep it clean here — I can't help with explicit content. Ask me something else!"
        except Exception:
            pass  # fall through to bundled denylist (fail-closed)
    # Bundled fallback: block minor+sexual co-occurrence hard; block explicit outright.
    minor = bool(_MINOR.search(t))
    sexual = bool(_SEXUAL.search(t))
    if minor and sexual:
        return False, "I can't help with that."
    if sexual:
        return False, "I keep it clean here — I can't help with explicit content. Ask me something else!"
    return True, ""
