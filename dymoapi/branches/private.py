import requests
from ..exceptions import APIError, BadRequestError

def is_valid_data(token, data):
    if not any([key in list(data.keys()) for key in ["email", "phone", "domain", "creditCard", "ip"]]): raise BadRequestError("You must provide at least one parameter.")
    try:
        response = requests.post("https://api.tpeoficial.com/v1/private/secure/verify", json=data, headers={"Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def send_email(token, data):
    if not data.get("from"): raise BadRequestError("You must provide an email address from which the following will be sent.")
    if not data.get("to"): raise BadRequestError("You must provide an email to be sent to.")
    if not data.get("subject"): raise BadRequestError("You must provide a subject for the email to be sent.")
    if not data.get("html"): raise BadRequestError("You must provide HTML.")
    try:
        response = requests.post("https://api.tpeoficial.com/v1/private/sender/sendEmail", json=data, headers={"Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))