"""
XSStrike Test Suite

This package contains comprehensive unit and integration tests for the XSStrike XSS detection tool.

Test Structure:
- conftest.py: Pytest configuration and shared fixtures
- test_encoders.py: URL and base64 encoding functionality
- test_checker.py: Payload reflection detection and efficiency scoring
- test_fuzzer.py: Fuzzing engine with WAF detection
- test_generator.py: Payload generation for different contexts
- test_bruteforcer.py: Bruteforce scanning mode with encoding fallback

Running Tests:
    pytest                          # Run all tests
    pytest -v                       # Verbose output
    pytest tests/test_encoders.py  # Run specific test file
    pytest -k fallback              # Run tests matching pattern
    pytest --cov=core              # Generate coverage report

Coverage Target: 80%+
"""
