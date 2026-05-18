from autotrain_data_forge.extractors import extract_page


def test_extract_page_removes_scripts_and_normalizes_links() -> None:
    page = extract_page(
        """
        <html>
          <head><title>Demo</title><script>secret()</script></head>
          <body>
            <a href="/next">Next</a>
            <img src="/image.png" />
            <p>Hello   world</p>
          </body>
        </html>
        """,
        "https://example.com/docs/start",
    )

    assert page.title == "Demo"
    assert "secret" not in page.text
    assert "Hello world" in page.text
    assert page.links == ["https://example.com/next"]
    assert page.images == ["https://example.com/image.png"]
