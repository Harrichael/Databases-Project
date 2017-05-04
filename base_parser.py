"""
Michael Harrington

This file provides a base parser for creating recursive descent parsers
"""

from functools import wraps
from itertools import tee

class ParserException(Exception):
    pass

class Parser(object):
    def __init__(self):
        self.iTokens = None
        self.token = None

    def getToken(self):
        try:
            self.token = next(self.iTokens)
            print "Token: " + self.token
        except StopIteration:
            raise ParserException('Unexpected end of input!')

    def parse(self):
        self.iTokens = iter(self.tokens)
        self.getToken()

    """
    Lets turn all self.parse_* to self.try_* automagically!
    """
    def __getattr__(self, name):
        if name.startswith('try_'):
            parseName = 'parse_' + name[4:]
            parseAttr = getattr(self, parseName)
            setattr(self, name, self.getTryDecorator()(parseAttr))
            return getattr(self, name)

        raise AttributeError('Attribute does not exist: {}'.format(name))

    def getTryDecorator(self):
        def tryDecorator(parseFunc):
            @wraps(parseFunc)
            def wrapper(*args):
                success = True
                retVal = None
                tokenSave, self.iTokens = tee(self.iTokens)
                try:
                    retVal = parseFunc(*args)
                except ParserException:
                    success = False
                    self.iTokens = tokenSave

                return success, retVal

            return wrapper

        return tryDecorator

    def parse_Terminal(self, terminal):
        token = self.token
        if self.token == terminal:
            self.getToken()
        else:
            raise ParserException('Terminal not found: ' + terminal)
        return token

    def parse_Keyword(self, keyword):
        token = self.token.upper()
        if self.token.upper() == keyword.upper():
            self.getToken()
        else:
            raise ParserException('Keyword not found: ' + keyword)
        return token

    def parse_Token(self):
        self.getToken()

