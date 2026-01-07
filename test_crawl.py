import unittest
from crawl import (
    normalize_url,
    get_h1_from_html,
    get_first_paragraph_from_html,
    get_urls_from_html,
    get_images_from_html,
    extract_page_data,
)


class TestCrawl(unittest.TestCase):

    # ---------- normalize_url ----------

    def test_normalize_url_https(self):
        self.assertEqual(
            normalize_url("https://blog.boot.dev/path"),
            "blog.boot.dev/path",
        )

    def test_normalize_url_http(self):
        self.assertEqual(
            normalize_url("http://blog.boot.dev/path"),
            "blog.boot.dev/path",
        )

    def test_normalize_url_trailing_slash(self):
        self.assertEqual(
            normalize_url("https://blog.boot.dev/path/"),
            "blog.boot.dev/path",
        )

    def test_normalize_url_no_path(self):
        self.assertEqual(
            normalize_url("https://blog.boot.dev"),
            "blog.boot.dev",
        )

    # ---------- get_h1_from_html ----------

    def test_get_h1_basic(self):
        html = "<html><body><h1>Title</h1></body></html>"
        self.assertEqual(get_h1_from_html(html), "Title")

    def test_get_h1_nested(self):
        html = "<html><body><div><h1>Nested</h1></div></body></html>"
        self.assertEqual(get_h1_from_html(html), "Nested")

    def test_get_h1_whitespace(self):
        html = "<html><body><h1>   Spaced   </h1></body></html>"
        self.assertEqual(get_h1_from_html(html), "Spaced")

    def test_get_h1_missing(self):
        html = "<html><body></body></html>"
        self.assertEqual(get_h1_from_html(html), "")

    # ---------- get_first_paragraph_from_html ----------

    def test_first_paragraph_basic(self):
        html = "<html><body><p>Hello</p></body></html>"
        self.assertEqual(get_first_paragraph_from_html(html), "Hello")

    def test_first_paragraph_main_priority(self):
        html = """
        <html><body>
            <p>Outside</p>
            <main><p>Inside</p></main>
        </body></html>
        """
        self.assertEqual(get_first_paragraph_from_html(html), "Inside")

    def test_first_paragraph_no_main(self):
        html = "<html><body><p>Only one</p></body></html>"
        self.assertEqual(get_first_paragraph_from_html(html), "Only one")

    def test_first_paragraph_missing(self):
        html = "<html><body></body></html>"
        self.assertEqual(get_first_paragraph_from_html(html), "")

    # ---------- get_urls_from_html ----------

    def test_get_urls_absolute(self):
        html = '<a href="https://blog.boot.dev">Boot</a>'
        result = get_urls_from_html(html, "https://blog.boot.dev")
        self.assertEqual(result, ["https://blog.boot.dev"])

    def test_get_urls_relative(self):
        html = '<a href="/path">Path</a>'
        result = get_urls_from_html(html, "https://blog.boot.dev")
        self.assertEqual(result, ["https://blog.boot.dev/path"])

    def test_get_urls_multiple(self):
        html = """
        <a href="/a">A</a>
        <a href="/b">B</a>
        """
        result = get_urls_from_html(html, "https://blog.boot.dev")
        self.assertEqual(
            result,
            [
                "https://blog.boot.dev/a",
                "https://blog.boot.dev/b",
            ],
        )

    def test_get_urls_missing_href(self):
        html = "<a>No link</a>"
        result = get_urls_from_html(html, "https://blog.boot.dev")
        self.assertEqual(result, [])

    # ---------- get_images_from_html ----------

    def test_get_images_relative(self):
        html = '<img src="/img.png">'
        result = get_images_from_html(html, "https://blog.boot.dev")
        self.assertEqual(result, ["https://blog.boot.dev/img.png"])

    def test_get_images_absolute(self):
        html = '<img src="https://blog.boot.dev/img.png">'
        result = get_images_from_html(html, "https://blog.boot.dev")
        self.assertEqual(result, ["https://blog.boot.dev/img.png"])

    def test_get_images_missing_src(self):
        html = "<img alt='nope'>"
        result = get_images_from_html(html, "https://blog.boot.dev")
        self.assertEqual(result, [])

    # ---------- extract_page_data ----------

    def test_extract_page_data_basic(self):
        html = """
        <html><body>
            <h1>Title</h1>
            <p>Paragraph</p>
            <a href="/a"></a>
            <img src="/img.png">
        </body></html>
        """

        result = extract_page_data(html, "https://blog.boot.dev")

        self.assertEqual(
            result,
            {
                "url": "https://blog.boot.dev",
                "h1": "Title",
                "first_paragraph": "Paragraph",
                "outgoing_links": ["https://blog.boot.dev/a"],
                "image_urls": ["https://blog.boot.dev/img.png"],
            },
        )

    def test_extract_page_data_missing_elements(self):
        html = "<html><body></body></html>"

        result = extract_page_data(html, "https://blog.boot.dev")

        self.assertEqual(
            result,
            {
                "url": "https://blog.boot.dev",
                "h1": "",
                "first_paragraph": "",
                "outgoing_links": [],
                "image_urls": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
