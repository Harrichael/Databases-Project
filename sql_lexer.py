"""
Michael Harrington
Grant Broadwater

Lexer for SQL like input for assignment
"""

import re

class Lexer(object):
    re_token        = re.compile('[\w]+[.][\w]+|[\w]+|[^ \t\n\r\f\v\w]')

    re_identifier   = re.compile('[a-zA-Z](\w)*')
    re_attribute    = re.compile('[a-zA-Z](\w)*[.][a-zA-Z](\w)*|[a-zA-Z](\w)*')
    re_value        = re.compile('[+-]?[0-9]+[.][0-9]+|[+-]?[0-9]+|["][^"]*["]|[\'][^\']*[\']')

    keywords = set([
        'SELECT',
        'FROM',
        'WHERE',
        'GROUP',
        'BY',
        'AS',
        'OR',
        'AND',
        'INTERSECT',
        'UNION',
        'EXCEPT',
        'ADD',

        'HAVING',
        'CONTAINS',
        'IN',
        'EXISTS',
        'MAX',
        'MIN',
        'COUNT',
        'AVG',
    ])
    sentinelToken   = ''

    @classmethod
    def tokenize(cls, inputStr):
        return re.findall(cls.re_token, inputStr) + [cls.sentinelToken]

    @classmethod
    def identifier(cls, token):
        if token.upper() in cls.keywords:
            return False

        return cls.re_identifier.match(token)

    @classmethod
    def attribute(cls, token):
        return cls.re_attribute.match(token)

    @classmethod
    def value(cls, token):
        return cls.re_value.match(token)

