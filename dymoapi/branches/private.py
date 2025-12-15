import requests
from ..config import get_base_url
from ..utils.decorators import deprecated
from typing import Optional, Dict, Any, List
from ..exceptions import APIError, BadRequestError

@deprecated("is_valid_data_raw")
def is_valid_data(token, data):
    if not any([key in list(data.keys()) for key in ["url", "email", "phone", "domain", "creditCard", "ip", "wallet", "userAgent", "iban"]]): raise BadRequestError("You must provide at least one parameter.")
    try:
        response = requests.post(f"{get_base_url()}/v1/private/secure/verify", json=data, headers={"User-Agent": "DymoAPISDK/1.0.0", "X-Dymo-SDK-Env": "Python", "X-Dymo-SDK-Version" : "0.0.62", "Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def is_valid_data_raw(token, data):
    if not any([key in list(data.keys()) for key in ["url", "email", "phone", "domain", "creditCard", "ip", "wallet", "userAgent", "iban"]]): raise BadRequestError("You must provide at least one parameter.")
    try:
        response = requests.post(f"{get_base_url()}/v1/private/secure/verify", json=data, headers={"User-Agent": "DymoAPISDK/1.0.0", "X-Dymo-SDK-Env": "Python", "X-Dymo-SDK-Version" : "0.0.62", "Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))

def is_valid_email(token: Optional[str], email: str, rules: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
    """
    Validates the given email against the configured deny rules.

    Args:
        token (str | None): Authentication token (required).
        email (str): Email to validate.
        rules (dict | None): Optional rules dict with 'deny' list. Defaults to
            ["FRAUD", "INVALID", "NO_MX_RECORDS", "NO_REPLY_EMAIL"].
            ⚠️ "NO_MX_RECORDS", "HIGH_RISK_SCORE", "NO_GRAVATAR" and "NO_REACHABLE" are PREMIUM.

    Returns:
        bool: True if the email passes all deny rules, False otherwise.

    Raises:
        APIError: If token is None or the request fails.
    """
    if token is None: raise APIError("Invalid private token.")

    if rules is None: rules = {"deny": ["FRAUD", "INVALID", "NO_MX_RECORDS", "NO_REPLY_EMAIL"]}

    plugins = [
        "mxRecords" if "NO_MX_RECORDS" in rules["deny"] else None,
        "reachable" if "NO_REACHABLE" in rules["deny"] else None,
        "riskScore" if "HIGH_RISK_SCORE" in rules["deny"] else None,
        "gravatar" if "NO_GRAVATAR" in rules["deny"] else None
    ]
    plugins = [p for p in plugins if p is not None]

    try:
        resp = requests.post(
            f"{get_base_url()}/v1/private/secure/verify",
            json={"email": email, "plugins": plugins},
            headers={"User-Agent": "DymoAPISDK/1.0.0", "X-Dymo-SDK-Env": "Python", "X-Dymo-SDK-Version" : "0.0.62", "Authorization": token}
        )
        resp.raise_for_status()
        data = resp.json().get("email", {})

        deny = rules.get("deny", [])
        reasons: List[str] = []

        if "INVALID" in deny and not data.get("valid", True):
            return {
                "email": email,
                "allow": False,
                "reasons": ["INVALID"],
                "response": data
            }
        if "FRAUD" in deny and data.get("fraud", False): reasons.append("FRAUD")
        if "PROXIED_EMAIL" in deny and data.get("proxiedEmail", False): reasons.append("PROXIED_EMAIL")
        if "FREE_SUBDOMAIN" in deny and data.get("freeSubdomain", False): reasons.append("FREE_SUBDOMAIN")
        if "PERSONAL_EMAIL" in deny and not data.get("corporate", False): reasons.append("PERSONAL_EMAIL")
        if "CORPORATE_EMAIL" in deny and data.get("corporate", False): reasons.append("CORPORATE_EMAIL")
        if "NO_MX_RECORDS" in deny and len(data.get("plugins", {}).get("mxRecords", [])) == 0: reasons.append("NO_MX_RECORDS")
        if "NO_REPLY_EMAIL" in deny and data.get("noReply", False): reasons.append("NO_REPLY_EMAIL")
        if "ROLE_ACCOUNT" in deny and data.get("plugins", {}).get("roleAccount", False): reasons.append("ROLE_ACCOUNT")
        if "NO_REACHABLE" in deny and not data.get("plugins", {}).get("reachable", True): reasons.append("NO_REACHABLE")
        if "HIGH_RISK_SCORE" in deny and data.get("plugins", {}).get("riskScore", 0) >= 80: reasons.append("HIGH_RISK_SCORE")
        if "NO_GRAVATAR" in deny and isinstance(data.get("plugins", {}).get("gravatarUrl"), str): reasons.append("NO_GRAVATAR")

        return {
            "email": email,
            "allow": len(reasons) == 0,
            "reasons": reasons,
            "response": data
        }

    except requests.RequestException as e: raise APIError(f"[Dymo API] {str(e)}")

def is_valid_ip(token: Optional[str], ip: str, rules: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
    """
    Validates the given IP against the configured deny rules.

    Args:
        token (str | None): Authentication token (required).
        email (str): IP to validate.
        rules (dict | None): Optional rules dict with 'deny' list. Defaults to
            ["FRAUD", "INVALID", "TOR_NETWORK"].
            ⚠️ "TOR_NETWORK" and "HIGH_RISK_SCORE" are PREMIUM.

    Returns:
        bool: True if the IP passes all deny rules, False otherwise.

    Raises:
        APIError: If token is None or the request fails.
    """
    if token is None: raise APIError("Invalid private token.")

    if rules is None: rules = {"deny": ["FRAUD", "INVALID", "TOR_NETWORK"]}

    plugins = [
        "torNetwork" if "TOR_NETWORK" in rules["deny"] else None,
        "riskScore" if "HIGH_RISK_SCORE" in rules["deny"] else None
    ]
    plugins = [p for p in plugins if p is not None]

    try:
        resp = requests.post(
            f"{get_base_url()}/v1/private/secure/verify",
            json={"email": ip, "plugins": plugins},
            headers={"User-Agent": "DymoAPISDK/1.0.0", "X-Dymo-SDK-Env": "Python", "X-Dymo-SDK-Version" : "0.0.62", "Authorization": token}
        )
        resp.raise_for_status()
        data = resp.json().get("ip", {})

        deny = rules.get("deny", [])
        reasons: List[str] = []

        if "INVALID" in deny and not data.get("valid", True):
            return {
                "ip": ip,
                "allow": False,
                "reasons": ["INVALID"],
                "response": data
            }
        if "FRAUD" in deny and data.get("fraud", False): reasons.append("FRAUD")
        if "TOR_NETWORK" in deny and data.get("plugins", {}).get("torNetwork", False): reasons.append("TOR_NETWORK")
        if "HIGH_RISK_SCORE" in deny and data.get("plugins", {}).get("riskScore", 0) >= 80: reasons.append("HIGH_RISK_SCORE")

        # Country block rules.
        for rule in rules["deny"]:
            if rule.startswith("COUNTRY:"):
                block = rule.split(":")[1] # Extract country code.
                if data.get("countryCode") == block: reasons.append(f"COUNTRY:{block}")

        return {
            "ip": ip,
            "allow": len(reasons) == 0,
            "reasons": reasons,
            "response": data
        }

    except requests.RequestException as e: raise APIError(f"[Dymo API] {str(e)}")

def is_valid_phone(token: Optional[str], phone: str, rules: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
    """
    Validates the given phone against the configured deny rules.

    Args:
        token (str | None): Authentication token (required).
        phone (str): Phone to validate.
        rules (dict | None): Optional rules dict with 'deny' list. Defaults to
            ["FRAUD", "INVALID"].
            ⚠️ "HIGH_RISK_SCORE" is PREMIUM.

    Returns:
        bool: True if the phone passes all deny rules, False otherwise.

    Raises:
        APIError: If token is None or the request fails.
    """
    if token is None: raise APIError("Invalid private token.")

    if rules is None: rules = {"deny": ["FRAUD", "INVALID"]}

    plugins = [
        "riskScore" if "HIGH_RISK_SCORE" in rules["deny"] else None
    ]
    plugins = [p for p in plugins if p is not None]

    try:
        resp = requests.post(
            f"{get_base_url()}/v1/private/secure/verify",
            json={"phone": phone, "plugins": plugins},
            headers={"User-Agent": "DymoAPISDK/1.0.0", "X-Dymo-SDK-Env": "Python", "X-Dymo-SDK-Version" : "0.0.62", "Authorization": token}
        )
        resp.raise_for_status()
        data = resp.json().get("phone", {})

        deny = rules.get("deny", [])
        reasons: List[str] = []

        if "INVALID" in deny and not data.get("valid", True):
            return {
                "phone": phone,
                "allow": False,
                "reasons": ["INVALID"],
                "response": data
            }
        if "FRAUD" in deny and data.get("fraud", False): reasons.append("FRAUD")
        if "HIGH_RISK_SCORE" in deny and data.get("plugins", {}).get("riskScore", 0) >= 80: reasons.append("HIGH_RISK_SCORE")

        # Country block rules.
        for rule in rules["deny"]:
            if rule.startswith("COUNTRY:"):
                block = rule.split(":")[1] # Extract country code.
                if data.get("countryCode") == block: reasons.append(f"COUNTRY:{block}")

        return {
            "email": phone,
            "allow": len(reasons) == 0,
            "reasons": reasons,
            "response": data
        }

    except requests.RequestException as e: raise APIError(f"[Dymo API] {str(e)}")

def send_email(token, data):
    if not data.get("from"): raise BadRequestError("You must provide an email address from which the following will be sent.")
    if not data.get("to"): raise BadRequestError("You must provide an email to be sent to.")
    if not data.get("subject"): raise BadRequestError("You must provide a subject for the email to be sent.")
    if not data.get("html"): raise BadRequestError("You must provide HTML.")
    try:
        response = requests.post(f"{get_base_url()}/v1/private/sender/sendEmail", json=data, headers={"User-Agent": "DymoAPISDK/1.0.0", "X-Dymo-SDK-Env": "Python", "X-Dymo-SDK-Version" : "0.0.62", "Authorization": token})
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
        response = requests.post(f"{get_base_url()}/v1/private/srng", json=data, headers={"User-Agent": "DymoAPISDK/1.0.0", "X-Dymo-SDK-Env": "Python", "X-Dymo-SDK-Version" : "0.0.62", "Authorization": token})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))


def extract_with_textly(token: str, data: dict) -> dict:
    if not data.get("data"): raise BadRequestError("No data provided.")
    if not data.get("format"): raise BadRequestError("No format provided.")

    try:
        response = requests.post(
            f"{get_base_url()}/private/textly/extract",
            json=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "DymoAPISDK/1.0.0",
                "Authorization": token
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e: raise APIError(str(e))