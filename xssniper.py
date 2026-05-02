#!/usr/bin/env python3

from __future__ import print_function
from datetime import datetime
from core.colors import end, red, white, bad, info
# Just a fancy ass banner
print('''%s
\tXSSniper %sv3.1.5   
%s''' % (red, white, end))
print("\n[+]Done ")
print("[+]Scane started at: ",datetime.now())
print("-"*50)

from core.colors import end, red, white, bad, info

# Just a fancy ass banner
print('''%s
\tXSSniper %sv3.1.5
%s''' % (red, white, end))

try:
    import concurrent.futures
    from urllib.parse import urlparse
    try:
        import fuzzywuzzy
    except ImportError:
        import os
        print ('%s fuzzywuzzy isn\'t installed, installing now.' % info)
        ret_code = os.system('pip3 install fuzzywuzzy')
        if(ret_code != 0):
            print('%s fuzzywuzzy installation failed.' % bad)
            quit()
        print ('%s fuzzywuzzy has been installed, restart XSStrike.' % info)
        quit()
except ImportError:  # throws error in python2
    print('%s XSStrike isn\'t compatible with python2.\n Use python > 3.4 to run XSStrike.' % bad)
        print ('%s fuzzywuzzy has been installed, restart XSSniper.' % info)
        quit()
except ImportError:  # throws error in python2
    print('%s XSSniper isn\'t compatible with python2.\n Use python > 3.4 to run XSSniper.' % bad)
    quit()

# Let's import whatever we need from standard lib
import sys
import json
import argparse

# ... and configurations core lib
import core.config
import core.log

# Processing command line arguments, where dest var names will be mapped to local vars with the same name
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', help='url', dest='target')
parser.add_argument('--data', help='post data', dest='paramData')
parser.add_argument('-e', '--encode', help='encode payloads (url or base64, default: url)',
                    dest='encode', choices=['url', 'base64'], default='url')
parser.add_argument('--encode-fallback', help='retry failed payloads with the selected encoding',
                    dest='encode_fallback', action='store_true')
parser.add_argument('--fuzzer', help='fuzzer',
                    dest='fuzz', action='store_true')
parser.add_argument('--update', help='update',
                    dest='update', action='store_true')
parser.add_argument('--timeout', help='timeout',
                    dest='timeout', type=int, default=core.config.timeout)
parser.add_argument('--proxy', help='use prox(y|ies)',
                    dest='proxy', action='store_true')
parser.add_argument('--crawl', help='crawl',
                    dest='recursive', action='store_true')
parser.add_argument('--json', help='treat post data as json',
                    dest='jsonData', action='store_true')
parser.add_argument('--path', help='inject payloads in the path',
                    dest='path', action='store_true')
parser.add_argument(
    '--seeds', help='load crawling seeds from a file', dest='args_seeds')
parser.add_argument(
    '-f', '--file', help='load payloads from a file', dest='args_file')
parser.add_argument('-l', '--level', help='level of crawling',
                    dest='level', type=int, default=2)
parser.add_argument('--headers', help='add headers',
                    dest='add_headers', nargs='?', const=True)
parser.add_argument('-t', '--threads', help='number of threads',
                    dest='threadCount', type=int, default=core.config.threadCount)
parser.add_argument('-d', '--delay', help='delay between requests',
                    dest='delay', type=int, default=core.config.delay)
parser.add_argument('--skip', help='don\'t ask to continue',
                    dest='skip', action='store_true')
parser.add_argument('--skip-dom', help='skip dom checking',
                    dest='skipDOM', action='store_true')
parser.add_argument('--blind', help='inject blind XSS payload while crawling',
                    dest='blindXSS', action='store_true')
parser.add_argument('--export-json', help='Save results to JSON file', action='store_true')
parser.add_argument('--console-log-level', help='Console logging level',
                    dest='console_log_level', default=core.log.console_log_level,
                    choices=core.log.log_config.keys())
parser.add_argument('--file-log-level', help='File logging level', dest='file_log_level',
                    choices=core.log.log_config.keys(), default=None)
parser.add_argument('--log-file', help='Name of the file to log', dest='log_file',
                    default=core.log.log_file)

args = parser.parse_args()

from core.config_loader import ConfigLoader, apply_config_to_args

# Processing command line arguments, where dest var names will be mapped to local vars with the same name
parser = argparse.ArgumentParser(
    description='XSStrike - Advanced XSS Detection and Exploitation Suite',
    epilog='''Examples:
  Basic scan:
    python3 xsstrike.py -u http://example.com

  Crawl and scan:
    python3 xsstrike.py -u http://example.com --crawl --level 3

  Fuzz with custom payloads:
    python3 xsstrike.py -u http://example.com --fuzzer -f payloads.txt

  Use configuration file:
    python3 xsstrike.py -u http://example.com --config custom.yaml

  POST data scan:
    python3 xsstrike.py -u http://example.com --data "param=value"

For more options, use --help''',
    formatter_class=argparse.RawDescriptionHelpFormatter
)

