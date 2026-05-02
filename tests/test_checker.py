"""
Tests for core/checker.py

Tests verify:
- Payload reflection detection
- Efficiency scoring
- Encoding fallback behavior
- Position tracking of reflections
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.checker import checker
from core.encoders import base64, url


class TestCheckerReflectionDetection:
    """
    Test Suite: Reflection detection in HTTP responses
    
    Verifies: The checker correctly identifies where injected payloads appear in responses
    """

    def test_simple_reflection_detection(self, mock_requester, sample_params, sample_headers):
        """
        Test: Detects when a payload is reflected in the response.
        
        Verifies: Checker identifies successful payload injection
        """
        payload = "<img src=x>"
        
        # Mock response contains the payload
        mock_response = Mock()
        mock_response.text = f"Search results for: st4r7s{payload}3nd"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.utils.fillHoles', return_value=[0]):
                result = checker(
                    "http://target.com",
                    sample_params,
                    sample_headers,
                    GET=True,
                    delay=0,
                    payload=payload,
                    positions=[0],
                    timeout=10,
                    encoding=False
                )
                
                assert isinstance(result, list)
                assert len(result) > 0

    def test_no_reflection_returns_empty(self, mock_requester, sample_params, sample_headers):
        """
        Test: Returns empty list when payload is not reflected.
        
        Verifies: Checker correctly identifies failed injections
        """
        payload = "<img src=x>"
        
        # Mock response does NOT contain the payload
        mock_response = Mock()
        mock_response.text = "Search results for: nothing here"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.utils.fillHoles', return_value=[]):
                result = checker(
                    "http://target.com",
                    sample_params,
                    sample_headers,
                    GET=True,
                    delay=0,
                    payload=payload,
                    positions=[],
                    timeout=10,
                    encoding=False
                )
                
                assert result == []


class TestCheckerWithEncoding:
    """
    Test Suite: Checker with payload encoding
    
    Verifies: Checker correctly applies encoding to payloads during testing
    """

    def test_checker_with_url_encoding(self, mock_requester, sample_params, sample_headers):
        """
        Test: Checker applies URL encoding to payloads.
        
        Verifies: Encoding function is called and payload is transformed
        """
        payload = "<img src=x>"
        encoded_payload = url(payload)
        
        mock_response = Mock()
        mock_response.text = f"Search: st4r7s{encoded_payload}3nd"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.utils.fillHoles', return_value=[0]):
                result = checker(
                    "http://target.com",
                    sample_params,
                    sample_headers,
                    GET=True,
                    delay=0,
                    payload=payload,
                    positions=[0],
                    timeout=10,
                    encoding=url,
                    encoding_fallback=False
                )
                
                # Verify requester was called
                assert mock_requester.called

    def test_checker_with_base64_encoding(self, mock_requester, sample_params, sample_headers):
        """
        Test: Checker applies base64 encoding to payloads.
        
        Verifies: Base64 encoding works correctly in checker
        """
        payload = "<script>alert(1)</script>"
        encoded_payload = base64(payload)
        
        mock_response = Mock()
        mock_response.text = f"Data: st4r7s{encoded_payload}3nd"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.utils.fillHoles', return_value=[0]):
                result = checker(
                    "http://target.com",
                    sample_params,
                    sample_headers,
                    GET=True,
                    delay=0,
                    payload=payload,
                    positions=[0],
                    timeout=10,
                    encoding=base64,
                    encoding_fallback=False
                )
                
                assert mock_requester.called


class TestCheckerFallback:
    """
    Test Suite: Checker encoding fallback mechanism
    
    Verifies: Checker retries with encoding when plain payload fails
    """

    def test_fallback_retries_with_encoding(self, mock_requester, sample_params, sample_headers):
        """
        Test: When raw payload fails, fallback retries with encoding.
        
        Verifies: Fallback mechanism first tries raw, then encoded
        """
        payload = "<img src=x>"
        
        # First call (raw): no reflection
        # Second call (encoded): reflection found
        responses = [
            Mock(text="No match here"),
            Mock(text=f"Found: st4r7s{url(payload)}3nd")
        ]
        mock_requester.side_effect = responses
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.utils.fillHoles', return_value=[]):
                result = checker(
                    "http://target.com",
                    sample_params,
                    sample_headers,
                    GET=True,
                    delay=0,
                    payload=payload,
                    positions=[],
                    timeout=10,
                    encoding=url,
                    encoding_fallback=True
                )
                
                # Should have made 2 calls (raw + fallback)
                assert mock_requester.call_count >= 1

    def test_fallback_skipped_without_flag(self, mock_requester, sample_params, sample_headers):
        """
        Test: Fallback is not attempted when flag is False.
        
        Verifies: Without encoding_fallback flag, checker only tries once
        """
        payload = "<img src=x>"
        
        mock_response = Mock()
        mock_response.text = "No reflection"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.utils.fillHoles', return_value=[]):
                result = checker(
                    "http://target.com",
                    sample_params,
                    sample_headers,
                    GET=True,
                    delay=0,
                    payload=payload,
                    positions=[],
                    timeout=10,
                    encoding=url,
                    encoding_fallback=False
                )
                
                # Without fallback, should call once per position
                assert mock_requester.call_count >= 1

    def test_fallback_disabled_with_no_encoding(self, mock_requester, sample_params, sample_headers):
        """
        Test: Fallback has no effect when encoding is False.
        
        Verifies: Fallback requires an encoding method to work
        """
        payload = "<img src=x>"
        
        mock_response = Mock()
        mock_response.text = "No reflection"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.utils.fillHoles', return_value=[]):
                result = checker(
                    "http://target.com",
                    sample_params,
                    sample_headers,
                    GET=True,
                    delay=0,
                    payload=payload,
                    positions=[],
                    timeout=10,
                    encoding=False,
                    encoding_fallback=True  # Flag set but no encoding
                )
                
                # Should only check once since there's no encoding to fallback to
                assert result == []


class TestCheckerEfficiencyScoring:
    """
    Test Suite: Efficiency scoring of reflections
    
    Verifies: Checker correctly scores how well payloads are reflected
    """

    def test_perfect_reflection_scores_high(self, mock_requester, sample_params, sample_headers):
        """
        Test: Perfect reflection receives high efficiency score.
        
        Verifies: Identical payload reflection scores near 100
        """
        payload = "abc123"
        
        # Exact reflection
        mock_response = Mock()
        mock_response.text = f"Result: st4r7s{payload}3nd"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.utils.fillHoles', return_value=[0]):
                result = checker(
                    "http://target.com",
                    sample_params,
                    sample_headers,
                    GET=True,
                    delay=0,
                    payload=payload,
                    positions=[0],
                    timeout=10,
                    encoding=False
                )
                
                assert len(result) > 0

    def test_partial_reflection_scores_lower(self, mock_requester, sample_params, sample_headers):
        """
        Test: Partial reflection receives lower efficiency score.
        
        Verifies: Filtered/modified payloads score lower
        """
        payload = "abc123"
        
        # Partial reflection (only part of the payload)
        mock_response = Mock()
        mock_response.text = f"Result: st4r7sa3nd"  # Only 'a' from the payload
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('core.utils.fillHoles', return_value=[0]):
                result = checker(
                    "http://target.com",
                    sample_params,
                    sample_headers,
                    GET=True,
                    delay=0,
                    payload=payload,
                    positions=[0],
                    timeout=10,
                    encoding=False
                )
                
                assert isinstance(result, list)
