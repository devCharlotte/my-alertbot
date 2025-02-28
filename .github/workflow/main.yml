name: Run Discord Bot

on:
  schedule:
    - cron: "0 23 * * *"  # 한국 시간 08:00 (UTC 23:00, 전날)
    - cron: "0 0 * * *"   # 한국 시간 09:00 (UTC 00:00)
    - cron: "0 1 * * *"   # 한국 시간 10:00 (UTC 01:00)
    - cron: "0 2 * * *"   # 한국 시간 11:00 (UTC 02:00)
    - cron: "0 3 * * *"   # 한국 시간 12:00 (UTC 03:00)
    - cron: "0 4 * * *"   # 한국 시간 13:00 (UTC 04:00)
    - cron: "0 5 * * *"   # 한국 시간 14:00 (UTC 05:00)
    - cron: "0 6 * * *"   # 한국 시간 15:00 (UTC 06:00)
    - cron: "0 7 * * *"   # 한국 시간 16:00 (UTC 07:00)
    - cron: "0 8 * * *"   # 한국 시간 17:00 (UTC 08:00)
    - cron: "0 9 * * *"   # 한국 시간 18:00 (UTC 09:00)
    - cron: "0 10 * * *"  # 한국 시간 19:00 (UTC 10:00)
    - cron: "0 11 * * *"  # 한국 시간 20:00 (UTC 11:00)
    - cron: "0 12 * * *"  # 한국 시간 21:00 (UTC 12:00)
    - cron: "0 13 * * *"  # 한국 시간 22:00 (UTC 13:00)
  workflow_dispatch:  # 수동 실행 버튼 활성화

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run bot
        env:
          DISCORD_TOKEN: ${{ secrets.DISCORD_TOKEN }}
          CHANNEL_ID: ${{ secrets.CHANNEL_ID }}
        run: python bot.py
