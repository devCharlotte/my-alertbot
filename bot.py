import requests
from bs4 import BeautifulSoup
import discord
import asyncio
import json
import os

# GitHub Secrets에서 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")  # 디스코드 봇 토큰
CHANNEL_ID = os.getenv("CHANNEL_ID")  # 디스코드 채널 ID

# 환경 변수 검증
if not TOKEN or not CHANNEL_ID:
    raise ValueError("🚨 환경 변수가 설정되지 않음! GitHub Secrets 확인 필요")

CHANNEL_ID = int(CHANNEL_ID)  # 채널 ID를 정수로 변환

DATA_FILE = "latest_posts.json"
BASE_URL = "https://inno.hongik.ac.kr"
TARGET_URL = f"{BASE_URL}/career/board/17"

# 디스코드 클라이언트 설정
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def send_debug_message(content):
    """디스코드 채널에 디버깅 메시지 전송"""
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"🛠️ [디버깅] {content}")
    else:
        print(f"🚨 채널 ID {CHANNEL_ID}을 찾을 수 없음.")

async def check_new_posts():
    await send_debug_message("✅ 봇 실행 시작")

    # 디스코드 채널 확인
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        await send_debug_message(f"🚨 채널 ID {CHANNEL_ID}을 찾을 수 없음! 봇이 올바른 서버에 추가되었는지 확인 필요")
        await client.close()
        return

    await send_debug_message("✅ 디스코드 채널 연결 성공")

    # 웹사이트 크롤링
    try:
        response = requests.get(TARGET_URL)
        response.raise_for_status()
        await send_debug_message("✅ 웹사이트 요청 성공")
    except requests.RequestException as e:
        await send_debug_message(f"🚨 크롤링 오류 발생: {e}")
        await client.close()
        return

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.select("ul.board-list li")
    await send_debug_message(f"✅ 크롤링 완료, {len(articles)}개의 글을 찾음")

    new_posts = []
    for article in articles:
        title_tag = article.select_one("a")
        if title_tag:
            title = title_tag.text.strip()
            link = BASE_URL + title_tag["href"]
            new_posts.append({"title": title, "link": link})

    if not new_posts:
        await send_debug_message("🚨 새 글 없음!")
        await client.close()
        return

    await send_debug_message(f"🔍 최신 글 제목: {new_posts[0]['title']}")

    # 테스트 모드: 가장 최신 글을 강제로 알림
    TEST_MODE = True
    if TEST_MODE:
        test_post = new_posts[0]  # 최신 글 1개 선택
        message = f"🚨 [테스트 알림] 🚨\n**{test_post['title']}**\n🔗 {test_post['link']}"
        await send_debug_message(message)
        await send_debug_message("✅ 테스트 메시지 전송 완료!")
        await client.close()
        return

    # 저장된 데이터 불러오기
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            saved_posts = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        saved_posts = []

    new_entries = [post for post in new_posts if post not in saved_posts]

    if not new_entries:
        await send_debug_message("🚨 새 글 없음! 알림 전송 안 함.")
        await client.close()
        return

    for post in new_entries:
        message = f"📢 새 글이 올라왔습니다!\n**{post['title']}**\n🔗 {post['link']}"
        await send_debug_message(message)

    # 새로운 글을 저장
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(new_posts, file, indent=4, ensure_ascii=False)

    await send_debug_message("✅ 새 글 저장 완료")
    await client.close()

@client.event
async def on_ready():
    await send_debug_message(f"✅ 봇 로그인 완료: {client.user}")
    await check_new_posts()

client.run(TOKEN)
