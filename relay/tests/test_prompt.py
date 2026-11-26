"""Tests for relay/prompt.py — Ghostgotchi system prompt builder."""

import unittest
from relay.prompt import build_system_prompt


class TestBuildSystemPrompt(unittest.TestCase):

    # --- French content mood contains the correct French opening ---
    def test_content_fr_contains_french_opening(self):
        prompt = build_system_prompt("content", "fr")
        self.assertIn("Tu es là !", prompt)
        self.assertIn("J'ai rêvé de toi toute la journée", prompt)

    # --- Spanish crying mood contains the correct Spanish lament ---
    def test_crying_es_contains_spanish_lament(self):
        prompt = build_system_prompt("crying", "es")
        self.assertIn("Me abandonaste", prompt)
        self.assertIn("lloré toda la noche", prompt)

    # --- okay/fr prompt must not break character or reveal AI nature ---
    def test_okay_fr_no_prohibited_words(self):
        prompt = build_system_prompt("okay", "fr")
        for forbidden in ("English", "AI", "language model", "artificial intelligence"):
            self.assertNotIn(
                forbidden,
                prompt,
                msg=f"Prompt must not contain '{forbidden}'",
            )

    # --- prompt stays within Gemini Live system-prompt size limit ---
    def test_all_prompts_under_2000_chars(self):
        for mood in ("content", "okay", "crying"):
            for lang in ("fr", "es"):
                prompt = build_system_prompt(mood, lang)
                self.assertLess(
                    len(prompt),
                    2000,
                    msg=f"Prompt for ({mood}, {lang}) is {len(prompt)} chars — exceeds 2000",
                )

    # --- all six (mood, language) combinations return a non-empty string ---
    def test_all_combinations_return_string(self):
        for mood in ("content", "okay", "crying"):
            for lang in ("fr", "es"):
                with self.subTest(mood=mood, lang=lang):
                    result = build_system_prompt(mood, lang)
                    self.assertIsInstance(result, str)
                    self.assertGreater(len(result), 0)

    # --- invalid inputs raise ValueError ---
    def test_invalid_mood_raises(self):
        with self.assertRaises(ValueError):
            build_system_prompt("angry", "fr")

    def test_invalid_language_raises(self):
        with self.assertRaises(ValueError):
            build_system_prompt("content", "zh")

    # --- Spanish openings use Spanish, not French ---
    def test_okay_es_contains_spanish_opening(self):
        prompt = build_system_prompt("okay", "es")
        self.assertIn("extrañé", prompt)

    def test_content_es_contains_spanish_opening(self):
        prompt = build_system_prompt("content", "es")
        self.assertIn("Soñé contigo", prompt)


if __name__ == "__main__":
    unittest.main()
