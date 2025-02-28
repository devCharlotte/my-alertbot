import os
import discord
import asyncio
from datetime import datetime
from dotenv import load_dotenv  # 환경 변수 로드 (pip install python-dotenv)

# .env 파일에서 환경 변수 로드
load_dotenv()

# GitHub Secrets에서 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN:
    raise ValueError("🚨 DISCORD_TOKEN이 설정되지 않았습니다. .env 파일 또는 GitHub Secrets를 확인하세요.")

if not CHANNEL_ID:
    raise ValueError("🚨 CHANNEL_ID가 설정되지 않았습니다. .env 파일 또는 GitHub Secrets를 확인하세요.")

CHANNEL_ID = int(CHANNEL_ID)  # 숫자로 변환

# 디스코드 클라이언트 설정
intents = discord.Intents.all()  # 모든 이벤트 감지 (필요 시 MESSAGE CONTENT INTENT 활성화)
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
        print(f"🚨 채널 ID {CHANNEL_ID}을 찾을 수 없음. 봇이 올바른 서버에 추가되었는지 확인하세요.")
        return
    
    print("✅ 쉬는 시간 알림 봇이 정상적으로 시작되었습니다!")
    
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
            except discord.Forbidden:
                print(f"🚨 권한 오류: 봇이 {CHANNEL_ID} 채널에 메시지를 보낼 권한이 없습니다. 디스코드 권한 설정을 확인하세요.")
                return
            except discord.HTTPException as e:
                print(f"🚨 디스코드 API 오류 발생: {e}")
            except Exception as e:
                print(f"🚨 예상치 못한 오류 발생: {e}")

            await asyncio.sleep(60)  # 1분 대기 후 다시 확인 (중복 방지)
        else:
            await asyncio.sleep(10)  # 10초마다 현재 시간 확인

@client.event
async def on_ready():
    print(f"✅ 봇 로그인 완료: {client.user}")
    client.loop.create_task(send_break_notification())  # 알림 스케줄링 시작

try:
    client.run(TOKEN)
except discord.LoginFailure:
    print("🚨 로그인 실패: DISCORD_TOKEN이 잘못되었습니다. 개발자 포털에서 올바른 토큰을 복사했는지 확인하세요.")
except Exception as e:
    print(f"🚨 봇 실행 중 예기치 않은 오류 발생: {e}")
