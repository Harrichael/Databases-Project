"""
Michael Harrington
Grant Broadwater

CLI file for sql like tree syntax printing
"""

import sys

from sql_parser import parse_sql

print(parse_sql(sys.stdin.read()))
