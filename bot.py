import requests
from bs4 import BeautifulSoup
import discord
import asyncio
import json
import os
import re

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
LAST_KNOWN_ID = 56  # ✅ 기준이 되는 마지막 게시글 번호 (57 이상이면 알림)

# 실행 모드 설정
TEST_MODE = True  # True: 디버깅 및 테스트 실행 / False: 정상 실행

# 디스코드 클라이언트 설정
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def send_debug_message(content):
    """디스코드 채널에 디버깅 메시지 전송"""
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    
    if channel:
        try:
            # 메시지 길이가 2000자를 넘으면 나눠서 전송
            for i in range(0, len(content), 1900):
                await channel.send(f"🛠️ [디버깅] {content[i:i+1900]}")
        except Exception as e:
            print(f"🚨 디스코드 메시지 전송 오류: {e}")
    else:
        print(f"🚨 채널 ID {CHANNEL_ID}을 찾을 수 없음.")

async def check_new_posts():
    await send_debug_message(f"✅ 봇 실행 시작 (TEST_MODE = {TEST_MODE})")

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

    # 게시글 목록 가져오기
    articles = soup.select("table.board-list tbody tr")
    await send_debug_message(f"✅ 크롤링 완료, {len(articles)}개의 글을 찾음")

    new_posts = []
    max_post_id = LAST_KNOWN_ID

    for article in articles:
        title_tag = article.select_one("a")
        if title_tag:
            title = title_tag.text.strip()
            link = BASE_URL + title_tag["href"]

            # ✅ URL 디버깅 메시지 전송 (게시글 URL 확인)
            await send_debug_message(f"🔍 게시글 링크: {link}")

            # ✅ 게시글 번호 추출 (boardview/17/XX 형태에서 XX 추출)
            match = re.search(r"/boardview/17/(\d+)", link)
            if match:
                post_id = int(match.group(1))
                max_post_id = max(max_post_id, post_id)

                # ✅ 기준 번호(56)보다 크면 알림 보냄
                if post_id > LAST_KNOWN_ID:
                    new_posts.append({"id": post_id, "title": title, "link": link})
                    await send_debug_message(f"🚨 새 게시글 발견! (ID: {post_id})")

    # 🔹 TEST MODE ON: 가장 최신 글을 강제 전송
    if TEST_MODE:
        if new_posts:
            test_post = max(new_posts, key=lambda x: x["id"])  # 가장 높은 ID 글 선택
            message = f"🚨 [테스트 알림] 🚨\n**{test_post['title']}** (ID: {test_post['id']})\n🔗 {test_post['link']}"
            await send_debug_message(message)
            await send_debug_message("✅ 테스트 메시지 전송 완료!")
        else:
            await send_debug_message(f"🚨 테스트 모드 활성화, 그러나 새로운 게시글 없음 (최신 게시글 ID: {max_post_id})")

        await client.close()
        return

    await send_debug_message("✅ 테스트 모드 OFF, 새 글 감지 시작")

    if not new_posts:
        await send_debug_message(f"🚨 기준 ID {LAST_KNOWN_ID} 이상인 새 글 없음! (최신 게시글 ID: {max_post_id})")
        await client.close()
        return

    for post in new_posts:
        message = f"📢 새 글이 올라왔습니다!\n**{post['title']}** (ID: {post['id']})\n🔗 {post['link']}"
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
