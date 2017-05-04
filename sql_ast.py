"""
Michael Harrington
Grant Broadwater

Abstract Syntax Tree for sql like input for assignment
"""

class AST_Node(object):
    pass

class AST_SQL(AST_Node):
    def __init__(self, ast_tableDecls, ast_queries):
        self.tables = ast_tableDecls
        self.queries = ast_queries

    def __str__(self):
        return str(self.tables) + '\n\n' + str(self.queries)

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

class AST_SqlQueries(AST_Node):
    def __init__(self):
        self.queries = []

    def addQuery(self, ast_query):
        self.queries.append(ast_query)

    def __str__(self):
        return '\n\n'.join(map(str, self.queries))

class AST_SqlQuery(AST_Node):
    def __init__(self, qselect, qfrom):
        self.qselect = qselect
        self.qfrom = qfrom
        self.qwhere = None
        self.qgb = None
        self.qhaving = None
        self.qchain = None
        self.child = None

    def setWhere(self, qwhere):
        self.qwhere = qwhere

    def setHaving(self, qhaving):
        self.qhaving = qhaving

    def setGroupBy(self, qgb):
        self.qgb = qgb

    def setChild(self, qchain, query):
        self.qchain = qchain
        self.child = query

    def __str__(self):
        return '\n'.join(map(str, [
            'Query: ',
            self.qselect,
            self.qfrom,
            self.qwhere,
            self.qgb,
            self.qhaving,
            self.qchain,
            self.child,
        ]))

class AST_Select(AST_Node):
    def __init__(self):
        self.selectors = []

    def addSelector(self, ast_selector):
        self.selectors.append(ast_selector)

    def __str__(self):
        return 'SELECT ' + ', '.join(map(str, self.selectors))

class AST_Aggregate(AST_Node):
    def __init__(self, keyword, attribute):
        self.keyword = keyword
        self.attribute = attribute

    def __str__(self):
        return self.keyword + ' of ' + str(self.attribute)

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
        if self.alias:
            return self.alias + '-' + self.name
        else:
            return self.name

class AST_Where(AST_Node):
    def __init__(self):
        self.boolExprs = []
        self.boolComps = []

    def addBoolExpr(self, ast_be, ast_bc):
        self.boolExprs.append(ast_be)
        self.boolComps.append(ast_bc)

    @property
    def boolEC(self):
        for e, c in zip(self.boolExprs, self.boolComps[1:] + [None]):
            yield e
            if c:
                yield c

    def __str__(self):
        return 'WHERE ' + ' '.join(map(str, self.boolEC))

class AST_BoolFullExpr(AST_Node):
    def __init__(self):
        self.boolExprs = []
        self.boolComps = []

    def addBoolExpr(self, ast_be, ast_bc):
        self.boolExprs.append(ast_be)
        self.boolComps.append(ast_bc)

    @property
    def boolEC(self):
        for e, c in zip(self.boolExprs, self.boolComps[1:] + [None]):
            yield e
            if c:
                yield c

    @property
    def aggregators(self):
        for e in self.boolExprs:
            for agg in e.aggregators:
                yield agg

    def __str__(self):
        if len(self.boolExprs) == 1:
            return str(self.boolExprs[0])
        return '( ' + ' '.join(map(str, self.boolEC)) + ' ) '


class AST_Having(AST_Node):
    def __init__(self):
        self.boolExprs = []
        self.boolComps = []

    def addBoolExpr(self, ast_be, ast_bc):
        self.boolExprs.append(ast_be)
        self.boolComps.append(ast_bc)

    @property
    def boolEC(self):
        for e, c in zip(self.boolExprs, self.boolComps[1:] + [None]):
            yield e
            if c:
                yield c

    @property
    def aggregators(self):
        for e in self.boolExprs:
            for agg in e.aggregators:
                yield agg

    def __str__(self):
        return 'HAVING ' + ' '.join(map(str, self.boolEC))


class AST_BoolExpr(AST_Node):
    def __init__(self, lhs, comp, rhs):
        self.lhs = lhs
        self.comp = comp
        self.rhs = rhs

    @property
    def aggregators(self):
        if type(self.lhs) == AST_Aggregate:
            yield str(self.lhs)
        if type(self.rhs) == AST_Aggregate:
            yield str(self.rhs)

    def __str__(self):
        return ' '.join(map(str, [self.lhs, self.comp, self.rhs]))

class AST_GroupBy(AST_Node):
    def __init__(self):
        self.attributes = []

    def addAttribute(self, attribute):
        self.attributes.append(attribute)

    def __str__(self):
        return 'GROUP BY ' + ', '.join(map(str, self.attributes))

