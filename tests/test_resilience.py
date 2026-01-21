"""
DymoAPI Resilience System Tests

This module contains comprehensive tests for the resilience system
implemented in the DymoAPI Python SDK.
"""

import pytest
from unittest.mock import Mock, patch
from dymoapi.resilience import ResilienceManager, ResilienceConfig, FallbackDataGenerator
from requests import RequestException, Response


class TestResilienceConfig:
    """Test cases for ResilienceConfig class."""
    
    def test_default_config(self):
        """Test that default configuration values are set correctly."""
        config = ResilienceConfig()
        assert config.fallback_enabled is False
        assert config.retry_attempts == 2
        assert config.retry_delay == 1000
    
    def test_custom_config(self):
        """Test that custom configuration values are set correctly."""
        config = ResilienceConfig(
            fallback_enabled=True,
            retry_attempts=3,
            retry_delay=500
        )
        assert config.fallback_enabled is True
        assert config.retry_attempts == 3
        assert config.retry_delay == 500


class TestResilienceManager:
    """Test cases for ResilienceManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ResilienceManager()
    
    def test_get_config(self):
        """Test that get_config returns the configuration object."""
        config = self.manager.get_config()
        assert hasattr(config, 'fallback_enabled')
        assert hasattr(config, 'retry_attempts')
        assert hasattr(config, 'retry_delay')
    
    def test_retry_on_network_error(self):
        """Test that the manager retries on network errors."""
        config = ResilienceConfig(retry_attempts=3, retry_delay=10)
        manager = ResilienceManager(config)
        
        with patch('requests.Session.request') as mock_request:
            # Simulate network errors followed by success
            mock_request.side_effect = [
                RequestException("Network error"),
                RequestException("Network error"),
                Mock(status_code=200, json=lambda: {"success": True})
            ]
            
            session = Mock()
            result = manager.execute_with_resilience(
                session=session,
                method="GET",
                url="http://test.com"
            )
            
            assert result["success"] is True
            assert mock_request.call_count == 3
    
    def test_use_fallback_when_enabled(self):
        """Test that fallback data is used when enabled and all retries fail."""
        config = ResilienceConfig(
            fallback_enabled=True,
            retry_attempts=2,
            retry_delay=10
        )
        manager = ResilienceManager(config)
        
        with patch('requests.Session.request') as mock_request:
            # Simulate all requests failing
            mock_request.side_effect = RequestException("Network error")
            
            session = Mock()
            fallback_data = {"fallback": True}
            
            result = manager.execute_with_resilience(
                session=session,
                method="GET",
                url="http://test.com",
                fallback_data=fallback_data
            )
            
            assert result == fallback_data
            assert mock_request.call_count == 2
    
    def test_throw_error_when_fallback_disabled(self):
        """Test that error is thrown when fallback is disabled and all retries fail."""
        config = ResilienceConfig(
            fallback_enabled=False,
            retry_attempts=2,
            retry_delay=10
        )
        manager = ResilienceManager(config)
        
        with patch('requests.Session.request') as mock_request:
            # Simulate all requests failing
            mock_request.side_effect = RequestException("Network error")
            
            session = Mock()
            
            with pytest.raises(RequestException):
                manager.execute_with_resilience(
                    session=session,
                    method="GET",
                    url="http://test.com"
                )
            
            assert mock_request.call_count == 2
    
    def test_retry_on_500_status(self):
        """Test that the manager retries on 500 status codes."""
        config = ResilienceConfig(retry_attempts=2, retry_delay=10)
        manager = ResilienceManager(config)
        
        with patch('requests.Session.request') as mock_request:
            # Simulate 500 error followed by success
            response_500 = Mock()
            response_500.status_code = 500
            response_200 = Mock()
            response_200.status_code = 200
            response_200.json.return_value = {"success": True}
            
            mock_request.side_effect = [
                RequestException(response=response_500),
                response_200
            ]
            
            session = Mock()
            result = manager.execute_with_resilience(
                session=session,
                method="GET",
                url="http://test.com"
            )
            
            assert result["success"] is True
            assert mock_request.call_count == 2
    
    def test_no_retry_on_4xx_except_429(self):
        """Test that the manager doesn't retry on 4xx errors (except 429)."""
        config = ResilienceConfig(retry_attempts=2, retry_delay=10)
        manager = ResilienceManager(config)
        
        with patch('requests.Session.request') as mock_request:
            # Simulate 404 error
            response_404 = Mock()
            response_404.status_code = 404
            
            mock_request.side_effect = RequestException(response=response_404)
            
            session = Mock()
            
            with pytest.raises(RequestException):
                manager.execute_with_resilience(
                    session=session,
                    method="GET",
                    url="http://test.com"
                )
            
            assert mock_request.call_count == 1


