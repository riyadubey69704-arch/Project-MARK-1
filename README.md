# Project Mark-One 🦾

A real, functional, non-lethal wearable robotics + AI suit — built from scratch by a first-year BTech ECE student at Thapar Institute of Engineering & Technology, Patiala.

This is **not** a costume project. Every component here is real engineering: actual sensors, actual actuators, actual AI — built incrementally, with an honest timeline, and zero weapons or lethal systems by design.

---

## 🧠 What's working right now

**JARVIS** — the AI core of the suit — is live and functional:
- Voice input via microphone (speech-to-text)
- Multilingual recognition (English, Hindi, Punjabi)
- Fixed suit-command handling (status checks, power level, diagnostics, safety protocol)
- Open-ended conversation powered by Claude (Anthropic API)
- Natural voice replies (text-to-speech)

## 🏗️ The full vision

Project Mark-One is architected in three systems:

| System | Purpose |
|---|---|
| **JARVIS** | The AI brain — voice interface, decision-making, sensor fusion |
| **The Suit** | Wearable hardware — helmet, chest core, gauntlets, exo-limbs, boots |
| **The HUD** | Helmet-based vision and heads-up display |

Each body module runs on its own ESP32, communicating wirelessly with a central Raspberry Pi running JARVIS.

### Explicitly excluded
No weapons, no lethal systems, anywhere in this design. "Defense" features are limited to non-lethal safety and deterrence: a personal alarm siren, a disorientation strobe, GPS/GSM emergency alerts, gas/smoke detection, and passive impact armor.

## 🗺️ Roadmap

| Phase | What | Timeline |
|---|---|---|
| 1 | JARVIS AI Brain (software only) | Month 1 |
| 2 | Chest Core + Helmet basics | Month 2-3 |
| 3 | Gauntlets + Safety System | Month 3-4 |
| — | **Milestone: Smart Suit Demo Ready** | End of Month 4 |
| 4 | Exo-Limbs (requires lab/fabrication access) | Month 5-10 |
| 5 | Boots + full integration + polish | Month 10-14 |

## 🛠️ Tech stack

- **Python** — JARVIS core logic
- **SpeechRecognition** — voice input (Google Web Speech API)
- **pyttsx3** — offline text-to-speech
- **Anthropic Claude API** — open-ended conversation and reasoning
- **Three.js** — interactive 3D suit configurator (design/planning tool)

## 🚀 Running JARVIS locally

```bash
pip install SpeechRecognition pyttsx3 pyaudio anthropic python-dotenv

Create a .env file in the project root:
code
ANTHROPIC_API_KEY=your-key-here

Then run:
Bash
python jarvis.py

Say things like "status", "suit check", "power level", "engage", or ask it anything open-ended.
👤 Built by
Riya, BTech ECE, Thapar Institute of Engineering & Technology (2026 batch).
This project is under active development. Contributions, suggestions, and mentorship are welcome.



