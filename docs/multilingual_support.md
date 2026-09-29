# 🌍 Multilingual Voice & Chat Support

Ines is designed to communicate and understand commands in **multiple languages** without requiring cloud translation services.

---

## 🌐 Supported Languages

Ines provides 6 primary language slots configured in `configs/languages.yaml`:

| Language Code | Language | Default State | Whisper Code |
|---------------|----------|---------------|--------------|
| `en` | English | **Enabled** | `en` |
| `hi` | Hindi | Configurable | `hi` |
| `es` | Spanish | Configurable | `es` |
| `fr` | French | Configurable | `fr` |
| `de` | German | Configurable | `de` |
| `mr` | Marathi | Configurable | `mr` |

> Over 90+ additional languages supported by Whisper can be substituted in `configs/languages.yaml`.

---

## 🔄 Language Processing Flow

1. **Spoken Input**: The user speaks in any enabled language.
2. **Automatic Language Detection**: Whisper detects the language probability distribution during the initial audio chunk.
3. **Transcription**: Audio is transcribed into the detected language's script.
4. **Intent Handling**: Intent classification maps multilingual commands (e.g., *"Crea una carpeta llamada Proyectos"* or *"एक फ़ोल्डर बनाओ"*) to canonical actions (`create_folder`).
5. **Response Generation**: Ines replies in the user's spoken language.

---

## ⚙️ Enabling / Disabling Languages

Edit `configs/languages.yaml`:
```yaml
active_languages:
  - code: "en"
    name: "English"
    enabled: true

  - code: "hi"
    name: "Hindi"
    enabled: true    # Toggle to true
```