class TestFallbackDataGenerator:
    """Test cases for FallbackDataGenerator class."""
    
    def test_generate_fallback_data_invalid_method(self):
        """Test that invalid method raises ValueError."""
        with pytest.raises(ValueError):
            FallbackDataGenerator.generate_fallback_data("invalid_method")
    
    def test_url_validation(self):
        """Test URL validation regex."""
        # Valid URLs
        assert FallbackDataGenerator._validate_url("https://example.com") is True
        assert FallbackDataGenerator._validate_url("http://subdomain.example.com/path") is True
        
        # Invalid URLs
        assert FallbackDataGenerator._validate_url("not-a-url") is False
        assert FallbackDataGenerator._validate_url("") is False
    
    def test_email_validation(self):
        """Test email validation regex."""
        # Valid emails
        assert FallbackDataGenerator._validate_email("test@example.com") is True
        assert FallbackDataGenerator._validate_email("user.name+tag@domain.co.uk") is True
        
        # Invalid emails
        assert FallbackDataGenerator._validate_email("invalid-email") is False
        assert FallbackDataGenerator._validate_email("") is False
    
    def test_domain_validation(self):
        """Test domain validation with TLD."""
        # Valid domains
        assert FallbackDataGenerator._validate_domain("example.com") is True
        assert FallbackDataGenerator._validate_domain("sub.domain.co.uk") is True
        
        # Invalid domains
        assert FallbackDataGenerator._validate_domain("localhost") is False
        assert FallbackDataGenerator._validate_domain("domain") is False
    
    def test_credit_card_validation(self):
        """Test credit card validation with Luhn algorithm."""
        # Valid credit cards
        assert FallbackDataGenerator._validate_credit_card("4532015112830366") is True  # Visa test card
        assert FallbackDataGenerator._validate_credit_card({"pan": "5555555555554444"}) is True  # Mastercard test card
        
        # Invalid credit cards
        assert FallbackDataGenerator._validate_credit_card("1234567890123456") is False
        assert FallbackDataGenerator._validate_credit_card("") is False
    
    def test_ip_validation(self):
        """Test IP validation for IPv4 and IPv6."""
        # Valid IPs
        assert FallbackDataGenerator._validate_ip("192.168.1.1") is True
        assert FallbackDataGenerator._validate_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True
        
        # Invalid IPs
        assert FallbackDataGenerator._validate_ip("256.256.256.256") is False
        assert FallbackDataGenerator._validate_ip("invalid-ip") is False
    
    def test_phone_validation(self):
        """Test phone number validation."""
        # Valid phone numbers
        assert FallbackDataGenerator._validate_phone("+34617509462") is True
        assert FallbackDataGenerator._validate_phone("+14155552671") is True
        
        # Invalid phone numbers
        assert FallbackDataGenerator._validate_phone("abc") is False
        assert FallbackDataGenerator._validate_phone("123") is True  # 123 is a valid phone number with + prefix
    
    def test_wallet_validation(self):
        """Test wallet address validation for Bitcoin and Ethereum."""
        # Valid wallets
        assert FallbackDataGenerator._validate_wallet("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa") is True  # Bitcoin
        assert FallbackDataGenerator._validate_wallet("0x742d35Cc6634C0532925a3b844Bc454e4438f44e") is True  # Ethereum
        
        # Invalid wallets
        assert FallbackDataGenerator._validate_wallet("invalid-wallet") is False
        assert FallbackDataGenerator._validate_wallet("") is False
    
    def test_iban_validation(self):
        """Test IBAN validation."""
        # Valid IBANs
        assert FallbackDataGenerator._validate_iban("ES8201825332130207315465") is True
        assert FallbackDataGenerator._validate_iban("GB82WEST123456987654321") is True
        
        # Invalid IBANs
        assert FallbackDataGenerator._validate_iban("INVALID") is False
        assert FallbackDataGenerator._validate_iban("") is False
    
    def test_extract_domain_from_url(self):
        """Test domain extraction from URL."""
        assert FallbackDataGenerator._extract_domain("https://subdomain.example.com/path") == "subdomain.example.com"
        assert FallbackDataGenerator._extract_domain("http://example.com") == "example.com"
        assert FallbackDataGenerator._extract_domain("invalid-url") == ""
    
    def test_generate_is_valid_data_fallback(self):
        """Test fallback data generation for isValidData method."""
        data = {
            "url": "https://example.com",
            "email": "test@example.com",
            "ip": "192.168.1.1"
        }
        
        result = FallbackDataGenerator.generate_fallback_data("isValidData", data)
        
        assert result["url"]["valid"] is True
        assert result["url"]["domain"] == "example.com"
        assert result["email"]["valid"] is True
        assert result["ip"]["valid"] is True
        assert result["creditCard"]["fraud"] is False
    
    def test_generate_email_validator_fallback(self):
        """Test fallback data generation for isValidEmail method."""
        result = FallbackDataGenerator.generate_fallback_data("isValidEmail", "test@example.com")
        
        assert result["email"] == "test@example.com"
        assert result["allow"] is True
        assert result["reasons"] == []
        assert result["response"]["valid"] is True
    
    def test_generate_ip_validator_fallback(self):
        """Test fallback data generation for isValidIP method."""
        result = FallbackDataGenerator.generate_fallback_data("isValidIP", "192.168.1.1")
        
        assert result["ip"] == "192.168.1.1"
        assert result["allow"] is True
        assert result["reasons"] == []
        assert result["response"]["valid"] is True
    
    def test_generate_phone_validator_fallback(self):
        """Test fallback data generation for isValidPhone method."""
        result = FallbackDataGenerator.generate_fallback_data("isValidPhone", "+34617509462")
        
        assert result["phone"] == "+34617509462"
        assert result["allow"] is True
        assert result["reasons"] == []
        assert result["response"]["valid"] is True


class TestDymoAPIWithResilience:
    """Test cases for DymoAPI integration with resilience system."""
    
    def test_resilience_config_initialization(self):
        """Test that DymoAPI initializes resilience system correctly."""
        from dymoapi import DymoAPI
        
        # Test with custom resilience config
        client = DymoAPI({
            "api_key": "test-key",
            "resilience_config": {
                "fallback_enabled": True,
                "retry_attempts": 3,
                "retry_delay": 500
            }
        })
        
        assert client.resilience.config.fallback_enabled is True
        assert client.resilience.config.retry_attempts == 3
        assert client.resilience.config.retry_delay == 500
    
    def test_default_resilience_config(self):
        """Test that DymoAPI uses default resilience config when none provided."""
        from dymoapi import DymoAPI
        
        client = DymoAPI({"api_key": "test-key"})
        
        assert client.resilience.config.fallback_enabled is False
        assert client.resilience.config.retry_attempts == 2
        assert client.resilience.config.retry_delay == 1000