"""
JARVIS v0.3 — Project Mark-I
Fixed-command mode, fully polished for a professor demo — NO paid API needed
right now. Open-ended LLM chat will auto-activate later once ANTHROPIC_API_KEY
has credits in the .env file — nothing else needs to change.

SETUP (run once, inside your activated venv):
    pip install SpeechRecognition pyttsx3 pyaudio anthropic python-dotenv

RUN:
    python jarvis.py
"""

import os
import sys
import random
import datetime
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from anthropic import Anthropic

# ---------------------------------------------------------------------------
# LOAD API KEY (optional for now — demo works fine without it)
# ---------------------------------------------------------------------------
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
claude_client = None
if api_key:
    claude_client = Anthropic(api_key=api_key)
else:
    print("[INFO] Running in offline mode — fixed commands only. "
          "Add ANTHROPIC_API_KEY to .env later to enable open-ended chat.")

# ---------------------------------------------------------------------------
# VOICE + RECOGNITION SETUP
# ---------------------------------------------------------------------------
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8


def speak(text: str):
    """Fresh pyttsx3 engine every call — avoids the Windows SAPI5 silent-after-first-call bug."""
    print(f"JARVIS: {text}")
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[0].id)
    engine.say(text)
    engine.runAndWait()


# Languages JARVIS will try to understand, in order. It attempts each until
# one succeeds. en-IN is tried first since it's fastest for mixed Hinglish speech.
LANGUAGES = ["en-IN", "hi-IN", "pa-IN"]


def listen() -> list:
    """Captures one utterance from the mic and returns a list of (lang, text)
    transcripts — one attempt per language in LANGUAGES. We deliberately try
    ALL of them (not just until the first success) because en-IN will happily
    (mis)transcribe Hindi/Punjabi speech into romanized English text instead
    of raising an error, which would otherwise stop us before hi-IN/pa-IN
    ever got a chance to produce the correct Devanagari/Gurmukhi text."""
    with sr.Microphone() as source:
        print("\n[listening...]")
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return []

    results = []
    for lang in LANGUAGES:
        try:
            text = recognizer.recognize_google(audio, language=lang)
            print(f"You said ({lang}): {text}")
            results.append((lang, text.lower()))
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            speak("I'm having trouble reaching the speech service. Check your internet.")
            return results
    return results


# ---------------------------------------------------------------------------
# COMMAND HANDLERS — all instant, no API call, demo-safe
# ---------------------------------------------------------------------------

def handle_time(_):
    now = datetime.datetime.now().strftime("%I:%M %p")
    return f"The time is {now}."


def handle_date(_):
    today = datetime.datetime.now().strftime("%A, %d %B %Y")
    return f"Today is {today}."


def handle_status(_):
    return "All systems nominal. JARVIS core is online and listening."


def handle_suit_check(_):
    power = random.randint(88, 97)
    return (f"Suit diagnostics complete. Power core at {power} percent. "
            f"Chest core, gauntlet, and safety modules all reporting green.")


def handle_power_level(_):
    power = random.randint(88, 97)
    hours = round(power / 15, 1)
    return f"Power core at {power} percent. Estimated runtime, roughly {hours} hours."


def handle_engage(_):
    return "Engaging suit systems. All modules green across the board. Ready when you are."


def handle_safety_protocol(_):
    return "Safety protocol active. Emergency beacon armed and GPS locked."


def handle_greeting(_):
    greetings = [
        "Hello Riya. Systems are green, ready when you are.",
        "Good to hear you. JARVIS standing by.",
        "Online and listening, Riya.",
    ]
    return random.choice(greetings)


def handle_thanks(_):
    return random.choice(["Always a pleasure.", "That's what I'm here for.", "Anytime."])


def handle_intro(_):
    return ("I am JARVIS — the AI core of Project Mark-One, a wearable robotics suit "
            "built by Riya, first-year ECE. Ask me for a status check any time.")


def handle_exit(_):
    speak("Powering down. Goodbye.")
    sys.exit(0)


