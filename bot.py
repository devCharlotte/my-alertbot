import requests
from bs4 import BeautifulSoup
import discord
import asyncio
import json
import os

# GitHub Secrets에서 환경 변수 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")  # 디스코드 봇 토큰
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # 디스코드 채널 ID
TEST_MODE = True  # 테스트 모드 활성화 (True로 변경하면 테스트 실행됨)

DATA_FILE = "latest_posts.json"
BASE_URL = "https://inno.hongik.ac.kr"
TARGET_URL = f"{BASE_URL}/career/board/17"

# 디스코드 클라이언트 설정
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 저장된 데이터 불러오기
def load_saved_posts():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# 최신 글을 저장
def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=4, ensure_ascii=False)

# 새 글 크롤링
def get_latest_posts():
    response = requests.get(TARGET_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = soup.select("ul.board-list li")  # 글 목록을 가져오는 CSS 선택자
    new_posts = []

    for article in articles:
        title_tag = article.select_one("a")
        if title_tag:
            title = title_tag.text.strip()
            link = BASE_URL + title_tag["href"]
            new_posts.append({"title": title, "link": link})

    return new_posts

# 새 글 확인 및 디스코드 알림 전송
async def check_new_posts():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    saved_posts = load_saved_posts()
    latest_posts = get_latest_posts()

    if TEST_MODE:
        # 테스트 모드: 가장 마지막 글을 강제로 알림
        if latest_posts:
            test_post = latest_posts[0]  # 최신 글 1개 선택
            message = f"🚨 [테스트 알림] 🚨\n**{test_post['title']}**\n🔗 {test_post['link']}"
            await channel.send(message)
        await client.close()
        return

    if not saved_posts:
        save_posts(latest_posts)
        return

    new_entries = [post for post in latest_posts if post not in saved_posts]

    for post in new_entries:
        message = f"📢 준희야 새로운 공지 업로드 됐어!!!!!\n**{post['title']}**\n🔗 {post['link']}"
        await channel.send(message)

    if new_entries:
        save_posts(latest_posts)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await check_new_posts()

client.run(TOKEN)
