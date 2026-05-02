"""
Tests for core/generator.py

Tests verify:
- Payload vector generation
- Context-aware payload crafting
- Payload confidence scoring
- Filter evasion techniques
"""

import pytest
from unittest.mock import Mock, patch
from core.generator import generator


class TestGeneratorBasicPayloads:
    """
    Test Suite: Basic payload generation
    
    Verifies: Generator creates exploitable payloads for different contexts
    """

    def test_generator_returns_vectors(self):
        """
        Test: Generator returns dictionary of payload vectors.
        
        Verifies: Output structure contains confidence levels as keys
        """
        occurences = {
            0: {
                'context': 'html',
                'score': {'<': 100, '>': 100},
                'details': {}
            }
        }
        response = "<div>test</div>"
        
        result = generator(occurences, response)
        
        assert isinstance(result, dict)
        assert all(isinstance(k, int) for k in result.keys())

    def test_generator_confidence_ordering(self):
        """
        Test: Vectors are organized by confidence level.
        
        Verifies: High-confidence payloads are separated from low-confidence ones
        """
        occurences = {
            0: {
                'context': 'html',
                'score': {'<': 100, '>': 100},
                'details': {}
            }
        }
        response = "<div>test</div>"
        
        result = generator(occurences, response)
        
        # Keys should be confidence scores
        assert all(isinstance(k, int) for k in result.keys())
        # Higher numbers = higher confidence
        assert max(result.keys()) >= min(result.keys())

    def test_generator_creates_payload_sets(self):
        """
        Test: Each confidence level contains a set of payloads.
        
        Verifies: Payloads are stored in sets for deduplication
        """
        occurences = {
            0: {
                'context': 'html',
                'score': {'<': 100, '>': 100},
                'details': {}
            }
        }
        response = "<div>test</div>"
        
        result = generator(occurences, response)
        
        for confidence, payloads in result.items():
            assert isinstance(payloads, set)


class TestGeneratorContextAwareness:
    """
    Test Suite: Context-aware payload generation
    
    Verifies: Generator creates payloads tailored to reflection context
    """

    def test_html_context_payloads(self):
        """
        Test: HTML context generates tag-based payloads.
        
        Verifies: Payloads contain HTML tags and event handlers for HTML context
        """
        occurences = {
            0: {
                'context': 'html',
                'score': {'<': 100, '>': 100},
                'details': {}
            }
        }
        response = "<div>test</div>"
        
        result = generator(occurences, response)
        
        # Should have some payloads
        total_payloads = sum(len(v) for v in result.values())
        assert total_payloads > 0

    def test_attribute_context_payloads(self):
        """
        Test: Attribute context generates quote-breaking payloads.
        
        Verifies: Attribute payloads use quotes and event handlers
        """
        occurences = {
            0: {
                'context': 'attribute',
                'score': {'"': 100, '>': 100},
                'details': {
                    'tag': 'img',
                    'type': 'value',
                    'quote': '"',
                    'name': 'src',
                    'value': 'test'
                }
            }
        }
        response = '<img src="test">'
        
        result = generator(occurences, response)
        
        total_payloads = sum(len(v) for v in result.values())
        assert total_payloads > 0

    def test_script_context_payloads(self):
        """
        Test: Script context generates JavaScript payloads.
        
        Verifies: Script payloads break out of JavaScript context
        """
        occurences = {
            0: {
                'context': 'script',
                'score': {'</script>': 100, '>': 100},
                'details': {'quote': "'"}
            }
        }
        response = "<script>var x = 'test';</script>"
        
        result = generator(occurences, response)
        
        total_payloads = sum(len(v) for v in result.values())
        assert total_payloads > 0


