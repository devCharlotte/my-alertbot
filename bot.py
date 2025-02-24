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
    articles = soup.select("table.board-list tbody tr")  # ✅ 게시글 행(tr) 선택
    await send_debug_message(f"✅ 크롤링 완료, {len(articles)}개의 글을 찾음")

    if not articles:
        await send_debug_message(f"🚨 게시글을 찾을 수 없음! HTML 구조 확인 필요:\n{soup.prettify()[:1900]}")
        await client.close()
        return

    new_posts = []
    max_post_id = LAST_KNOWN_ID

    for article in articles:
        tds = article.find_all("td")  # ✅ <td> 요소들 가져오기
        if len(tds) < 2:
            continue  # 게시글 형식이 아니면 스킵

        post_id = None
        try:
            post_id = int(tds[0].text.strip())  # ✅ 첫 번째 <td>에서 게시글 번호 추출
        except ValueError:
            continue

        title_tag = article.find("a", href=True)
        if not title_tag:
            continue  # 제목 링크가 없으면 스킵

        title = title_tag.text.strip()
        link = BASE_URL + title_tag["href"]

        # ✅ 게시글 번호 확인 및 디버깅 메시지 전송
        await send_debug_message(f"🔍 게시글 번호: {post_id}, 제목: {title}, 링크: {link}")

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
