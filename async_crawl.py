import asyncio
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import aiohttp

from crawl import normalize_url, extract_page_data  # reuse your old helpers


class AsyncCrawler:
    def __init__(self, base_url, max_concurrency=3, max_pages=50):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.page_data = {}  # finished page data
        self.lock = asyncio.Lock()  # protect page_data
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None

        # --- max pages support ---
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()
        self.scheduled_count = 0  # counts pages scheduled to crawl

    # --- Context manager for aiohttp ---
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    # --- Track page visits safely ---
    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.should_stop:
                return False

            if normalized_url in self.page_data:
                return False

            # Increment scheduled pages
            self.scheduled_count += 1
            if self.scheduled_count > self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False

            return True

    # --- Async get_html ---
    async def get_html(self, url):
        async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as response:
            if response.status >= 400:
                raise Exception(f"HTTP error: {response.status}")
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("text/html"):
                raise Exception(f"Invalid content type: {content_type}")
            return await response.text()

    # --- Recursive crawl_page ---
    async def crawl_page(self, current_url):
        if self.should_stop:
            return

        # Only crawl URLs on the same domain
        if urlparse(current_url).netloc != self.base_domain:
            return

        normalized_url = normalize_url(current_url)
        first_visit = await self.add_page_visit(normalized_url)
        if not first_visit:
            return

        print(f"Crawling: {current_url}")

        async with self.semaphore:
            try:
                html = await self.get_html(current_url)
            except Exception as e:
                print(f"error fetching {current_url}: {e}")
                return

            # Extract page data
            page_info = extract_page_data(html, current_url)
            async with self.lock:
                self.page_data[normalized_url] = page_info

            # Extract links and schedule recursive crawl
            soup = BeautifulSoup(html, "html.parser")
            urls = [urljoin(current_url, a.get("href")) for a in soup.find_all("a") if a.get("href")]

            tasks = []
            for url in urls:
                if self.should_stop:
                    break  # stop scheduling new tasks
                task = asyncio.create_task(self.crawl_page(url))
                self.all_tasks.add(task)
                task.add_done_callback(lambda t: self.all_tasks.discard(t))
                tasks.append(task)

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    # --- Public crawl method ---
    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data


# --- Wrapper function to run the async crawler ---
async def crawl_site_async(base_url, max_concurrency=3, max_pages=50):
    async with AsyncCrawler(base_url, max_concurrency=max_concurrency, max_pages=max_pages) as crawler:
        page_data = await crawler.crawl()
        return page_data
