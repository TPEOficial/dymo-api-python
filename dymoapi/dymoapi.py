import logging
from .utils.basics import DotDict
import os, sys, requests, importlib
from .exceptions import AuthenticationError
from .config import set_base_url, get_base_url
import dymoapi.response_models as response_models
from .services.autoupload import check_for_updates

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class DymoAPI:
    tokens_response = None
    tokens_verified = False    

    def __init__(self, config={}):
        """
        This is the main class to interact with the Dymo API. It should be
        instantiated with the root API key and the API key. The root API key is
        used to fetch the tokens and the API key is used to authenticate the
        requests.

        Args:
            - options (dict, optional): Options to create the DymoAPI instance.
            - options["rootApiKey"] (str, optional): The root API key. Defaults to None.
            - options["apiKey"] (str, optional): The API key. Defaults to None.
            - options["local"] (bool, optional): Whether to use a local server instead of 
                                            the cloud server. Defaults to False.
            - options["serverEmailConfig"] (dict, optional): 
                                        The server email config. Defaults to None.

        Example:
            dymo_api = DymoAPI({
                "rootApiKey": "6bfb7675-6b69-4f8d-9f43-5a6f7f02c6c5",
                "apiKey": "4c8b7675-6b69-4f8d-9f43-5a6f7f02c6c5",
                "local": True
            })
        """
        self.root_api_key = config.get("root_api_key", None)
        self.api_key = config.get("api_key", None)
        self.server_email_config = config.get("server_email_config", None)
        self.local = config.get("local", False)

        set_base_url(self.local)
        self.base_url = get_base_url()
        check_for_updates()
        if self.api_key: self.initialize_tokens()
    
    def _get_function(self, module_name, function_name="main"):
        if module_name == "private" and self.api_key is None: return logging.error("Invalid private token.")
        func = getattr(importlib.import_module(f".branches.{module_name}", package="dymoapi"), function_name)
        if module_name == "private": return lambda *args, **kwargs: DotDict(func(self.api_key, *args, **kwargs))
        return lambda *args, **kwargs: DotDict(func(*args, **kwargs))

    def initialize_tokens(self):
        if DymoAPI.tokens_response and DymoAPI.tokens_verified: return print("[Dymo API] Using cached tokens response.")
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
            DymoAPI.tokens_response = data
            DymoAPI.tokens_verified = True
            print("[Dymo API] Tokens initialized successfully.")
        except (requests.RequestException, AuthenticationError) as e:
            return logging.error(f"Token validation error: {e}")

    def is_valid_data(self, data: response_models.Validator) -> response_models.DataVerifierResponse:
        """
        Validates the given data against the configured validation settings.

        This method requires either the root API key or the API key to be set.
        If neither is set, it will throw an error.

        Args:
            - data (response_models.Validator): The data to be validated.
            - data["email"] (str, optional): Optional email address to be validated.
            - data["phone"] (response_models.PhoneData, optional): Optional phone number data to be validated.
            - data["domain"] (str, optional): Optional domain name to be validated.
            - data["creditCard"] (str or response_models.CreditCardData, optional): Optional credit card number or data to be validated.
            - data["ip"] (str, optional): Optional IP address to be validated.
            - data["wallet"] (str, optional): Optional wallet address to be validated.
            - data["plugins"] (list[response_models.VerifyPlugins], optional): Optional array of verification plugins to be used.

        Returns:
            Promise[response_models.DataVerifierResponse]: A promise that resolves to the response from the server.

        Raises:
            Exception: An error will be thrown if there is an issue with the validation process.

        [Documentation](https://docs.tpeoficial.com/docs/dymo-api/private/data-verifier)
        """
        response = self._get_function("private", "is_valid_data")(data)
        if response.get("ip",{}).get("as"):
            response["ip"]["_as"] = response["ip"]["as"]
            response["ip"]["_class"] = response["ip"]["class"]
            response["ip"].pop("as")
            response["ip"].pop("class")
        return response_models.DataVerifierResponse(**response)
    
    def send_email(self, data: response_models.EmailStatus) -> response_models.SendEmailResponse:
        """
        Sends an email using the configured email client settings.

        This method requires either the root API key or the server email config to be set.
        If neither is set, an error will be thrown.

        Args:
            - data (dict): The email data to be sent.
            - data["from"] (str): The email address from which the email will be sent.
            - data["to"] (str): The email address to which the email will be sent.
            - data["subject"] (str): The subject of the email.
            - data["html"] (str, optional): The HTML content of the email.
            - data["react"] (Object, optional): The React component to be rendered as the email content.
            - data["options"] (dict, optional): Content configuration options.
            - data["options"]["priority"] (str, optional): Email priority (default: "normal").  Allowed values: "high", "normal", "low".
            - data["options"]["waitToResponse"] (bool, optional): Wait until the email is sent (default: True).
            - data["options"]["composeTailwindClasses"] (bool, optional): Whether to compose tailwind classes.
            - data["attachments"] (list[dict], optional): A list of attachments to be included in the email.
            - data["attachments"][i]["filename"] (str): The name of the attached file.
            - data["attachments"][i]["path"] (str, optional): The path or URL of the attached file. Either this or `content` must be provided.
            - data["attachments"][i]["content"] (bytes, optional): The content of the attached file as a Buffer. Either this or `path` must be provided.
            - data["attachments"][i]["cid"] (str, optional): The CID (Content-ID) of the attached file, used for inline images.

        Returns:
            Promise[response_models.EmailStatus]: A promise that resolves to the response from the server.

        Raises:
            Exception: An error will be thrown if there is an issue with the email sending process.

        [Documentation](https://docs.tpeoficial.com/docs/dymo-api/private/sender-send-email/getting-started)

        """
        if not self.server_email_config and not self.root_api_key: return logging.error("You must configure the email client settings.")
        return response_models.DataVerifierResponse(**self._get_function("private", "send_email")({**data, "serverEmailConfig": self.server_email_config}))
    
    def get_random(self, data: response_models.SRNG) -> response_models.SRNGResponse:
        """
        Generates a random number (or numbers) between the provided min and max values.

        This method requires either the root API key or the API key to be set.
        If neither is set, an error will be thrown.

        Args:
            - data (response_models.SRNG): The data for random number generation.
            - data["min"] (int/float): The minimum value of the range.
            - data["max"] (int/float): The maximum value of the range.
            - data["quantity"] (int, optional): The number of random values to generate. Defaults to 1.

        Returns:
            Promise[response_models.SRNGResponse]: A promise that resolves to the response from the server.

        Raises:
            Exception: An error will be thrown if there is an issue with the random number 
                    generation process.
            
        [Documentation](https://docs.tpeoficial.com/docs/dymo-api/private/secure-random-number-generator)

        """
        return response_models.DataVerifierResponse(**self._get_function("private", "get_random")({**data}))

    def get_prayer_times(self, data: response_models.PrayerTimesData) -> response_models.PrayerTimesResponse:
        """
        Retrieves the prayer times for the given location.

        This method requires a latitude and longitude to be provided in the
        data object. If either of these are not provided, an error will be thrown.

        Args:
            - data (response_models.PrayerTimesData): The data for retrieving prayer times.
            - data["lat"] (float): The latitude of the location.
            - data["lon"] (float): The longitude of the location.

        Returns:
            Promise[response_models.PrayerTimesResponse | dict]: A promise that resolves to the 
                                                        response from the server. The response
                                                        can be either a `CountryPrayerTimes` object 
                                                        or a dictionary with an "error" key (if there was a problem).

        Raises:
            Exception: An error will be thrown if there is an issue with the prayer times 
                    retrieval process.

        [Documentation](https://docs.tpeoficial.com/docs/dymo-api/public/prayertimes)
        """
        return response_models.PrayerTimesResponse(**self._get_function("public", "get_prayer_times")(data))

    def satinizer(self, data: response_models.InputSanitizerData) -> response_models.SatinizerResponse:
        """
        Sanitizes the input, replacing any special characters with their HTML entities.

        Args:
            - data (response_models.InputSanitizerData): The data for sanitizing the input.
            - data["input"] (str): The input string to be sanitized.

        Returns:
            Promise[response_models.SatinizerResponse]: A promise that resolves to the 
                                                        response from the server.

        Raises:
            Exception: An error will be thrown if there is an issue with the 
                    sanitization process.

        [Documentation](https://docs.tpeoficial.com/docs/dymo-api/public/input-satinizer)
        """
        return response_models.SatinizerResponse(**self._get_function("public", "satinizer")(data))

    def is_valid_pwd(self, data: response_models.IsValidPwdData) -> response_models.IsValidPwdResponse:
        """
        Validates a password based on the given parameters.

        This method requires the password to be provided in the data object.
        If the password is not provided, an error will be thrown. The method
        will validate the password against the following rules:
            - The password must be at least `data["min"]` characters long (default 8).
            - The password must be at most `data["max"]` characters long (default 32).
            - The password must contain at least one uppercase letter.
            - The password must contain at least one lowercase letter.
            - The password must contain at least one number.
            - The password must contain at least one special character.
            - The password must not contain any of the given banned words.

        Args:
            - data (response_models.IsValidPwdData): The data for password validation.
            - data["min"] (int, optional): Minimum length of the password. Defaults to 8.
            - data["max"] (int, optional): Maximum length of the password. Defaults to 32.
            - data["email"] (str, optional): Optional email associated with the password.
            - data["password"] (str): The password to be validated.
            - data["bannedWords"] (str or list[str], optional): The list of banned words that the password must not contain.

        Returns:
            Promise[response_models.IsValidPwdResponse]: A promise that resolves to the 
                                                            response from the server.

        Raises:
            Exception: An error will be thrown if there is an issue with the password 
                    validation process.

        [Documentation](https://docs.tpeoficial.com/docs/dymo-api/public/password-validator)
        """
        return response_models.IsValidPwdResponse(**self._get_function("public", "is_valid_pwd")(data))

    def new_url_encrypt(self, data) -> response_models.UrlEncryptResponse:
        return response_models.UrlEncryptResponse(**self._get_function("public", "new_url_encrypt")(data))
    
if __name__ == "__main__": sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))