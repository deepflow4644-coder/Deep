"""
Daily Itihas AI Fact-Image Generator
--------------------------------------
Roz 5 naye Hindi history facts generate karta hai, unke liye background
image banata hai (Pollinations.ai - free), aur upar stylish Hindi text +
"Its Deep Verse | Itihas AI" branding bar overlay karta hai.

Zero-cost stack:
- Groq API (free) -> Hindi facts + Instagram captions generate karta hai
- Pollinations.ai (free, no key) -> background images
- Google Fonts (free) -> Baloo 2 (Hindi) aur Cinzel (branding bar)

Environment variable chahiye: GROQ_API_KEY
"""

import os
import re
import json
import time
import requests
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont

# ---------------- CONFIG ----------------
IMG_WIDTH, IMG_HEIGHT = 1080, 1350
OUTPUT_DIR = "generated_images"
USED_FACTS_FILE = "used_facts.json"
FONTS_DIR = "fonts"
NUM_FACTS_PER_DAY = 5

GOLD = (212, 175, 55)
RED_HIGHLIGHT = (200, 40, 40)
CREAM = (250, 240, 220)
DARK_OVERLAY = (20, 12, 8)

GROQ_MODEL = "llama-3.3-70b-versatile"


# ---------------- FONT DOWNLOAD (Google Fonts, free) ----------------
def download_google_font(family, weight, out_path):
    if os.path.exists(out_path):
        return out_path
    css_url = f"https://fonts.googleapis.com/css2?family={quote(family)}:wght@{weight}"
    resp = requests.get(css_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    match = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", resp.text)
    if not match:
        raise RuntimeError(f"Font URL nahi mila {family} ke liye")
    font_bytes = requests.get(match.group(1), timeout=30).content
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(font_bytes)
    return out_path


# ---------------- GROQ: generate facts ----------------
def generate_facts(used_facts):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable set nahi hai.")

    avoid_list = "\n".join(f"- {f}" for f in used_facts[-150:]) or "(koi nahi)"

    system_prompt = f"""Tum ek Indian history expert ho, "Itihas AI" channel ke liye content bana rahe ho.

{NUM_FACTS_PER_DAY} bilkul naye, alag-alag, lesser-known Indian history facts do
(pre-colonial, colonial/British Raj, aur post-independence period se mix karke).

Yeh facts PEHLE USE HO CHUKE HAIN - inhe dobara mat dena:
{avoid_list}

Sirf ek valid JSON array return karo, kuch aur text nahi, koi markdown fence nahi.
Har object mein yeh keys honi chahiye:
- "fact_hindi": Fact Hindi mein, chhota aur punchy (1-2 line). Proper nouns/naam
  English mein rakh sakte ho, baaki Hindi mein.
- "highlight_gold": list of 1-3 words/phrases (fact_hindi ke andar se hi, exact
  match) jo sabse important/shocking hain - gold color mein highlight honge
- "highlight_red": list of 0-2 words/phrases (fact_hindi ke andar se, exact match)
  jo numbers ya extra-dramatic hain - red color mein highlight honge
- "caption": Instagram caption style mein, engaging hook tone, 2-3 line, phir
  4-6 relevant hashtags niche (jaise #IndianHistory #ItihasAI)
- "image_prompt": Ek ENGLISH description (10-20 words) us fact se related visual
  scene ke liye - cinematic, historical, painting-style, taaki background image
  banane mein use ho sake

JSON array format mein hi jawab do, kuch aur nahi."""

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": system_prompt}],
            "temperature": 0.9,
        },
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"].strip()

    content = re.sub(r"^```(json)?", "", content.strip())
    content = re.sub(r"```$", "", content.strip())

    facts = json.loads(content)
    return facts[:NUM_FACTS_PER_DAY]


# ---------------- Background image (Pollinations - free) ----------------
def fetch_background(prompt, index):
    full_prompt = f"{prompt}, aged parchment texture, cinematic historical painting, warm gold and maroon tones"
    url = f"https://image.pollinations.ai/prompt/{quote(full_prompt)}?width={IMG_WIDTH}&height={IMG_HEIGHT}&nologo=true"
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            path = f"/tmp/bg_{index}.jpg"
            with open(path, "wb") as f:
                f.write(resp.content)
            return Image.open(path).convert("RGBA")
        except Exception:
            time.sleep(3)
    raise RuntimeError("Background image fetch nahi ho payi (3 attempts ke baad).")


