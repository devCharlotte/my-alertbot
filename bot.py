import os
import discord
import asyncio
from datetime import datetime

# GitHub Secrets에서 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    raise ValueError("🚨 환경 변수가 설정되지 않음! GitHub Secrets 확인 필요")

CHANNEL_ID = int(CHANNEL_ID)

# 디스코드 클라이언트 설정
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 알림 시간 설정 (매일 08:40 ~ 22:00 사이 40분, 50분, 정각(00분) 마다 알림)
ALARM_HOURS = range(8, 23)  # 08:00 ~ 22:59
ALARM_MINUTES = {
    40: "⏳ 준희야 열심히 하고 있지?! 조금만 더 힘내자! 💪",
    50: "⏰ 준희야 쉬는 시간이야! 스트레칭하고 물 마시고 멀리 보자! ☕",
    0: "🚀 준희야 쉬는 시간 끝났어!!! 다시 열심히 하자! 화이팅! 🎯"
}

async def send_break_notification():
    """설정된 시간마다 쉬는 시간 알림을 전송"""
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    
    if not channel:
        print(f"🚨 채널 ID {CHANNEL_ID}을 찾을 수 없음.")
        return
    
    print("✅ 쉬는 시간 알림 봇이 시작되었습니다!")
    
    while not client.is_closed():
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        if current_hour in ALARM_HOURS and current_minute in ALARM_MINUTES:
            time_str = now.strftime("%H:%M")
            message = f"{ALARM_MINUTES[current_minute]}\n🕒 현재 시각: {time_str}"

            try:
                await channel.send(message)
                print(f"✅ 알림 전송됨: {message}")
            except Exception as e:
                print(f"🚨 알림 전송 오류: {e}")

            await asyncio.sleep(60)  # 1분 대기 후 다시 확인 (중복 방지)
        else:
            await asyncio.sleep(10)  # 10초마다 현재 시간 확인

@client.event
async def on_ready():
    print(f"✅ 봇 로그인 완료: {client.user}")
    client.loop.create_task(send_break_notification())  # 알림 스케줄링 시작

client.run(TOKEN)
