import time
import json
import os
import discord
import asyncio
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

# Selenium 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창 없이 실행
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# GitHub Actions에서 Chrome 실행 경로 설정
chrome_options.binary_location = "/usr/bin/google-chrome"

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

    # Selenium을 사용하여 브라우저 열기
    try:
        driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=chrome_options)
        driver.get(TARGET_URL)

        # JavaScript 로딩을 기다림 (최대 10초)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.board-list tbody tr"))
        )

    except Exception as e:
        await send_debug_message(f"🚨 Selenium 실행 오류 발생: {e}")
        driver.quit()
        await client.close()
        return

    # 게시글 목록 가져오기
    articles = driver.find_elements(By.CSS_SELECTOR, "table.board-list tbody tr")
    await send_debug_message(f"✅ 크롤링 완료, {len(articles)}개의 글을 찾음")

    if not articles:
        await send_debug_message(f"🚨 게시글을 찾을 수 없음! JavaScript 로딩 문제 가능성 있음")
        driver.quit()
        await client.close()
        return

    new_posts = []
    max_post_id = LAST_KNOWN_ID

    for article in articles:
        try:
            post_id = int(article.find_element(By.TAG_NAME, "td").text.strip())  # ✅ 첫 번째 <td>에서 게시글 번호 추출
        except ValueError:
            continue

        title_tag = article.find_element(By.TAG_NAME, "a")
        if not title_tag:
            continue  # 제목 링크가 없으면 스킵

        title
