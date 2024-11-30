BASE_URL = "https://api.tpeoficial.com"

def set_base_url(is_local: bool):
    global BASE_URL
    BASE_URL = "http://localhost:3050" if is_local else "https://api.tpeoficial.com"