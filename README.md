# Itihas AI — Daily History Images

Automated pipeline that generates 10 Hindi history fact-images per day
(5 at 4 AM IST, 5 at 5 AM IST) using Google AI Studio (Gemini +
Nano Banana 2 Lite), and uploads them to a Google Drive folder for
manual posting to Instagram.

## Files

- `main.py` — orchestrates the full pipeline for one run
- `src/fact_generator.py` — generates a fact + caption using Gemini
- `src/image_generator.py` — generates a background image using Nano Banana 2 Lite
- `src/branding.py` — overlays text + "Itihas AI" branding onto the image
- `src/drive_uploader.py` — uploads the final image to Google Drive
- `src/fact_tracker.py` — reads/writes `used_facts.json` so facts never repeat
- `used_facts.json` — running list of facts already generated
- `.github/workflows/daily-images.yml` — GitHub Actions workflow (2 daily cron triggers)

## One-time setup needed before this runs

1. **Google AI Studio API key**
   - Go to https://aistudio.google.com → "Get API Key" → create one
   - Add it as a GitHub repo secret named `GEMINI_API_KEY`

2. **Google Drive service account**
   - Create a Google Cloud project → enable Drive API → create a
     service account → generate a JSON key
   - Share your target Drive folder with the service account's email
     (give it Editor access)
   - Add the full JSON key content as a GitHub secret named
     `GDRIVE_SERVICE_ACCOUNT_JSON`
   - Add the target Drive folder's ID as a GitHub secret named
     `DRIVE_FOLDER_ID`

3. **Font file**
   - Download a Devanagari-supporting font (e.g. Noto Sans Devanagari
     Bold) and place it at `assets/fonts/NotoSansDevanagari-Bold.ttf`

4. **Verify the image model name**
   - `src/image_generator.py` uses a placeholder model string for
     "Nano Banana 2 Lite" — confirm the exact model name in Google AI
     Studio's model list before the first run

5. **Workflow permissions**
   - In repo Settings → Actions → General → Workflow permissions,
     make sure "Read and write permissions" is selected (so the
     workflow can commit `used_facts.json`)

## Testing manually

You can trigger a test run any time from the GitHub Actions tab using
"Run workflow" (the `workflow_dispatch` trigger), without waiting for
the scheduled time.