# ---------------- Multi-color wrapped text drawing ----------------
def draw_wrapped_colored_text(draw, words_with_colors, font, max_width, start_y, center_x, line_spacing=14):
    lines = []
    current_line = []
    current_width = 0
    space_w = draw.textlength(" ", font=font)

    for word, color in words_with_colors:
        w = draw.textlength(word, font=font)
        if current_width + w + (space_w if current_line else 0) > max_width and current_line:
            lines.append(current_line)
            current_line = []
            current_width = 0
        current_line.append((word, color))
        current_width += w + (space_w if len(current_line) > 1 else 0)
    if current_line:
        lines.append(current_line)

    y = start_y
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + line_spacing

    for line in lines:
        line_width = sum(draw.textlength(w, font=font) for w, _ in line) + space_w * (len(line) - 1)
        x = center_x - line_width / 2
        for word, color in line:
            draw.text((x + 2, y + 2), word, font=font, fill=(0, 0, 0, 160))
            draw.text((x, y), word, font=font, fill=color)
            x += draw.textlength(word, font=font) + space_w
        y += line_height

    return y


# ---------------- Compose final image ----------------
def compose_image(bg_img, fact_hindi, highlight_gold, highlight_red, hindi_font_path, brand_font_path, out_path):
    img = bg_img.resize((IMG_WIDTH, IMG_HEIGHT)).convert("RGBA")

    gradient = Image.new("L", (1, IMG_HEIGHT), 0)
    for y in range(IMG_HEIGHT):
        if y > IMG_HEIGHT * 0.45:
            gradient.putpixel((0, y), int(180 * ((y - IMG_HEIGHT * 0.45) / (IMG_HEIGHT * 0.55))))
    gradient = gradient.resize((IMG_WIDTH, IMG_HEIGHT))
    overlay = Image.new("RGBA", (IMG_WIDTH, IMG_HEIGHT), DARK_OVERLAY + (0,))
    overlay.putalpha(gradient)
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    border_margin = 24
    draw.rectangle(
        [border_margin, border_margin, IMG_WIDTH - border_margin, IMG_HEIGHT - border_margin],
        outline=GOLD, width=4,
    )
    draw.rectangle(
        [border_margin + 10, border_margin + 10, IMG_WIDTH - border_margin - 10, IMG_HEIGHT - border_margin - 10],
        outline=(120, 20, 20), width=2,
    )

    brand_font = ImageFont.truetype(brand_font_path, 32)
    bar_y = 55
    draw.line([(60, bar_y + 45), (IMG_WIDTH - 60, bar_y + 45)], fill=GOLD, width=2)
    draw.text((60, bar_y), "Its Deep Verse", font=brand_font, fill=CREAM)
    right_text = "Itihas AI"
    rw = draw.textlength(right_text, font=brand_font)
    draw.text((IMG_WIDTH - 60 - rw, bar_y), right_text, font=brand_font, fill=CREAM)

    fact_font = ImageFont.truetype(hindi_font_path, 54)

    words_with_colors = []
    tokens = re.findall(r"\S+", fact_hindi)
    for token in tokens:
        color = CREAM
        clean = token.strip("।,.?!")
        if any(clean in h or h in clean for h in highlight_red if h):
            color = RED_HIGHLIGHT
        elif any(clean in h or h in clean for h in highlight_gold if h):
            color = GOLD
        words_with_colors.append((token, color))

    draw_wrapped_colored_text(
        draw, words_with_colors, fact_font,
        max_width=IMG_WIDTH - 160, start_y=IMG_HEIGHT - 420, center_x=IMG_WIDTH // 2,
    )

    img.convert("RGB").save(out_path, "JPEG", quality=92)


# ---------------- Main ----------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    used_facts = []
    if os.path.exists(USED_FACTS_FILE):
        with open(USED_FACTS_FILE, "r", encoding="utf-8") as f:
            used_facts = json.load(f)

    print("Facts generate ho rahe hain (Groq)...")
    facts = generate_facts(used_facts)

    print("Fonts download ho rahe hain (Google Fonts)...")
    hindi_font_path = download_google_font("Baloo+2", "800", f"{FONTS_DIR}/Baloo2-Bold.ttf")
    brand_font_path = download_google_font("Cinzel", "600", f"{FONTS_DIR}/Cinzel-SemiBold.ttf")

    date_tag = time.strftime("%Y-%m-%d")
    captions_out = []

    for i, fact in enumerate(facts, start=1):
        print(f"Image {i}/{len(facts)} ban rahi hai...")
        bg = fetch_background(fact["image_prompt"], i)
        out_path = os.path.join(OUTPUT_DIR, f"{date_tag}_fact{i}.jpg")
        compose_image(
            bg, fact["fact_hindi"], fact.get("highlight_gold", []), fact.get("highlight_red", []),
            hindi_font_path, brand_font_path, out_path,
        )
        captions_out.append(f"Fact {i}:\n{fact['caption']}\n")
        used_facts.append(fact["fact_hindi"])

    with open(USED_FACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(used_facts, f, ensure_ascii=False, indent=2)

    captions_path = os.path.join(OUTPUT_DIR, f"{date_tag}_captions.txt")
    with open(captions_path, "w", encoding="utf-8") as f:
        f.write("\n".join(captions_out))

    print("Sab images aur captions ban gaye!")


if __name__ == "__main__":
    main()
