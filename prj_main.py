"""
Michael Harrington
Grant Broadwater

CLI file for sql like tree syntax printing
"""

import sys

from sql_parser import parse_sql
from ast_print import PrettyASTPrint, RAPrint, RAQsTreePrint

ast = parse_sql(sys.stdin.read())
print('----Input Debug Printing----')
print(ast)
print('\n\n----SQL Tree Printing----')
PrettyASTPrint(ast)
print('\n\n----Relational Algebra Printing----')
RAPrint(ast)
print('\n\n----Query Tree Algebra Printing----')
RAQsTreePrint(ast)
