import json
import time
import google.generativeai as genai
from app.config import Config
from app.utils.logger import logger


class AIService:
    """Wrapper around Google Gemini for language-related AI tasks."""

    def __init__(self):
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set – AI endpoints will fail")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    # ── helpers ────────────────────────────────────────────────────────

    def _generate(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the raw text response.

        Retries up to 3 times on rate-limit (429) errors with backoff.
        """
        logger.debug("Gemini prompt (%d chars): %s…", len(prompt), prompt[:120])
        last_error = None
        for attempt in range(3):
            try:
                response = self.model.generate_content(prompt)
                text = response.text.strip()
                logger.debug("Gemini response (%d chars)", len(text))
                return text
            except Exception as e:
                last_error = e
                if "429" in str(e) or "quota" in str(e).lower():
                    wait = (attempt + 1) * 10  # 10s, 20s, 30s
                    logger.warning("Rate limited (attempt %d/3), retrying in %ds…", attempt + 1, wait)
                    time.sleep(wait)
                else:
                    raise
        raise Exception(f"AI request failed after 3 retries (rate limited). Please wait a minute and try again. Details: {last_error}")

    def _parse_json(self, raw: str) -> dict:
        """Try to extract a JSON object from the model output."""
        # Gemini sometimes wraps JSON in ```json ... ```
        cleaned = raw
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[-1]
        if "```" in cleaned:
            cleaned = cleaned.split("```")[0]
        return json.loads(cleaned.strip())

    # ── public methods ─────────────────────────────────────────────────

    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        """Translate *text* from source_lang to target_lang.

        Returns dict with keys: translated_text, source_language, target_language, confidence
        """
        prompt = f"""You are a professional language translator. 
Translate the following text from {source_lang} to {target_lang}.
Respond ONLY with a JSON object (no markdown fences) containing:
- "translated_text": the translated text
- "source_language": "{source_lang}"
- "target_language": "{target_lang}"  
- "confidence": a confidence score between 0.0 and 1.0
- "notes": any translation notes or alternative translations (brief)

Text to translate:
\"\"\"{text}\"\"\"
"""
        raw = self._generate(prompt)
        try:
            return self._parse_json(raw)
        except json.JSONDecodeError:
            return {
                "translated_text": raw,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": None,
                "notes": "Could not parse structured response",
            }

    def grammar_check(self, text: str, language: str = "English") -> dict:
        """Check grammar of *text* and return corrections.

        Returns dict with keys: corrected_text, errors, score, suggestions
        """
        prompt = f"""You are an expert {language} grammar checker and writing assistant.
Analyze the following text for grammar, spelling, punctuation, and style issues.
Respond ONLY with a JSON object (no markdown fences) containing:
- "corrected_text": the corrected version of the text
- "errors": a list of objects, each with "original", "correction", and "explanation"
- "score": a grammar quality score between 0.0 and 1.0 (1.0 = perfect)
- "suggestions": a list of brief style/improvement suggestions

Text to analyze:
\"\"\"{text}\"\"\"
"""
        raw = self._generate(prompt)
        try:
            return self._parse_json(raw)
        except json.JSONDecodeError:
            return {
                "corrected_text": raw,
                "errors": [],
                "score": None,
                "suggestions": [],
            }

    def summarize(self, text: str, target_language: str = None, max_sentences: int = 3) -> dict:
        """Summarize *text*, optionally in *target_language*.

        Returns dict with keys: summary, language, sentence_count, key_points
        """
        lang_instruction = ""
        if target_language:
            lang_instruction = f"Provide the summary in {target_language}."

        prompt = f"""You are a text summarization expert.
Summarize the following text in at most {max_sentences} sentences. {lang_instruction}
Respond ONLY with a JSON object (no markdown fences) containing:
- "summary": the summarized text
- "language": the language of the summary
- "sentence_count": number of sentences in the summary
- "key_points": a list of key points extracted from the text

Text to summarize:
\"\"\"{text}\"\"\"
"""
        raw = self._generate(prompt)
        try:
            return self._parse_json(raw)
        except json.JSONDecodeError:
            return {
                "summary": raw,
                "language": target_language or "unknown",
                "sentence_count": None,
                "key_points": [],
            }

    def detect_language(self, text: str) -> dict:
        """Detect the language of *text*.

        Returns dict with keys: detected_language, language_code, confidence, alternatives
        """
        prompt = f"""You are a language detection expert.
Identify the language of the following text.
Respond ONLY with a JSON object (no markdown fences) containing:
- "detected_language": the full name of the detected language (e.g. "English")
- "language_code": the ISO 639-1 code (e.g. "en")
- "confidence": a confidence score between 0.0 and 1.0
- "alternatives": a list of other possible languages with their codes and confidence scores

Text to analyze:
\"\"\"{text}\"\"\"
"""
        raw = self._generate(prompt)
        try:
            return self._parse_json(raw)
        except json.JSONDecodeError:
            return {
                "detected_language": raw,
                "language_code": None,
                "confidence": None,
                "alternatives": [],
            }


# Module-level singleton
ai_service = AIService()
