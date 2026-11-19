name: AvroraAI

on:
  workflow_dispatch:
  schedule:
    - cron: "0 * * * *"

permissions:
  contents: read

jobs:
  create-cartoon:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Download project
        uses: actions/checkout@v4

      - name: Install FFmpeg
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg fonts-dejavu-core

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Create cartoon
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python main.py

      - name: Save video
        uses: actions/upload-artifact@v4
        with:
          name: AvroraAI-cartoon
          path: output/
          if-no-files-found: error
          retention-days: 7
