import os
import discord
import asyncio
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    raise ValueError("🚨 DISCORD_TOKEN 또는 CHANNEL_ID가 설정되지 않았습니다. GitHub Secrets를 확인하세요.")

CHANNEL_ID = int(CHANNEL_ID)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 기본 알람 스케줄 (매시간 00분, 30분, 50분)
ALARM_HOURS = range(8, 24)  # 08:00 ~ 23:59
ALARM_MINUTES = {
    0: "🔔 00시 00분!!",
    30: "🕞 30분이야! 다시 집중해보자!",
    50: "⏳ 50분! 이제 잠깐 쉬는 시간을 가져보자!"
}

# 특정 요일 특정 시간 알림 추가
EXTRA_SCHEDULES = {
    "Monday": {10: "📢 월요일 오전 10시! 새로운 한 주가 시작됐어!"},
    "Wednesday": {15: "📢 수요일 오후 3시! 주중 절반 지났어! 힘내자!"},
    "Friday": {20: "📢 금요일 밤 8시! 주말이 다가왔어! 조금만 더 힘내!"}
}

async def send_notification():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print(f"🚨 채널 ID {CHANNEL_ID}을 찾을 수 없음. 봇이 서버에 추가되었는지 확인하세요.")
        return

    print("✅ 알림 봇 실행 중...")

    while True:
        now = datetime.now()
        weekday = now.strftime("%A")  # 요일 (Monday, Tuesday, ...)

        # 기본 알람 스케줄
        if now.hour in ALARM_HOURS and now.minute in ALARM_MINUTES:
            message = f"{ALARM_MINUTES[now.minute]}\n🕒 현재 시각: {now.strftime('%H:%M')}"
            await channel.send(message)
            print(f"✅ 알림 전송: {message}")

        # 특정 요일 추가 알림
        if weekday in EXTRA_SCHEDULES and now.hour in EXTRA_SCHEDULES[weekday]:
            message = f"{EXTRA_SCHEDULES[weekday][now.hour]}\n🕒 현재 시각: {now.strftime('%H:%M')}"
            await channel.send(message)
            print(f"✅ 요일별 알림 전송: {message}")

        await asyncio.sleep(60)  # 중복 방지 (1분 대기)

@client.event
async def on_ready():
    print(f"✅ 봇 로그인 완료: {client.user}")
    client.loop.create_task(send_notification())

# GitHub Actions 환경에서는 백그라운드 실행이 필요 없으므로 기본 실행 방식 수정
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # GitHub Actions 실행 환경에서도 정상 동작하도록 설정
    client.run(TOKEN)
