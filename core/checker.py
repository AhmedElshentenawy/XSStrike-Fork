from core.config import xsschecker
from core.requester import requester
from typing import Dict, List, Callable
from core.utils import replaceValue, fillHoles
from core.log import setup_logger

logger = setup_logger(__name__)


def checker(url: str, params: Dict[str, str], headers: Dict[str, str], GET: bool, delay: int, payload: str, positions: List[int], timeout: int, encoding: Callable[[str], str], encoding_fallback: bool = False) -> List[int]:
    def run_check(use_encoding):
        logger.progress("Testing payload with {} encoding...".format("enabled" if use_encoding else "disabled"))
        checkString = 'st4r7s' + payload + '3nd'
        if use_encoding and encoding:
            checkString = encoding(unquote(checkString))
        response = requester(url, replaceValue(
            params, xsschecker, checkString, copy.deepcopy), headers, GET, delay, timeout).text.lower()
        reflectedPositions = []
        for match in re.finditer('st4r7s', response):
            reflectedPositions.append(match.start())
        filledPositions = fillHoles(positions, reflectedPositions)
        #  Itretating over the reflections
        num = 0
        efficiencies = []
        for position in filledPositions:
            allEfficiencies = []
            try:
                reflected = response[reflectedPositions[num]
                    :reflectedPositions[num]+len(checkString)]
                efficiency = fuzz.partial_ratio(reflected, checkString.lower())
                allEfficiencies.append(efficiency)
            except IndexError:
                pass
            if position:
                reflected = response[position:position+len(checkString)]
                if use_encoding and encoding:
                    efficiency = fuzz.partial_ratio(reflected, checkString)
                else:
                    efficiency = fuzz.partial_ratio(reflected, checkString)
                if reflected[:-2] == ('\\%s' % checkString.replace('st4r7s', '').replace('3nd', '')):
                    efficiency = 90
                allEfficiencies.append(efficiency)
                efficiencies.append(max(allEfficiencies))
            else:
                efficiencies.append(0)
            num += 1
        return list(filter(None, efficiencies))

    efficiencies = run_check(False if encoding_fallback else bool(encoding))
    if encoding and encoding_fallback and not efficiencies:
        efficiencies = run_check(True)
    return efficiencies
