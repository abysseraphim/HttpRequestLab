import requests
from urllib.parse import urlsplit
from core import request_parser
from core import history_data

def send_request(method, url, raw_request, allow_redirects=False):
    parsed = request_parser.parse_request(raw_request)

    request_host = parsed["headers"].get("Host", "").strip()

    url_parts = urlsplit(url)

    if request_host != url_parts.netloc:
        parsed["headers"]["Host"] = url_parts.netloc
        path = parsed["path"]

        if not path.startswith("/"):
            path = "/" + path

        url = f"{url_parts.scheme}://{url_parts.netloc}{path}"

    headers = parsed["headers"]
    body = parsed["body"]

    try:
        r = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=body,
            timeout=10,
            allow_redirects=allow_redirects
        )

        print("History:", len(r.history))
        for resp in r.history:
            print(resp.status_code, resp.url)

        print("Final:", r.status_code, r.url)

        rData = {
            "method": method,
            "url": r.url,
            "status": r.status_code,
            "host_header": headers.get("Host"),
            "request_headers": headers,
            "request_body": body,
            "redirects": len(r.history),
            "raw_request": raw_request,
            "timeElapsed": r.elapsed.total_seconds(),
            "size": len(r.content)
        }

        history_data.HISTORY.append(rData)

        return {
            "success": True,
            "status": r.status_code,
            "body": r.text,
            "headers": r.headers,
            "url": r.url,
            "reason": r.reason,
            "encoding": r.encoding,
            "timeElapsed": r.elapsed.total_seconds()
        }

    except Exception as err:
        print("[e]error occured:", err)
        return {
            "success": False,
            "error": str(err)
        }