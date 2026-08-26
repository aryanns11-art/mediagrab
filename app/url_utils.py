from urllib.parse import urlparse

def is_valid(url):
    url = url.strip()

    if not url:
        return False

    parsed = urlparse(url)

    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
    )


def detect_platform(url):
    
    parsed = urlparse(url.lower())

    domain = parsed.netloc

    if "youtube.com" in domain or "youtu.be" in domain:
        return "YouTube"

    if "instagram.com" in domain:
        return "Instagram"

    if "facebook.com" in domain or "fb.watch" in domain:
        return "Facebook"

    return "Unknown"