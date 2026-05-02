"""
Tests for configuration file support.

Tests ConfigLoader for YAML/JSON loading, validation, and integration.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.config_loader import ConfigLoader, apply_config_to_args
import argparse


class TestConfigLoaderBasics:
    """Test ConfigLoader initialization and file finding."""
    
    def test_config_loader_with_explicit_path(self):
        """Test: ConfigLoader with explicit file path"""
        loader = ConfigLoader('/tmp/test.yaml')
        assert loader.config_path == '/tmp/test.yaml'
    
    def test_config_loader_without_path(self):
        """Test: ConfigLoader finds existing config file"""
        loader = ConfigLoader()
        # Will try to find xssniper.yaml in current directory
        assert loader.config_path is None or loader.config_path.endswith(('.yaml', '.yml', '.json'))
    
    def test_get_defaults(self):
        """Test: _get_defaults returns proper default structure"""
        loader = ConfigLoader()
        defaults = loader._get_defaults()
        
        assert 'request' in defaults
        assert 'scanning' in defaults
        assert 'output' in defaults
        assert 'advanced' in defaults
        
        assert defaults['request']['delay'] == 0
        assert defaults['request']['timeout'] == 10
        assert defaults['scanning']['encode'] == 'url'
        assert defaults['scanning']['encode_fallback'] == False


class TestConfigLoaderJSON:
    """Test loading JSON configuration files."""
    
    def test_load_valid_json_config(self):
        """Test: Loading valid JSON configuration file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_config = {
                'request': {
                    'delay': 2,
                    'timeout': 20,
                    'proxy': 'http://proxy:8080'
                },
                'scanning': {
                    'encode': 'base64',
                    'encode_fallback': True,
                    'min_efficiency': 50
                }
            }
            json.dump(json_config, f)
            f.flush()
            
            loader = ConfigLoader(f.name)
            config = loader.load()
            
            assert config['request']['delay'] == 2
            assert config['request']['timeout'] == 20
            assert config['scanning']['encode'] == 'base64'
            assert config['scanning']['encode_fallback'] == True
            assert config['scanning']['min_efficiency'] == 50
            
            os.unlink(f.name)
    
    def test_load_invalid_json_config(self):
        """Test: Loading invalid JSON returns defaults"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{invalid json content')
            f.flush()
            
            loader = ConfigLoader(f.name)
            config = loader.load()
            
            # Should return defaults on error
            assert config['request']['delay'] == 0
            assert config['scanning']['encode'] == 'url'
            
            os.unlink(f.name)
    
    def test_load_json_with_partial_config(self):
        """Test: Partial JSON config merges with defaults"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            partial_config = {
                'request': {
                    'delay': 3
                }
            }
            json.dump(partial_config, f)
            f.flush()
            
            loader = ConfigLoader(f.name)
            config = loader.load()
            
            assert config['request']['delay'] == 3
            assert config['request']['timeout'] == 10  # Default
            assert config['scanning']['encode'] == 'url'  # Default
            
            os.unlink(f.name)


