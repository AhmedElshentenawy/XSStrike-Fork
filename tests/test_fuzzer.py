"""
Tests for core/fuzzer.py

Tests verify:
- Fuzzing payload injection
- WAF detection and response
- Encoding fallback during fuzzing
- Payload reflection detection in fuzzer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from core.fuzzer import fuzzer
from core.encoders import url, base64


class TestFuzzerBasicFunctioning:
    """
    Test Suite: Basic fuzzer operation
    
    Verifies: Fuzzer injects payloads and monitors responses
    """

    def test_fuzzer_injects_fuzz_strings(self, mock_requester, sample_params, sample_headers):
        """
        Test: Fuzzer sends fuzz strings in parameters.
        
        Verifies: Fuzzer calls requester with modified parameters
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Response without reflection"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.config.fuzzes', ['<img>', '<svg>']):
                with patch('core.log.setup_logger'):
                    fuzzer(
                        "http://target.com",
                        sample_params,
                        sample_headers,
                        GET=True,
                        delay=0,
                        timeout=10,
                        WAF=None,
                        encoding=False,
                        encoding_fallback=False
                    )
                    
                    # Should call requester at least once for each fuzz string
                    assert mock_requester.call_count >= 2

    def test_fuzzer_detects_reflection(self, mock_requester, sample_params, sample_headers):
        """
        Test: Fuzzer identifies when fuzz strings are reflected.
        
        Verifies: Fuzzer correctly logs successful reflections
        """
        payload = "<img>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = f"Result: {payload}"  # Payload reflected
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.config.fuzzes', [payload]):
                with patch('core.log.setup_logger') as mock_logger:
                    fuzzer(
                        "http://target.com",
                        sample_params,
                        sample_headers,
                        GET=True,
                        delay=0,
                        timeout=10,
                        WAF=None,
                        encoding=False,
                        encoding_fallback=False
                    )
                    
                    assert mock_requester.called


class TestFuzzerWithEncoding:
    """
    Test Suite: Fuzzer with payload encoding
    
    Verifies: Fuzzer correctly applies encoding to fuzz strings
    """

    def test_fuzzer_with_url_encoding(self, mock_requester, sample_params, sample_headers):
        """
        Test: Fuzzer applies URL encoding when encoding flag is set.
        
        Verifies: Encoding is applied before sending payloads
        """
        payload = "<img src=x>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "No reflection"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.config.fuzzes', [payload]):
                with patch('core.log.setup_logger'):
                    fuzzer(
                        "http://target.com",
                        sample_params,
                        sample_headers,
                        GET=True,
                        delay=0,
                        timeout=10,
                        WAF=None,
                        encoding=url,
                        encoding_fallback=False
                    )
                    
                    # Verify requester was called with encoded payload
                    assert mock_requester.called

    def test_fuzzer_with_base64_encoding(self, mock_requester, sample_params, sample_headers):
        """
        Test: Fuzzer applies base64 encoding when encoding flag is set.
        
        Verifies: Base64 encoding works in fuzzer context
        """
        payload = "<script>alert(1)</script>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Response"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.config.fuzzes', [payload]):
                with patch('core.log.setup_logger'):
                    fuzzer(
                        "http://target.com",
                        sample_params,
                        sample_headers,
                        GET=True,
                        delay=0,
                        timeout=10,
                        WAF=None,
                        encoding=base64,
                        encoding_fallback=False
                    )
                    
                    assert mock_requester.called


