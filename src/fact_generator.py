"""
fact_generator.py

Calls Gemini (via Google AI Studio API) to generate one Hindi history
fact + a short Instagram caption, making sure it hasn't been used before.

SETTINGS (change here if needed):
- MODEL_NAME: which Gemini model to use for text generation.
- PROMPT_TEMPLATE: the instruction given to Gemini.
"""

import os
from google import genai
from .fact_tracker import load_used_facts

MODEL_NAME = "gemini-2.5-flash"

PROMPT_TEMPLATE = """
Tum ek Indian history expert ho. Ek naya, interesting, kam-suna-hua
history fact do (Hindi/Devanagari script mein), jo in facts mein se
KOI BHI NA ho (ye already use ho chuke hain, inhe repeat mat karo):

{used_facts}

Format bilkul isi tarah do (aur kuch mat likho):
FACT: <ek ya do line ka history fact, Devanagari mein>
CAPTION: <Instagram ke liye chhota engaging caption, Devanagari mein, hashtags ke sath>
"""


def generate_fact():
    used_facts = load_used_facts()
    used_facts_text = "\n".join(f"- {f}" for f in used_facts) if used_facts else "(abhi koi nahi)"

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=PROMPT_TEMPLATE.format(used_facts=used_facts_text),
    )

    text = response.text.strip()

    fact_line = ""
    caption_line = ""
    for line in text.splitlines():
        if line.startswith("FACT:"):
            fact_line = line.replace("FACT:", "").strip()
        elif line.startswith("CAPTION:"):
            caption_line = line.replace("CAPTION:", "").strip()

    return fact_line, caption_line
