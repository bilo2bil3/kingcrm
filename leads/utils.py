from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def add_query_string(url, params):
    url_parts = list(urlparse(url))
    query = dict(parse_qs(url_parts[4], keep_blank_values=True))
    query.update(params)
    qs_parts = []
    for k, v in query.items():
        if isinstance(v, (str, int)):
            qs_parts.append((k, v))
        elif isinstance(v, list):
            for f in v:
                qs_parts.append((k, f))
    url_parts[4] = urlencode(qs_parts)
    return urlunparse(url_parts)
