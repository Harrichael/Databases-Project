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

    def __str__(self):
        return '{}:{}'.format(self.att_name, self.att_type)

class AST_TableDecl(AST_Node):
    def __init__(self, name):
        self.name = name
        self.attributes = []

    def addAttribute(self, ast_attr):
        self.attributes.append(ast_attr)

    def __str__(self):
        return 'Table: {}({})'.format(self.name, ', '.join(map(str, self.attributes)))

class AST_TableDecls(AST_Node):
    def __init__(self):
        self.tables = []

    def addTable(self, ast_table):
        self.tables.append(ast_table)

    def __str__(self):
        return '\n\n'.join(map(str, self.tables))

class AST_SQL(AST_Node):
    def __init__(self, ast_tableDecls, ast_queries):
        self.tables = ast_tableDecls
        self.queries = ast_queries

    def __str__(self):
        return str(self.tables) + '\n\n' + str(self.queries)

class AST_SqlQueries(AST_Node):
    def __init__(self):
        self.queries = []

    def addQuery(self, ast_query):
        self.queries.append(ast_query)

    def __str__(self):
        return '\n\n'.join(map(str, self.queries))

class AST_SqlQuery(AST_Node):
    def __init__(self, qselect, qfrom, qwhere, qgb):
        self.qselect = qselect
        self.qfrom = qfrom
        self.qwhere = qwhere
        self.qgb = qgb

    def __str__(self):
        return '\n'.join(map(str, [
            'Query: ',
            self.qselect,
            self.qfrom,
            self.qwhere,
            self.qgb,
        ]))

class AST_Select(AST_Node):
    def __init__(self):
        self.selectors = []

    def addSelector(self, ast_selector):
        self.selectors.append(ast_selector)

    def __str__(self):
        return 'SELECT ' + ', '.join(map(str, self.selectors))

class AST_Attribute(AST_Node):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return self.token

class AST_From(AST_Node):
    def __init__(self):
        self.tables = []

    def addTable(self, ast_table):
        self.tables.append(ast_table)

    def __str__(self):
        return 'FROM ' + ', '.join(map(str, self.tables))

class AST_FromTable(AST_Node):
    def __init__(self, name):
        self.name = name
        self.alias = ''

    def setAlias(self, alias):
        self.alias = alias

    def __str__(self):
        return self.alias + '-' + self.name