class TestConfigLoaderYAML:
    """Test loading YAML configuration files."""
    
    @pytest.mark.skipif(not pytest.importorskip("yaml", minversion=None), 
                       reason="PyYAML not installed")
    def test_load_valid_yaml_config(self):
        """Test: Loading valid YAML configuration file"""
        yaml = pytest.importorskip("yaml")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_content = """
request:
  delay: 5
  timeout: 30
  proxy: socks5://localhost:1080
scanning:
  encode: url
  encode_fallback: true
  min_efficiency: 60
output:
  log_level: debug
"""
            f.write(yaml_content)
            f.flush()
            
            loader = ConfigLoader(f.name)
            config = loader.load()
            
            assert config['request']['delay'] == 5
            assert config['request']['timeout'] == 30
            assert config['scanning']['encode'] == 'url'
            assert config['scanning']['encode_fallback'] == True
            assert config['output']['log_level'] == 'debug'
            
            os.unlink(f.name)
    
    @pytest.mark.skipif(not pytest.importorskip("yaml", minversion=None), 
                       reason="PyYAML not installed")
    def test_load_invalid_yaml_config(self):
        """Test: Loading invalid YAML returns defaults"""
        yaml = pytest.importorskip("yaml")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: [yaml: content:")
            f.flush()
            
            loader = ConfigLoader(f.name)
            config = loader.load()
            
            assert config['request']['delay'] == 0
            assert config['scanning']['encode'] == 'url'
            
            os.unlink(f.name)


class TestConfigLoaderValidation:
    """Test configuration validation."""
    
    def test_valid_configuration(self):
        """Test: Valid configuration passes validation"""
        loader = ConfigLoader()
        loader.config = loader._get_defaults()
        
        is_valid, message = loader.validate()
        assert is_valid == True
        assert 'valid' in message.lower()
    
    def test_invalid_delay(self):
        """Test: Invalid delay fails validation"""
        loader = ConfigLoader()
        loader.config = loader._get_defaults()
        loader.config['request']['delay'] = -1
        
        is_valid, message = loader.validate()
        assert is_valid == False
        assert 'delay' in message.lower()
    
    def test_invalid_timeout(self):
        """Test: Invalid timeout fails validation"""
        loader = ConfigLoader()
        loader.config = loader._get_defaults()
        loader.config['request']['timeout'] = 0
        
        is_valid, message = loader.validate()
        assert is_valid == False
        assert 'timeout' in message.lower()
    
    def test_invalid_encode_method(self):
        """Test: Invalid encoding method fails validation"""
        loader = ConfigLoader()
        loader.config = loader._get_defaults()
        loader.config['scanning']['encode'] = 'invalid'
        
        is_valid, message = loader.validate()
        assert is_valid == False
        assert 'encode' in message.lower()
    
    def test_invalid_min_efficiency(self):
        """Test: Invalid min_efficiency fails validation"""
        loader = ConfigLoader()
        loader.config = loader._get_defaults()
        loader.config['scanning']['min_efficiency'] = 150
        
        is_valid, message = loader.validate()
        assert is_valid == False
        assert 'efficiency' in message.lower()


class TestConfigLoaderGetters:
    """Test configuration value getters."""
    
    def test_get_existing_value(self):
        """Test: Get returns existing configuration value"""
        loader = ConfigLoader()
        loader.config = loader._get_defaults()
        
        delay = loader.get('request', 'delay')
        assert delay == 0
        
        encode = loader.get('scanning', 'encode')
        assert encode == 'url'
    
    def test_get_nonexistent_value(self):
        """Test: Get returns default for nonexistent value"""
        loader = ConfigLoader()
        loader.config = loader._get_defaults()
        
        value = loader.get('request', 'nonexistent', 'default_value')
        assert value == 'default_value'
    
    def test_to_dict(self):
        """Test: to_dict returns entire configuration"""
        loader = ConfigLoader()
        config_dict = loader.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'request' in config_dict
        assert 'scanning' in config_dict


class TestApplyConfigToArgs:
    """Test applying configuration to command-line arguments."""
    
    def test_apply_config_to_args_with_defaults(self):
        """Test: apply_config_to_args fills in missing values"""
        args = argparse.Namespace(
            delay=None,
            timeout=None,
            encode=None,
            encode_fallback=False
        )
        
        loader = ConfigLoader()
        updated_args = apply_config_to_args(args, loader)
        
        assert updated_args.delay == 0  # From config
        assert updated_args.timeout == 10  # From config
        assert updated_args.encode == 'url'  # From config
    
    def test_apply_config_preserves_cli_args(self):
        """Test: CLI arguments override config file"""
        args = argparse.Namespace(
            delay=5,
            timeout=20,
            encode='base64',
            encode_fallback=True,
            user_agent='custom-agent'
        )
        
        loader = ConfigLoader()
        updated_args = apply_config_to_args(args, loader)
        
        assert updated_args.delay == 5  # Preserved from CLI
        assert updated_args.timeout == 20  # Preserved from CLI
        assert updated_args.encode == 'base64'  # Preserved from CLI
    
    def test_apply_config_creates_missing_attributes(self):
        """Test: apply_config creates missing attributes on args"""
        args = argparse.Namespace(delay=None)
        
        loader = ConfigLoader()
        updated_args = apply_config_to_args(args, loader)
        
        assert hasattr(updated_args, 'timeout')
        assert hasattr(updated_args, 'encode')
        assert hasattr(updated_args, 'log_level')


class TestConfigMerging:
    """Test configuration merging logic."""
    
    def test_merge_partial_config_with_defaults(self):
        """Test: Partial config merges properly with defaults"""
        loader = ConfigLoader()
        partial = {
            'request': {
                'delay': 10
            },
            'scanning': {
                'min_efficiency': 75
            }
        }
        
        merged = loader._merge_defaults(partial)
        
        assert merged['request']['delay'] == 10  # Overridden
        assert merged['request']['timeout'] == 10  # Default
        assert merged['scanning']['min_efficiency'] == 75  # Overridden
        assert merged['scanning']['encode'] == 'url'  # Default
    
    def test_merge_empty_config(self):
        """Test: Empty config merges to get all defaults"""
        loader = ConfigLoader()
        merged = loader._merge_defaults({})
        
        assert len(merged) > 0
        assert 'request' in merged
        assert 'scanning' in merged


class TestConfigFileNotFound:
    """Test behavior when config file is not found."""
    
    def test_nonexistent_file_returns_defaults(self):
        """Test: Nonexistent config file returns defaults"""
        loader = ConfigLoader('/nonexistent/path/config.yaml')
        config = loader.load()
        
        assert config['request']['delay'] == 0
        assert config['scanning']['encode'] == 'url'
    
    def test_none_path_returns_defaults(self):
        """Test: None path returns defaults"""
        loader = ConfigLoader(None)
        loader.config_path = None
        config = loader.load()
        
        assert config['request']['delay'] == 0
        assert config['scanning']['encode'] == 'url'


class TestConfigIntegration:
    """Integration tests for configuration system."""
    
    def test_full_workflow_json(self):
        """Test: Full workflow with JSON config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_dict = {
                'request': {'delay': 1, 'timeout': 15},
                'scanning': {'encode': 'base64', 'encode_fallback': True},
                'output': {'log_level': 'debug'}
            }
            json.dump(config_dict, f)
            f.flush()
            
            # Load config
            loader = ConfigLoader(f.name)
            config = loader.load()
            
            # Validate
            is_valid, _ = loader.validate()
            assert is_valid
            
            # Get values
            assert loader.get('request', 'delay') == 1
            assert loader.get('scanning', 'encode') == 'base64'
            
            # Apply to args
            args = argparse.Namespace()
            updated_args = apply_config_to_args(args, loader)
            assert updated_args.delay == 1
            assert updated_args.encode == 'base64'
            
            os.unlink(f.name)
    
    def test_config_precedence(self):
        """Test: Config file < CLI args precedence"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'request': {'delay': 10}}, f)
            f.flush()
            
            loader = ConfigLoader(f.name)
            args = argparse.Namespace(delay=5, timeout=None)  # CLI arg takes precedence
            
            updated_args = apply_config_to_args(args, loader)
            assert updated_args.delay == 5  # CLI arg wins
            assert updated_args.timeout == 10  # Config file used
            
            os.unlink(f.name)
