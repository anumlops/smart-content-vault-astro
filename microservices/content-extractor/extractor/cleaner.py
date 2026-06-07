import re

from bs4 import BeautifulSoup, Tag

BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote"}
CONTAINER_TAGS = {"div", "section", "article", "main", "header", "footer", "ul", "ol"}


class Cleaner:
    def clean(self, html_fragment: str) -> str:
        if not html_fragment:
            return ""
        soup = BeautifulSoup(html_fragment, "lxml")
        for tag in soup.find_all(["script", "style", "noscript", "iframe"]):
            tag.decompose()
        body = soup.find("body")
        root = body if body else soup
        blocks = self._extract_blocks(root)
        seen = []
        for block in blocks:
            if not seen or block != seen[-1]:
                seen.append(block)
        text = "\n\n".join(seen)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" ([,\.;:!?\)\]])", r"\1", text)
        text = re.sub(r"([\(\[]) ", r"\1", text)
        text = re.sub(r" +", " ", text)
        text = re.sub(r"\n\s*\n", "\n\n", text)
        return text.strip()

    def _extract_blocks(self, element) -> list[str]:
        blocks = []
        for child in element.children:
            if isinstance(child, Tag):
                if child.name in BLOCK_TAGS:
                    text = child.get_text(separator=" ", strip=True)
                    text = re.sub(r" +", " ", text)
                    if text:
                        prefix = "#" * min(int(child.name[1]), 6) if child.name.startswith("h") else ""
                        if prefix:
                            text = f"{prefix} {text}"
                        elif child.name == "li":
                            text = f"- {text}"
                        elif child.name == "blockquote":
                            text = f"> {text}"
                        blocks.append(text)
                elif child.name in CONTAINER_TAGS:
                    blocks.extend(self._extract_blocks(child))
            elif isinstance(child, str):
                t = child.strip()
                if t:
                    blocks.append(t)
        return blocks
