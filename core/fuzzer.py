import copy
import requests
from random import randint
from time import sleep
from urllib.parse import unquote

from core.colors import end, red, green, yellow
from core.config import fuzzes, xsschecker
from core.requester import requester
from core.utils import replaceValue, counter
from core.log import setup_logger

logger = setup_logger(__name__)


def fuzzer(url, params, headers, GET, delay, timeout, WAF, encoding, encoding_fallback=False):
    for fuzz in fuzzes:
        if delay == 0:
            delay = 0
        t = delay + randint(delay, delay * 2) + counter(fuzz)
        sleep(t)
        raw_fuzz = fuzz
        encoded_fuzz = encoding(unquote(raw_fuzz)) if encoding else raw_fuzz
        payload = encoded_fuzz if encoding and not encoding_fallback else raw_fuzz
        try:
            data = replaceValue(params, xsschecker, payload, copy.deepcopy)
            response = requester(url, data, headers, GET, delay/2, timeout)
            if encoding and encoding_fallback and raw_fuzz.lower() not in response.text.lower() and encoded_fuzz.lower() not in response.text.lower():
                payload = encoded_fuzz
                data = replaceValue(params, xsschecker, payload, copy.deepcopy)
                response = requester(url, data, headers, GET, delay/2, timeout)
        except requests.RequestException as e:
            logger.error('WAF is dropping suspicious requests.')
            logger.debug('Error details: {}'.format(str(e)))
            if delay == 0:
                logger.info('Delay has been increased to %s6%s seconds.' % (green, end))
                delay += 6
            limit = (delay + 1) * 50
            timer = -1
            while timer < limit:
                logger.info('\rFuzzing will continue after %s%i%s seconds.\t\t\r' % (green, limit, end))
                limit -= 1
                sleep(1)
            try:
                requester(url, params, headers, GET, 0, 10)
                logger.good('Pheww! Looks like sleeping for %s%i%s seconds worked!' % (
                    green, ((delay + 1) * 2), end))
            except requests.RequestException as e:
                logger.error('\nLooks like WAF has blocked our IP Address. Sorry!')
                logger.debug('Error details: {}'.format(str(e)))
                break
        display_fuzz = raw_fuzz if payload == raw_fuzz else (encoding(payload) if encoding else payload)
        if payload.lower() in response.text.lower():  # if fuzz string is reflected in the response
            result = ('%s[passed]  %s' % (green, end))
        # if the server returned an error (Maybe WAF blocked it)
        elif str(response.status_code)[:1] != '2':
            result = ('%s[blocked] %s' % (red, end))
        else:  # if the fuzz string was not reflected in the response completely
            result = ('%s[filtered]%s' % (yellow, end))
        logger.info('%s %s' % (result, display_fuzz))
