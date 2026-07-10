import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://news.ycombinator.com/"
TIMEOUT = 10
CSV_PATH = "hn_articles.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}


def fetch_page(url):
    """Ambil HTML dari url, return response object (atau None kalau gagal)."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()  # kalau status 404/500/dll, langsung lempar HTTPError
        return response
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengambil {url}: {e}")
        return None


def parse_articles(html):
    """Parse HTML jadi list dict {title, link, score, author, age}."""
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.find_all("tr", class_="athing")

    data = []
    for article in articles:
        # Struktur HN: <span class="titleline"><a href="...">Judul</a></span>
        title_tag = article.find("span", class_="titleline")
        if not title_tag:
            continue

        link_tag = title_tag.find("a")
        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        link = link_tag.get("href")

        # Score, author, dan age ada di baris <tr> BERIKUTNYA (class="subtext"),
        # bukan di dalam baris "athing" itu sendiri. Jadi perlu cari sibling-nya.
        subtext_row = article.find_next_sibling("tr")
        subtext = subtext_row.find("td", class_="subtext") if subtext_row else None

        score = None
        author = None
        age = None

        if subtext:
            score_tag = subtext.find("span", class_="score")
            if score_tag:
                score = score_tag.get_text(strip=True)

            author_tag = subtext.find("a", class_="hnuser")
            if author_tag:
                author = author_tag.get_text(strip=True)

            age_tag = subtext.find("span", class_="age")
            if age_tag:
                # Tag <a> di dalam span.age biasanya berisi teks "X hours ago"
                age_link = age_tag.find("a")
                age = age_link.get_text(strip=True) if age_link else age_tag.get_text(strip=True)

        data.append({
            "title": title,
            "link": link,
            "score": score,
            "author": author,
            "age": age
        })

    return data


if __name__ == "__main__":
    response = fetch_page(URL)

    if response is None:
        print("Gagal mengambil halaman.")
    else:
        articles = parse_articles(response.text)

        for item in articles:
            print(f"Title: {item['title']}")
            print(f"Link: {item['link']}")
            print(f"Score: {item['score']}")
            print(f"Author: {item['author']}")
            print(f"Age: {item['age']}")
            print()

        df = pd.DataFrame(articles)
        df.to_csv(CSV_PATH, index=False)
        print(f"Selesai! {len(df)} artikel disimpan ke {CSV_PATH}")