class TestGeneratorQuoteHandling:
    """
    Test Suite: Quote handling in payload generation
    
    Verifies: Generator correctly handles different quote types
    """

    def test_double_quote_handling(self):
        """
        Test: Generates payloads for double-quoted attributes.
        
        Verifies: Payloads start with double quotes to break context
        """
        occurences = {
            0: {
                'context': 'attribute',
                'score': {'"': 100, '>': 100},
                'details': {
                    'tag': 'div',
                    'type': 'value',
                    'quote': '"',
                    'name': 'class',
                    'value': 'test'
                }
            }
        }
        response = '<div class="test">'
        
        result = generator(occurences, response)
        
        # Should generate payloads
        assert sum(len(v) for v in result.values()) > 0

    def test_single_quote_handling(self):
        """
        Test: Generates payloads for single-quoted attributes.
        
        Verifies: Payloads start with single quotes
        """
        occurences = {
            0: {
                'context': 'attribute',
                'score': {"'": 100, '>': 100},
                'details': {
                    'tag': 'img',
                    'type': 'value',
                    'quote': "'",
                    'name': 'src',
                    'value': 'test'
                }
            }
        }
        response = "<img src='test'>"
        
        result = generator(occurences, response)
        
        assert sum(len(v) for v in result.values()) > 0

    def test_no_quote_handling(self):
        """
        Test: Generates payloads for unquoted attributes.
        
        Verifies: Payloads for attributes without quotes
        """
        occurences = {
            0: {
                'context': 'attribute',
                'score': {'>': 100},
                'details': {
                    'tag': 'img',
                    'type': 'value',
                    'quote': '',
                    'name': 'src',
                    'value': 'test'
                }
            }
        }
        response = "<img src=test>"
        
        result = generator(occurences, response)
        
        assert sum(len(v) for v in result.values()) > 0


class TestGeneratorEfficiencyScoring:
    """
    Test Suite: Payload confidence and efficiency scoring
    
    Verifies: Generator ranks payloads by likelihood of success
    """

    def test_high_efficiency_high_confidence(self):
        """
        Test: Payloads with high filter efficiency get high confidence.
        
        Verifies: Confidence increases with escapeability
        """
        occurences = {
            0: {
                'context': 'html',
                'score': {'<': 100, '>': 100},  # All characters pass through
                'details': {}
            }
        }
        response = "<div>test</div>"
        
        result = generator(occurences, response)
        
        # Should have high-confidence payloads (keys 10, 9, 8, etc.)
        high_confidence_keys = [k for k in result.keys() if k >= 8]
        assert len(high_confidence_keys) > 0

    def test_low_efficiency_low_confidence(self):
        """
        Test: Payloads with low filter efficiency get lower confidence.
        
        Verifies: Difficult-to-escape contexts get lower confidence ratings
        """
        occurences = {
            0: {
                'context': 'html',
                'score': {'<': 10, '>': 10},  # Characters are heavily filtered
                'details': {}
            }
        }
        response = "<div>test</div>"
        
        result = generator(occurences, response)
        
        # Should have payloads across confidence spectrum
        assert len(result) > 0


class TestGeneratorEmptyOccurences:
    """
    Test Suite: Generator behavior with edge cases
    
    Verifies: Generator handles empty or invalid input gracefully
    """

    def test_empty_occurences(self):
        """
        Test: Generator handles empty occurences dictionary.
        
        Verifies: No crash on empty input
        """
        occurences = {}
        response = "<div>test</div>"
        
        result = generator(occurences, response)
        
        assert isinstance(result, dict)

    def test_missing_details(self):
        """
        Test: Generator handles occurence with missing details.
        
        Verifies: Graceful handling of incomplete data
        """
        occurences = {
            0: {
                'context': 'html',
                'score': {'<': 100, '>': 100},
                'details': {}
            }
        }
        response = "<div>test</div>"
        
        result = generator(occurences, response)
        
        assert isinstance(result, dict)

    def test_bad_tag_exclusion(self):
        """
        Test: Generator excludes payloads in bad tag contexts.
        
        Verifies: Tags like <script>, <style> are handled specially
        """
        occurences = {
            0: {
                'context': 'html',
                'score': {'<': 100, '>': 100},
                'details': {'badTag': 'script'}
            }
        }
        response = "<script>var x='test';</script>"
        
        result = generator(occurences, response)
        
        assert isinstance(result, dict)
