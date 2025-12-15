import re, requests
from urllib.parse import quote
from ..config import get_base_url
from ..utils.decorators import deprecated
from ..exceptions import APIError, BadRequestError

headers = {"User-Agent": "DymoAPISDK/1.0.0", "X-Dymo-SDK-Env": "Python", "X-Dymo-SDK-Version" : "0.0.62"}

def get_prayer_times(data):
    """
    Gets the prayer times for a given latitude and longitude.

    Args:
        data (dict): Data containing the latitude and longitude.

    Returns:
        dict: Prayer times.

    Raises:
        BadRequestError: If the input is not provided.
        APIError: If the request fails.
    """
    if not data.lat or not data.lon: raise BadRequestError("You must provide a latitude and longitude.")
    params = {
        "lat": data.get("lat"),
        "lon": data.get("lon")
    }
    try:
        response = requests.get(f"{get_base_url()}/v1/public/islam/prayertimes", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def satinize(input_value):
    """
    Sanitizes the given input according to the Dymo API standard.

    Args:
        data (dict): Data containing the input to sanitize.

    Returns:
        dict: Sanitized input.

    Raises:
        BadRequestError: If the input is not provided.
        APIError: If the request fails.
    """
    try:
        if input_value is None: raise BadRequestError("You must specify at least the input.")
        response = requests.get(f"{get_base_url()}/v1/public/inputSatinizer", params={"input": quote(input_value)}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

@deprecated("satinize")
def satinizer(input_value):
    """
    Sanitizes the given input according to the Dymo API standard.

    Args:
        data (dict): Data containing the input to sanitize.

    Returns:
        dict: Sanitized input.

    Raises:
        BadRequestError: If the input is not provided.
        APIError: If the request fails.
    """
    try:
        if input is None: raise BadRequestError("You must specify at least the input.")
        response = requests.get(f"{get_base_url()}/v1/public/inputSatinizer", params={"input": quote(input_value)}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def satinize(input_value):
    """
    Sanitizes the given input according to the Dymo API standard.

    Args:
        input (str): The input to sanitize.

    Returns:
        dict: Sanitized input.

    Raises:
        BadRequestError: If the input is not provided.
        APIError: If the request fails.
    """
    try:
        if input_value is None: raise BadRequestError("You must specify at least the input.")
        response = requests.get(f"{get_base_url()}/v1/public/inputSatinizer", params={"input":quote(input_value)}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def is_valid_pwd(data):
    """
    Validates the given password against the configured deny rules.

    Args:
        data (dict): Data containing the password to validate, optionally an email address, a list of banned words and a minimum and maximum length.

    Returns:
        dict: Validation result.

    Raises:
        BadRequestError: If the input is not provided or is invalid.
        APIError: If the request fails.
    """
    try:
        email = data.get("email")
        password = data.get("password")
        banned_words = data.get("bannedWords")
        min_length = data.get("min")
        max_length = data.get("max")
        if password is None: raise BadRequestError("You must specify at least the password.")
        params = {"password": quote(password)}
        if email:
            if not re.match(r"^[a-zA-Z0-9._\-+]+@?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$", email): raise BadRequestError("If you provide an email address it must be valid.")
            params["email"] = quote(email)
        if banned_words:
            if isinstance(banned_words, str):
                banned_words = banned_words.strip("[]").split(",")  # Eliminar los corchetes y dividir por comas
                banned_words = [word.strip() for word in banned_words]  # Eliminar espacios alrededor de cada palabra
            if not isinstance(banned_words, list) or len(banned_words) > 10: raise BadRequestError("If you provide a list of banned words; the list may not exceed 10 words and must be of array type.")
            if not all(isinstance(word, str) for word in banned_words) or len(set(banned_words)) != len(banned_words): raise BadRequestError("If you provide a list of banned words; all elements must be non-repeated strings.")
            params["bannedWords"] = banned_words
        if min_length is not None:
            if not isinstance(min_length, int) or min_length < 8 or min_length > 32: raise BadRequestError("If you provide a minimum it must be valid.")
            params["min"] = min_length
        if max_length is not None:
            if not isinstance(max_length, int) or max_length < 32 or max_length > 100: raise BadRequestError("If you provide a maximum it must be valid.")
            params["max"] = max_length
        response = requests.get(f"{get_base_url()}/v1/public/validPwd", params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def new_url_encrypt(url):
    """
    Encrypts the given URL.

    Args:
        url (str): The URL to encrypt.

    Returns:
        dict: Encrypted URL.

    Raises:
        BadRequestError: If the input is not provided or is invalid.
        APIError: If the request fails.
    """
    try:
        if url is None or not (url.startswith("https://") or url.startswith("http://")): raise BadRequestError("You must provide a valid url.")
        response = requests.get(f"{get_base_url()}/v1/public/url-encrypt", params={"url": url}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))