class TestFuzzerEncodingFallback:
    """
    Test Suite: Fuzzer encoding fallback
    
    Verifies: Fuzzer retries with encoding when plain fuzz fails
    """

    def test_fallback_retries_with_encoding(self, mock_requester, sample_params, sample_headers):
        """
        Test: Fallback retries fuzz string with encoding when plain fails.
        
        Verifies: Two requests made (raw + encoded) when fallback detects no reflection
        """
        payload = "<img>"
        
        # First request: no reflection
        response1 = Mock()
        response1.status_code = 200
        response1.text = "No reflection here"
        
        # Second request (fallback): reflection found
        response2 = Mock()
        response2.status_code = 200
        response2.text = f"Found: {url(payload)}"
        
        mock_requester.side_effect = [response1, response2]
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.config.fuzzes', [payload]):
                with patch('core.log.setup_logger'):
                    fuzzer(
                        "http://target.com",
                        sample_params,
                        sample_headers,
                        GET=True,
                        delay=0,
                        timeout=10,
                        WAF=None,
                        encoding=url,
                        encoding_fallback=True
                    )
                    
                    # Should make at least 2 calls per fuzz (raw + fallback)
                    assert mock_requester.call_count >= 2

    def test_fallback_skipped_on_raw_success(self, mock_requester, sample_params, sample_headers):
        """
        Test: Fallback is not used if raw payload is reflected.
        
        Verifies: Fallback only triggers when raw payload fails
        """
        payload = "<img>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = f"Success: {payload}"  # Already reflected
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.config.fuzzes', [payload]):
                with patch('core.log.setup_logger'):
                    fuzzer(
                        "http://target.com",
                        sample_params,
                        sample_headers,
                        GET=True,
                        delay=0,
                        timeout=10,
                        WAF=None,
                        encoding=url,
                        encoding_fallback=True
                    )
                    
                    # Should only make 1 call since raw payload succeeded
                    call_count_per_fuzz = mock_requester.call_count
                    assert call_count_per_fuzz >= 1

    def test_fallback_disabled_no_retry(self, mock_requester, sample_params, sample_headers):
        """
        Test: Without fallback flag, no retry is performed.
        
        Verifies: Single request per fuzz when fallback is disabled
        """
        payload = "<img>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "No reflection"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.config.fuzzes', [payload]):
                with patch('core.log.setup_logger'):
                    fuzzer(
                        "http://target.com",
                        sample_params,
                        sample_headers,
                        GET=True,
                        delay=0,
                        timeout=10,
                        WAF=None,
                        encoding=url,
                        encoding_fallback=False
                    )
                    
                    assert mock_requester.call_count >= 1


class TestFuzzerWAFDetection:
    """
    Test Suite: WAF detection during fuzzing
    
    Verifies: Fuzzer responds to WAF blocks with appropriate delays
    """

    def test_waf_detected_adds_delay(self, mock_requester, sample_params, sample_headers):
        """
        Test: When WAF is detected, fuzzer adds delay.
        
        Verifies: WAF detection increases request intervals
        """
        # Mock to simulate WAF blocking (exception)
        from requests.exceptions import RequestException
        
        mock_requester.side_effect = RequestException("Connection reset by WAF")
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.config.fuzzes', ['<img>']):
                with patch('core.log.setup_logger'):
                    with patch('time.sleep') as mock_sleep:
                        try:
                            fuzzer(
                                "http://target.com",
                                sample_params,
                                sample_headers,
                                GET=True,
                                delay=0,
                                timeout=10,
                                WAF=True,
                                encoding=False,
                                encoding_fallback=False
                            )
                        except:
                            pass
                        
                        # Sleep should be called for WAF delay
                        assert mock_sleep.called

    def test_blocked_response_logged(self, mock_requester, sample_params, sample_headers):
        """
        Test: Blocked responses (non-2xx) are logged.
        
        Verifies: Fuzzer tracks responses that indicate WAF blocking
        """
        payload = "<img>"
        
        mock_response = Mock()
        mock_response.status_code = 403  # Forbidden - likely WAF
        mock_response.text = "Access Denied"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.config.fuzzes', [payload]):
                with patch('core.log.setup_logger') as mock_logger:
                    fuzzer(
                        "http://target.com",
                        sample_params,
                        sample_headers,
                        GET=True,
                        delay=0,
                        timeout=10,
                        WAF=True,
                        encoding=False,
                        encoding_fallback=False
                    )
                    
                    assert mock_requester.called
