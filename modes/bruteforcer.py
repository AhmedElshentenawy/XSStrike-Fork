import copy
from urllib.parse import urlparse, unquote

from core.colors import good, green, end
from core.requester import requester
from core.utils import getUrl, getParams
from core.log import setup_logger

logger = setup_logger(__name__)


def bruteforcer(target, paramData, payloadList, encoding, headers, delay, timeout, encoding_fallback=False):
    GET, POST = (False, True) if paramData else (True, False)
    logger.progress('Preparing bruteforce scan for target: %s' % target)
    host = urlparse(target).netloc  # Extracts host out of the url
    logger.debug('Parsed host to bruteforce: {}'.format(host))
    url = getUrl(target, GET)
    logger.debug('Parsed url to bruteforce: {}'.format(url))
    params = getParams(target, paramData, GET)
    logger.debug_json('Bruteforcer params:', params)
    if not params:
        logger.error('No parameters to test.')
        quit()
    for paramName in params.keys():
        logger.progress('Bruteforcing parameter: %s' % paramName)
        paramsCopy = copy.deepcopy(params)
        for index, payload in enumerate(payloadList, start=1):
            logger.progress('Testing payload %i/%i for %s' % (index, len(payloadList), paramName))
            raw_payload = payload
            encoded_payload = encoding(unquote(raw_payload)) if encoding else raw_payload
            if encoding and not encoding_fallback:
                payload = encoded_payload
            else:
                payload = raw_payload
            paramsCopy[paramName] = payload
            response = requester(url, paramsCopy, headers,
                                 GET, delay, timeout).text
            if encoding and encoding_fallback and raw_payload not in response and encoded_payload not in response:
                logger.progress('Retrying with fallback encoding for payload %i/%i' % (index, len(payloadList)))
                payload = encoded_payload
                paramsCopy[paramName] = payload
                response = requester(url, paramsCopy, headers,
                                     GET, delay, timeout).text
            if payload == raw_payload:
                display_payload = raw_payload
            else:
                display_payload = encoding(payload)
            if raw_payload in response or encoded_payload in response:
                logger.info('%s %s' % (good, display_payload))
    logger.progress('Bruteforce scan completed for target: %s' % target)
