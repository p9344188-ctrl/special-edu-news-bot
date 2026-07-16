import os
import feedparser
import asyncio
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

KEYWORDS = [
    "특수교육",
    "특수교육대상학생",
    "장애학생 교육",
    "특수학급",
    "특수학교",
    "특수교사",
    "특수교육실무사",
    "개별화교육계획",

    "통합교육",
    "장애학생 통합교육",
    "통합학급",
    "장애학생 통합학급",
    "통합교육 지원",
    "통합교육 실태",
    "장애학생 일반학교",
    "일반학교 특수교육대상학생",
    "통합교육 내실화",
    "통합교육 차별",
    "통합교육 교사",
    "통합교육 보조인력",
    "통합교육지원단",
    "통합학급 과밀",
    "통합학급 학생 수",
    "특수교육대상학생 일반학교",

    "장애학생 인권",
    "장애학생 학대",
    "장애학생 학교폭력",
    "장애학생 차별",
    "발달장애 학생",

    "행동중재",
    "교육부 특수교육",
    "교육부 통합교육",
    "시도교육청 특수교육",
    "시도교육청 통합교육",
]

MAX_NEWS = 12


def google_news_rss_url(keyword):
    encoded = quote(keyword)
    return f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"


def collect_news():
    articles = []
    seen_titles = set()

    for keyword in KEYWORDS:
        url = google_news_rss_url(keyword)
        feed = feedparser.parse(url)

        for entry in feed.entries[:4]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            if not title or not link:
                continue

            simple_title = title.replace(" ", "")
            if simple_title in seen_titles:
                continue

            seen_titles.add(simple_title)

            articles.append({
                "keyword": keyword,
                "title": title,
                "link": link,
            })

    return articles[:MAX_NEWS]


def make_message(articles):
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst).strftime("%Y년 %m월 %d일")

    if not articles:
        return f"📌 {today} 특수교육·통합교육 관련 뉴스\n\n오늘 수집된 관련 뉴스가 없습니다."

    message = f"📌 {today} 특수교육·통합교육 관련 뉴스\n\n"

    for i, article in enumerate(articles, 1):
        message += (
            f"{i}. {article['title']}\n"
            f"   🔎 검색어: {article['keyword']}\n"
            f"   🔗 {article['link']}\n\n"
        )

    message += "※ 자동 수집된 뉴스입니다. 세부 내용은 기사 원문을 확인해 주세요."
    return message


def split_message(message, limit=3500):
    parts = []
    current = ""

    for block in message.split("\n\n"):
        if len(current) + len(block) + 2 > limit:
            if current:
                parts.append(current)
            current = block
        else:
            current = current + "\n\n" + block if current else block

    if current:
        parts.append(current)

    return parts


async def send_news():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    articles = collect_news()
    message = make_message(articles)

    for msg in split_message(message):
        await bot.send_message(
            chat_id=CHAT_ID,
            text=msg,
            disable_web_page_preview=True,
        )


if __name__ == "__main__":
    asyncio.run(send_news())
