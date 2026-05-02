# Configuration File Quick Start

## 5-Minute Setup

### Step 1: Create Configuration File
```bash
# Copy the example config
cp xssniper.yaml ~/.xssniper/xssniper.yaml

# Or create from scratch
cat > xssniper.yaml << EOF
request:
  delay: 2
  timeout: 15

scanning:
  encode: 'url'
  encode_fallback: true
  min_efficiency: 25
EOF
```

### Step 2: Customize (Optional)
Edit `xssniper.yaml` with your preferred settings:
```bash
nano xssniper.yaml
```

### Step 3: Run XSSniper
```bash
# Auto-loads from current directory or ~/.xssniper/
python3 xssniper.py -u http://target.com

# Or specify a config file
python3 xssniper.py -u http://target.com --config /path/to/config.yaml
```

## Common Configurations

### Rapid Testing (Fast Scanning)
```yaml
request:
  delay: 0
  timeout: 5

scanning:
  encode: 'base64'
  encode_fallback: true
```

### Stealth Mode (Evasion)
```yaml
request:
  delay: 10
  timeout: 30
  proxy: "socks5://localhost:1080"

scanning:
  encode: 'url'
  encode_fallback: false
```

### Thorough Assessment
```yaml
request:
  delay: 2
  timeout: 20

scanning:
  encode: 'url'
  encode_fallback: true
  min_efficiency: 0
  skip_dom: false
```

## Command Line vs Config File

**Config File** (for defaults):
```bash
python3 xssniper.py -u http://target.com
# Uses settings from xssniper.yaml
```

**CLI Overrides** (for specific scans):
```bash
python3 xssniper.py -u http://target.com -d 5 --encode base64
# Uses delay=5 and base64 encoding (overrides config)
```

## Validation

Check if your config is valid:
```python
from core.config_loader import ConfigLoader

loader = ConfigLoader('xssniper.yaml')
is_valid, message = loader.validate()
print(f"Valid: {is_valid}, Message: {message}")
```

## For More Information

See [CONFIGURATION.md](CONFIGURATION.md) for complete documentation.
