from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ExtractedPage:
    title: str
    text: str
    links: list[str]
    images: list[str]


def extract_page(html: str, base_url: str) -> ExtractedPage:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    text = " ".join(soup.get_text(" ").split())
    links = [
        urljoin(base_url, href)
        for anchor in soup.find_all("a")
        if (href := _string_attribute(anchor.get("href")))
    ]
    images = [
        urljoin(base_url, src)
        for image in soup.find_all("img")
        if (src := _string_attribute(image.get("src")))
    ]
    return ExtractedPage(title=title, text=text, links=links, images=images)


def _string_attribute(value: object) -> str:
    return value if isinstance(value, str) else ""
