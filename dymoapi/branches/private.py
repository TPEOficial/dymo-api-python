import requests
from ..exceptions import APIError, BadRequestError

def is_valid_data(token, data):
    if not {"email", "phone", "domain", "credit_card", "ip"}.intersection({key for key in vars(data) if getattr(data, key) is not None}): raise BadRequestError("You must provide at least one parameter.")
    try:
        response = requests.post("https://api.tpeoficial.com/v1/private/secure/verify", json=data.__dict__, headers={"Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))