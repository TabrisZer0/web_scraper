import csv

def write_csv_report(page_data, filename="report.csv"):
    """
    Writes the page_data dictionary to a CSV file.

    :param page_data: Dictionary of crawled page data (values are page dicts)
    :param filename: CSV filename to write
    """
    # Define CSV columns
    fieldnames = ["page_url", "h1", "first_paragraph", "outgoing_link_urls", "image_urls"]

    # Open CSV file for writing
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write each page
        for page in page_data.values():
            if not page:  # skip any None entries, just in case
                continue

            writer.writerow({
                "page_url": page.get("url", ""),
                "h1": page.get("h1", ""),
                "first_paragraph": page.get("first_paragraph", ""),
                "outgoing_link_urls": ";".join(page.get("outgoing_links", [])),
                "image_urls": ";".join(page.get("image_urls", []))
            })
