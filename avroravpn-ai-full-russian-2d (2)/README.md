# AvroraVPN AI — Russian 2D cartoon prototype

This GitHub Actions project creates a short vertical Russian-language cartoon with:
- Gemini-generated 5-scene script
- two recurring simple 2D characters (Бублик and Пиксель)
- Russian neural voices via Edge TTS
- captions and AvroraVPN branding
- MP4 output uploaded as a GitHub Actions artifact

## Setup
1. Upload `main.py`, `requirements.txt`, and `.github/workflows/avroravpn.yml` to the **root** of your GitHub repository, preserving the `.github/workflows` folders.
2. In GitHub: Settings → Secrets and variables → Actions → New repository secret.
3. Secret name: `GEMINI_API_KEY`. Paste your Gemini key into the secret value. Never put API keys in source code or public chat.
4. Actions → AvroraVPN 2D Cartoon → Run workflow.

## Output
Open the completed workflow run and download the artifact named `avroravpn-cartoon-...`.
The MP4 is vertical 720×1280. A text file with the script is also included.

## Schedule and limitations
The workflow is scheduled hourly, but GitHub scheduled runs can be delayed and are not guaranteed exactly on the hour. GitHub Actions usage limits apply. This prototype creates simple procedural 2D animation, not frame-by-frame neural animation. It does not publish to TikTok automatically. TikTok auto-publishing requires a separately configured and approved TikTok Content Posting API app and user OAuth authorization; never share your TikTok password.

## Cost and API notes
Gemini API free quotas and availability depend on Google's current terms and may change. Edge TTS uses Microsoft's online speech service; it requires internet access during the workflow run.
