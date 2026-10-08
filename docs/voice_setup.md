# 🎙️ Voice & Wake Word Setup Guide

This guide walks you through setting up microphone capture, the "Hey Megan" wake word engine, and local speech-to-text with OpenAI Whisper.

---

## ⚙️ Components

1. **Audio Capture**: Uses `sounddevice` or `pyaudio` to stream 16kHz mono audio.
2. **Wake Word Detection**: Powered by `openWakeWord` with lightweight ONNX models running continuously in the background.
3. **Speech-to-Text (STT)**: Powered by local `whisper` models (`medium` or `large-v3`).

---

## 🎧 Setup Steps

### 1. Check Audio Input Devices
Run the following Python one-liner to list your active microphones:
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```
Note the device index of your microphone and set `microphone_index` in `configs/ines_settings.yaml` (or leave as `null` for system default).

### 2. Prepare Wake Word Model
Run the wake word setup script:
```bash
python scripts/setup_wake_word.py
```
This downloads or verifies the openWakeWord ONNX model for "Hey Megan".

### 3. Verify Whisper Model
Whisper models are downloaded automatically on first run and cached locally in `models/` or `~/.cache/whisper`.
You can pre-download the model:
```bash
python scripts/download_models.py --model whisper-medium
```

---

## 🔄 Voice Pipeline Loop

1. **Background Listener**: Listens to ambient mic input.
2. **Wake Word Triggered**: On detecting "Hey Megan", status changes from `idle` to `listening`.
3. **Audio Recording**: Buffers speech until silence is detected (`silence_timeout_seconds`).
4. **Whisper Transcription**: Audio buffer is converted to text and automatically language-tagged.
5. **Core Execution**: Transcribed text is submitted to the intent classifier & chat engine.
