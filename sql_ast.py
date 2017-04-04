"""
Michael Harrington
Grant Broadwater

Abstract Syntax Tree for sql like input for assignment
"""

class AST_Node(object):
    pass

class AST_AttributeDecl(AST_Node):
    def __init__(self, att_name, att_type):
        self.att_name = att_name
        self.att_type = att_type

class AST_TableDecl(AST_Node):
    def __init__(self, name):
        self.name = name
        self.attributes = []

    def addAttribute(self, ast_attr):
        self.attributes.append(ast_attr)

    def __str__(self):
        return 'Table: {}({})'.format(self.name, len(self.attributes))

class AST_TableDecls(AST_Node):
    def __init__(self):
        self.tables = []

    def addTable(self, ast_table):
        self.tables.append(ast_table)

    def __str__(self):
        return '\n'.join(map(str, self.tables))

class AST_SQL(AST_Node):
    def __init__(self, ast_tableDecls, ast_queries):
        self.tables = ast_tableDecls
        self.queries = ast_queries

    def __str__(self):
        return str(self.tables) + '\n' + str(self.queries)

class AST_SqlQueries(AST_Node):
    def __init__(self):
        self.queries = []

    def addQuery(self, ast_query):
        self.queries.append(ast_query)

    def __str__(self):
        return '\n'.join(map(str, self.queries))

class AST_SqlQuery(AST_Node):
    def __init__(self):
        pass

    def __str__(self):
        return 'Query'