# Target Options
target_group = parser.add_argument_group('Target Options')
target_group.add_argument('-u', '--url', 
                        help='Target URL to scan for XSS vulnerabilities',
                        dest='target')
target_group.add_argument('--data', 
                         help='POST data to send with requests (e.g., "param1=value1&param2=value2")',
                         dest='paramData')
target_group.add_argument('--json', 
                         help='Treat POST data as JSON format',
                         dest='jsonData', action='store_true')
target_group.add_argument('--path', 
                         help='Inject payloads in the URL path instead of parameters',
                         dest='path', action='store_true')

# Encoding Options
encoding_group = parser.add_argument_group('Encoding Options')
encoding_group.add_argument('-e', '--encode', 
                          help='Encode payloads to evade filters (url: URL encoding, base64: Base64 encoding, default: url)',
                          dest='encode', choices=['url', 'base64'], default='url')
encoding_group.add_argument('--encode-fallback', 
                           help='Retry failed payloads with the selected encoding method',
                           dest='encode_fallback', action='store_true')

# Scanning Modes
scan_group = parser.add_argument_group('Scanning Modes')
scan_group.add_argument('--fuzzer', 
                       help='Enable fuzzer mode for interactive payload testing',
                       dest='fuzz', action='store_true')
scan_group.add_argument('--crawl', 
                       help='Crawl the target website for additional URLs to scan',
                       dest='recursive', action='store_true')
scan_group.add_argument('-l', '--level', 
                       help='Crawling depth level (default: 2)',
                       dest='level', type=int, default=2)
scan_group.add_argument('--seeds', 
                       help='Load crawling seeds from a file (one URL per line)',
                       dest='args_seeds')
scan_group.add_argument('-f', '--file', 
                       help='Load custom payloads from a file (one payload per line, or "default" for built-in)',
                       dest='args_file')
scan_group.add_argument('--blind', 
                       help='Inject blind XSS payload while crawling (requires --crawl)',
                       dest='blindXSS', action='store_true')

# Request Options
request_group = parser.add_argument_group('Request Options')
request_group.add_argument('--timeout', 
                          help='Request timeout in seconds (default: 10)',
                          dest='timeout', type=int, default=core.config.timeout)
request_group.add_argument('--proxy', 
                          help='Use proxy settings from config.py',
                          dest='proxy', action='store_true')
request_group.add_argument('--headers', 
                          help='Add custom headers (prompts if no value provided)',
                          dest='add_headers', nargs='?', const=True)
request_group.add_argument('-t', '--threads', 
                          help='Number of concurrent threads (default: 10)',
                          dest='threadCount', type=int, default=core.config.threadCount)
request_group.add_argument('-d', '--delay', 
                          help='Delay between requests in seconds (default: 0)',
                          dest='delay', type=int, default=core.config.delay)

# Output Options
output_group = parser.add_argument_group('Output Options')
output_group.add_argument('--console-log-level', 
                         help='Console logging level (default: info)',
                         dest='console_log_level', default=core.log.console_log_level,
                         choices=core.log.log_config.keys())
output_group.add_argument('--file-log-level', 
                         help='File logging level (default: none)',
                         dest='file_log_level', choices=core.log.log_config.keys(), default=None)
output_group.add_argument('--log-file', 
                         help='Path to log file (default: xsstrike.log)',
                         dest='log_file', default=core.log.log_file)

# Configuration
config_group = parser.add_argument_group('Configuration')
config_group.add_argument('--config', 
                         help='Path to configuration file (YAML or JSON format)',
                         dest='config_file', default=None)

# Other Options
other_group = parser.add_argument_group('Other Options')
other_group.add_argument('--update', 
                        help='Update XSStrike to the latest version',
                        dest='update', action='store_true')
other_group.add_argument('--skip', 
                        help='Skip confirmation prompts',
                        dest='skip', action='store_true')
other_group.add_argument('--skip-dom', 
                        help='Skip DOM-based XSS checking',
                        dest='skipDOM', action='store_true')
args = parser.parse_args()

# Load configuration from file and merge with command-line arguments
config_loader = ConfigLoader(args.config_file)
config_loader.validate()  # Validate config file
args = apply_config_to_args(args, config_loader)

