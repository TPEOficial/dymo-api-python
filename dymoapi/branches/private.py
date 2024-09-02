import requests
from ..exceptions import APIError, BadRequestError

def is_valid_data(token, data):
    if not any([key in list(data.keys()) for key in ["email", "phone", "domain", "creditCard", "ip"]]): raise BadRequestError("You must provide at least one parameter.")
    try:
        response = requests.post("https://api.tpeoficial.com/v1/private/secure/verify", json=data, headers={"Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))