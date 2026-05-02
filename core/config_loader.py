"""
Configuration file loader for XSStrike.

Supports YAML configuration files for setting default values.
Usage:
    from core.config_loader import ConfigLoader
    config = ConfigLoader('xsstrike.yaml')
    settings = config.load()
"""

import os
import json
from pathlib import Path
from core.log import setup_logger

logger = setup_logger(__name__)

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigLoader:
    """Load and manage configuration from external files."""
    
    def __init__(self, config_path=None):
        """
        Initialize config loader.
        
        Args:
            config_path (str): Path to config file. If None, uses 'xsstrike.yaml' or 'xsstrike.json'
        """
        self.config_path = config_path or self._find_config_file()
        self.config = {}
    
    def _find_config_file(self):
        """Find config file in current directory or home directory."""
        # Check current directory first
        for filename in ['xsstrike.yaml', 'xsstrike.yml', 'xsstrike.json']:
            if os.path.exists(filename):
                return filename
        
        # Check home directory
        home = Path.home()
        for filename in ['xsstrike.yaml', 'xsstrike.yml', 'xsstrike.json']:
            path = home / f'.xsstrike/{filename}'
            if path.exists():
                return str(path)
        
        return None
    
    def load(self):
        """
        Load configuration from file.
        
        Returns:
            dict: Configuration dictionary with defaults merged
        """
        if not self.config_path:
            logger.debug('No configuration file found. Using defaults.')
            return self._get_defaults()
        
        if not os.path.exists(self.config_path):
            logger.warning(f'Config file not found: {self.config_path}')
            return self._get_defaults()
        
        try:
            if self.config_path.endswith('.json'):
                return self._load_json()
            else:  # YAML or YML
                return self._load_yaml()
        except Exception as e:
            logger.error(f'Failed to load config file: {e}')
            logger.info('Using default configuration.')
            return self._get_defaults()
    
    def _load_yaml(self):
        """Load YAML configuration file."""
        if not YAML_AVAILABLE:
            logger.warning('PyYAML not installed. Install with: pip install pyyaml')
            return self._get_defaults()
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            logger.debug(f'Loaded configuration from {self.config_path}')
            return self._merge_defaults(config)
        except yaml.YAMLError as e:
            logger.error(f'YAML parsing error: {e}')
            return self._get_defaults()
    
    def _load_json(self):
        """Load JSON configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.debug(f'Loaded configuration from {self.config_path}')
            return self._merge_defaults(config)
        except json.JSONDecodeError as e:
            logger.error(f'JSON parsing error: {e}')
            return self._get_defaults()
    
    def _get_defaults(self):
        """Get default configuration."""
        return {
            'request': {
                'delay': 0,
                'timeout': 10,
                'user_agent': '',
                'proxy': None,
            },
            'scanning': {
                'encode': 'url',
                'encode_fallback': False,
                'min_efficiency': 0,
                'skip_dom': False,
                'skip_waf': False,
            },
            'output': {
                'log_level': 'info',
                'log_format': 'text',
                'output_file': None,
            },
            'advanced': {
                'threads': 2,
                'crawl_depth': 2,
                'crawl_limit': 100,
            },
        }
    
    def _merge_defaults(self, config):
        """
        Merge user config with defaults.
        
        Args:
            config (dict): User configuration
            
        Returns:
            dict: Merged configuration with defaults
        """
        defaults = self._get_defaults()
        
        for section, values in defaults.items():
            if section not in config:
                config[section] = {}
            for key, default_value in values.items():
                if key not in config[section]:
                    config[section][key] = default_value
        
        return config
    
    def get(self, section, key, default=None):
        """
        Get configuration value.
        
        Args:
            section (str): Config section (request, scanning, output, advanced)
            key (str): Config key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        if not self.config:
            self.config = self.load()
        
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default
    
    def to_dict(self):
        """Get entire configuration as dictionary."""
        if not self.config:
            self.config = self.load()
        return self.config
    
    def validate(self):
        """
        Validate configuration values.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        config = self.to_dict()
        
        # Validate delay
        try:
            delay = config['request']['delay']
            if not isinstance(delay, (int, float)) or delay < 0:
                return False, "Request delay must be a non-negative number"
        except (KeyError, TypeError):
            return False, "Invalid request.delay configuration"
        
        # Validate timeout
        try:
            timeout = config['request']['timeout']
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                return False, "Request timeout must be a positive number"
        except (KeyError, TypeError):
            return False, "Invalid request.timeout configuration"
        
        # Validate encoding
        try:
            encode = config['scanning']['encode']
            if encode not in ['url', 'base64', None]:
                return False, "Scanning encode must be 'url' or 'base64'"
        except (KeyError, TypeError):
            return False, "Invalid scanning.encode configuration"
        
        # Validate min_efficiency
        try:
            efficiency = config['scanning']['min_efficiency']
            if not isinstance(efficiency, (int, float)) or not (0 <= efficiency <= 100):
                return False, "min_efficiency must be between 0 and 100"
        except (KeyError, TypeError):
            return False, "Invalid scanning.min_efficiency configuration"
        
        return True, "Configuration valid"


def apply_config_to_args(args, config=None):
    """
    Apply configuration file settings to command-line arguments.
    Config file values are used as defaults, command-line args override them.
    
    Args:
        args: argparse.Namespace object with command-line arguments
        config (ConfigLoader): ConfigLoader instance. If None, creates new one.
        
    Returns:
        argparse.Namespace: Updated args with config values merged
    """
    if config is None:
        config = ConfigLoader()
    
    cfg = config.to_dict()
    
    # Apply request settings
    if not hasattr(args, 'delay') or args.delay is None:
        args.delay = cfg['request']['delay']
    if not hasattr(args, 'timeout') or args.timeout is None:
        args.timeout = cfg['request']['timeout']
    if not hasattr(args, 'user_agent') or args.user_agent is None:
        args.user_agent = cfg['request']['user_agent']
    if not hasattr(args, 'proxy') or args.proxy is None:
        args.proxy = cfg['request']['proxy']
    
    # Apply scanning settings
    if not hasattr(args, 'encode') or args.encode is None:
        args.encode = cfg['scanning']['encode']
    if not hasattr(args, 'encode_fallback'):
        args.encode_fallback = cfg['scanning']['encode_fallback']
    if not hasattr(args, 'min_efficiency') or args.min_efficiency is None:
        args.min_efficiency = cfg['scanning']['min_efficiency']
    if not hasattr(args, 'skip_dom'):
        args.skip_dom = cfg['scanning']['skip_dom']
    
    # Apply output settings
    if not hasattr(args, 'log_level') or args.log_level is None:
        args.log_level = cfg['output']['log_level']
    if not hasattr(args, 'log_format') or args.log_format is None:
        args.log_format = cfg['output']['log_format']
    if not hasattr(args, 'output_file') or args.output_file is None:
        args.output_file = cfg['output']['output_file']
    
    return args