# Pull all parameter values of dict from argparse namespace into local variables of name == key
# The following works, but the static checkers are too static ;-) locals().update(vars(args))
target = args.target
path = args.path
jsonData = args.jsonData
paramData = args.paramData
encode = args.encode
fuzz = args.fuzz
update = args.update
timeout = args.timeout
proxy = args.proxy
recursive = args.recursive
args_file = args.args_file
args_seeds = args.args_seeds
level = args.level
add_headers = args.add_headers
threadCount = args.threadCount
delay = args.delay
skip = args.skip
skipDOM = args.skipDOM
blindXSS = args.blindXSS
core.log.console_log_level = args.console_log_level
core.log.file_log_level = args.file_log_level
core.log.log_file = args.log_file

logger = core.log.setup_logger()

logger.progress("Initializing XSSniper scanner...")

core.config.globalVariables = vars(args)

# Import everything else required from core lib
from core.config import blindPayload
from core.encoders import base64
from core.photon import photon
from core.prompt import prompt
from core.updater import updater
from core.utils import extractHeaders, reader, converter

from modes.bruteforcer import bruteforcer
from modes.crawl import crawl
from modes.scan import scan
from modes.singleFuzz import singleFuzz

if type(args.add_headers) == bool:
    headers = extractHeaders(prompt())
elif type(args.add_headers) == str:
    headers = extractHeaders(args.add_headers)
else:
    from core.config import headers

core.config.globalVariables['headers'] = headers
core.config.globalVariables['checkedScripts'] = set()
core.config.globalVariables['checkedForms'] = {}
core.config.globalVariables['definitions'] = json.loads('\n'.join(reader(sys.path[0] + '/db/definitions.json')))

if path:
    paramData = converter(target, target)
elif jsonData:
    headers['Content-type'] = 'application/json'
    paramData = converter(paramData)

if args_file:
    if args_file == 'default':
        payloadList = core.config.payloads
    else:
        payloadList = list(filter(None, reader(args_file)))

seedList = []
if args_seeds:
    seedList = list(filter(None, reader(args_seeds)))

if encode == 'base64':
    encoding = base64
else:
    from core.encoders import url

    encoding = url

encoding_fallback = args.encode_fallback

if not proxy:
    core.config.proxies = {}

if update:  # if the user has supplied --update argument
    updater()
    quit()  # quitting because files have been changed

if not target and not args_seeds:  # if the user hasn't supplied a url
    logger.no_format('\n' + parser.format_help().lower())
    quit()

if fuzz:
    singleFuzz(target, paramData, encoding, headers, delay, timeout, encoding_fallback)
elif not recursive and not args_seeds:
    if args_file:
        bruteforcer(target, paramData, payloadList, encoding, headers, delay, timeout, encoding_fallback)
    else:
        results = scan(target, paramData, encoding, headers, delay, timeout, skipDOM, skip, encoding_fallback)
        if args.export_json:
            from core.utils import save_results_to_json
            save_results_to_json(results)
else:
    if target:
        seedList.append(target)
    for target in seedList:
    logger.no_format('\n' + parser.format_help())
    quit()

if fuzz:
    logger.progress("Starting interactive fuzzer mode...")
    singleFuzz(target, paramData, encoding, headers, delay, timeout, encoding_fallback)
elif not recursive and not args_seeds:
    logger.progress("Starting XSS vulnerability scan...")
    if args_file:
        logger.progress("Loading custom payloads from file...")
        bruteforcer(target, paramData, payloadList, encoding, headers, delay, timeout, encoding_fallback)
    else:
        logger.progress("Using built-in payload database...")
        scan(target, paramData, encoding, headers, delay, timeout, skipDOM, skip, encoding_fallback)
else:
    logger.progress("Starting crawling and scanning mode...")
    if target:
        seedList.append(target)
    for target in seedList:
        logger.progress("Crawling target: {}".format(target))
        logger.run('Crawling the target')
        scheme = urlparse(target).scheme
        logger.debug('Target scheme: {}'.format(scheme))
        host = urlparse(target).netloc
        main_url = scheme + '://' + host
        crawlingResult = photon(target, headers, level,
                                threadCount, delay, timeout, skipDOM)
        forms = crawlingResult[0]
        domURLs = list(crawlingResult[1])
        difference = abs(len(domURLs) - len(forms))
        if len(domURLs) > len(forms):
            for i in range(difference):
                forms.append(0)
        elif len(forms) > len(domURLs):
            for i in range(difference):
                domURLs.append(0)
        threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
        futures = (threadpool.submit(crawl, scheme, host, main_url, form,
                                     blindXSS, blindPayload, headers, delay, timeout, encoding, encoding_fallback) for form, domURL in zip(forms, domURLs))
        for i, _ in enumerate(concurrent.futures.as_completed(futures)):
            if i + 1 == len(forms) or (i + 1) % threadCount == 0:
                logger.info('Progress: %i/%i\r' % (i + 1, len(forms)))
        logger.no_format('')
