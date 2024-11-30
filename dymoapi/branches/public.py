import re, requests
from urllib.parse import quote
from ..config import BASE_URL, set_base_url
from ..exceptions import APIError, BadRequestError

def get_prayer_times(data):
    if not data.lat or not data.lon: raise BadRequestError("You must provide a latitude and longitude.")
    params = {
        "lat": data.get("lat"),
        "lon": data.get("lon")
    }
    try:
        response = requests.get(f"{BASE_URL}/v1/public/islam/prayertimes", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def satinizer(data):
    try:
        input_value = data.get("input")
        if input_value is None: raise BadRequestError("You must specify at least the input.")
        response = requests.get(f"{BASE_URL}/v1/public/inputSatinizer", params={"input":quote(input_value)})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def is_valid_pwd(data):
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
        response = requests.get(f"{BASE_URL}/v1/public/validPwd", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def new_url_encrypt(url):
    try:
        if url is None or not (url.startswith("https://") or url.startswith("http://")): raise BadRequestError("You must provide a valid url.")
        response = requests.get(f"{BASE_URL}/v1/public/url-encrypt", params={"url": url})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))