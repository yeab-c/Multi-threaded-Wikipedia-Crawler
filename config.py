from dataclasses import dataclass

@dataclass
class PageData:
    url: str
    title: str
    text: str
    links: list[str]
