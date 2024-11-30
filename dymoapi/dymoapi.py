from .utils.basics import DotDict
import os, sys, requests, importlib
from datetime import datetime, timedelta
from .config import BASE_URL, set_base_url
from .exceptions import AuthenticationError
import dymoapi.response_models as response_models
from .services.autoupload import check_for_updates

class DymoAPI:
    def __init__(self, config={}):
        self.root_api_key = config.get("root_api_key", None)
        self.api_key = config.get("api_key", None)
        self.server_email_config = config.get("server_email_config", None)
        self.tokens_response = None
        self.last_fetch_time = None
        self.local = config.get("local", False)

        set_base_url(self.local)
        self.base_url = BASE_URL
        check_for_updates()
        if self.api_key: self.initialize_tokens()
    
    def _get_function(self, module_name, function_name="main"):
        if module_name == "private" and self.api_key is None: raise AuthenticationError("Invalid private token.")
        func = getattr(importlib.import_module(f".branches.{module_name}", package="dymoapi"), function_name)
        if module_name == "private": return lambda *args, **kwargs: DotDict(func(self.api_key, *args, **kwargs))
        return lambda *args, **kwargs: DotDict(func(*args, **kwargs))

    def initialize_tokens(self):
        current_time = datetime.now()
        if self.tokens_response and self.last_fetch_time and (current_time - self.last_fetch_time) < timedelta(minutes=5): return print("[Dymo API] Using cached tokens response.")

        tokens = {}
        if self.root_api_key: tokens["root"] = f"Bearer {self.root_api_key}"
        if self.api_key: tokens["private"] = f"Bearer {self.api_key}"

        if not tokens: return

        try:
            response = requests.post(f"{self.base_url}/v1/dvr/tokens", json={"tokens": tokens})
            response.raise_for_status()
            data = response.json()
            if self.root_api_key and not data.get("root"): raise AuthenticationError("Invalid root token.")
            if self.api_key and not data.get("private"): raise AuthenticationError("Invalid private token.")
            self.tokens_response = data
            self.last_fetch_time = current_time
            print("[Dymo API] Tokens initialized successfully.")
        except requests.RequestException as e:
            print(f"[Dymo API] Error during token validation: {e}")
            raise AuthenticationError(f"Token validation error: {e}")

    def is_valid_data(self, data) -> response_models.DataVerifierResponse:
        response = self._get_function("private", "is_valid_data")(data)
        if response.get("ip",{}).get("as"):
            response["ip"]["_as"] = response["ip"]["as"]
            response["ip"]["_class"] = response["ip"]["class"]
            response["ip"].pop("as")
            response["ip"].pop("class")
        return response_models.DataVerifierResponse(**response)
    
    def send_email(self, data) -> response_models.SendEmailResponse:
        if not self.server_email_config and not self.root_api_key: raise AuthenticationError("You must configure the email client settings.")
        return response_models.DataVerifierResponse(**self._get_function("private", "send_email")({**data, "serverEmailConfig": self.server_email_config}))
    
    def get_random(self, data) -> response_models.SRNGResponse:
        return response_models.DataVerifierResponse(**self._get_function("private", "get_random")({**data}))

    def get_prayer_times(self, data) -> response_models.PrayerTimesResponse:
        return response_models.PrayerTimesResponse(**self._get_function("public", "get_prayer_times")(data))

    def satinizer(self, data) -> response_models.SatinizerResponse:
        return response_models.SatinizerResponse(**self._get_function("public", "satinizer")(data))

    def is_valid_pwd(self, data) -> response_models.IsValidPwdResponse:
        return response_models.IsValidPwdResponse(**self._get_function("public", "is_valid_pwd")(data))

    def new_url_encrypt(self, data) -> response_models.UrlEncryptResponse:
        return response_models.UrlEncryptResponse(**self._get_function("public", "new_url_encrypt")(data))
    
if __name__ == "__main__": sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))