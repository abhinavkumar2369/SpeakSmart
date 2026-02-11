---
title: SpeakSmart
emoji: 🗣️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# SpeakSmart - AI Language Translation & Grammar Engine

This Space runs SpeakSmart, a powerful RESTful API for language translation, grammar checking, and text analysis powered by Google Gemini AI.

## Setup

1. Go to **Settings** → **Repository secrets**
2. Add your `GEMINI_API_KEY` (get one from [Google AI Studio](https://aistudio.google.com/apikey))

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/ai/translate` - Translate text
- `POST /api/ai/grammar-check` - Check grammar
- `POST /api/ai/summarize` - Summarize text
- `POST /api/ai/language-detect` - Detect language

Full documentation: [GitHub Repository](https://github.com/yourusername/SpeakSmart)
