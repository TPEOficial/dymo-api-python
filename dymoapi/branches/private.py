import requests
from ..config import BASE_URL, set_base_url
from ..exceptions import APIError, BadRequestError

def is_valid_data(token, data):
    if not any([key in list(data.keys()) for key in ["email", "phone", "domain", "creditCard", "ip", "wallet"]]): raise BadRequestError("You must provide at least one parameter.")
    try:
        response = requests.post(f"{BASE_URL}/v1/private/secure/verify", json=data, headers={"Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def send_email(token, data):
    if not data.get("from"): raise BadRequestError("You must provide an email address from which the following will be sent.")
    if not data.get("to"): raise BadRequestError("You must provide an email to be sent to.")
    if not data.get("subject"): raise BadRequestError("You must provide a subject for the email to be sent.")
    if not data.get("html"): raise BadRequestError("You must provide HTML.")
    try:
        response = requests.post(f"{BASE_URL}/v1/private/sender/sendEmail", json=data, headers={"Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def get_random(token, data):
    if not data.get("from"): raise BadRequestError("You must provide an email address from which the following will be sent.")
    if not data.get("to"): raise BadRequestError("You must provide an email to be sent to.")
    if not data.get("subject"): raise BadRequestError("You must provide a subject for the email to be sent.")
    if not data.get("html"): raise BadRequestError("You must provide HTML.")

    if not data.min or not data.max: raise BadRequestError("Both 'min' and 'max' parameters must be defined.")
    if (data.min >= data.max): raise BadRequestError("'min' must be less than 'max'.")
    if data.min < -1000000000 or data.min > 1000000000: raise BadRequestError("'min' must be an integer in the interval [-1000000000}, 1000000000].")
    if data.max < -1000000000 or data.max > 1000000000: raise BadRequestError("'max' must be an integer in the interval [-1000000000}, 1000000000].")
    try:
        response = requests.post(f"{BASE_URL}/v1/private/srng", json=data, headers={"Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))