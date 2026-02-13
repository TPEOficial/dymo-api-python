import re
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

class FallbackDataGenerator:
    @staticmethod
    def generate_fallback_data(method: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates fallback data for various validation methods.
        
        Args:
            method: The method name (isValidData, isValidEmail, etc.)
            input_data: Optional input data to use for validation
            
        Returns:
            Dictionary with fallback data structure matching the method
        """
        if method == "isValidData" or method == "isValidDataRaw": return FallbackDataGenerator._generate_data_validation_analysis(input_data)
        elif method == "isValidEmail": return FallbackDataGenerator._generate_email_validator_response(input_data)
        elif method == "isValidIP": return FallbackDataGenerator._generate_ip_validator_response(input_data)
        elif method == "isValidPhone": return FallbackDataGenerator._generate_phone_validator_response(input_data)
        elif method == "sendEmail": return FallbackDataGenerator._generate_email_status()
        elif method == "getRandom": return FallbackDataGenerator._generate_srng_summary(input_data)
        elif method == "extractWithTextly": return FallbackDataGenerator._generate_extract_with_textly(input_data)
        elif method == "getPrayerTimes": return FallbackDataGenerator._generate_prayer_times(input_data)
        elif method == "satinize" or method == "satinizer": return FallbackDataGenerator._generate_satinized_input_analysis(input_data)
        elif method == "isValidPwd": return FallbackDataGenerator._generate_password_validation_result(input_data)
        else: raise ValueError(f"Unknown method for fallback: {method}")
    
    @staticmethod
    def _validate_url(url: Optional[str]) -> bool:
        """Validates URL using regex."""
        if not url: return False
        url_regex = r'^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return bool(re.match(url_regex, url))
    
    @staticmethod
    def _validate_email(email: Optional[str]) -> bool:
        """Validates email using regex."""
        if not email: return False
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return bool(re.match(email_regex, email))
    
    @staticmethod
    def _validate_domain(domain: Optional[str]) -> bool:
        """Validates domain with TLD validation."""
        if not domain: return False
        domain_regex = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9])*$'
        if not re.match(domain_regex, domain): return False
        # Validate that it has a TLD (last part with content)
        parts = domain.split('.')
        return len(parts) >= 2 and len(parts[-1]) > 0
    
    @staticmethod
    def _validate_credit_card(credit_card: Optional[Union[str, Dict[str, Any]]]) -> bool:
        """Validates credit card using Luhn algorithm."""
        if not credit_card: return False
        
        card_number = credit_card if isinstance(credit_card, str) else credit_card.get('pan', '')
        if not card_number: return False
            
        # Basic regex validation
        card_regex = r'^\d{13,19}$'
        if not re.match(card_regex, card_number.replace(' ', '')): return False
        
        # Luhn algorithm
        digits = [int(d) for d in card_number.replace(' ', '')]
        total = 0
        is_even = False
        
        for digit in reversed(digits):
            if is_even:
                digit *= 2
                if digit > 9: digit -= 9
            total += digit
            is_even = not is_even
            
        return total % 10 == 0
    
    @staticmethod
    def _validate_ip(ip: Optional[str]) -> bool:
        """Validates IPv4 and IPv6 addresses."""
        if not ip: return False
        
        # IPv4 regex
        ipv4_regex = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        # IPv6 regex (simplified)
        ipv6_regex = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        
        return bool(re.match(ipv4_regex, ip)) or bool(re.match(ipv6_regex, ip))
    
    @staticmethod
    def _validate_phone(phone: Optional[Union[str, Dict[str, Any]]]) -> bool:
        """Validates international phone numbers."""
        if not phone: return False
        
        phone_number = phone if isinstance(phone, str) else phone.get('phone', '')
        if not phone_number: return False
            
        phone_regex = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(phone_regex, re.sub(r'[^\d+]', '', phone_number)))
    
    @staticmethod
    def _validate_wallet(wallet: Optional[str]) -> bool:
        """Validates Bitcoin and Ethereum addresses."""
        if not wallet: return False
        
        # Bitcoin address regex
        bitcoin_regex = r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'
        # Ethereum address regex
        ethereum_regex = r'^0x[a-fA-F0-9]{40}$'
        
        return bool(re.match(bitcoin_regex, wallet)) or bool(re.match(ethereum_regex, wallet))
    
    @staticmethod
    def _validate_iban(iban: Optional[str]) -> bool:
        """Validates IBAN using regex."""
        if not iban: return False
        
        iban_regex = r'^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$'
        return bool(re.match(iban_regex, iban.replace(' ', '').upper()))
    
    @staticmethod
    def _extract_domain(url: Optional[str]) -> str:
        """Extracts domain from URL."""
        if not url: return ""
        try: return urlparse(url).hostname or ""
        except Exception: return ""
    
    @staticmethod
    def _generate_data_validation_analysis(input_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates fallback data for isValidData method."""
        url = input_data.get('url') if input_data else None
        domain = input_data.get('domain') if input_data else None
        credit_card = input_data.get('creditCard') if input_data else None
        ip = input_data.get('ip') if input_data else None
        wallet = input_data.get('wallet') if input_data else None
        user_agent = input_data.get('userAgent') if input_data else None
        iban = input_data.get('iban') if input_data else None
        
        return {
            "url": {
                "valid": FallbackDataGenerator._validate_url(url),
                "fraud": False,
                "freeSubdomain": False,
                "customTLD": False,
                "url": url or "",
                "domain": FallbackDataGenerator._extract_domain(url),
                "plugins": FallbackDataGenerator._generate_default_plugins()
            },
            "email": FallbackDataGenerator._generate_email_data_analysis(input_data.get('email') if input_data else None),
            "phone": FallbackDataGenerator._generate_phone_data_analysis(input_data.get('phone') if input_data else None),
            "domain": {
                "valid": FallbackDataGenerator._validate_domain(domain),
                "fraud": False,
                "freeSubdomain": False,
                "customTLD": False,
                "domain": domain or "",
                "plugins": FallbackDataGenerator._generate_default_plugins()
            },
            "creditCard": {
                "valid": FallbackDataGenerator._validate_credit_card(credit_card),
                "fraud": False,
                "test": False,
                "type": "unknown",
                "creditCard": credit_card if isinstance(credit_card, str) else credit_card.get('pan', '') if credit_card else "",
                "plugins": {"blocklist": False, "riskScore": 0}
            },
            "ip": FallbackDataGenerator._generate_ip_data_analysis(ip),
            "wallet": {
                "valid": FallbackDataGenerator._validate_wallet(wallet),
                "fraud": False,
                "wallet": wallet or "",
                "type": "unknown",
                "plugins": {"blocklist": False, "riskScore": 0, "torNetwork": False}
            },
            "userAgent": {
                "valid": True,
                "fraud": False,
                "userAgent": user_agent or "",
                "bot": True,
                "device": {"type": "unknown", "brand": "unknown"},
                "plugins": {"blocklist": False, "riskScore": 0}
            },
            "iban": {
                "valid": FallbackDataGenerator._validate_iban(iban),
                "fraud": False,
                "iban": iban or "",
                "plugins": {"blocklist": False, "riskScore": 0}
            }
        }
    
    @staticmethod
    def _generate_email_validator_response(input_data: Optional[str]) -> Dict[str, Any]:
        """Generates fallback data for isValidEmail method."""
        email = input_data if isinstance(input_data, str) else input_data.get('email', '') if input_data else ''
        
        return {
            "email": email,
            "allow": FallbackDataGenerator._validate_email(email),
            "reasons": [] if FallbackDataGenerator._validate_email(email) else ["INVALID"],
            "response": FallbackDataGenerator._generate_email_data_analysis(email)
        }
    
    @staticmethod
    def _generate_email_data_analysis(email: Optional[str]) -> Dict[str, Any]:
        """Generates email analysis data."""
        return {
            "valid": FallbackDataGenerator._validate_email(email),
            "fraud": False,
            "proxiedEmail": False,
            "freeSubdomain": False,
            "corporate": False,
            "email": email or "",
            "realUser": "",
            "didYouMean": None,
            "noReply": False,
            "customTLD": False,
            "domain": "",
            "roleAccount": False,
            "plugins": FallbackDataGenerator._generate_email_plugins()
        }
    
    @staticmethod
    def _generate_ip_validator_response(input_data: Optional[str]) -> Dict[str, Any]:
        """Generates fallback data for isValidIP method."""
        ip = input_data if isinstance(input_data, str) else input_data.get('ip', '') if input_data else ''
        
        return {
            "ip": ip,
            "allow": FallbackDataGenerator._validate_ip(ip),
            "reasons": [] if FallbackDataGenerator._validate_ip(ip) else ["INVALID"],
            "response": FallbackDataGenerator._generate_ip_data_analysis(ip)
        }
    
    @staticmethod
    def _generate_ip_data_analysis(ip: Optional[str]) -> Dict[str, Any]:
        """Generates IP analysis data."""
        is_valid = FallbackDataGenerator._validate_ip(ip)
        
        return {
            "valid": is_valid,
            "type": "IPv4" if is_valid else "Invalid",
            "class": "A" if is_valid else "Unknown",
            "fraud": False,
            "ip": ip or "",
            "continent": "",
            "continentCode": "",
            "country": "",
            "countryCode": "",
            "region": "",
            "regionName": "",
            "city": "",
            "district": "",
            "zipCode": "",
            "lat": 0,
            "lon": 0,
            "timezone": "",
            "offset": 0,
            "currency": "",
            "isp": "",
            "org": "",
            "as": "",
            "asname": "",
            "mobile": False,
            "proxy": True,
            "hosting": False,
            "plugins": {"blocklist": False, "riskScore": 0}
        }
    
    @staticmethod
    def _generate_phone_validator_response(input_data: Optional[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """Generates fallback data for isValidPhone method."""
        phone = input_data if isinstance(input_data, str) else input_data.get('phone', '') if input_data else ''
        
        return {
            "phone": phone,
            "allow": FallbackDataGenerator._validate_phone(phone),
            "reasons": [] if FallbackDataGenerator._validate_phone(phone) else ["INVALID"],
            "response": FallbackDataGenerator._generate_phone_data_analysis(phone)
        }
    
    @staticmethod
    def _generate_phone_data_analysis(phone: Optional[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """Generates phone analysis data."""
        phone_number = phone if isinstance(phone, str) else phone.get('phone', '') if phone else ''
        is_valid = FallbackDataGenerator._validate_phone(phone_number)
        
        return {
            "valid": is_valid,
            "fraud": False,
            "phone": phone_number,
            "prefix": "",
            "number": "",
            "lineType": "Unknown",
            "carrierInfo": {
                "carrierName": "",
                "accuracy": 0,
                "carrierCountry": "",
                "carrierCountryCode": ""
            },
            "country": "",
            "countryCode": "",
            "plugins": {"blocklist": False, "riskScore": 0}
        }
    
    @staticmethod
    def _generate_email_status() -> Dict[str, Any]:
        """Generates fallback data for sendEmail method."""
        return {
            "status": False,
            "error": "API unavailable - using fallback response"
        }
    
    @staticmethod
    def _generate_srng_summary(input_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates fallback data for getRandom method."""
        quantity = input_data.get('quantity', 1) if input_data else 1
        values = [{"integer": 0, "float": 0.0} for _ in range(quantity)]
        
        return {
            "values": values,
            "executionTime": 0
        }
    
    @staticmethod
    def _generate_extract_with_textly(input_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates fallback data for extractWithTextly method."""
        return {
            "data": input_data.get('data', '') if input_data else '',
            "extracted": {},
            "error": "API unavailable - using fallback response"
        }
    
    @staticmethod
    def _generate_prayer_times(input_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates fallback data for getPrayerTimes method."""
        return {
            "error": "API unavailable - using fallback response"
        }
    
    @staticmethod
    def _generate_satinized_input_analysis(input_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates fallback data for satinize method."""
        return {
            "input": input_data.get('input', '') if input_data else '',
            "formats": {
                "ascii": False,
                "bitcoinAddress": False,
                "cLikeIdentifier": False,
                "coordinates": False,
                "crediCard": False,
                "date": False,
                "discordUsername": False,
                "doi": False,
                "domain": False,
                "e164Phone": False,
                "email": False,
                "emoji": False,
                "hanUnification": False,
                "hashtag": False,
                "hyphenWordBreak": False,
                "ipv6": False,
                "ip": False,
                "jiraTicket": False,
                "macAddress": False,
                "name": False,
                "number": False,
                "panFromGstin": False,
                "password": False,
                "port": False,
                "tel": False,
                "text": False,
                "semver": False,
                "ssn": False,
                "uuid": False,
                "url": False,
                "urlSlug": False,
                "username": False
            },
            "includes": {
                "spaces": False,
                "hasSql": False,
                "hasNoSql": False,
                "letters": False,
                "uppercase": False,
                "lowercase": False,
                "symbols": False,
                "digits": False
            }
        }
    
    @staticmethod
    def _generate_password_validation_result(input_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates fallback data for isValidPwd method."""
        return {
            "valid": False,
            "password": input_data.get('password', '') if input_data else '',
            "details": [
                {
                    "validation": "length",
                    "message": "API unavailable - using fallback response"
                }
            ]
        }
    
    @staticmethod
    def _generate_default_plugins() -> Dict[str, Any]:
        """Generates default plugin responses."""
        return {
            "blocklist": False,
            "compromiseDetector": False,
            "mxRecords": [],
            "nsfw": False,
            "reputation": "unknown",
            "riskScore": 0,
            "torNetwork": False,
            "typosquatting": 0,
            "urlShortener": False
        }
    
    @staticmethod
    def _generate_email_plugins() -> Dict[str, Any]:
        """Generates email-specific plugin responses."""
        return {
            "blocklist": False,
            "compromiseDetector": False,
            "mxRecords": [],
            "nsfw": False,
            "reputation": "unknown",
            "riskScore": 0,
            "socialFootprint": {
                "totalChecked": 0,
                "platforms": []
            },
            "torNetwork": False,
            "typosquatting": 0,
            "urlShortener": False,
            "gravatarUrl": None
        }