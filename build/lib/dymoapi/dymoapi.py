import requests
from datetime import datetime, timedelta
from .exceptions import TokenValidationError

class DymoAPI:
    def __init__(self, config):
        self.root_api_key = config.get("root_api_key", None)
        self.api_key = config.get("api_key", None)
        self.tokens_response = None
        self.last_fetch_time = None

        if self.api_key: self.initialize_tokens()

    def initialize_tokens(self):
        current_time = datetime.now()
        if self.tokens_response and self.last_fetch_time and (current_time - self.last_fetch_time) < timedelta(minutes=5):
            print("[Dymo API] Using cached tokens response.")
            return

        tokens = {}
        if self.root_api_key: tokens["root"] = f"Bearer {self.root_api_key}"
        if self.api_key: tokens["private"] = f"Bearer {self.api_key}"

        if not tokens: return

        try:
            response = requests.post("https://api.tpeoficial.com/v1/dvr/tokens", json={"tokens": tokens})
            response.raise_for_status()
            data = response.json()
            if self.root_api_key and not data.get("root"): raise TokenValidationError("Invalid root token.")
            if self.api_key and not data.get("private"): raise TokenValidationError("Invalid private token.")
            self.tokens_response = data
            self.last_fetch_time = current_time
            print("[Dymo API] Tokens initialized successfully.")
        except requests.RequestException as e:
            print(f"[Dymo API] Error during token validation: {e}")
            raise TokenValidationError(f"Token validation error: {e}")

    def print_label(self, label_text):
        print(f"[Dymo API] Printing label with text: {label_text} using API key: {self.api_key}")

    # Private methods (placeholders for actual implementations)
    def is_valid_data(self, data):
        return True

    # Public methods (placeholders for actual implementations)
    def get_prayer_times(self, data):
        return "Prayer times"

    def input_satinizer(self, data):
        return "Sanitized input"

    def is_valid_pwd(self, data):
        return True

    def new_url_encrypt(self, data):
        return "Encrypted URL"