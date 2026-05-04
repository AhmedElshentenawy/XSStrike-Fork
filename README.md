# XSSniper

> Fork of the original `xsstrike` with new configuration, encoding, logging, error handling, and test improvements.

## Overview

XSSniper is a Cross Site Scripting detection toolkit that combines parser-based context analysis, payload generation, fuzzing, crawling, and optional plugin scanning.

This repository is a fork of the original `xsstrike` project. It preserves the core XSS scanning capabilities while adding safer CLI behavior, external configuration support, payload encoding options, progress logging, and a growing test suite.

## What’s new in this fork

- Config file support for YAML and JSON via `--config`
- `xssniper.yaml` / `xssniper.json` configuration overlays
- Encoding options for URL and Base64 payload delivery
- Encoding fallback and retry logic for better coverage
- Step-based progress logging for scan/crawl/fuzz workflow visibility
- Improved error handling and request validation
- Polished CLI help text and grouped arguments
- Modular core design with clearer input/output flow
- `pytest`-ready tests and documentation examples
- Renamed entrypoint and repository branding to `xssniper`

## Classic XSSniper / xsstrike features

- Reflected XSS scanning
- DOM XSS scanning
- Multi-threaded crawling
- Context analysis
- Configurable core
- WAF detection & evasion
- Outdated JS lib scanning
- Intelligent payload generator
- Handmade HTML & JavaScript parser.om/s0md3v/XSStrike/wiki/Compatibility-&-Dependencies)
- *Estimated Time of Arrival (ETA)
- *Export results to JSON
- Handmade HTML & JavaScript parser
- Powerful fuzzing engine
- Blind XSS support
- Highly researched work-flow
- Complete HTTP support
- Bruteforce payloads from a file
- Blind XSS support
- Parameter discovery and hidden inputs
- Complete HTTP support with headers and cookies
- Integration with custom plugins such as `retireJS`

## Installation

```bash
git clone https://github.com/s0md3v/XSSniper
cd XSSniper
pip install -r requirements.txt --break-system-packages
```

> If you are using a virtual environment, activate it before installing dependencies.

## Usage

Run the scanner with the new entrypoint:

```bash
python xssniper.py --help
```

### Example commands

Scan a URL with default settings:

```bash
python xssniper.py --url https://example.com
```

Use a config file:

```bash
python xssniper.py --config xssniper.yaml
```

Encode payloads as Base64:

```bash
python xssniper.py --payload-encoding base64 --url https://example.com
```

### Recommended workflow

1. Start with a simple reflected scan.
2. Add `--config` to tune payload delivery and request headers.
3. Enable `--payload-encoding` when targets require encoded vectors.
4. Use built-in crawling and fuzzing for deeper discovery.

## Configuration

This fork adds a configuration loader that merges external settings with defaults.

Supported config formats:

- YAML: `xssniper.yaml`
- JSON: `xssniper.json`

Configuration can override targets, headers, encoders, and scan options.

> See `CONFIGURATION.md` and `CONFIG_IMPLEMENTATION.md` for full config examples and loader behavior.

## Screenshot placeholders

Add your proof-of-concept images here once available.

### Example proof-of-concept screenshot

![POC screenshot 1](docs/poc1.png)

### Progress logging example

![POC screenshot 2](docs/poc2.png)

### Payload generation example

![POC screenshot 3](docs/poc3.png)

## Documentation

- `CONFIGURATION.md` — configuration quickstart and options
- `CONFIG_IMPLEMENTATION.md` — loader and default merge behavior
- `tests/README.md` — testing and development guidance

## Running tests

```bash
pytest
```

## Contribution

- Report bugs or feature requests
- Propose improvements with a pull request
- Add documentation and test coverage
- Share your experience and feedback

## License

Licensed under the GNU GPLv3. See [LICENSE](LICENSE) for details.

## Credits

This fork builds on the design of the original `xsstrike` project. The WAF signatures in `/db/wafSignatures.json` are adapted from sqlmap, and `/plugins/retireJS.py` is derived from `retirejslib`.
