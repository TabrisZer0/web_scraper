from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path.rstrip("/")
    if path:
        return f"{host}{path}"
    return host


def get_h1_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    return h1.get_text(strip=True) if h1 else ""


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    p = main.find("p") if main else soup.find("p")
    return p.get_text(strip=True) if p else ""


def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for a in soup.find_all("a"):
        href = a.get("href")
        if href:
            urls.append(urljoin(base_url, href))
    return urls


def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            images.append(urljoin(base_url, src))
    return images


def extract_page_data(html: str, page_url: str) -> dict:
    return {
        "url": page_url,
        "h1": get_h1_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }

import requests


def get_html(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": "BootCrawler/1.0"}
    )

    if response.status_code >= 400:
        raise Exception(f"HTTP error: {response.status_code}")

    content_type = response.headers.get("Content-Type", "")
    if not content_type.startswith("text/html"):
        raise Exception(f"Invalid content type: {content_type}")

    return response.text

from urllib.parse import urlparse

def crawl_page(base_url, current_url=None, page_data=None):
    if page_data is None:
        page_data = {}

    if current_url is None:
        current_url = base_url

    # STEP 1: Stay in same domain
    base_netloc = urlparse(base_url).netloc
    current_netloc = urlparse(current_url).netloc
    if current_netloc != base_netloc:
        return page_data

    # STEP 2: Normalize URL
    normalized_url = normalize_url(current_url)

    # STEP 3: Skip if already crawled
    if normalized_url in page_data:
        return page_data

    print(f"crawling: {current_url}")

    # STEP 4: Get HTML
    try:
        html = get_html(current_url)
    except Exception as e:
        print(f"error fetching {current_url}: {e}")
        return page_data

    # STEP 5: Extract page data
    page_info = extract_page_data(html, current_url)
    page_data[normalized_url] = page_info

    # STEP 6: Recurse
    urls = get_urls_from_html(html, base_url)
    for url in urls:
        crawl_page(base_url, url, page_data)

    return page_data
