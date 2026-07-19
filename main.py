"""
main.py

Orchestrates the full daily pipeline:
1. Generate a fresh (non-repeated) history fact + caption (Gemini)
2. Generate a background image for it (Nano Banana 2 Lite)
3. Add branding/text overlay onto the image
4. Upload the final image to Google Drive
5. Save the fact into used_facts.json so it's never repeated

SETTING (change here if needed):
- IMAGES_PER_RUN: how many images to generate in a single run.
  GitHub Actions will call this script twice a day (4 AM and 5 AM IST),
  so IMAGES_PER_RUN=5 gives 5+5 = 10 images/day total.
"""

import os
import sys
import tempfile

from src.fact_generator import generate_fact
from src.image_generator import generate_image
from src.branding import add_branding
from src.drive_uploader import upload_to_drive
from src.fact_tracker import save_used_fact

IMAGES_PER_RUN = 5


def run():
    batch_label = sys.argv[1] if len(sys.argv) > 1 else "batch"

    for i in range(IMAGES_PER_RUN):
        print(f"[{batch_label}] Generating image {i + 1}/{IMAGES_PER_RUN}...")

        fact_text, caption_text = generate_fact()
        if not fact_text:
            print("Fact generate nahi hui, skip kar rahe hain.")
            continue

        with tempfile.TemporaryDirectory() as tmp_dir:
            raw_image_path = os.path.join(tmp_dir, "raw.png")
            final_image_path = os.path.join(tmp_dir, "final.png")

            generate_image(fact_text, raw_image_path)
            add_branding(raw_image_path, fact_text, final_image_path)

            file_name = f"itihas_{batch_label}_{i + 1}.png"
            upload_to_drive(final_image_path, file_name)

        save_used_fact(fact_text)
        print(f"[{batch_label}] Done: {fact_text[:40]}...")


if __name__ == "__main__":
    run()
