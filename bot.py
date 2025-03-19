import os
import discord
import asyncio
from datetime import datetime

# GitHub Secrets에서 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    raise ValueError("🚨 DISCORD_TOKEN 또는 CHANNEL_ID가 설정되지 않았습니다. GitHub Secrets를 확인하세요.")

CHANNEL_ID = int(CHANNEL_ID)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 기본 알람 스케줄 (매시간 00분, 30분, 50분)
ALARM_HOURS = range(8, 24)  # 08:00 ~ 23:59
ALARM_MINUTES = {0: "🔔 00시 00분!!", 30: "🕞 30분이야! 다시 집중해보자!", 50: "⏳ 50분! 이제 잠깐 쉬는 시간을 가져보자!"}

# 특정 요일 특정 시간 알림 (자유롭게 추가 가능)
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

    # 🚀 **첫 실행 시 테스트 메시지 전송 (봇이 정상 작동하는지 확인)**
    test_message = "✅ 디스코드 봇이 정상적으로 실행되었습니다! 알림이 정상적으로 전송될 예정입니다."
    await channel.send(test_message)
    print(f"✅ 테스트 메시지 전송: {test_message}")

    print("✅ 알림 봇 실행 중... 하루 동안 지속 실행")

    while True:
        now = datetime.now()
        weekday = now.strftime("%A")  # 요일 (Monday, Tuesday, ...)

        # 기본 알람 스케줄
        if now.hour in ALARM_HOURS and now.minute in ALARM_MINUTES:
            message = f"{ALARM_MINUTES[now.minute]}\n🕒 현재 시각: {now.strftime('%H:%M')}"
            await channel.send(message)
            print(f"✅ 알림 전송: {message}")

        # 특정 요일 추가 알림
        if weekday in EXTRA_SCHEDULES and now.hour in EXTRA_SCHEDULES[weekday] and now.minute == 0:
            message = f"{EXTRA_SCHEDULES[weekday][now.hour]}\n🕒 현재 시각: {now.strftime('%H:%M')}"
            await channel.send(message)
            print(f"✅ 요일별 알림 전송: {message}")

        await asyncio.sleep(60)  # 1분 대기 후 다시 확인

@client.event
async def on_ready():
    print(f"✅ 봇 로그인 완료: {client.user}")
    client.loop.create_task(send_notification())

if __name__ == "__main__":
    client.run(TOKEN)
