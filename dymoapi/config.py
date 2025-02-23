import re

BASE_URL = "https://api.tpeoficial.com"

def set_base_url(base_url: str) -> None:
    if re.match(r"^(https://api\.tpeoficial\.com$|http://(localhost:\d+|dymoapi:\d+))$", base_url):
        global BASE_URL
        BASE_URL = base_url
    else: raise ValueError("[Dymo API] Invalid URL. It must be https://api.tpeoficial.com or start with http://localhost or http://dymoapi followed by a port.")

def get_base_url():
    return BASE_URL