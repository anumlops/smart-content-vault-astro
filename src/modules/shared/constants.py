from .types import ContentCategory


VALID_CATEGORIES: list[str] = [c.value for c in ContentCategory]

CATEGORY_DOMAIN_MAP: dict[str, list[str]] = {
    "Technology": [
        "github.com", "stackoverflow.com", "dev.to", "medium.com",
        "techcrunch.com", "wired.com", "theverge.com", "arstechnica.com",
        "zdnet.com", "infoworld.com", "techradar.com", "digitaltrends.com",
    ],
    "Business": [
        "forbes.com", "bloomberg.com", "reuters.com", "wsj.com",
        "businessinsider.com", "economist.com", "inc.com", "entrepreneur.com",
        "hbr.org", "fastcompany.com",
    ],
    "Finance": [
        "investopedia.com", "fool.com", "marketwatch.com", "cnbc.com",
        "seekingalpha.com", "finviz.com", "tradingview.com", "coinbase.com",
        "binance.com", "coindesk.com",
    ],
    "Education": [
        "coursera.org", "udemy.com", "edx.org", "khanacademy.org",
        "udacity.com", "pluralsight.com", "skillshare.com", "mit.edu",
        "stanford.edu", "harvard.edu",
    ],
    "Health": [
        "webmd.com", "mayoclinic.org", "healthline.com", "verywellhealth.com",
        "who.int", "cdc.gov", "nih.gov", "medicalnewstoday.com",
    ],
    "Entertainment": [
        "youtube.com", "youtu.be", "netflix.com", "hulu.com", "spotify.com",
        "imdb.com", "rottentomatoes.com", "tiktok.com", "twitch.tv",
    ],
    "Productivity": [
        "notion.so", "todoist.com", "asana.com", "trello.com", "evernote.com",
        "obsidian.md", "roamresearch.com", "linear.app",
    ],
    "Career": [
        "linkedin.com", "indeed.com", "glassdoor.com", "monster.com",
        "levels.fyi", "teamblind.com", "leetcode.com",
    ],
    "Marketing": [
        "hubspot.com", "neilpatel.com", "moz.com", "searchenginejournal.com",
        "socialmediaexaminer.com", "marketingland.com", "buffer.com",
    ],
    "Lifestyle": [
        "airbnb.com", "tripadvisor.com", "lonelyplanet.com", "nomadlist.com",
        "theminimalists.com", "zenhabits.net",
    ],
}

TAG_MAX_COUNT = 10
TAG_MIN_COUNT = 5
SUMMARY_MAX_LENGTH = 500
TAKEAWAY_MAX_COUNT = 5
