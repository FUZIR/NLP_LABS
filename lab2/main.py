import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://tsn.ua/news/"
PAGES_COUNT = 50

def clean_article_text(text: str) -> str:
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()
        line = line.replace("NBSP", " ")
        if not line:
            continue

        if "©" in line or "/" in line:
            continue

        if line in ["Війна в Україні", "Політика", "Світ", "Україна"]:
            continue

        if line.startswith("Нагадаємо"):
            continue

        if sum(c.isdigit() for c in line) / len(line) > 0.3:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)

def parse_new_tsn(pages_count: int):
    news_data = []
    all_news_links = []
    session = requests.Session()

    for i in range(pages_count):
        page = session.get(URL + f"page-{i+1}")
        soup = BeautifulSoup(page.text, "html.parser")

        news_links = soup.find_all("a", {"class": "c-entry__link u-link-overlay"})
        links = [link.get("href") for link in news_links]
        all_news_links.extend(links)

    for link in all_news_links:
        page = session.get(link)
        soup = BeautifulSoup(page.text, "html.parser")

        time = soup.find("time", class_="text-current c-bar__link c-entry__time").get("datetime")
        header = soup.find("h1", {"class": "c-entry__title c-title c-title--h1 font-bold"}).text.strip()
        article = soup.find("div", {"class": "c-prose c-post__inner"})
        paragraphs = article.find_all("p")

        texts = []
        for p in paragraphs:
            txt = p.get_text(" ", strip=True)
            if len(txt) > 40:
                texts.append(txt)
        total_text = "\n".join(texts)
        news_data.append({"datetime": time, "header": header, "text": clean_article_text(total_text)})

    pd.DataFrame(news_data).to_csv("./news.csv", index=False)



if __name__ == '__main__':
    parse_new_tsn(pages_count=PAGES_COUNT)