# Web Scraper

Lightweight web crawler for extracting page metadata (H1, first paragraph), outgoing links, and image URLs. Exports results to `report.csv`.

**Core files:**
- `Web_Scraper/crawl.py`: HTML parsing helpers and a synchronous recursive crawler (`crawl_page`).
- `Web_Scraper/async_crawl.py`: `AsyncCrawler` implementation with concurrency control (`max_concurrency`) and `max_pages` support.
- `Web_Scraper/main.py`: CLI entrypoint that runs the async crawler and writes a CSV via `csv_report.py`.
- `Web_Scraper/csv_report.py`: Writes crawled page data to `report.csv`.
- `Web_Scraper/test_crawl.py`: Unit tests for parsing helpers.

Requirements
------------
- Python 3.8+
- Packages: `beautifulsoup4`, `requests`, `aiohttp` (for async crawling)

Setup (recommended)
-------------------
Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install beautifulsoup4 requests aiohttp
```

Running the crawler
-------------------
Run the CLI entrypoint. Usage:

```bash
python3 Web_Scraper/main.py <base_url> [max_concurrency] [max_pages]
```

Examples:

```bash
# default concurrency=3, max_pages=50
python3 Web_Scraper/main.py https://example.com

# set concurrency to 5 and limit to 100 pages
python3 Web_Scraper/main.py https://example.com 5 100
```

The script writes `report.csv` in the repository root. Each row includes page URL, H1, first paragraph, outgoing links (semicolon-separated), and image URLs (semicolon-separated).

Running tests
-------------
Install test dependencies (see Setup) then run:

```bash
python3 Web_Scraper/test_crawl.py
# or
python3 -m unittest Web_Scraper/test_crawl.py
```

Notes & Tips
------------
- The project contains both a synchronous crawler (`crawl_page`) and an async crawler (`AsyncCrawler`). `main.py` uses the async crawler by default.
- Start with `max_concurrency=1` while debugging to avoid overwhelming a site.
- Be courteous: respect `robots.txt` and site rate limits when crawling external sites.
- If you want a `requirements.txt`, run:

```bash
pip freeze > requirements.txt
```


