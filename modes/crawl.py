import copy
import re

import core.config
from core.colors import green, end
from core.config import xsschecker
from core.filterChecker import filterChecker
from core.generator import generator
from core.htmlParser import htmlParser
from core.requester import requester
from core.log import setup_logger

logger = setup_logger(__name__)


def crawl(scheme, host, main_url, form, blindXSS, blindPayload, headers, delay, timeout, encoding, encoding_fallback=False):
    logger.progress('Starting crawl scan on %s' % main_url)
    if form:
        for each in form.values():
            url = each['action']
            if url:
                logger.progress('Processing form action: %s' % url)
                if url.startswith(main_url):
                    pass
                elif url.startswith('//') and url[2:].startswith(host):
                    url = scheme + '://' + url[2:]
                elif url.startswith('/'):
                    url = scheme + '://' + host + url
                elif re.match(r'\w', url[0]):
                    url = scheme + '://' + host + '/' + url
                if url not in core.config.globalVariables['checkedForms']:
                    core.config.globalVariables['checkedForms'][url] = []
                method = each['method']
                GET = True if method == 'get' else False
                inputs = each['inputs']
                paramData = {}
                for one in inputs:
                    paramData[one['name']] = one['value']
                    for paramName in paramData.keys():
                        if paramName not in core.config.globalVariables['checkedForms'][url]:
                            logger.progress('Testing form parameter %s on %s' % (paramName, url))
                            core.config.globalVariables['checkedForms'][url].append(paramName)
                            paramsCopy = copy.deepcopy(paramData)
                            paramsCopy[paramName] = xsschecker
                            logger.progress('Sending request to %s' % url)
                            response = requester(
                                url, paramsCopy, headers, GET, delay, timeout)
                            occurences = htmlParser(response, encoding)
                            positions = occurences.keys()
                            logger.progress('Analyzing response for injected reflections...')
                            occurences = filterChecker(
                                url, paramsCopy, headers, GET, delay, occurences, timeout, encoding, core.config.globalVariables.get('encode_fallback', False))
                            vectors = generator(occurences, response.text)
                            if vectors:
                                for confidence, vects in vectors.items():
                                    try:
                                        payload = list(vects)[0]
                                        logger.vuln('Vulnerable webpage: %s%s%s' %
                                                    (green, url, end))
                                        logger.vuln('Vector for %s%s%s: %s' %
                                                    (green, paramName, end, payload))
                                        break
                                    except IndexError:
                                        pass
                            if blindXSS and blindPayload:
                                logger.progress('Submitting blind XSS payload to %s' % url)
                                paramsCopy[paramName] = blindPayload
                                requester(url, paramsCopy, headers,
                                          GET, delay, timeout)
    logger.progress('Crawl scan completed for %s' % main_url)
