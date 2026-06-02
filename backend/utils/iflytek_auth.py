"""iFlytek API authentication — HMAC-SHA256 URL signing."""
import hmac
import hashlib
import base64
from email.utils import formatdate
from urllib.parse import urlparse, urlencode, urlunparse


def assemble_auth_url(url: str, method: str, api_key: str, api_secret: str) -> str:
    """Sign a URL with iFlytek HMAC-SHA256 auth, returning the authenticated URL."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    path = parsed.path or "/"

    # RFC 1123 date
    date = formatdate(timeval=None, localtime=False, usegmt=True)

    # Build signing string
    signing_string = f"host: {host}\ndate: {date}\n{method.upper()} {path} HTTP/1.1"

    # HMAC-SHA256 sign
    signature = base64.b64encode(
        hmac.new(api_secret.encode("utf-8"), signing_string.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")

    # Build authorization string and Base64-encode it
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")

    # Add query params
    query = {
        "authorization": authorization,
        "date": date,
        "host": host,
    }
    # Merge with existing query params if any
    existing = {}
    if parsed.query:
        for p in parsed.query.split("&"):
            if "=" in p:
                k, v = p.split("=", 1)
                existing[k] = v
    existing.update(query)

    new_query = urlencode(existing)
    authenticated = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    return authenticated
