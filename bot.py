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

ALARM_HOURS = range(8, 23)  # 08:00 ~ 22:59
ALARM_MINUTES = {
    40: "⏳ 준희야 열심히 하고 있지?! 조금만 더 힘내자! 💪",
    50: "⏰ 준희야 쉬는 시간이야! 스트레칭하고 물 마시고 멀리 보자! ☕",
    0: "🚀 준희야 쉬는 시간 끝났어!!! 다시 열심히 하자! 화이팅! 🎯"
}

async def send_notification():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print(f"🚨 채널 ID {CHANNEL_ID}을 찾을 수 없음. 봇이 서버에 추가되었는지 확인하세요.")
        return
    
    print("✅ 알림 봇 실행 중...")

    while not client.is_closed():
        now = datetime.now()
        if now.hour in ALARM_HOURS and now.minute in ALARM_MINUTES:
            message = f"{ALARM_MINUTES[now.minute]}\n🕒 현재 시각: {now.strftime('%H:%M')}"
            try:
                await channel.send(message)
                print(f"✅ 알림 전송: {message}")
            except Exception as e:
                print(f"🚨 오류 발생: {e}")

            await asyncio.sleep(60)  # 중복 방지
        else:
            await asyncio.sleep(10)

@client.event
async def on_ready():
    print(f"✅ 봇 로그인 완료: {client.user}")
    client.loop.create_task(send_notification())

client.run(TOKEN)
