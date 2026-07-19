"""
image_generator.py

Calls Google AI Studio's image model to generate a background image
based on the history fact.

IMPORTANT SETTING TO VERIFY:
- MODEL_NAME below is set to a placeholder for "Nano Banana 2 Lite".
  Please confirm the EXACT model string from Google AI Studio's model
  list before running this (Studio > Models), since this name may
  differ slightly from what's written here.

Other SETTINGS:
- IMAGE_PROMPT_TEMPLATE: instruction given to the image model.
"""

import os
from google import genai

MODEL_NAME = "gemini-3.1-flash-lite-image"  # <-- verify exact name in Google AI Studio

IMAGE_PROMPT_TEMPLATE = """
Create a cinematic, historically-themed background illustration
(no text, no words, no letters in the image) representing this
Indian history fact: {fact}

Style: rich colors, dramatic lighting, painting-like, suitable as an
Instagram post background for a history page.
"""


def generate_image(fact_text, output_path):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=IMAGE_PROMPT_TEMPLATE.format(fact=fact_text),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            with open(output_path, "wb") as f:
                f.write(part.inline_data.data)
            return output_path

    raise RuntimeError("Image generation mein koi image data wapas nahi mili.")
