"""
JARVIS v0.1 — Project Mark-I
Week 1 core: listens on mic, understands basic commands, replies by voice.
Built so Week 2 can plug in an LLM for open-ended replies without rewriting this.

SETUP (run once in terminal):
    pip install SpeechRecognition pyttsx3 pyaudio

    Windows: pyaudio usually installs fine via pip.
    Mac:     brew install portaudio   (then pip install pyaudio)
    Linux:   sudo apt install python3-pyaudio portaudio19-dev

RUN:
    python jarvis.py

NOTE: Speech recognition here uses Google's free Web Speech API through the
`speech_recognition` library — needs internet, no API key required. This is
fine for a demo. If you want fully offline STT later, swap in Vosk (I can
help with that when you need it — not needed for the pitch demo).
"""

import speech_recognition as sr
import pyttsx3
import datetime
import sys

# ---------------------------------------------------------------------------
# VOICE ENGINE SETUP
# ---------------------------------------------------------------------------


recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True


def speak(text: str):
    """
    JARVIS speaks a line and also prints it, so the demo is visible on screen.

    NOTE: pyttsx3's SAPI5 driver on Windows has a known bug where the engine
    goes silent after the first utterance if you reuse one global engine
    object across multiple say()/runAndWait() calls. Creating a fresh engine
    each time avoids it completely and costs almost no extra time.
    """
    print(f"JARVIS: {text}")
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[0].id)
    engine.say(text)
    engine.runAndWait()


def listen() -> str:
    """Captures one utterance from the mic and returns lowercase transcribed text."""
    with sr.Microphone() as source:
        print("\n[listening...]")
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("I'm having trouble reaching the speech service. Check your internet.")
        return ""


# ---------------------------------------------------------------------------
# COMMAND HANDLERS
# Each function takes the raw command text and returns a reply string.
# Add new commands here — Week 2 LLM fallback slots in at the bottom.
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
    # Placeholder for now — Week 2/Phase 2 will wire this to real sensor data
    # coming from the Chest Core over serial/WiFi.
    return "Suit diagnostics: power core standing by. No hardware modules connected yet."


def handle_intro(_):
    return "I am JARVIS, online and ready. Built by Riya as part of Project Mark-One."


def handle_exit(_):
    speak("Shutting down. Goodbye.")
    sys.exit(0)


# command text (substring match) -> handler function
COMMANDS = {
    "time": handle_time,
    "date": handle_date,
    "status": handle_status,
    "suit check": handle_suit_check,
    "who are you": handle_intro,
    "introduce yourself": handle_intro,
    "shut down": handle_exit,
    "exit": handle_exit,
    "quit": handle_exit,
}


def fallback_reply(command_text: str) -> str:
    """
    Week 1: simple canned fallback for anything not matched above.
    Week 2: replace this function's body with a call to an LLM API
    (Claude/GPT) so JARVIS can answer open-ended questions too.
    Keep the function signature the same — nothing else needs to change.
    """
    return "I heard you, but that command isn't wired up yet."


def process_command(command_text: str) -> str:
    if not command_text:
        return ""
    for trigger, handler in COMMANDS.items():
        if trigger in command_text:
            return handler(command_text)
    return fallback_reply(command_text)


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def main():
    speak("JARVIS online. Say 'who are you' to begin, or 'shut down' to exit.")
    while True:
        command = listen()
        reply = process_command(command)
        if reply:
            speak(reply)


if __name__ == "__main__":
    main()