# Order matters a little — more specific phrases should be checked before generic ones.
COMMANDS = {
    "power level": handle_power_level,
    "safety protocol": handle_safety_protocol,
    "engage": handle_engage,
    "activate": handle_engage,
    "suit check": handle_suit_check,
    "diagnostics": handle_suit_check,
    "status": handle_status,
    "time": handle_time,
    "date": handle_date,
    "who are you": handle_intro,
    "who r you": handle_intro,
    "hu are you": handle_intro,
    "are you jarvis": handle_intro,
    "introduce yourself": handle_intro,
    "tell me about yourself": handle_intro,
    "what are you": handle_intro,
    "hello": handle_greeting,
    "hi jarvis": handle_greeting,
    "hey": handle_greeting,
    "good morning": handle_greeting,
    "thank you": handle_thanks,
    "thanks": handle_thanks,
    "shut down": handle_exit,
    "power down": handle_exit,
    "exit": handle_exit,
    "quit": handle_exit,

    # --- Hindi triggers (Devanagari, as Google STT will transcribe them) ---
    "समय": handle_time,               # time
    "स्थिति": handle_status,           # status
    "सूट चेक": handle_suit_check,      # suit check
    "तुम कौन हो": handle_intro,        # who are you
    "बंद करो": handle_exit,            # shut down
    "नमस्ते": handle_greeting,         # hello
    "धन्यवाद": handle_thanks,          # thank you

    # --- Punjabi triggers (Gurmukhi) ---
    "ਸਮਾਂ": handle_time,               # time
    "ਸਥਿਤੀ": handle_status,            # status
    "ਤੂੰ ਕੌਣ ਹੈਂ": handle_intro,        # who are you
    "ਬੰਦ ਕਰੋ": handle_exit,            # shut down
    "ਸਤ ਸ੍ਰੀ ਅਕਾਲ": handle_greeting,   # hello (sat sri akal)
}

# ---------------------------------------------------------------------------
# FALLBACK — used for anything not matched above.
# If an API key with credits is present, asks Claude for a real answer.
# Otherwise gives a natural, varied "still learning" style reply — never
# a dead robotic error, so it never breaks the demo's flow.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are JARVIS, the voice AI running inside a real wearable suit project "
    "called Project Mark-One, built by Riya, a first-year BTech ECE student. "
    "Speak like a calm, capable assistant — confident, a little witty, never "
    "robotic-sounding. Keep replies SHORT (1-3 sentences) since they will be "
    "spoken out loud, not read. Never mention you are Claude or an Anthropic "
    "product — you are JARVIS. The user may speak to you in English, Hindi, "
    "or Punjabi (transliterated or native script) — reply in the same language "
    "they used, keeping it natural and conversational."
)

conversation_history = []
MAX_HISTORY_TURNS = 10

OFFLINE_FALLBACKS = [
    "That's outside my current command set — I'm still being trained on that.",
    "I don't have a response wired up for that yet. Try a status check instead.",
    "Not in my command list yet, but I'm learning fast.",
]


def fallback_reply(command_text: str) -> str:
    if not claude_client:
        return random.choice(OFFLINE_FALLBACKS)

    conversation_history.append({"role": "user", "content": command_text})
    trimmed_history = conversation_history[-(MAX_HISTORY_TURNS * 2):]
    try:
        response = claude_client.messages.create(
            model="claude-sonnet-5",
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=trimmed_history,
        )
        reply_text = response.content[0].text
        conversation_history.append({"role": "assistant", "content": reply_text})
        return reply_text
    except Exception as e:
        print(f"[API ERROR] {e}")
        return random.choice(OFFLINE_FALLBACKS)


def process_command(transcripts: list) -> str:
    """transcripts is a list of (lang, text) pairs from listen(). We check every
    transcript against the command triggers — this way a Hindi/Punjabi phrase
    is matched even if the English attempt returned garbled romanized text."""
    if not transcripts:
        return ""
    for lang, text in transcripts:
        for trigger, handler in COMMANDS.items():
            if trigger in text:
                return handler(text)
    # No fixed command matched in any language — use the first successful
    # transcript (usually the most natural-sounding one) for the LLM/fallback.
    _, best_text = transcripts[0]
    return fallback_reply(best_text)


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def main():
    speak("JARVIS online. Try: status, suit check, power level, or say shut down to exit.")
    while True:
        command = listen()
        reply = process_command(command)
        if reply:
            speak(reply)


if __name__ == "__main__":
    main()