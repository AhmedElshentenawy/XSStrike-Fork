# Configuration File Support

XSStrike now supports external configuration files in YAML or JSON format. This allows you to set default values for all scanning options without modifying code or using command-line arguments every time.

## Configuration File Format

Configuration files use a hierarchical structure with four main sections:

### 1. Request Settings
```yaml
request:
  delay: 0              # Delay between requests (seconds, float)
  timeout: 10           # Request timeout (seconds)
  user_agent: ""        # Custom User-Agent header (empty = random)
  proxy: null           # Proxy URL (http://ip:port or socks5://ip:port)
```

### 2. Scanning Settings
```yaml
scanning:
  encode: 'url'                # Encoding method: 'url' or 'base64'
  encode_fallback: false       # Retry with encoding if initial request fails
  min_efficiency: 0            # Minimum reflection efficiency (0-100)
  skip_dom: false              # Skip DOM vulnerability scanning
  skip_waf: false              # Skip WAF detection
```

### 3. Output Settings
```yaml
output:
  log_level: 'info'            # Logging level: debug, info, warning, error
  log_format: 'text'           # Output format: 'text' or 'json'
  output_file: null            # Save results to file (null = stdout only)
```

### 4. Advanced Settings
```yaml
advanced:
  threads: 2                    # Number of threads for crawling
  crawl_depth: 2                # Maximum crawling depth
  crawl_limit: 100              # Maximum number of links to crawl
```

## Usage

### Option 1: Default Location
Place `xsstrike.yaml` or `xsstrike.json` in your current directory:
```bash
# XSStrike will automatically find and load xsstrike.yaml
python3 xsstrike.py -u http://target.com
```

### Option 2: Custom Location
Use the `--config` flag to specify a config file:
```bash
python3 xsstrike.py -u http://target.com --config /path/to/config.yaml
python3 xsstrike.py -u http://target.com --config ~/.xsstrike/prod-config.json
```

### Option 3: Home Directory
Place config in `~/.xsstrike/xsstrike.yaml`:
```bash
mkdir -p ~/.xsstrike
cp xsstrike.yaml ~/.xsstrike/
python3 xsstrike.py -u http://target.com  # Loads from home directory
```

## Examples

### Example 1: Basic YAML Configuration
File: `xsstrike.yaml`
```yaml
request:
  delay: 2
  timeout: 15

scanning:
  encode: 'url'
  encode_fallback: true
  min_efficiency: 25

output:
  log_level: 'info'
```

Usage:
```bash
python3 xsstrike.py -u http://vulnerable-site.com
# Uses delay=2, timeout=15, base64 encoding with fallback
```

### Example 2: JSON Configuration for Different Environments
File: `config-aggressive.json`
```json
{
  "request": {
    "delay": 0,
    "timeout": 5
  },
  "scanning": {
    "encode": "base64",
    "encode_fallback": true,
    "min_efficiency": 50
  },
  "advanced": {
    "threads": 4,
    "crawl_depth": 3
  }
}
```

Usage:
```bash
python3 xsstrike.py -u http://target.com --config config-aggressive.json
```

### Example 3: Conservative Scanning
File: `config-conservative.yaml`
```yaml
request:
  delay: 5
  timeout: 20
  proxy: "http://proxy:8080"

scanning:
  encode: 'url'
  encode_fallback: false
  min_efficiency: 75
  skip_waf: false
```

Usage:
```bash
python3 xsstrike.py -u http://target.com --config config-conservative.yaml
```

## Configuration Precedence

Command-line arguments **override** configuration file settings:

```bash
# Config file sets delay=2, but CLI sets delay=5
python3 xsstrike.py -u http://target.com --config xsstrike.yaml -d 5
# Uses delay=5 (CLI wins)

# Config file sets encode='base64', CLI doesn't specify it
python3 xsstrike.py -u http://target.com --config xsstrike.yaml
# Uses encode='base64' (from config file)
```

## Validation

Configuration files are automatically validated when loaded. Invalid values will be caught:

```bash
$ python3 xsstrike.py -u http://target.com --config invalid.yaml
# Error: Request timeout must be a positive number
# Using default configuration.
```

## Converting Between YAML and JSON

### YAML to JSON
```bash
# Using Python
python3 -c "import yaml, json; print(json.dumps(yaml.safe_load(open('xsstrike.yaml'))))" > xsstrike.json
```

### JSON to YAML
```bash
# Using Python
python3 -c "import json, yaml; print(yaml.dump(json.load(open('xsstrike.json'))))" > xsstrike.yaml
```

## Configuration Examples by Use Case

### Security Assessment (Thorough)
```yaml
request:
  delay: 3
  timeout: 20

scanning:
  encode: 'url'
  encode_fallback: true
  min_efficiency: 0
  skip_dom: false
  skip_waf: false

advanced:
  threads: 2
  crawl_depth: 3
  crawl_limit: 200
```

### Bounty Hunting (Fast)
```yaml
request:
  delay: 0
  timeout: 10

scanning:
  encode: 'base64'
  encode_fallback: true
  min_efficiency: 30

advanced:
  threads: 4
  crawl_depth: 2
  crawl_limit: 100
```

### Stealthy Scanning (WAF Bypass)
```yaml
request:
  delay: 10
  timeout: 30
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  proxy: "socks5://localhost:9050"

scanning:
  encode: 'url'
  encode_fallback: false
  min_efficiency: 50
  skip_waf: false

advanced:
  threads: 1
  crawl_depth: 1
```

## Programmatic Usage

### In Python Code
```python
from core.config_loader import ConfigLoader, apply_config_to_args
import argparse

# Load configuration
loader = ConfigLoader('xsstrike.yaml')
config = loader.to_dict()

# Get specific values
delay = loader.get('request', 'delay', default=0)
encoding = loader.get('scanning', 'encode', default='url')

# Validate configuration
is_valid, message = loader.validate()
if not is_valid:
    print(f"Config error: {message}")

# Apply to args
args = argparse.Namespace(delay=None, timeout=None)
args = apply_config_to_args(args, loader)
```

## Troubleshooting

### "Config file not found"
- Check the file path is correct
- For home directory: place file in `~/.xsstrike/xsstrike.yaml`
- Verify file permissions are readable

### "YAML parsing error"
- Install PyYAML: `pip install pyyaml`
- Check YAML syntax (use a YAML validator)
- Ensure proper indentation (spaces, not tabs)

### "Validation failed"
- Check config values are within valid ranges
- delay: must be >= 0
- timeout: must be > 0
- min_efficiency: must be 0-100
- encode: must be 'url' or 'base64'

### Config file ignored
- Check if using `--config` flag correctly
- Verify CLI args aren't overriding values (they take precedence)
- Check for typos in section or key names

## Best Practices

1. **Start with defaults**: Copy provided `xsstrike.yaml` and modify only what you need
2. **Use version control**: Keep configs in git with sensitive values removed
3. **Environment-specific configs**: Create separate files (dev, prod, aggressive, conservative)
4. **Validate before use**: Always run validation before using new configs
5. **Document changes**: Comment your configs for team members
6. **Use YAML for readability**: YAML is more readable than JSON for humans
7. **Use JSON for automation**: JSON works better with CI/CD pipelines

## Environment Variables (Future)

In future versions, you'll be able to override config with environment variables:
```bash
XS_DELAY=2 XS_ENCODE=base64 python3 xsstrike.py -u http://target.com
```
