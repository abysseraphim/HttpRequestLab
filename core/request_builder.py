from urllib.parse import urlsplit

DEFAULT_HEADERS = {
    "User-Agent": "BurpLite-RequestLab",
    "Accept": "*/*",
    "Connection": "close"
}

def build_request(method, url, headers=None):
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    parsed = urlsplit(url)

    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query

    host = parsed.netloc

    headers = headers or DEFAULT_HEADERS

    request = f"{method} {path} HTTP/1.1\n"
    request += f"Host: {host}\n"

    for k, v in headers.items():
        request += f"{k}: {v}\n"

    request += "\n"
    return request
