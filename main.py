import sys
import asyncio
from async_crawl import crawl_site_async
from csv_report import write_csv_report


async def main_async():
    # --- CLI arguments ---
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)

    base_url = sys.argv[1]

    # Optional arguments: max_concurrency and max_pages
    max_concurrency = int(sys.argv[2]) if len(sys.argv) >= 3 else 3
    max_pages = int(sys.argv[3]) if len(sys.argv) == 4 else 50

    print(f"starting crawl of: {base_url} (concurrency={max_concurrency}, max_pages={max_pages})")

    # --- Run async crawler ---
    page_data = await crawl_site_async(base_url, max_concurrency=max_concurrency, max_pages=max_pages)

    # --- Export to CSV ---
    write_csv_report(page_data)
    print(f"CSV report generated: report.csv")
    print(f"crawl complete\npages found: {len(page_data)}")


if __name__ == "__main__":
    asyncio.run(main_async())
