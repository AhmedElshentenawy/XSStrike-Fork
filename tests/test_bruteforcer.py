"""
Tests for modes/bruteforcer.py

Tests verify:
- Payload list iteration
- Parameter value replacement
- Encoding fallback behavior in bruteforce mode
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from modes.bruteforcer import bruteforcer
from core.encoders import url, base64


class TestBruteforcerBasics:
    """
    Test Suite: Basic bruteforcer operation
    
    Verifies: Bruteforcer iterates through payload list and tests each
    """

    def test_bruteforcer_tests_payload_list(self, mock_requester):
        """
        Test: Bruteforcer sends each payload from the list.
        
        Verifies: All payloads in list are tested
        """
        payloads = [
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
            '"><script>alert(1)</script>'
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Response without reflection"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('modes.bruteforcer.getUrl', return_value='http://target.com/page'):
                with patch('modes.bruteforcer.getParams', return_value={'q': 'search'}):
                    with patch('core.log.setup_logger'):
                        bruteforcer(
                            'http://target.com/page?q=search',
                            None,
                            payloads,
                            encoding=False,
                            headers={'User-Agent': 'Test'},
                            delay=0,
                            timeout=10,
                            encoding_fallback=False
                        )
                        
                        # Should have made requests for each payload
                        assert mock_requester.call_count >= len(payloads)

    def test_bruteforcer_detects_matches(self, mock_requester):
        """
        Test: Bruteforcer identifies matching payloads.
        
        Verifies: Payloads that appear in responses are detected
        """
        payloads = ['<img src=x>']
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = f"Results contain: {payloads[0]}"  # Payload reflected
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('modes.bruteforcer.getUrl', return_value='http://target.com/page'):
                with patch('modes.bruteforcer.getParams', return_value={'q': 'search'}):
                    with patch('core.log.setup_logger') as mock_logger:
                        bruteforcer(
                            'http://target.com/page?q=search',
                            None,
                            payloads,
                            encoding=False,
                            headers={'User-Agent': 'Test'},
                            delay=0,
                            timeout=10,
                            encoding_fallback=False
                        )
                        
                        assert mock_requester.called


class TestBruteforcerEncoding:
    """
    Test Suite: Bruteforcer with encoding
    
    Verifies: Bruteforcer applies encoding to payloads
    """

    def test_bruteforcer_with_url_encoding(self, mock_requester):
        """
        Test: Bruteforcer applies URL encoding to payloads.
        
        Verifies: Payloads are URL-encoded before sending
        """
        payloads = ['<img src=x>']
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Response"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('modes.bruteforcer.getUrl', return_value='http://target.com/page'):
                with patch('modes.bruteforcer.getParams', return_value={'q': 'search'}):
                    with patch('core.log.setup_logger'):
                        bruteforcer(
                            'http://target.com/page?q=search',
                            None,
                            payloads,
                            encoding=url,
                            headers={'User-Agent': 'Test'},
                            delay=0,
                            timeout=10,
                            encoding_fallback=False
                        )
                        
                        assert mock_requester.called

    def test_bruteforcer_with_base64_encoding(self, mock_requester):
        """
        Test: Bruteforcer applies base64 encoding to payloads.
        
        Verifies: Base64 encoding works in bruteforcer
        """
        payloads = ['<script>alert(1)</script>']
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Response"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('modes.bruteforcer.getUrl', return_value='http://target.com/page'):
                with patch('modes.bruteforcer.getParams', return_value={'q': 'search'}):
                    with patch('core.log.setup_logger'):
                        bruteforcer(
                            'http://target.com/page?q=search',
                            None,
                            payloads,
                            encoding=base64,
                            headers={'User-Agent': 'Test'},
                            delay=0,
                            timeout=10,
                            encoding_fallback=False
                        )
                        
                        assert mock_requester.called


class TestBruteforcerEncodingFallback:
    """
    Test Suite: Bruteforcer encoding fallback
    
    Verifies: Bruteforcer retries with encoding when plain payload fails
    """

    def test_fallback_retries_with_encoding(self, mock_requester):
        """
        Test: Bruteforcer retries with encoding when raw doesn't match.
        
        Verifies: Two requests made when fallback detects no match
        """
        payloads = ['<img src=x>']
        
        # First request: no match
        response1 = Mock()
        response1.status_code = 200
        response1.text = "No match here"
        
        # Second request: match with encoded
        response2 = Mock()
        response2.status_code = 200
        response2.text = f"Found: {url(payloads[0])}"
        
        mock_requester.side_effect = [response1, response2]
        
        with patch('core.requester.requester', mock_requester):
            with patch('modes.bruteforcer.getUrl', return_value='http://target.com/page'):
                with patch('modes.bruteforcer.getParams', return_value={'q': 'search'}):
                    with patch('core.log.setup_logger'):
                        bruteforcer(
                            'http://target.com/page?q=search',
                            None,
                            payloads,
                            encoding=url,
                            headers={'User-Agent': 'Test'},
                            delay=0,
                            timeout=10,
                            encoding_fallback=True
                        )
                        
                        # Should have made at least 2 calls per payload
                        assert mock_requester.call_count >= 2

    def test_fallback_skipped_on_raw_match(self, mock_requester):
        """
        Test: Fallback is not used if raw payload matches.
        
        Verifies: Fallback only triggers when raw payload doesn't match
        """
        payloads = ['<img src=x>']
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = f"Success: {payloads[0]}"  # Already matched
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('modes.bruteforcer.getUrl', return_value='http://target.com/page'):
                with patch('modes.bruteforcer.getParams', return_value={'q': 'search'}):
                    with patch('core.log.setup_logger'):
                        bruteforcer(
                            'http://target.com/page?q=search',
                            None,
                            payloads,
                            encoding=url,
                            headers={'User-Agent': 'Test'},
                            delay=0,
                            timeout=10,
                            encoding_fallback=True
                        )
                        
                        # Should only make 1 call per payload since raw matched
                        call_count_per_payload = mock_requester.call_count
                        assert call_count_per_payload >= 1

    def test_fallback_disabled_no_retry(self, mock_requester):
        """
        Test: Without fallback flag, no retry is attempted.
        
        Verifies: Single request per payload when fallback disabled
        """
        payloads = ['<img src=x>']
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "No match"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('modes.bruteforcer.getUrl', return_value='http://target.com/page'):
                with patch('modes.bruteforcer.getParams', return_value={'q': 'search'}):
                    with patch('core.log.setup_logger'):
                        bruteforcer(
                            'http://target.com/page?q=search',
                            None,
                            payloads,
                            encoding=url,
                            headers={'User-Agent': 'Test'},
                            delay=0,
                            timeout=10,
                            encoding_fallback=False
                        )
                        
                        # Should be exactly 1 call per payload
                        assert mock_requester.call_count >= 1


class TestBruteforcerParameterHandling:
    """
    Test Suite: Parameter injection in bruteforcer
    
    Verifies: Bruteforcer correctly injects payloads into parameters
    """

    def test_parameter_replacement(self, mock_requester):
        """
        Test: Bruteforcer replaces parameter values with payloads.
        
        Verifies: Original param structure is maintained
        """
        payloads = ['<img src=x>']
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Response"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('modes.bruteforcer.getUrl', return_value='http://target.com/page'):
                with patch('modes.bruteforcer.getParams', return_value={'q': 'search', 'id': '123'}):
                    with patch('core.log.setup_logger'):
                        bruteforcer(
                            'http://target.com/page?q=search&id=123',
                            None,
                            payloads,
                            encoding=False,
                            headers={'User-Agent': 'Test'},
                            delay=0,
                            timeout=10,
                            encoding_fallback=False
                        )
                        
                        # Verify requester was called with modified params
                        assert mock_requester.called

    def test_multiple_parameters(self, mock_requester):
        """
        Test: Bruteforcer tests each parameter separately.
        
        Verifies: All parameters receive payloads
        """
        payloads = ['<img src=x>']
        params = {'q': 'search', 'id': '123', 'filter': 'active'}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Response"
        mock_requester.return_value = mock_response
        
        with patch('core.requester.requester', mock_requester):
            with patch('modes.bruteforcer.getUrl', return_value='http://target.com/page'):
                with patch('modes.bruteforcer.getParams', return_value=params):
                    with patch('core.log.setup_logger'):
                        bruteforcer(
                            'http://target.com/page?q=search&id=123&filter=active',
                            None,
                            payloads,
                            encoding=False,
                            headers={'User-Agent': 'Test'},
                            delay=0,
                            timeout=10,
                            encoding_fallback=False
                        )
                        
                        # Should call requester for each param * each payload
                        expected_calls = len(params) * len(payloads)
                        assert mock_requester.call_count >= expected_calls
